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
    
    # Get the moment boundaries
    start, end = moment['start'], moment['end']
    
    # PRINCIPLE-BASED: Give AI the FULL transcript context
    # The best hook could come from ANYWHERE in the video
    # No arbitrary time limits - let the AI decide based on principles
    relevant_segments = transcript_segments  # Full transcript
    
    # Mark which segments are in the discovered moment
    moment_segment_indices = set()
    for i, seg in enumerate(relevant_segments):
        seg_start = seg.get('start', 0)
        if start <= seg_start <= end:
            moment_segment_indices.add(i)
    
    # Format segments with timestamps
    # For long transcripts, show full context but truncate individual segment text
    segment_text = ""
    total_duration = transcript_segments[-1].get('end', 0) if transcript_segments else 0
    
    for i, seg in enumerate(relevant_segments):
        seg_start = seg.get('start', 0)
        in_moment = i in moment_segment_indices
        marker = ">>>" if in_moment else "   "
        
        # Show full text for segments in/near moment, abbreviated for distant ones
        text = seg.get('text', '')
        if not in_moment and abs(seg_start - start) > 120:
            # Distant segments: show first 80 chars to save tokens but maintain context
            text = text[:80] + "..." if len(text) > 80 else text
        
        segment_text += f"{marker} [{i}] [{seg_start:.1f}s] {text}\n"
    
    # Build composition context from BRAIN principles - PRINCIPLE-BASED, NO RIGID RULES
    composition_context = f"""
[PRINZIPIEN-BASIERTE KOMPOSITION - KEINE STARREN REGELN!]

📺 VIDEO-KONTEXT
   Gesamtdauer: {total_duration:.0f}s ({total_duration/60:.1f} Minuten)
   Der gefundene Moment (>>> markiert) ist nur der CONTENT-KERN.
   Der beste HOOK kann von ÜBERALL im Video kommen!

🎯 EINZIGES ZIEL: WATCHTIME MAXIMIEREN
   - Welcher Satz im GESAMTEN Video würde Menschen zum Weiterschauen zwingen?
   - Welche Struktur hält Menschen bis zum Ende?
   - Was macht im Gesamtkontext Sinn?

🔥 TRANSFORMATION PATTERNS (aus echten Viral-Daten):

   HOOK EXTRACTION (340% höhere Completion!)
   - "Arbeite niemals für Geld" kam bei 653s (NACH der Geschichte bei 564s)
   - Im viralen Clip: Dieser Satz wurde an Position 0 gestellt
   - PRINZIP: Der Payoff einer Geschichte kann der Hook einer anderen sein
   
   BELIEFBREAKER
   - "Hört bitte auf am Wochenende auszuschlafen"
   - PRINZIP: Was 99% glauben widersprechen = instant Attention
   
   METAPHOR HOOK
   - "Schlafen ist wie Fußball spielen"
   - PRINZIP: Komplexes mit Alltäglichem verbinden
   
   CLEAN EXTRACTION
   - Nur wenn der natürliche Hook bereits 8+/10 ist
   - PRINZIP: Nicht optimieren was schon perfekt ist

⚠️ KEINE STARREN REGELN:
   - KEIN "Hook muss innerhalb von X Sekunden sein"
   - KEIN "Story muss chronologisch sein"
   - KEINE festen Strukturen
   
   STATTDESSEN: Was würde DICH zum Weiterschauen zwingen?
   Denke wie ein Zuschauer, der durch den Feed scrollt.
"""
    
    # Build round-specific instructions
    if round_num == 1:
        round_instruction = """
RUNDE 1: PRINZIPIEN-BASIERTE ANALYSE

SCHRITT 1: Verstehe den CONTENT-KERN (>>> markierte Segmente)
- Was ist die Kernaussage/Geschichte?
- Warum hat DISCOVER diesen Moment als viral-fähig identifiziert?

SCHRITT 2: Scanne das GESAMTE Transcript nach dem perfekten HOOK
- Der beste Hook kann von ÜBERALL kommen (nicht nur nahe dem Moment!)
- Frage: Welcher einzelne Satz würde Menschen zum Stoppen bringen?
- Muss thematisch zum Content-Kern passen

SCHRITT 3: Strukturiere für MAXIMALE WATCHTIME
- Hook: Der Satz der zum Stoppen zwingt (kann von überall sein)
- Story/Content: Der eigentliche Moment (>>> Segmente)
- Payoff: Befriedigung die zum Fertigschauen motiviert

KEINE STARREN REGELN - nutze dein Urteil basierend auf den Prinzipien!
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
• Du KANNST Segmente von ÜBERALL im Video verwenden!
• KEINE Zeitlimits - wenn ein Satz von Minute 25 perfekt passt, nutze ihn
• Einzige Bedingung: Es muss thematisch Sinn machen und Watchtime maximieren
• Hook muss in ersten 3 Sekunden Aufmerksamkeit fangen
• Achte auf saubere Satzgrenzen
• Frage dich: "Würde ICH bei diesem ersten Satz weiterschauen?"
• Frage dich: "Macht dieser Clip als Ganzes Sinn?"
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

