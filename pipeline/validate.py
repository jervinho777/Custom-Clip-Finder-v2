"""
STAGE 3: VALIDATE

Quality scoring using BRAIN patterns.
Uses Quality Oracle identity for final decisions.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

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
    
    Args:
        composed_clip: Composed clip structure from COMPOSE
        use_brain: Whether to use BRAIN for comparison
        
    Returns:
        ValidationResult with verdict and assessment
    """
    # Get BRAIN context
    similar_clips = []
    quality_signals = {}
    
    if use_brain:
        principles = load_principles()
        quality_signals = principles.get("quality_signals", {})
        
        # Find similar clips
        hook_text = composed_clip.get("hook_text", "")
        if hook_text:
            try:
                similar_clips = await get_similar_clips(hook_text, n_results=5)
            except Exception:
                pass
    
    # Build prompt
    system_prompt, user_prompt = build_validate_prompt(
        composed_clip=composed_clip,
        similar_clips=similar_clips,
        quality_signals=quality_signals
    )
    
    # Use Claude for validation (dynamic detection)
    from models.base import get_model
    model = get_model("anthropic", tier="sonnet")
    
    response = await model.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.3  # Low temperature for consistent scoring
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
    composed_clips: List[Dict]
) -> List[ValidatedClip]:
    """
    Validate multiple clips.
    
    Args:
        composed_clips: List of composed clip structures
        
    Returns:
        List of ValidatedClip objects
    """
    import asyncio
    
    validated = []
    
    for clip in composed_clips:
        result = await validate_clip(clip)
        
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
    
    Args:
        validated_clips: All validated clips
        target_count: How many to select
        
    Returns:
        Top clips with rank assigned
    """
    # Filter approved clips
    approved = [
        vc for vc in validated_clips
        if vc.validation.verdict in ["approve", "refine"]
    ]
    
    if not approved:
        return []
    
    # Build ranking prompt
    clips_data = [
        {
            "hook_text": vc.clip.get("hook_text", ""),
            "total_duration": vc.clip.get("total_duration", 0),
            "structure_type": vc.clip.get("structure_type", ""),
            "validation": {
                "assessment": vc.validation.assessment,
                "predicted_performance": vc.validation.predicted_performance
            }
        }
        for vc in approved
    ]
    
    system_prompt, user_prompt = build_final_ranking_prompt(clips_data, target_count)
    
    model = ClaudeModel("claude-sonnet-4-20250514")
    response = await model.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.3
    )
    
    # Parse ranking
    ranking = _parse_ranking(response.content)
    
    # Assign ranks
    ranked_clips = []
    for entry in ranking.get("final_selection", []):
        idx = entry.get("clip_index", 0)
        if 0 <= idx < len(approved):
            clip = approved[idx]
            clip.rank = entry.get("rank", len(ranked_clips) + 1)
            ranked_clips.append(clip)
    
    # Add remaining approved clips without rank
    ranked_indices = {entry.get("clip_index") for entry in ranking.get("final_selection", [])}
    for i, clip in enumerate(approved):
        if i not in ranked_indices:
            clip.rank = len(ranked_clips) + 1
            ranked_clips.append(clip)
    
    return ranked_clips[:target_count]


def _parse_ranking(response: str) -> Dict:
    """Parse ranking response."""
    import json
    import re
    
    json_match = re.search(r'\{[\s\S]*\}', response)
    if not json_match:
        return {"final_selection": []}
    
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        return {"final_selection": []}

