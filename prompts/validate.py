"""
VALIDATE Stage Prompts (XML-Optimized, V2 - Archetype-Aware)

Stage 3: Quality scoring using BRAIN patterns.
Uses Quality Oracle identity for final decisions.
Refactored to XML structure for optimal Prompt Caching performance.

V2 Changes:
- Länge wird RELATIV zum Archetyp bewertet (Stories dürfen länger sein)
- Council Remixes bekommen mehr Vertrauen (structure pre-validated)
- Circular Loop Bonus (Hook = Ende vorwegnehmen = Strong)
"""

import json
from typing import List, Dict, Optional
from .identities import QUALITY_ORACLE


# =============================================================================
# 🎯 ARCHETYPE-SPECIFIC DURATION RULES
# =============================================================================

ARCHETYPE_DURATION_RULES = {
    "paradox_story": {"optimal": (45, 90), "max": 120, "type": "immersion"},
    "emotional": {"optimal": (45, 90), "max": 120, "type": "immersion"},
    "story": {"optimal": (45, 90), "max": 120, "type": "immersion"},
    "insight": {"optimal": (20, 45), "max": 60, "type": "density"},
    "contrarian_rant": {"optimal": (30, 60), "max": 75, "type": "density"},
    "listicle": {"optimal": (30, 60), "max": 90, "type": "density"},
    "tutorial": {"optimal": (30, 60), "max": 90, "type": "density"},
    "council_remix": {"optimal": (30, 90), "max": 120, "type": "flexible"},
    "unknown": {"optimal": (20, 60), "max": 90, "type": "density"},
}


