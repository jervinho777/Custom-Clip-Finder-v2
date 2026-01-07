"""
STAGE 2: COMPOSE

Restructure moments for maximum viral potential.
Uses 3-round debate with Viral Architect identity.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field

from models.base import ClaudeModel
from brain.learn import load_principles, get_principle_context_for_prompt
from prompts.compose import build_compose_prompt, build_debate_synthesis_prompt


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


async def compose_clip(
    moment: Dict,
    transcript_segments: List[Dict],
    debate_rounds: int = 3
) -> ComposedClip:
    """
    Compose a clip from a discovered moment.
    
    Uses multi-round debate to find optimal structure.
    
    Args:
        moment: Moment dict from DISCOVER stage
        transcript_segments: Full transcript
        debate_rounds: Number of debate rounds (default 3)
        
    Returns:
        ComposedClip with optimized structure
    """
    print(f"Composing clip for moment {moment.get('start', 0):.1f}s - {moment.get('end', 0):.1f}s")
    
    # Load composition patterns from BRAIN
    principles = load_principles()
    composition_patterns = principles.get("transformation_principles", [])
    
    # Get principle context for prompts (if available)
    principle_context = get_principle_context_for_prompt()
    
    # Use Claude Sonnet for debate (dynamic detection)
    from models.base import get_model
    model = get_model("anthropic", tier="sonnet")
    
    proposals = []
    
    # Run debate rounds
    for round_num in range(1, debate_rounds + 1):
        print(f"  Round {round_num}/{debate_rounds}...")
        
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
            proposals.append(proposal)
    
    # Synthesize final structure
    if len(proposals) >= 2:
        final = await _synthesize_debate(proposals, moment, model)
    elif proposals:
        final = proposals[-1]
    else:
        # Fallback to clean extraction
        final = _create_fallback_structure(moment)
    
    return ComposedClip(
        structure_type=final.get("structure_type", "clean_extraction"),
        segments=final.get("segments", []),
        total_duration=final.get("total_duration", moment.get("end", 0) - moment.get("start", 0)),
        hook_text=final.get("hook_text", ""),
        reasoning=final.get("reasoning", ""),
        predicted_completion_rate=final.get("predicted_completion_rate", "25-30%"),
        confidence=final.get("confidence", 0.7),
        original_moment=moment,
        debate_rounds=proposals
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

