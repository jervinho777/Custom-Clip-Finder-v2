"""
BRAIN Analysis Phase

Phase 1 des Systems: Lernen aus existierenden Daten

Code 1: Analysiert isolierte virale Clips → Extrahiert Patterns
Code 2: Analysiert Longform→Clip Paare → Extrahiert Composition Patterns
Code 3: Führt beide zusammen → Erstellt PRINCIPLES.json

Wird einmalig initial und dann wöchentlich ausgeführt.
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from models.base import get_model


class BrainAnalyzer:
    """
    Analysiert Trainingsdaten und erstellt/aktualisiert PRINCIPLES.json
    
    Flowchart:
    Virale Clips ──► Code 1 ──► isolated_patterns
                         ↘
    Paare ──────────► Code 2 ──► composition_patterns
                         ↘
                    Code 3 ──► PRINCIPLES.json
    """
    
    def __init__(self):
        self.brain_dir = Path(__file__).parent
        self.data_dir = Path(__file__).parent.parent / "data"
        self.training_dir = self.data_dir / "training"
        self.learnings_dir = self.data_dir / "learnings"
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        
        # Output files
        self.isolated_patterns_file = self.learnings_dir / "isolated_patterns.json"
        self.composition_patterns_file = self.learnings_dir / "composition_patterns.json"
        self.principles_file = self.brain_dir / "PRINCIPLES.json"
    
    async def run_full_analysis(self) -> Dict:
        """
        Führt komplette Analyse-Pipeline aus.
        
        Returns:
            Dict mit Statistiken und generierten Principles
        """
        print("\n" + "="*70)
        print("🧠 BRAIN ANALYSIS PHASE")
        print("="*70)
        
        # Code 1: Isolierte Clips analysieren
        print("\n📊 CODE 1: Analysiere isolierte virale Clips...")
        isolated_patterns = await self._analyze_isolated_clips()
        
        # Code 2: Paare analysieren
        print("\n🔄 CODE 2: Analysiere Longform→Clip Paare...")
        composition_patterns = await self._analyze_pairs()
        
        # Code 3: Zusammenführen
        print("\n🎯 CODE 3: Synthetisiere Master Principles...")
        principles = await self._synthesize_principles(
            isolated_patterns, 
            composition_patterns
        )
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)
        print(f"   Isolated Patterns: {len(isolated_patterns.get('patterns', []))}")
        print(f"   Composition Patterns: {len(composition_patterns.get('patterns', []))}")
        print(f"   Output: {self.principles_file}")
        
        return {
            "isolated_patterns": isolated_patterns,
            "composition_patterns": composition_patterns,
            "principles": principles
        }
    
    async def _analyze_isolated_clips(self) -> Dict:
        """
        Code 1: Analysiert isolierte virale Clips.
        
        Extrahiert:
        - Hook-Patterns (was funktioniert in ersten 3 Sekunden)
        - Content-Typen (Story, Insight, Tutorial, etc.)
        - Performance-Korrelationen
        """
        # Load training data
        goat_file = self.training_dir / "goat_training_data.json"
        
        if not goat_file.exists():
            print("   ⚠️ goat_training_data.json nicht gefunden")
            return {"patterns": [], "source": "none"}
        
        with open(goat_file) as f:
            clips = json.load(f)
        
        # Filter high performers (>500k views)
        high_performers = [
            c for c in clips
            if c.get("performance", {}).get("views", 0) >= 500000
        ]
        
        print(f"   Gefunden: {len(high_performers)} High-Performer Clips")
        
        if not high_performers:
            return {"patterns": [], "source": "goat_training_data.json"}
        
        # Configurable sample size (default: 50 for cost efficiency, can be increased)
        # More clips = better patterns, but higher cost
        max_clips_to_analyze = int(os.getenv("BRAIN_MAX_CLIPS_ANALYZE", "50"))
        max_clips_in_prompt = int(os.getenv("BRAIN_MAX_CLIPS_IN_PROMPT", "20"))
        
        # Use all high performers if less than max, otherwise sample
        if len(high_performers) <= max_clips_to_analyze:
            sample = high_performers
            print(f"   Analysiere alle {len(sample)} High-Performer")
        else:
            sample = high_performers[:max_clips_to_analyze]
            print(f"   Analysiere Sample von {len(sample)}/{len(high_performers)} High-Performern (max_clips_to_analyze={max_clips_to_analyze})")
        
        # Build analysis prompt (use subset for prompt to stay within token limits)
        clips_text = ""
        clips_for_prompt = sample[:max_clips_in_prompt]
        print(f"   Verwende {len(clips_for_prompt)} Clips im Prompt (max_clips_in_prompt={max_clips_in_prompt})")
        
        for i, clip in enumerate(clips_for_prompt, 1):
            perf = clip.get("performance", {})
            transcript = clip.get("transcript", {}).get("text", "")[:500]
            clips_text += f"""
