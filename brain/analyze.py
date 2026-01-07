"""
BRAIN Analysis Phase V2 - Rein Prinzipienbasiert

Phase 1 des Systems: Lernen aus existierenden Daten

WICHTIG: Extrahiert NUR Prinzipien (WARUM), keine Regeln (WAS).

Code 1: Analysiert isolierte virale Clips → Extrahiert Prinzipien + Frequenzen
Code 2: Analysiert Longform→Clip Paare → Extrahiert Transformations-Prinzipien
Code 3: Führt beide zusammen → Erstellt hierarchische BRAIN_PRINCIPLES.json
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter

from models.base import get_model


class BrainAnalyzer:
    """
    Analysiert Trainingsdaten und erstellt hierarchische BRAIN_PRINCIPLES.json
    
    KERNPRINZIP: Extrahiere WARUM etwas funktioniert, nicht WAS es enthält.
    
    Keine spezifischen Beispiele aus Transkripten!
    Keine starren Regeln wie "muss X Sekunden sein"!
    Nur transferierbare Prinzipien!
    """
    
    def __init__(self):
        self.brain_dir = Path(__file__).parent
        self.data_dir = Path(__file__).parent.parent / "data"
        self.training_dir = self.data_dir / "training"
        self.learnings_dir = self.data_dir / "learnings"
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        
        # Output files
        self.isolated_analysis_file = self.learnings_dir / "isolated_analysis.json"
        self.pairs_analysis_file = self.learnings_dir / "pairs_analysis.json"
        self.principles_file = self.brain_dir / "BRAIN_PRINCIPLES.json"
    
    # =========================================================================
    # SYSTEM PROMPT für alle Analysen
    # =========================================================================
    
    PRINCIPLE_EXTRACTION_SYSTEM = """Du bist ein Prinzipien-Extraktor für virale Content-Analyse.

DEINE AUFGABE: Extrahiere das WARUM, nicht das WAS.

❌ VERBOTEN - Starre Regeln:
- "Hook muss in 0-3 Sekunden sein"
- "Clip sollte 45-60 Sekunden dauern"
- "Immer mit Paradox starten"
- Spezifische Beispiele aus den Transkripten zitieren

✅ ERLAUBT - Flexible Prinzipien:
- "Kognitive Dissonanz zwingt das Gehirn zur Aufmerksamkeit" (WARUM)
- "Offene Loops aktivieren den Zeigarnik-Effekt" (WARUM)
- "Emotionale Eskalation hält die Watchtime hoch" (WARUM)

PRINZIP-FORMAT:
Jedes Prinzip MUSS diese Struktur haben:
{
    "principle": "Name des Prinzips",
    "why_works": "Warum funktioniert es psychologisch/neurologisch?",
    "when_to_apply": "In welchen Situationen ist es anwendbar?",
    "how_to_recognize": "Woran erkenne ich, dass ich es anwenden sollte?"
}

KEINE:
- Festen Zeitangaben (statt "3 Sekunden" → "so schnell wie möglich")
- Spezifischen Texte aus Videos (keine Zitate!)
- Template-Strukturen (statt "Hook→Story→Payoff" → "Spannung aufbauen und auflösen")

