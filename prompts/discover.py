"""
DISCOVER Stage Prompts (V6 - Viral DNA Edition)

3-Phasen-Prozess:
1. Content Scouting: Finde Content Bodies (Rohdiamanten)
2. Global Hook Hunting: Suche im GESAMTEN Video nach dem besten Hook
3. Blueprint Assembly: Setze die Segmente zusammen

KRITISCH: 
- KEINE ZEITGRENZEN! Der Hook kann 20 Minuten später kommen.
- IGNORIERE VISUALS! Wir haben nur Text - fokussiere auf verbale Hooks.
- VIRAL DNA CRITERIA basierend auf interner SOP.
"""

from typing import List, Dict, Tuple, Optional
import json
import re


# =============================================================================
# VIRAL DNA CRITERIA (Text-Based Analysis - Interne SOP)
# =============================================================================

VIRAL_DNA_CRITERIA = """
🔍 VIRAL DNA CHECKLIST (Text-Based Analysis):

═══════════════════════════════════════════════════════════════
1. 🎣 THE VERBAL HOOK (0-5s) - "The Information Gap"
═══════════════════════════════════════════════════════════════
   [SOP: Info Gap, Primacy Effect]
   
   - Erzeugt der ERSTE Satz eine Frage im Kopf des Zuschauers?
   - Gibt es einen "Verbal Pattern Interrupt"? 
     (Kontroverse Aussage, laute Beschreibung, sofortiger Konflikt)
   
   ❌ REJECT: "Hallo zusammen, heute möchte ich über..."
   ✅ ACCEPT: "Du wurdest dein ganzes Leben über Geld belogen."
   ✅ ACCEPT: "Arbeite niemals für Geld."
   ✅ ACCEPT: "Das ist der größte Fehler, den alle machen."

═══════════════════════════════════════════════════════════════
2. 🧬 MASS APPEAL & RELATABILITY
═══════════════════════════════════════════════════════════════
   [SOP: Mass Appeal, Simplicity]
   
   - Ist das Thema verständlich für einen müden Zuschauer um 23 Uhr?
   - Berührt es universelle Themen?
     • Status & Erfolg
     • Geld & Wohlstand  
     • Gesundheit & Energie
     • Beziehungen & Liebe
     • Sinn & Erfüllung
   
   ❌ REJECT: Nischen-Fachjargon, komplexe Konzepte
   ✅ ACCEPT: Wenn ein 12-Jähriger es verstehen würde

═══════════════════════════════════════════════════════════════
3. 🎢 STRUCTURAL TENSION (Retention)
═══════════════════════════════════════════════════════════════
   [SOP: Open Loops, Watchtime]
   
   OPEN LOOP: Verspricht der Sprecher einen Payoff, der erst am Ende kommt?
   - "Und dann hat er mir etwas gesagt, das alles verändert hat..."
   - "Der dritte Punkt ist der wichtigste..."
   
   STORYTIME: Gibt es einen narrativen Bogen?
   - Setup → Konflikt → Auflösung
   - Problem → Spannung → Lösung
   
   ❌ REJECT: Lineare Listen ohne Spannung
   ❌ REJECT: Monotone Erklärungen
   ✅ ACCEPT: Geschichte mit Wendepunkt
   ✅ ACCEPT: Aufbau von Spannung zum Fazit

═══════════════════════════════════════════════════════════════
4. 💎 UTILITY & VALUE (Save-ability)
═══════════════════════════════════════════════════════════════
   [SOP: Learning, Aha-Moment]
   
   - Gibt es einen klaren "Aha-Moment"?
   - Gibt es konkrete, umsetzbare Ratschläge?
   - Würden Leute das SPEICHERN, um später darauf zurückzugreifen?
   
   ❌ REJECT: Vage Philosophie ohne Substanz
   ✅ ACCEPT: "Mach das jeden Morgen und..."
   ✅ ACCEPT: "Der Trick ist..." + konkrete Anleitung

═══════════════════════════════════════════════════════════════
5. 🔥 IGNITION (Shareability)
═══════════════════════════════════════════════════════════════
   [SOP: Controversy, Humor, Emotion]
   
   KONTROVERSE: Gibt es eine polarisierende Meinung?
   - "Das wird die Hälfte von euch wütend machen..."
   - "Alle sagen X, aber eigentlich ist Y richtig..."
   
   HUMOR: Gibt es eine Punchline oder einen Moment der Erleichterung?
   
   EMOTION: Berührt es den Zuschauer emotional?
   - Würdest du das einem Freund schicken mit "Das bin so ich"?
   - Würdest du es teilen mit "Das MUSST du sehen"?
   
   ❌ REJECT: Neutral, keine Reaktion auslösend
   ✅ ACCEPT: Löst starke Reaktion aus (Zustimmung ODER Widerspruch)
"""


