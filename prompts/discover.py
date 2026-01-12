"""
DISCOVER Stage Prompts (V6.1 - Viral DNA & Narrative Protection)

3-Phasen-Prozess für ALLE Longform-Inputs:
1. Content Scouting: Identifiziere Value-Blöcke (Unterscheidung Story vs. Info).
2. Global Hook Hunting: Finde den stärksten Einstieg im gesamten Video.
3. Blueprint Assembly: Baue den Clip nach viralen Prinzipien.

UNIVERSAL UPDATE:
- Narrative Protection: Schützt Geschichten vor "Über-Optimierung".
- Tension Maintenance: Verhindert das zu frühe Auflösen von Spannung.
"""

from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json
import re
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# HEADLINE PATTERNS LOADER (Brain Integration)
# =============================================================================

_headline_patterns_cache: Optional[List[Dict]] = None
HEADLINE_PATTERNS_FILE = Path("data/headline_patterns.json")


def _load_headline_patterns() -> List[Dict]:
    """Lädt gelernte Headline-Patterns aus dem Brain."""
    global _headline_patterns_cache
    
    if _headline_patterns_cache is not None:
        return _headline_patterns_cache
    
    if not HEADLINE_PATTERNS_FILE.exists():
        logger.info("No headline_patterns.json found - using default patterns")
        return []
    
    try:
        with open(HEADLINE_PATTERNS_FILE) as f:
            data = json.load(f)
        _headline_patterns_cache = data.get('patterns', [])
        logger.info(f"Loaded {len(_headline_patterns_cache)} headline patterns from Brain")
        return _headline_patterns_cache
    except Exception as e:
        logger.warning(f"Error loading headline patterns: {e}")
        return []


def _format_headline_patterns_for_prompt(patterns: List[Dict], max_patterns: int = 5) -> str:
    """Formatiert die Headline-Patterns für den Prompt (V2 - Opus-kompatibel)."""
    if not patterns:
        return ""
    
    result = "\n\n🧠 MASTER HEADLINE-PATTERNS (Opus-Synthesized):\n"
    result += "═" * 50 + "\n"
    
    # Sortiere nach Strength (S-Tier > A-Tier > B-Tier) oder Occurrence
    strength_order = {"S-Tier": 0, "A-Tier": 1, "B-Tier": 2, "Unknown": 3}
    sorted_patterns = sorted(
        patterns, 
        key=lambda x: (strength_order.get(x.get('strength', 'Unknown'), 3), -x.get('occurrence_count', 0))
    )
    
    for i, p in enumerate(sorted_patterns[:max_patterns], 1):
        # Support both old (Sonnet) and new (Opus) field names
        name = p.get('name', p.get('archetype_name', 'Unknown'))
        trigger = p.get('psychological_trigger', p.get('trigger', 'N/A'))
        formula = p.get('formula', 'N/A')
        strength = p.get('strength', '')
        usage = p.get('usage_instructions', p.get('usage_context', ''))
        
        # Get examples (support both formats)
        examples = p.get('best_examples', [])
        if not examples:
            example = p.get('example_from_data', 'N/A')
            examples = [example] if example != 'N/A' else []
        
        strength_badge = f" [{strength}]" if strength else ""
        
        result += f"""
{i}. {name}{strength_badge}
   🧬 Trigger: {trigger}
   📝 Formel: {formula}
   💡 Beispiele: {', '.join(examples[:2]) if examples else 'N/A'}
   📌 Wann nutzen: {usage[:100]}{'...' if len(usage) > 100 else ''}
"""
    
    result += """
═══════════════════════════════════════════════════
ANWEISUNG: Wähle das Pattern, das am besten zum Content passt.
Die Formel ist dein Template - ersetze [Platzhalter] mit konkretem Inhalt.
Achte auf den psychologischen Trigger - er muss zum Thema passen!
"""
    
    return result