def build_validate_prompt(
    composed_clip: Dict,
    similar_clips: Optional[List[Dict]] = None,
    quality_signals: Optional[Dict] = None
) -> tuple[str, str]:
    """
    Build XML-structured prompt for VALIDATE stage.
    
    V2: Archetype-aware validation with flexible duration rules.
    """
    system = QUALITY_ORACLE
    
    # 1. Prepare BRAIN Data
    brain_data = []
    if similar_clips:
        for clip in similar_clips[:5]:
            meta = clip.get('metadata', {}) or clip
            brain_data.append({
                "hook": (meta.get('hook') or clip.get('text', ''))[:100],
                "views": meta.get('views', 0),
                "completion_rate": meta.get('completion_rate', 'N/A')
            })

    signals_data = []
    if quality_signals:
        for k, v in list(quality_signals.items())[:5]:
            signals_data.append(f"{k}: {v.get('description', str(v)) if isinstance(v, dict) else str(v)}")

    # 2. Prepare Clip Data with Archetype Context
    structure_type = composed_clip.get('structure_type', 'unknown')
    archetype = composed_clip.get('archetype', structure_type)
    duration = composed_clip.get('total_duration', 0)
    
    # Get archetype-specific rules
    archetype_key = archetype.lower() if archetype else 'unknown'
    if 'remix' in structure_type.lower() or 'council' in structure_type.lower():
        archetype_key = 'council_remix'
    
    duration_rules = ARCHETYPE_DURATION_RULES.get(archetype_key, ARCHETYPE_DURATION_RULES['unknown'])
    
    # Analyze cut points for Flow-Physics
    segments = composed_clip.get('segments', [])
    segment_analysis = []
    unsafe_cuts = []
    
    for i, s in enumerate(segments):
        text = s.get('text', '')
        last_char = text.strip()[-1] if text.strip() else ''
        is_safe_cut = last_char in {'.', '!', '?', '。', '！', '？'}
        ends_incomplete = last_char in {',', ':', ';', '-', '–'} or text.strip().endswith(('und', 'aber', 'weil', 'dass', 'wenn', 'oder'))
        
        seg_info = {
            "role": s.get('role', 'unknown'),
            "duration": round(s.get('end', 0) - s.get('start', 0), 1),
            "end_text": text[-30:] if text else "N/A",  # Last 30 chars for cut analysis
            "is_safe_cut": is_safe_cut,
            "needs_crossfade": ends_incomplete and i < len(segments) - 1  # Not last segment
        }
        segment_analysis.append(seg_info)
        
        if ends_incomplete and i < len(segments) - 1:
            unsafe_cuts.append({
                "segment_index": i,
                "end_text": text[-50:] if text else "",
                "reason": "Sentence incomplete (comma/conjunction)"
            })
    
    clip_structure = {
        "type": structure_type,
        "archetype": archetype,
        "duration": round(duration, 1),
        "duration_context": {
            "optimal_range": f"{duration_rules['optimal'][0]}-{duration_rules['optimal'][1]}s",
            "max_allowed": f"{duration_rules['max']}s",
            "pacing_mode": duration_rules['type'],
            "is_within_optimal": duration_rules['optimal'][0] <= duration <= duration_rules['optimal'][1],
            "is_within_max": duration <= duration_rules['max']
        },
        "hook": composed_clip.get('hook_text', 'N/A'),
        "segments": segment_analysis,
        "flow_physics": {
            "unsafe_cuts_detected": len(unsafe_cuts),
            "unsafe_cut_details": unsafe_cuts[:3],  # First 3 for context
            "overall_flow_risk": "high" if len(unsafe_cuts) >= 2 else "medium" if len(unsafe_cuts) == 1 else "low"
        },
        "is_council_remix": 'remix' in structure_type.lower() or 'council' in structure_type.lower(),
        "creator_reasoning": composed_clip.get('reasoning', 'N/A')
    }

    # 3. Build Prompt with Archetype-Aware Rules
    user_prompt = f"""
<viral_brain_context>
    <similar_successful_clips>
{json.dumps(brain_data, indent=2, ensure_ascii=False)}
    </similar_successful_clips>
    <quality_signals>
{json.dumps(signals_data, indent=2, ensure_ascii=False)}
    </quality_signals>
</viral_brain_context>

<candidate_clip>
{json.dumps(clip_structure, indent=2, ensure_ascii=False)}
</candidate_clip>

<validation_rules>
    ⚠️ KRITISCH - LIES DIESE REGELN BEVOR DU BEWERTEST:
    
    ═══════════════════════════════════════════════════════════════════════════════
    🔬 FLOW-PHYSIK (ERSTER PRÜFPUNKT - NICHT IGNORIEREN!):
    ═══════════════════════════════════════════════════════════════════════════════
    
    Analysiere die "flow_physics" im JSON:
    
    - Wenn unsafe_cuts_detected > 0: PRÜFE die Schnittstellen!
      → Segment endet mit Punkt ("...für Geld.") = ✓ Safe Cut
      → Segment endet mit Komma ("...weil,") = ⚠️ Unsafe Cut → needs_crossfade: true
      
    - Wenn overall_flow_risk == "high": 
      → Der Clip hat harte Schnitte an grammatikalisch falschen Stellen
      → REFINE mit Hinweis: "Unsichere Schnitte bei Segment X und Y gefunden"
    
    ═══════════════════════════════════════════════════════════════════════════════
    
    1. LÄNGE RELATIV ZUM ARCHETYP:
       - Stories/Parabeln (paradox_story, emotional): 45-90s sind OPTIMAL, bis 120s OK
       - Insights/Rants (insight, contrarian_rant): 20-45s optimal, bis 60s OK
       - Bestrafe Länge NUR wenn Content "bloated" (Wiederholungen, Füller) wirkt
       - Ein 50s Story-Clip ist BESSER als ein 25s Fragment!
    
    2. COUNCIL REMIX VERTRAUEN:
       - Wenn is_council_remix == true: Die Struktur wurde von 5 Top-AIs validiert
       - Prüfe primär "Flow-Physik" und "Logik-Lücken", NICHT starre Zeitgrenzen
       - Ein Remix hat bereits den Surgeon-Test bestanden
    
    3. CIRCULAR LOOP BONUS:
       - Wenn der Hook (Anfang) das Ende vorwegnimmt = "Open Loop" = STRONG
       - Beispiel: "Arbeite niemals für Geld" -> Story -> Erklärung = VIRAL
       - Das ist ein PREMIUM-Muster, bewerte es entsprechend hoch
    
    4. HOOK-QUALITÄT > LÄNGE:
       - Ein starker Hook (8+/10) mit 60s Clip = APPROVE
       - Ein schwacher Hook mit 20s Clip = REFINE oder REJECT
</validation_rules>

<task>
    Bewerte diesen Clip als "Quality Oracle".
    
    PRÜFE IN DIESER REIHENFOLGE:
    1. Hook-Stärke: Würde ICH stoppen? (0-3 Sek Test)
    2. Circular Loop: Nimmt der Hook das Ende vorweg? → +2 Bonus
    3. Flow: Gibt es Brüche oder fühlt sich die Story natürlich an?
    4. Länge (RELATIV): Nur bestrafen wenn "bloated", nicht weil > 30s
    
    Entscheide:
    - APPROVE: Hook stark (7+/10) UND Struktur sauber (auch bei 60-90s!)
    - REFINE: Potential da, aber kleine Optimierung möglich
    - REJECT: Nur bei totalem Müll (schwacher Hook + chaotische Struktur)
</task>

<output_format>
    Antworte STRIKT mit diesem JSON:
    {{
      "verdict": "approve | refine | reject",
      "confidence": 0.85,
      "assessment": {{
        "hook_quality": {{ "rating": "strong | medium | weak", "score": 8, "reasoning": "..." }},
        "structure_quality": {{ "rating": "strong | medium | weak", "reasoning": "..." }},
        "length_assessment": {{ "rating": "optimal | acceptable | bloated", "reasoning": "..." }},
        "flow_physics": {{
          "rating": "smooth | acceptable | choppy",
          "unsafe_cuts_found": 0,
          "needs_crossfade": false,
          "reasoning": "Alle Schnitte an Satz-Enden (Punkte)."
        }},
        "circular_loop_detected": true,
        "viral_potential": {{ "rating": "high | medium | low", "reasoning": "..." }}
      }},
      "predicted_performance": {{
        "completion_rate": "25-30%",
        "comparison": "Besser als Durchschnitt"
      }},
      "refinements": ["Vorschlag 1", "Vorschlag 2"],
      "crossfade_segments": []
    }}
    
    WICHTIG für Flow-Physik:
    - Wenn flow_physics.rating == "choppy": verdict sollte "refine" sein
    - Wenn needs_crossfade == true: Füge betroffene Segment-Indices in "crossfade_segments" ein
</output_format>
"""
    
    return system, user_prompt.strip()


