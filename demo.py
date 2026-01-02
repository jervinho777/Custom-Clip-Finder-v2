#!/usr/bin/env python3
"""
Demo: Finde Clips in einem Video
"""

import sys
from pathlib import Path

def main():
    print("🎬 CLIP FINDER DEMO\n")
    
    # Check if video provided
    if len(sys.argv) < 2:
        print("Usage: python demo.py <video_path>")
        print("\nExample:")
        print("  python demo.py ~/Downloads/mein_video.mp4")
        print("\nOr place video in: ~/custom-clip-finder/data/uploads/test.mp4")
        print("  Then run: python demo.py data/uploads/test.mp4")
        sys.exit(1)
    
    video_path = Path(sys.argv[1]).expanduser()
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    print(f"📹 Video: {video_path.name}")
    print(f"   Size: {video_path.stat().st_size / (1024*1024):.1f} MB\n")
    
    # Import components
    from backend.processors.video_processor import VideoProcessor
    from backend.processors.transcriber import Transcriber
    
    # 1. Process Video
    print("=" * 60)
    print("STEP 1: Video Analysis")
    print("=" * 60)
    
    video_proc = VideoProcessor(str(video_path))
    
    print(f"\n📊 Metadata:")
    print(f"   Duration: {video_proc.metadata['duration']:.1f}s")
    print(f"   Resolution: {video_proc.metadata['width']}x{video_proc.metadata['height']}")
    print(f"   FPS: {video_proc.metadata['fps']:.1f}")
    print(f"   Has Audio: {video_proc.metadata['has_audio']}")
    
    # 2. Extract Audio
    print("\n" + "=" * 60)
    print("STEP 2: Audio Extraction")
    print("=" * 60 + "\n")
    
    audio_path = str(video_path).replace(video_path.suffix, '_audio.wav')
    video_proc.extract_audio(audio_path)
    
    # 3. Transcribe
    print("\n" + "=" * 60)
    print("STEP 3: Transcription (this takes a while...)")
    print("=" * 60 + "\n")
    
    transcriber = Transcriber(model_size="medium")
    transcript = transcriber.transcribe(audio_path, language="de")
    
    print(f"\n📝 Transcript Preview:")
    print(f"   Total text length: {len(transcript['text'])} chars")
    print(f"   Segments: {len(transcript['segments'])}")
    print(f"\n   First 200 chars:")
    print(f"   {transcript['text'][:200]}...")
    
    # 4. Scene Detection
    print("\n" + "=" * 60)
    print("STEP 4: Scene Detection")
    print("=" * 60 + "\n")
    
    scenes = video_proc.detect_scenes()
    
    print(f"Found {len(scenes)} scenes:")
    for i, (start, end) in enumerate(scenes[:5], 1):  # Show first 5
        duration = end - start
        print(f"   Scene {i}: {start:.1f}s - {end:.1f}s (Duration: {duration:.1f}s)")
    
    if len(scenes) > 5:
        print(f"   ... and {len(scenes)-5} more scenes")
    
    # 5. Simple Clip Suggestions
    print("\n" + "=" * 60)
    print("STEP 5: Clip Suggestions (Simple)")
    print("=" * 60 + "\n")
    
    # Find good starting points (scenes + keywords)
    viral_keywords = ['geheimnis', 'trick', 'tipp', 'warum', 'wie']
    
    suggestions = []
    
    for segment in transcript['segments'][:20]:  # First 20 segments
        text_lower = segment['text'].lower()
        
        # Check for viral keywords
        has_keyword = any(kw in text_lower for kw in viral_keywords)
        
        if has_keyword:
            suggestions.append({
                'start': segment['start'],
                'text': segment['text'][:100],
                'reason': 'Contains viral keyword'
            })
    
    print(f"Found {len(suggestions)} potential clips:\n")
    
    for i, sugg in enumerate(suggestions[:5], 1):
        print(f"{i}. Start: {sugg['start']:.1f}s")
        print(f"   Text: {sugg['text']}...")
        print(f"   Reason: {sugg['reason']}\n")
    
    # Summary
    print("=" * 60)
    print("✅ DEMO COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Fine-tune clip detection with ML model")
    print("  - Add feature extraction")
    print("  - Build full API")
    print(f"\nTranscript saved for review:")
    print(f"  Audio: {audio_path}")
    
    # Cleanup option
    print("\n🗑️  Cleanup?")
    cleanup = input("Delete temporary audio file? (y/n): ")
    if cleanup.lower() == 'y':
        Path(audio_path).unlink()
        print("Cleaned up!")

if __name__ == "__main__":
    main()
