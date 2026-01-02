#!/usr/bin/env python3
import sys
from pathlib import Path
from backend.processors.video_processor import VideoProcessor
from backend.ml.clip_finder import IntelligentClipFinder
from backend.utils.transcript_cache import TranscriptCache

def main():
    print("🤖 INTELLIGENT CLIP FINDER\n")
    
    if len(sys.argv) < 2:
        print("Usage: python demo_intelligent.py <video_path>")
        sys.exit(1)
    
    video_path = Path(sys.argv[1]).expanduser()
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    print(f"📹 Video: {video_path.name}")
    
    model_path = Path("data/models/custom_virality_model.pkl")
    if model_path.exists():
        print(f"✅ Using CUSTOM model (25 clips, 52M views)")
    
    print()
    
    print("🔧 Initializing...")
    clip_finder = IntelligentClipFinder()
    video_proc = VideoProcessor(str(video_path))
    cache = TranscriptCache()
    
    print("\n🎵 Extracting audio...")
    audio_path = str(video_path).replace(video_path.suffix, '_audio.wav')
    video_proc.extract_audio(audio_path)
    
    print("\n📝 Loading transcript...")
    transcript = cache.get(str(video_path))
    
    if transcript:
        print(f"   ✅ Cache hit! ({len(transcript['segments'])} segments)")
    else:
        print("   ⏳ Transcribing (first time, ~3 min)...")
        transcript = clip_finder.transcriber.transcribe(audio_path, language="de")
        cache.save(str(video_path), transcript)
        print(f"   ✅ Done! ({len(transcript['segments'])} segments)")
        print("   💾 Cached for next time")
    
    print("\n🤖 Finding clips...")
    clips = clip_finder.find_clips(
        video_path=str(video_path),
        audio_path=audio_path,
        transcript=transcript,
        min_duration=30,
        max_duration=90,
        top_n=10
    )
    
    print("\n" + "="*70)
    print("🏆 TOP CLIPS")
    print("="*70 + "\n")
    
    for i, clip in enumerate(clips, 1):
        print(f"CLIP #{i} - {clip['rating']}")
        print(f"Score: {clip['score']:.1f}/100")
        
        if 'predicted_engagement' in clip.get('explanation', {}):
            print(f"Predicted Engagement: {clip['explanation']['predicted_engagement']}")
        
        print(f"Time: {clip['start']:.1f}s - {clip['end']:.1f}s")
        print(f"Text: {clip['text'][:100]}...")
        
        if clip.get('strengths'):
            print("Strengths:", ", ".join(clip['strengths'][:3]))
        
        print()
    
    print("="*70)
    avg = sum(c['score'] for c in clips) / len(clips)
    print(f"Average: {avg:.1f} | Range: {clips[-1]['score']:.1f}-{clips[0]['score']:.1f}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