Clip {i}:
Views: {perf.get('views', 0):,}
Completion Rate: {perf.get('completion_rate', 0):.0%}
Hook (erste 100 chars): {transcript[:100]}
---
"""
        
        from models.base import get_model
        model = get_model("anthropic", tier="sonnet")  # Sonnet für Analyse
        
        response = await model.generate(
            prompt=f"""Analysiere diese Top-Performer Clips und extrahiere PRINZIPIEN (nicht Regeln!):

{clips_text}

WICHTIG: Extrahiere PRINZIPIEN, nicht Regeln!

❌ KEINE Regeln wie:
- "Hook muss immer das Wort X enthalten"
- "Hook muss genau 3 Sekunden lang sein"
- "Clip muss immer mit Frage beginnen"

✅ STATTDESSEN Prinzipien wie:
- "Hooks funktionieren, wenn sie kognitive Dissonanz erzeugen"
- "Hooks sollten so kurz wie möglich, aber so lang wie nötig sein"
- "Fragen funktionieren als Hooks, wenn sie eine Information Gap öffnen"

Extrahiere:
1. Hook-Prinzipien: WARUM funktionieren die erfolgreichsten Hooks? (Nicht WAS sie enthalten)
2. Content-Prinzipien: Welche übergeordneten Konzepte machen Content viral? (Nicht welche Wörter)
3. Strukturelle Prinzipien: Welche Prinzipien stecken hinter erfolgreichen Clip-Strukturen? (Nicht feste Templates)

Antworte als JSON:
{{
  "hook_principles": [
    {{
      "principle": "Das übergeordnete Prinzip (z.B. 'Kognitive Dissonanz erzeugt Aufmerksamkeit')",
      "why_works": "Warum funktioniert dieses Prinzip psychologisch?",
      "examples": ["Beispiel 1", "Beispiel 2"],
      "application": "Wie kann man dieses Prinzip auf andere Situationen anwenden?",
      "frequency": "X%"
    }}
  ],
  "content_principles": [
    {{
      "principle": "Übergeordnetes Content-Prinzip",
      "why_works": "Warum funktioniert es?",
      "characteristics": ["Merkmal 1", "Merkmal 2"],
      "application": "Wie anwenden?"
    }}
  ],
  "structural_principles": [
    {{
      "principle": "Strukturelles Prinzip (z.B. 'Spannung aufbauen und auflösen')",
      "why_works": "Warum funktioniert diese Struktur?",
      "application": "Wie kann man das Prinzip flexibel anwenden?"
    }}
  ]
}}""",
            system="""Du bist ein Prinzipien-Extraktor für Viral Content. 

WICHTIG: Du extrahierst PRINZIPIEN, nicht Regeln!

Prinzipien sind:
- Übergeordnete Konzepte, die auf verschiedene Situationen anwendbar sind
- Erklären WARUM etwas funktioniert, nicht WAS es ist
- Flexibel und kontextabhängig anwendbar

