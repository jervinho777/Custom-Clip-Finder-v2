#!/usr/bin/env python3
"""
Export clips as MP4 + XML (Premiere Pro ready)
"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from backend.processors.video_processor import VideoProcessor
from backend.processors.transcriber import Transcriber
from backend.processors.feature_extractor import FeatureExtractor
from backend.ml.models.virality_predictor import ViralityPredictor
from backend.ai.content_restructurer import ContentRestructurer
from backend.utils.transcript_cache import TranscriptCache

def create_premiere_xml(variant, output_path, video_file, clip_duration):
    """
    Create Premiere Pro XML with markers and captions
    """
    
    # Get sentences with timing
    sentences = variant['structure']
    
    # Build XML
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
  <sequence id="sequence-1">
    <name>{variant['name']}</name>
    <duration>{int(clip_duration * 30)}</duration>
    <rate>
      <timebase>30</timebase>
      <ntsc>FALSE</ntsc>
    </rate>
    
    <media>
      <video>
        <track>
          <clipitem id="clipitem-1">
            <name>{Path(video_file).name}</name>
            <start>{int(sentences[0]['start'] * 30)}</start>
            <end>{int(sentences[-1]['end'] * 30)}</end>
            <in>{int(sentences[0]['start'] * 30)}</in>
            <out>{int(sentences[-1]['end'] * 30)}</out>
            
            <file id="file-1">
              <name>{Path(video_file).name}</name>
              <pathurl>file://localhost/{Path(video_file).absolute()}</pathurl>
              <rate>
                <timebase>30</timebase>
              </rate>
              <duration>{int(clip_duration * 30)}</duration>
            </file>
"""
    
    # Add markers for each sentence
    xml += "            <marker>\n"
    
    for i, sent in enumerate(sentences, 1):
        marker_time = int(sent['start'] * 30)
        xml += f"""              <marker>
                <name>Sentence {i}</name>
                <comment>{sent['text'][:100]}</comment>
                <in>{marker_time}</in>
                <out>{marker_time + int(sent['duration'] * 30)}</out>
              </marker>
"""
    
    xml += """            </marker>
          </clipitem>
        </track>
      </video>
      
      <audio>
        <track>
          <clipitem id="clipitem-audio-1">
            <name>{Path(video_file).name}</name>
            <start>{int(sentences[0]['start'] * 30)}</start>
            <end>{int(sentences[-1]['end'] * 30)}</end>
            <in>{int(sentences[0]['start'] * 30)}</in>
            <out>{int(sentences[-1]['end'] * 30)}</out>
            <file id="file-1"/>
          </clipitem>
        </track>
      </audio>
    </media>
    
    <!-- Metadata -->
    <logginginfo>
      <description>
AI Generated Clip
Strategy: {variant.get('strategy', 'N/A')}
Predicted Retention: {variant.get('predicted_retention', 'N/A')}%
Duration: {clip_duration:.1f}s
Sentences: {len(sentences)}

Hook Strategy:
{variant.get('hook_strategy', 'N/A')}

Strengths:
{chr(10).join('- ' + s for s in variant.get('strengths', []))}

Risks:
{chr(10).join('- ' + r for r in variant.get('risks', []))}
      </description>
    </logginginfo>
  </sequence>
</xmeml>
"""
    
    # Save XML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml)

def create_captions_srt(variant, output_path):
    """
    Create SRT captions file
    """
    
    sentences = variant['structure']
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, sent in enumerate(sentences, 1):
            start_time = format_srt_time(sent['start'])
            end_time = format_srt_time(sent['end'])
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{sent['text']}\n\n")

