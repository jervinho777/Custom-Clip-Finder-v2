#!/usr/bin/env python3
"""
Test if Restructure step damages viral clips
"""

import asyncio
import json
from pathlib import Path
from create_clips_v4_integrated import CreateClipsV4Integrated


async def test_restructure_impact():
    """Compare viral clip before and after restructure"""
    
    print("\n" + "="*70)
    print("🧪 RESTRUCTURE IMPACT TEST")
    print("="*70)
    
    # Initialize
    v4 = CreateClipsV4Integrated()
    
    # Load viral clip transcript
    transcript_file = Path("data/cache/transcripts/viral_clip_transcript.json")
    
    if not transcript_file.exists():
        print("❌ Run test_viral_clip_complete.py first to create transcript!")
        return
    
    with open(transcript_file) as f:
        data = json.load(f)
        segments = data['segments']
    
    print(f"\n📝 Loaded transcript: {len(segments)} segments")
    
    # Create ORIGINAL clip (no restructure)
    duration = segments[-1]['end'] if segments else 30
    
    original_clip = {
        'start': 0,
        'end': duration,
        'segments': segments,
        'video_path': '/Users/jervinquisada/custom-clip-finder/output/clips/Dieter Lange Viral Clip.mp4',
        'original_indices': list(range(len(segments)))
    }
    
    story = {'storylines': [], 'standalone_moments': []}
    
    # TEST 1: ORIGINAL (NO RESTRUCTURE)
    print("\n" + "="*70)
    print("📊 TEST 1: ORIGINAL CLIP (No Restructure)")
    print("="*70)
    
    result_original = await v4._evaluate_quality_debate(original_clip, story)
    
    score_original = result_original.get('total_score', result_original.get('score', 0))
    tier_original = result_original.get('quality_tier', result_original.get('tier', 'unknown'))
    passed_original = tier_original in ['A', 'B', 'C']
    confidence_original = result_original.get('consensus_confidence', result_original.get('confidence', 0))
    
    print(f"\n   🎯 ORIGINAL CLIP:")
    print(f"      Score: {score_original}/50")
    print(f"      Tier: {tier_original}")
    print(f"      Passed: {passed_original}")
    print(f"      Confidence: {confidence_original:.0%}")
    
    # TEST 2: RESTRUCTURED
    print("\n" + "="*70)
    print("📊 TEST 2: RESTRUCTURED CLIP")
    print("="*70)
    
    print(f"\n   🔄 Running restructure...")
    
    # Create a moment from the clip
    moment = {
        'id': 1,
        'start': original_clip['start'],
        'end': original_clip['end'],
        'topic': 'Viral clip test',
        'strength': 'high',
        'reason': 'Proven 2.4M views'
    }
    
    # Run restructure (uses _restructure_with_review)
    restructured_clip = await v4._restructure_with_review(
        moment,
        segments,
        story
    )
    
    if not restructured_clip:
        print(f"   ❌ Restructure failed!")
        return
    
    # Get segments from restructured clip
    restructured_segments = []
    if 'structure' in restructured_clip:
        restructured_segments = restructured_clip['structure'].get('segments', [])
    elif 'segments' in restructured_clip:
        restructured_segments = restructured_clip['segments']
    
    print(f"   ✅ Restructured!")
    print(f"      Original segments: {len(original_clip['segments'])}")
    print(f"      Restructured segments: {len(restructured_segments)}")
    
    # Create clip dict for evaluation
    restructured_clip_for_eval = {
        'start': restructured_clip.get('start', 0),
        'end': restructured_clip.get('end', duration),
        'segments': restructured_segments,
        'video_path': original_clip['video_path'],
        'structure': restructured_clip.get('structure', {})
    }
    
    # Evaluate restructured
    print(f"\n   🔬 Evaluating restructured clip...")
    
    result_restructured = await v4._evaluate_quality_debate(restructured_clip_for_eval, story)
    
    score_restructured = result_restructured.get('total_score', result_restructured.get('score', 0))
    tier_restructured = result_restructured.get('quality_tier', result_restructured.get('tier', 'unknown'))
    passed_restructured = tier_restructured in ['A', 'B', 'C']
    confidence_restructured = result_restructured.get('consensus_confidence', result_restructured.get('confidence', 0))
    
    print(f"\n   🎯 RESTRUCTURED CLIP:")
    print(f"      Score: {score_restructured}/50")
    print(f"      Tier: {tier_restructured}")
    print(f"      Passed: {passed_restructured}")
    print(f"      Confidence: {confidence_restructured:.0%}")
    
    # COMPARISON
    print("\n" + "="*70)
    print("📊 IMPACT ANALYSIS")
    print("="*70)
    
    score_delta = score_restructured - score_original
    
    print(f"\n   ORIGINAL:     {score_original}/50 ({tier_original}-tier) {'✅ PASS' if passed_original else '❌ REJECT'}")
    print(f"   RESTRUCTURED: {score_restructured}/50 ({tier_restructured}-tier) {'✅ PASS' if passed_restructured else '❌ REJECT'}")
    print(f"   DELTA:        {score_delta:+.1f} points")
    
    # Verdict
    print("\n" + "="*70)
    print("🎯 VERDICT")
    print("="*70)
    
    if score_delta > 2:
        print(f"\n   ✅ RESTRUCTURE IMPROVES!")
        print(f"      +{score_delta:.1f} points improvement")
        print(f"      Restructure is HELPING viral potential!")
    
    elif score_delta < -2:
        print(f"\n   🚨 RESTRUCTURE DESTROYS!")
        print(f"      {score_delta:.1f} points LOSS")
        print(f"      Restructure is DAMAGING viral clips!")
        print(f"\n   💡 SOLUTION:")
        print(f"      - Skip restructure for high-scoring clips")
        print(f"      - Or use different restructure strategy")
        print(f"      - Or keep original structure")
    
    else:
        print(f"\n   ≈ RESTRUCTURE NEUTRAL")
        print(f"      Delta: {score_delta:.1f} points (minimal impact)")
        print(f"      Restructure neither helps nor hurts")
    
    # Show reasoning comparison
    print("\n" + "="*70)
    print("📝 REASONING COMPARISON")
    print("="*70)
    
    reasoning_orig = result_original.get('reasoning', {})
    if isinstance(reasoning_orig, dict):
        strengths_orig = reasoning_orig.get('strengths', [])
        weaknesses_orig = reasoning_orig.get('weaknesses', [])
    else:
        strengths_orig = []
        weaknesses_orig = []
    
    print(f"\n   ORIGINAL STRENGTHS:")
    if strengths_orig:
        for s in strengths_orig[:3]:
            print(f"      • {s[:100]}...")
    else:
        print(f"      (No strengths listed)")
    
    reasoning_restr = result_restructured.get('reasoning', {})
    if isinstance(reasoning_restr, dict):
        strengths_restr = reasoning_restr.get('strengths', [])
        weaknesses_restr = reasoning_restr.get('weaknesses', [])
    else:
        strengths_restr = []
        weaknesses_restr = []
    
    print(f"\n   RESTRUCTURED STRENGTHS:")
    if strengths_restr:
        for s in strengths_restr[:3]:
            print(f"      • {s[:100]}...")
    else:
        print(f"      (No strengths listed)")
    
    print(f"\n   ORIGINAL WEAKNESSES:")
    if weaknesses_orig:
        for w in weaknesses_orig[:3]:
            print(f"      • {w[:100]}...")
    else:
        print(f"      (No weaknesses listed)")
    
    print(f"\n   RESTRUCTURED WEAKNESSES:")
    if weaknesses_restr:
        for w in weaknesses_restr[:3]:
            print(f"      • {w[:100]}...")
    else:
        print(f"      (No weaknesses listed)")


if __name__ == '__main__':
    asyncio.run(test_restructure_impact())