Du antwortest NUR mit validem JSON."""
    
    # =========================================================================
    # HAUPTANALYSE
    # =========================================================================
    
    async def run_full_analysis(self) -> Dict:
        """
        Führt komplette prinzipienbasierte Analyse-Pipeline aus.
        """
        print("\n" + "="*70)
        print("🧠 BRAIN ANALYSIS V2 - Prinzipienbasiert")
        print("="*70)
        print("   Ziel: Extrahiere WARUM Dinge funktionieren, nicht WAS sie sind")
        print("   Keine spezifischen Beispiele, nur transferierbare Prinzipien!")
        print("="*70)
        
        # Code 1: Isolierte Clips → Prinzipien + Frequenzen
        print("\n📊 PHASE 1: Analysiere isolierte virale Clips...")
        isolated_analysis = await self._analyze_isolated_clips_v2()
        
        # Code 2: Paare → Transformations-Prinzipien
        print("\n🔄 PHASE 2: Analysiere Longform→Clip Transformationen...")
        pairs_analysis = await self._analyze_pairs_v2()
        
        # Code 3: Zusammenführen → Hierarchische Prinzipien
        print("\n🎯 PHASE 3: Synthetisiere Master-Prinzipien...")
        master_principles = await self._synthesize_master_principles(
            isolated_analysis, 
            pairs_analysis
        )
        
        print("\n" + "="*70)
        print("✅ ANALYSE ABGESCHLOSSEN")
        print("="*70)
        print(f"   📁 Output: {self.principles_file}")
        print(f"   📊 Clips analysiert: {isolated_analysis.get('total_clips', 0)}")
        print(f"   🔄 Paare analysiert: {pairs_analysis.get('total_pairs', 0)}")
        
        return {
            "isolated_analysis": isolated_analysis,
            "pairs_analysis": pairs_analysis,
            "master_principles": master_principles
        }
    
    # =========================================================================
    # CODE 1: Isolierte Clips analysieren
    # =========================================================================
    
    async def _analyze_isolated_clips_v2(self) -> Dict:
        """
        Analysiert alle isolierten viralen Clips.
        
        Extrahiert:
        1. Hook-Prinzipien (WARUM funktionieren diese Hooks?)
        2. Content-Prinzipien (WARUM ist dieser Content viral?)
        3. Struktur-Prinzipien (WARUM funktioniert diese Struktur?)
        4. Frequenzen (Wie oft kommt jedes Prinzip vor?)
        """
        goat_file = self.training_dir / "goat_training_data.json"
        
        if not goat_file.exists():
            print("   ⚠️ goat_training_data.json nicht gefunden")
            return {"error": "no_data", "total_clips": 0}
        
        with open(goat_file) as f:
            all_clips = json.load(f)
        
        # Filter clips with transcripts
        clips_with_transcripts = [
            c for c in all_clips
            if c.get("transcript", {}).get("text")
        ]
        
        total_clips = len(clips_with_transcripts)
        print(f"   📊 Total Clips: {total_clips}")
        
        if not clips_with_transcripts:
            return {"error": "no_transcripts", "total_clips": 0}
        
        # Sort by views (highest first)
        clips_with_transcripts.sort(
            key=lambda c: c.get("performance", {}).get("views", 0),
            reverse=True
        )
        
        # Batch configuration
        batch_size = int(os.getenv("BRAIN_BATCH_SIZE", "25"))
        max_batches = int(os.getenv("BRAIN_MAX_BATCHES", "40"))  # 40 * 25 = 1000 clips
        
        num_batches = min((total_clips + batch_size - 1) // batch_size, max_batches)
        clips_to_analyze = min(total_clips, num_batches * batch_size)
        
        print(f"   🔄 Analysiere {clips_to_analyze} Clips in {num_batches} Batches")
        print(f"   💰 Geschätzte Kosten: ~${num_batches * 0.30:.2f} (Opus)")
        
        # Collect all principle occurrences for frequency counting
        all_hook_principles = []
        all_content_principles = []
        all_structure_principles = []
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_clips)
            batch_clips = clips_with_transcripts[start_idx:end_idx]
            
            if not batch_clips:
                break
            
            print(f"   📊 Batch {batch_idx + 1}/{num_batches}: Clips {start_idx + 1}-{end_idx}")
            
            result = await self._analyze_isolated_batch(batch_clips, batch_idx + 1)
            
            if result:
                all_hook_principles.extend(result.get("hook_principles", []))
                all_content_principles.extend(result.get("content_principles", []))
                all_structure_principles.extend(result.get("structure_principles", []))
        
        # Calculate frequencies
        print(f"   🔢 Berechne Frequenzen...")
        
        hook_freq = self._calculate_frequencies(all_hook_principles)
        content_freq = self._calculate_frequencies(all_content_principles)
        structure_freq = self._calculate_frequencies(all_structure_principles)
        
        # Deduplicate and create final list
        hook_principles = self._deduplicate_principles(all_hook_principles, hook_freq)
        content_principles = self._deduplicate_principles(all_content_principles, content_freq)
        structure_principles = self._deduplicate_principles(all_structure_principles, structure_freq)
        
        analysis = {
            "total_clips": clips_to_analyze,
            "batches_processed": num_batches,
            "analyzed_at": datetime.now().isoformat(),
            "hook_principles": hook_principles,
            "content_principles": content_principles,
            "structure_principles": structure_principles
        }
        
        # Save
        with open(self.isolated_analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {self.isolated_analysis_file.name}")
        print(f"      Hook-Prinzipien: {len(hook_principles)}")
        print(f"      Content-Prinzipien: {len(content_principles)}")
        print(f"      Struktur-Prinzipien: {len(structure_principles)}")
        
        return analysis
    
    async def _analyze_isolated_batch(self, clips: List[Dict], batch_num: int) -> Optional[Dict]:
        """
        Analysiere einen Batch von Clips und extrahiere Prinzipien.
        """
        import re
        
        # Build clips summary (NO specific text from transcripts!)
        clips_summary = ""
        for i, clip in enumerate(clips, 1):
            perf = clip.get("performance", {})
            transcript = clip.get("transcript", {})
            text = transcript.get("text", "")
            
            # Extract characteristics, NOT the actual text
            word_count = len(text.split())
            has_question = "?" in text[:200]
            has_numbers = any(c.isdigit() for c in text[:200])
            starts_with_command = text.strip().lower().startswith(("hör", "mach", "nimm", "schau", "denk", "vergiss", "stell", "arbeite"))
            has_contrast = any(word in text.lower()[:300] for word in ["aber", "jedoch", "obwohl", "nicht", "niemals", "statt"])
            
            clips_summary += f"""