def format_srt_time(seconds):
    """Format seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def create_metadata_json(variant, output_path):
    """
    Create JSON metadata file
    """
    
    metadata = {
        'name': variant['name'],
        'strategy': variant.get('strategy', ''),
        'hook_strategy': variant.get('hook_strategy', ''),
        'predicted_retention': variant.get('predicted_retention', 0),
        'duration': variant['total_duration'],
        'sentence_count': variant['sentence_count'],
        'strengths': variant.get('strengths', []),
        'risks': variant.get('risks', []),
        'ai_generated': variant.get('ai_generated', False),
        'sentences': [
            {
                'text': s['text'],
                'start': s['start'],
                'end': s['end'],
                'duration': s['duration'],
                'type': s['type'],
                'ml_score': s['ml_score']
            } for s in variant['structure']
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) < 2:
        print("Usage: python export_clips_with_xml.py <video_path> [--auto-export]")
        sys.exit(1)
    
    video_path = Path(sys.argv[1]).expanduser()
    auto_export = '--auto-export' in sys.argv
    
    print("🎬 FULL EXPORT: MP4 + XML + SRT + JSON\n")
    
    # Initialize
    print("🔧 Initializing...")
    video_proc = VideoProcessor(str(video_path))
    cache = TranscriptCache()
    feature_extractor = FeatureExtractor()
    predictor = ViralityPredictor()
    restructurer = ContentRestructurer(predictor, feature_extractor)
    
    if not restructurer.has_claude:
        print("❌ Claude not available")
        sys.exit(1)
    
    # Get transcript
    print("\n📝 Loading transcript...")
    audio_path = str(video_path).replace(video_path.suffix, '_audio.wav')
    video_proc.extract_audio(audio_path)
    
    transcript = cache.get(str(video_path))
    if not transcript:
        transcriber = Transcriber(model_size="medium")
        transcript = transcriber.transcribe(audio_path, language="de")
        cache.save(str(video_path), transcript)
    
    # AI Analysis
    print("\n🤖 AI Analysis...")
    sentences = restructurer.analyze_sentences(transcript, audio_path)
    variants = restructurer.build_clip_variants(sentences, (45, 60))
    
    print(f"\n✅ Generated {len(variants)} clips")
    
    # Export confirmation
    if not auto_export:
        export = input("\n💾 Export all clips? (y/n): ")
        if export.lower() != 'y':
            return
    
    # Export
    print(f"\n🎬 EXPORTING {len(variants)} CLIPS...")
    print("   Each clip gets: MP4 + XML + SRT + JSON\n")
    
    output_dir = Path("data/outputs/clips") / video_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exported = []
    
    for i, variant in enumerate(variants, 1):
        try:
            structure = variant['structure']
            start_time = structure[0]['start']
            end_time = structure[-1]['end']
            duration = end_time - start_time
            
            # Create clean filename
            retention = variant.get('predicted_retention', 0)
            base_name = f"clip{i:02d}_ret{retention:.0f}_{variant['name'][:25]}"
            base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))
            base_name = base_name.replace(' ', '_')
            
            # File paths
            mp4_file = output_dir / f"{base_name}.mp4"
            xml_file = output_dir / f"{base_name}.xml"
            srt_file = output_dir / f"{base_name}.srt"
            json_file = output_dir / f"{base_name}.json"
            
            print(f"[{i}/{len(variants)}] {base_name[:50]}")
            
            # 1. Export MP4
            print(f"   MP4...", end=' ')
            video_proc.create_clip(
                start_time=start_time,
                duration=duration,
                output_path=str(mp4_file)
            )
            print("✅")
            
            # 2. Create XML
            print(f"   XML...", end=' ')
            create_premiere_xml(variant, xml_file, video_path, duration)
            print("✅")
            
            # 3. Create SRT
            print(f"   SRT...", end=' ')
            create_captions_srt(variant, srt_file)
            print("✅")
            
            # 4. Create JSON
            print(f"   JSON...", end=' ')
            create_metadata_json(variant, json_file)
            print("✅")
            
            exported.append({
                'name': base_name,
                'mp4': str(mp4_file),
                'xml': str(xml_file),
                'srt': str(srt_file),
                'json': str(json_file),
                'retention': retention,
                'duration': duration
            })
            
            print()
            
        except Exception as e:
            print(f"   ❌ Failed: {e}\n")
    
    # Summary
    print("="*70)
    print("✅ EXPORT COMPLETE")
    print("="*70)
    print(f"Exported: {len(exported)}/{len(variants)} clips")
    print(f"Location: {output_dir}")
    print(f"\nEach clip includes:")
    print(f"  • MP4 (video file)")
    print(f"  • XML (Premiere Pro project)")
    print(f"  • SRT (captions)")
    print(f"  • JSON (metadata)")
    
    # Create master manifest
    manifest_file = output_dir / "_MANIFEST.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump({
            'video_source': str(video_path),
            'total_clips': len(variants),
            'exported': len(exported),
            'export_date': str(Path.cwd()),
            'clips': exported
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Master manifest: {manifest_file}")
    print(f"\n🎯 Ready for editing in Premiere Pro!")

if __name__ == "__main__":
    main()
