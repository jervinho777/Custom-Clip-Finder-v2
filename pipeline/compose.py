"""
STAGE 2: COMPOSE

Restructure moments for maximum viral potential.
Uses 3-round debate with Viral Architect identity.

FUSION ENGINE INTEGRATION:
- Uses ViralBrainPrompt to combine 967+ clip analysis with editing tactics
- Dynamic prompts based on learned patterns
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field

from models.base import ClaudeModel, get_model, OPUS_MODEL_ID, SONNET_MODEL_ID
from brain.learn import load_principles, get_principle_context_for_prompt
from prompts.compose import build_compose_prompt, build_debate_synthesis_prompt
from prompts.viral_editor import ViralBrainPrompt


# =============================================================================
# Global Fusion Engine Instance
# =============================================================================

_viral_brain: Optional[ViralBrainPrompt] = None


def _get_viral_brain() -> ViralBrainPrompt:
    """Get or initialize the Viral Brain Fusion Engine."""
    global _viral_brain
    if _viral_brain is None:
        print("🧠 Initializing Viral Brain Fusion Engine...")
        _viral_brain = ViralBrainPrompt()
        stats = _viral_brain.get_stats()
        print(f"   ✅ Loaded: {stats['archetypes_loaded']} archetypes, {stats['rules_loaded']} rules, {stats['examples_loaded']} examples")
    return _viral_brain


@dataclass
class ComposedClip:
    """A composed/restructured clip."""
    structure_type: str  # clean_extraction, hook_extraction, reordered, council_remix
    segments: List[Dict]
    total_duration: float
    hook_text: str
    reasoning: str
    predicted_completion_rate: str = "25-30%"
    confidence: float = 0.0
    original_moment: Optional[Dict] = None
    debate_rounds: List[Dict] = field(default_factory=list)
    # VIRAL FACTORY: Headline für maximale Watchtime
    viral_headline: str = ""
    headline_type: str = ""  # problem, character, provokation
    headline_is_essential: bool = False  # True wenn Audio-Start Kontext braucht
    # V8: Adaptive Pacing
    pacing_mode: str = "density"  # density | immersion
    removed_safety_bridges: List[str] = field(default_factory=list)
    # V2 Validation: Original archetype für archetype-aware Validation
    archetype: str = "unknown"  # paradox_story, insight, contrarian_rant, etc.


# =============================================================================
# V8: ADAPTIVE PACING ENGINE - Ruthless Logic
# =============================================================================

# Safety Bridges Blacklist - Diese Sätze TÖTEN Viralität
SAFETY_BRIDGE_PATTERNS = [
    "versteh mich nicht falsch",
    "ich meine nicht, dass",
    "ich meine nicht dass",
    "ich sage nicht, dass",
    "ich sage nicht dass",
    "achtung, das ist wichtig",
    "lass mich erklären",
    "bevor ihr mich falsch versteht",
    "um fair zu sein",
    "das ist wichtig zu verstehen",
    "kurz zur erklärung",
    "ich möchte nur sagen",
    "ich will nur sagen",
    "das muss ich dazu sagen",
    "eine wichtige anmerkung",
    "ich erzähle euch eine geschichte",
    "ich möchte euch etwas zeigen",
    "heute geht es um",
    "in diesem video",
    "ich möchte heute über",
]


def remove_safety_bridges(text: str) -> tuple[str, list[str]]:
    """
    Entfernt Safety Bridges aus dem Text.
    
    Returns:
        Tuple von (cleaned_text, list of removed phrases)
    """
    if not text:
        return text, []
    
    cleaned = text
    removed = []
    
    for pattern in SAFETY_BRIDGE_PATTERNS:
        # Case-insensitive search
        import re
        matches = re.findall(rf'[^.!?]*{re.escape(pattern)}[^.!?]*[.!?]?', cleaned, re.IGNORECASE)
        
        for match in matches:
            if match.strip():
                removed.append(match.strip())
                cleaned = cleaned.replace(match, ' ')
    
    # Clean up multiple spaces
    cleaned = ' '.join(cleaned.split())
    
    return cleaned, removed


def apply_pacing_constraints(clip_data: Dict) -> Dict:
    """
    Wendet die harten Pacing-Constraints an.
    
    V8 Adaptive Pacing Engine:
    - DENSITY: Hook < 5s, Total < 60s, aggressives Kürzen
    - IMMERSION: Flexible Länge, atmosphärische Details bleiben
    
    Returns:
        Updated clip_data mit warnings/flags
    """
    pacing_mode = clip_data.get('pacing_mode', 'density')
    total_duration = clip_data.get('total_duration', 0)
    hook_duration = clip_data.get('hook_duration', 0)
    
    warnings = []
    flags = {
        'is_bloated': False,
        'hook_too_long': False,
        'requires_trim': False,
        'trim_percentage': 0
    }
    
    # ═══════════════════════════════════════════════════════════════
    # DENSITY MODE CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════
    if pacing_mode == 'density':
        # Hook max 7 seconds (hard limit) / ideal < 5s
        if hook_duration > 10:
            flags['hook_too_long'] = True
            warnings.append(f"⚠️ HOOK ZU LANG: {hook_duration:.0f}s > 10s (FORCE CUT erforderlich)")
        elif hook_duration > 7:
            warnings.append(f"⚠️ Hook grenzwertig: {hook_duration:.0f}s (ideal < 7s)")
        
        # Total max 60 seconds
        if total_duration > 60:
            flags['is_bloated'] = True
            flags['requires_trim'] = True
            # Calculate required trim percentage (30% of middle section)
            excess = total_duration - 60
            flags['trim_percentage'] = min(30, int((excess / total_duration) * 100))
            warnings.append(
                f"⚠️ BLOATED: {total_duration:.0f}s > 60s (DENSITY Mode). "
                f"Empfehlung: {flags['trim_percentage']}% Kürzung des Mittelteils."
            )
    
    # ═══════════════════════════════════════════════════════════════
    # IMMERSION MODE CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════
    elif pacing_mode == 'immersion':
        # Hook can be longer for scene-setting, but still has limits
        if hook_duration > 15:
            flags['hook_too_long'] = True
            warnings.append(f"⚠️ Hook auch für IMMERSION zu lang: {hook_duration:.0f}s > 15s")
        
        # Check for "turn" every 15 seconds (story pacing)
        if total_duration > 180 and not clip_data.get('has_turns', True):
            warnings.append("⚠️ Story > 3 Min ohne dokumentierte Wendungen. Prüfen!")
    
    # ═══════════════════════════════════════════════════════════════
    # UNIVERSAL CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════
    
    # Remove safety bridges from hook text
    hook_text = clip_data.get('hook_text', '')
    if hook_text:
        cleaned_hook, removed = remove_safety_bridges(hook_text)
        if removed:
            clip_data['hook_text'] = cleaned_hook
            clip_data['removed_safety_bridges'] = removed
            warnings.append(f"🧹 Entfernt {len(removed)} Safety Bridge(s) aus Hook")
    
    # ═══════════════════════════════════════════════════════════════
    # 🛡️ SANITY CHECK: Validate all segments (prevent FFmpeg crashes)
    # ═══════════════════════════════════════════════════════════════
    MIN_SEGMENT_DURATION = 3.0  # Minimum 3 seconds to prevent FFmpeg error -30599999
    
    segments = clip_data.get('segments', [])
    for seg in segments:
        seg_start = seg.get('start', 0)
        seg_end = seg.get('end', 0)
        seg_role = seg.get('role', 'unknown')
        
        if seg_end <= seg_start:
            # Invalid segment - fix it!
            fixed_end = seg_start + MIN_SEGMENT_DURATION
            print(f"   🛡️ SANITY CHECK: Fixing invalid segment {seg_role} ({seg_start:.1f}s -> {seg_end:.1f}s) → {fixed_end:.1f}s")
            seg['end'] = fixed_end
            warnings.append(f"🛡️ FIXED: Segment {seg_role} had end <= start (set to {MIN_SEGMENT_DURATION}s min)")
        
        # Also fix very short segments (< 1s) that might cause issues
        elif (seg_end - seg_start) < 1.0:
            fixed_end = seg_start + MIN_SEGMENT_DURATION
            print(f"   🛡️ SANITY CHECK: Extending too-short segment {seg_role} ({seg_end - seg_start:.1f}s) → {MIN_SEGMENT_DURATION}s")
            seg['end'] = fixed_end
            warnings.append(f"🛡️ FIXED: Segment {seg_role} too short (<1s, extended to {MIN_SEGMENT_DURATION}s)")
    
    # Add warnings to clip_data
    clip_data['pacing_warnings'] = warnings
    clip_data['pacing_flags'] = flags
    
    return clip_data


def force_hook_trim(hook_text: str, max_seconds: float = 7.0) -> str:
    """
    Trimmt einen Hook auf ca. max_seconds (geschätzt 2-3 Wörter/Sekunde).
    
    Returns:
        Gekürzter Hook-Text (erster Satz oder erste ~15 Wörter)
    """
    if not hook_text:
        return hook_text
    
    # Schätzung: ~2.5 Wörter pro Sekunde
    max_words = int(max_seconds * 2.5)
    
    # Split in Sätze
    sentences = hook_text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return hook_text
    
    # Nimm den ersten Satz
    first_sentence = sentences[0]
    words = first_sentence.split()
    
    if len(words) <= max_words:
        return first_sentence
    
    # Kürze auf max_words
    return ' '.join(words[:max_words]) + '...'


def validate_and_fix_segments(segments: List[Dict], min_duration: float = 3.0) -> List[Dict]:
    """
    🛡️ SAFETY VALVE: Validiert und repariert Segmente vor dem Export.
    
    Verhindert FFmpeg Fehler -30599999 durch:
    1. Prüfung auf end <= start
    2. Prüfung auf zu kurze Segmente
    3. Automatische Korrektur ungültiger Werte
    
    Args:
        segments: Liste der Clip-Segmente
        min_duration: Minimale Segment-Dauer (default: 3s)
        
    Returns:
        Bereinigte Segment-Liste
    """
    if not segments:
        return segments
    
    fixed_segments = []
    
    for seg in segments:
        seg_copy = seg.copy()  # Don't mutate original
        seg_start = seg_copy.get('start', 0)
        seg_end = seg_copy.get('end', 0)
        seg_role = seg_copy.get('role', 'unknown')
        
        # ═══════════════════════════════════════════════════════════════
        # CRITICAL FIX: end <= start → FFmpeg crash
        # ═══════════════════════════════════════════════════════════════
        if seg_end <= seg_start:
            print(f"   ⚠️ CRITICAL: Invalid segment detected! {seg_role}: end ({seg_end:.1f}s) <= start ({seg_start:.1f}s)")
            seg_copy['end'] = seg_start + min_duration
            print(f"   🛡️ FIXED: Resetting to safe duration: {seg_start:.1f}s → {seg_copy['end']:.1f}s")
        
        # ═══════════════════════════════════════════════════════════════
        # FIX: Too short segments (< 1s)
        # ═══════════════════════════════════════════════════════════════
        elif (seg_end - seg_start) < 1.0:
            print(f"   ⚠️ WARNING: Segment {seg_role} too short ({seg_end - seg_start:.2f}s)")
            seg_copy['end'] = seg_start + min_duration
            print(f"   🛡️ FIXED: Extended to {min_duration}s minimum")
        
        fixed_segments.append(seg_copy)
    
    return fixed_segments


async def compose_clip(
    moment: Dict,
    transcript_segments: List[Dict],
    debate_rounds: int = 3,
    use_fusion_engine: bool = True
) -> ComposedClip:
    """
    Compose a clip from a discovered moment.
    
    Uses multi-round debate to find optimal structure.
    Now powered by the Viral Brain Fusion Engine!
    
    Args:
        moment: Moment dict from DISCOVER stage
        transcript_segments: Full transcript
        debate_rounds: Number of debate rounds (default 3)
        use_fusion_engine: Use ViralBrainPrompt for dynamic prompts (default True)
        
    Returns:
        ComposedClip with optimized structure
    """
    print(f"Composing clip for moment {moment.get('start', 0):.1f}s - {moment.get('end', 0):.1f}s")
    
    # Initialize Fusion Engine
    if use_fusion_engine:
        viral_brain = _get_viral_brain()
        print("   🧠 Generated Dynamic Viral Prompt (Fusion Engine)")
    
    # Load composition patterns from BRAIN (legacy, still useful)
    principles = load_principles()
    composition_patterns = principles.get("transformation_principles", [])
    
    # Get principle context for prompts (if available)
    principle_context = get_principle_context_for_prompt()
    
    # 💎 HIGH-LEVERAGE: Opus für Compose/Editing (höchste Qualität!)
    try:
        model = get_model("anthropic", model=OPUS_MODEL_ID)
        print(f"   💎 Using OPUS for Compose (V8 Butcher Mode)")
    except ValueError:
        # Fallback to Sonnet if Opus unavailable
        model = get_model("anthropic", model=SONNET_MODEL_ID)
        print(f"   ⚠️ Opus unavailable, using Sonnet for Compose")
    
    proposals = []
    
    # Extract the raw transcript text for this moment
    moment_start = moment.get("start", 0)
    moment_end = moment.get("end", 0)
    raw_transcript = _extract_moment_text(transcript_segments, moment_start, moment_end)
    
    # Run debate rounds
    for round_num in range(1, debate_rounds + 1):
        print(f"  Round {round_num}/{debate_rounds}...")
        
        if use_fusion_engine and round_num == 1:
            # First round: Use Fusion Engine for maximum context
            fusion_instruction = viral_brain.build(raw_transcript)
            
            # CRITICAL: Append the JSON structure so the parser works correctly
            # Must match the schema expected by _parse_proposal() and ComposedClip
            format_instruction = """