# =============================================================================
# DEFAULT FEW-SHOT EXAMPLES (Fallback wenn Brain leer)
# =============================================================================

DEFAULT_FEW_SHOT_EXAMPLES = [
    {
        "id": "paradox_story",
        "name": "Paradox Story (Dieter Lange Pattern)",
        "hook_instruction": "Nimm das Fazit/die Moral und setze es an den Anfang.",
        "example_hook": "Arbeite niemals für Geld.",
        "structure": ["hook", "body", "payoff"]
    },
    {
        "id": "contrarian_rant",
        "name": "Contrarian Rant (Frädrich Pattern)",
        "hook_instruction": "Starte mit der provokantesten Aussage.",
        "example_hook": "Eisbergsalat hat so viel Vitamine wie Papier.",
        "structure": ["hook", "body", "payoff"]
    },
    {
        "id": "listicle",
        "name": "Listicle (Nummerierte Liste)",
        "hook_instruction": "Starte mit der Zahl und dem Versprechen.",
        "example_hook": "3 Dinge, die erfolgreiche Menschen anders machen.",
        "structure": ["hook", "body"]
    },
    {
        "id": "insight",
        "name": "Insight (Naval Ravikant Pattern)",
        "hook_instruction": "Der Insight selbst ist der Hook.",
        "example_hook": "Desire is a contract to be unhappy.",
        "structure": ["body"]
    },
    {
        "id": "emotional",
        "name": "Emotional Story",
        "hook_instruction": "Nimm den emotionalen Höhepunkt als Teaser.",
        "example_hook": "In diesem Moment hat sich alles verändert.",
        "structure": ["setup", "body", "peak"]
    }
]


# =============================================================================
# VIRAL DNA CRITERIA (Universelle Prinzipien)
# =============================================================================

VIRAL_DNA_CRITERIA = """
🔍 VIRAL DNA CHECKLIST (Universal Principles):

═══════════════════════════════════════════════════════════════
0. ⚡ ZERO LATENCY (Nicht verhandelbar!)
═══════════════════════════════════════════════════════════════
   - Keine Stille am Anfang. Kein "Ähm". Kein Räuspern.
   - Der erste Frame muss Energie haben.

═══════════════════════════════════════════════════════════════
1. 🎣 THE VERBAL HOOK - "The Curiosity Gap"
═══════════════════════════════════════════════════════════════
   [Principle: Primacy Effect & Cognitive Dissonance]
   
   - Der erste Satz muss eine "Lücke" im Wissen oder Weltbild des Zuschauers öffnen.
   
   ⛔️ UNIVERSAL ANTI-PATTERN: "The Safety Bridge"
   Die KI neigt dazu, kontroverse Aussagen sofort zu relativieren ("Ich meine nicht X, sondern Y").
   -> DAS IST VERBOTEN.
   -> Lass die Kontroverse stehen. Die Auflösung gehört ans Ende des Clips, nicht an den Anfang.
   -> Spannung entsteht durch Ungewissheit.

═══════════════════════════════════════════════════════════════
2. 📺 VISUAL COMPENSATION (Headline Strategy)
═══════════════════════════════════════════════════════════════
   [Principle: Headlines retten fehlenden Kontext]
   
   ALTE REGEL (VERALTET): "Verwerfe Clips mit Pronomen-Start ('Er sagte...')."
   
   NEUE REGEL: "RETTE den Clip mit einer HEADLINE!"
   
   - Wenn der Audio-Start Kontext benötigt (z.B. "Und er sagte...", "Das Problem ist..."):
     -> Die HEADLINE muss diesen Kontext liefern.
     -> Beispiel: Audio = "Er sagte: Arbeite niemals für Geld."
                  Headline = "Was der alte Mann den Kindern sagte"
   
   - Jeder Clip bekommt eine Headline für Split-Testing.
   - Headlines sind < 5 Wörter, KONKRET und SCROLL-STOPPER.

═══════════════════════════════════════════════════════════════
3. 🧬 MASS APPEAL (Relatability)
═══════════════════════════════════════════════════════════════
   - Ist das Thema verständlich ohne Fachwissen (Universelle Sprache)?
   - Spricht es menschliche Grundbedürfnisse an (Status, Sicherheit, Liebe, Verstehen)?

═══════════════════════════════════════════════════════════════
4. 🎢 STRUCTURAL TENSION (Context-Aware Value)
═══════════════════════════════════════════════════════════════
   [Principle: Narrative Integrity]
   
   Wir unterscheiden zwei Arten von Content:
   
   A) INFORMATIONAL CONTENT (Tutorials, Fakten, Listen)
      -> Hier ist Value = Information pro Minute.
      -> Kürze Füller, sei präzise.
      
   B) NARRATIVE CONTENT (Stories, Parabeln, Metaphern, Witze)
      -> Hier ist Value = Emotionale Bindung & Kopfkino.
      -> Schneide KEINE Details weg, die für die Atmosphäre nötig sind.
      -> Eine Geschichte braucht Zeit zum Atmen. "Effizienz" tötet die Story.
      -> Beispiel: "Ein alter Mann ging die Straße entlang" ist KEIN Füller, sondern Setup.

═══════════════════════════════════════════════════════════════
5. 💎 PAYOFF (Utility)
═══════════════════════════════════════════════════════════════
   - Der Clip muss das Versprechen des Hooks einlösen.
   - Bei Stories: Die Moral/Pointe muss glasklar sein.
"""