# =============================================================================
# DISCOVERY SYSTEM PROMPT (Text-Based, No Visuals!)
# =============================================================================

DISCOVERY_SYSTEM_PROMPT = f"""
Du bist ein Experte für virale Content-Analyse. Dein Ziel ist es, Segmente in einem Roh-Transkript zu identifizieren, die hohes virales Potenzial haben.

{VIRAL_DNA_CRITERIA}

═══════════════════════════════════════════════════════════════
DEINE AUFGABE
═══════════════════════════════════════════════════════════════

Scanne die Transkript-Segmente und extrahiere "Candidate Moments".
Für jeden Moment MUSST du ihn gegen die Viral DNA Checklist validieren.

═══════════════════════════════════════════════════════════════
KRITISCHE REGELN
═══════════════════════════════════════════════════════════════

1. IGNORIERE VISUALS: 
   Du hast NUR Text. Fokussiere auf verbale Hooks, Story-Struktur und Pacing.
   Keine Annahmen über B-Roll, Schnitte oder visuelle Effekte.

2. STRENGES FILTERING: 
   95% des Contents ist Rauschen. Extrahiere NUR die Top 5% "Gold".
   Lieber 3 exzellente Momente als 10 mittelmäßige.

3. KONTEXT-BEWUSSTSEIN: 
   Selbst wenn ein Satz gut ist - hat er ein logisches Ende?
   Stelle sicher, dass der extrahierte Clip ALLEINE funktioniert.

4. VERBAL HOOK FIRST:
   Der erste Satz entscheidet. Wenn er langweilig ist, suche einen besseren
   Hook woanders im Transkript und stelle ihn nach vorne.

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT (JSON)
═══════════════════════════════════════════════════════════════

DU ANTWORTEST NUR MIT VALIDEM JSON.
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
    Phase 1: Content Scouting - Finde die "Rohdiamanten".
    
    Suche nach zusammenhängenden Inhaltsblöcken:
    - Vollständige Geschichten
    - Zusammenhängende Argumentationen
    - Standalone Insights
    
    WICHTIG: Wir bewerten NOCH NICHT ob der Hook gut ist!
    Das kommt in Phase 2 (Global Hook Hunting).
    """
    
    system = f"""Du bist ein Senior Video-Editor bei einem viralen Content-Studio.

DEINE ROLLE: Du bist der "Content Scout" - du siehst das Rohmaterial
und findest die verborgenen Schätze (Rohdiamanten).

{VIRAL_DNA_CRITERIA}

═══════════════════════════════════════════════════════════════
PHASE 1: CONTENT SCOUTING
═══════════════════════════════════════════════════════════════

DEINE AUFGABE: Finde zusammenhängende Inhalts-Blöcke mit viralem Potenzial.

Ein "Rohdiamant" ist:
✓ Eine VOLLSTÄNDIGE Geschichte mit Open Loop und Payoff
✓ Eine kontroverse These mit Begründung (Ignition!)
✓ Ein konkreter Insight mit Aha-Moment (Utility!)
✓ Ein relatable Moment mit Mass Appeal

WICHTIG - FOKUS AUF TEXT:
✗ IGNORIERE visuelle Elemente - du hast NUR das Transkript
✗ Ob der Anfang gut ist (das prüfen wir später!)
✗ Ob ein Hook vorhanden ist (das suchen wir später!)

Du suchst NUR nach dem KÖRPER (Body) des Contents.
Der perfekte verbale Hook kann woanders im Video sein - das ist Phase 2.

QUALITÄTSKRITERIEN (basierend auf Viral DNA):
• Mass Appeal: Universelles Thema, einfach verständlich
• Structural Tension: Narrative arc, Open Loop zum Payoff
• Utility: Konkreter Wert, Aha-Moment
• Ignition: Kontroverse oder emotionale Reaktion

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

[ROHMATERIAL - Transkript mit Zeitstempeln]
{transcript_text[:30000]}

[ARCHETYPEN ZUM ERKENNEN]
{arch_text}

[DEINE AUFGABE]
Scanne das Transkript und finde ALLE zusammenhängenden Content-Blöcke.

Für jeden Block liefere:
• start: Startzeit in Sekunden
• end: Endzeit in Sekunden 
• archetype: Welcher Archetyp? (paradox_story, contrarian_rant, listicle, insight, emotional, tutorial)
• summary: 1-Satz Zusammenfassung des INHALTS
• core_message: Was ist die Kernaussage/Moral/Pointe?
• has_native_hook: true/false - Ist der ANFANG des Blocks bereits "catchy"?

[REGELN]
• NUR vollständige Gedanken (keine halben Geschichten)
• Minimum {min_duration} Sekunden, Maximum {max_duration} Sekunden
• Bei "paradox_story": Die GANZE Geschichte bis zur Moral finden
• Ignoriere langweilige Intros - der echte Content zählt

[OUTPUT FORMAT]
```json
[
  {{
    "start": 540.0,
    "end": 720.0,
    "archetype": "paradox_story",
    "summary": "Geschichte über alten Mann der Kindern Geld gibt",
    "core_message": "Arbeite niemals für Geld, sondern für Leidenschaft",
    "has_native_hook": false
  }},
  {{
    "start": 120.0,
    "end": 180.0,
    "archetype": "insight",
    "summary": "Philosophischer Gedanke über Ausdauer",
    "core_message": "Der wichtigste Skill ist Ausdauer, nicht Talent",
    "has_native_hook": true
  }}
]
```

Finde ALLE Rohdiamanten:
"""
    
    return system.strip(), user.strip()


