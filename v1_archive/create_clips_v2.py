#!/usr/bin/env python3
"""
🎬 WORKFLOW 2: CREATE CLIPS v2 (Multi-Step Process)

V2 Änderungen:
- Multi-Step Process statt Ein-Prompt
- Aggressive Moment-Finding (alle guten Momente, nicht nur "beste 4")
- Context-Reduktion pro Step
- Datengestütztes Scoring (später)

INPUT: Longform video (MP4)
OUTPUT:
  - Multiple watchtime-optimized clips (MP4)
  - Premiere Pro XML for each clip
  - Transcript with structure notes
  - Multiple versions per clip (different hooks/structures)
  - Virality/Watchtime scores
"""

import json
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None

# Import master learnings
try:
    from master_learnings import load_master_learnings, get_learnings_for_prompt
    LEARNINGS_AVAILABLE = True
except ImportError:
    LEARNINGS_AVAILABLE = False

# Optional ML
try:
    import pickle
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False

# Optional Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except:
    WHISPER_AVAILABLE = False


# =============================================================================
# KNOWLEDGE BASE
# =============================================================================

WATCHTIME_FRAMEWORK = """
## SOCIAL MEDIA ALGORITHMUS - DIE WAHRHEIT

### Grundlegendes Verständnis:
Der Algorithmus ist KEIN mysteriöses System - er ist ein reiner Performance-Vergleichsmechanismus.
Er hat nur EIN Ziel: Maximierung der Watchtime auf der Plattform.
Warum? Plattformen generieren 99% ihrer Einnahmen durch Werbeanzeigen.
Mehr Watchtime = mehr Ad-Impressions = mehr Umsatz.

### Das Multiplayer-Game Prinzip:
- Du kämpfst NICHT gegen den Algorithmus - er ist nur der Schiedsrichter
- Du kämpfst gegen ALLE anderen Videos in deiner Nische
- Der Algorithmus wählt einfach das Video mit den besten Metriken aus dem Pool
- Wenn dein Video nicht performt, ist es nicht "Shadowbanning" - es ist einfach schlechter als die Konkurrenz

### Der Testgruppen-Mechanismus:
1. Initial Test: Video wird kleiner Testgruppe gezeigt (User mit Interesse am Thema)
2. Performance-Vergleich: Metriken werden mit ALLEN anderen Videos zum Thema verglichen
3. Skalierung: Video mit höchster Watchtime/Engagement gewinnt und wird weiter ausgespielt

### Die einzige Metrik die zählt:
"Make a video so good that people cannot physically scroll past"

Optimiere ALLES auf:
1. Watch Time (absolute Priorität)
2. Completion Rate
3. Engagement (als Indikator für Interesse)
4. Session Duration (wie lange bleiben User NACH deinem Video)

### Die brutale Wahrheit:
Vergiss Trends, Hashtags, Posting-Zeiten - das ist alles sekundär.
Der Algorithmus wird IMMER das Video bevorzugen, das Menschen länger auf der Plattform hält.
Deine Videos müssen so gut sein, dass sie zur Cashcow der Plattform werden.

---

## WATCHTIME OPTIMIZATION FRAMEWORK

### Algorithmus-Realität:
- Algorithmus = Performance-Vergleich, nicht Feind
- EINZIGES Ziel: Watchtime maximieren (= mehr Ads = mehr Geld)
- Dein Video kämpft gegen ALLE anderen Videos
- Kein Shadowbanning - nur schlechtere Performance als Konkurrenz

### Die 12 Virality Triggers:
1. Mass Appeal - Spricht breite Masse an?
2. Humor - Lustig?
3. Berühmtheiten - Halo-Effekt?
4. Headline/Hook - Öffnet Loops? Erste 3 Sekunden?
5. Storytime - Spannende Geschichte?
6. Kontroverse - Meinungsverschiedenheiten?
7. Learning - Direkt anwendbar? Speichern?
8. Shareability - Weitersenden?
9. Einfachheit - Nach 1x schauen klar?
10. Primacy-Recency - Erster & letzter Eindruck?
11. Information Gap - Nach 1. Satz dranbleiben?
12. Trend - Aktuell? Im Trend?

### Clip-Struktur für MAX Watchtime:

**HOOK (0-3 Sekunden)** - KRITISCH!
- Muss SOFORT Spannung aufbauen
- Klare Value Proposition
- Visueller + verbaler Stop-Trigger
- Wenn User hier abspringen, kostest du die Plattform Geld
- KEIN "Hallo", KEIN Intro, direkt rein
- Stärkster Moment ZUERST

**LOOP (3-10 Sekunden)**
- Unvollständiger Loop öffnen (Gehirn will Abschluss)
- "Gleich zeige ich dir..."
- Versprechen was kommt

**CONTENT (mit Pattern Interrupts)**
- Jede Sekunde muss Grund liefern weiterzuschauen
- Keine Füller, keine Langeweile
- Alle 5-7 Sekunden: Mini-Payoff oder neuer Hook
- Ständige Teaser für kommende Information
- Emotionale Achterbahn statt Flatline

**PAYOFF (Ende)**
- Loop schließen
- Satisfying Conclusion
- Optional: Neuer Loop für nächstes Video

### Cialdini Principles:
- Reciprocity: Gib Wert zuerst
- Commitment: Kleine Zusagen
- Social Proof: Zahlen, Testimonials
- Authority: Expertise zeigen
- Liking: Authentisch, relatable
- Scarcity: FOMO erzeugen
"""


