"""
BRAIN Analysis V4 - Struktur-Archetypen Extraction

Fokus: WAS wurde gemacht, nicht WARUM es funktioniert.

Extrahiert aus den 972 viralen Clips:
1. Archetypen (Paradox Story, Contrarian Rant, Listicle, Insight)
2. Struktur-Templates (Hook-Position, Segment-Reihenfolge)
3. Editing-Patterns (Was wurde umgestellt?)

Output: data/learned_patterns.json
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
import asyncio

from models.base import get_model


# =============================================================================
# Die 4 Haupt-Archetypen
# =============================================================================

ARCHETYPE_DEFINITIONS = {
    "paradox_story": {
        "name": "Paradox Story (Dieter Lange Pattern)",
        "description": "Geschichte mit überraschendem Fazit. Das Fazit wird als Hook nach vorne gezogen.",
        "structure": ["hook", "body", "payoff"],
        "hook_location": "end",  # Der beste Hook ist am ENDE der Story
        "markers": ["arbeite niemals", "das problem ist", "die wahrheit ist", "der trick ist"],
        "examples": ["Dieter Lange: Arbeite niemals für Geld"]
    },
    "contrarian_rant": {
        "name": "Contrarian Rant (Frädrich Pattern)",
        "description": "Provokante These mit anschließendem Beweis.",
        "structure": ["hook", "body", "payoff"],
        "hook_location": "middle",  # Die Kontroverse ist oft versteckt
        "markers": ["ist müll", "ist falsch", "vergiss", "hör auf", "der größte fehler"],
        "examples": ["Frädrich: Eisbergsalat hat so viel Vitamin C wie Papier"]
    },
    "listicle": {
        "name": "Listicle (Nummerierte Liste)",
        "description": "Strukturierte Liste mit Zahl im Hook.",
        "structure": ["hook", "body"],
        "hook_location": "start",  # Hook ist native am Anfang
        "markers": ["3 dinge", "5 gründe", "hier sind", "nummer eins", "erstens"],
        "examples": ["3 Dinge die erfolgreiche Menschen anders machen"]
    },
    "insight": {
        "name": "Insight (Naval Ravikant Pattern)",
        "description": "Einzelner philosophischer Gedanke, Hook ist der Insight selbst.",
        "structure": ["body"],
        "hook_location": "start",  # Hook ist native
        "markers": ["der wichtigste", "das geheimnis", "die einzige", "wenn du verstehst"],
        "examples": ["Naval: Desire is a contract to be unhappy"]
    }
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LearnedPattern:
    """Ein gelerntes Struktur-Muster."""
    archetype: str
    name: str
    description: str
    structure: List[str]  # ["hook", "body", "payoff"]
    hook_location: str  # start, middle, end
    
    # Statistiken
    occurrence_count: int = 0
    avg_views: float = 0
    avg_hook_strength: float = 0
    
    # Beispiele
    example_hooks: List[str] = None
    example_clips: List[str] = None
    
    def __post_init__(self):
        if self.example_hooks is None:
            self.example_hooks = []
        if self.example_clips is None:
            self.example_clips = []


@dataclass
class ClipAnalysis:
    """Analyse eines einzelnen Clips."""
    clip_id: str
    archetype: str
    hook_text: str
    hook_location: str  # start, middle, end
    structure: List[str]
    views: int
    was_remixed: bool  # Wurde der Clip umgestellt?


# =============================================================================
# Brain Analyzer V4
# =============================================================================

class BrainAnalyzer:
    """
    Analysiert virale Clips und extrahiert Struktur-Archetypen.
    
    Ziel: Konkrete "Schablonen" die 1:1 angewendet werden können.
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.training_dir = self.data_dir / "training"
        self.output_file = self.data_dir / "learned_patterns.json"
        
    async def run_full_analysis(self) -> Dict:
        """
        Führt die komplette Archetypen-Analyse durch.
        
        Returns:
            Dict mit gelernten Patterns
        """
        print("\n" + "="*60)
        print("🧠 BRAIN ANALYSIS V4 - Struktur-Archetypen")
        print("="*60)
        
        # Phase 1: Clips laden und klassifizieren
        print("\n📊 Phase 1: Clips klassifizieren...")
        clip_analyses = await self._classify_clips()
        
        # Phase 2: Patterns aggregieren
        print("\n📐 Phase 2: Patterns aggregieren...")
        patterns = self._aggregate_patterns(clip_analyses)
        
        # Phase 3: Speichern
        print("\n💾 Phase 3: Speichern...")
        result = self._save_patterns(patterns, clip_analyses)
        
        print("\n" + "="*60)
        print("✅ ANALYSE ABGESCHLOSSEN")
        print("="*60)
        print(f"   Clips analysiert: {len(clip_analyses)}")
        print(f"   Patterns gefunden: {len(patterns)}")
        print(f"   Output: {self.output_file}")
        
        return result
    
    async def _classify_clips(self) -> List[ClipAnalysis]:
        """
        Klassifiziert alle Clips nach Archetypen.
        
        Verwendet einfache Heuristiken + optional AI für schwierige Fälle.
        """
        goat_file = self.training_dir / "goat_training_data.json"
        
        if not goat_file.exists():
            print("   ⚠️ goat_training_data.json nicht gefunden")
            return []
        
        with open(goat_file) as f:
            clips = json.load(f)
        
        # Nur Clips mit Transkript
        clips_with_text = [
            c for c in clips
            if c.get("transcript", {}).get("text")
        ]
        
        print(f"   Gefunden: {len(clips_with_text)} Clips mit Transkript")
        
        analyses = []
        
        for clip in clips_with_text:
            analysis = self._classify_single_clip(clip)
            if analysis:
                analyses.append(analysis)
        
        # Statistiken
        archetype_counts = Counter(a.archetype for a in analyses)
        print(f"   Klassifiziert:")
        for arch, count in archetype_counts.most_common():
            print(f"      {arch}: {count}")
        
        return analyses
    
    def _classify_single_clip(self, clip: Dict) -> Optional[ClipAnalysis]:
        """
        Klassifiziert einen einzelnen Clip.
        
        Verwendet Marker-basierte Heuristik für Geschwindigkeit.
        """
        text = clip.get("transcript", {}).get("text", "")
        if not text:
            return None
        
        text_lower = text.lower()
        perf = clip.get("performance", {})
        views = perf.get("views", 0)
        
        # Hook extrahieren (erste 2 Sätze)
        sentences = text.replace("!", ".").replace("?", ".").split(".")
        hook_text = ". ".join(s.strip() for s in sentences[:2] if s.strip())
        hook_lower = hook_text.lower()
        
        # Klassifizierung basierend auf Markern
        archetype = "insight"  # Default
        hook_location = "start"
        was_remixed = False
        
        # Check für Listicle
        if any(m in text_lower[:200] for m in ARCHETYPE_DEFINITIONS["listicle"]["markers"]):
            archetype = "listicle"
            hook_location = "start"
        
        # Check für Contrarian Rant
        elif any(m in text_lower for m in ARCHETYPE_DEFINITIONS["contrarian_rant"]["markers"]):
            archetype = "contrarian_rant"
            # Prüfe ob die Kontroverse am Anfang ist
            if any(m in hook_lower for m in ARCHETYPE_DEFINITIONS["contrarian_rant"]["markers"]):
                hook_location = "start"
            else:
                hook_location = "middle"
                was_remixed = True  # Kontroverse wurde wahrscheinlich nach vorne gezogen
        
        # Check für Paradox Story (Story-Marker + Fazit-Marker)
        elif self._is_story(text_lower) and self._has_moral_marker(text_lower):
            archetype = "paradox_story"
            # Prüfe ob das Fazit am Anfang ist (wurde remixed)
            if any(m in hook_lower for m in ARCHETYPE_DEFINITIONS["paradox_story"]["markers"]):
                hook_location = "start"
                was_remixed = True  # Fazit wurde nach vorne gezogen!
            else:
                hook_location = "end"
        
        # Struktur bestimmen
        structure = ARCHETYPE_DEFINITIONS.get(archetype, {}).get("structure", ["body"])
        
        return ClipAnalysis(
            clip_id=clip.get("video_id", "unknown"),
            archetype=archetype,
            hook_text=hook_text[:200],
            hook_location=hook_location,
            structure=structure,
            views=views,
            was_remixed=was_remixed
        )
    
    def _is_story(self, text: str) -> bool:
        """Prüft ob der Text eine Geschichte enthält."""
        story_markers = [
            "es war", "eines tages", "ich erinnere", "vor vielen",
            "eine geschichte", "ich erzähle", "stell dir vor",
            "als ich", "vor kurzem", "letzte woche"
        ]
        return any(m in text for m in story_markers)
    
    def _has_moral_marker(self, text: str) -> bool:
        """Prüft ob der Text ein Fazit/Moral hat."""
        moral_markers = [
            "das bedeutet", "die moral", "der punkt ist", "das heißt",
            "niemals", "immer", "der trick", "das geheimnis", "deshalb"
        ]
        return any(m in text for m in moral_markers)
    
    def _aggregate_patterns(self, analyses: List[ClipAnalysis]) -> List[LearnedPattern]:
        """
        Aggregiert die Clip-Analysen zu Patterns.
        """
        # Gruppiere nach Archetyp
        by_archetype: Dict[str, List[ClipAnalysis]] = {}
        for a in analyses:
            if a.archetype not in by_archetype:
                by_archetype[a.archetype] = []
            by_archetype[a.archetype].append(a)
        
        patterns = []
        
        for archetype, clips in by_archetype.items():
            definition = ARCHETYPE_DEFINITIONS.get(archetype, {})
            
            # Statistiken berechnen
            total_views = sum(c.views for c in clips)
            avg_views = total_views / len(clips) if clips else 0
            remixed_count = sum(1 for c in clips if c.was_remixed)
            
            # Top Hooks sammeln (nach Views sortiert)
            top_clips = sorted(clips, key=lambda c: c.views, reverse=True)[:10]
            example_hooks = [c.hook_text for c in top_clips]
            
            patterns.append(LearnedPattern(
                archetype=archetype,
                name=definition.get("name", archetype),
                description=definition.get("description", ""),
                structure=definition.get("structure", ["body"]),
                hook_location=definition.get("hook_location", "start"),
                occurrence_count=len(clips),
                avg_views=avg_views,
                avg_hook_strength=7.0,  # Placeholder
                example_hooks=example_hooks,
                example_clips=[c.clip_id for c in top_clips[:5]]
            ))
        
        # Sortiere nach Occurrence
        patterns.sort(key=lambda p: p.occurrence_count, reverse=True)
        
        return patterns
    
    def _save_patterns(
        self, 
        patterns: List[LearnedPattern], 
        analyses: List[ClipAnalysis]
    ) -> Dict:
        """Speichert die Patterns als JSON."""
        
        # Berechne Remix-Statistiken
        total_remixed = sum(1 for a in analyses if a.was_remixed)
        remix_rate = total_remixed / len(analyses) if analyses else 0
        
        result = {
            "version": "4.0",
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_clips_analyzed": len(analyses),
                "total_remixed": total_remixed,
                "remix_rate": f"{remix_rate:.1%}",
            },
            "archetypes": {
                p.archetype: asdict(p) for p in patterns
            },
            "patterns_list": [asdict(p) for p in patterns],
            # Spezial-Sektion für Hook-Hunting
            "hook_hunting_rules": {
                "paradox_story": {
                    "search_location": "end",
                    "search_radius_seconds": 120,
                    "markers": ARCHETYPE_DEFINITIONS["paradox_story"]["markers"],
                    "instruction": "Suche das Fazit/die Moral am ENDE der Geschichte und ziehe es an den Anfang."
                },
                "contrarian_rant": {
                    "search_location": "middle",
                    "search_radius_seconds": 60,
                    "markers": ARCHETYPE_DEFINITIONS["contrarian_rant"]["markers"],
                    "instruction": "Suche die provokanteste Aussage und stelle sie an den Anfang."
                },
                "listicle": {
                    "search_location": "start",
                    "search_radius_seconds": 0,
                    "markers": ARCHETYPE_DEFINITIONS["listicle"]["markers"],
                    "instruction": "Der Hook ist bereits am Anfang (die Zahl/Liste)."
                },
                "insight": {
                    "search_location": "start",
                    "search_radius_seconds": 0,
                    "markers": ARCHETYPE_DEFINITIONS["insight"]["markers"],
                    "instruction": "Der Hook ist der Insight selbst. Clean extraction."
                }
            }
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {self.output_file}")
        
        return result


# =============================================================================
# Helper Functions
# =============================================================================

def load_learned_patterns() -> Dict:
    """Lädt die gelernten Patterns."""
    patterns_file = Path(__file__).parent.parent / "data" / "learned_patterns.json"
    
    if patterns_file.exists():
        with open(patterns_file) as f:
            return json.load(f)
    return {}


def get_archetype_template(archetype: str) -> Dict:
    """Holt das Template für einen Archetyp."""
    patterns = load_learned_patterns()
    return patterns.get("archetypes", {}).get(archetype, {})


def get_hook_hunting_rule(archetype: str) -> Dict:
    """Holt die Hook-Hunting Regel für einen Archetyp."""
    patterns = load_learned_patterns()
    return patterns.get("hook_hunting_rules", {}).get(archetype, {})


# =============================================================================
# Entry Point
# =============================================================================

async def run_analysis():
    """Run full BRAIN analysis."""
    analyzer = BrainAnalyzer()
    return await analyzer.run_full_analysis()


if __name__ == "__main__":
    asyncio.run(run_analysis())