# =============================================================================
# HEADLINE STRATEGY (Pattern-Based)
# =============================================================================

HEADLINE_STRATEGY = """
📺 HEADLINE TYPES (Wähle basierend auf Archetyp):

INSIGHT / TUTORIAL → "Problem-Headline"
   Beispiele: "Lotto Lüge", "Warum du arm bleibst", "Der größte Fehler"
   
STORY / PARADOX → "Character-Headline"  
   Beispiele: "Was Armstrong bereut", "Der alte Mann & die Kinder", "Ihre letzten Worte"

RANT / CONTRARIAN → "Provokation-Headline"
   Beispiele: "Eisberg = Papier", "Schule zerstört dich", "Vergiss Leidenschaft"

REGELN:
- Max 5 Wörter
- Konkret schlägt Abstrakt ("Lotto Lüge" > "Die Wahrheit über Geld")
- Emotionen schlagen Fakten ("Warum du weinst" > "Studie zeigt")
"""


# =============================================================================
# Phase 1: CONTENT SCOUTING (Find the Body)
# =============================================================================

def build_content_scouting_prompt(
    transcript_text: str,
    archetypes: List[Dict],
    min_duration: int = 20,
    max_duration: int = 180,
    video_duration_minutes: Optional[float] = None
) -> Tuple[str, str]:
    """
    Phase 1: Content Scouting.
    Ziel: Finde in sich geschlossene Einheiten (Bodies).
    """
    
    system = f"""Du bist ein Senior Video-Editor für virale Formate.

DEINE ROLLE: Content Scout. Du filterst riesige Mengen Text nach "Gold".

{VIRAL_DNA_CRITERIA}

═══════════════════════════════════════════════════════════════
AUFGABE: CONTENT SCOUTING
═══════════════════════════════════════════════════════════════

Scanne das Transkript nach zusammenhängenden Blöcken.

WICHTIG - ERKENNE DEN MODUS:

1. MODUS "STORYTELLER":
   - Wenn der Speaker eine Anekdote, Parabel oder persönliche Geschichte erzählt.
   - REGEL: Extrahiere den GANZEN Block (Setup -> Konflikt -> Auflösung).
   - Ignoriere "Informationsdichte". Die Story selbst ist der Value.

2. MODUS "TEACHER":
   - Wenn der Speaker Fakten, Schritte oder Thesen erklärt.
   - REGEL: Suche nach dichten, klaren Argumentationsketten.

DU ANTWORTEST NUR MIT JSON."""

    # Format Archetypes
    arch_text = ""
    for arch in archetypes:
        arch_text += f"\n• {arch['id'].upper()}: {arch['name']}"
        if arch.get('markers'):
            arch_text += f"\n  Marker: {', '.join(arch['markers'][:3])}"
    
    duration_context = ""
    if video_duration_minutes:
        duration_context = f"\n[VIDEO-LÄNGE: {video_duration_minutes:.0f} Minuten]"
    
    user = f"""
{duration_context}

[ROHMATERIAL]
{transcript_text[:30000]}

[ARCHETYPEN]
{arch_text}

[AUFGABE]
Finde alle viralen Content-Blöcke.
Achte besonders auf STORIES (erkennbar an Charakteren, Ortsbeschreibungen, Zeitabläufen).
Wenn du eine Story findest, markiere sie als 'paradox_story' oder 'emotional_story' und nimm den GANZEN Bogen auf.

[OUTPUT FORMAT]
```json
[
  {{
    "start": 540.0,
    "end": 720.0,
    "archetype": "paradox_story",
    "summary": "Parabel über [Thema]",
    "core_message": "[Die Moral der Geschichte]",
    "has_native_hook": false,
    "reasoning": "Klassische Heldenreise-Struktur mit starkem Payoff am Ende."
  }}
]
```
"""
    return system.strip(), user.strip()