# =============================================================================
# Phase 2: GLOBAL HOOK HUNTING (Find the Start - NO TIME LIMITS!)
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
    Phase 2: Global Hook Hunting - KEINE ZEITGRENZEN!
    
    Der perfekte Hook kann überall im Video sein:
    - 5 Minuten vor dem Body
    - 20 Minuten nach dem Body
    - Im Recap ganz am Ende
    - In einer Q&A Session
    
    Diese Funktion instruiert die KI, im GESAMTEN Transkript
    nach dem perfekten Hook zu suchen.
    """
    
    system = f"""Du bist der "Hook Hunter" - der weltbeste Experte für virale Einstiege.

═══════════════════════════════════════════════════════════════
PHASE 2: GLOBAL HOOK HUNTING (Text-Based!)
═══════════════════════════════════════════════════════════════

DEINE MISSION: Finde den EINEN perfekten VERBALEN Hook für den Content Body.

⚠️ KRITISCHE REGELN ⚠️

1. IGNORIERE DIE ZEITACHSE!
   Der perfekte Hook kann ÜBERALL im Video sein:
   • 5 Minuten VOR dem Body
   • 20 Minuten NACH dem Body
   • Im Recap am Ende
   • In einer Q&A

2. IGNORIERE VISUALS!
   Du hast NUR Text. Fokussiere auf den VERBALEN Hook.
   Keine Annahmen über Bilder, Schnitte oder B-Roll.

3. DU SUCHST NICHT LOKAL. DU SUCHST GLOBAL.

═══════════════════════════════════════════════════════════════
VIRAL DNA: DER PERFEKTE VERBALE HOOK
═══════════════════════════════════════════════════════════════

🎣 THE VERBAL HOOK muss einen "Information Gap" erzeugen:

✅ ACCEPT (Gap erzeugt):
   • "Arbeite niemals für Geld." (Warum?!)
   • "Ein Eisbergsalat hat so viel Vitamin C wie ein Blatt Papier." (Wirklich?!)
   • "Du wurdest dein ganzes Leben belogen." (Worüber?!)
   • "Das ist der größte Fehler, den 99% machen." (Was?!)

