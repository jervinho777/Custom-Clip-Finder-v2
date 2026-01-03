"""
VALIDATE Stage Prompts

Stage 3: Quality scoring using BRAIN patterns.
Uses Quality Oracle identity for final decisions.
"""

from typing import List, Dict, Optional
from .identities import QUALITY_ORACLE


def build_validate_prompt(
    composed_clip: Dict,
    similar_clips: Optional[List[Dict]] = None,
    quality_signals: Optional[Dict] = None
) -> tuple[str, str]:
    """
    Build prompt for VALIDATE stage.
    
    Args:
        composed_clip: Composed clip structure from COMPOSE
        similar_clips: Similar clips from BRAIN with performance data
        quality_signals: Quality signals from PRINCIPLES.json
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = QUALITY_ORACLE
    
    # Build BRAIN context
    brain_context = ""
    
    if similar_clips:
        brain_context += "\n[ÄHNLICHE CLIPS AUS BRAIN]\n"
        for i, clip in enumerate(similar_clips[:5], 1):
            # Views can be in metadata (from vector store) or top-level
            metadata = clip.get('metadata', {})
            views = metadata.get('views') or clip.get('views', 0)
            completion = metadata.get('completion_rate') or clip.get('completion_rate', 0)
            hook = metadata.get('hook') or clip.get('hook') or clip.get('text', '')[:80]
            
            # Format views and completion safely (could be 'N/A' string)
            if isinstance(views, (int, float)):
                views_str = f"{int(views):,}"
            else:
                views_str = str(views)
            
            if isinstance(completion, (int, float)):
                completion_str = f"{completion:.0%}"
            else:
                completion_str = str(completion) if completion else "N/A"
            
            brain_context += f"{i}. {views_str} Views | {completion_str} Completion\n"
            brain_context += f"   Hook: \"{hook[:80]}...\"\n"
    
    if quality_signals:
        brain_context += "\n[QUALITY SIGNALS]\n"
        for signal, data in list(quality_signals.items())[:5]:
            if isinstance(data, dict):
                brain_context += f"• {signal}: {data.get('description', str(data))}\n"
    
    # Format clip structure
    clip_info = f"""
[CLIP STRUKTUR]
Typ: {composed_clip.get('structure_type', 'unknown')}
Dauer: {composed_clip.get('total_duration', 0):.1f}s
Hook: "{composed_clip.get('hook_text', 'N/A')}"

Segmente:
"""
    for seg in composed_clip.get('segments', []):
        start = seg.get('start', 0)
        end = seg.get('end', 0)
        duration = end - start
        clip_info += f"  • {seg.get('role', 'unknown')}: {duration:.1f}s (Video: {start:.1f}s-{end:.1f}s)\n"
    
    clip_info += f"\nBegründung: {composed_clip.get('reasoning', 'N/A')}"
    
    user_prompt = f"""
{brain_context}

{clip_info}

[TASK]
Bewerte diesen Clip basierend auf deiner Erfahrung und den BRAIN-Daten.

WICHTIG: KEIN starres Scoring-System!
Nutze dein Urteil als Quality Oracle.
Vergleiche mit ähnlichen erfolgreichen Clips.

[OUTPUT FORMAT]
```json
{{
  "verdict": "approve | refine | reject",
  "confidence": 0.85,
  
  "assessment": {{
    "hook_quality": {{
      "rating": "strong | medium | weak",
      "reasoning": "Warum dieser Hook funktioniert/nicht funktioniert"
    }},
    "structure_quality": {{
      "rating": "strong | medium | weak",
      "reasoning": "Bewertung der Clip-Struktur"
    }},
    "viral_potential": {{
      "rating": "high | medium | low",
      "reasoning": "Basierend auf BRAIN-Vergleich"
    }}
  }},
  
  "predicted_performance": {{
    "views_range": "100K-500K",
    "completion_rate": "25-30%",
    "comparison": "Ähnlich wie [Clip X] der Y Views hatte"
  }},
  
  "refinements": [
    "Optional: Verbesserungsvorschläge falls verdict != approve"
  ]
}}
```

ENTSCHEIDUNGSKRITERIEN:
• approve: Clip ist bereit für Export (Hook 7+/10, gute Struktur)
• refine: Potential vorhanden, könnte verbessert werden (Hook 5+/10) - BEVORZUGE DIESES VERDICT!
• reject: NUR wenn komplett hoffnungslos (Hook unter 4/10, kein klarer Payoff, 100% Filler)
"""
    
    return system, user_prompt.strip()


def build_final_ranking_prompt(
    validated_clips: List[Dict],
    target_count: int = 10
) -> tuple[str, str]:
    """
    Build prompt for final ranking of all validated clips.
    
    Args:
        validated_clips: All clips that passed validation
        target_count: How many clips to select
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = QUALITY_ORACLE
    
    clips_overview = ""
    for i, clip in enumerate(validated_clips, 1):
        assessment = clip.get('validation', {}).get('assessment', {})
        clips_overview += f"""
{i}. Hook: "{clip.get('hook_text', 'N/A')[:60]}..."
   Dauer: {clip.get('total_duration', 0):.1f}s
   Typ: {clip.get('structure_type', 'unknown')}
   Hook Quality: {assessment.get('hook_quality', {}).get('rating', 'unknown')}
   Viral Potential: {assessment.get('viral_potential', {}).get('rating', 'unknown')}
   Predicted Views: {clip.get('validation', {}).get('predicted_performance', {}).get('views_range', 'N/A')}
"""
    
    user_prompt = f"""
[ALLE VALIDIERTEN CLIPS]
{clips_overview}

[TASK]
Wähle die TOP {target_count} Clips für den finalen Export.
Ranke sie nach erwartetem Viral-Erfolg.

Kriterien für Ranking:
1. Hook-Stärke (wichtigstes Kriterium)
2. Einzigartigkeit (Diversität im Content)
3. Predicted Performance
4. Completion Rate Potential

[OUTPUT FORMAT]
```json
{{
  "final_selection": [
    {{
      "rank": 1,
      "clip_index": 3,
      "reasoning": "Stärkster Hook, paradoxes Statement"
    }},
    {{
      "rank": 2,
      "clip_index": 7,
      "reasoning": "Emotionale Story mit starkem Payoff"
    }}
  ],
  "diversity_check": "Clips decken verschiedene Content-Types ab",
  "total_predicted_value": "Geschätzte Gesamt-Reichweite aller Clips"
}}
```
"""
    
    return system, user_prompt.strip()

