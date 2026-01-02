#!/usr/bin/env python3
"""
Export RESTRUCTURED clips - only selected sentences!
"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import subprocess
from typing import List, Dict

from backend.processors.video_processor import VideoProcessor
from backend.processors.transcriber import Transcriber
from backend.processors.feature_extractor import FeatureExtractor
from backend.ml.models.virality_predictor import ViralityPredictor
from backend.ai.content_restructurer import ContentRestructurer
from backend.utils.transcript_cache import TranscriptCache

def create_restructured_clip(video_path: str, sentences: List[Dict], output_path: str):
    """
    Create clip with ONLY selected sentences (cut out everything else)
    """
    
    # Create temp files for each sentence
    temp_dir = Path("data/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    segment_files = []
    
    print(f"   Extracting {len(sentences)} segments...")
    
    for i, sent in enumerate(sentences):
        segment_file = temp_dir / f"segment_{i:03d}.mp4"
        
        # Extract just this sentence
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-ss', str(sent['start']),
            '-t', str(sent['duration']),
            '-c', 'copy',
            '-avoid_negative_ts', '1',
            str(segment_file)
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        segment_files.append(segment_file)
    
    # Create concat file
    concat_file = temp_dir / "concat_list.txt"
    with open(concat_file, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg.absolute()}'\n")
    
    print(f"   Concatenating segments...")
    
    # Concatenate all segments
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Cleanup temp files
    for seg in segment_files:
        seg.unlink()
    concat_file.unlink()
    
    print(f"   ✅ Created restructured clip")

def create_xml_for_restructured(variant, output_path, mp4_path):
    """
    Create XML with info about restructuring
    """
    
    sentences = variant['structure']
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
  <sequence id="sequence-1">
    <name>{variant['name']}</name>
    
    <!-- RESTRUCTURED CLIP -->
    <!-- Original sentences stitched together -->
    
    <logginginfo>
      <description>
🎬 AI RESTRUCTURED CLIP

Strategy: {variant.get('strategy', 'N/A')}
Predicted Retention: {variant.get('predicted_retention', 'N/A')}%
Total Duration: {variant['total_duration']:.1f}s
Segments: {len(sentences)}

Hook Strategy:
{variant.get('hook_strategy', 'N/A')}

Structure (in order):
{chr(10).join(f"{i+1}. [{s['type']}] {s['text'][:80]}..." for i, s in enumerate(sentences))}

Strengths:
{chr(10).join('• ' + s for s in variant.get('strengths', []))}

Risks:
{chr(10).join('• ' + r for r in variant.get('risks', []))}

---
This clip was created by:
1. AI selected {len(sentences)} key sentences
2. Extracted each sentence separately
3. Stitched them together in optimal order
4. Cut out all filler content between sentences
      </description>
    </logginginfo>
  </sequence>
</xmeml>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml)

def main():
    if len(sys.argv) < 2:
        print("Usage: python export_clips_restructured.py <video_path> [--auto-export]")
        sys.exit(1)
    
    video_path = Path(sys.argv[1]).expanduser()
    auto_export = '--auto-export' in sys.argv
    
    print("🎬 RESTRUCTURED CLIP EXPORT")
    print("   Cuts out filler, keeps only AI-selected sentences\n")
    
    # Initialize
    print("🔧 Initializing...")
    cache = TranscriptCache()
    feature_extractor = FeatureExtractor()
    predictor = ViralityPredictor()
    restructurer = ContentRestructurer(predictor, feature_extractor)
    
    if not restructurer.has_claude:
        print("❌ Claude not available")
        sys.exit(1)
    
    # Get transcript
    print("\n📝 Loading transcript...")
    video_proc = VideoProcessor(str(video_path))
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
    
    print(f"\n✅ Generated {len(variants)} restructured clips")
    
    # Show what will be done
    print("\n📋 Example (Clip #1):")
    example = variants[0]
    print(f"   Name: {example['name']}")
    print(f"   Segments: {len(example['structure'])}")
    print(f"   Total: {example['total_duration']:.1f}s (from {len(example['structure'])} separate parts)")
    print(f"\n   Structure:")
    for i, s in enumerate(example['structure'][:5], 1):
        print(f"   {i}. {s['text'][:60]}...")
    if len(example['structure']) > 5:
        print(f"   ... and {len(example['structure']) - 5} more segments")
    
    # Confirm
    if not auto_export:
        print("\n⚠️  This will:")
        print("   1. Extract each selected sentence separately")
        print("   2. Stitch them together in new order")
        print("   3. Cut out all filler between sentences")
        export = input("\nProceed? (y/n): ")
        if export.lower() != 'y':
            return
    
    # Export
    print(f"\n🎬 EXPORTING {len(variants)} RESTRUCTURED CLIPS...")
    print("   This takes longer - creating actual cuts!\n")
    
    output_dir = Path("data/outputs/clips") / video_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exported = []
    
    for i, variant in enumerate(variants, 1):
        try:
            retention = variant.get('predicted_retention', 0)
            base_name = f"clip{i:02d}_ret{retention:.0f}_{variant['name'][:25]}"
            base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))
            base_name = base_name.replace(' ', '_')
            
            mp4_file = output_dir / f"{base_name}.mp4"
            xml_file = output_dir / f"{base_name}.xml"
            json_file = output_dir / f"{base_name}.json"
            
            print(f"[{i}/{len(variants)}] {base_name[:50]}")
            print(f"   Creating {len(variant['structure'])} cuts...")
            
            # Create restructured clip
            create_restructured_clip(
                str(video_path),
                variant['structure'],
                str(mp4_file)
            )
            
            # Create XML
            create_xml_for_restructured(variant, xml_file, mp4_file)
            
            # Create JSON metadata
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'name': variant['name'],
                    'strategy': variant.get('strategy', ''),
                    'predicted_retention': variant.get('predicted_retention', 0),
                    'duration': variant['total_duration'],
                    'segments': len(variant['structure']),
                    'structure': [
                        {
                            'text': s['text'],
                            'type': s['type'],
                            'original_time': f"{s['start']:.1f}s"
                        } for s in variant['structure']
                    ]
                }, f, indent=2, ensure_ascii=False)
            
            exported.append(base_name)
            print()
            
        except Exception as e:
            print(f"   ❌ Failed: {e}\n")
    
    # Summary
    print("="*70)
    print("✅ EXPORT COMPLETE")
    print("="*70)
    print(f"Exported: {len(exported)}/{len(variants)} restructured clips")
    print(f"Location: {output_dir}")
    print(f"\n🎯 Each clip:")
    print(f"   • Only contains AI-selected sentences")
    print(f"   • Filler content removed")
    print(f"   • Optimized structure for retention")
    print(f"\n📁 Files: MP4 + XML + JSON")

if __name__ == "__main__":
    main()