# =============================================================================
# Phase 2: GLOBAL HOOK HUNTING
# =============================================================================

def build_global_hook_hunting_prompt(
    body_summary: str,
    body_core_message: str,
    body_start: float,
    body_end: float,
    archetype: str,
    full_transcript_text: str,
    pre_scanned_candidates: Optional[List[Dict]] = None,
    named_patterns: Optional[List[Dict]] = None
) -> Tuple[str, str]:
    """
    Phase 2: Global Hook Hunting + Headline Generation.
    Ziel: Finde den Satz, der maximale Neugier weckt + generiere Headline.
    """
    
    # Load learned headline patterns from Brain
    headline_patterns = _load_headline_patterns()
    headline_brain_context = _format_headline_patterns_for_prompt(headline_patterns, max_patterns=5)
    
    system = f"""Du bist der "Hook Hunter".

═══════════════════════════════════════════════════════════════
PHASE 2: GLOBAL HOOK HUNTING + HEADLINE GENERATION
═══════════════════════════════════════════════════════════════

Finde den perfekten VERBALEN Einstieg für den gefundenen Body.
PLUS: Generiere eine HEADLINE für jeden Clip (Split-Testing).

STRATEGIE: "REVERSE ENGINEERING"

1. Lies die Kernaussage/Moral des Content-Body.
2. Suche im Transkript nach dem Satz, der diese Moral am stärksten verkörpert.
3. Oft steht dieser Satz am ENDE des Blocks (als Fazit).
4. Wir nehmen dieses Fazit und setzen es an den ANFANG (The Hook).

⚠️ ANTI-SAFETY REGEL: Vermeide "Weichmacher".
   - Schlecht: "Ich glaube, dass wir vielleicht weniger arbeiten sollten."
   - Gut: "Arbeit ist Zeitverschwendung." (Der Body erklärt dann warum).
   - Suche den radikalsten Satz!

{HEADLINE_STRATEGY}
{headline_brain_context}
HEADLINE-KONTEXT-REGEL:
Wenn der Audio-Hook abstrakt beginnt (z.B. "Und er sagte...", "Das Problem ist..."),
MUSS die Headline konkret sein und den fehlenden Kontext liefern!

DU ANTWORTEST NUR MIT JSON."""

    # Format candidates & patterns
    candidates_text = ""
    if pre_scanned_candidates:
        candidates_text = "\n[KANDIDATEN IM UMKREIS]"
        for i, cand in enumerate(pre_scanned_candidates[:10]):
            candidates_text += f"\n{i+1}. [{cand.get('timestamp', 0):.0f}s] \"{cand.get('text', '')[:80]}...\""

    patterns_text = ""
    if named_patterns:
        patterns_text = "\n\n[KNOWN PATTERNS]"
        for p in named_patterns[:5]:
            patterns_text += f"\n• {p.get('name', '')}: {p.get('hook_instruction', '')}"

    # Determine headline type based on archetype
    headline_hint = ""
    if archetype in ["insight", "tutorial", "listicle"]:
        headline_hint = "→ Nutze eine PROBLEM-HEADLINE (z.B. 'Lotto Lüge', 'Warum du arm bleibst')"
    elif archetype in ["paradox_story", "emotional", "emotional_story"]:
        headline_hint = "→ Nutze eine CHARACTER-HEADLINE (z.B. 'Was Armstrong bereut', 'Der alte Mann')"
    elif archetype in ["contrarian_rant", "rant"]:
        headline_hint = "→ Nutze eine PROVOKATION-HEADLINE (z.B. 'Schule zerstört dich')"

    user = f"""
[ZIEL-BODY]
Archetyp: {archetype.upper()}
Inhalt: {body_summary}
Moral: {body_core_message}
{headline_hint}
{patterns_text}
{candidates_text}

[GESAMTES TRANSKRIPT]
{full_transcript_text[:40000]}

[AUFGABE]
1. Finde den EINEN Satz, der das Thema am stärksten zuspitzt ("The Spike").
2. Generiere eine HEADLINE (< 5 Wörter) für den Clip.
3. Liefere ZWEI VARIANTEN für Split-Testing.

[OUTPUT FORMAT]
```json
{{
  "hook_timestamp": 720.0,
  "hook_end_timestamp": 725.0,
  "hook_text": "Arbeite niemals für Geld.",
  "hook_type": "conclusion_moved_to_start",
  "needs_headline_context": false,
  "variants": [
    {{
      "variant": "A",
      "strategy": "audio_hook_strong",
      "viral_headline": "Warum Arbeit Gift ist",
      "reasoning": "Audio-Hook ist stark genug, Headline verstärkt die Kontroverse."
    }},
    {{
      "variant": "B", 
      "strategy": "headline_carries_hook",
      "viral_headline": "Was der alte Mann sagte",
      "reasoning": "Falls wir mitten in der Story starten, liefert die Headline den Kontext."
    }}
  ],
  "recommended_variant": "A",
  "reasoning": "Das ist die radikalste Formulierung der Kernaussage."
}}
```
"""
    return system.strip(), user.strip()


