"""
STAGE 1: DISCOVER

Find viral moments in video transcripts.
Uses 5-AI ensemble with Algorithm Whisperer identity.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from models import AIEnsemble
from brain import load_principles, get_similar_clips
from prompts.discover import build_discover_prompt, parse_discover_response
from utils import Cache


@dataclass
class Moment:
    """A potential viral moment."""
    start: float
    end: float
    content_type: str
    hook_strength: int
    viral_potential: int
    reasoning: str
    similar_pattern: str
    votes: int = 0
    confidence: float = 0.0


async def discover_moments(
    transcript_segments: List[Dict],
    video_path: Optional[str] = None,
    use_cache: bool = True,
    min_consensus: int = 3
) -> List[Moment]:
    """
    Discover viral moments in a transcript.
    
    Uses 5-AI ensemble to find and vote on moments.
    
    Args:
        transcript_segments: List of transcript segments with start, end, text
        video_path: Optional path for caching
        use_cache: Whether to use cached results
        min_consensus: Minimum votes for a moment to be included
        
    Returns:
        List of Moment objects sorted by viral potential
    """
    cache = Cache()
    
    # Check cache
    if use_cache and video_path:
        cached = cache.get_pipeline_result(video_path, "discover")
        if cached:
            print("Using cached DISCOVER results")
            return [Moment(**m) for m in cached.get("result", {}).get("moments", [])]
    
    # Load BRAIN context
    principles = load_principles()
    
    # Get similar clips (if vector store initialized)
    similar_clips = []
    if transcript_segments:
        sample_text = " ".join(s.get("text", "") for s in transcript_segments[:5])
        try:
            similar_clips = await get_similar_clips(sample_text, n_results=5)
        except Exception:
            pass
    
    # Build prompt
    system_prompt, user_prompt = build_discover_prompt(
        transcript_segments=transcript_segments,
        similar_clips=similar_clips,
        principles=principles
    )
    
    print("Running DISCOVER with 5-AI ensemble...")
    
    # Run ensemble
    ensemble = AIEnsemble()
    response = await ensemble.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.7,
        min_consensus=min_consensus
    )
    
    print(f"Ensemble confidence: {response.confidence:.0%}")
    print(f"Total cost: ${response.total_cost:.4f}")
    
    # Parse response
    moments_data = parse_discover_response(response.consensus)
    
    # Convert to Moment objects
    moments = []
    for m in moments_data:
        moments.append(Moment(
            start=m["start"],
            end=m["end"],
            content_type=m["content_type"],
            hook_strength=m["hook_strength"],
            viral_potential=m["viral_potential"],
            reasoning=m["reasoning"],
            similar_pattern=m["similar_pattern"],
            confidence=response.confidence
        ))
    
    # Sort by viral potential
    moments.sort(key=lambda x: x.viral_potential, reverse=True)
    
    # Cache results
    if video_path:
        cache.set_pipeline_result(video_path, "discover", {
            "moments": [
                {
                    "start": m.start,
                    "end": m.end,
                    "content_type": m.content_type,
                    "hook_strength": m.hook_strength,
                    "viral_potential": m.viral_potential,
                    "reasoning": m.reasoning,
                    "similar_pattern": m.similar_pattern,
                    "confidence": m.confidence
                }
                for m in moments
            ],
            "ensemble_cost": response.total_cost,
            "ensemble_confidence": response.confidence
        })
    
    print(f"Discovered {len(moments)} moments")
    return moments


async def discover_with_voting(
    transcript_segments: List[Dict],
    top_n: int = 10
) -> List[Moment]:
    """
    Discover moments with multi-round voting.
    
    Each AI votes independently, then moments with
    highest consensus are selected.
    
    Args:
        transcript_segments: Transcript segments
        top_n: Number of top moments to return
        
    Returns:
        List of top moments by consensus
    """
    # Run standard discovery
    moments = await discover_moments(
        transcript_segments=transcript_segments,
        use_cache=False
    )
    
    # Already sorted by potential, take top N
    return moments[:top_n]

