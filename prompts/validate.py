"""
VALIDATE Stage Prompts (XML-Optimized)

Stage 3: Quality scoring using BRAIN patterns.
Uses Quality Oracle identity for final decisions.
Refactored to XML structure for optimal Prompt Caching performance.
"""

import json
from typing import List, Dict, Optional
from .identities import QUALITY_ORACLE


def build_validate_prompt(
    composed_clip: Dict,
    similar_clips: Optional[List[Dict]] = None,
    quality_signals: Optional[Dict] = None
) -> tuple[str, str]:
    """
    Build XML-structured prompt for VALIDATE stage.
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

    # 2. Prepare Clip Data
    clip_structure = {
        "type": composed_clip.get('structure_type', 'unknown'),
        "duration": round(composed_clip.get('total_duration', 0), 1),
        "hook": composed_clip.get('hook_text', 'N/A'),
        "segments": [
            {
                "role": s.get('role', 'unknown'),
                "duration": round(s.get('end', 0) - s.get('start', 0), 1)
            }
            for s in composed_clip.get('segments', [])
        ],
        "creator_reasoning": composed_clip.get('reasoning', 'N/A')
    }

    # 3. Build Prompt
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

<task>
    Bewerte diesen Clip als "Quality Oracle".
    Vergleiche ihn mit den <similar_successful_clips>.
    
    Entscheide:
    - APPROVE: Wenn Hook stark (7+/10) und Struktur sauber ist.
    - REFINE: Wenn Potential da ist, aber Optimierung möglich (Bevorzugt!).
    - REJECT: Nur bei totalem Müll.
</task>

<output_format>
    Antworte STRIKT mit diesem JSON:
    {{
      "verdict": "approve | refine | reject",
      "confidence": 0.85,
      "assessment": {{
        "hook_quality": {{ "rating": "strong", "reasoning": "..." }},
        "structure_quality": {{ "rating": "medium", "reasoning": "..." }},
        "viral_potential": {{ "rating": "high", "reasoning": "..." }}
      }},
      "predicted_performance": {{
        "completion_rate": "25-30%",
        "comparison": "Besser als Durchschnitt"
      }},
      "refinements": ["Vorschlag 1", "Vorschlag 2"]
    }}
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
