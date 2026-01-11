"""
BRAIN Analysis V4.5 - Hybrid Semantic Archetypen Extraction

Powered by Claude Opus 4.5 (claude-opus-4-5-20251101)

Fokus: WAS wurde gemacht, nicht WARUM es funktioniert.

HYBRID-ANSATZ:
1. Lädt alle Clips aus goat_training_data.json
2. Nutzt Claude Opus 4.5 für semantische Analyse
3. Extrahiert: Archetype, Hook, Payoff, Emotional Driver, Viral Intensity
4. Speichert in data/learned_patterns.json

CLI:
    uv run python brain/analyze.py                 # 100% aller Clips
    uv run python brain/analyze.py --sample 0.1   # 10% der Clips
"""

import json
import asyncio
import logging
import random
import argparse
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import Counter

from dotenv import load_dotenv
load_dotenv()

# Importiere die DNA Kriterien für Konsistenz
from prompts.discover import VIRAL_DNA_CRITERIA

# Model Detection
from models.auto_detect import get_model, KNOWN_MODELS

# Anthropic SDK
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ anthropic package not installed. Run: uv add anthropic")


# =============================================================================
# Logger Setup
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Die 6 Haupt-Archetypen (Konstanten)
# =============================================================================

ARCHETYPE_DEFINITIONS = {
    "paradox_story": {
        "name": "Paradox Story (Dieter Lange Pattern)",
        "description": "Geschichte mit überraschendem Fazit. Das Fazit wird als Hook nach vorne gezogen.",
        "structure": ["hook", "body", "payoff"],
        "hook_location": "end",
        "markers": ["arbeite niemals", "das problem ist", "die wahrheit ist", "der trick ist"],
        "emotional_drivers": ["surprise", "wisdom", "revelation"],
    },
    "contrarian_rant": {
        "name": "Contrarian Rant (Frädrich Pattern)",
        "description": "Provokante These mit anschließendem Beweis. Tonfall ist emotional/wütend.",
        "structure": ["hook", "body", "payoff"],
        "hook_location": "middle",
        "markers": ["ist müll", "ist falsch", "vergiss", "hör auf", "der größte fehler"],
        "emotional_drivers": ["anger", "frustration", "righteous_indignation"],
    },
    "listicle": {
        "name": "Listicle (Nummerierte Liste)",
        "description": "Strukturierte Liste mit Zahl im Hook.",
        "structure": ["hook", "body"],
        "hook_location": "start",
        "markers": ["3 dinge", "5 gründe", "hier sind", "nummer eins", "erstens"],
        "emotional_drivers": ["curiosity", "completeness", "value"],
    },
    "insight": {
        "name": "Insight (Naval Ravikant Pattern)",
        "description": "Einzelner philosophischer Gedanke, Hook ist der Insight selbst.",
        "structure": ["body"],
        "hook_location": "start",
        "markers": ["der wichtigste", "das geheimnis", "die einzige", "wenn du verstehst"],
        "emotional_drivers": ["wisdom", "truth", "clarity"],
    },
    "tutorial": {
        "name": "Tutorial (How-To Pattern)",
        "description": "Praktische Anleitung mit Ergebnis-Hook.",
        "structure": ["hook", "body", "payoff"],
        "hook_location": "start",
        "markers": ["so machst du", "schritt für schritt", "hier ist wie"],
        "emotional_drivers": ["empowerment", "value", "competence"],
    },
    "emotional": {
        "name": "Emotional (Story Peak Pattern)",
        "description": "Persönliche Geschichte mit emotionalem Höhepunkt.",
        "structure": ["setup", "body", "peak"],
        "hook_location": "peak",
        "markers": ["ich habe geweint", "es hat mich verändert", "in diesem moment"],
        "emotional_drivers": ["empathy", "connection", "vulnerability"],
    }
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ClipPattern:
    """Analysiertes Pattern eines einzelnen Clips."""
    clip_id: str
    username: str
    views: int
    
    archetype: str
    confidence: float
    reasoning: str
    
    hook_text: str
    hook_location: str
    is_hook_remixed: bool
    
    payoff_text: str
    emotional_driver: str
    viral_intensity: int
    
    key_phrase: str
    target_audience: str


# =============================================================================
# Opus 4.5 Client
# =============================================================================

class OpusClient:
    """
    Client für Claude Opus 4.5 API.
    
    Model: claude-opus-4-5-20251101 (STRIKTE VORGABE)
    """
    
    # STRIKTE MODEL ID
    MODEL_ID = "claude-opus-4-5-20251101"
    
    def __init__(self):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: uv add anthropic")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=api_key)
        self.model = self.MODEL_ID
        
        logger.info(f"🤖 OpusClient initialized with model: {self.model}")
    
    async def analyze_clip(self, clip: Dict) -> Optional[Dict]:
        """
        Analysiert einen Clip semantisch mit Claude Opus 4.5.
        
        Returns:
            Dict mit Analyse-Ergebnissen oder None bei Fehler
        """
        transcript = clip.get("transcript", {}).get("text", "")
        if len(transcript) < 50:
            return None
        
        username = clip.get("username", "unknown")
        views = clip.get("performance", {}).get("views", 0)
        
        system_prompt = f"""You are an Expert Viral Architect running on Claude Opus 4.5.
Your goal: Deconstruct the viral structure of this clip.

{VIRAL_DNA_CRITERIA}

═══════════════════════════════════════════════════════════════
ARCHETYPES TO DETECT:
═══════════════════════════════════════════════════════════════

1. paradox_story - Unexpected twist/lesson (Dieter Lange Style)
2. contrarian_rant - Provocative thesis + proof (Stefan Frädrich Style)  
3. listicle - Enumeration ("3 things that...")
4. insight - Deep philosophical realization (Naval Style)
5. tutorial - How-To with result hook
6. emotional - Personal story with emotional peak

═══════════════════════════════════════════════════════════════
CRITICAL: OUTPUT ONLY VALID JSON. NO MARKDOWN.
═══════════════════════════════════════════════════════════════"""

        user_prompt = f"""ANALYZE THIS TRANSCRIPT:

METADATA:
- Account: {username}
- Views: {views:,}

TRANSCRIPT:
{transcript[:2500]}

═══════════════════════════════════════════════════════════════
TASKS:
═══════════════════════════════════════════════════════════════

1. Classify the Archetype (paradox_story, contrarian_rant, listicle, insight, tutorial, emotional)
2. Extract the exact 'Hook' (first 3-5s concept that grabs attention)
3. Extract the 'Payoff' (the resolution/conclusion)
4. Identify the 'Emotional Driver' (Anger, Greed, Validation, Fear, Curiosity, etc.)
5. Score the 'Viral Intensity' (1-10) based on the DNA Criteria
6. Determine if the hook was REMIXED (moved from another position)

OUTPUT (JSON ONLY):
{{
  "archetype": "paradox_story",
  "confidence": 0.85,
  "reasoning": "Brief explanation why this archetype fits...",
  
  "hook_text": "The exact hook sentence or concept",
  "hook_location": "end",
  "is_hook_remixed": true,
  
  "payoff_text": "The conclusion or punchline",
  "emotional_driver": "surprise",
  "viral_intensity": 8,
  
  "key_phrase": "The one sentence that summarizes everything",
  "target_audience": "Entrepreneurs, Self-improvement seekers"
}}"""

        try:
            # Synchroner Call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.0,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                system=system_prompt
            )
            
            # Parse JSON response
            content = response.content[0].text
            
            # Extract JSON (handle potential markdown code blocks)
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            # Add metadata
            data['clip_id'] = clip.get('video_id', 'unknown')
            data['username'] = username
            data['views'] = views
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Error for clip {clip.get('video_id', 'unknown')}: {e}")
            return None
        except Exception as e:
            logger.error(f"Opus analysis failed for clip {clip.get('video_id', 'unknown')}: {e}")
            return None