Regeln sind:
- Starre Vorschriften ("muss immer X enthalten")
- Feste Templates ("immer 3 Sekunden")
- Kontext-unabhängige Formeln

Extrahiere nur Prinzipien!""",
            temperature=0.3
        )
        
        # Parse response
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            patterns = json.loads(json_match.group()) if json_match else {}
        except:
            patterns = {"raw_response": response.content}
        
        patterns["source"] = "goat_training_data.json"
        patterns["clips_analyzed"] = len(sample)
        patterns["total_high_performers"] = len(high_performers)
        patterns["sample_size"] = max_clips_to_analyze
        patterns["analyzed_at"] = datetime.now().isoformat()
        
        # Save
        with open(self.isolated_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {self.isolated_patterns_file.name}")
        
        return patterns
    
    async def _analyze_pairs(self) -> Dict:
        """
        Code 2: Analysiert Longform→Clip Paare.
        
        Extrahiert:
        - Transformation Patterns (wie wird gekürzt)
        - Hook Extraction Techniques
        - Cutting Principles
        
        Sucht zuerst nach vorhandenen restructure_analysis_*.json Dateien.
        Falls keine gefunden, analysiert Paare aus pairs_config.json.
        """
        # Load existing restructure analyses
        existing_analyses = list(self.learnings_dir.glob("restructure_analysis_*.json"))
        
        if existing_analyses:
            print(f"   Gefunden: {len(existing_analyses)} vorhandene Pair-Analysen")
            all_patterns = []
            for analysis_file in existing_analyses:
                try:
                    with open(analysis_file) as f:
                        analysis = json.load(f)
                    
                    # Prüfe ob composition_principles vorhanden (neue Struktur)
                    if "composition_principles" in analysis:
                        all_patterns.append({
                            "source": analysis_file.name,
                            "principles": analysis["composition_principles"]
                        })
                except:
                    continue
            
            # Wenn keine composition_principles gefunden, analysiere aus Transkripten
            if not all_patterns:
                print("   ⚠️ Vorhandene Analysen haben keine 'composition_principles'")
                print("   📋 Analysiere Paare aus pairs_config.json...")
                existing_analyses = []  # Force re-analysis
            else:
                print(f"   ✅ {len(all_patterns)} Analysen mit composition_principles gefunden")
        
        if not existing_analyses or not all_patterns:
            # Keine vorhandenen Analysen - analysiere Paare aus Config
            print("   ⚠️ Keine vorhandenen Analysen gefunden")
            print("   📋 Analysiere Paare aus pairs_config.json...")
            
            pairs_config = self.training_dir / "pairs_config.json"
            transcripts_dir = self.data_dir / "cache" / "transcripts"
            
            if not pairs_config.exists():
                print(f"   ❌ pairs_config.json nicht gefunden: {pairs_config}")
                return {"patterns": [], "source": "none"}
            
            with open(pairs_config) as f:
                config = json.load(f)
            
            all_patterns = []
            for pair in config.get("pairs", []):
                longform_file = transcripts_dir / pair["longform"]
                clip_file = transcripts_dir / pair["clip"]
                
                if not longform_file.exists():
                    print(f"   ⚠️ Longform nicht gefunden: {pair['longform']}")
                    continue
                if not clip_file.exists():
                    print(f"   ⚠️ Clip nicht gefunden: {pair['clip']}")
                    continue
                
                # Lade Transkripte
                with open(longform_file) as f:
                    longform = json.load(f)
                with open(clip_file) as f:
                    clip = json.load(f)
                
                # Analysiere Transformation
                pattern = await self._analyze_single_pair(
                    pair_id=pair["id"],
                    longform=longform,
                    clip=clip,
                    expected_pattern=pair.get("pattern", "unknown")
                )
                
                if pattern:
                    all_patterns.append(pattern)
        
        composition_patterns = {
            "patterns": all_patterns,
            "source": "restructure_analyses" if existing_analyses else "pairs_config.json",
            "pairs_analyzed": len(all_patterns),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Save
        with open(self.composition_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(composition_patterns, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {self.composition_patterns_file.name}")
        
        return composition_patterns
    
    async def _analyze_single_pair(
        self,
        pair_id: str,
        longform: Dict,
        clip: Dict,
        expected_pattern: str
    ) -> Optional[Dict]:
        """
        Analysiere ein einzelnes Longform→Clip Paar.
        
        Returns:
            Dict mit composition_principles oder None
        """
        from models.base import get_model
        
        model = get_model("anthropic", tier="sonnet")
        
        longform_text = longform.get("text", "")[:2000]  # Truncate
        clip_text = clip.get("text", "")
        clip_hook = clip.get("segments", [{}])[0].get("text", "")[:200]
        
        prompt = f"""Analysiere diese Longform→Clip Transformation und extrahiere PRINZIPIEN:

