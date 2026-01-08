"""
STAGE 1: DISCOVER (V5 - Global Hook Hunting Edition)

"Content First, Hook Second" - Aber OHNE Zeitgrenzen!

Der Hook kann 30 Minuten nach dem Body kommen.
Wie Dieter Lange: Story bei 09:00, Fazit bei 12:00.

═══════════════════════════════════════════════════════════════
3-PHASEN-PROZESS:
═══════════════════════════════════════════════════════════════

PHASE 1: CONTENT SCOUTING ("Das Sichten")
- Scanne nach zusammenhängenden Inhalts-Blöcken
- Finde nur den "Body" (Rohdiamant)
- Ignoriere erstmal ob der Anfang gut ist

PHASE 2: GLOBAL HOOK HUNTING ("Die Suche")
- Für jeden Body: Suche im GESAMTEN Transkript
- KEINE Zeitgrenzen! Der Hook kann überall sein
- Nutze Vector Store für semantische Ähnlichkeit
- Nutze LLM für finale Auswahl

PHASE 3: BLUEPRINT ASSEMBLY ("Der Schnitt")
- Wende das passende Pattern an
- Erstelle die Segment-Liste
- Generiere Editing-Anweisungen

═══════════════════════════════════════════════════════════════
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import asyncio
import time
import logging

# Setup logging
logger = logging.getLogger(__name__)

from models.base import get_model
from models.schemas import (
    Segment, SegmentRole, ContentBody, FoundHook, 
    Moment, Archetype, DiscoveryResult
)
from brain.analyze import (
    load_learned_patterns, 
    get_hook_hunting_rule,
    ARCHETYPE_DEFINITIONS
)
from brain.vector_store import (
    VectorStore,
    GlobalHookCandidate,
    find_global_hooks
)
from prompts.discover import (
    build_content_scouting_prompt,
    build_global_hook_hunting_prompt,
    build_assembly_prompt,
    parse_content_scouting_response,
    parse_global_hook_response,
    parse_assembly_response,
    DEFAULT_FEW_SHOT_EXAMPLES
)
from utils import Cache


# =============================================================================
# Configuration - KEINE ZEITGRENZEN MEHR!
# =============================================================================

# Alte Konstante entfernt:
# HOOK_SEARCH_RADIUS = 180  # ❌ GELÖSCHT - Keine Zeitgrenzen!

# Mindest-/Maximaldauer für Content Bodies
MIN_BODY_DURATION = 20
MAX_BODY_DURATION = 180

# Mindestdauer für finalen Clip
MIN_CLIP_DURATION = 15
MAX_CLIP_DURATION = 120

# Wie viele Hook-Kandidaten pro Body prüfen wir?
MAX_HOOK_CANDIDATES = 10


# =============================================================================
# Helper: Transcript Formatting
# =============================================================================

def format_transcript_with_timestamps(segments: List[Dict]) -> str:
    """Formatiert Transkript-Segmente mit Zeitstempeln."""
    lines = []
    for seg in segments:
        start = seg.get('start', 0)
        text = seg.get('text', '')
        speaker = seg.get('speaker', '')
        
        if speaker:
            lines.append(f"[{start:.1f}s] [{speaker}] {text}")
        else:
            lines.append(f"[{start:.1f}s] {text}")
    
    return "\n".join(lines)


def get_text_at_timerange(
    segments: List[Dict], 
    start: float, 
    end: float
) -> str:
    """Extrahiert Text aus einem Zeitbereich."""
    texts = []
    for seg in segments:
        seg_start = seg.get('start', 0)
        seg_end = seg.get('end', seg_start + 1)
        
        if seg_start >= start and seg_end <= end:
            texts.append(seg.get('text', ''))
        elif seg_start < end and seg_end > start:
            # Overlap
            texts.append(seg.get('text', ''))
    
    return " ".join(texts)


def get_video_duration(segments: List[Dict]) -> float:
    """Berechnet die Gesamtlänge des Videos."""
    if not segments:
        return 0.0
    return max(seg.get('end', seg.get('start', 0)) for seg in segments)


# =============================================================================
# FUZZY MATCHING für Text → Timestamp
# =============================================================================

def find_text_timestamp_fuzzy(
    search_text: str,
    segments: List[Dict],
    min_similarity: float = 0.85
) -> Optional[Tuple[float, float, str, bool]]:
    """
    Findet den Timestamp für einen Text mit Fuzzy Matching.
    
    PROBLEM: Die KI identifiziert Hook-Text, aber Whisper-Transkript
    hat kleine Fehler oder die KI halluziniert leicht.
    
    LÖSUNG: 
    1. Versuche exakten Match
    2. Bei Fehlschlag: Fuzzy Match mit >85% Ähnlichkeit
    3. Logge Warnung bei Fuzzy Match
    
    Args:
        search_text: Der zu suchende Text (von KI identifiziert)
        segments: Die Transkript-Segmente
        min_similarity: Minimale Ähnlichkeit für Fuzzy Match (default 85%)
        
    Returns:
        Tuple von (start_time, end_time, matched_text, was_fuzzy)
        oder None wenn kein Match gefunden
    """
    if not search_text or not segments:
        return None
    
    # Normalisiere Suchtext
    search_normalized = search_text.lower().strip()
    
    # STEP 1: Exakter Match
    for seg in segments:
        seg_text = seg.get('text', '').lower().strip()
        
        if search_normalized in seg_text or seg_text in search_normalized:
            # Exakter Match gefunden
            return (
                seg.get('start', 0),
                seg.get('end', seg.get('start', 0) + 5),
                seg.get('text', ''),
                False  # was_fuzzy = False
            )
    
    # STEP 2: Fuzzy Match - Suche besten Match
    best_match = None
    best_similarity = 0.0
    
    # Baue vollständigen Text für Sliding Window
    full_text_segments = []
    for seg in segments:
        full_text_segments.append({
            'start': seg.get('start', 0),
            'end': seg.get('end', seg.get('start', 0) + 1),
            'text': seg.get('text', '')
        })
    
    # Sliding Window über Segmente (1-3 Segmente kombiniert)
    for window_size in [1, 2, 3]:
        for i in range(len(full_text_segments) - window_size + 1):
            window_segs = full_text_segments[i:i + window_size]
            window_text = " ".join(s['text'] for s in window_segs).lower().strip()
            
            # Berechne Ähnlichkeit
            similarity = SequenceMatcher(
                None, 
                search_normalized, 
                window_text
            ).ratio()
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'start': window_segs[0]['start'],
                    'end': window_segs[-1]['end'],
                    'text': " ".join(s['text'] for s in window_segs),
                    'similarity': similarity
                }
            
            # Auch Substring-Match prüfen
            if len(search_normalized) > 20:
                # Suche kürzeren Text im längeren
                if len(window_text) > len(search_normalized):
                    # Sliding window im Window
                    for j in range(len(window_text) - len(search_normalized) + 1):
                        substr = window_text[j:j + len(search_normalized)]
                        sub_sim = SequenceMatcher(None, search_normalized, substr).ratio()
                        if sub_sim > best_similarity:
                            best_similarity = sub_sim
                            best_match = {
                                'start': window_segs[0]['start'],
                                'end': window_segs[-1]['end'],
                                'text': " ".join(s['text'] for s in window_segs),
                                'similarity': sub_sim
                            }
    
    # Prüfe ob bester Match über Schwelle liegt
    if best_match and best_similarity >= min_similarity:
        logger.warning(
            f"⚠️ FUZZY MATCH verwendet ({best_similarity:.0%} Ähnlichkeit): "
            f"Gesucht: '{search_text[:50]}...' → "
            f"Gefunden: '{best_match['text'][:50]}...' @ {best_match['start']:.1f}s"
        )
        print(
            f"      ⚠️ Fuzzy Match ({best_similarity:.0%}): "
            f"'{search_text[:30]}...' → '{best_match['text'][:30]}...' @ {best_match['start']:.1f}s"
        )
        
        return (
            best_match['start'],
            best_match['end'],
            best_match['text'],
            True  # was_fuzzy = True
        )
    
    # Kein Match gefunden
    if best_match:
        logger.warning(
            f"❌ Kein Match gefunden (beste Ähnlichkeit: {best_similarity:.0%}): "
            f"'{search_text[:50]}...'"
        )
    
    return None


def find_hook_timestamp(
    hook_text: str,
    segments: List[Dict],
    fallback_timestamp: Optional[float] = None
) -> Tuple[float, float]:
    """
    Findet den Timestamp für einen Hook-Text.
    
    Wrapper um find_text_timestamp_fuzzy mit Fallback-Logik.
    
    Args:
        hook_text: Der Hook-Text
        segments: Die Transkript-Segmente
        fallback_timestamp: Fallback-Timestamp wenn kein Match
        
    Returns:
        Tuple von (start_time, end_time)
    """
    result = find_text_timestamp_fuzzy(hook_text, segments)
    
    if result:
        start, end, matched_text, was_fuzzy = result
        return start, end
    
    # Fallback
    if fallback_timestamp is not None:
        logger.warning(
            f"❌ Hook-Text nicht gefunden, verwende Fallback @ {fallback_timestamp:.1f}s: "
            f"'{hook_text[:50]}...'"
        )
        return fallback_timestamp, fallback_timestamp + 5.0
    
    # Letzter Fallback: Anfang des Videos
    logger.error(f"❌ Hook-Text nicht gefunden und kein Fallback: '{hook_text[:50]}...'")
    return 0.0, 5.0


# =============================================================================
# PHASE 1: CONTENT SCOUTING (Find the Body)
# =============================================================================

async def phase1_content_scouting(
    transcript_segments: List[Dict],
    learned_patterns: Dict
) -> List[ContentBody]:
    """
    Phase 1: Content Scouting - Finde die Rohdiamanten.
    
    Scannt das Transkript nach zusammenhängenden Inhaltsblöcken:
    - Vollständige Geschichten
    - Zusammenhängende Argumentationen
    - Standalone Insights
    
    NOCH KEINE Hook-Bewertung! Nur Content finden.
    
    Args:
        transcript_segments: Das vollständige Transkript
        learned_patterns: Gelernte Muster aus dem Brain
        
    Returns:
        Liste von ContentBody Objekten (Rohdiamanten)
    """
    print("\n" + "─"*50)
    print("📍 PHASE 1: Content Scouting")
    print("─"*50)
    
    # Formatiere Transkript
    transcript_text = format_transcript_with_timestamps(transcript_segments)
    video_duration = get_video_duration(transcript_segments)
    
    # Hole Archetypen für den Prompt
    archetypes_info = []
    for arch_id, arch_data in ARCHETYPE_DEFINITIONS.items():
        archetypes_info.append({
            "id": arch_id,
            "name": arch_data["name"],
            "markers": arch_data.get("markers", [])[:3]
        })
    
    # Build Prompt
    system_prompt, user_prompt = build_content_scouting_prompt(
        transcript_text=transcript_text,
        archetypes=archetypes_info,
        min_duration=MIN_BODY_DURATION,
        max_duration=MAX_BODY_DURATION,
        video_duration_minutes=video_duration / 60 if video_duration else None
    )
    
    # Schnelles Modell für Phase 1
    try:
        model = get_model("anthropic", tier="sonnet")
    except ValueError:
        try:
            model = get_model("openai", tier="flagship")
        except ValueError:
            model = get_model("openai", tier="mini")
    
    print(f"   🔍 Scanning with {model.provider}...")
    
    response = await model.generate(
        user_prompt,
        system=system_prompt,
        temperature=0.5,
        max_tokens=4000
    )
    
    # Parse Response
    candidates = parse_content_scouting_response(response.content)
    
    # Konvertiere zu ContentBody Objekten
    bodies = []
    for c in candidates:
        archetype_str = c.get('archetype', 'unknown')
        
        # Prüfe ob Hook native ist oder gesucht werden muss
        has_native = c.get('has_native_hook', False)
        
        try:
            archetype = Archetype(archetype_str)
        except ValueError:
            archetype = Archetype.UNKNOWN
        
        # Hole Text aus Transkript
        body_text = get_text_at_timerange(
            transcript_segments,
            c.get('start', 0),
            c.get('end', 0)
        )
        
        bodies.append(ContentBody(
            start=c.get('start', 0),
            end=c.get('end', 0),
            text=body_text[:500] if body_text else c.get('text', ''),
            archetype=archetype,
            topic_summary=c.get('summary', ''),
            has_native_hook=has_native,
            needs_hook_hunt=not has_native
        ))
    
    print(f"   ✅ Found {len(bodies)} content bodies:")
    for i, b in enumerate(bodies[:8]):
        marker = "✓ native" if b.has_native_hook else "🔍 needs hunt"
        print(f"      {i+1}. [{b.start:.0f}s-{b.end:.0f}s] {b.archetype.value} | {marker}")
        print(f"         └─ {b.topic_summary[:50]}...")
    
    return bodies


# =============================================================================
# PHASE 2: GLOBAL HOOK HUNTING (NO TIME LIMITS!)
# =============================================================================

async def phase2_global_hook_hunting(
    body: ContentBody,
    transcript_segments: List[Dict],
    learned_patterns: Dict
) -> FoundHook:
    """
    Phase 2: Global Hook Hunting - KEINE ZEITGRENZEN!
    
    Sucht den besten Hook für einen Body im GESAMTEN Transkript.
    Der Hook kann 30 Minuten nach dem Body kommen!
    
    Zwei-Stufen-Prozess:
    1. Vector Store: Finde semantisch passende "punchy" Sätze
    2. LLM: Wähle den besten Hook aus den Kandidaten
    
    Args:
        body: Der Content Body für den wir einen Hook suchen
        transcript_segments: Das KOMPLETTE Transkript (kein Truncation!)
        learned_patterns: Gelernte Muster
        
    Returns:
        FoundHook Objekt
    """
    # Wenn Native Hook, extrahiere vom Anfang
    if body.has_native_hook:
        native_text = get_text_at_timerange(
            transcript_segments, 
            body.start, 
            min(body.start + 8, body.end)
        )
        return FoundHook(
            start=body.start,
            end=min(body.start + 8, body.end),
            text=native_text[:200] if native_text else "Native hook",
            source="native",
            distance_from_body=0
        )
    
    print(f"      🌍 Global Hook Hunt für: {body.topic_summary[:40]}...")
    
    # ===================
    # Stufe 1: Vector Store Pre-Scan
    # ===================
    print(f"         Stage 1: Vector Store pre-scan...")
    
    # Hole Kandidaten aus dem gesamten Transkript
    try:
        hook_candidates = await find_global_hooks(
            body_topic=body.topic_summary,
            transcript_segments=transcript_segments,
            top_k=MAX_HOOK_CANDIDATES
        )
    except Exception as e:
        print(f"         ⚠️ Vector Store failed: {e}")
        hook_candidates = []
    
    # Format Kandidaten für LLM
    pre_scanned = []
    if hook_candidates:
        print(f"         Found {len(hook_candidates)} pre-scanned candidates")
        for cand in hook_candidates[:5]:
            pre_scanned.append({
                "timestamp": cand.timestamp,
                "text": cand.sentence,
                "punch_score": cand.punch_score,
                "semantic_score": cand.semantic_score,
                "viral_match": cand.matched_viral_hook
            })
            print(f"            • [{cand.timestamp:.0f}s] {cand.sentence[:50]}... (punch: {cand.punch_score:.2f})")
    
    # ===================
    # Stufe 2: LLM Final Selection
    # ===================
    print(f"         Stage 2: LLM final selection...")
    
    # Formatiere vollständiges Transkript
    full_transcript_text = format_transcript_with_timestamps(transcript_segments)
    
    # Hole Named Patterns
    named_patterns = learned_patterns.get('named_patterns', DEFAULT_FEW_SHOT_EXAMPLES)
    
    # Build Prompt
    system_prompt, user_prompt = build_global_hook_hunting_prompt(
        body_summary=body.topic_summary,
        body_core_message=body.topic_summary,  # TODO: Könnte separates Feld sein
        body_start=body.start,
        body_end=body.end,
        archetype=body.archetype.value,
        full_transcript_text=full_transcript_text,
        pre_scanned_candidates=pre_scanned,
        named_patterns=named_patterns
    )
    
    # Schnelles aber gutes Modell für Entscheidung
    try:
        model = get_model("anthropic", tier="sonnet")
    except ValueError:
        try:
            model = get_model("openai", tier="flagship")
        except ValueError:
            model = get_model("openai", tier="mini")
    
    response = await model.generate(
        user_prompt,
        system=system_prompt,
        temperature=0.3,
        max_tokens=800
    )
    
    # Parse Hook
    hook_data = parse_global_hook_response(response.content)
    
    if hook_data and hook_data.get('hook_text'):
        hook_text = hook_data.get('hook_text', '')
        llm_timestamp = hook_data.get('hook_timestamp', 0)
        
        # FUZZY MATCHING: Finde den exakten Timestamp für den Hook-Text
        # Die KI gibt einen Text zurück, aber Whisper-Transkript kann leicht abweichen
        fuzzy_result = find_text_timestamp_fuzzy(hook_text, transcript_segments)
        
        if fuzzy_result:
            # Fuzzy Match gefunden
            actual_start, actual_end, matched_text, was_fuzzy = fuzzy_result
            
            if was_fuzzy:
                print(f"         📍 Timestamp korrigiert: {llm_timestamp:.0f}s → {actual_start:.0f}s")
            
            hook_start = actual_start
            hook_end = actual_end
            final_hook_text = matched_text[:200]
        else:
            # Kein Match - verwende LLM Timestamp als Fallback
            logger.warning(
                f"Hook-Text nicht im Transkript gefunden, verwende LLM-Timestamp: "
                f"'{hook_text[:50]}...' @ {llm_timestamp:.0f}s"
            )
            print(f"         ⚠️ Hook-Text nicht gefunden, verwende LLM-Timestamp @ {llm_timestamp:.0f}s")
            hook_start = llm_timestamp
            hook_end = hook_data.get('hook_end_timestamp', llm_timestamp + 5)
            final_hook_text = hook_text[:200]
        
        distance = hook_start - body.start
        
        # Bestimme Source basierend auf Distanz
        if abs(distance) < 30:
            source = "native"
        elif distance > 0:
            source = "from_later"  # Hook kommt nach dem Body
        else:
            source = "from_earlier"  # Hook kommt vor dem Body
        
        print(f"         ✅ Found hook: \"{final_hook_text[:50]}...\"")
        print(f"            @ {hook_start:.0f}s | Distance: {distance:.0f}s | Type: {hook_data.get('hook_type', 'unknown')}")
        
        return FoundHook(
            start=hook_start,
            end=hook_end,
            text=final_hook_text,
            source=source,
            distance_from_body=distance
        )
    
    # Fallback: Bester Vector Store Kandidat
    if hook_candidates:
        best = hook_candidates[0]
        print(f"         ⚠️ LLM fallback to best vector match @ {best.timestamp:.0f}s")
        return FoundHook(
            start=best.timestamp,
            end=best.end_timestamp,
            text=best.sentence[:200],
            source="from_vector_store",
            distance_from_body=best.timestamp - body.start
        )
    
    # Letzter Fallback: Native Hook
    print(f"         ⚠️ Fallback to native hook")
    native_text = get_text_at_timerange(
        transcript_segments, 
        body.start, 
        min(body.start + 10, body.end)
    )
    return FoundHook(
        start=body.start,
        end=min(body.start + 10, body.end),
        text=native_text[:200] if native_text else "Fallback hook",
        source="native",
        distance_from_body=0
    )


# =============================================================================
# PHASE 3: BLUEPRINT ASSEMBLY (Der Schnitt)
# =============================================================================

def phase3_blueprint_assembly(
    body: ContentBody,
    hook: FoundHook,
    transcript_segments: List[Dict],
    learned_patterns: Dict
) -> Moment:
    """
    Phase 3: Blueprint Assembly - Der finale Schnitt.
    
    Setzt Body + Hook zu einem fertigen Moment zusammen.
    Wendet das passende Pattern an.
    
    Args:
        body: Der Content Body
        hook: Der gefundene Hook
        transcript_segments: Für Text-Extraktion
        learned_patterns: Gelernte Muster
        
    Returns:
        Fertiges Moment Objekt
    """
    segments = []
    requires_remix = hook.source != "native"
    
    # Segment 1: Hook (immer Position 0)
    segments.append(Segment(
        start=hook.start,
        end=hook.end,
        role=SegmentRole.HOOK,
        text=hook.text
    ))
    
    # Segment 2: Body
    body_start = body.start
    body_end = body.end
    
    # Wenn Hook vom Ende des Bodies kommt, adjust Body
    if hook.source == "from_later" and hook.start > body.end:
        # Hook ist NACH dem Body, also Body komplett abspielen
        pass
    elif hook.source == "from_later" and hook.start >= body.start and hook.start < body.end:
        # Hook ist im Body, also Body bis Hook
        body_end = min(body.end, hook.start)
    
    body_text = get_text_at_timerange(transcript_segments, body_start, body_end)
    
    segments.append(Segment(
        start=body_start,
        end=body_end,
        role=SegmentRole.BODY,
        text=body_text
    ))
    
    # Optional: Payoff (wenn Hook vom Ende kam)
    if hook.source in ["from_later", "from_body_end"] and hook.distance_from_body > 30:
        # Der vollständige Payoff nach dem Hook
        payoff_start = hook.start
        payoff_end = hook.end + 10  # Etwas Kontext nach dem Hook
        
        payoff_text = get_text_at_timerange(transcript_segments, payoff_start, payoff_end)
        if payoff_text:
            segments.append(Segment(
                start=payoff_start,
                end=payoff_end,
                role=SegmentRole.PAYOFF,
                text=payoff_text
            ))
    
    # Pattern Name basierend auf Archetyp und Hook-Source
    if hook.source == "from_later" and body.archetype == Archetype.PARADOX_STORY:
        pattern_name = "Dieter Lange Pattern"
    elif hook.source == "from_later" and body.archetype == Archetype.CONTRARIAN_RANT:
        pattern_name = "Frädrich Pattern"
    elif hook.source == "from_later":
        pattern_name = "Podcast Recap Pattern"
    else:
        pattern_name = f"Clean {body.archetype.value.title()}"
    
    # Editing Instruction
    if requires_remix:
        editing = f"REMIX: Hole Hook von {hook.start:.0f}s (Distance: {hook.distance_from_body:.0f}s), dann Body ab {body_start:.0f}s"
    else:
        editing = f"CLEAN CUT: {body_start:.0f}s bis {body_end:.0f}s"
    
    # Viral Potential Scoring
    hook_strength = 8 if requires_remix else 6
    if abs(hook.distance_from_body) > 120:  # > 2 Minuten Distanz
        hook_strength += 1  # Bonus für kreative Remixe
    
    viral_potential = hook_strength
    if body.archetype in [Archetype.PARADOX_STORY, Archetype.CONTRARIAN_RANT]:
        viral_potential += 1
    
    return Moment(
        segments=segments,
        archetype=body.archetype,
        pattern_name=pattern_name,
        hook_text=hook.text,
        body_summary=body.topic_summary,
        full_text=body.text,
        hook_strength=min(10, hook_strength),
        viral_potential=min(10, viral_potential),
        editing_instruction=editing,
        requires_remix=requires_remix,
        reasoning=f"Archetyp: {body.archetype.value}. Hook: {hook.source} @ {hook.start:.0f}s (Distance: {hook.distance_from_body:.0f}s)"
    )


# =============================================================================
# Main Discovery Function (3-Phasen-Prozess)
# =============================================================================

async def discover_moments(
    transcript_segments: List[Dict],
    video_path: Optional[str] = None,
    use_cache: bool = True
) -> List[Moment]:
    """
    Hauptfunktion: Findet virale Momente mit dem 3-Phasen-Editor-Workflow.
    
    ═══════════════════════════════════════════════════════════════
    DER 3-PHASEN-PROZESS:
    ═══════════════════════════════════════════════════════════════
    
    PHASE 1: CONTENT SCOUTING
    - Scanne das Transkript nach Rohdiamanten
    - Finde vollständige Stories, Rants, Insights
    
    PHASE 2: GLOBAL HOOK HUNTING (KEINE ZEITGRENZEN!)
    - Für jeden Body: Suche im GESAMTEN Video nach dem Hook
    - Vector Store Pre-Scan + LLM Final Selection
    
    PHASE 3: BLUEPRINT ASSEMBLY
    - Wende das passende Pattern an
    - Erstelle die Segment-Liste
    
    Args:
        transcript_segments: Das Transkript (VOLLSTÄNDIG!)
        video_path: Für Caching
        use_cache: Cache nutzen?
        
    Returns:
        Liste von Moment Objekten, sortiert nach Viral Potential
    """
    start_time = time.time()
    cache = Cache()
    
    # Check Cache
    if use_cache and video_path:
        cached = cache.get_pipeline_result(video_path, "discover_v5")
        if cached:
            print("Using cached DISCOVER V5 results")
            moments_data = cached.get("result", {}).get("moments", [])
            return [Moment(**m) for m in moments_data]
    
    print("\n" + "═"*60)
    print("🎬 DISCOVER V5 - Global Hook Hunting Edition")
    print("═"*60)
    print("   ⚠️  KEINE ZEITGRENZEN - Hooks können überall sein!")
    
    video_duration = get_video_duration(transcript_segments)
    print(f"   📊 Video: {video_duration/60:.1f} Minuten | {len(transcript_segments)} Segmente")
    
    # Lade gelernte Patterns
    print("\n📚 Loading patterns from Brain...")
    learned_patterns = load_learned_patterns()
    if learned_patterns:
        print(f"   ✓ Loaded {len(learned_patterns.get('archetypes', {}))} archetypes")
    else:
        print("   ⚠️ No learned patterns found. Using defaults.")
        learned_patterns = {}
    
    # ===================
    # PHASE 1: Content Scouting
    # ===================
    bodies = await phase1_content_scouting(transcript_segments, learned_patterns)
    
    if not bodies:
        print("\n   ❌ No content bodies found!")
        return []
    
    # ===================
    # PHASE 2: Global Hook Hunting
    # ===================
    print("\n" + "─"*50)
    print("🌍 PHASE 2: Global Hook Hunting")
    print("─"*50)
    print("   🔓 NO TIME LIMITS - Searching entire transcript!")
    
    moments = []
    hooks_hunted = 0
    global_hooks_found = 0
    
    for i, body in enumerate(bodies):
        print(f"\n   [{i+1}/{len(bodies)}] {body.archetype.value}: {body.topic_summary[:40]}...")
        
        # Global Hook Hunting
        hook = await phase2_global_hook_hunting(
            body, 
            transcript_segments, 
            learned_patterns
        )
        
        if hook.source != "native":
            hooks_hunted += 1
            if abs(hook.distance_from_body) > 60:  # > 1 Minute
                global_hooks_found += 1
        
        # ===================
        # PHASE 3: Blueprint Assembly
        # ===================
        moment = phase3_blueprint_assembly(body, hook, transcript_segments, learned_patterns)
        moments.append(moment)
    
    # Sortiere nach Viral Potential
    moments.sort(key=lambda m: m.viral_potential, reverse=True)
    
    # ===================
    # Summary
    # ===================
    elapsed = time.time() - start_time
    remixed_count = sum(1 for m in moments if m.requires_remix)
    
    print("\n" + "═"*60)
    print("✅ DISCOVERY COMPLETE")
    print("═"*60)
    print(f"   📊 Total Moments: {len(moments)}")
    print(f"   🔍 Hooks Hunted: {hooks_hunted}")
    print(f"   🌍 Global Hooks (>1min distance): {global_hooks_found}")
    print(f"   🔀 Requires Remix: {remixed_count}")
    print(f"   ⏱️  Processing Time: {elapsed:.1f}s")
    
    print("\n   🏆 Top 5 Moments:")
    for i, m in enumerate(moments[:5]):
        remix = "🌍 REMIX" if m.requires_remix else "✂️ CLEAN"
        print(f"      {i+1}. [{m.start:.0f}s-{m.end:.0f}s] {remix} | {m.archetype.value} | Potential: {m.viral_potential}/10")
        if m.requires_remix:
            print(f"         └─ {m.editing_instruction}")
    
    # Cache Results
    if video_path:
        cache.set_pipeline_result(video_path, "discover_v5", {
            "moments": [m.model_dump() for m in moments],
            "statistics": {
                "total_bodies": len(bodies),
                "hooks_hunted": hooks_hunted,
                "global_hooks_found": global_hooks_found,
                "remixed_count": remixed_count,
                "processing_time": elapsed
            }
        })
    
    return moments


# =============================================================================
# Legacy Compatibility
# =============================================================================

async def discover_with_voting(
    transcript_segments: List[Dict],
    top_n: int = 10
) -> List[Moment]:
    """Legacy function - redirects to main discover."""
    moments = await discover_moments(transcript_segments, use_cache=False)
    return moments[:top_n]


# Legacy names
detect_content_bodies = phase1_content_scouting
hunt_hook_for_body = phase2_global_hook_hunting
assemble_moment = phase3_blueprint_assembly
