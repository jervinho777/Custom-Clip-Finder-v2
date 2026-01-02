import json
import sys
sys.path.insert(0, '.')

from create_clips_v4_integrated import OpenLoopBridging

print("="*70)
print("🧪 STAGE 1.75 DRY RUN TEST - Dieter Lange")
print("="*70)

# Load longform transcript
with open('data/cache/transcripts/Dieter Lange_transcript.json') as f:
    longform = json.load(f)['segments']

# Load viral clip to find correct segments
with open('data/cache/transcripts/Dieter Lange Viral Clip_transcript.json') as f:
    clip = json.load(f)['segments']

print(f"\n✅ Loaded longform: {len(longform)} segments")
print(f"✅ Loaded clip: {len(clip)} segments")

# Find where viral clip is in longform
print(f"\n🔍 Finding viral clip location in longform...")
start_idx = None
end_idx = None

for i, seg in enumerate(longform):
    if 'arbeite niemals für geld' in seg['text'].lower():
        start_idx = i
        print(f"   Found start at segment {i} ({seg['start']:.1f}s)")
        
        # Find end
        for j, seg2 in enumerate(longform[i:], start=i):
            if 'freude am tun' in seg2['text'].lower() and 'ersetzt' in seg2['text'].lower():
                end_idx = j
                print(f"   Found end at segment {j} ({seg2['end']:.1f}s)")
                break
        break

if start_idx is None or end_idx is None:
    print("❌ Could not find viral clip in longform!")
    exit(1)

# Find segment with question "Was ist hier passiert?"
question_idx = None
for i in range(start_idx, end_idx + 1):
    if 'was ist hier passiert' in longform[i]['text'].lower():
        question_idx = i
        print(f"   Found question at segment {i} ({longform[i]['end']:.1f}s)")
        break

if question_idx is None:
    print("❌ Could not find question segment!")
    exit(1)

# Create test moment (story up to question, WITHOUT payoff)
test_moment = {
    'start': longform[start_idx]['start'],
    'end': longform[question_idx]['end'],
    'segments': longform[start_idx:question_idx+1],
    'duration': longform[question_idx]['end'] - longform[start_idx]['start']
}

print(f"\n📊 TEST MOMENT (before Stage 1.75):")
print(f"   Segments: {start_idx} to {question_idx} ({len(test_moment['segments'])} total)")
print(f"   Start: {test_moment['start']:.1f}s")
print(f"   End: {test_moment['end']:.1f}s")
print(f"   Last text: '{test_moment['segments'][-1]['text'][-80:]}'")

# Test Stage 1.75
print(f"\n🔍 RUNNING Stage 1.75...")
bridger = OpenLoopBridging(segments=longform)
result = bridger.detect_and_bridge(test_moment)

print(f"\n📊 RESULT (after Stage 1.75):")
print(f"   Start: {result['start']:.1f}s")
print(f"   End: {result['end']:.1f}s")
print(f"   Segments: {len(result['segments'])}")
print(f"   Bridged gap: {result.get('bridged_gap', False)}")

if result.get('bridged_gap'):
    print(f"   Extension: +{result['end'] - test_moment['end']:.1f}s")
    print(f"   Last text: '{result['segments'][-1]['text']}'")

print(f"\n{'='*70}")

# Expected end from viral clip
expected_end = longform[end_idx]['end']

if result.get('bridged_gap') and abs(result['end'] - expected_end) < 1:
    print("✅ SUCCESS! Stage 1.75 works perfectly!")
    print(f"   Extended from {test_moment['end']:.1f}s to {result['end']:.1f}s")
    print(f"   Expected end: {expected_end:.1f}s")
    print(f"   Found payoff: 'Die Freude am Tun ist ersetzt...'")
    print(f"   Complete story arc! 🎉")
else:
    print("❌ FAILED! Stage 1.75 did not bridge correctly")
    print(f"   Expected end: {expected_end:.1f}s")
    print(f"   Got: {result['end']:.1f}s")

print("="*70)