LONGFORM (Ausschnitt):
{longform_text}

VIRAL CLIP:
Hook: {clip_hook}
Volltext: {clip_text[:1000]}

Erwartetes Pattern: {expected_pattern}

WICHTIG: Extrahiere PRINZIPIEN, nicht Regeln!

❌ KEINE Regeln wie:
- "Hook muss immer vom Ende kommen"
- "Clip muss immer 60 Sekunden sein"
- "Muss immer Segment X vor Segment Y"

✅ STATTDESSEN Prinzipien wie:
- "Wenn der Payoff stärker ist als der native Hook, ziehe den Payoff nach vorne"
- "Clips sollten so lang sein wie nötig, um die Story zu erzählen"
- "Segment-Reihenfolge sollte der emotionalen Journey folgen"

Extrahiere:
1. Hook-Transformations-Prinzip: WARUM wurde der Hook so transformiert? (Nicht: Was wurde gemacht)
2. Cutting-Prinzipien: Welche übergeordneten Prinzipien stecken hinter den Cuts? (Nicht: Welche Wörter wurden entfernt)
3. Erfolgs-Prinzipien: WARUM funktioniert diese Transformation? (Nicht: Was ist das Ergebnis)

Antworte als JSON:
{{
    "transformation_type": "hook_extraction|clean_extraction|cross_moment",
    "hook_origin": "native|extracted|cross_moment",
    "cutting_principles": [
        {{
            "principle": "Übergeordnetes Prinzip (z.B. 'Jedes Wort muss einen Grund haben')",
            "why": "Warum funktioniert dieses Prinzip?",
            "application": "Wie kann man es flexibel anwenden?"
        }}
    ],
    "success_principles": [
        {{
            "principle": "Prinzip das den Erfolg erklärt",
            "why": "Warum funktioniert es?",
            "application": "Wie anwenden?"
        }}
    ],
    "composition_principles": {{
        "hook_strategy": "Prinzip-basierte Hook-Strategie (nicht Regel!)",
        "pacing": "Prinzip-basiertes Pacing (nicht feste Sekunden!)",
        "structure": "Prinzip-basierte Struktur (nicht Template!)"
    }}
}}"""
        
        try:
            response = await model.generate(
                prompt=prompt,
                system="Du bist ein Expert für Video-Content-Transformation. Analysiere wie Longform zu viralen Clips transformiert wird.",
                temperature=0.3
            )
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                analysis = json.loads(json_match.group())
                return {
                    "source": f"pair_{pair_id}",
                    "principles": analysis.get("composition_principles", {})
                }
        except Exception as e:
            print(f"   ⚠️ Fehler bei Analyse von {pair_id}: {e}")
        
        return None
    
    async def _synthesize_principles(
        self, 
        isolated: Dict, 
        composition: Dict
    ) -> Dict:
        """
        Code 3: Synthetisiert beide Pattern-Typen zu Master Principles.
        """
        # Load current principles as base
        current_principles = {}
        if self.principles_file.exists():
            with open(self.principles_file) as f:
                current_principles = json.load(f)
        
        from models.base import get_model
        model = get_model("anthropic", tier="sonnet")
        
        synthesis_prompt = f"""
