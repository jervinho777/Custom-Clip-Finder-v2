"""
COMPOSE Stage Prompts

Stage 2: Restructure moments for maximum viral potential.
Uses 3-round debate with Viral Architect identity.
"""

from typing import List, Dict, Optional
from .identities import VIRAL_ARCHITECT


def build_compose_prompt(
    moment: Dict,
    transcript_segments: List[Dict],
    composition_patterns: Optional[Dict] = None,
    round_num: int = 1,
    previous_proposals: Optional[List[Dict]] = None
) -> tuple[str, str]:
    """
    Build prompt for COMPOSE stage.
    
    Args:
        moment: The moment to compose (from DISCOVER)
        transcript_segments: Full transcript for context
        composition_patterns: Patterns from BRAIN
        round_num: Debate round (1-3)
        previous_proposals: Proposals from previous rounds
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = VIRAL_ARCHITECT
    
    # Get segments around the moment
    start, end = moment['start'], moment['end']
    
    # Include 30s before and after for context
    context_start = max(0, start - 30)
    context_end = end + 30
    
    relevant_segments = [
        seg for seg in transcript_segments
        if context_start <= seg.get('start', 0) <= context_end
    ]
    
    # Format segments with timestamps
    segment_text = ""
    for i, seg in enumerate(relevant_segments):
        seg_start = seg.get('start', 0)
        in_moment = start <= seg_start <= end
        marker = ">>>" if in_moment else "   "
        segment_text += f"{marker} [{i}] [{seg_start:.1f}s] {seg.get('text', '')}\n"
    
    # Build composition context
    composition_context = ""
    if composition_patterns:
        composition_context = "\n[COMPOSITION PATTERNS AUS BRAIN]\n"
        if 'hook_extraction' in composition_patterns:
            composition_context += f"• Hook Extraction: {composition_patterns['hook_extraction'].get('principle', '')}\n"
        if 'cutting_principles' in composition_patterns:
            composition_context += f"• Cutting: {composition_patterns['cutting_principles'].get('principle', '')}\n"
    
    # Build round-specific instructions
    if round_num == 1:
        round_instruction = """
RUNDE 1: INITIAL PROPOSAL
Erstelle deinen ersten Vorschlag für die Clip-Struktur.
Denke über verschiedene Ansätze nach:
- Clean Extraction (wenn Hook natürlich stark ist)
- Hook Extraction (wenn Payoff als Hook besser wäre)
- Reihenfolge ändern (wenn Story-Flow verbessert werden kann)
"""
    elif round_num == 2:
        prev_proposals_text = "\n".join([
            f"Vorschlag {i+1}: {p.get('structure_type', 'unknown')}"
            for i, p in enumerate(previous_proposals or [])
        ])
        round_instruction = f"""
RUNDE 2: KRITIK & VERBESSERUNG
Bisherige Vorschläge:
{prev_proposals_text}

Analysiere die bisherigen Vorschläge:
- Was funktioniert gut?
- Was könnte besser sein?
- Erstelle einen VERBESSERTEN Vorschlag
"""
    else:
        round_instruction = """
RUNDE 3: FINALE SYNTHESE
Erstelle die FINALE Clip-Struktur.
Kombiniere die besten Elemente aus allen Runden.
Diese Struktur wird für den Export verwendet.
"""
    
    user_prompt = f"""
{composition_context}

[MOMENT INFO]
Start: {start:.1f}s | Ende: {end:.1f}s | Dauer: {end-start:.1f}s
Content Type: {moment.get('content_type', 'unknown')}
Hook Strength: {moment.get('hook_strength', 5)}/10
Viral Potential: {moment.get('viral_potential', 5)}/10

[KONTEXT & MOMENT (>>> = im Moment)]
{segment_text}

{round_instruction}

[OUTPUT FORMAT]
```json
{{
  "structure_type": "clean_extraction | hook_extraction | reordered",
  "segments": [
    {{
      "role": "hook | context | content | payoff",
      "segment_indices": [0, 1, 2],
      "start": 45.2,
      "end": 52.1
    }}
  ],
  "total_duration": 55.3,
  "hook_text": "Der erste Satz des Clips",
  "reasoning": "Warum diese Struktur optimal ist",
  "predicted_completion_rate": "25-30%"
}}
```

WICHTIG:
• segment_indices verweisen auf die Segmente oben [0], [1], etc.
• Jedes Segment braucht start/end Timestamps
• Hook muss in ersten 3 Sekunden Aufmerksamkeit fangen
• Achte auf saubere Satzgrenzen
"""
    
    return system, user_prompt.strip()


def build_debate_synthesis_prompt(
    proposals: List[Dict],
    moment: Dict
) -> tuple[str, str]:
    """
    Build prompt for synthesizing debate results.
    
    Args:
        proposals: All proposals from debate rounds
        moment: Original moment
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = VIRAL_ARCHITECT
    
    proposals_text = ""
    for i, p in enumerate(proposals, 1):
        proposals_text += f"""
--- VORSCHLAG {i} ---
Typ: {p.get('structure_type', 'unknown')}
Dauer: {p.get('total_duration', 0):.1f}s
Hook: {p.get('hook_text', 'N/A')[:100]}
Begründung: {p.get('reasoning', 'N/A')}
"""
    
    user_prompt = f"""
[ALLE VORSCHLÄGE]
{proposals_text}

[ORIGINAL MOMENT]
Start: {moment['start']:.1f}s | Ende: {moment['end']:.1f}s
Viral Potential: {moment.get('viral_potential', 5)}/10

[TASK]
Wähle den BESTEN Vorschlag oder kombiniere die besten Elemente.
Erstelle die FINALE Struktur die für den Export verwendet wird.

Kriterien:
1. Stärkster Hook (ersten 3 Sekunden)
2. Höchste predicted Completion Rate
3. Sauberste Schnitte
4. Vollständige Gedanken

[OUTPUT FORMAT]
```json
{{
  "final_structure": {{
    "structure_type": "...",
    "segments": [...],
    "total_duration": ...,
    "hook_text": "...",
    "reasoning": "..."
  }},
  "confidence": 0.85,
  "selected_from": "proposal_3 with modifications"
}}
```
"""
    
    return system, user_prompt.strip()