═══════════════════════════════════════════════════════════════════════
⚠️ CRITICAL: OUTPUT FORMAT REQUIREMENT
═══════════════════════════════════════════════════════════════════════

You MUST output your response in valid JSON format matching this EXACT structure:

```json
{
  "structure_type": "hook_extraction | reordered | clean_extraction",
  "segments": [
    {
      "role": "hook",
      "start": <float: start time in seconds>,
      "end": <float: end time in seconds>,
      "text": "The hook text"
    },
    {
      "role": "body", 
      "start": <float>,
      "end": <float>,
      "text": "The body text"
    }
  ],
  "total_duration": <float: total clip duration>,
  "hook_text": "The first 1-2 sentences that grab attention",
  "edited_text": "The complete edited viral version of the transcript",
  "reasoning": "Why you made these specific edits and chose this structure",
  "predicted_completion_rate": "30-40%",
  "confidence": 0.85
}
```

RULES:
- Use the ORIGINAL timestamps from the transcript segments
- "segments" must include at least one segment with "role": "body"
- If you moved a hook from later in the video, include it as a separate segment with "role": "hook"
- Output ONLY the JSON, no additional text before or after
"""
            
            system_prompt = "You are an Elite Viral Video Editor. Follow the instructions exactly. Output ONLY valid JSON."
            user_prompt = fusion_instruction + format_instruction
        else:
            # Subsequent rounds: Use debate prompts
            system_prompt, user_prompt = build_compose_prompt(
                moment=moment,
                transcript_segments=transcript_segments,
                composition_patterns=composition_patterns,
                round_num=round_num,
                previous_proposals=proposals if round_num > 1 else None
            )
        
        response = await model.generate(
            prompt=user_prompt,
            system=system_prompt,
            temperature=0.7 if round_num < debate_rounds else 0.3,
            cache_system=True  # 🚀 Enable caching for Opus (90% cost savings!)
        )
        
        # Parse proposal
        proposal = _parse_proposal(response.content)
        if proposal:
            proposal["round"] = round_num
            if use_fusion_engine and round_num == 1:
                proposal["source"] = "fusion_engine"
            proposals.append(proposal)
    
    # Synthesize final structure
    if len(proposals) >= 2:
        final = await _synthesize_debate(proposals, moment, model)
    elif proposals:
        final = proposals[-1]
    else:
        # Fallback to clean extraction
        final = _create_fallback_structure(moment)
    
    # VIRAL FACTORY: Preserve headline from moment or extract from final
    viral_headline = (
        final.get("viral_headline") or 
        moment.get("viral_headline") or 
        ""
    )
    headline_type = final.get("headline_type", moment.get("headline_type", ""))
    headline_is_essential = final.get("headline_is_essential", moment.get("headline_is_essential", False))
    
    # V8: Extract pacing mode and apply constraints
    pacing_mode = final.get("pacing_mode", "density")
    removed_bridges = final.get("removed_safety_bridges", [])
    
    # Apply pacing constraints
    clip_data = {
        "pacing_mode": pacing_mode,
        "total_duration": final.get("total_duration", moment.get("end", 0) - moment.get("start", 0)),
        "hook_duration": final.get("hook_duration", 5),
        "hook_text": final.get("hook_text", ""),
        "has_turns": True  # Assume turns exist for now
    }
    clip_data = apply_pacing_constraints(clip_data)
    
    # Log warnings if any
    warnings = clip_data.get("pacing_warnings", [])
    if warnings:
        print(f"   ⚠️ Pacing Constraints ({pacing_mode.upper()}):")
        for w in warnings:
            print(f"      {w}")
    
    # Merge removed safety bridges
    all_removed = removed_bridges + clip_data.get("removed_safety_bridges", [])
    
    # ═══════════════════════════════════════════════════════════════
    # 🛡️ FINAL SAFETY VALVE: Validate all segments before export
    # ═══════════════════════════════════════════════════════════════
    raw_segments = final.get("segments", [])
    validated_segments = validate_and_fix_segments(raw_segments)
    
    # Recalculate total_duration after potential fixes
    if validated_segments:
        calculated_duration = sum(
            seg.get('end', 0) - seg.get('start', 0) 
            for seg in validated_segments
        )
    else:
        calculated_duration = final.get("total_duration", moment.get("end", 0) - moment.get("start", 0))
    
    return ComposedClip(
        structure_type=final.get("structure_type", "clean_extraction"),
        segments=validated_segments,
        total_duration=calculated_duration,
        hook_text=clip_data.get("hook_text", final.get("hook_text", "")),
        reasoning=final.get("reasoning", ""),
        predicted_completion_rate=final.get("predicted_completion_rate", "25-30%"),
        confidence=final.get("confidence", 0.7),
        original_moment=moment,
        debate_rounds=proposals,
        viral_headline=viral_headline,
        headline_type=headline_type,
        headline_is_essential=headline_is_essential,
        pacing_mode=pacing_mode,
        removed_safety_bridges=all_removed
    )


def _parse_proposal(response: str) -> Optional[Dict]:
    """Parse a composition proposal from AI response."""
    import json
    import re
    
    # Try to extract JSON
    json_match = re.search(r'\{[\s\S]*\}', response)
    if not json_match:
        return None
    
    try:
        proposal = json.loads(json_match.group())
        
        # Validate required fields
        if "segments" not in proposal:
            return None
        
        return proposal
    except json.JSONDecodeError:
        return None


async def _synthesize_debate(
    proposals: List[Dict],
    moment: Dict,
    model: ClaudeModel
) -> Dict:
    """Synthesize debate results into final structure."""
    system_prompt, user_prompt = build_debate_synthesis_prompt(proposals, moment)
    
    response = await model.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.3
    )
    
    result = _parse_proposal(response.content)
    
    if result and "final_structure" in result:
        final = result["final_structure"]
        final["confidence"] = result.get("confidence", 0.8)
        return final
    elif result:
        result["confidence"] = 0.7
        return result
    
    # Fallback to last proposal
    return proposals[-1]


def _create_fallback_structure(moment: Dict) -> Dict:
    """Create fallback clean extraction structure."""
    return {
        "structure_type": "clean_extraction",
        "segments": [
            {
                "role": "content",
                "start": moment.get("start", 0),
                "end": moment.get("end", 0)
            }
        ],
        "total_duration": moment.get("end", 0) - moment.get("start", 0),
        "hook_text": "",
        "reasoning": "Fallback clean extraction",
        "confidence": 0.5
    }


def _extract_moment_text(
    transcript_segments: List[Dict],
    start_time: float,
    end_time: float
) -> str:
    """
    Extract raw transcript text for a specific time range.
    
    Args:
        transcript_segments: List of transcript segments with start, end, text
        start_time: Start time in seconds
        end_time: End time in seconds
        
    Returns:
        Concatenated text from matching segments
    """
    texts = []
    
    for segment in transcript_segments:
        seg_start = segment.get("start", 0)
        seg_end = segment.get("end", 0)
        
        # Check for overlap
        if seg_end >= start_time and seg_start <= end_time:
            text = segment.get("text", "")
            if text:
                texts.append(text)
    
    return " ".join(texts)


async def compose_batch(
    moments: List[Dict],
    transcript_segments: List[Dict],
    max_parallel: int = 3
) -> List[ComposedClip]:
    """
    Compose multiple clips in parallel.
    
    Args:
        moments: List of moments to compose
        transcript_segments: Full transcript
        max_parallel: Max parallel compositions
        
    Returns:
        List of ComposedClip objects
    """
    import asyncio
    
    results = []
    
    for i in range(0, len(moments), max_parallel):
        batch = moments[i:i+max_parallel]
        
        tasks = [
            compose_clip(m, transcript_segments)
            for m in batch
        ]
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, ComposedClip):
                results.append(result)
            else:
                print(f"Composition failed: {result}")
    
    return results

