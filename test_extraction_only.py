#!/usr/bin/env python3
"""
ULTRA FAST - Extraction validation only (30 sec, $0)

Shows moment extraction results WITHOUT evaluation
Perfect for rapid iteration!
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
import sys
import hashlib

sys.path.insert(0, str(Path(__file__).parent))

from create_clips_v4_integrated import CreateClipsV4Integrated


async def validate_extraction(video_path: str):
    """Test extraction logic only - instant feedback"""
    
    print(f"\n{'='*70}")
    print(f"⚡ EXTRACTION VALIDATOR - Ultra Fast")
    print(f"{'='*70}")
    print(f"\n   Video: {Path(video_path).name}")
    print(f"   Mode: Extraction validation only (NO AI calls)")
    
    # Load transcript
    video_file = Path(video_path)
    transcript_file = Path(f"data/cache/transcripts/{video_file.stem}_transcript.json")
    
    if not transcript_file.exists():
        print(f"   ❌ No transcript found!")
        print(f"   Run: python create_clips_v4_integrated.py \"{video_path}\"")
        return
    
    with open(transcript_file) as f:
        data = json.load(f)
        segments = data['segments']
    
    print(f"   ✅ Loaded {len(segments)} segments")
    
    # Load cached moments (from previous run)
    cache_file = Path("data/cache/pipeline/moments_cache.json")
    
    if not cache_file.exists():
        print(f"\n   ❌ No moments cache found!")
        print(f"   Run cached test first: python test_2stage_cached.py")
        return
    
    with open(cache_file) as f:
        cache = json.load(f)
    
    # Get moments for this video
    video_hash = hashlib.md5(str(video_path).encode()).hexdigest()[:8]
    
    if video_hash not in cache:
        print(f"\n   ❌ No cached moments for this video!")
        print(f"   Run: python test_2stage_cached.py \"{video_path}\"")
        return
    
    moments = cache[video_hash]
    
    print(f"\n{'='*70}")
    print(f"📊 EXTRACTION ANALYSIS")
    print(f"{'='*70}")
    
    print(f"\n   Total moments: {len(moments)}")
    
    # Analyze moments
    valid = 0
    invalid = 0
    
    issues = {
        'no_segments': 0,
        'too_short': 0,
        'too_long': 0,
        'no_text': 0
    }
    
    durations = []
    segment_counts = []
    
    for m in moments:
        duration = m.get('end', 0) - m.get('start', 0)
        seg_count = len(m.get('segments', []))
        
        durations.append(duration)
        segment_counts.append(seg_count)
        
        # Validate
        is_valid = True
        
        if seg_count == 0:
            is_valid = False
            issues['no_segments'] += 1
        
        if duration < 10:
            is_valid = False
            issues['too_short'] += 1
        elif duration > 120:
            is_valid = False
            issues['too_long'] += 1
        
        if seg_count > 0:
            text = ''.join([s.get('text', '') for s in m['segments']])
            if len(text.strip()) < 50:
                is_valid = False
                issues['no_text'] += 1
        
        if is_valid:
            valid += 1
        else:
            invalid += 1
    
    print(f"\n   ✅ Valid: {valid} ({valid/len(moments)*100:.0f}%)")
    print(f"   ❌ Invalid: {invalid} ({invalid/len(moments)*100:.0f}%)")
    
    if invalid > 0:
        print(f"\n   ⚠️  Invalid breakdown:")
        for issue, count in issues.items():
            if count > 0:
                print(f"      - {issue.replace('_', ' ').title()}: {count}")
    
    # Statistics
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print(f"\n   📊 Duration Statistics:")
        print(f"      Average: {avg_duration:.1f}s")
        print(f"      Min: {min_duration:.1f}s")
        print(f"      Max: {max_duration:.1f}s")
        print(f"      Target: 35-70s")
        
        in_range = sum(1 for d in durations if 35 <= d <= 70)
        print(f"      In range: {in_range}/{len(durations)} ({in_range/len(durations)*100:.0f}%)")
    
    # Show examples
    print(f"\n   🔍 Sample Moments:")
    
    # Valid examples
    valid_moments = [m for m in moments if len(m.get('segments', [])) > 0]
    if valid_moments:
        print(f"\n   ✅ Valid Examples:")
        for i, m in enumerate(valid_moments[:3], 1):
            duration = m.get('end', 0) - m.get('start', 0)
            text = m['segments'][0].get('text', '')[:60] if m['segments'] else ''
            print(f"      {i}. {m.get('start', 0):.0f}s-{m.get('end', 0):.0f}s ({duration:.0f}s)")
            print(f"         {text}...")
    
    # Invalid examples
    invalid_moments = [m for m in moments if len(m.get('segments', [])) == 0 or 
                      (m.get('end', 0) - m.get('start', 0)) < 10]
    if invalid_moments:
        print(f"\n   ❌ Invalid Examples:")
        for i, m in enumerate(invalid_moments[:3], 1):
            duration = m.get('end', 0) - m.get('start', 0)
            seg_count = len(m.get('segments', []))
            print(f"      {i}. {m.get('start', 0):.0f}s-{m.get('end', 0):.0f}s ({duration:.0f}s, {seg_count} segs)")
    
    # Quality score
    print(f"\n   {'='*70}")
    print(f"   📈 EXTRACTION QUALITY SCORE")
    print(f"   {'='*70}")
    
    score = valid / len(moments) * 100 if moments else 0
    
    if score >= 90:
        print(f"\n   🔥 EXCELLENT: {score:.0f}%")
        print(f"   Ready for production!")
    elif score >= 75:
        print(f"\n   ✅ GOOD: {score:.0f}%")
        print(f"   Minor improvements needed")
    elif score >= 60:
        print(f"\n   ⚠️  FAIR: {score:.0f}%")
        print(f"   Needs optimization")
    else:
        print(f"\n   ❌ POOR: {score:.0f}%")
        print(f"   Major fixes required")
    
    print(f"\n   ⏱️  Time: Instant (using cache)")
    print(f"   💰 Cost: $0")
    
    return {
        'total': len(moments),
        'valid': valid,
        'invalid': invalid,
        'score': score
    }


if __name__ == '__main__':
    video = sys.argv[1] if len(sys.argv) > 1 else "data/uploads/Dieter Lange.mp4"
    asyncio.run(validate_extraction(video))

