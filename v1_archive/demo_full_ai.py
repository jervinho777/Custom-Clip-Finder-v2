#!/usr/bin/env python3
"""
Full AI-Powered Clip Finder
ML Analysis + Claude Strategic Structuring for EVERY video
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
    print("🤖 FULL AI-POWERED CLIP FINDER")
    print("ML + Claude AI for maximum quality\n")
    
    if len(sys.argv) < 2:
        print("Usage: python demo_full_ai.py <video_path>")
        sys.exit(1)
    
    video_path = Path(sys.argv[1]).expanduser()
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    print(f"📹 Video: {video_path.name}")
    print(f"💰 Cost: ~$0.08 (Full AI Analysis)")
    print()
    
    # Initialize systems
    print("🔧 Initializing AI systems...")
    video_proc = VideoProcessor(str(video_path))
    cache = TranscriptCache()
    feature_extractor = FeatureExtractor()
    predictor = ViralityPredictor()
    
    # Check Claude availability
    restructurer = ContentRestructurer(predictor, feature_extractor)
    
    if not restructurer.has_claude:
        print("❌ Claude API not available")
        print("   Add ANTHROPIC_API_KEY to .env")
        sys.exit(1)
    
    print("✅ Claude AI connected")
    
    # Extract audio
    print("\n🎵 Extracting audio...")
    audio_path = str(video_path).replace(video_path.suffix, '_audio.wav')
    video_proc.extract_audio(audio_path)
    
    # Get transcript
    print("\n📝 Loading transcript...")
    transcript = cache.get(str(video_path))
    
    if transcript:
        print(f"   ✅ Cached ({len(transcript['segments'])} segments)")
    else:
        print("   Transcribing...")
        transcriber = Transcriber(model_size="medium")
        transcript = transcriber.transcribe(audio_path, language="de")
        cache.save(str(video_path), transcript)
        print(f"   ✅ Done ({len(transcript['segments'])} segments)")
    
    # PHASE 1: ML Sentence Analysis
    print("\n" + "="*70)
    print("PHASE 1: ML ANALYSIS")
    print("="*70)
    
    sentences = restructurer.analyze_sentences(transcript, audio_path)
    
    print(f"\n📊 Analyzed {len(sentences)} sentences")
    print(f"\n🏆 Top 10 Sentences by ML Score:\n")
    
    for i, sent in enumerate(sentences[:10], 1):
        print(f"{i}. Score: {sent['ml_score']:.1f} | Type: {sent['type']}")
        print(f"   {sent['text'][:70]}...")
        print()
    
    # PHASE 2: AI Strategic Building
    print("="*70)
    print("PHASE 2: CLAUDE AI STRATEGIC ANALYSIS")
    print("="*70)
    
    print("\n🧠 Claude is analyzing and building optimal structures...")
    print("   (This will cost ~$0.08)\n")
    
    variants = restructurer.build_clip_variants(
        sentences,
        target_duration=(45, 60)
    )
    
    if not variants:
        print("❌ No variants generated")
        return
    
    # Display AI-Generated Variants
    print("\n" + "="*70)
    print("🎬 CLAUDE AI CLIP VARIANTS")
    print("="*70)
    
    for i, variant in enumerate(variants, 1):
        print(f"\n{'='*70}")
        print(f"VARIANT #{i}: {variant['name']}")
        print(f"{'='*70}")
        
        if variant.get('ai_generated'):
            print(f"🤖 AI Model: {variant.get('ai_model', 'claude')}")
        
        print(f"\n📊 Metrics:")
        print(f"   Duration: {variant['total_duration']:.1f}s")
        print(f"   Sentences: {variant['sentence_count']}")
        print(f"   Predicted Retention: {variant.get('predicted_retention', 'N/A')}%")
        
        if variant.get('strategy'):
            print(f"\n💡 Strategy:")
            print(f"   {variant['strategy']}")
        
        if variant.get('hook_strategy'):
            print(f"\n🎣 Hook Strategy:")
            print(f"   {variant['hook_strategy']}")
        
        if variant.get('flow_explanation'):
            print(f"\n📈 Flow:")
            print(f"   {variant['flow_explanation']}")
        
        print(f"\n📝 Structure ({variant['sentence_count']} sentences):")
        for j, sent in enumerate(variant['structure'][:5], 1):
            print(f"   {j}. [{sent['type']}] {sent['text'][:60]}...")
        
        if len(variant['structure']) > 5:
            print(f"   ... and {len(variant['structure']) - 5} more sentences")
        
        if variant.get('strengths'):
            print(f"\n✅ Strengths:")
            for strength in variant['strengths']:
                print(f"   • {strength}")
        
        if variant.get('risks'):
            print(f"\n⚠️  Risks:")
            for risk in variant['risks']:
                print(f"   • {risk}")
        
        print()
    
    # Summary
    print("="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Variants generated: {len(variants)}")
    print(f"Best predicted retention: {max(v.get('predicted_retention', 0) for v in variants)}%")
    print(f"Total sentences analyzed: {len(sentences)}")
    print(f"AI-powered variants: {sum(1 for v in variants if v.get('ai_generated'))}")
    
    # Cost tracking
    print("\n💰 Cost Tracking:")
    try:
        from backend.ai.claude_strategist import ClaudeStrategist
        from dotenv import load_dotenv
        load_dotenv()
        
        claude = ClaudeStrategist()
        stats = claude.get_usage_stats()
        
        print(f"   This call: ~$0.08")
        print(f"   Total today: ${stats['total_cost']:.2f}")
        print(f"   Est. monthly (800 videos): ${stats['estimated_monthly_cost']:.2f}")
    except:
        pass
    
    print("\n✅ Full AI Analysis Complete!")
    print("\n📚 Next: Export best variant as video clip")

if __name__ == "__main__":
    main()
