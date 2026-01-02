"""
BRAIN Analysis Phase

Phase 1 des Systems: Lernen aus existierenden Daten

Code 1: Analysiert isolierte virale Clips → Extrahiert Patterns
Code 2: Analysiert Longform→Clip Paare → Extrahiert Composition Patterns
Code 3: Führt beide zusammen → Erstellt PRINCIPLES.json

Wird einmalig initial und dann wöchentlich ausgeführt.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from models.base import ClaudeModel


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
        
        # Sample for analysis (max 50 to save costs)
        sample = high_performers[:50]
        
        # Build analysis prompt
        clips_text = ""
        for i, clip in enumerate(sample[:20], 1):
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
            prompt=f"""Analysiere diese Top-Performer Clips und extrahiere PATTERNS:

{clips_text}

Extrahiere:
1. Hook-Patterns: Was haben die erfolgreichsten Hooks gemeinsam?
2. Content-Typen: Welche Arten von Content performen am besten?
3. Strukturelle Muster: Wie sind die Clips aufgebaut?

Antworte als JSON:
{{
  "hook_patterns": [
    {{"type": "...", "frequency": "X%", "example": "...", "why_works": "..."}}
  ],
  "content_types": [
    {{"type": "...", "avg_completion": 0.XX, "characteristics": ["..."]}}
  ],
  "structural_patterns": [
    {{"pattern": "...", "description": "..."}}
  ]
}}""",
            system="Du bist ein Viral Content Analyst. Extrahiere Patterns aus erfolgreichen Clips.",
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
        """
        # Load existing restructure analyses
        existing_analyses = list(self.learnings_dir.glob("restructure_analysis_*.json"))
        
        if not existing_analyses:
            print("   ⚠️ Keine Restructure-Analysen gefunden")
            return {"patterns": [], "source": "none"}
        
        print(f"   Gefunden: {len(existing_analyses)} Pair-Analysen")
        
        # Collect patterns from existing analyses
        all_patterns = []
        for analysis_file in existing_analyses:
            try:
                with open(analysis_file) as f:
                    analysis = json.load(f)
                
                if "composition_principles" in analysis:
                    all_patterns.append({
                        "source": analysis_file.name,
                        "principles": analysis["composition_principles"]
                    })
            except:
                continue
        
        composition_patterns = {
            "patterns": all_patterns,
            "source": "restructure_analyses",
            "pairs_analyzed": len(all_patterns),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Save
        with open(self.composition_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(composition_patterns, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {self.composition_patterns_file.name}")
        
        return composition_patterns
    
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
        
        model = ClaudeModel("claude-sonnet-4-5-20250929")
        
        synthesis_prompt = f"""
Du hast zwei Datenquellen für virale Content-Patterns:

1. ISOLATED PATTERNS (aus {isolated.get('clips_analyzed', 0)} erfolgreichen Clips):
{json.dumps(isolated.get('hook_patterns', [])[:5], indent=2, ensure_ascii=False)}

2. COMPOSITION PATTERNS (aus {composition.get('pairs_analyzed', 0)} Longform→Clip Transformationen):
{json.dumps([p.get('principles', {}) for p in composition.get('patterns', [])[:3]], indent=2, ensure_ascii=False)}

3. AKTUELLE PRINCIPLES (Basis):
{json.dumps({k: v for k, v in current_principles.items() if k.startswith('hook_') or k.startswith('cutting_')}, indent=2, ensure_ascii=False)}

TASK:
Synthetisiere diese zu MASTER PRINCIPLES die beide Perspektiven vereinen:
- WAS macht einen Clip viral (aus Isolated Analysis)
- WIE transformiert man Longform zu viral (aus Pair Analysis)

WICHTIG: Behalte das MASTER PRINCIPLE bei:
"Make a video so good that people cannot physically scroll past"

Antworte als JSON mit:
- hook_patterns (merged)
- transformation_patterns (merged)  
- cutting_principles (merged)
- synthesis_insights (neue Erkenntnisse)
"""

        response = await model.generate(
            prompt=synthesis_prompt,
            system="Du bist ein Pattern-Synthesizer. Kombiniere Patterns zu Master Principles.",
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

