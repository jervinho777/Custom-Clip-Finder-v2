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

from models.base import ClaudeModel
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
    structure_type: str  # clean_extraction, hook_extraction, reordered
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
    
    # Use Claude Sonnet for debate (dynamic detection)
    from models.base import get_model
    model = get_model("anthropic", tier="sonnet")
    
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
            temperature=0.7 if round_num < debate_rounds else 0.3
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
    
    return ComposedClip(
        structure_type=final.get("structure_type", "clean_extraction"),
        segments=final.get("segments", []),
        total_duration=final.get("total_duration", moment.get("end", 0) - moment.get("start", 0)),
        hook_text=final.get("hook_text", ""),
        reasoning=final.get("reasoning", ""),
        predicted_completion_rate=final.get("predicted_completion_rate", "25-30%"),
        confidence=final.get("confidence", 0.7),
        original_moment=moment,
        debate_rounds=proposals,
        viral_headline=viral_headline,
        headline_type=headline_type,
        headline_is_essential=headline_is_essential
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

