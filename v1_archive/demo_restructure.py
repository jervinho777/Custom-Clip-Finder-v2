#!/usr/bin/env python3
"""
Demo: Content Restructuring with ML + AI
"""

import sys
from pathlib import Path
from backend.processors.video_processor import VideoProcessor
from backend.processors.transcriber import Transcriber
from backend.processors.feature_extractor import FeatureExtractor
from backend.ml.models.virality_predictor import ViralityPredictor
from backend.ai.content_restructurer import ContentRestructurer
from backend.utils.transcript_cache import TranscriptCache

def main():
    print("🤖 INTELLIGENT CONTENT RESTRUCTURER\n")
    print("ML Pattern Recognition + AI Strategic Thinking\n")
    
    if len(sys.argv) < 2:
        print("Usage: python demo_restructure.py <video_path>")
        sys.exit(1)
    
    video_path = Path(sys.argv[1]).expanduser()
    
    if not video_path.exists():
        print(f"❌ Video not found")
        sys.exit(1)
    
    print(f"📹 Video: {video_path.name}\n")
    
    # Initialize
    print("🔧 Initializing systems...")
    video_proc = VideoProcessor(str(video_path))
    transcriber = Transcriber(model_size="medium")
    feature_extractor = FeatureExtractor()
    predictor = ViralityPredictor()
    cache = TranscriptCache()
    
    # Extract audio
    print("\n🎵 Extracting audio...")
    audio_path = str(video_path).replace(video_path.suffix, '_audio.wav')
    video_proc.extract_audio(audio_path)
    
    # Transcript
    print("\n📝 Loading transcript...")
    transcript = cache.get(str(video_path))
    
    if not transcript:
        print("   Transcribing...")
        transcript = transcriber.transcribe(audio_path, language="de")
        cache.save(str(video_path), transcript)
    else:
        print(f"   ✅ Cached ({len(transcript['segments'])} segments)")
    
    # Initialize Restructurer
    restructurer = ContentRestructurer(predictor, feature_extractor)
    
    # PHASE 1: ML Analysis
    print("\n" + "="*70)
    print("PHASE 1: ML SENTENCE ANALYSIS")
    print("="*70)
    
    sentences = restructurer.analyze_sentences(transcript, audio_path)
    
    print(f"\n📊 Top 10 Sentences by ML Score:\n")
    for i, sent in enumerate(sentences[:10], 1):
        print(f"{i}. Score: {sent['ml_score']:.1f} | Type: {sent['type']}")
        print(f"   {sent['text'][:80]}...")
        print()
    
    # PHASE 2: AI Structure Building
    print("="*70)
    print("PHASE 2: AI CLIP CONSTRUCTION")
    print("="*70)
    
    variants = restructurer.build_clip_variants(sentences, target_duration=(45, 60))
    
    print(f"\n🎬 Built {len(variants)} clip variants:\n")
    
    for i, variant in enumerate(variants, 1):
        print(f"{'='*70}")
        print(f"VARIANT #{i}: {variant['name']}")
        print(f"{'='*70}")
        print(f"Duration: {variant['total_duration']:.1f}s")
        print(f"Sentences: {variant['sentence_count']}")
        print(f"Predicted Watchtime: {variant['predicted_watchtime']:.1f}%")
        print(f"\nStructure:")
        
        for j, sent in enumerate(variant['structure'], 1):
            print(f"  {j}. [{sent['type']}] {sent['text'][:60]}...")
        
        print()
    
    print("="*70)
    print("✅ Analysis complete!")
    print("\nNext: Export best variant as video clip")

if __name__ == "__main__":
    main()