Clip {i} (Views: {perf.get('views', 0):,}, Completion: {perf.get('completion_rate', 0):.0%}):
- Wörter: {word_count}
- Startet mit Frage: {has_question}
- Enthält Zahlen: {has_numbers}
- Startet mit Imperativ: {starts_with_command}
- Enthält Kontrast/Negation: {has_contrast}
- Hook-Typ (geschätzt): {self._guess_hook_type(text[:200])}
"""
        
        prompt = f"""Analysiere diese {len(clips)} viralen Clips und extrahiere PRINZIPIEN.

CLIP-CHARAKTERISTIKEN (keine Texte!):
{clips_summary}

EXTRAHIERE FÜR JEDEN CLIP:
1. Hook-Prinzip: WARUM funktioniert der Hook? (Nicht: Was steht drin)
2. Content-Prinzip: WARUM ist der Inhalt viral? (Nicht: Was ist der Inhalt)
3. Struktur-Prinzip: WARUM funktioniert die Struktur? (Nicht: Wie ist sie aufgebaut)

WICHTIG:
- Keine spezifischen Texte zitieren!
- Keine festen Zeitangaben!
- Nur psychologische/neurologische WARUM-Erklärungen!

JSON-Antwort:
{{
    "hook_principles": [
        {{
            "principle": "Kognitive Dissonanz",
            "why_works": "Das Gehirn kann Widersprüche nicht ignorieren - evolutionär überlebenswichtig",
            "when_to_apply": "Wenn der Content eine kontraintuitive Wahrheit enthält",
            "how_to_recognize": "Speaker widerspricht gängiger Meinung oder stellt Paradox auf"
        }}
    ],
    "content_principles": [...],
    "structure_principles": [...]
}}"""

        model = get_model("anthropic", tier="opus")
        
        try:
            response = await model.generate(
                prompt=prompt,
                system=self.PRINCIPLE_EXTRACTION_SYSTEM,
                temperature=0.3,
                cache_system=True
            )
            
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                return json.loads(json_match.group())
            else:
                print(f"      ⚠️ Batch {batch_num}: Kein JSON gefunden")
                return None
                
        except Exception as e:
            print(f"      ⚠️ Batch {batch_num}: Fehler - {e}")
            return None
    
    def _guess_hook_type(self, hook_text: str) -> str:
        """Schätze den Hook-Typ basierend auf Charakteristiken (nicht Text!)."""
        text = hook_text.lower()
        
        if "?" in text:
            return "question"
        elif any(word in text for word in ["nicht", "niemals", "nie", "hört auf", "stop"]):
            return "contrarian"
        elif any(word in text for word in ["wie", "ist wie", "genauso wie"]):
            return "metaphor"
        elif any(c.isdigit() for c in text):
            return "statistic"
        elif any(word in text for word in ["gestern", "heute", "letzte woche", "als ich"]):
            return "story"
        elif text.strip()[:4] in ["hör ", "mach", "nimm", "schau", "denk"]:
            return "imperative"
        else:
            return "statement"
    
    def _calculate_frequencies(self, principles: List[Dict]) -> Dict[str, int]:
        """Berechne wie oft jedes Prinzip vorkommt."""
        counter = Counter()
        for p in principles:
            name = p.get("principle", "unknown")
            # Normalize name
            name = name.lower().strip()
            counter[name] += 1
        return dict(counter)
    
    def _deduplicate_principles(self, principles: List[Dict], frequencies: Dict[str, int]) -> List[Dict]:
        """Dedupliziere Prinzipien und füge Frequenzen hinzu."""
        seen = {}
        
        for p in principles:
            name = p.get("principle", "").lower().strip()
            if name not in seen:
                # Add frequency
                total = sum(frequencies.values())
                freq = frequencies.get(name, 1)
                p["frequency"] = f"{(freq / total * 100):.0f}%" if total > 0 else "N/A"
                p["occurrences"] = freq
                seen[name] = p
        
        # Sort by occurrences
        result = list(seen.values())
        result.sort(key=lambda x: x.get("occurrences", 0), reverse=True)
        
        return result[:15]  # Top 15 pro Kategorie
    
    # =========================================================================
    # CODE 2: Paare analysieren
    # =========================================================================
    
    async def _analyze_pairs_v2(self) -> Dict:
        """
        Analysiert Longform→Clip Paare für Transformations-Prinzipien.
        
        Extrahiert:
        1. Warum wurde der Hook gewählt? (Nicht: Welcher Text)
        2. Warum wurde umstrukturiert? (Nicht: Welche Segmente)
        3. Was macht die Transformation viral? (Prinzip, nicht Beispiel)
        """
        pairs_config = self.training_dir / "pairs_config.json"
        transcripts_dir = self.data_dir / "cache" / "transcripts"
        
        if not pairs_config.exists():
            print("   ⚠️ pairs_config.json nicht gefunden")
            return {"error": "no_config", "total_pairs": 0}
        
        with open(pairs_config) as f:
            config = json.load(f)
        
        pairs = config.get("pairs", [])
        print(f"   📋 Gefunden: {len(pairs)} Paare")
        
        all_transformation_principles = []
        
        for pair in pairs:
            longform_file = transcripts_dir / pair["longform"]
            clip_file = transcripts_dir / pair["clip"]
            
            if not longform_file.exists():
                print(f"   ⚠️ Longform nicht gefunden: {pair['longform']}")
                continue
            if not clip_file.exists():
                print(f"   ⚠️ Clip nicht gefunden: {pair['clip']}")
                continue
            
            with open(longform_file) as f:
                longform = json.load(f)
            with open(clip_file) as f:
                clip = json.load(f)
            
            print(f"   🔄 Analysiere: {pair['id']}")
            
            result = await self._analyze_pair_transformation(
                pair_id=pair["id"],
                longform=longform,
                clip=clip,
                pattern_hint=pair.get("pattern", "unknown")
            )
            
            if result:
                all_transformation_principles.append(result)
        
        # Synthesize transformation principles
        print(f"   🔄 Synthetisiere {len(all_transformation_principles)} Transformations-Analysen...")
        
        synthesis = await self._synthesize_transformation_principles(all_transformation_principles)
        
        analysis = {
            "total_pairs": len(all_transformation_principles),
            "analyzed_at": datetime.now().isoformat(),
            "individual_analyses": all_transformation_principles,
            "synthesized_principles": synthesis
        }
        
        # Save
        with open(self.pairs_analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Gespeichert: {self.pairs_analysis_file.name}")
        
        return analysis
    
    async def _analyze_pair_transformation(
        self,
        pair_id: str,
        longform: Dict,
        clip: Dict,
        pattern_hint: str
    ) -> Optional[Dict]:
        """
        Analysiere eine einzelne Longform→Clip Transformation.
        
        WICHTIG: Extrahiere Prinzipien, NICHT spezifische Texte oder Segmente!
        """
        import re
        
        # Extract characteristics, NOT content
        longform_segments = longform.get("segments", [])
        clip_segments = clip.get("segments", [])
        
        longform_duration = longform_segments[-1].get("end", 0) if longform_segments else 0
        clip_duration = clip_segments[-1].get("end", 0) if clip_segments else 0
        compression_ratio = clip_duration / longform_duration if longform_duration > 0 else 0
        
        # Analyze structural changes (without revealing content)
        clip_text = clip.get("text", "")
        longform_text = longform.get("text", "")
        
        # Find where clip content appears in longform (rough position)
        clip_start_in_longform = longform_text.lower().find(clip_text[:100].lower()) if clip_text else -1
        hook_comes_from_later = clip_start_in_longform > len(longform_text) * 0.3 if clip_start_in_longform > 0 else False
        
        characteristics = {
            "longform_duration_minutes": longform_duration / 60,
            "clip_duration_seconds": clip_duration,
            "compression_ratio": compression_ratio,
            "hook_restructured": hook_comes_from_later,
            "pattern_hint": pattern_hint
        }
        
        prompt = f"""Analysiere diese Longform→Clip Transformation und extrahiere PRINZIPIEN.