def build_final_ranking_prompt(
    validated_clips: List[Dict],
    target_count: int = 10
) -> tuple[str, str]:
    """
    Build XML-structured prompt for final ranking.
    """
    system = QUALITY_ORACLE
    
    # Prepare data specifically for ranking (metadata only)
    ranking_candidates = []
    for i, item in enumerate(validated_clips):
        # Handle both list of dicts (if pre-processed) or list of objects
        # The validate pipeline passes a dict with 'id', 'hook', etc.
        ranking_candidates.append(item)

    user_prompt = f"""
<task_context>
    Wir haben eine Auswahl validierter Clips.
    Wähle die TOP {target_count} für den Export.
</task_context>

<candidates>
{json.dumps(ranking_candidates, indent=2, ensure_ascii=False)}
</candidates>

<ranking_criteria>
    1. Hook-Stärke (Der Scroll-Stopper ist alles).
    2. Content-Diversität (Nicht 5x das gleiche Thema).
    3. Viral-Potential (Predicted Performance).
</ranking_criteria>

<output_format>
    Antworte mit JSON:
    {{
      "final_selection": [
        {{ "rank": 1, "clip_index": 0, "reasoning": "..." }},
        {{ "rank": 2, "clip_index": 4, "reasoning": "..." }}
      ]
    }}
    WICHTIG: Nutze "clip_index" passend zur ID/Position in der <candidates> Liste.
</output_format>
"""
    
    return system, user_prompt.strip()
