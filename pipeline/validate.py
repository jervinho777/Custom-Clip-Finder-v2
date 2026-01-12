"""
STAGE 3: VALIDATE (Optimized)

Quality scoring using BRAIN patterns.
Uses Quality Oracle identity for final decisions.
Parallelized processing with Prompt Caching enabled.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio

from models.base import ClaudeModel
from brain import load_principles, get_similar_clips
from prompts.validate import build_validate_prompt, build_final_ranking_prompt


@dataclass
class ValidationResult:
    """Result of clip validation."""
    verdict: str  # approve, refine, reject
    confidence: float
    assessment: Dict
    predicted_performance: Dict
    refinements: List[str]


@dataclass 
class ValidatedClip:
    """A validated clip ready for export."""
    clip: Dict  # Original ComposedClip data
    validation: ValidationResult
    rank: Optional[int] = None


async def validate_clip(
    composed_clip: Dict,
    use_brain: bool = True
) -> ValidationResult:
    """
    Validate a composed clip using BRAIN patterns.
    """
    # Get BRAIN context
    similar_clips = []
    quality_signals = {}
    
    if use_brain:
        try:
            principles = load_principles()
            quality_signals = principles.get("quality_signals", {})
            
            # Find similar clips based on hook
            hook_text = composed_clip.get("hook_text", "")
            if hook_text:
                similar_clips = await get_similar_clips(hook_text, n_results=5)
        except Exception:
            pass  # Fail silently on brain issues to keep pipeline running
    
    # Build prompt
    system_prompt, user_prompt = build_validate_prompt(
        composed_clip=composed_clip,
        similar_clips=similar_clips,
        quality_signals=quality_signals
    )
    
    # Use Claude for validation
    from models.base import get_model
    model = get_model("anthropic", tier="sonnet")
    
    response = await model.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.3,
        cache_system=True  # <--- ENABLED CACHING
    )
    
    # Parse response
    result = _parse_validation(response.content)
    
    return ValidationResult(
        verdict=result.get("verdict", "refine"),
        confidence=result.get("confidence", 0.7),
        assessment=result.get("assessment", {}),
        predicted_performance=result.get("predicted_performance", {}),
        refinements=result.get("refinements", [])
    )


def _parse_validation(response: str) -> Dict:
    """Parse validation response."""
    import json
    import re
    
    json_match = re.search(r'\{[\s\S]*\}', response)
    if not json_match:
        return {"verdict": "refine", "confidence": 0.5}
    
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        return {"verdict": "refine", "confidence": 0.5}


async def validate_batch(
    composed_clips: List[Dict],
    max_parallel: int = 5
) -> List[ValidatedClip]:
    """
    Validate multiple clips in parallel.
    
    Args:
        composed_clips: List of composed clip structures
        max_parallel: Limit concurrent API calls
        
    Returns:
        List of ValidatedClip objects
    """
    print(f"Validating {len(composed_clips)} clips (Parallel: {max_parallel})...")
    
    validated = []
    
    # Process in chunks to respect rate limits
    for i in range(0, len(composed_clips), max_parallel):
        batch = composed_clips[i:i+max_parallel]
        
        # Create tasks for current batch
        tasks = [validate_clip(clip) for clip in batch]
        
        # Run parallel
        results = await asyncio.gather(*tasks)
        
        # Combine results with original clips
        for clip, result in zip(batch, results):
            validated.append(ValidatedClip(
                clip=clip,
                validation=result
            ))
            
    return validated


async def rank_clips(
    validated_clips: List[ValidatedClip],
    target_count: int = 10
) -> List[ValidatedClip]:
    """
    Rank validated clips and select top N.
    Includes deduplication logic.
    """
    # Filter approved/refine clips
    approved = [
        vc for vc in validated_clips
        if vc.validation.verdict in ["approve", "refine"]
    ]
    
    if not approved:
        return []
    
    # --- Deduplication Logic (Helper Functions) ---
    
    def _parse_completion_range(value: object) -> float:
        import re
        if not isinstance(value, str): return 0.0
        nums = re.findall(r"(\d+(?:\.\d+)?)", value)
        if not nums: return 0.0
        floats = [float(n) for n in nums[:2]]
        if len(floats) == 1: return floats[0] / 100.0
        return ((floats[0] + floats[1]) / 2.0) / 100.0

    def _merged_intervals(segments: List[Dict]) -> List[tuple[float, float]]:
        intervals = []
        for s in segments:
            try:
                a, b = float(s.get("start", 0)), float(s.get("end", 0))
                if b > a: intervals.append((a, b))
            except Exception: continue
        if not intervals: return []
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for a, b in intervals[1:]:
            la, lb = merged[-1]
            if a <= lb: merged[-1] = (la, max(lb, b))
            else: merged.append((a, b))
        return merged

    def _overlap_duration(a: List[tuple], b: List[tuple]) -> float:
        i = j = 0
        total = 0.0
        while i < len(a) and j < len(b):
            a0, a1 = a[i]
            b0, b1 = b[j]
            start, end = max(a0, b0), min(a1, b1)
            if end > start: total += end - start
            if a1 <= b1: i += 1
            else: j += 1
        return total

    def _interval_total(intervals: List[tuple]) -> float:
        return sum((b - a) for a, b in intervals)

    def _clip_score(vc: ValidatedClip) -> float:
        pred = vc.validation.predicted_performance or {}
        completion = _parse_completion_range(pred.get("completion_rate", ""))
        return completion * 0.7 + float(vc.validation.confidence or 0) * 0.3

    # --- Apply Deduplication ---
    
    candidates = sorted(approved, key=_clip_score, reverse=True)
    diverse = []
    diverse_intervals = []
    OVERLAP_THRESHOLD = 0.65

    for vc in candidates:
        intervals = _merged_intervals(vc.clip.get("segments", []))
        if not intervals:
            diverse.append(vc); diverse_intervals.append([])
            continue

        is_dup = False
        vc_total = _interval_total(intervals) or 1e-9
        for existing in diverse_intervals:
            if not existing: continue
            ov = _overlap_duration(intervals, existing)
            ratio = ov / min(vc_total, (_interval_total(existing) or 1e-9))
            if ratio >= OVERLAP_THRESHOLD:
                is_dup = True
                break

        if not is_dup:
            diverse.append(vc)
            diverse_intervals.append(intervals)

    approved = diverse

    # --- AI Ranking ---

    clips_data = [
        {
            "id": i,
            "hook": vc.clip.get("hook_text", ""),
            "duration": vc.clip.get("total_duration", 0),
            "type": vc.clip.get("structure_type", ""),
            "assessment": vc.validation.assessment
        }
        for i, vc in enumerate(approved)
    ]
    
    system_prompt, user_prompt = build_final_ranking_prompt(clips_data, target_count)
    
    model = ClaudeModel("claude-sonnet-4-20250514")
    response = await model.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.3,
        cache_system=True  # Cache ranking instructions too
    )
    
    ranking_result = _parse_ranking(response.content)
    
    # Apply ranks
    final_clips = []
    
    # Map back from index to object
    for entry in ranking_result.get("final_selection", []):
        idx = entry.get("clip_index")
        if idx is not None and 0 <= idx < len(approved):
            clip = approved[idx]
            clip.rank = entry.get("rank", 999)
            final_clips.append(clip)
            
    # Fill up to target_count if AI selected fewer
    if len(final_clips) < target_count and len(final_clips) < len(approved):
        selected_ids = {c.clip.get('hook_text') for c in final_clips}
        for clip in approved:
            if clip.clip.get('hook_text') not in selected_ids:
                clip.rank = len(final_clips) + 1
                final_clips.append(clip)
                if len(final_clips) >= target_count:
                    break
    
    return final_clips[:target_count]


def _parse_ranking(response: str) -> Dict:
    import json
    import re
    json_match = re.search(r'\{[\s\S]*\}', response)
    return json.loads(json_match.group()) if json_match else {"final_selection": []}