# =============================================================================
# Brain Analyzer V4.5
# =============================================================================

class BrainAnalyzer:
    """
    Brain Analyzer V4.5 - Powered by Claude Opus 4.5
    
    Analysiert virale Clips und extrahiert Struktur-Patterns.
    
    SMART RESUME: Überspringt bereits analysierte Clips.
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.training_file = self.data_dir / "training" / "goat_training_data.json"
        self.output_file = self.data_dir / "learned_patterns.json"
        
        self.opus_client: Optional[OpusClient] = None
        self.existing_patterns: List[Dict] = []  # Für Resume
        self.existing_clip_ids: set = set()  # Für schnellen Lookup
    
    def _load_existing_patterns(self) -> Tuple[List[Dict], set]:
        """
        Lädt existierende Patterns für Smart Resume.
        
        Returns:
            Tuple von (patterns_list, set_of_clip_ids)
        """
        if not self.output_file.exists():
            return [], set()
        
        try:
            with open(self.output_file, 'r') as f:
                data = json.load(f)
            
            # Extrahiere raw_patterns (enthält clip_ids)
            patterns = data.get("raw_patterns", [])
            
            # Extrahiere alle clip_ids
            clip_ids = set()
            for p in patterns:
                clip_id = p.get("clip_id")
                if clip_id:
                    clip_ids.add(clip_id)
            
            return patterns, clip_ids
            
        except Exception as e:
            logger.warning(f"Could not load existing patterns: {e}")
            return [], set()
    
    async def run_full_analysis(self, sample_rate: float = 1.0, force_restart: bool = False) -> Dict:
        """
        Führt die komplette Analyse durch.
        
        SMART RESUME: Überspringt bereits analysierte Clips automatisch.
        
        Args:
            sample_rate: Anteil der Clips (0.0 - 1.0), Default 1.0 = 100%
            force_restart: Wenn True, ignoriere existierende Patterns und starte neu
        """
        print("\n" + "="*60)
        print("🧠 BRAIN ANALYSIS V4.5 - Opus Powered")
        print("="*60)
        print(f"   Model: claude-opus-4-5-20251101")
        print(f"   Sample Rate: {sample_rate*100:.0f}%")
        
        # =====================================================================
        # SMART RESUME: Lade existierende Patterns
        # =====================================================================
        if not force_restart:
            self.existing_patterns, self.existing_clip_ids = self._load_existing_patterns()
            
            if self.existing_clip_ids:
                print(f"\n🔄 SMART RESUME AKTIVIERT")
                print(f"   Found {len(self.existing_clip_ids)} existing patterns")
        else:
            print(f"\n⚠️ FORCE RESTART: Ignoriere existierende Patterns")
            self.existing_patterns = []
            self.existing_clip_ids = set()
        
        # Initialize Opus Client
        try:
            self.opus_client = OpusClient()
        except Exception as e:
            print(f"❌ Failed to initialize Opus Client: {e}")
            return {}
        
        # Load Training Data
        print("\n📊 Loading training data...")
        if not self.training_file.exists():
            print(f"❌ Training data not found: {self.training_file}")
            return {}
        
        with open(self.training_file, 'r') as f:
            all_clips = json.load(f)
        
        # Filter clips with transcript
        clips_with_transcript = [
            c for c in all_clips
            if c.get("transcript", {}).get("text") and len(c.get("transcript", {}).get("text", "")) > 50
        ]
        
        print(f"   Total clips: {len(all_clips)}")
        print(f"   With transcript: {len(clips_with_transcript)}")
        
        # =====================================================================
        # SMART RESUME: Filtere bereits analysierte Clips
        # =====================================================================
        if self.existing_clip_ids:
            clips = [
                c for c in clips_with_transcript
                if c.get("video_id") not in self.existing_clip_ids
            ]
            
            skipped = len(clips_with_transcript) - len(clips)
            print(f"\n🔄 Resuming Analysis:")
            print(f"   ✅ Already analyzed: {skipped} clips (skipping)")
            print(f"   📋 Remaining to analyze: {len(clips)} clips")
        else:
            clips = clips_with_transcript
        
        # Check if nothing to do
        if not clips:
            print(f"\n✅ All clips already analyzed! Nothing to do.")
            # Return existing data
            if self.output_file.exists():
                with open(self.output_file, 'r') as f:
                    return json.load(f)
            return {}
        
        # Sampling (nur auf verbleibende Clips anwenden)
        if sample_rate < 1.0:
            sample_size = max(1, int(len(clips) * sample_rate))
            clips = random.sample(clips, sample_size)
            print(f"   📉 Subsampling: Analyzing {len(clips)} of remaining clips")
        else:
            print(f"   🔥 FULL POWER: Analyzing ALL {len(clips)} remaining clips")
        
        # Analyze with concurrency limit
        print("\n🤖 Running Opus 4.5 Analysis...")
        
        new_results = []
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        failed_count = 0
        
        async def analyze_with_limit(clip: Dict, index: int, total: int) -> Optional[Dict]:
            nonlocal failed_count
            async with semaphore:
                # Berechne globalen Index (existing + current)
                global_index = len(self.existing_clip_ids) + index + 1
                total_global = len(self.existing_clip_ids) + total
                
                print(f"   [{global_index}/{total_global}] Analyzing {clip.get('video_id', 'unknown')[:30]}...")
                
                try:
                    result = await self.opus_client.analyze_clip(clip)
                    
                    # Small delay to respect rate limits
                    await asyncio.sleep(0.3)
                    
                    return result
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed: {clip.get('video_id', 'unknown')}: {e}")
                    
                    # Bei zu vielen Fehlern: Früh speichern und abbrechen
                    if failed_count >= 5:
                        print(f"\n⚠️ Too many failures ({failed_count}). Saving progress...")
                        raise Exception("Too many API failures")
                    
                    return None
        
        try:
            # Create tasks
            tasks = [
                analyze_with_limit(clip, i, len(clips)) 
                for i, clip in enumerate(clips)
            ]
            
            # Execute all
            analyses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results (exclude exceptions)
            new_results = [
                a for a in analyses 
                if a is not None and not isinstance(a, Exception)
            ]
            
        except Exception as e:
            logger.error(f"Analysis interrupted: {e}")
            print(f"\n⚠️ Analysis interrupted. Saving partial results...")
        
        # =====================================================================
        # MERGE: Kombiniere existierende + neue Patterns
        # =====================================================================
        all_results = self.existing_patterns + new_results
        
        print(f"\n✅ Analysis complete:")
        print(f"   Existing patterns: {len(self.existing_patterns)}")
        print(f"   New patterns: {len(new_results)}")
        print(f"   Total: {len(all_results)}")
        
        # Aggregate patterns (nutze ALLE Ergebnisse)
        print("\n📐 Aggregating patterns...")
        aggregated = self._aggregate_patterns(all_results)
        
        # Berechne Statistiken
        total_clips_in_db = len(clips_with_transcript) if 'clips_with_transcript' in dir() else len(all_results)
        
        # Build output
        output = {
            "version": "4.5-hybrid",
            "model": OpusClient.MODEL_ID,
            "generated_at": datetime.now().isoformat(),
            
            "statistics": {
                "total_clips_in_db": total_clips_in_db,
                "total_clips_analyzed": len(all_results),
                "new_clips_this_run": len(new_results),
                "existing_clips_resumed": len(self.existing_patterns),
                "success_rate": f"{len(all_results)/total_clips_in_db*100:.1f}%" if total_clips_in_db > 0 else "N/A",
                "sample_rate": f"{sample_rate*100:.0f}%",
                "is_complete": len(all_results) >= total_clips_in_db
            },
            
            "archetype_definitions": ARCHETYPE_DEFINITIONS,
            "archetypes": aggregated["archetypes"],
            "patterns_list": aggregated["patterns_list"],
            "hook_hunting_rules": aggregated["hook_hunting_rules"],
            
            "raw_patterns": all_results  # MERGED: alte + neue Patterns
        }
        
        # Save
        print("\n💾 Saving results...")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to: {self.output_file}")
        
        # Print Summary
        self._print_summary(all_results, aggregated)
        
        return output
    
    def _aggregate_patterns(self, results: List[Dict]) -> Dict:
        """Aggregiert die Einzelergebnisse zu Patterns."""
        
        by_archetype: Dict[str, List[Dict]] = {}
        
        for r in results:
            arch = r.get("archetype", "insight")
            if arch not in by_archetype:
                by_archetype[arch] = []
            by_archetype[arch].append(r)
        
        archetypes = {}
        patterns_list = []
        
        for arch, clips in by_archetype.items():
            definition = ARCHETYPE_DEFINITIONS.get(arch, {})
            
            # Stats
            total_views = sum(c.get("views", 0) for c in clips)
            avg_views = total_views / len(clips) if clips else 0
            
            avg_intensity = sum(c.get("viral_intensity", 5) for c in clips) / len(clips) if clips else 5
            avg_confidence = sum(c.get("confidence", 0.5) for c in clips) / len(clips) if clips else 0.5
            
            remixed_count = sum(1 for c in clips if c.get("is_hook_remixed", False))
            remix_rate = remixed_count / len(clips) if clips else 0
            
            # Top examples (by views)
            top_clips = sorted(clips, key=lambda c: c.get("views", 0), reverse=True)[:10]
            
            # Emotional drivers distribution
            emotional_drivers = Counter(c.get("emotional_driver", "unknown") for c in clips)
            
            pattern = {
                "archetype": arch,
                "name": definition.get("name", arch),
                "description": definition.get("description", ""),
                "structure": definition.get("structure", ["body"]),
                "hook_location": definition.get("hook_location", "start"),
                
                "occurrence_count": len(clips),
                "avg_views": round(avg_views, 0),
                "avg_viral_intensity": round(avg_intensity, 1),
                "avg_confidence": round(avg_confidence, 2),
                "remix_rate": round(remix_rate, 2),
                
                "example_hooks": [c.get("hook_text", "") for c in top_clips if c.get("hook_text")],
                "example_payoffs": [c.get("payoff_text", "") for c in top_clips if c.get("payoff_text")],
                "example_clips": [c.get("clip_id", "") for c in top_clips[:5]],
                
                "common_emotional_drivers": dict(emotional_drivers.most_common(5)),
                "common_key_phrases": [c.get("key_phrase", "") for c in top_clips if c.get("key_phrase")][:5]
            }
            
            archetypes[arch] = pattern
            patterns_list.append(pattern)
        
        # Sort by occurrence
        patterns_list.sort(key=lambda p: p["occurrence_count"], reverse=True)
        
        # Hook Hunting Rules
        hook_hunting_rules = {
            arch_id: {
                "search_location": arch_def.get("hook_location", "start"),
                "markers": arch_def.get("markers", []),
                "emotional_drivers": arch_def.get("emotional_drivers", []),
                "instruction": self._get_hunt_instruction(arch_id, arch_def),
                "remix_rate": archetypes.get(arch_id, {}).get("remix_rate", 0)
            }
            for arch_id, arch_def in ARCHETYPE_DEFINITIONS.items()
        }
        
        return {
            "archetypes": archetypes,
            "patterns_list": patterns_list,
            "hook_hunting_rules": hook_hunting_rules
        }
    
    def _get_hunt_instruction(self, arch_id: str, arch_def: Dict) -> str:
        """Generiert Hook-Hunting Anweisung."""
        location = arch_def.get("hook_location", "start")
        
        instructions = {
            "end": "Suche das Fazit/die Moral am ENDE und ziehe es an den Anfang.",
            "middle": "Suche die emotionalste/provokanteste Aussage und stelle sie nach vorne.",
            "peak": "Suche den emotionalen Höhepunkt und verwende ihn als Hook.",
            "start": "Der Hook ist bereits am Anfang. Clean extraction."
        }
        
        return instructions.get(location, "Analysiere die Struktur und finde den besten Hook.")
    
    def _print_summary(self, results: List[Dict], aggregated: Dict):
        """Druckt Zusammenfassung."""
        print("\n" + "="*60)
        print("✅ BRAIN ANALYSIS V4.5 COMPLETE")
        print("="*60)
        
        print(f"\n📊 STATISTIKEN:")
        print(f"   Clips analysiert: {len(results)}")
        print(f"   Model: {OpusClient.MODEL_ID}")
        
        print(f"\n🎯 ARCHETYPEN-VERTEILUNG:")
        for p in aggregated["patterns_list"]:
            remix = f" (Remix: {p['remix_rate']*100:.0f}%)" if p['remix_rate'] > 0.1 else ""
            intensity = f" | Intensity: {p['avg_viral_intensity']:.1f}"
            print(f"   {p['archetype']}: {p['occurrence_count']} clips{remix}{intensity}")
        
        print(f"\n💡 TOP HOOKS:")
        for p in aggregated["patterns_list"][:3]:
            if p.get("example_hooks"):
                hook = p["example_hooks"][0][:60] + "..." if len(p["example_hooks"][0]) > 60 else p["example_hooks"][0]
                print(f"   [{p['archetype']}] \"{hook}\"")
        
        print(f"\n📁 Output: {self.output_file}")


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
    """Gibt Template für Archetyp zurück."""
    return load_learned_patterns().get("archetypes", {}).get(archetype, {})


def get_hook_hunting_rule(archetype: str) -> Dict:
    """Gibt Hook-Hunting Regel zurück."""
    return load_learned_patterns().get("hook_hunting_rules", {}).get(archetype, {})


def get_archetype_definition(archetype: str) -> Dict:
    """Gibt Archetyp-Definition zurück."""
    return ARCHETYPE_DEFINITIONS.get(archetype, {})


# =============================================================================
# CLI
# =============================================================================

async def run_analysis(sample_rate: float = 1.0, force_restart: bool = False) -> Dict:
    """
    Entry point für Analyse.
    
    Args:
        sample_rate: Anteil der Clips (0.0 - 1.0)
        force_restart: Ignoriere existierende Patterns und starte neu
    """
    analyzer = BrainAnalyzer()
    return await analyzer.run_full_analysis(
        sample_rate=sample_rate, 
        force_restart=force_restart
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Brain V4.5 Analysis (Powered by Claude Opus 4.5)"
    )
    parser.add_argument(
        "--sample",
        type=float,
        default=1.0,
        help="Fraction of clips to analyze (0.0 - 1.0). Default: 1.0 (100%%)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force restart: Ignore existing patterns and re-analyze all clips"
    )
    
    args = parser.parse_args()
    
    # Validate sample rate
    sample_rate = max(0.01, min(1.0, args.sample))
    
    print(f"🧠 Starting BRAIN V4.5 Analysis")
    print(f"   Model: claude-opus-4-5-20251101")
    print(f"   Sample Rate: {sample_rate*100:.0f}%")
    print(f"   Force Restart: {args.force}")
    
    asyncio.run(run_analysis(sample_rate=sample_rate, force_restart=args.force))
