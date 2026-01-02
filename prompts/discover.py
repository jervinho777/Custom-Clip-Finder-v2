"""
DISCOVER Stage Prompts

Stage 1: Find viral moments in transcripts.
Uses 5-AI ensemble with Algorithm Whisperer identity.
"""

from typing import List, Dict, Optional
from .identities import ALGORITHM_WHISPERER


def build_discover_prompt(
    transcript_segments: List[Dict],
    similar_clips: Optional[List[Dict]] = None,
    principles: Optional[Dict] = None,
    num_moments: int = 15
) -> tuple[str, str]:
    """
    Build prompt for DISCOVER stage.
    
    Args:
        transcript_segments: List of transcript segments with start, end, text
        similar_clips: Optional list of similar successful clips from BRAIN
        principles: Optional principles from PRINCIPLES.json
        num_moments: Target number of moments to find
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = ALGORITHM_WHISPERER
    
    # Build context from BRAIN if available
    context = ""
    
    if similar_clips:
        context += "\n[KONTEXT AUS BRAIN - Ähnliche erfolgreiche Clips]\n"
        for i, clip in enumerate(similar_clips[:5], 1):
            views = clip.get('views', 'N/A')
            hook = clip.get('hook', clip.get('text', '')[:100])
            context += f"{i}. {views:,} Views: \"{hook}...\"\n"
    
    if principles:
        context += "\n[KERN-PRINZIPIEN]\n"
        for key, value in list(principles.items())[:5]:
            if isinstance(value, dict) and 'principle' in value:
                context += f"• {value['principle']}\n"
            elif isinstance(value, str):
                context += f"• {value}\n"
    
    # Format transcript
    transcript_text = ""
    for seg in transcript_segments:
        start = seg.get('start', 0)
        text = seg.get('text', '')
        transcript_text += f"[{start:.1f}s] {text}\n"
    
    # Truncate if too long
    if len(transcript_text) > 15000:
        transcript_text = transcript_text[:15000] + "\n[...gekürzt...]"
    
    user_prompt = f"""
{context}

[TRANSCRIPT]
{transcript_text}

[TASK]
Analysiere dieses Transcript und identifiziere {num_moments}-20 Momente 
die viral gehen könnten.

Für jeden Moment:
• Start/End Timestamp (in Sekunden)
• Content Type: story | insight | tutorial | emotional | controversial
• Hook Strength (1-10): Wie stark ist der natürliche Hook?
• Viral Potential (1-10): Basierend auf deiner Erfahrung
• Begründung: WARUM dieser Moment Potential hat (1-2 Sätze)
• Ähnlicher Erfolg: Welchem erfolgreichen Pattern ähnelt er?

[CONSTRAINTS]
• Kein Moment unter 20 Sekunden
• Kein Moment über 90 Sekunden  
• Nur VOLLSTÄNDIGE Gedanken (keine Cliffhanger ohne Payoff)
• Bevorzuge Momente mit starkem natürlichen Hook
• Output als JSON Array

[OUTPUT FORMAT]
```json
[
  {{
    "start": 45.2,
    "end": 78.5,
    "content_type": "story",
    "hook_strength": 8,
    "viral_potential": 9,
    "reasoning": "Paradox-Statement öffnet Loop, emotionale Payoff",
    "similar_pattern": "Dieter Lange Lebenslinie"
  }}
]
```
"""
    
    return system, user_prompt.strip()


def parse_discover_response(response: str) -> List[Dict]:
    """
    Parse DISCOVER stage response into structured moments.
    
    Args:
        response: Raw AI response (should contain JSON)
        
    Returns:
        List of moment dicts
    """
    import json
    import re
    
    # Try to extract JSON from response
    json_match = re.search(r'\[[\s\S]*\]', response)
    if not json_match:
        return []
    
    try:
        moments = json.loads(json_match.group())
        
        # Validate and clean moments
        valid_moments = []
        for m in moments:
            if not isinstance(m, dict):
                continue
            if 'start' not in m or 'end' not in m:
                continue
            
            # Ensure required fields
            valid_moments.append({
                "start": float(m.get('start', 0)),
                "end": float(m.get('end', 0)),
                "content_type": m.get('content_type', 'unknown'),
                "hook_strength": int(m.get('hook_strength', 5)),
                "viral_potential": int(m.get('viral_potential', 5)),
                "reasoning": m.get('reasoning', ''),
                "similar_pattern": m.get('similar_pattern', '')
            })
        
        return valid_moments
    
    except json.JSONDecodeError:
        return []