TRANSFORMATION-CHARAKTERISTIKEN (keine Texte!):
- Longform Dauer: {characteristics['longform_duration_minutes']:.1f} Minuten
- Clip Dauer: {characteristics['clip_duration_seconds']:.0f} Sekunden
- Kompressionsrate: {characteristics['compression_ratio']:.1%}
- Hook wurde umstrukturiert: {characteristics['hook_restructured']}
- Pattern-Hinweis: {characteristics['pattern_hint']}

EXTRAHIERE:
1. HOOK-TRANSFORMATIONS-PRINZIP: WARUM wurde der Hook so gewählt/transformiert?
2. STRUKTUR-PRINZIP: WARUM funktioniert die neue Struktur besser als das Original?
3. WATCHTIME-PRINZIP: Was macht diese Transformation watchtime-optimal?

WICHTIG:
- Keine spezifischen Texte zitieren!
- Keine Template-Strukturen!
- Nur psychologische/neurologische WARUM-Erklärungen!

JSON-Antwort:
{{
    "pair_id": "{pair_id}",
    "hook_transformation_principle": {{
        "principle": "...",
        "why_works": "...",
        "when_to_apply": "...",
        "how_to_recognize": "..."
    }},
    "structure_principle": {{
        "principle": "...",
        "why_works": "...",
        "when_to_apply": "...",
        "how_to_recognize": "..."
    }},
    "watchtime_principle": {{
        "principle": "...",
        "why_works": "...",
        "when_to_apply": "...",
        "how_to_recognize": "..."
    }}
}}"""

        model = get_model("anthropic", tier="opus")
        
        try:
            response = await model.generate(
                prompt=prompt,
                system=self.PRINCIPLE_EXTRACTION_SYSTEM,
                temperature=0.3,
                cache_system=True
            )
            
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                return json.loads(json_match.group())
            else:
                print(f"      ⚠️ {pair_id}: Kein JSON gefunden")
                return None
                
        except Exception as e:
            print(f"      ⚠️ {pair_id}: Fehler - {e}")
            return None
    
    async def _synthesize_transformation_principles(
        self, 
        individual_analyses: List[Dict]
    ) -> Dict:
        """
        Synthetisiere individuelle Pair-Analysen zu Master-Transformations-Prinzipien.
        """
        import re
        
        if not individual_analyses:
            return {}
        
        # Collect all principles
        all_hook = [a.get("hook_transformation_principle", {}) for a in individual_analyses if a]
        all_structure = [a.get("structure_principle", {}) for a in individual_analyses if a]
        all_watchtime = [a.get("watchtime_principle", {}) for a in individual_analyses if a]
        
        prompt = f"""Synthetisiere diese {len(individual_analyses)} Transformations-Analysen zu Master-Prinzipien.