❌ REJECT (Kein Gap):
   • "Hallo zusammen, heute möchte ich..."
   • "In diesem Video erkläre ich..."
   • "Lasst uns über X sprechen..."

═══════════════════════════════════════════════════════════════
HOOK-TYPEN NACH ARCHETYP
═══════════════════════════════════════════════════════════════

• PARADOX_STORY: Suche das FAZIT/die MORAL
  → Oft am ENDE der Story ("Deswegen sage ich: ...")
  → Dieter Lange Pattern: Moral von Minute 12 an Minute 0

• CONTRARIAN_RANT: Suche die PROVOKANTESTE Aussage
  → "Das ist kompletter Bullshit" > "Lass mich erklären warum..."
  → Maximale Ignition!

• LISTICLE: Suche den ÜBERRASCHENDSTEN Listenpunkt
  → Der kontroverseste oder unerwartete

• INSIGHT: Suche den KERN-SATZ
  → Oft eine knackige Zusammenfassung am Ende
  → Maximal 10 Wörter, maximaler Impact

DU ANTWORTEST NUR MIT JSON."""

    # Format pre-scanned candidates
    candidates_text = ""
    if pre_scanned_candidates:
        candidates_text = "\n[VORAUSGEWÄHLTE HOOK-KANDIDATEN (nach Punch-Score)]"
        for i, cand in enumerate(pre_scanned_candidates[:10]):
            candidates_text += f"\n{i+1}. [{cand.get('timestamp', 0):.0f}s] \"{cand.get('text', '')[:80]}...\""
            if cand.get('viral_match'):
                candidates_text += f" (ähnlich zu: {cand.get('viral_match')[:40]}...)"
    
    # Format named patterns
    patterns_text = ""
    if named_patterns:
        patterns_text = "\n\n[GELERNTE PATTERNS AUS DEM BRAIN]"
        for p in named_patterns[:5]:
            patterns_text += f"\n• {p.get('name', '')}: {p.get('hook_instruction', '')}"
    
    user = f"""
[DER CONTENT BODY (für den wir einen Hook suchen)]
Archetyp: {archetype.upper()}
Zeitraum: {body_start:.0f}s - {body_end:.0f}s
Summary: {body_summary}
Kernaussage: {body_core_message}
{patterns_text}
{candidates_text}

═══════════════════════════════════════════════════════════════
[VOLLSTÄNDIGES TRANSKRIPT - DURCHSUCHE ALLES!]
═══════════════════════════════════════════════════════════════

{full_transcript_text[:40000]}

═══════════════════════════════════════════════════════════════
[DEINE AUFGABE]
═══════════════════════════════════════════════════════════════

Finde den EINEN Satz im gesamten Transkript, der als perfekter Hook
für den oben beschriebenen Content Body funktioniert.

DURCHSUCHE DAS GESAMTE VIDEO:
• Der Body ist bei {body_start:.0f}s-{body_end:.0f}s
• Der Hook kann ÜBERALL sein - auch 30 Minuten später!
• Suche besonders am ENDE des Themenblocks nach Fazits
• Suche in Recaps, Q&As, Zusammenfassungen

[OUTPUT FORMAT]
```json
{{
  "hook_timestamp": 720.0,
  "hook_end_timestamp": 725.0,
  "hook_text": "Arbeite niemals für Geld.",
  "hook_type": "conclusion_moved_to_start",
  "distance_from_body_seconds": 180,
  "reasoning": "Die Moral der Geschichte kommt erst 3 Minuten nach dem Body. Sie ist perfekt als Hook weil sie kontrovers ist und sofort Neugier weckt.",
  "confidence": 0.95
}}
```

Finde den perfekten Hook:
"""
    
    return system.strip(), user.strip()


# =============================================================================
# Phase 3: BLUEPRINT ASSEMBLY (Der Schnitt)
# =============================================================================

def build_assembly_prompt(
    body_info: Dict,
    found_hook: Dict,
    pattern_name: str,
    editing_rules: Optional[List[str]] = None
) -> Tuple[str, str]:
    """
    Phase 3: Blueprint Assembly - Der finale Schnitt.
    
    Wir haben Body und Hook - jetzt bauen wir den Clip zusammen.
    Diese Phase erzeugt die finalen Segment-Anweisungen.
    """
    
    system = """Du bist ein Schnitt-Experte für virale Clips.

