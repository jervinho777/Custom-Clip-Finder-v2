#!/usr/bin/env python3
"""
🚀 WATCHTIME-OPTIMIZED CLIP EXTRACTOR v2

INPUT: Video path (z.B. data/uploads/test.mp4)
- Auto-finds cached transcript in data/cache/transcripts/
- If not found, transcribes with Whisper

OUTPUT: 
  - Watchtime-optimierte Short-Form Clips (MP4)
  - Premiere Pro XML für jeden Clip
  - Transcript mit Timecodes
"""

import json
import os
import subprocess
import re
import hashlib
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

# =============================================================================
# KNOWLEDGE BASE
# =============================================================================

WATCHTIME_OPTIMIZATION = """
# WATCHTIME OPTIMIZATION FRAMEWORK

## Algorithmus-Verständnis:
- Algorithmus hat EIN Ziel: Watchtime maximieren
- Du kämpfst gegen ALLE anderen Videos
- Video mit höchster Watchtime gewinnt

## Clip-Struktur für MAX Watchtime:

### 1. HOOK (0-3 Sekunden) - KRITISCH
- Muss SOFORT Spannung aufbauen
- Information Gap öffnen
- Visueller + verbaler Stop-Trigger
- KEIN Intro, KEIN "Hallo", direkt rein

### 2. LOOP ÖFFNEN (3-10 Sekunden)
- Versprechen was kommt
- "Gleich zeige ich dir..."
- Unvollständiger Loop → Gehirn will Abschluss

### 3. CONTENT MIT PATTERN INTERRUPTS
- Alle 5-7 Sekunden: Mini-Payoff oder neuer Hook
- Keine Monotonie
- Emotionale Achterbahn (nicht Flatline)

### 4. PAYOFF + LOOP SCHLIESSEN (Ende)
- Versprechen einlösen
- Satisfying Conclusion
- Optional: Neuer Loop für nächstes Video

## Hook-Typen die funktionieren:
1. "Warum [kontraintuitives Statement]"
2. "Der größte Fehler bei [Topic]"
3. "[Zahl] Dinge die [Gruppe] nicht wissen"
4. "Was passiert wenn [Szenario]"
5. Story-Start: "Als ich [dramatisches Event]..."

## Red Flags (Watchtime Killer):
- Langsamer Start
- "Hey Leute, willkommen..."
- Zu viel Kontext vor dem Hook
- Monotone Energie
- Kein klarer Payoff
"""

PREMIERE_XML_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <sequence>
    <name>{clip_name}</name>
    <duration>{duration_frames}</duration>
    <rate>
      <timebase>{fps}</timebase>
      <ntsc>FALSE</ntsc>
    </rate>
    <media>
      <video>
        <track>
          <clipitem>
            <name>{clip_name}</name>
            <duration>{duration_frames}</duration>
            <start>{start_frame}</start>
            <end>{end_frame}</end>
            <in>{in_frame}</in>
            <out>{out_frame}</out>
            <file id="file-1">
              <name>{source_file}</name>
              <pathurl>file://{source_path}</pathurl>
            </file>
          </clipitem>
        </track>
      </video>
      <audio>
        <track>
          <clipitem>
            <name>{clip_name}_audio</name>
            <duration>{duration_frames}</duration>
            <start>{start_frame}</start>
            <end>{end_frame}</end>
            <in>{in_frame}</in>
            <out>{out_frame}</out>
            <file id="file-1"/>
          </clipitem>
        </track>
      </audio>
    </media>
  </sequence>