# =============================================================================
# Phase 3: BLUEPRINT ASSEMBLY
# =============================================================================

def build_assembly_prompt(
    body_info: Dict,
    found_hook: Dict,
    pattern_name: str,
    editing_rules: Optional[List[str]] = None,
    hook_variants: Optional[List[Dict]] = None
) -> Tuple[str, str]:
    """
    Phase 3: Blueprint Assembly + Final Headline Selection.
    Ziel: Harte Schnitte für maximale Retention + Headline für Watchtime.
    """
    
    # Load learned headline patterns from Brain
    headline_patterns = _load_headline_patterns()
    headline_brain_context = _format_headline_patterns_for_prompt(headline_patterns, max_patterns=5)
    
    system = f"""Du bist ein Schnitt-Experte.

═══════════════════════════════════════════════════════════════
PHASE 3: BLUEPRINT ASSEMBLY + HEADLINE FINALIZATION
═══════════════════════════════════════════════════════════════

Baue den finalen Clip-Plan MIT Headline.

PRINZIP "TENSION MAINTENANCE":
Wir wollen den Zuschauer "in der Luft hängen lassen".

1. HOOK (Der Köder): Wirf die These/Frage in den Raum.
2. HARD CUT (Der Cliff): Schneide SOFORT in den Content/Story-Start.
3. KEINE ERKLÄRUNG: Schneide alle Sätze weg, die zwischen Hook und Story "vermitteln" oder "relativieren".
   Der Zuschauer muss denken: "Wie meint er das?" -> Die Story ist die Antwort.

{HEADLINE_STRATEGY}
{headline_brain_context}
HEADLINE-PFLICHT:
Jeder Clip bekommt eine Headline für maximale Watchtime.
Wenn der Audio-Start Kontext braucht, MUSS die Headline ihn liefern.

DU ANTWORTEST NUR MIT JSON."""

    rules_text = ""
    if editing_rules:
        rules_text = "\n[EDITING RULES]"
        for rule in editing_rules[:5]:
            rules_text += f"\n• {rule}"

    variants_text = ""
    if hook_variants:
        variants_text = "\n[HEADLINE VARIANTEN aus Phase 2]"
        for v in hook_variants:
            variants_text += f"\n• Variante {v.get('variant', '?')}: \"{v.get('viral_headline', '')}\" ({v.get('strategy', '')})"

    user = f"""
[BODY]
Start: {body_info.get('start', 0):.0f}s
End: {body_info.get('end', 0):.0f}s
Archetyp: {body_info.get('archetype', 'unknown')}

[HOOK]
Start: {found_hook.get('hook_timestamp', 0):.0f}s
Text: {found_hook.get('hook_text', '')}
{rules_text}
{variants_text}

[AUFGABE]
1. Erstelle die Schnittliste.
2. Wähle die beste Headline (oder erstelle eine bessere).
3. Prüfe: Braucht der Audio-Start Headline-Kontext?

[OUTPUT FORMAT]
```json
{{
  "segments": [
    {{
      "role": "hook",
      "start": {found_hook.get('hook_timestamp', 0)},
      "end": {found_hook.get('hook_end_timestamp', 0)},
      "clip_position": 0
    }},
    {{
      "role": "body",
      "start": {body_info.get('start', 0)},
      "end": {body_info.get('end', 0)},
      "clip_position": 1
    }}
  ],
  "viral_headline": "Warum Arbeit Gift ist",
  "headline_type": "problem",
  "headline_is_essential": false,
  "editing_instruction": "Harter Schnitt. Entferne die Moderation zwischen Hook und Story-Beginn."
}}
```
"""
    return system.strip(), user.strip()