═══════════════════════════════════════════════════════════════
PHASE 3: BLUEPRINT ASSEMBLY
═══════════════════════════════════════════════════════════════

Du hast den Content Body und den Hook gefunden.
Jetzt baust du den finalen Clip zusammen.

PRINZIPIEN:
• HOOK immer zuerst (Position 0)
• BODY folgt (ggf. gekürzt)
• PAYOFF am Ende (falls vorhanden)
• Gesamtlänge: 20-90 Sekunden ideal

DU ANTWORTEST NUR MIT JSON."""

    rules_text = ""
    if editing_rules:
        rules_text = "\n[EDITING RULES]"
        for rule in editing_rules[:5]:
            rules_text += f"\n• {rule}"
    
    user = f"""
[BODY]
Start: {body_info.get('start', 0):.0f}s
End: {body_info.get('end', 0):.0f}s
Archetyp: {body_info.get('archetype', 'unknown')}
Summary: {body_info.get('summary', '')}

[GEFUNDENER HOOK]
Timestamp: {found_hook.get('hook_timestamp', 0):.0f}s
Text: {found_hook.get('hook_text', '')}
Typ: {found_hook.get('hook_type', 'unknown')}

[PATTERN]
{pattern_name}
{rules_text}

[AUFGABE]
Erstelle die Segment-Liste für den finalen Clip.