HOOK-TRANSFORMATIONS-PRINZIPIEN ({len(all_hook)}):
{json.dumps(all_hook, indent=2, ensure_ascii=False)}

STRUKTUR-PRINZIPIEN ({len(all_structure)}):
{json.dumps(all_structure, indent=2, ensure_ascii=False)}

WATCHTIME-PRINZIPIEN ({len(all_watchtime)}):
{json.dumps(all_watchtime, indent=2, ensure_ascii=False)}

AUFGABE:
1. Dedupliziere ähnliche Prinzipien
2. Extrahiere die übergeordneten MASTER-PRINZIPIEN
3. Behalte nur die wichtigsten 5 pro Kategorie

WICHTIG:
- Keine spezifischen Beispiele!
- Nur transferierbare Prinzipien!

JSON-Antwort:
{{
    "hook_transformation_principles": [
        {{
            "principle": "...",
            "why_works": "...",
            "when_to_apply": "...",
            "how_to_recognize": "...",
            "frequency": "X von Y Paaren"
        }}
    ],
    "structure_principles": [...],
    "watchtime_principles": [...]
}}"""

        model = get_model("anthropic", tier="opus")
        
        try:
            response = await model.generate(
                prompt=prompt,
                system=self.PRINCIPLE_EXTRACTION_SYSTEM,
                temperature=0.3,
                cache_system=True
            )
            
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
                
        except Exception as e:
            print(f"   ⚠️ Synthese-Fehler: {e}")
            return {}
    
    # =========================================================================
    # CODE 3: Master-Prinzipien synthetisieren
    # =========================================================================
    
    async def _synthesize_master_principles(
        self, 
        isolated_analysis: Dict, 
        pairs_analysis: Dict
    ) -> Dict:
        """
        Synthetisiert beide Analyse-Quellen zu hierarchischen Master-Prinzipien.
        """
        import re
        
        prompt = f"""Du hast zwei Datenquellen für virale Content-Prinzipien:

1. ISOLIERTE CLIPS ({isolated_analysis.get('total_clips', 0)} Clips):
Hook-Prinzipien:
{json.dumps(isolated_analysis.get('hook_principles', [])[:5], indent=2, ensure_ascii=False)}

Content-Prinzipien:
{json.dumps(isolated_analysis.get('content_principles', [])[:5], indent=2, ensure_ascii=False)}

Struktur-Prinzipien:
{json.dumps(isolated_analysis.get('structure_principles', [])[:5], indent=2, ensure_ascii=False)}

2. TRANSFORMATIONS-PAARE ({pairs_analysis.get('total_pairs', 0)} Paare):
{json.dumps(pairs_analysis.get('synthesized_principles', {}), indent=2, ensure_ascii=False)}

AUFGABE: Erstelle eine hierarchische Master-Prinzipien-Struktur.

Die Struktur soll so aufgebaut sein:
1. CORE_PRINCIPLES: Die 3-5 fundamentalsten Prinzipien die ALLES erklären
2. HOOK_PRINCIPLES: Prinzipien für Hook-Erstellung (aus beiden Quellen)
3. TRANSFORMATION_PRINCIPLES: Prinzipien für Longform→Clip Transformation
4. QUALITY_PRINCIPLES: Woran erkenne ich einen guten Clip?

WICHTIG:
- Keine spezifischen Beispiele!
- Keine festen Regeln (keine Zeitangaben, keine Templates)!
- Nur transferierbare WARUM-Erklärungen!

JSON-Antwort:
{{
    "version": "3.0",
    "master_principle": "Make a video so good that people cannot physically scroll past",
    "core_principles": [
        {{
            "principle": "...",
            "why_works": "...",
            "application": "..."
        }}
    ],
    "hook_principles": [...],
    "transformation_principles": [...],
    "quality_principles": [...]
}}"""

        model = get_model("anthropic", tier="opus")
        
        try:
            response = await model.generate(
                prompt=prompt,
                system=self.PRINCIPLE_EXTRACTION_SYSTEM,
                temperature=0.3,
                cache_system=True
            )
            
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                master = json.loads(json_match.group())
            else:
                master = {}
                
        except Exception as e:
            print(f"   ⚠️ Master-Synthese-Fehler: {e}")
            master = {}
        
        # Add metadata
        master["last_updated"] = datetime.now().isoformat()
        master["data_sources"] = {
            "isolated_clips": isolated_analysis.get("total_clips", 0),
            "transformation_pairs": pairs_analysis.get("total_pairs", 0)
        }
        
        # Save
        with open(self.principles_file, 'w', encoding='utf-8') as f:
            json.dump(master, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Master-Prinzipien gespeichert: {self.principles_file.name}")
        
        return master


async def run_analysis():
    """Run full BRAIN analysis."""
    analyzer = BrainAnalyzer()
    return await analyzer.run_full_analysis()


if __name__ == "__main__":
    asyncio.run(run_analysis())
