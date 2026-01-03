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
    
    # Include 90s before and 60s after for context
    # CRITICAL: Best hooks often come AFTER the story (payoff-as-hook pattern)
    context_start = max(0, start - 90)
    context_end = end + 60
    
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
    
    # Build composition context from BRAIN principles
    composition_context = ""
    if composition_patterns:
        composition_context = """
[COMPOSITION PATTERNS AUS BRAIN - LIES DIESE GENAU!]

🔥 HOOK EXTRACTION (340% höhere Completion Rate!)
   WANN: Wenn der natürliche Hook schwach ist, aber der Payoff stark
   WIE: Nimm den Payoff-Satz und stelle ihn an den ANFANG
   
   BEISPIEL (aus echten Viral-Daten):
   - "Arbeite niemals für Geld" kam bei 653s im Original (NACH der Geschichte)
   - Im viralen Clip: Dieser Satz wurde an den ANFANG gestellt
   - Dann folgt die Geschichte (Kinder ärgern Geschichte)
   - Dann der Rest des Payoffs
   
   WICHTIG: Schau auch NACH dem Moment-Fenster nach starken Hooks!
   Der beste Hook kommt oft 10-30 Sekunden NACH der Geschichte.

🎯 CLEAN EXTRACTION
   WANN: Wenn der natürliche Hook bereits stark ist (8+/10)
   WIE: Extrahiere mit minimalen Cuts, bewahre den natürlichen Flow

🧠 BELIEFBREAKER
   WANN: Speaker widerspricht einer Annahme die 99% glauben
   WIE: Führe mit dem kontraintuitiven Statement
   BEISPIEL: "Hört bitte auf am Wochenende auszuschlafen"

💡 METAPHOR HOOK
   WANN: Speaker nutzt starken Vergleich/Analogie
   WIE: Extrahiere den Vergleich als Hook
   BEISPIEL: "Schlafen ist wie Fußball spielen"

PRINZIP: Suche im GESAMTEN Kontext (auch NACH dem Moment!) nach dem Satz,
der am meisten Neugier erzeugt und zum Weiterschauen zwingt.
"""
    
    # Build round-specific instructions
    if round_num == 1:
        round_instruction = """
RUNDE 1: HOOK-SCAN + INITIAL PROPOSAL

SCHRITT 1: Scanne ALLE Sätze im Kontext (auch die NACH >>> dem Moment <<<)
- Welcher Satz erzeugt am meisten Neugier?
- Welcher Satz ist kurz, provokant, und macht Lust weiterzuschauen?
- Achte besonders auf Sätze die 10-60s NACH dem Moment kommen!

SCHRITT 2: Entscheide welcher Ansatz am besten passt:
- Clean Extraction: Wenn der natürliche Hook schon stark ist (8+/10)
- Hook Extraction: Wenn ein besserer Hook VOR oder NACH dem Moment existiert
- Beliefbreaker: Wenn ein kontraintuitiver Satz existiert

SCHRITT 3: Erstelle die Clip-Struktur mit dem stärksten Hook an Position 0
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
• Du DARFST Segmente von AUSSERHALB des >>> Moments <<< verwenden!
• Hook kann von VOR oder NACH dem Moment kommen
• Der beste Hook ist oft der Payoff-Satz der NACH der Geschichte kommt
• Hook muss in ersten 3 Sekunden Aufmerksamkeit fangen
• Achte auf saubere Satzgrenzen
• Frage dich: "Würde ICH bei diesem ersten Satz weiterschauen?"
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