[OUTPUT FORMAT]
```json
{{
  "pattern_applied": "{pattern_name}",
  "segments": [
    {{
      "role": "hook",
      "start": {found_hook.get('hook_timestamp', 0)},
      "end": {found_hook.get('hook_end_timestamp', found_hook.get('hook_timestamp', 0) + 5)},
      "clip_position": 0
    }},
    {{
      "role": "body",
      "start": {body_info.get('start', 0)},
      "end": {body_info.get('end', 0)},
      "clip_position": 1
    }}
  ],
  "total_duration_estimate": 60,
  "requires_remix": true,
  "editing_instruction": "Hook von {found_hook.get('hook_timestamp', 0):.0f}s an den Anfang, dann Body von {body_info.get('start', 0):.0f}s"
}}
```
"""
    
    return system.strip(), user.strip()


# =============================================================================
# Response Parsing
# =============================================================================

def parse_content_scouting_response(response: str) -> List[Dict]:
    """Parse the Content Scouting (Phase 1) response."""
    json_match = re.search(r'\[[\s\S]*\]', response)
    if not json_match:
        return []
    
    try:
        candidates = json.loads(json_match.group())
        
        valid = []
        for c in candidates:
            if not isinstance(c, dict):
                continue
            if 'start' not in c or 'end' not in c:
                continue
            
            valid.append({
                'start': float(c.get('start', 0)),
                'end': float(c.get('end', 0)),
                'archetype': c.get('archetype', 'unknown'),
                'summary': c.get('summary', ''),
                'core_message': c.get('core_message', ''),
                'has_native_hook': c.get('has_native_hook', False),
                'text': c.get('text', '')
            })
        
        return valid
    
    except json.JSONDecodeError:
        return []


def parse_global_hook_response(response: str) -> Dict:
    """Parse the Global Hook Hunting (Phase 2) response."""
    json_match = re.search(r'\{[\s\S]*\}', response)
    if not json_match:
        return {}
    
    try:
        hook = json.loads(json_match.group())
        
        if not isinstance(hook, dict):
            return {}
        
        return {
            'hook_timestamp': float(hook.get('hook_timestamp', 0)),
            'hook_end_timestamp': float(hook.get('hook_end_timestamp', hook.get('hook_timestamp', 0) + 5)),
            'hook_text': hook.get('hook_text', ''),
            'hook_type': hook.get('hook_type', 'unknown'),
            'distance_from_body_seconds': float(hook.get('distance_from_body_seconds', 0)),
            'reasoning': hook.get('reasoning', ''),
            'confidence': float(hook.get('confidence', 0.5))
        }
    
    except json.JSONDecodeError:
        return {}


def parse_assembly_response(response: str) -> Dict:
    """Parse the Blueprint Assembly (Phase 3) response."""
    json_match = re.search(r'\{[\s\S]*\}', response)
    if not json_match:
        return {}
    
    try:
        assembly = json.loads(json_match.group())
        
        if not isinstance(assembly, dict):
            return {}
        
        return {
            'pattern_applied': assembly.get('pattern_applied', ''),
            'segments': assembly.get('segments', []),
            'total_duration_estimate': float(assembly.get('total_duration_estimate', 60)),
            'requires_remix': assembly.get('requires_remix', False),
            'editing_instruction': assembly.get('editing_instruction', '')
        }
    
    except json.JSONDecodeError:
        return {}


# =============================================================================
# Legacy Compatibility
# =============================================================================

# Map old function names to new ones
def build_candidate_detection_prompt(*args, **kwargs):
    """Legacy wrapper → Content Scouting."""
    return build_content_scouting_prompt(*args, **kwargs)


def build_hook_hunting_prompt(
    body_summary: str,
    body_text: str,
    context_text: str,
    context_start: float,
    context_end: float,
    archetype: str,
    markers: List[str],
    instruction: str
) -> Tuple[str, str]:
    """Legacy wrapper → Global Hook Hunting."""
    return build_global_hook_hunting_prompt(
        body_summary=body_summary,
        body_core_message=instruction,
        body_start=context_start,
        body_end=context_end,
        archetype=archetype,
        full_transcript_text=context_text
    )


def parse_candidates_response(response: str) -> List[Dict]:
    """Legacy wrapper."""
    return parse_content_scouting_response(response)


def parse_hook_response(response: str) -> Dict:
    """Legacy wrapper."""
    return parse_global_hook_response(response)


def build_discover_prompt(*args, **kwargs):
    """Legacy wrapper."""
    transcript_segments = kwargs.get('transcript_segments', [])
    transcript_text = ""
    for seg in transcript_segments[:500]:
        start = seg.get('start', 0)
        text = seg.get('text', '')
        transcript_text += f"[{start:.1f}s] {text}\n"
    
    archetypes = [
        {"id": "paradox_story", "name": "Story mit Moral", "markers": ["niemals", "das bedeutet"]},
        {"id": "contrarian_rant", "name": "Kontroverse These", "markers": ["ist falsch", "ist müll"]},
        {"id": "listicle", "name": "Liste", "markers": ["3 dinge", "hier sind"]},
        {"id": "insight", "name": "Insight", "markers": ["das wichtigste", "der trick"]}
    ]
    
    return build_content_scouting_prompt(transcript_text, archetypes)


def parse_discover_response(response: str) -> List[Dict]:
    """Legacy wrapper."""
    return parse_content_scouting_response(response)


def build_segmentation_prompt(transcript_text: str, target_block_count=None):
    """Legacy wrapper."""
    archetypes = [
        {"id": "paradox_story", "name": "Story", "markers": []},
        {"id": "insight", "name": "Insight", "markers": []}
    ]
    return build_content_scouting_prompt(transcript_text, archetypes)


def parse_segmentation_response(response: str) -> List[Dict]:
    """Legacy wrapper."""
    return parse_content_scouting_response(response)


# Default examples
DEFAULT_FEW_SHOT_EXAMPLES = [
    {
        "name": "Dieter Lange Pattern",
        "archetype": "paradox_story",
        "description": "Geschichte über alten Mann, Fazit 'Arbeite niemals für Geld' kommt 3 Minuten NACH der Story.",
        "hook_instruction": "Suche das Fazit am ENDE der Geschichte und setze es an den Anfang."
    },
    {
        "name": "Frädrich Rant Pattern",
        "archetype": "contrarian_rant",
        "description": "Rant über Vitamine, provokanteste Aussage mitten im Content.",
        "hook_instruction": "Suche die schärfste/kontroverseste Aussage im ganzen Rant."
    },
    {
        "name": "Podcast Recap Pattern",
        "archetype": "insight",
        "description": "Insight wird am Ende des Podcasts im Recap nochmal zusammengefasst.",
        "hook_instruction": "Suche im Recap/Outro nach einer knackigen Zusammenfassung des Insights."
    }
]