Du hast zwei Datenquellen für virale Content-PRINZIPIEN:

1. ISOLATED PRINCIPLES (aus {isolated.get('clips_analyzed', 0)} erfolgreichen Clips):
{json.dumps(isolated.get('hook_principles', isolated.get('hook_patterns', []))[:5], indent=2, ensure_ascii=False)}

2. COMPOSITION PRINCIPLES (aus {composition.get('pairs_analyzed', 0)} Longform→Clip Transformationen):
{json.dumps([p.get('principles', {}) for p in composition.get('patterns', [])[:3]], indent=2, ensure_ascii=False)}

3. AKTUELLE PRINCIPLES (Basis):
{json.dumps({k: v for k, v in current_principles.items() if k.startswith('hook_') or k.startswith('cutting_')}, indent=2, ensure_ascii=False)}

TASK:
Synthetisiere diese zu MASTER PRINCIPLES die beide Perspektiven vereinen.

WICHTIG: 
- Extrahiere PRINZIPIEN, nicht Regeln!
- Prinzipien erklären WARUM etwas funktioniert, nicht WAS es ist
- Prinzipien sind flexibel und kontextabhängig anwendbar
- Keine starren Regeln wie "muss immer X enthalten" oder "muss genau Y Sekunden sein"

MASTER PRINCIPLE (immer beibehalten):
"Make a video so good that people cannot physically scroll past"

Antworte als JSON mit:
- hook_principles (merged, prinzipienbasiert)
- transformation_principles (merged, prinzipienbasiert)  
- cutting_principles (merged, prinzipienbasiert)
- synthesis_insights (neue Prinzipien-Erkenntnisse)

Jedes Prinzip sollte haben:
- "principle": "Das übergeordnete Prinzip"
- "why": "Warum funktioniert es?"
- "application": "Wie kann man es flexibel anwenden?"
"""

        response = await model.generate(
            prompt=synthesis_prompt,
            system="""Du bist ein Prinzipien-Synthesizer. 

WICHTIG: Du synthetisierst PRINZIPIEN, nicht Regeln!

Prinzipien:
- Erklären WARUM etwas funktioniert
- Sind flexibel und kontextabhängig anwendbar
- Können auf verschiedene Situationen angewendet werden

Regeln (NICHT extrahieren!):
- Starre Vorschriften ("muss immer X")
- Feste Templates ("immer Y Sekunden")
- Kontext-unabhängige Formeln

Kombiniere die Inputs zu übergeordneten Master Principles.""",
            temperature=0.3
        )
        
        # Parse response
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            synthesized = json.loads(json_match.group()) if json_match else {}
        except:
            synthesized = {}
        
        # Merge with current principles
        updated_principles = current_principles.copy()
        
        # Update with synthesized patterns
        if synthesized.get("hook_patterns"):
            updated_principles["hook_patterns"] = synthesized["hook_patterns"]
        if synthesized.get("transformation_patterns"):
            updated_principles["transformation_patterns"] = synthesized["transformation_patterns"]
        if synthesized.get("cutting_principles"):
            updated_principles["cutting_principles"] = synthesized["cutting_principles"]
        if synthesized.get("synthesis_insights"):
            updated_principles["synthesis_insights"] = synthesized["synthesis_insights"]
        
        # Update metadata
        updated_principles["version"] = "2.1"
        updated_principles["last_updated"] = datetime.now().isoformat()
        updated_principles["data_sources"] = {
            "isolated_clips": isolated.get("clips_analyzed", 0),
            "transformations": composition.get("pairs_analyzed", 0)
        }
        
        # Save
        with open(self.principles_file, 'w', encoding='utf-8') as f:
            json.dump(updated_principles, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {self.principles_file.name}")
        
        return updated_principles


async def run_analysis():
    """Run full BRAIN analysis."""
    analyzer = BrainAnalyzer()
    return await analyzer.run_full_analysis()


if __name__ == "__main__":
    asyncio.run(run_analysis())