class CreateClipsV2:
    """
    Main class for creating watchtime-optimized clips (Multi-Step Process)
    """
    
    # Model Configuration
    AVAILABLE_MODELS = {
        'haiku': 'claude-haiku-4-20250514',
        'sonnet': 'claude-sonnet-4-5-20250929',
        'opus': 'claude-opus-4-20250514'
    }
    
    MODEL_COSTS = {
        'haiku': {'input': 0.80, 'output': 4.00},  # per 1M tokens
        'sonnet': {'input': 3.00, 'output': 15.00},
        'opus': {'input': 15.00, 'output': 75.00}
    }
    
    def __init__(self):
        # API
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if ANTHROPIC_AVAILABLE and self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None
        
        # Model Selection (defaults)
        self.default_model = 'sonnet'  # Default: Sonnet 4.5
        self.premium_model = 'opus'    # Premium: Opus 4.5 for critical tasks
        
        # Paths
        self.data_dir = Path("data")
        self.cache_dir = self.data_dir / "cache" / "transcripts"
        self.output_dir = Path("output/clips")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load learned patterns
        self.patterns = self._load_patterns()
        self.ml_model = self._load_ml_model()
        
        print("="*70)
        print("🎬 CREATE CLIPS v2 - Multi-Step Process")
        print("="*70)
        print(f"   🤖 AI: {'Connected' if self.client else 'Not available'}")
        print(f"   📚 Patterns: {'Loaded' if self.patterns else 'Not found - run analyze_and_learn.py first'}")
        print(f"   📈 ML Model: {'Loaded' if self.ml_model else 'Not found'}")
        print(f"   🧠 Master Learnings: {'Loaded' if LEARNINGS_AVAILABLE else 'Not available'}")
        print(f"   🤖 Default Model: {self.default_model.upper()}")
        print(f"   ⭐ Premium Model: {self.premium_model.upper()}")
    
    def set_model(self, model_name='sonnet', premium_model=None):
        """
        Set AI models for processing
        
        Args:
            model_name: 'haiku', 'sonnet', or 'opus'
            premium_model: Optional separate model for critical tasks
                          (Story Analysis, Restructuring)
        
        Examples:
            # All Sonnet (balanced)
            creator.set_model('sonnet')
            
            # All Opus (premium)
            creator.set_model('opus')
            
            # Mixed: Sonnet for critical, Haiku for simple
            creator.set_model('haiku', premium_model='sonnet')
            
            # Ultra Premium: Opus for critical, Sonnet for simple
            creator.set_model('sonnet', premium_model='opus')
        """
        
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model: {model_name}. Choose: {list(self.AVAILABLE_MODELS.keys())}")
        
        if premium_model and premium_model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Invalid premium model: {premium_model}. Choose: {list(self.AVAILABLE_MODELS.keys())}")
        
        self.default_model = model_name
        self.premium_model = premium_model or model_name
        
        print(f"\n{'='*70}")
        print("🤖 MODEL CONFIGURATION")
        print(f"{'='*70}")
        print(f"   Default Model: {self.default_model.upper()}")
        print(f"   Premium Model: {self.premium_model.upper()}")
        print(f"\n💰 Estimated costs per video:")
        
        # Calculate estimated costs (per 1M tokens)
        default_cost = self.MODEL_COSTS[self.default_model]
        premium_cost = self.MODEL_COSTS[self.premium_model]
        
        # Rough estimates (in tokens, converted to cost)
        # Story Analysis: ~50k input, ~8k output
        story_analysis = (50 * premium_cost['input'] + 8 * premium_cost['output']) / 1000
        # Find Moments: ~20k input, ~5k output
        find_moments = (20 * premium_cost['input'] + 5 * premium_cost['output']) / 1000
        # Restructure: ~50k input, ~30k output (per moment, estimate 5 moments)
        restructure = (50 * premium_cost['input'] + 30 * premium_cost['output']) / 1000 * 5
        # Variations: ~30k input, ~20k output (per clip, estimate 5 clips)
        variations = (30 * default_cost['input'] + 20 * default_cost['output']) / 1000 * 5
        
        total = story_analysis + find_moments + restructure + variations
        
        print(f"   Story Analysis: ${story_analysis:.2f} ({self.premium_model})")
        print(f"   Find Moments: ${find_moments:.2f} ({self.premium_model})")
        print(f"   Restructure (5 moments): ${restructure:.2f} ({self.premium_model})")
        print(f"   Variations (5 clips): ${variations:.2f} ({self.default_model})")
        print(f"   ─────────────────")
        print(f"   TOTAL: ~${total:.2f}")
        print(f"{'='*70}\n")
    
    def _get_model(self, task_type='default'):
        """
        Get appropriate model for task
        
        Args:
            task_type: 'default', 'premium', 'simple'
        
        Returns:
            model string
        """
        
        if task_type == 'premium':
            return self.AVAILABLE_MODELS[self.premium_model]
        elif task_type == 'simple':
            return self.AVAILABLE_MODELS[self.default_model]
        else:
            return self.AVAILABLE_MODELS[self.default_model]
    
    def _load_patterns(self):
        """Load learned patterns - prefers deep_learned_patterns.json"""
        
        # Prefer deep patterns (from Smart Sampling) over basic patterns
        deep_patterns_file = self.data_dir / "deep_learned_patterns.json"
        basic_patterns_file = self.data_dir / "learned_patterns.json"
        
        if deep_patterns_file.exists():
            print(f"   📚 Loading DEEP patterns (Smart Sampling)")
            with open(deep_patterns_file, 'r') as f:
                return json.load(f)
        elif basic_patterns_file.exists():
            print(f"   📚 Loading basic patterns")
            with open(basic_patterns_file, 'r') as f:
                return json.load(f)
        return None
    
    def _load_ml_model(self):
        """Load ML model"""
        if not ML_AVAILABLE:
            return None
        
        model_file = self.data_dir / "ml_model.pkl"
        if model_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"   ⚠️  Could not load ML model: {e}")
                return None
        return None
    
    # =========================================================================
    # TRANSCRIPT HANDLING
    # =========================================================================
    
    def find_transcript(self, video_path):
        """Auto-find cached transcript for video"""
        
        video_path = Path(video_path)
        video_name = video_path.stem.lower()
        
        print(f"\n🔍 Looking for cached transcript...")
        
        if not self.cache_dir.exists():
            print(f"   ❌ Cache directory not found")
            return None
        
        cache_files = list(self.cache_dir.glob("*.json"))
        
        # Strategy 1: Match by name
        for f in cache_files:
            if video_name in f.stem.lower():
                print(f"   ✅ Found: {f.name}")
                return f
        
        # Strategy 2: List available and let user choose
        if cache_files:
            print(f"\n   📦 Available transcripts ({len(cache_files)}):")
            for i, f in enumerate(cache_files[:15], 1):
                try:
                    with open(f, 'r') as fh:
                        data = json.load(fh)
                        preview = data.get('text', str(data))[:60]
                        print(f"      {i}. {f.name}")
                        print(f"         {preview}...")
                except:
                    print(f"      {i}. {f.name}")
            
            choice = input(f"\n   Select (1-{len(cache_files)}) or Enter to transcribe: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(cache_files):
                return cache_files[int(choice) - 1]
        
        return None
    
    def load_transcript(self, path):
        """Load transcript and return segments"""
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        if 'segments' in data:
            return data['segments']
        elif 'text' in data:
            # Create pseudo-segments
            text = data['text']
            words = text.split()
            segments = []
            chunk_size = 25
            
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i+chunk_size]
                segments.append({
                    'text': ' '.join(chunk),
                    'start': i / 2.5,
                    'end': (i + len(chunk)) / 2.5
                })
            
            return segments
        
        return [{'text': str(data), 'start': 0, 'end': 60}]
    
    def transcribe_video(self, video_path):
        """Transcribe with Whisper"""
        
        if not WHISPER_AVAILABLE:
            print("❌ Whisper not installed")
            return None
        
        print(f"\n🎤 Transcribing video...")
        
        model = whisper.load_model("base")
        result = model.transcribe(str(video_path), language='de', verbose=False)
        
        # Cache it
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / f"{Path(video_path).stem}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Cached: {cache_file}")
        
        return result['segments']
    
    # =========================================================================
    # MULTI-STEP CLIP EXTRACTION
    # =========================================================================
    
    def _get_focused_context(self, context_type="minimal"):
        """
        Get only relevant context for specific task
        
        Context Types:
        - "minimal": Nur Hook-Patterns für Moment-Finding
        - "hook_focused": Hook-Mastery für Restructuring
        - "scoring": Scoring-Weights für Bewertung
        """
        
        if not LEARNINGS_AVAILABLE:
            return ""
        
        master = load_master_learnings()
        
        if context_type == "minimal":
            # Nur Hook-Patterns für Moment-Finding
            hooks = master.get('hook_mastery', {}).get('winning_hook_types', [])[:3]
            hook_text = ""
            newline = "\n"
            for h in hooks:
                if isinstance(h, dict):
                    hook_text += f"• {h.get('type', 'Unknown')}: {h.get('template', '')}{newline}"
                else:
                    hook_text += f"• {h}{newline}"
            
            return f"""
WINNING HOOK PATTERNS (für Moment-Erkennung):
{hook_text or "Keine Hook-Patterns verfügbar"}
"""
        
        elif context_type == "hook_focused":
            # Hook-Mastery + Viral Examples für Restructuring
            hooks = master.get('hook_mastery', {}).get('winning_hook_types', [])[:5]
            formulas = master.get('hook_mastery', {}).get('hook_formulas', [])[:5]
            
            # Get viral examples for guidance
            viral_examples = master.get('viral_examples', [])[:3]  # Top 3 examples
            
            viral_examples_text = ""
            for ex in viral_examples:
                template_id = ex.get('template_id', 'unknown')
                strategy = ex.get('restructuring_strategy', 'unknown')
                hook_pattern = ex.get('hook_pattern', {})
                hook_type = hook_pattern.get('hook_type', 'unknown')
                viral_examples_text += f"""
- Template: {template_id}
  Strategy: {strategy}
  Hook Type: {hook_type}
  Success Rate: {ex.get('success_rate', 0):.0%}
"""
            
            return f"""
HOOK MASTERY:
WINNING HOOKS:
{json.dumps(hooks, indent=2, ensure_ascii=False)}

HOOK FORMELN:
{json.dumps(formulas, indent=2, ensure_ascii=False)}

VIRAL EXAMPLES (für Guidance):
{viral_examples_text or "Noch keine viral examples"}
"""
        
        elif context_type == "scoring":
            # Nur Scoring-Weights
            weights = master.get('scoring_weights', {})
            return f"""
SCORING WEIGHTS:
{json.dumps(weights, indent=2, ensure_ascii=False)}
"""
        
        return ""
    
    def _format_segments(self, segments, max_chars=20000):
        """
        Format segments for prompt - with smart truncation
        """
        full_text = ""
        char_count = 0
        
        newline = "\n"
        for seg in segments:
            seg_text = f"[{seg['start']:.1f}s-{seg['end']:.1f}s] {seg['text']}{newline}"
            
            if char_count + len(seg_text) > max_chars:
                # Add indicator that more content exists
                remaining = len(segments) - segments.index(seg)
                full_text += f"{newline}[... {remaining} weitere Segmente ...]{newline}"
                break
            
            full_text += seg_text
            char_count += len(seg_text)
        
        return full_text
    
    def _find_all_moments(self, segments):
        """
        STEP 1: Find ALL strong moments - Chunked processing für lange Videos
        
        UPDATED: Teilt lange Videos in 5-min Chunks für bessere Performance
        
        Returns:
            List of moment dicts with simplified format:
            {
                "id": int,
                "start": float,
                "end": float,
                "topic": str,
                "strength": "high/medium/low",
                "reason": str
            }
        """
        
        if not self.client:
            print("❌ No API key")
            return []
        
        print(f"\n{'='*70}")
        print("🔍 STEP 1: FINDING ALL STRONG MOMENTS")
        print(f"{'='*70}")
        
        # Calculate video duration
        total_duration = segments[-1]['end'] if segments else 0
        print(f"\n📊 Video Stats:")
        print(f"   Duration: {total_duration/60:.1f} minutes")
        print(f"   Segments: {len(segments)}")
        
        # For videos > 10 minutes: Chunk processing
        chunk_size = 300  # 5 minutes per chunk
        
        if total_duration > 600:  # > 10 minutes
            print(f"\n   📦 Long video detected - using chunked processing")
            print(f"   📦 Chunk size: {chunk_size/60:.1f} minutes")
            
            all_moments = []
            
            # Process in chunks
            chunk_start = 0
            chunk_num = 1
            
            while chunk_start < total_duration:
                chunk_end = min(chunk_start + chunk_size, total_duration)
                
                print(f"\n   🔍 Chunk {chunk_num}: {chunk_start/60:.1f}-{chunk_end/60:.1f} min")
                
                # Get segments for this chunk
                chunk_segments = [
                    s for s in segments 
                    if chunk_start <= s.get('start', 0) < chunk_end
                ]
                
                if not chunk_segments:
                    chunk_start = chunk_end
                    chunk_num += 1
                    continue
                
                # Find moments in this chunk
                chunk_moments = self._find_moments_in_chunk(
                    chunk_segments, 
                    chunk_start, 
                    chunk_end,
                    chunk_num
                )
                
                print(f"      ✅ Found {len(chunk_moments)} moments in chunk")
                all_moments.extend(chunk_moments)
                
                chunk_start = chunk_end
                chunk_num += 1
            
            # Print summary
            print(f"\n✅ Total moments found: {len(all_moments)}")
            
            # Count by strength
            strength_counts = {}
            for moment in all_moments:
                strength = moment.get('strength', 'unknown')
                strength_counts[strength] = strength_counts.get(strength, 0) + 1
            
            if strength_counts:
                print(f"   📊 By strength:")
                for strength, count in strength_counts.items():
                    print(f"      • {strength}: {count}")
            
            # Print sample moments
            if all_moments:
                print(f"\n🎯 Sample moments:")
                for moment in all_moments[:5]:
                    moment_id = moment.get('id', moment.get('moment_id', '?'))
                    topic = moment.get('topic', 'No topic')
                    reason = moment.get('reason', moment.get('why_strong', 'No reason'))
                    print(f"   • #{moment_id}: {moment['start']:.1f}s-{moment['end']:.1f}s ({moment.get('strength', '?')})")
                    print(f"     Topic: {topic}")
                    print(f"     {reason[:80]}...")
                
                if len(all_moments) > 5:
                    print(f"   ... und {len(all_moments) - 5} weitere")
            
            return all_moments
        
        else:
            # Short video: Process normally
            print(f"\n   ✅ Short video - processing in single pass")
            return self._find_moments_single_pass(segments)
    
    def _find_moments_in_chunk(self, chunk_segments, chunk_start, chunk_end, chunk_num):
        """
        Find moments in a single chunk (≤5 minutes)
        """
        
        # Format segments
        transcript_text = self._format_segments(
            chunk_segments, 
            max_chars=10000
        )
        
        prompt = f"""Du bist ein Content-Analyst für virale Short-Form Videos.

VIDEO CHUNK: {chunk_start/60:.1f} - {chunk_end/60:.1f} Minuten

TRANSCRIPT:
{transcript_text}

Finde ALLE starken Momente in diesem Abschnitt.

WICHTIG:
- Finde 3-8 Momente in diesem Chunk
- Sei aggressiv, nicht konservativ
- Jeder Moment der Potential hat
- Ein Moment ist "stark" wenn er:
  * Einen klaren Hook hat
  * Eine interessante Aussage/Story enthält
  * Emotionale Reaktion auslösen könnte
  * Lernen/Value bietet
  * Kontroverse/Meinung enthält

ANTWORTE in JSON:
{{
  "moments": [
    {{
      "id": 1,
      "start": 45.2,
      "end": 78.5,
      "topic": "Kontroverse Aussage über [Thema]",
      "strength": "high",
      "reason": "Klare kontroverse Aussage die Diskussion auslöst"
    }}
  ]
}}

WICHTIG:
- Start/End Zeiten müssen INNERHALB des Chunks sein ({chunk_start:.1f}s - {chunk_end:.1f}s)
- Finde 3-8 Momente pro Chunk
- Sei nicht zu selektiv
"""
        
        try:
            response = self.client.messages.create(
                model=self._get_model('premium'),
                max_tokens=5000,
                timeout=120.0,  # 2 min timeout per chunk
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                
                moments = result.get('moments', [])
                
                # Validate times are within chunk
                validated_moments = []
                for moment in moments:
                    start = moment.get('start', chunk_start)
                    end = moment.get('end', start + 30)
                    
                    # Ensure times are within chunk
                    if start < chunk_start:
                        start = chunk_start
                    if end > chunk_end:
                        end = chunk_end
                    if start >= end:
                        continue
                    
                    moment['start'] = start
                    moment['end'] = end
                    validated_moments.append(moment)
                
                return validated_moments
            
            else:
                print(f"      ⚠️ Could not parse AI response for chunk {chunk_num}")
                return []
        
        except Exception as e:
            print(f"      ⚠️ Error in chunk {chunk_num}: {e}")
            return []
    
    def _find_moments_single_pass(self, segments):
        """
        Original method for short videos (< 10 min)
        Process entire video in one pass
        """
        
        # Format transcript (smart truncation if too long)
        transcript_text = self._format_segments(segments, max_chars=20000)
        
        # KEIN Hook Context - AI kennt Hooks bereits aus MASTER_LEARNINGS
        # Context weiter reduziert für mehr Momente
        
        # AGGRESSIVE Prompt - find ALL moments, not just best ones
        prompt = f"""Du bist ein Content-Analyst für virale Short-Form Videos.

Deine Aufgabe: Finde ALLE starken Momente in diesem Video.

WICHTIG - Sei AGRESSIV, nicht konservativ:
- Wenn ein Moment auch nur POTENTIAL hat → nimm ihn mit
- Wir wollen 10-20+ Momente finden, nicht nur 4-5
- Besser zu viele als zu wenige - wir filtern später
- Ein Moment ist "stark" wenn er:
  * Einen klaren Hook hat (auch wenn er erst später kommt)
  * Eine interessante Aussage/Story enthält
  * Emotionale Reaktion auslösen könnte
  * Lernen/Value bietet
  * Kontroverse/Meinung enthält
  * Humor/Entertainment bietet

---

VIDEO TRANSCRIPT:
{transcript_text}

---

AUFGABE:

Durchsuche das GESAMTE Video und identifiziere ALLE Momente die Potenzial haben.

Für jeden Moment:
1. Bestimme Start- und Endzeitpunkt (30-90 Sekunden pro Moment)
2. Bewerte die Stärke (high/medium/low)
3. Kurze Beschreibung des Themas
4. 1-2 Sätze warum dieser Moment stark ist

Antworte EXAKT in diesem vereinfachten JSON-Format:

{{
    "moments": [
        {{
            "id": 1,
            "start": 45.2,
            "end": 78.5,
            "topic": "Kontroverse Aussage über [Thema]",
            "strength": "high",
            "reason": "Klare kontroverse Aussage die Diskussion auslöst"
        }},
        {{
            "id": 2,
            "start": 120.5,
            "end": 165.0,
            "topic": "Persönliche Story über [Ereignis]",
            "strength": "medium",
            "reason": "Gute Story aber etwas langsam im Aufbau"
        }}
    ],
    "total_found": 15
}}

WICHTIG:
- Finde MINDESTENS 10-15 Momente (bei langen Videos auch 20+)
- Sei nicht zu selektiv - wir wollen alle Optionen sehen
- Momente können sich überlappen (das ist OK)
- Fokus auf Vielfalt: verschiedene Themen
- Vereinfachtes Format = mehr Momente möglich
"""
        
        print("\n🧠 AI scanning video for ALL strong moments...")
        print("   📋 Strategy: Aggressive - find everything with potential")
        print("   📝 Format: Simplified (more moments possible)")
        
        try:
            response = self.client.messages.create(
                model=self._get_model('premium'),  # Premium task: Finding moments
                max_tokens=15000,  # MEHR statt WENIGER für viele Momente
                timeout=180.0,  # 3 min timeout for single pass
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                
                moments = result.get('moments', [])
                total_found = result.get('total_found', len(moments))
                
                print(f"\n✅ Found {len(moments)} moments!")
                print(f"   📊 Total found: {total_found}")
                
                # Count by strength
                strength_counts = {}
                for moment in moments:
                    strength = moment.get('strength', 'unknown')
                    strength_counts[strength] = strength_counts.get(strength, 0) + 1
                
                if strength_counts:
                    print(f"   📊 By strength:")
                    for strength, count in strength_counts.items():
                        print(f"      • {strength}: {count}")
                
                # Print first few moments
                print(f"\n🎯 Sample moments:")
                for moment in moments[:5]:
                    moment_id = moment.get('id', moment.get('moment_id', '?'))
                    topic = moment.get('topic', 'No topic')
                    reason = moment.get('reason', moment.get('why_strong', 'No reason'))
                    print(f"   • #{moment_id}: {moment['start']:.1f}s-{moment['end']:.1f}s ({moment.get('strength', '?')})")
                    print(f"     Topic: {topic}")
                    print(f"     {reason[:80]}...")
                
                if len(moments) > 5:
                    print(f"   ... und {len(moments) - 5} weitere")
                
                return moments
            
            else:
                print("❌ Could not parse AI response")
                return []
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def _get_moment_segments(self, moment, all_segments):
        """Extract segments for a specific moment"""
        moment_start = moment.get('start', 0)
        moment_end = moment.get('end', 0)
        
        moment_segments = []
        for seg in all_segments:
            seg_start = seg.get('start', 0)
            seg_end = seg.get('end', 0)
            
            # Check if segment overlaps with moment
            if seg_end >= moment_start and seg_start <= moment_end:
                moment_segments.append(seg)
        
        return moment_segments
    
    def _analyze_story_structure(self, segments):
        """
        SCHRITT 0: Verstehe die komplette Story-Struktur des Videos
        
        Diese Methode läuft EINMAL am Anfang und analysiert:
        1. Haupt-Narratives/Storylines
        2. Zusammenhängende Story-Blöcke
        3. Dependencies zwischen Segmenten
        4. Welche Teile MÜSSEN zusammenbleiben
        
        Returns:
            {
                "storylines": [
                    {
                        "storyline_id": "story_1",
                        "topic": "Vater-Sohn Konflikt",
                        "segments": [...],
                        "can_standalone": true,
                        "requires_context": false
                    }
                ],
                "standalone_moments": [...]
            }
        """
        
        if not self.client:
            print("\n⚠️  No API key - skipping story analysis")
            return {
                "storylines": [],
                "standalone_moments": []
            }
        
        print("\n" + "="*70)
        print("📖 ANALYZING STORY STRUCTURE")
        print("="*70)
        
        # Format komplettes Transcript (mehr Context für Story-Analyse)
        full_text = self._format_segments(segments, max_chars=50000)
        
        # Get Master Learnings for context
        story_context = ""
        if LEARNINGS_AVAILABLE:
            master = load_master_learnings()
            key_insights = master.get('key_insights', [])[:3]
            if key_insights:
                story_context = "\n".join([f"• {i}" for i in key_insights])
        
        prompt = f"""Du bist ein Story-Analyst für Video-Content.

AUFGABE: Analysiere die komplette Story-Struktur dieses Videos.

VIDEO TRANSCRIPT:
{full_text[:45000]}

"""
        newline = "\n"
        if story_context:
            prompt += f"KEY INSIGHTS (für Context):{newline}{story_context}"
        
        prompt += """

---

ANALYSIERE:

1. STORYLINES (zusammenhängende Narratives):
   - Welche Haupt-Stories gibt es?
   - Welche Segmente gehören zusammen?
   - Gibt es Dependencies? (Teil B braucht Teil A zum Verständnis)
   - Beispiel: "Upgrade Metapher" hat Setup (142s) und Application (270s) - beide gehören zusammen

2. STANDALONE MOMENTS:
   - Welche Momente sind selbsterklärend?
   - Welche können als Clip funktionieren OHNE Context?
   - Beispiel: "Kreative Demenz" Konzept ist komplett in einem Segment erklärt

3. DEPENDENCIES:
   - Welche Segmente MÜSSEN zusammenbleiben?
   - Was passiert wenn man sie trennt?
   - Markiere explizit: "requires_context: true" wenn Context nötig ist

REGELN:
- Sei konservativ: Wenn unsicher ob Dependency → markiere es als "requires_context: true"
- Story-Kohärenz ist WICHTIGER als Hook-Strength
- Lieber weniger Clips die Sinn machen, als viele die verwirren
- Ein Storyline kann mehrere Segmente haben (z.B. Setup → Payoff)

ANTWORTE EXAKT in diesem JSON Format:

{{
  "storylines": [
    {{
      "storyline_id": "story_1",
      "topic": "Vater-Sohn Konflikt",
      "segments": [
        {{
          "start": 388.9,
          "end": 523.7,
          "role": "setup_conflict_resolution",
          "dependencies": [],
          "key_elements": ["Mobbing", "Aussprache", "Heilung"]
        }}
      ],
      "can_standalone": true,
      "requires_context": false,
      "why_standalone": "Komplette Story in einem Block"
    }},
    {{
      "storyline_id": "story_2",
      "topic": "Upgrade Metapher",
      "segments": [
        {{
          "start": 142.5,
          "end": 200.3,
          "role": "metaphor_explanation",
          "dependencies": [],
          "key_elements": ["Business Class Story", "Upgrade Konzept"]
        }},
        {{
          "start": 270.4,
          "end": 330.9,
          "role": "metaphor_application",
          "dependencies": ["142.5-200.3"],
          "key_elements": ["Nicht entschuldigen", "Selbstwert"]
        }}
      ],
      "can_standalone": false,
      "requires_context": true,
      "why_requires_context": "Teil 2 braucht Teil 1 zum Verständnis"
    }}
  ],
  "standalone_moments": [
    {{
      "start": 20.9,
      "end": 52.1,
      "topic": "Kreative Demenz",
      "why_standalone": "Komplettes Konzept in einem Segment erklärt"
    }}
  ]
}}

WICHTIG:
- Segmente müssen mit start/end Zeiten aus dem Transcript sein
- Dependencies sind Array von Segment-Ranges (z.B. ["142.5-200.3"])
- can_standalone: true = kann als Clip funktionieren ohne andere Teile
- requires_context: true = braucht andere Segmente zum Verständnis
"""
        
        try:
            response = self.client.messages.create(
                model=self._get_model('premium'),  # Premium task: Story analysis
                max_tokens=8000,
                timeout=180.0,  # 3 min timeout
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                story_structure = json.loads(json_match.group())
                
                # Validate structure
                if 'storylines' not in story_structure:
                    story_structure['storylines'] = []
                if 'standalone_moments' not in story_structure:
                    story_structure['standalone_moments'] = []
                
                print(f"\n   ✅ Found {len(story_structure['storylines'])} storylines")
                print(f"   ✅ Found {len(story_structure['standalone_moments'])} standalone moments")
                
                # Show summary
                for storyline in story_structure['storylines'][:3]:
                    topic = storyline.get('topic', 'Unknown')
                    standalone = "✅ Standalone" if storyline.get('can_standalone') else "⚠️ Needs Context"
                    print(f"      • {topic}: {standalone}")
                
                return story_structure
            
            else:
                print("   ⚠️  Could not parse AI response")
                return {
                    "storylines": [],
                    "standalone_moments": []
                }
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "storylines": [],
                "standalone_moments": []
            }
    
    def _restructure_moment(self, moment, all_segments, story_structure=None):
        """
        STEP 2: Restructure einzelnen Moment für maximale Watch Time
        
        Args:
            moment: Dict von _find_all_moments() mit id, start, end, topic, strength, reason
            all_segments: Alle Transcript-Segmente (für Context)
            story_structure: Story-Struktur von _analyze_story_structure() (optional)
        
        Returns:
            Optimierter Clip mit structure, reasoning, etc.
        """
        
        if not self.client:
            print(f"   ⚠️  No API key for moment {moment.get('id', '?')}")
            return None
        
        moment_id = moment.get('id', moment.get('moment_id', 'unknown'))
        moment_start = moment.get('start', 0)
        moment_end = moment.get('end', 0)
        moment_duration = moment_end - moment_start
        
        print(f"\n   🔧 Restructuring moment #{moment_id} ({moment_start:.1f}s-{moment_end:.1f}s)")
        
        # Extract segments for this moment
        moment_segments = self._get_moment_segments(moment, all_segments)
        
        if not moment_segments:
            print(f"      ⚠️  No segments found for moment")
            return None
        
        # Format moment transcript
        moment_text = self._format_segments(moment_segments, max_chars=5000)
        
        # Get focused context (Hook-Mastery + Viral Examples)
        hook_context = self._get_focused_context("hook_focused")
        
        # Get Master Learnings for viral examples
        viral_examples_guidance = ""
        if LEARNINGS_AVAILABLE:
            master = load_master_learnings()
            viral_examples = master.get('viral_examples', [])[:3]
            
            if viral_examples:
                newline = "\n"
                viral_examples_guidance = f"{newline}{newline}ERFOLGREICHE BEISPIELE (nutze als Inspiration):{newline}"
                for ex in viral_examples:
                    hook_pattern = ex.get('hook_pattern', {})
                    structure_pattern = ex.get('structure_pattern', {})
                    template_id = ex.get('template_id', 'unknown')
                    hook_type = hook_pattern.get('hook_type', 'unknown')
                    hook_formula = hook_pattern.get('hook_formula', 'N/A')
                    structure_name = structure_pattern.get('structure_name', 'unknown')
                    success_rate = ex.get('success_rate', 0)
                    when_to_use = ', '.join(ex.get('when_to_use', [])[:2])
                    viral_examples_guidance += f"""{newline}- Template: {template_id}
  Hook Strategy: {hook_type} - {hook_formula}
  Structure: {structure_name}
  Success Rate: {success_rate:.0%}
  When to use: {when_to_use}
"""
        
        # Add Story Context if available
        story_context = ""
        if story_structure:
            # Check if moment is part of a storyline
            moment_start = moment.get('start', 0)
            moment_end = moment.get('end', 0)
            
            relevant_storylines = []
            for storyline in story_structure.get('storylines', []):
                for seg in storyline.get('segments', []):
                    seg_start = seg.get('start', 0)
                    seg_end = seg.get('end', 0)
                    if seg_end >= moment_start and seg_start <= moment_end:
                        relevant_storylines.append(storyline)
                        break
            
            if relevant_storylines:
                newline = "\n"
                story_context = f"{newline}{newline}STORY CONTEXT (WICHTIG für Kohärenz):{newline}"
                for sl in relevant_storylines:
                    topic = sl.get('topic', 'Unknown')
                    standalone = sl.get('can_standalone', False)
                    requires_context = sl.get('requires_context', False)
                    standalone_text = '✅ Ja' if standalone else '❌ Nein'
                    context_text = '⚠️ Ja' if requires_context else '✅ Nein'
                    important_text = 'Diese Story kann alleine funktionieren' if standalone else 'Diese Story braucht andere Teile - sei vorsichtig beim Restrukturieren!'
                    segments_count = len(sl.get('segments', []))
                    story_context += f"""{newline}- Storyline: {topic}
  Standalone: {standalone_text}
  Requires Context: {context_text}
  Segments: {segments_count}
  
  WICHTIG: {important_text}
"""
            
            # Check standalone moments
            newline = "\n"
            for standalone_moment in story_structure.get('standalone_moments', []):
                sm_start = standalone_moment.get('start', 0)
                sm_end = standalone_moment.get('end', 0)
                if sm_end >= moment_start and sm_start <= moment_end:
                    topic = standalone_moment.get('topic', 'Unknown')
                    why = standalone_moment.get('why_standalone', 'N/A')
                    story_context += f"""{newline}- Standalone Moment: {topic}
  ✅ Kann alleine funktionieren ohne Context
  Warum: {why}
"""
        
        # AI Prompt für Restrukturierung
        prompt = f"""Du bist ein Elite-Editor für virale Short-Form Content.

Deine Aufgabe: Restrukturiere diesen Moment für MAXIMALE Watch Time.

WICHTIG: Story-Kohärenz ist KRITISCH! Ein Clip der keinen Sinn ergibt performt schlecht.

{hook_context}

{viral_examples_guidance}

{story_context}

---

MOMENT TRANSCRIPT:
{moment_text}

MOMENT INFO:
- Topic: {moment.get('topic', 'Unknown')}
- Strength: {moment.get('strength', 'unknown')}
- Why Strong: {moment.get('reason', 'N/A')}
- Duration: {moment_duration:.1f}s

---

AUFGABE:

1. ANALYSIERE den Moment und finde den STÄRKSTEN Hook
   - Hook muss NICHT am Anfang sein!
   - Suche INNERHALB des Moments nach dem stärksten Satz/Moment
   - Nutze Viral Examples als Inspiration

2. RESTRUKTURIERE für maximale Watch Time:
   - Hook ZUERST (0-3s) - auch wenn er ursprünglich in der Mitte war
   - Context (3-15s) - Setup für Hook (NUR wenn Story es erlaubt!)
   - Content (15-40s) - Hauptinhalt mit Pattern Interrupts
   - Payoff (40-45s) - Satisfying Conclusion
   
   WICHTIG: Respektiere Story-Dependencies!
   - Wenn Story "requires_context: true" → füge nötigen Context hinzu
   - Wenn Story "can_standalone: false" → entferne NICHT wichtige Teile
   - Story-Kohärenz > Hook-Strength
   
3. ENTFERNE schwache Teile:
   - Langsame Intros (NUR wenn Story es erlaubt)
   - Füller
   - Wiederholungen
   - ABER: Entferne NICHT wenn es Story-Dependency ist!
   
4. OPTIMIERE Length:
   - Ziel: 30-60 Sekunden
   - Sweet Spot: 45 Sekunden
   - ABER: Wenn Story länger braucht → mache es länger (besser als verwirrend)

Antworte EXAKT in diesem JSON-Format:

{{
    "clip_id": "clip_{moment_id:02d}",
    "original_moment": {{
        "id": {moment_id},
        "start": {moment_start},
        "end": {moment_end},
        "topic": "{moment.get('topic', 'Unknown')}",
        "strength": "{moment.get('strength', 'unknown')}"
    }},
    "structure": {{
        "segments": [
            {{
                "role": "hook",
                "start": 145.0,
                "end": 150.0,
                "text": "Der stärkste Satz wird Hook",
                "reason": "Stärkster emotionaler Moment"
            }},
            {{
                "role": "context",
                "start": 140.0,
                "end": 145.0,
                "text": "Setup für Hook",
                "reason": "Erklärt warum Hook wichtig ist"
            }},
            {{
                "role": "content",
                "start": 150.0,
                "end": 165.0,
                "text": "Hauptinhalt",
                "reason": "Main content mit Pattern Interrupts"
            }},
            {{
                "role": "payoff",
                "start": 165.0,
                "end": 170.0,
                "text": "Abschluss",
                "reason": "Satisfying conclusion"
            }}
        ],
        "total_duration": 30.0,
        "restructured": true,
        "strategy": "hook_from_middle"
    }},
    "reasoning": {{
        "hook_choice": "Sentence at 145s has strongest emotional impact",
        "reorder_strategy": "Move climax to front, add context, then payoff",
        "removed_parts": ["Slow intro at 140-142s"],
        "watch_time_optimization": "Start strong, maintain tension, satisfying end"
    }},
    "scores": {{
        "watchtime_potential": 85,
        "virality_potential": 78,
        "hook_strength": 9
    }}
}}

WICHTIG:
- Hook-Zeiten müssen INNERHALB des Moments liegen ({moment_start:.1f}s - {moment_end:.1f}s)
- Alle Segment-Zeiten müssen korrekt sein
- Struktur muss Hook → Context → Content → Payoff folgen
- Optimale Length: 30-60s
"""
        
        try:
            response = self.client.messages.create(
                model=self._get_model('premium'),  # Premium task: Restructuring
                max_tokens=4000,
                timeout=120.0,  # 2 min timeout
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                clip_data = json.loads(json_match.group())
                
                # Validate times are within moment range
                structure = clip_data.get('structure', {})
                segments = structure.get('segments', [])
                
                # Adjust times to be relative to moment start
                adjusted_segments = []
                for seg in segments:
                    original_start = seg.get('start', moment_start)
                    original_end = seg.get('end', original_start + 5)
                    
                    # Ensure times are within moment
                    if original_start < moment_start:
                        original_start = moment_start
                    if original_end > moment_end:
                        original_end = moment_end
                    
                    adjusted_seg = seg.copy()
                    adjusted_seg['start'] = original_start
                    adjusted_seg['end'] = original_end
                    adjusted_segments.append(adjusted_seg)
                
                clip_data['structure']['segments'] = adjusted_segments
                
                # Recalculate total duration
                if adjusted_segments:
                    clip_data['structure']['total_duration'] = adjusted_segments[-1].get('end', moment_end) - adjusted_segments[0].get('start', moment_start)
                
                print(f"      ✅ Restructured: {len(adjusted_segments)} segments, {clip_data['structure']['total_duration']:.1f}s")
                
                return clip_data
            
            else:
                print(f"      ⚠️  Could not parse AI response")
                return None
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return None
    
    def _get_story_context_for_clip(self, clip, story_structure):
        """Extract relevant story context for quality evaluation"""
        
        clip_structure = clip.get('structure', {})
        clip_segments = clip_structure.get('segments', [])
        
        if not clip_segments:
            return {}
        
        clip_start = clip_segments[0].get('start', 0)
        clip_end = clip_segments[-1].get('end', 0)
        
        # Find which storyline this clip belongs to
        for storyline in story_structure.get('storylines', []):
            for seg in storyline.get('segments', []):
                seg_start = seg.get('start', 0)
                seg_end = seg.get('end', 0)
                if seg_start <= clip_start <= seg_end:
                    return {
                        'storyline_topic': storyline.get('topic', 'Unknown'),
                        'can_standalone': storyline.get('can_standalone', False),
                        'requires_context': storyline.get('requires_context', False),
                        'key_elements': seg.get('key_elements', [])
                    }
        
        # Check standalone moments
        for moment in story_structure.get('standalone_moments', []):
            moment_start = moment.get('start', 0)
            moment_end = moment.get('end', 0)
            if moment_start <= clip_start <= moment_end:
                return {
                    'type': 'standalone',
                    'topic': moment.get('topic', 'Unknown'),
                    'why_standalone': moment.get('why_standalone', 'N/A')
                }
        
        return {'type': 'unknown'}
    
    def _score_clip_quality(self, restructured_clip, story_structure):
        """
        Bewertet Clip-Qualität mit AI
        
        Kriterien (je 0-10):
        1. Story Coherence (macht Story Sinn?)
        2. Hook Strength (wie stark ist der Hook?)
        3. Natural Flow (fließt es natürlich?)
        4. Watchtime Potential (werden Leute bis Ende schauen?)
        5. Emotional Impact (emotional engaging?)
        
        Returns:
            {
                "total_score": 42,  # 0-50
                "scores": {...},
                "reasoning": {...},
                "quality_tier": "A"  # A/B/C/D
            }
        """
        
        if not self.client:
            print(f"   ⚠️  No API key for quality scoring")
            return {
                'total_score': 30,
                'scores': {},
                'reasoning': {'strengths': [], 'weaknesses': [], 'recommendation': 'unknown'},
                'quality_tier': 'C'
            }
        
        clip_structure = restructured_clip.get('structure', {})
        clip_reasoning = restructured_clip.get('reasoning', {})
        
        # Get story context
        story_context = self._get_story_context_for_clip(restructured_clip, story_structure)
        
        # Build segments text for AI
        segments_text = ""
        newline = "\n"
        for seg in clip_structure.get('segments', []):
            role = seg.get('role', 'unknown')
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            text = seg.get('text', '')[:200]
            segments_text += f"{newline}[{role.upper()}] {start:.1f}s-{end:.1f}s{newline}"
            segments_text += f"{text}...{newline}"
        
        prompt = f"""Du bist ein Quality Evaluator für virale Short-Form Videos.

AUFGABE: Bewerte diesen Clip nach 5 Kriterien (je 0-10 Punkte).

CLIP STRUCTURE:
{segments_text}

RESTRUCTURING STRATEGY:
{clip_reasoning.get('reorder_strategy', 'N/A')}

STORY CONTEXT:
- Topic: {story_context.get('storyline_topic', story_context.get('topic', 'N/A'))}
- Standalone: {story_context.get('can_standalone', 'N/A')}
- Requires Context: {story_context.get('requires_context', 'N/A')}

BEWERTE STRENG (lieber zu kritisch als zu locker):

1. STORY COHERENCE (0-10):
   Macht die Story Sinn? Versteht man alles ohne Vorwissen?
   
   0-3: Story konfus/macht keinen Sinn
   4-6: Story OK, aber Lücken
   7-8: Story macht Sinn
   9-10: Story kristallklar

2. HOOK STRENGTH (0-10):
   Wie stark sind die ersten 3 Sekunden?
   
   0-3: Schwacher/langweiliger Hook
   4-6: OK Hook
   7-8: Starker Hook
   9-10: Unwiderstehlicher Hook

3. NATURAL FLOW (0-10):
   Fließt der Clip natürlich oder wirkt er zusammengeschnitten?
   
   0-3: Sehr abgehackt
   4-6: Etwas holprig
   7-8: Fließt gut
   9-10: Perfekt smooth

4. WATCHTIME POTENTIAL (0-10):
   Werden Leute bis zum Ende schauen?
   
   0-3: Hohes Drop-off Risiko
   4-6: Durchschnittliche Retention
   7-8: Gute Retention
   9-10: Excellente Retention

5. EMOTIONAL IMPACT (0-10):
   Löst der Clip Emotionen aus?
   
   0-3: Emotional flach
   4-6: Leicht emotional
   7-8: Emotional engaging
   9-10: Sehr impactful

WICHTIG:
- Story-Kohärenz ist WICHTIGER als Hook-Strength
- Wenn Clip verwirrt → niedrige Story Score
- Wenn restrukturiert aber nicht smooth → niedrige Flow Score

ANTWORTE EXAKT in diesem JSON Format:
{{
  "scores": {{
    "story_coherence": 8,
    "hook_strength": 7,
    "natural_flow": 9,
    "watchtime_potential": 8,
    "emotional_impact": 7
  }},
  "total_score": 39,
  "reasoning": {{
    "strengths": [
      "Hook ist emotional stark",
      "Story fließt natürlich"
    ],
    "weaknesses": [
      "Payoff könnte stärker sein"
    ],
    "recommendation": "good"
  }},
  "quality_tier": "B"
}}
"""
        
        try:
            # Use premium model for quality eval
            response = self.client.messages.create(
                model=self._get_model('premium'),
                max_tokens=2000,
                timeout=60.0,  # 1 min timeout
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                quality = json.loads(json_match.group())
                
                # Calculate tier from score if not provided
                if 'quality_tier' not in quality:
                    score = quality.get('total_score', 0)
                    if score >= 40:
                        quality['quality_tier'] = 'A'
                    elif score >= 32:
                        quality['quality_tier'] = 'B'
                    elif score >= 24:
                        quality['quality_tier'] = 'C'
                    else:
                        quality['quality_tier'] = 'D'
                
                return quality
            
            else:
                print(f"   ⚠️  Could not parse quality response")
                return {
                    'total_score': 30,
                    'scores': {},
                    'reasoning': {'strengths': [], 'weaknesses': [], 'recommendation': 'unknown'},
                    'quality_tier': 'C'
                }
        
        except Exception as e:
            print(f"   ⚠️ Quality scoring error: {e}")
            # Fallback: neutral score
            return {
                'total_score': 30,
                'scores': {},
                'reasoning': {'strengths': [], 'weaknesses': [], 'recommendation': 'unknown'},
                'quality_tier': 'C'
            }
    
    def _create_variations(self, restructured_clip, all_segments):
        """
        STEP 3: Create variations for a clip
        
        Creates 2-3 variations with different hooks/structures
        
        Args:
            clip: Restructured clip from _restructure_moment()
            all_segments: All transcript segments
        
        Returns:
            List of variations
        """
        
        quality_tier = restructured_clip.get('quality', {}).get('quality_tier', 'C')
        clip_id = restructured_clip.get('clip_id', 'unknown')
        
        # Determine how many variations based on tier
        if quality_tier == 'A':
            max_variations = 3
        elif quality_tier == 'B':
            max_variations = 2
        else:  # C or unknown
            max_variations = 1
        
        print(f"\n   🎨 Creating variations for {clip_id} (Tier {quality_tier}, max {max_variations})...")
        
        variations = []
        
        # Original always included
        original = {
            'version_id': f"{clip_id}_original",
            'version_name': 'Original Structure',
            'variation_type': 'original',
            'structure': restructured_clip.get('structure', {}),
            'reasoning': restructured_clip.get('reasoning', {}),
            'quality': restructured_clip.get('quality', {}),
            'scores': restructured_clip.get('scores', {})
        }
        variations.append(original)
        
        # Additional variations only if tier allows and AI available
        if max_variations >= 2 and self.client:
            # Try alternative hook
            alt = self._create_alternative_variation(restructured_clip, all_segments, 'hook')
            if alt:
                variations.append(alt)
        
        if max_variations >= 3 and self.client:
            # Try different structure
            diff = self._create_alternative_variation(restructured_clip, all_segments, 'structure')
            if diff:
                variations.append(diff)
        
        return variations
    
    def _create_alternative_variation(self, clip, all_segments, variation_type):
        """Create a single alternative variation"""
        
        clip_id = clip.get('clip_id', 'unknown')
        structure = clip.get('structure', {})
        segments = structure.get('segments', [])
        
        if not segments:
            return None
        
        # Format clip transcript
        clip_text = ""
        for seg in segments:
            clip_text += f"[{seg.get('start', 0):.1f}s-{seg.get('end', 0):.1f}s] {seg.get('text', '')}\n"
        
        hook_context = self._get_focused_context("hook_focused")
        
        if variation_type == 'hook':
            prompt = f"""Erstelle eine ALTERNATIVE Hook-Variation für diesen Clip.

{hook_context}

CLIP STRUCTURE:
{clip_text}

AUFGABE: Nutze einen ANDEREN starken Satz als Hook (nicht den Original-Hook).

Antworte im gleichen JSON Format wie Original, aber mit anderem Hook.
"""
        else:  # structure
            prompt = f"""Erstelle eine ANDERE Struktur-Variation für diesen Clip.

{hook_context}

CLIP STRUCTURE:
{clip_text}

AUFGABE: Nutze eine ANDERE Struktur (z.B. Payoff-First statt Hook-First).

Antworte im gleichen JSON Format wie Original, aber mit anderer Struktur.
"""
        
        try:
            response = self.client.messages.create(
                model=self._get_model('simple'),  # Simple task: Variations
                max_tokens=4000,
                timeout=60.0,  # 1 min timeout
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                variation_data = json.loads(json_match.group())
                
                variation = {
                    'version_id': f"{clip_id}_{variation_type}",
                    'version_name': f"Alternative {variation_type.title()}",
                    'variation_type': variation_type,
                    'structure': variation_data.get('structure', structure),
                    'scores': variation_data.get('scores', {}),
                    'why_different': f"Alternative {variation_type} approach"
                }
                
                return variation
            
            return None
        
        except Exception as e:
            print(f"      ⚠️  Variation creation error: {e}")
            return None
    
    def extract_clips(self, segments, video_path):
        """
        Multi-Step Clip Extraction Process
        
        V2: Statt einem großen Prompt, machen wir es Schritt für Schritt
        """
        
        if not self.client:
            print("❌ No API key")
            return None
        
        print(f"\n{'='*70}")
        print("🎬 MULTI-STEP CLIP EXTRACTION")
        print(f"{'='*70}")
        
        # STEP 1: Find ALL strong moments
        moments = self._find_all_moments(segments)
        
        if not moments:
            print("\n❌ No moments found")
            return None
        
        print(f"\n✅ Step 1 complete: Found {len(moments)} moments")
        
        # STEP 0: Analyze Story Structure (NEW!)
        story_structure = self._analyze_story_structure(segments)
        
        # STEP 2: Restructure each moment (with story context)
        print(f"\n{'='*70}")
        print("🔧 STEP 2: RESTRUCTURING MOMENTS (with Story Context)")
        print(f"{'='*70}")
        
        restructured_clips = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n[{i}/{len(moments)}] Processing moment #{moment.get('id', i)}...")
            
            restructured = self._restructure_moment(moment, segments, story_structure)
            
            if restructured:
                restructured_clips.append(restructured)
            else:
                print(f"      ⚠️  Skipping moment #{moment.get('id', i)}")
        
        if not restructured_clips:
            print("\n❌ No clips restructured")
            return None
        
        print(f"\n✅ Step 2 complete: {len(restructured_clips)} clips restructured")
        
        # STEP 2.5: QUALITY FILTER (NEW!)
        print(f"\n{'='*70}")
        print("⭐ STEP 2.5: Quality Evaluation & Filtering")
        print(f"{'='*70}")
        
        quality_checked_clips = []
        tier_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for i, clip in enumerate(restructured_clips, 1):
            print(f"\n📊 Evaluating clip {i}/{len(restructured_clips)}...")
            
            quality = self._score_clip_quality(clip, story_structure)
            
            # Add quality to clip data
            clip['quality'] = quality
            
            tier = quality.get('quality_tier', 'C')
            total = quality.get('total_score', 0)
            
            tier_counts[tier] += 1
            
            if tier == 'A':
                print(f"   ⭐ EXCELLENT (A) - Score: {total}/50")
                quality_checked_clips.append(clip)
            elif tier == 'B':
                print(f"   ✅ GOOD (B) - Score: {total}/50")
                quality_checked_clips.append(clip)
            elif tier == 'C':
                print(f"   ⚠️  MEDIOCRE (C) - Score: {total}/50")
                quality_checked_clips.append(clip)
            else:  # tier == 'D'
                print(f"   ❌ POOR (D) - Score: {total}/50 - SKIPPED")
                # Don't add to quality_checked_clips
        
        print(f"\n📊 Quality Distribution:")
        print(f"   ⭐ A (Excellent): {tier_counts['A']}")
        print(f"   ✅ B (Good): {tier_counts['B']}")
        print(f"   ⚠️  C (Mediocre): {tier_counts['C']}")
        print(f"   ❌ D (Poor/Skipped): {tier_counts['D']}")
        print(f"\n   ✅ Passed Quality Filter: {len(quality_checked_clips)}/{len(restructured_clips)}")
        
        if not quality_checked_clips:
            print("\n❌ No clips passed quality filter")
            return None
        
        # STEP 3: Create Variations (quality-tier based)
        print(f"\n{'='*70}")
        print("🎨 STEP 3: Creating variations (quality-tier based)")
        print(f"{'='*70}")
        
        final_clips = []
        
        for i, clip in enumerate(quality_checked_clips, 1):
            tier = clip.get('quality', {}).get('quality_tier', 'C')
            clip_id = clip.get('clip_id', 'unknown')
            
            print(f"\n📌 Clip {i}/{len(quality_checked_clips)} (Tier {tier})...")
            
            variations = self._create_variations(clip, segments)
            
            if variations:
                final_clips.append({
                    "clip_id": clip_id,
                    "original_moment": clip.get('original_moment', {}),
                    "quality": clip.get('quality', {}),
                    "versions": variations,
                    "best_version": variations[0].get('version_id') if variations else None
                })
            
            print(f"   ✅ Created {len(variations)} variation(s)")
        
        total_versions = sum(len(c.get('versions', [])) for c in final_clips)
        print(f"\n✅ Step 3 complete: {len(final_clips)} clips with {total_versions} total versions")
        
        # Prepare result
        total_versions = sum(len(c.get('versions', [])) for c in final_clips)
        
        result = {
            "story_structure": story_structure,
            "analysis": {
                "total_moments_found": len(moments),
                "storylines_identified": len(story_structure.get('storylines', [])),
                "standalone_moments": len(story_structure.get('standalone_moments', [])),
                "clips_restructured": len(restructured_clips),
                "clips_passed_quality": len(quality_checked_clips),
                "clips_rejected": tier_counts['D'],
                "total_versions": total_versions
            },
            "quality_distribution": tier_counts,
            "clips": final_clips,
            "summary": {
                "total_clips": len(final_clips),
                "total_versions": total_versions,
                "steps_completed": 3,
                "story_aware": True,
                "quality_filtered": True
            }
        }
        
        # Final Summary
        print(f"\n{'='*70}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*70}")
        print(f"   📖 Story-aware moments: {len(moments)}")
        print(f"   🔄 Restructured clips: {len(restructured_clips)}")
        print(f"   ⭐ Quality passed: {len(quality_checked_clips)}")
        print(f"   ❌ Quality rejected: {tier_counts['D']}")
        print(f"   🎬 Total versions: {total_versions}")
        print(f"\n   Quality tiers: A={tier_counts['A']}, B={tier_counts['B']}, C={tier_counts['C']}")
        
        return result
    
    # =========================================================================
    # EXPORT FUNCTIONS (Updated for v2 structure)
    # =========================================================================
    
    def export_clips(self, extraction_result, video_path):
        """
        Export all clips with their versions
        
        Neue Struktur von extraction_result:
        {
            "clips": [
                {
                    "clip_id": "clip_01",
                    "original_moment": {...},
                    "versions": [
                        {
                            "version_id": "clip_01_original",
                            "version_name": "Original Structure",
                            "structure": {...}
                        }
                    ]
                }
            ],
            "analysis": {...}
        }
        """
        
        clips = extraction_result.get('clips', [])
        video_path = Path(video_path)
        
        print(f"\n{'='*70}")
        print(f"📦 EXPORTING CLIPS")
        print(f"{'='*70}")
        
        if not clips:
            print("❌ No clips to export")
            return None
        
        # Create output folder with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        export_dir = self.output_dir / f"{video_path.stem}_{timestamp}"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        exported_count = 0
        
        # Export each clip with its versions
        for clip_data in clips:
            clip_id = clip_data.get('clip_id', 'unknown')
            
            print(f"\n📦 Exporting {clip_id}...")
            print(f"   Versions: {len(clip_data.get('versions', []))}")
            
            for version in clip_data.get('versions', []):
                version_id = version.get('version_id', 'unknown')
                
                print(f"\n   📦 Exporting {version_id}...")
                
                try:
                    # Create version directory
                    version_dir = export_dir / version_id
                    version_dir.mkdir(exist_ok=True)
                    
                    # 1. Export MP4
                    self._export_mp4(version, video_path, version_dir, version_id)
                    
                    # 2. Export XML (Premiere)
                    self._export_xml(version, video_path, version_dir, version_id)
                    
                    # 3. Export Info JSON
                    self._export_info(clip_data, version, version_dir, version_id)
                    
                    exported_count += 1
                    
                except Exception as e:
                    print(f"      ⚠️ Error exporting {version_id}: {e}")
        
        # Save full extraction result
        with open(export_dir / "extraction_result.json", 'w') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ EXPORT COMPLETE!")
        print(f"{'='*70}")
        print(f"\n📁 Output: {export_dir}")
        print(f"   📊 Clips exported: {len(clips)}")
        print(f"   📊 Versions exported: {exported_count}")
        print(f"   📊 Each version has: MP4 + XML + Info JSON")
        
        return export_dir
    
    def _export_mp4(self, version, video_path, output_dir, name):
        """Export MP4 with reordered segments"""
        
        structure = version.get('structure', {})
        segments = structure.get('segments', [])
        
        if not segments:
            print(f"      ⚠️ No segments for {name}")
            return
        
        temp_files = []
        
        # Cut each segment in order
        for i, seg in enumerate(segments):
            temp_file = output_dir / f"temp_{i}.mp4"
            
            seg_start = seg.get('start', 0)
            seg_end = seg.get('end', seg_start + 10)
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-ss', str(seg_start),
                '-to', str(seg_end),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-avoid_negative_ts', 'make_zero',
                str(temp_file),
                '-loglevel', 'error'
            ]
            
            subprocess.run(cmd, capture_output=True)
            
            if temp_file.exists():
                temp_files.append(temp_file)
        
        # Concat all segments
        if temp_files:
            concat_file = output_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for tf in temp_files:
                    f.write(f"file '{tf.absolute()}'\n")
            
            output_mp4 = output_dir / f"{name}.mp4"
            
            subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                str(output_mp4),
                '-loglevel', 'error'
            ], capture_output=True)
            
            # Cleanup temp files
            for tf in temp_files:
                if tf.exists():
                    tf.unlink()
            if concat_file.exists():
                concat_file.unlink()
            
            if output_mp4.exists():
                file_size = output_mp4.stat().st_size / 1024 / 1024
                print(f"      ✅ MP4: {name}.mp4 ({file_size:.1f} MB)")
    
    def _export_xml(self, version, video_path, output_dir, name):
        """Export proper Premiere Pro XML with correct in/out points"""
        
        try:
            from premiere_xml_generator import generate_premiere_xml
            
            # Extract segments from version structure
            structure = version.get('structure', {})
            segments = structure.get('segments', [])
            
            if not segments:
                print(f"      ⚠️ No segments for XML")
                return
            
            xml_path = output_dir / f"{name}.xml"
            
            result = generate_premiere_xml(
                segments=segments,
                source_video_path=video_path,
                output_path=xml_path,
                sequence_name=name
            )
            
            if result:
                print(f"      ✅ XML: {name}.xml (Premiere ready)")
        
        except ImportError:
            # Fallback: Simple XML
            structure = version.get('structure', {})
            duration = structure.get('total_duration', 60)
            fps = 30
            
            xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <sequence>
    <n>{name}</n>
    <duration>{int(duration * fps)}</duration>
    <rate><timebase>{fps}</timebase></rate>
  </sequence>
</xmeml>"""
            
            xml_path = output_dir / f"{name}.xml"
            with open(xml_path, 'w') as f:
                f.write(xml)
            
            print(f"      ✅ XML: {name}.xml (simple)")
        except Exception as e:
            print(f"      ⚠️ XML error: {e}")
    
    def _export_info(self, clip_data, version, output_dir, name):
        """
        Export comprehensive clip info
        
        Includes:
        - Original moment info
        - Version structure
        - Reasoning
        - Scores
        """
        
        structure = version.get('structure', {})
        scores = version.get('scores', {})
        reasoning = version.get('reasoning', clip_data.get('reasoning', {}))
        
        info = {
            'clip_id': clip_data.get('clip_id', 'unknown'),
            'version_id': version.get('version_id', 'unknown'),
            'version_name': version.get('version_name', ''),
            
            # Original moment
            'original_moment': clip_data.get('original_moment', {}),
            
            # Structure (mit restructured segments)
            'structure': structure,
            
            # Reasoning (warum diese Struktur)
            'reasoning': reasoning,
            
            # Scores (wenn vorhanden)
            'scores': {
                'watchtime_potential': scores.get('watchtime_potential', 0),
                'virality_potential': scores.get('virality_potential', 0),
                'hook_strength': scores.get('hook_strength', 0)
            },
            
            # Metadata
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version_type': 'original' if 'original' in version.get('version_id', '') else 'variation',
                'system_version': 'v2_multi_step',
                'restructured': structure.get('restructured', False),
                'strategy': structure.get('strategy', 'unknown')
            }
        }
        
        info_path = output_dir / f"{name}_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        wt_score = scores.get('watchtime_potential', 0)
        vir_score = scores.get('virality_potential', 0)
        print(f"      ✅ Info: {name}_info.json (WT:{wt_score} VIR:{vir_score})")
    
    # =========================================================================
    # MAIN WORKFLOW
    # =========================================================================
    
    def process_video(self, video_path):
        """
        Complete workflow for a single video
        """
        
        video_path = Path(video_path)
        
        if not video_path.exists():
            print(f"❌ Video not found: {video_path}")
            return
        
        print(f"\n{'='*70}")
        print(f"🎬 PROCESSING: {video_path.name}")
        print(f"{'='*70}")
        
        # 1. Get transcript
        cached = self.find_transcript(video_path)
        
        if cached:
            segments = self.load_transcript(cached)
        else:
            segments = self.transcribe_video(video_path)
        
        if not segments:
            print("❌ No transcript")
            return
        
        print(f"   ✅ Loaded {len(segments)} segments")
        
        # 2. Extract clips (Multi-Step)
        result = self.extract_clips(segments, video_path)
        
        if not result:
            return
        
        # 3. Export clips
        export_choice = input("\n📦 Export clips? (y/n): ").strip().lower()
        if export_choice == 'y':
            self.export_clips(result, video_path)
        else:
            # Just save the analysis
            analysis_path = self.output_dir / f"{video_path.stem}_analysis_v2.json"
            with open(analysis_path, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n📊 Analysis saved: {analysis_path}")


def main():
    """Main entry point"""
    
    creator = CreateClipsV2()
    
    if not creator.patterns:
        print("\n⚠️  No learned patterns found!")
        print("   Run 'python analyze_and_learn.py' first to train the AI.")
        print("   Continuing without patterns (reduced accuracy)...\n")
    
    print("\n" + "="*70)
    print("📝 INPUT OPTIONS:")
    print("   1. 📁 Local video file path")
    print("   2. 🔗 Video URL (YouTube, Instagram, TikTok, etc.)")
    print("="*70)
    
    choice = input("\nChoice (1-2): ").strip()
    
    video_path = None
    
    if choice == '2':
        print("\n⚠️  URL download not yet implemented in v2")
        return
    
    else:
        # Local file
        video_path = input("\n📁 Video path: ").strip()
        
        if not video_path:
            print("❌ No video path")
            return
        
        video_path = Path(video_path)
        
        if not video_path.exists():
            print(f"❌ File not found: {video_path}")
            return
    
    creator.process_video(video_path)


if __name__ == "__main__":
    main()

