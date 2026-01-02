import json
import sys
sys.path.insert(0, '.')

from create_clips_v4_integrated import OpenLoopBridging

print("="*70)
print("🧪 TESTING Stage 1.75 - Self-Contained Clip")
print("="*70)

# Load Lebenslinie (self-contained clip)
with open('data/cache/transcripts/Lebenslinie V2_NOCTA_transcript.json') as f:
    clip = json.load(f)['segments']

print(f"\n✅ Loaded clip: {len(clip)} segments, {clip[-1]['end']:.1f}s")

# Check for open loops
print(f"\n🔍 Checking for open loops...")
for i, seg in enumerate(clip):
    text = seg['text'].lower()
    if '?' in text or 'warum' in text or 'was' in text[:20]:
        print(f"   Segment {i} ({seg['start']:.1f}s): Potential question")
        print(f"   '{seg['text'][:80]}...'")

# Create test moment ending BEFORE last segment
if len(clip) > 1:
    test_moment = {
        'start': clip[0]['start'],
        'end': clip[-2]['end'],
        'segments': clip[:-1],
        'duration': clip[-2]['end'] - clip[0]['start']
    }
    
    print(f"\n📊 TEST: Removing last segment")
    print(f"   Original: {clip[-1]['end']:.1f}s")
    print(f"   Test ends at: {test_moment['end']:.1f}s")
    print(f"   Last text: '{test_moment['segments'][-1]['text'][-60:]}'")
    
    # Test bridging
    bridger = OpenLoopBridging(segments=clip)
    result = bridger.detect_and_bridge(test_moment)
    
    print(f"\n📊 RESULT:")
    print(f"   End: {result['end']:.1f}s")
    print(f"   Bridged: {result.get('bridged_gap', False)}")
    
    if result.get('bridged_gap'):
        print(f"   ✅ Extended by {result['end'] - test_moment['end']:.1f}s")
    else:
        print(f"   ℹ️  No bridging needed (no open loop)")

print("="*70)
