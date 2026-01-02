#!/usr/bin/env python3
"""
Test viral clip with proper transcript extraction
"""

import asyncio
import json
from pathlib import Path
from create_clips_v4_integrated import CreateClipsV4Integrated


async def test_viral_clip():
    """Test the proven 2.4M views viral clip"""
    
    print("\n" + "="*70)
    print("🧪 VIRAL CLIP TEST - 2.4M VIEWS PROVEN")
    print("="*70)
    
    # Initialize
    v4 = CreateClipsV4Integrated()
    
    clip_path = Path("/Users/jervinquisada/custom-clip-finder/output/clips/Dieter Lange Viral Clip.mp4")
    
    if not clip_path.exists():
        print(f"❌ Clip not found!")
        return
    
    print(f"\n📹 Clip: {clip_path.name}")
    print(f"   Reality: 2.4M views ✅")
    
    # Step 1: Get transcript
    print(f"\n📝 Transcribing clip...")
    transcript_file = Path("data/cache/transcripts/viral_clip_transcript.json")
    
    if transcript_file.exists():
        print(f"   ✅ Loading cached transcript...")
        with open(transcript_file) as f:
            data = json.load(f)
            segments = data['segments']
    else:
        print(f"   🎙️  Creating new transcript...")
        segments = await v4._transcribe_with_assemblyai(clip_path)
        
        if segments:
            # Save it
            transcript_file.parent.mkdir(parents=True, exist_ok=True)
            with open(transcript_file, 'w') as f:
                json.dump({
                    'video_path': str(clip_path),
                    'segments': segments,
                    'service': 'assemblyai'
                }, f, indent=2)
            print(f"   ✅ Transcript saved!")
        else:
            print(f"   ❌ Transcription failed!")
            return
    
    print(f"   ✅ {len(segments)} segments")
    
    # Step 2: Create clip object
    duration = segments[-1]['end'] if segments else 30
    
    clip = {
        'start': 0,
        'end': duration,
        'segments': segments,
        'video_path': str(clip_path),
        'original_indices': list(range(len(segments)))
    }
    
    # Mock story
    story = {
        'storylines': [],
        'standalone_moments': []
    }
    
    # Step 3: Evaluate with FULL system
    print(f"\n" + "="*70)
    print(f"🔬 QUALITY EVALUATION - FULL SYSTEM")
    print(f"="*70)
    print(f"\n   🌌 Godmode: ON")
    print(f"   📚 Learnings: ON (175 clips)")
    print(f"   🎯 Threshold: 18/50")
    
    result = await v4._evaluate_quality_debate(clip, story)
    
    # Step 4: Show results
    print(f"\n" + "="*70)
    print(f"📊 RESULTS")
    print(f"="*70)
    
    score = result.get('total_score', result.get('score', 0))
    tier = result.get('quality_tier', result.get('tier', 'unknown'))
    passed = tier in ['A', 'B', 'C']
    confidence = result.get('consensus_confidence', result.get('confidence', 0))
    
    print(f"\n   🎯 SCORE: {score}/50")
    print(f"   📊 TIER: {tier}")
    print(f"   ✅ PASSED: {passed}")
    print(f"   🔍 CONFIDENCE: {confidence:.0%}")
    
    # Show reasoning
    consensus = result.get('consensus', '')
    if consensus:
        print(f"\n   📝 REASONING:")
        lines = consensus.split('\n')
        for line in lines[:20]:
            if line.strip():
                print(f"      {line[:100]}")
    
    # Validation
    validation = result.get('validation', {})
    if validation:
        print(f"\n   🔍 VALIDATION:")
        print(f"      Confidence: {validation.get('confidence', 0):.0%}")
        print(f"      Quality: {validation.get('quality_tier', 'unknown')}")
    
    # Final verdict
    print(f"\n" + "="*70)
    print(f"🎯 VERDICT")
    print(f"="*70)
    
    print(f"\n   REALITY: 2.4M views (TOP 0.1% outlier) ✅")
    print(f"   SYSTEM: {score}/50 ({tier}-tier) {'✅ PASS' if passed else '❌ REJECT'}")
    
    if passed:
        print(f"\n   ✅ SUCCESS! System correctly identified viral clip!")
        print(f"   System is working as expected!")
    else:
        print(f"\n   🚨 CRITICAL BUG!")
        print(f"   System REJECTS proven viral clip!")
        print(f"   → Godmode too brutal? Score: {score}/50")
        print(f"   → Learnings too strict?")
        print(f"   → Evaluation logic broken?")
        
        # Suggestions
        print(f"\n   💡 SUGGESTED FIXES:")
        if score < 15:
            print(f"      1. Disable Godmode (too brutal)")
            print(f"      2. Lower threshold to 12")
        elif score < 18:
            print(f"      1. Lower threshold to 15")
            print(f"      2. Reduce Godmode intensity")
        else:
            print(f"      1. Check why it didn't pass (score is {score})")
    
    return result


if __name__ == '__main__':
    asyncio.run(test_viral_clip())

