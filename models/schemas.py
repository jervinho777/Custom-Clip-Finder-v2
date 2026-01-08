"""
Pydantic Response Schemas for Structured AI Outputs

V4: Editor Workflow Architecture
- Simple, modular data structures
- "Content First, Hook Second" paradigm
- Clear Archetypen: Paradox Story, Contrarian Rant, Listicle, Insight
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


# ============================================================================
# Enums - Die 4 Archetypen
# ============================================================================

class Archetype(str, Enum):
    """Die 4 viralen Archetypen (Struktur-basiert)."""
    PARADOX_STORY = "paradox_story"  # Fazit als Hook -> Story -> Payoff
    CONTRARIAN_RANT = "contrarian_rant"  # Provokante These -> Beweis
    LISTICLE = "listicle"  # "Hier sind 3 Dinge..." -> 1, 2, 3
    INSIGHT = "insight"  # Einzelner philosophischer Gedanke
    TUTORIAL = "tutorial"  # How-To mit Ergebnis-Hook
    EMOTIONAL = "emotional"  # Persönliche Story mit Peak
    UNKNOWN = "unknown"


class SegmentRole(str, Enum):
    """Rolle eines Segments im finalen Clip."""
    HOOK = "hook"      # Aufmerksamkeits-Grabber (erste 3 Sekunden)
    SETUP = "setup"    # Kontext/Einleitung
    BODY = "body"      # Hauptinhalt
    PAYOFF = "payoff"  # Fazit/Punchline


# ============================================================================
# Core Data Structures
# ============================================================================

class Segment(BaseModel):
    """Ein einzelnes Segment im Clip."""
    start: float = Field(description="Startzeit im Originalvideo (Sekunden)")
    end: float = Field(description="Endzeit im Originalvideo (Sekunden)")
    role: SegmentRole = Field(description="Rolle im finalen Clip")
    text: str = Field(default="", description="Der Text dieses Segments")
    
    @property
    def duration(self) -> float:
        return self.end - self.start


class ContentBody(BaseModel):
    """
    Ein gefundener Inhalts-Block (Phase A: Candidate Detection).
    
    Das ist der "Rohdiamant" - ein zusammenhängender Inhaltsblock
    BEVOR wir nach einem Hook suchen.
    """
    start: float
    end: float
    text: str
    archetype: Archetype = Field(default=Archetype.UNKNOWN)
    topic_summary: str = Field(default="", description="1-Satz Zusammenfassung")
    has_native_hook: bool = Field(default=False, description="Hat der Anfang schon einen Hook?")
    needs_hook_hunt: bool = Field(default=True, description="Müssen wir nach Hook suchen?")


class FoundHook(BaseModel):
    """
    Ein gefundener Hook (Phase B: Hook Hunting).
    
    Kann aus dem Body selbst kommen oder aus dem Kontext.
    """
    start: float
    end: float
    text: str
    source: Literal["native", "from_body_end", "from_context", "from_later"] = Field(
        description="Woher der Hook kommt"
    )
    distance_from_body: float = Field(
        default=0,
        description="Sekunden Entfernung vom Body (negativ=davor, positiv=danach)"
    )


class Moment(BaseModel):
    """
    Ein viraler Moment = ContentBody + FoundHook + Editing Instructions.
    
    Das ist das finale Ergebnis: Ein "Virtual Cut" der:
    1. Den Body enthält (die Geschichte/der Inhalt)
    2. Den Hook enthält (ggf. von woanders)
    3. Editing-Anweisungen für den Zusammenbau
    """
    # Die Segment-Liste (non-linear!)
    segments: List[Segment] = Field(
        description="Geordnete Liste der Segmente für den finalen Clip"
    )
    
    # Archetype & Pattern
    archetype: Archetype
    pattern_name: str = Field(
        default="",
        description="Name des verwendeten Patterns (z.B. 'Dieter Lange Pattern')"
    )
    
    # Content
    hook_text: str = Field(description="Der Hook-Text (erste 3 Sekunden)")
    body_summary: str = Field(description="Zusammenfassung des Body")
    full_text: str = Field(default="", description="Vollständiger Text des Clips")
    
    # Scores
    hook_strength: int = Field(ge=1, le=10, default=5)
    viral_potential: int = Field(ge=1, le=10, default=5)
    
    # Editing
    editing_instruction: str = Field(
        default="",
        description="Menschenlesbare Schnittanweisung"
    )
    requires_remix: bool = Field(
        default=False,
        description="True wenn Segmente umgestellt werden müssen"
    )
    
    # Reasoning
    reasoning: str = Field(default="", description="Warum dieser Moment viral ist")
    
    # Computed properties for legacy compatibility
    @property
    def start(self) -> float:
        """Frühester Zeitpunkt aller Segmente."""
        if self.segments:
            return min(s.start for s in self.segments)
        return 0.0
    
    @property
    def end(self) -> float:
        """Spätester Zeitpunkt aller Segmente."""
        if self.segments:
            return max(s.end for s in self.segments)
        return 0.0
    
    @property
    def total_duration(self) -> float:
        """Gesamtdauer des zusammengesetzten Clips."""
        return sum(s.duration for s in self.segments)


# ============================================================================
# Archetypen-Templates (die "Schablonen")
# ============================================================================

class ArchetypeTemplate(BaseModel):
    """
    Ein gelerntes Struktur-Muster aus dem Brain.
    
    Beispiel: "Paradox Story"
    - Struktur: [HOOK: Fazit] -> [BODY: Story] -> [PAYOFF: Fazit wiederholt]
    - Beispiel: Dieter Lange "Arbeite niemals für Geld"
    """
    name: str = Field(description="Name des Archetyps")
    archetype: Archetype
    structure: List[SegmentRole] = Field(
        description="Reihenfolge der Rollen im finalen Clip"
    )
    description: str = Field(description="Beschreibung des Musters")
    hook_location: Literal["start", "middle", "end", "external"] = Field(
        description="Wo der beste Hook typischerweise zu finden ist"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Beispiele dieses Patterns"
    )
    views_weighted_score: float = Field(
        default=0.0,
        description="Performance-Score basierend auf Views"
    )


# ============================================================================
# Discovery Response
# ============================================================================

class DiscoveryResult(BaseModel):
    """Ergebnis der Discovery Phase."""
    # Gefundene Moments
    moments: List[Moment] = Field(default_factory=list)
    
    # Statistiken
    total_bodies_found: int = Field(default=0, description="Anzahl gefundener Content Bodies")
    hooks_hunted: int = Field(default=0, description="Anzahl Hooks die gesucht werden mussten")
    remixed_count: int = Field(default=0, description="Anzahl Moments die Remix brauchen")
    
    # Metadata
    video_duration: float = Field(default=0)
    processing_time_seconds: float = Field(default=0)


# ============================================================================
# Legacy Compatibility
# ============================================================================

# Alte Namen als Aliase
VideoSegment = Segment
NonLinearMoment = Moment
ViralArchetype = Archetype

class Timestamp(BaseModel):
    """Legacy Timestamp (für alte Funktionen)."""
    start: float
    end: float