# =============================================================================
# Legacy / Helper Functions
# =============================================================================
# (Keeping parsers and legacy wrappers unchanged for compatibility)

def parse_content_scouting_response(response: str) -> List[Dict]:
    """Parse Phase 1 response."""
    json_match = re.search(r'\[[\s\S]*\]', response)
    if not json_match:
        return []
    try:
        return json.loads(json_match.group())
    except Exception:
        return []


def parse_global_hook_response(response: str) -> Dict:
    """Parse Phase 2 response."""
    json_match = re.search(r'\{[\s\S]*\}', response)
    if not json_match:
        return {}
    try:
        return json.loads(json_match.group())
    except Exception:
        return {}


def parse_assembly_response(response: str) -> Dict:
    """Parse Phase 3 response."""
    json_match = re.search(r'\{[\s\S]*\}', response)
    if not json_match:
        return {}
    try:
        return json.loads(json_match.group())
    except Exception:
        return {}


# Legacy wrappers for backwards compatibility
def build_discover_prompt(*args, **kwargs):
    return build_content_scouting_prompt(*args, **kwargs)


def parse_discover_response(response):
    return parse_content_scouting_response(response)


def build_segmentation_prompt(*args, **kwargs):
    return build_content_scouting_prompt(*args, **kwargs)


def parse_segmentation_response(response):
    return parse_content_scouting_response(response)


def build_hook_hunting_prompt(*args, **kwargs):
    return build_global_hook_hunting_prompt(*args, **kwargs)


def parse_hook_response(response):
    return parse_global_hook_response(response)
