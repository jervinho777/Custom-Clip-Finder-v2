#!/usr/bin/env python3
"""
🎬 WORKFLOW 2: CREATE CLIPS

This script creates watchtime-optimized clips from longform videos.
Uses learned patterns from WORKFLOW 1 (analyze_and_learn.py)

INPUT: Longform video (MP4)
OUTPUT:
  - Multiple watchtime-optimized clips (MP4)
  - Premiere Pro XML for each clip
  - Transcript with structure notes
  - Multiple versions per clip (different hooks/structures)
  - Virality/Watchtime scores

FEATURES:
  ✅ Auto-finds cached transcripts
  ✅ AI determines optimal number of clips
  ✅ Creates multiple versions per clip
  ✅ Scores each clip with learned patterns
  ✅ Exports ready-to-upload files
"""

import json
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

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


class CreateClips:
    """
    Main class for creating watchtime-optimized clips
    """
    
    def __init__(self):
        # API
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        
        # Paths
        self.data_dir = Path("data")
        self.cache_dir = self.data_dir / "cache" / "transcripts"
        self.output_dir = Path("output/clips")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load learned patterns
        self.patterns = self._load_patterns()
        self.ml_model = self._load_ml_model()
        
        print("="*70)
        print("🎬 CREATE CLIPS - Watchtime Optimizer")
        print("="*70)
        print(f"   🤖 AI: {'Connected' if self.client else 'Not available'}")
        print(f"   📚 Patterns: {'Loaded' if self.patterns else 'Not found - run analyze_and_learn.py first'}")
        print(f"   📈 ML Model: {'Loaded' if self.ml_model else 'Not found'}")
        print(f"   🧠 Master Learnings: {'Loaded' if LEARNINGS_AVAILABLE else 'Not available'}")
    
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
        model_file = self.data_dir / "ml_model.pkl"
        if model_file.exists() and ML_AVAILABLE:
            with open(model_file, 'rb') as f:
                return pickle.load(f)
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
    # CLIP EXTRACTION
    # =========================================================================
    
    def extract_clips(self, segments, video_path):
        """
        AI-powered clip extraction
        
        - Determines optimal number of clips
        - Creates multiple versions per clip
        - Scores each version
        """
        
        if not self.client:
            print("❌ No API key")
            return None
        
        print(f"\n{'='*70}")
        print("🎬 EXTRACTING CLIPS")
        print(f"{'='*70}")
        
        # Prepare transcript
        full_text = ""
        for seg in segments:
            full_text += f"[{seg['start']:.1f}s-{seg['end']:.1f}s] {seg['text']}\n"
        
        total_duration = segments[-1]['end'] if segments else 0
        
        print(f"\n📊 Video Stats:")
        print(f"   Duration: {total_duration/60:.1f} minutes")
        print(f"   Segments: {len(segments)}")
        
        # Build patterns context - PRIORITIZE MASTER LEARNINGS
        patterns_ctx = ""
        
        # First try Master Learnings (most comprehensive)
        if LEARNINGS_AVAILABLE:
            try:
                patterns_ctx = get_learnings_for_prompt()
                print("   ✅ Using Master Learnings")
            except Exception as e:
                print(f"   ⚠️ Master Learnings error: {e}")
        
        # Fallback to basic patterns if no master learnings
        if not patterns_ctx and self.patterns:
            patterns_ctx = f"""
GELERNTE VIRAL PATTERNS (aus {self.patterns.get('metadata', {}).get('total_training_clips', 972)} erfolgreichen Clips):

VIRAL PATTERNS:
{json.dumps(self.patterns.get('viral_patterns', [])[:5], indent=2, ensure_ascii=False)}

WINNING HOOKS:
{json.dumps(self.patterns.get('hook_patterns', {}), indent=2, ensure_ascii=False)}

SCORING CRITERIA:
{json.dumps(self.patterns.get('scoring_criteria', {}), indent=2, ensure_ascii=False)}

RED FLAGS:
{json.dumps(self.patterns.get('red_flags', []), indent=2, ensure_ascii=False)}
"""
        
        prompt = f"""Du bist ein Elite-Editor für virale Short-Form Content.

{WATCHTIME_FRAMEWORK}

{patterns_ctx}

---

LONGFORM TRANSCRIPT:
{full_text[:18000]}

---

AUFGABE:

1. ANALYSIERE das Video und bestimme die OPTIMALE Anzahl von Clips
   - Qualität > Quantität
   - Nur Momente mit echtem Viral-Potential

2. Für JEDEN Clip:
   a) Finde die BESTE Kernaussage/Moment
   b) Identifiziere den STÄRKSTEN Hook (muss nicht am Anfang sein!)
   c) Erstelle 2-3 VERSIONEN mit unterschiedlichen Strukturen:
      - Version A: Hook aus der Mitte nach vorne gezogen
      - Version B: Alternativer Hook
      - Version C: Andere Reihenfolge (optional)

3. BEWERTE jede Version:
   - Watchtime Score (0-100)
   - Virality Score (0-100)
   - Begründung

Antworte in diesem JSON-Format:

{{
    "analysis": {{
        "total_duration_minutes": {total_duration/60:.1f},
        "recommended_clips": 5,
        "reasoning": "Warum diese Anzahl optimal ist",
        "content_themes": ["Theme 1", "Theme 2"]
    }},
    
    "clips": [
        {{
            "clip_id": "clip_01",
            "title": "Catchy Titel",
            "core_message": "Die Kernaussage in einem Satz",
            
            "versions": [
                {{
                    "version_id": "clip_01_A",
                    "version_name": "Hook First",
                    "structure": {{
                        "segments": [
                            {{
                                "role": "hook",
                                "start": 145.2,
                                "end": 149.5,
                                "text": "Der stärkste Satz"
                            }},
                            {{
                                "role": "context",
                                "start": 140.0,
                                "end": 145.2,
                                "text": "Kontext"
                            }},
                            {{
                                "role": "content",
                                "start": 149.5,
                                "end": 165.0,
                                "text": "Hauptinhalt"
                            }},
                            {{
                                "role": "payoff",
                                "start": 165.0,
                                "end": 172.0,
                                "text": "Abschluss"
                            }}
                        ],
                        "total_duration": 32.0
                    }},
                    "scores": {{
                        "watchtime_score": 85,
                        "virality_score": 78,
                        "hook_strength": 9,
                        "reasoning": "Warum diese Scores"
                    }},
                    "matched_patterns": ["Pattern 1", "Pattern 2"],
                    "improvements": ["Was noch besser sein könnte"]
                }},
                {{
                    "version_id": "clip_01_B",
                    "version_name": "Alternative Hook",
                    ...
                }}
            ],
            
            "best_version": "clip_01_A",
            "why_best": "Begründung"
        }}
    ],
    
    "summary": {{
        "total_clips": 5,
        "total_versions": 12,
        "average_watchtime_score": 82,
        "best_clip": "clip_01",
        "production_notes": "Hinweise für die Produktion"
    }}
}}"""
        
        print("\n🧠 AI analyzing video for optimal clips...")
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                
                # Print summary
                analysis = result.get('analysis', {})
                clips = result.get('clips', [])
                
                print(f"\n✅ Analysis complete!")
                print(f"   📊 Recommended clips: {analysis.get('recommended_clips', len(clips))}")
                print(f"   📝 Themes: {', '.join(analysis.get('content_themes', []))}")
                
                print(f"\n🎬 EXTRACTED CLIPS:")
                for clip in clips:
                    print(f"\n   {clip['clip_id']}: {clip['title']}")
                    print(f"   Core: {clip.get('core_message', '')[:60]}...")
                    
                    for v in clip.get('versions', []):
                        scores = v.get('scores', {})
                        print(f"      • {v['version_id']}: WT={scores.get('watchtime_score', 0)} VIR={scores.get('virality_score', 0)}")
                
                return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    # =========================================================================
    # EXPORT
    # =========================================================================
    
    def export_clips(self, extraction_result, video_path):
        """Export all clips and versions"""
        
        clips = extraction_result.get('clips', [])
        video_path = Path(video_path)
        
        print(f"\n{'='*70}")
        print(f"📦 EXPORTING CLIPS")
        print(f"{'='*70}")
        
        # Create output folder with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        export_dir = self.output_dir / f"{video_path.stem}_{timestamp}"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        exported = []
        
        for clip in clips:
            clip_id = clip['clip_id']
            
            for version in clip.get('versions', []):
                version_id = version['version_id']
                
                print(f"\n   📦 Exporting {version_id}...")
                
                try:
                    clip_dir = export_dir / version_id
                    clip_dir.mkdir(exist_ok=True)
                    
                    # 1. Export MP4
                    self._export_mp4(version, video_path, clip_dir, version_id)
                    
                    # 2. Export XML
                    self._export_xml(version, video_path, clip_dir, version_id)
                    
                    # 3. Export transcript/info
                    self._export_info(clip, version, clip_dir, version_id)
                    
                    exported.append(version_id)
                    
                except Exception as e:
                    print(f"      ⚠️ Error: {e}")
        
        # Save full extraction result
        with open(export_dir / "extraction_result.json", 'w') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ EXPORT COMPLETE!")
        print(f"{'='*70}")
        print(f"\n📁 Output: {export_dir}")
        print(f"   • {len(exported)} versions exported")
        print(f"   • Each has: MP4 + XML + Info")
        
        return export_dir
    
    def _export_mp4(self, version, video_path, output_dir, name):
        """Export MP4 with reordered segments"""
        
        segments = version.get('structure', {}).get('segments', [])
        
        if not segments:
            print(f"      ⚠️ No segments")
            return
        
        temp_files = []
        
        # Cut each segment
        for i, seg in enumerate(segments):
            temp_file = output_dir / f"temp_{i}.mp4"
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-ss', str(seg.get('start', 0)),
                '-to', str(seg.get('end', seg.get('start', 0) + 10)),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-avoid_negative_ts', 'make_zero',
                str(temp_file),
                '-loglevel', 'error'
            ]
            
            subprocess.run(cmd, capture_output=True)
            
            if temp_file.exists():
                temp_files.append(temp_file)
        
        # Concat
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
            
            # Cleanup
            for tf in temp_files:
                tf.unlink()
            concat_file.unlink()
            
            if output_mp4.exists():
                print(f"      ✅ MP4: {name}.mp4")
    

    def _export_xml(self, version, video_path, output_dir, name):
        """Export proper Premiere Pro XML with correct in/out points"""
        
        try:
            from premiere_xml_generator import generate_premiere_xml
            
            # Extract segments from version structure
            segments = version.get('structure', {}).get('segments', [])
            
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
            duration = version.get('structure', {}).get('total_duration', 60)
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

    def _export_info(self, clip, version, output_dir, name):
        """Export clip info/transcript"""
        
        scores = version.get('scores', {})
        
        info = {
            'clip_id': clip['clip_id'],
            'version_id': version['version_id'],
            'version_name': version.get('version_name', ''),
            'title': clip.get('title', ''),
            'core_message': clip.get('core_message', ''),
            'scores': {
                'watchtime_score': scores.get('watchtime_score', 0),
                'virality_score': scores.get('virality_score', 0),
                'hook_strength': scores.get('hook_strength', 0),
                'reasoning': scores.get('reasoning', '')
            },
            'structure': version.get('structure', {}),
            'matched_patterns': version.get('matched_patterns', []),
            'improvements': version.get('improvements', []),
            'is_best_version': clip.get('best_version') == version['version_id'],
            'exported_at': datetime.now().isoformat()
        }
        
        info_path = output_dir / f"{name}_info.json"
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"      ✅ Info: {name}_info.json (WT:{scores.get('watchtime_score', 0)} VIR:{scores.get('virality_score', 0)})")
    
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
        
        # 2. Extract clips
        result = self.extract_clips(segments, video_path)
        
        if not result:
            return
        
        # 3. Export
        export = input("\n📦 Export clips? (y/n): ").strip().lower()
        if export == 'y':
            self.export_clips(result, video_path)
        else:
            # Just save the analysis
            analysis_path = self.output_dir / f"{video_path.stem}_analysis.json"
            with open(analysis_path, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n📊 Analysis saved: {analysis_path}")


def download_video(url):
    """
    Download video from URL using yt-dlp
    
    Supports: YouTube, Instagram, TikTok, Facebook, Twitter, etc.
    """
    
    print(f"\n{'='*70}")
    print("📥 DOWNLOADING VIDEO")
    print(f"{'='*70}")
    print(f"   URL: {url}")
    
    # Create uploads directory
    uploads_dir = Path("data/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_template = str(uploads_dir / f"video_{timestamp}.%(ext)s")
    
    # yt-dlp command - FORCE video+audio merge
    cmd = [
        'yt-dlp',
        '--no-warnings',
        '--no-playlist',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Force video+audio
        '--merge-output-format', 'mp4',  # Ensure MP4 output
        '-o', output_template,
        url
    ]
    
    try:
        print("\n🔄 Downloading...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"❌ Download failed: {result.stderr}")
            return None
        
        # Find downloaded file
        downloaded_files = list(uploads_dir.glob(f"video_{timestamp}.*"))
        
        if not downloaded_files:
            print("❌ Could not find downloaded file")
            return None
        
        video_path = downloaded_files[0]
        
        # Verify it's a video file (not just audio)
        file_size = video_path.stat().st_size / 1024 / 1024
        
        print(f"\n✅ Downloaded: {video_path.name}")
        print(f"   Size: {file_size:.1f} MB")
        
        # Quick check if it has video stream
        check_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)
        
        if 'video' not in check_result.stdout:
            print(f"⚠️ WARNING: File might be audio-only!")
            print(f"   Trying alternative download method...")
            
            # Try again with different format
            video_path.unlink()
            
            cmd_alt = [
                'yt-dlp',
                '--no-warnings',
                '--no-playlist',
                '-f', 'best',
                '--recode-video', 'mp4',
                '-o', output_template,
                url
            ]
            
            result = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                return None
            
            downloaded_files = list(uploads_dir.glob(f"video_{timestamp}.*"))
            if downloaded_files:
                video_path = downloaded_files[0]
                print(f"   ✅ Retry successful: {video_path.name}")
        
        return video_path
    
    except subprocess.TimeoutExpired:
        print("❌ Download timeout (10 minutes)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main entry point"""
    
    creator = CreateClips()
    
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
        # Download from URL
        url = input("\n🔗 Video URL: ").strip()
        
        if not url:
            print("❌ No URL provided")
            return
        
        video_path = download_video(url)
        
        if not video_path:
            print("❌ Download failed")
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
