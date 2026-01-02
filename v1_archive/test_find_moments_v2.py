#!/usr/bin/env python3
"""
🧪 TEST SCRIPT: _find_all_moments() v2

Tests the new aggressive moment-finding approach.
Compares with v1 if possible.
"""

import json
from pathlib import Path
from create_clips_v2 import CreateClipsV2


def load_test_transcript():
    """Load a test transcript from cache"""
    
    cache_dir = Path("data/cache/transcripts")
    
    if not cache_dir.exists():
        print("❌ Cache directory not found")
        return None
    
    # Find available transcripts
    transcript_files = list(cache_dir.glob("*.json"))
    
    if not transcript_files:
        print("❌ No transcripts found in cache")
        return None
    
    # Use first available transcript
    transcript_path = transcript_files[0]
    
    print(f"\n📄 Loading transcript: {transcript_path.name}")
    
    with open(transcript_path, 'r') as f:
        data = json.load(f)
    
    # Extract segments
    if 'segments' in data:
        segments = data['segments']
        print(f"   ✅ Loaded {len(segments)} segments")
        return segments
    elif 'text' in data:
        # Create pseudo-segments
        text = data['text']
        words = text.split()
        segments = []
        chunk_size = 25
        
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i+chunk_size]
            segments.append({
                'text': ' '.join(chunk),
                'start': i / 2.5,
                'end': (i + len(chunk)) / 2.5
            })
        
        print(f"   ✅ Created {len(segments)} segments from text")
        return segments
    
    print("❌ Unknown transcript format")
    return None


def test_v2_find_moments():
    """Test the new _find_all_moments() method"""
    
    print("="*70)
    print("🧪 TEST: _find_all_moments() v2")
    print("="*70)
    
    # Load test transcript
    segments = load_test_transcript()
    
    if not segments:
        print("\n❌ Could not load test transcript")
        return None
    
    # Calculate video stats
    total_duration = segments[-1]['end'] if segments else 0
    print(f"\n📊 Video Stats:")
    print(f"   Duration: {total_duration/60:.1f} minutes")
    print(f"   Segments: {len(segments)}")
    
    # Initialize CreateClipsV2
    print(f"\n🔧 Initializing CreateClipsV2...")
    creator = CreateClipsV2()
    
    if not creator.client:
        print("❌ No API key - cannot test")
        return None
    
    # Run _find_all_moments()
    print(f"\n{'='*70}")
    print("🚀 RUNNING: _find_all_moments()")
    print(f"{'='*70}")
    
    moments = creator._find_all_moments(segments)
    
    if not moments:
        print("\n❌ No moments found")
        return None
    
    # Display results
    print(f"\n{'='*70}")
    print("📊 RESULTS")
    print(f"{'='*70}")
    
    print(f"\n✅ Total moments found: {len(moments)}")
    
    # Count by strength
    strength_counts = {}
    for moment in moments:
        strength = moment.get('strength', 'unknown')
        strength_counts[strength] = strength_counts.get(strength, 0) + 1
    
    print(f"\n📊 By strength:")
    for strength, count in sorted(strength_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {strength}: {count}")
    
    # Show all moments
    print(f"\n🎯 ALL MOMENTS FOUND:")
    print("-" * 70)
    
    for i, moment in enumerate(moments, 1):
        moment_id = moment.get('id', moment.get('moment_id', i))
        start = moment.get('start', 0)
        end = moment.get('end', 0)
        duration = end - start
        topic = moment.get('topic', 'No topic')
        strength = moment.get('strength', '?')
        reason = moment.get('reason', moment.get('why_strong', 'No reason'))
        
        print(f"\n   #{moment_id} [{strength.upper()}]")
        print(f"   ⏱️  {start:.1f}s - {end:.1f}s ({duration:.1f}s)")
        print(f"   📝 {topic}")
        print(f"   💡 {reason[:100]}{'...' if len(reason) > 100 else ''}")
    
    # Summary
    total_duration_covered = sum(
        moment.get('end', 0) - moment.get('start', 0) 
        for moment in moments
    )
    video_duration = segments[-1]['end'] if segments else 0
    
    print(f"\n{'='*70}")
    print("📈 SUMMARY")
    print(f"{'='*70}")
    print(f"   Moments found: {len(moments)}")
    print(f"   Video duration: {video_duration/60:.1f} minutes")
    print(f"   Total moments duration: {total_duration_covered/60:.1f} minutes")
    print(f"   Coverage: {total_duration_covered/video_duration*100:.1f}%")
    
    # Save results
    output_file = Path("output/test_moments_v2.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            'moments': moments,
            'summary': {
                'total_moments': len(moments),
                'strength_counts': strength_counts,
                'video_duration': video_duration,
                'total_moments_duration': total_duration_covered,
                'coverage_percent': total_duration_covered/video_duration*100 if video_duration > 0 else 0
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved: {output_file}")
    
    return moments


def compare_with_v1():
    """Compare v2 results with v1 if available"""
    
    print(f"\n{'='*70}")
    print("🔍 COMPARISON: v1 vs v2")
    print(f"{'='*70}")
    
    # Check if v1 results exist
    v1_results = Path("output/clips")
    v1_found = False
    
    if v1_results.exists():
        # Look for extraction_result.json files
        for result_file in v1_results.rglob("extraction_result.json"):
            try:
                with open(result_file, 'r') as f:
                    v1_data = json.load(f)
                
                clips = v1_data.get('clips', [])
                if clips:
                    print(f"\n📊 v1 Results (from {result_file.parent.name}):")
                    print(f"   Clips found: {len(clips)}")
                    
                    # Count versions
                    total_versions = sum(len(c.get('versions', [])) for c in clips)
                    print(f"   Total versions: {total_versions}")
                    
                    v1_found = True
                    break
            except:
                continue
    
    if not v1_found:
        print("\n⚠️  No v1 results found for comparison")
        print("   Run create_clips.py first to generate v1 results")
    
    print(f"\n💡 v2 Improvement:")
    print(f"   • Aggressive moment-finding (10-20+ moments)")
    print(f"   • Simplified format (more moments possible)")
    print(f"   • Higher token limit (15k vs 10k)")
    print(f"   • Reduced context (no hook patterns in prompt)")


def main():
    """Main test function"""
    
    print("\n" + "="*70)
    print("🧪 TEST SCRIPT: _find_all_moments() v2")
    print("="*70)
    
    # Run test
    moments = test_v2_find_moments()
    
    if moments:
        # Compare with v1
        compare_with_v1()
        
        print(f"\n{'='*70}")
        print("✅ TEST COMPLETE!")
        print(f"{'='*70}")
        print(f"\n📊 Key Metrics:")
        print(f"   • Moments found: {len(moments)}")
        print(f"   • Expected improvement: 2-5x more than v1")
        print(f"\n💡 Next Steps:")
        print(f"   • Review moments in output/test_moments_v2.json")
        print(f"   • Implement Step 2: _restructure_moment()")
        print(f"   • Implement Step 3: _create_variations()")
    else:
        print(f"\n❌ TEST FAILED")
        print(f"   Check API key and transcript availability")


if __name__ == "__main__":
    main()

