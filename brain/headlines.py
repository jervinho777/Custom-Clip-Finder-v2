"""
BRAIN: Viral Headline Generator

Nutzt die gelernten Patterns aus headline_patterns.json
um neue Headlines für Clips zu generieren.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

from models.base import get_model

logger = logging.getLogger(__name__)

# Pattern file location
PATTERNS_FILE = Path("data/headline_patterns.json")

# Cache for loaded patterns
_patterns_cache: Optional[List[Dict]] = None


def load_headline_patterns() -> List[Dict]:
    """Lädt die gelernten Headline-Patterns."""
    global _patterns_cache
    
    if _patterns_cache is not None:
        return _patterns_cache
    
    if not PATTERNS_FILE.exists():
        logger.warning(f"Headline patterns not found at {PATTERNS_FILE}")
        return []
    
    try:
        with open(PATTERNS_FILE) as f:
            data = json.load(f)
        _patterns_cache = data.get('patterns', [])
        logger.info(f"Loaded {len(_patterns_cache)} headline patterns")
        return _patterns_cache
    except Exception as e:
        logger.error(f"Error loading headline patterns: {e}")
        return []


def get_relevant_patterns(
    archetype: str,
    top_k: int = 3
) -> List[Dict]:
    """
    Findet die relevantesten Patterns für einen Archetyp.
    
    Args:
        archetype: z.B. "paradox_story", "contrarian_rant", "insight"
        top_k: Anzahl der zurückzugebenden Patterns
        
    Returns:
        Liste der relevantesten Patterns
    """
    patterns = load_headline_patterns()
    
    if not patterns:
        return []
    
    # Mapping von Archetypen zu passenden Triggern
    archetype_triggers = {
        "paradox_story": ["Neugier", "Überraschung", "Curiosity"],
        "contrarian_rant": ["Provokation", "Wut", "Identität", "Identity"],
        "insight": ["Weisheit", "Erkenntnis", "Curiosity"],
        "listicle": ["Vollständigkeit", "Gier", "Value"],
        "tutorial": ["Empowerment", "Gier", "How-To"],
        "emotional": ["Empathie", "Verlust", "Emotionen"],
        "emotional_story": ["Empathie", "Verlust", "Emotionen"]
    }
    
    target_triggers = archetype_triggers.get(archetype, ["Neugier"])
    
    # Score patterns by relevance
    scored = []
    for p in patterns:
        score = 0
        trigger = p.get('trigger', '').lower()
        
        # Check if any target trigger matches
        for t in target_triggers:
            if t.lower() in trigger:
                score += 10
        
        # Bonus for high occurrence
        score += p.get('occurrence_count', 0)
        
        scored.append((score, p))
    
    # Sort by score and return top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:top_k]]


async def generate_viral_headline(
    transcript_excerpt: str,
    archetype: str = "unknown",
    core_message: str = "",
    use_patterns: bool = True
) -> Dict:
    """
    Generiert eine virale Headline für einen Clip.
    
    Args:
        transcript_excerpt: Die ersten ~500 Zeichen des Clips
        archetype: Der Clip-Archetyp (paradox_story, etc.)
        core_message: Die Kernaussage des Clips
        use_patterns: Ob gelernte Patterns verwendet werden sollen
        
    Returns:
        Dict mit headline, type, und reasoning
    """
    model = get_model("anthropic", tier="sonnet")
    
    # Load relevant patterns
    patterns_context = ""
    if use_patterns:
        patterns = get_relevant_patterns(archetype, top_k=3)
        if patterns:
            patterns_context = "\n\nGELERNTE PATTERNS (nutze diese als Inspiration):\n"
            for i, p in enumerate(patterns, 1):
                patterns_context += f"""
{i}. {p.get('archetype_name', 'Unknown')}
   Trigger: {p.get('trigger', 'N/A')}
   Formel: {p.get('formula', 'N/A')}
   Beispiel: {p.get('example_from_data', 'N/A')}
"""
    
    system_prompt = f"""Du bist ein Elite-Copywriter für virale Social Media Headlines.

DEINE AUFGABE: Generiere eine HEADLINE (< 5 Wörter), die den Zuschauer zum Stoppen bringt.

HEADLINE-TYPEN:
- PROBLEM: "Lotto Lüge", "Warum du arm bleibst" (für Insights/Tutorials)
- CHARACTER: "Was Armstrong bereut", "Der alte Mann" (für Stories)
- PROVOKATION: "Schule zerstört dich" (für Rants)
- NEGATIVE: "Tue NIEMALS X" (für Warnungen)
- IDENTITY: "Du bist nicht X wenn..." (für Statusangst)

REGELN:
1. Max 5 Wörter
2. Konkret > Abstrakt
3. Emotion > Fakten
4. Deutsch bevorzugt (außer das Original ist Englisch)
{patterns_context}

Antworte NUR mit gültigem JSON."""

    user_prompt = f"""
CLIP-ARCHETYP: {archetype}
KERNAUSSAGE: {core_message or "Nicht angegeben"}

CLIP-TEXT (Anfang):
{transcript_excerpt[:500]}

Generiere 3 Headline-Varianten und wähle die beste.

OUTPUT FORMAT:
{{
  "headlines": [
    {{"text": "Headline 1", "type": "problem", "score": 8}},
    {{"text": "Headline 2", "type": "character", "score": 7}},
    {{"text": "Headline 3", "type": "provokation", "score": 9}}
  ],
  "best_headline": "Headline 3",
  "best_type": "provokation",
  "reasoning": "Warum diese Headline am besten passt"
}}
"""

    try:
        response = await model.generate(
            user_prompt,
            system=system_prompt,
            temperature=0.7,  # Etwas Kreativität erlauben
            max_tokens=500
        )
        
        # Parse response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response.content)
        if json_match:
            result = json.loads(json_match.group())
            return {
                "viral_headline": result.get("best_headline", ""),
                "headline_type": result.get("best_type", ""),
                "headline_variants": result.get("headlines", []),
                "reasoning": result.get("reasoning", "")
            }
            
    except Exception as e:
        logger.error(f"Error generating headline: {e}")
    
    # Fallback
    return {
        "viral_headline": "",
        "headline_type": "",
        "headline_variants": [],
        "reasoning": "Generation failed"
    }


def generate_headline_sync(
    transcript_excerpt: str,
    archetype: str = "unknown",
    core_message: str = ""
) -> str:
    """
    Synchrone Version für einfache Verwendung.
    Nutzt regelbasierte Generierung ohne LLM.
    """
    patterns = get_relevant_patterns(archetype, top_k=1)
    
    if not patterns:
        # Fallback basierend auf Archetyp
        if archetype in ["paradox_story", "emotional", "emotional_story"]:
            return "Die ganze Geschichte"
        elif archetype in ["contrarian_rant", "rant"]:
            return "Das musst du hören"
        elif archetype == "insight":
            return "Die harte Wahrheit"
        else:
            return "Viral Clip"
    
    # Nutze das beste Pattern als Template
    best = patterns[0]
    formula = best.get('formula', '')
    
    # Sehr simple Template-Ersetzung (in Production würde man hier mehr machen)
    if '[' in formula and ']' in formula:
        # Hat Platzhalter - nehme das Beispiel
        return best.get('example_from_data', formula)
    
    return formula


# Export für brain/__init__.py
__all__ = [
    'load_headline_patterns',
    'get_relevant_patterns', 
    'generate_viral_headline',
    'generate_headline_sync'
]