</xmeml>'''


class WatchtimeOptimizedExtractor:
    """
    Extract and restructure clips for maximum watchtime
    """
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        
        # Load learned patterns
        self.patterns = self._load_patterns()
        
        # Cache directory for transcripts
        self.cache_dir = Path("data/cache/transcripts")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directory
        self.output_dir = Path("output/clips")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Watchtime Optimizer initialized")
        if self.patterns:
            print(f"   📚 Loaded {len(self.patterns.get('extracted_patterns', []))} viral patterns")
        if self.client:
            print(f"   🤖 AI connected")
    
    def _load_patterns(self):
        """Load learned patterns from training"""
        patterns_file = Path("data/learned_patterns.json")
        
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                return json.load(f)
        return None
    
    def _get_file_hash(self, file_path):
        """Generate hash for file (for cache lookup)"""
        # Use file path + size for quick hash
        path = Path(file_path)
        if path.exists():
            stat = path.stat()
            hash_input = f"{path.name}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        return None
    
    def find_cached_transcript(self, video_path):
        """
        Look for cached transcript for this video
        
        Searches in data/cache/transcripts/ for matching files
        """
        
        video_path = Path(video_path)
        video_name = video_path.stem
        
        print(f"\n🔍 Looking for cached transcript...")
        print(f"   Video: {video_path.name}")
        
        # Strategy 1: Check by video name
        for cache_file in self.cache_dir.glob("*.json"):
            # Check if filename contains video name
            if video_name.lower() in cache_file.stem.lower():
                print(f"   ✅ Found by name: {cache_file}")
                return cache_file
        
        # Strategy 2: Check all cache files and look inside for matching source
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                # Check if this transcript matches our video
                source = data.get('source', '') or data.get('file', '') or ''
                if video_name.lower() in source.lower():
                    print(f"   ✅ Found by source: {cache_file}")
                    return cache_file
            except:
                continue
        
        # Strategy 3: Just list available cache files
        cache_files = list(self.cache_dir.glob("*.json"))
        if cache_files:
            print(f"\n   📦 Available cached transcripts ({len(cache_files)}):")
            for i, f in enumerate(cache_files[:10], 1):
                # Try to get preview
                try:
                    with open(f, 'r') as fh:
                        data = json.load(fh)
                        text = data.get('text', '')[:50] or str(data)[:50]
                        print(f"      {i}. {f.name}")
                        print(f"         Preview: {text}...")
                except:
                    print(f"      {i}. {f.name}")
            
            # Ask user to select
            choice = input(f"\n   Select transcript (1-{len(cache_files)}) or Enter to transcribe new: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(cache_files):
                selected = cache_files[int(choice) - 1]
                print(f"   ✅ Selected: {selected}")
                return selected
        
        print(f"   ❌ No cached transcript found")
        return None
    
    def load_transcript(self, transcript_path):
        """
        Load transcript with timestamps
        
        Supports:
        - JSON (Whisper format)
        - SRT
        - Plain text
        """
        
        path = Path(transcript_path)
        
        print(f"\n📝 Loading transcript: {path.name}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Handle different formats
        if 'segments' in data:
            # Whisper format
            segments = data['segments']
            print(f"   ✅ Loaded {len(segments)} segments (Whisper format)")
            return segments
        
        elif 'text' in data:
            # Simple text format - create pseudo-segments
            text = data['text']
            words = text.split()
            
            # Estimate ~2.5 words per second
            segments = []
            chunk_size = 25  # ~10 seconds per segment
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i+chunk_size]
                start = i / 2.5
                end = (i + len(chunk_words)) / 2.5
                
                segments.append({
                    'text': ' '.join(chunk_words),
                    'start': start,
                    'end': end
                })
            
            print(f"   ✅ Created {len(segments)} segments from text")
            return segments
        
        else:
            print(f"   ⚠️ Unknown format, trying to parse...")
            return [{'text': str(data), 'start': 0, 'end': 60}]
    
    def transcribe_video(self, video_path):
        """Transcribe video with Whisper and cache result"""
        
        print(f"\n🎤 Transcribing video with Whisper...")
        
        try:
            import whisper
            
            print("   Loading Whisper model (base)...")
            model = whisper.load_model("base")
            
            print("   Transcribing (this may take a few minutes)...")
            result = model.transcribe(str(video_path), language='de', verbose=False)
            
            # Cache the result
            video_hash = self._get_file_hash(video_path) or Path(video_path).stem
            cache_file = self.cache_dir / f"{video_hash}.json"
            
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Transcribed and cached: {cache_file}")
            
            return result['segments']
        
        except ImportError:
            print("   ❌ Whisper not installed. Run: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"   ❌ Transcription error: {e}")
            return None
    
    def extract_clips(self, transcript_segments, video_path=None, 
                     min_duration=30, max_duration=90, num_clips=10):
        """
        Main extraction pipeline
        
        Uses AI to find best moments and restructure for max watchtime
        """
        
        if not self.client:
            print("❌ No API key - cannot extract clips")
            return []
        
        print(f"\n{'='*70}")
        print("🎬 EXTRACTING WATCHTIME-OPTIMIZED CLIPS")
        print(f"{'='*70}")
        
        # Combine segments into full text with timestamps
        full_text = ""
        for seg in transcript_segments:
            full_text += f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}\n"
        
        total_duration = transcript_segments[-1]['end'] if transcript_segments else 0
        
        print(f"\n📊 Transcript Stats:")
        print(f"   Segments: {len(transcript_segments)}")
        print(f"   Duration: {total_duration/60:.1f} minutes")
        print(f"   Target: {num_clips} clips ({min_duration}-{max_duration}s each)")
        
        # Build patterns context
        patterns_context = ""
        if self.patterns:
            patterns_context = f"""
GELERNTE VIRAL PATTERNS (aus 972 erfolgreichen Clips):
{json.dumps(self.patterns.get('extracted_patterns', [])[:5], indent=2, ensure_ascii=False)}

WINNING HOOK PATTERNS:
{json.dumps(self.patterns.get('hook_patterns', {}), indent=2, ensure_ascii=False)}
"""
        
        prompt = f"""Du bist ein Elite-Editor für virale Short-Form Content.

{WATCHTIME_OPTIMIZATION}

{patterns_context}

---

LONGFORM TRANSCRIPT MIT TIMESTAMPS:
{full_text[:15000]}

---

AUFGABE:
1. Identifiziere die {num_clips} BESTEN Momente für Short-Form Clips
2. Für jeden Clip: Finde den stärksten HOOK (muss nicht am Anfang sein!)
3. RESTRUKTURIERE jeden Clip für maximale Watchtime:
   - Hook ZUERST (auch wenn es ursprünglich in der Mitte war)
   - Dann Context/Aufbau
   - Dann Payoff

WICHTIG:
- Clips sollten {min_duration}-{max_duration} Sekunden lang sein
- Der stärkste Moment/Satz wird zum HOOK
- Die Struktur darf vom Original abweichen!

Antworte in diesem JSON-Format:

{{
    "extracted_clips": [
        {{
            "clip_id": "clip_01",
            "title": "Kurzer, catchy Titel",
            "virality_score": 0.0-1.0,
            
            "original_segments": [
                {{
                    "text": "Originaltext des Segments",
                    "start": 123.4,
                    "end": 145.6
                }}
            ],
            
            "optimized_structure": {{
                "hook": {{
                    "text": "Der stärkste Satz/Moment",
                    "original_start": 130.2,
                    "original_end": 135.5,
                    "why_this_hook": "Erklärung warum das der Hook ist"
                }},
                "segments_order": [
                    {{
                        "role": "hook",
                        "start": 130.2,
                        "end": 135.5,
                        "text": "Hook text"
                    }},
                    {{
                        "role": "context", 
                        "start": 123.4,
                        "end": 130.2,
                        "text": "Context text"
                    }},
                    {{
                        "role": "payoff",
                        "start": 135.5,
                        "end": 145.6,
                        "text": "Payoff text"
                    }}
                ],
                "total_duration": 22.2,
                "restructure_notes": "Warum diese Struktur optimal ist"
            }},
            
            "predicted_performance": {{
                "hook_strength": 8,
                "retention_prediction": "high/medium/low",
                "viral_potential": "high/medium/low"
            }},
            
            "matched_patterns": ["Pattern 1", "Pattern 2"]
        }}
    ],
    
    "clips_summary": {{
        "total_clips": {num_clips},
        "average_virality": 0.75,
        "best_clip": "clip_01",
        "content_themes": ["Theme 1", "Theme 2"]
    }}
}}"""
        
        print("\n🧠 AI analyzing transcript for best moments...")
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                
                clips = result.get('extracted_clips', [])
                print(f"\n✅ Found {len(clips)} clips!")
                
                for clip in clips:
                    structure = clip.get('optimized_structure', {})
                    hook = structure.get('hook', {})
                    
                    print(f"\n   🎬 {clip['clip_id']}: {clip['title']}")
                    print(f"      Virality: {clip['virality_score']:.0%}")
                    print(f"      Duration: {structure.get('total_duration', 0):.1f}s")
                    print(f"      Hook: \"{hook.get('text', '')[:60]}...\"")
                    print(f"      Patterns: {', '.join(clip.get('matched_patterns', []))}")
                
                return result
            else:
                print("❌ Could not parse AI response")
                return None
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def export_clip(self, clip_data, source_video, output_name=None):
        """
        Export a single clip with reordered structure
        """
        
        clip_id = clip_data['clip_id']
        output_name = output_name or clip_id
        
        clip_dir = self.output_dir / output_name
        clip_dir.mkdir(parents=True, exist_ok=True)
        
        structure = clip_data.get('optimized_structure', {})
        segments = structure.get('segments_order', [])
        
        if not segments:
            print(f"   ⚠️ No segments for {clip_id}")
            return None
        
        print(f"\n📦 Exporting {clip_id}: {clip_data.get('title', '')}")
        
        # 1. Cut and concat segments with ffmpeg
        temp_files = []
        
        for i, seg in enumerate(segments):
            temp_file = clip_dir / f"temp_{i}.mp4"
            temp_files.append(temp_file)
            
            start = seg.get('start', 0)
            end = seg.get('end', start + 10)
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(source_video),
                '-ss', str(start),
                '-to', str(end),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-avoid_negative_ts', 'make_zero',
                str(temp_file),
                '-loglevel', 'error'
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Segment {i} cut failed")
                continue
        
        # 2. Create concat file
        concat_file = clip_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for temp_file in temp_files:
                if temp_file.exists():
                    f.write(f"file '{temp_file.absolute()}'\n")
        
        # 3. Concatenate
        output_mp4 = clip_dir / f"{output_name}.mp4"
        
        concat_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(output_mp4),
            '-loglevel', 'error'
        ]
        
        try:
            subprocess.run(concat_cmd, check=True, capture_output=True)
            print(f"   ✅ MP4: {output_mp4.name}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Concat failed: {e}")
        
        # Cleanup
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()
        if concat_file.exists():
            concat_file.unlink()
        
        # 4. Generate Premiere XML
        self._export_premiere_xml(clip_data, source_video, clip_dir, output_name)
        
        # 5. Save transcript
        self._export_transcript(clip_data, clip_dir, output_name)
        
        return clip_dir
    
    def _export_premiere_xml(self, clip_data, source_video, output_dir, name):
        """Generate Premiere Pro XML"""
        
        structure = clip_data.get('optimized_structure', {})
        fps = 30
        
        total_duration = structure.get('total_duration', 60)
        duration_frames = int(total_duration * fps)
        
        xml_content = PREMIERE_XML_TEMPLATE.format(
            clip_name=name,
            duration_frames=duration_frames,
            fps=fps,
            start_frame=0,
            end_frame=duration_frames,
            in_frame=0,
            out_frame=duration_frames,
            source_file=Path(source_video).name,
            source_path=str(Path(source_video).absolute())
        )
        
        xml_path = output_dir / f"{name}.xml"
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        
        print(f"   ✅ XML: {xml_path.name}")
    
    def _export_transcript(self, clip_data, output_dir, name):
        """Save clip transcript"""
        
        transcript = {
            'clip_id': clip_data['clip_id'],
            'title': clip_data.get('title', ''),
            'virality_score': clip_data.get('virality_score', 0),
            'structure': clip_data.get('optimized_structure', {}),
            'matched_patterns': clip_data.get('matched_patterns', []),
            'predicted_performance': clip_data.get('predicted_performance', {}),
            'exported_at': datetime.now().isoformat()
        }
        
        transcript_path = output_dir / f"{name}_transcript.json"
        with open(transcript_path, 'w') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Transcript: {transcript_path.name}")
    
    def process_video(self, video_path, num_clips=5, min_duration=30, max_duration=90):
        """
        Complete pipeline - just give it a video path!
        
        1. Auto-find cached transcript or transcribe
        2. Extract optimal clips
        3. Export all files
        """
        
        video_path = Path(video_path)
        
        if not video_path.exists():
            print(f"❌ Video not found: {video_path}")
            return None
        
        print(f"\n{'='*70}")
        print(f"🎬 PROCESSING: {video_path.name}")
        print(f"{'='*70}")
        
        # 1. Find or create transcript
        cached = self.find_cached_transcript(video_path)
        
        if cached:
            segments = self.load_transcript(cached)
        else:
            segments = self.transcribe_video(video_path)
        
        if not segments:
            print("❌ No transcript available")
            return None
        
        # 2. Extract clips
        result = self.extract_clips(
            segments,
            video_path,
            min_duration=min_duration,
            max_duration=max_duration,
            num_clips=num_clips
        )
        
        if not result:
            return None
        
        clips = result.get('extracted_clips', [])
        
        # 3. Export each clip
        print(f"\n{'='*70}")
        print(f"📦 EXPORTING {len(clips)} CLIPS")
        print(f"{'='*70}")
        
        for clip in clips:
            try:
                self.export_clip(clip, video_path)
            except Exception as e:
                print(f"   ⚠️ Error exporting {clip['clip_id']}: {e}")
        
        # 4. Save summary
        summary_path = self.output_dir / "extraction_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ COMPLETE!")
        print(f"{'='*70}")
        print(f"\n📁 Output: {self.output_dir}")
        print(f"   • {len(clips)} clips exported")
        print(f"   • Each clip has: MP4 + XML + Transcript")
        
        return result


def main():
    """Simple CLI - just enter video path"""
    
    print("="*70)
    print("🎬 WATCHTIME-OPTIMIZED CLIP EXTRACTOR v2")
    print("="*70)
    print("\n✨ Features:")
    print("   • Auto-finds cached transcripts")
    print("   • AI-powered clip extraction")
    print("   • Restructures for MAX watchtime")
    print("   • Exports MP4 + Premiere XML + Transcript")
    print("="*70)
    
    extractor = WatchtimeOptimizedExtractor()
    
    # Get video path
    video_path = input("\n📁 Video path: ").strip()
    
    if not video_path:
        print("❌ No video path provided")
        return
    
    # Get settings
    num_clips = input("🔢 Number of clips (default 5): ").strip()
    num_clips = int(num_clips) if num_clips else 5
    
    min_dur = input("⏱️  Min duration in seconds (default 30): ").strip()
    min_dur = int(min_dur) if min_dur else 30
    
    max_dur = input("⏱️  Max duration in seconds (default 90): ").strip()
    max_dur = int(max_dur) if max_dur else 90
    
    # Process
    extractor.process_video(
        video_path=video_path,
        num_clips=num_clips,
        min_duration=min_dur,
        max_duration=max_dur
    )


if __name__ == "__main__":
    main()
