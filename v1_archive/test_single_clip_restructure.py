#!/usr/bin/env python3
"""
Test restructure on SINGLE clip only
Minimal cost (~$0.50)
"""

import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from create_clips_v4_integrated import CreateClipsV4Integrated


async def test_single_restructure():
    """Test restructure on one clip"""
    
    v4 = CreateClipsV4Integrated()
    
    print(f"\n{'='*70}")
    print(f"🧪 SINGLE CLIP RESTRUCTURE TEST")
    print(f"{'='*70}")
    
    # Load transcript
    transcript_file = Path("data/cache/transcripts/Dieter Lange_transcript.json")
    
    with open(transcript_file, 'r') as f:
        data = json.load(f)
        segments = data['segments']
    
    # Create one test clip (segments 10-20)
    test_segments = segments[10:20]
    
    clip = {
        'start': test_segments[0]['start'],
        'end': test_segments[-1]['end'],
        'segments': test_segments,
        'video_path': str(Path("data/uploads/Dieter Lange.mp4")),
        'original_indices': list(range(10, 20))
    }
    
    story = {'storylines': [], 'standalone_moments': []}
    
    print(f"\n📊 Test clip:")
    print(f"   Duration: {clip['end'] - clip['start']:.1f}s")
    print(f"   Segments: {len(clip['segments'])}")
    print(f"   Start: {clip['start']:.1f}s")
    
    # Check original has text
    print(f"\n✅ Original segment 0:")
    print(f"   Keys: {list(clip['segments'][0].keys())}")
    print(f"   Has text: {'text' in clip['segments'][0]}")
    if 'text' in clip['segments'][0]:
        print(f"   Text: {clip['segments'][0]['text'][:80]}...")
    
    # Format original
    print(f"\n📝 Formatting original clip...")
    original_formatted = v4._format_clip_for_eval(clip)
    print(f"   Formatted length: {len(original_formatted)} chars")
    print(f"   Preview: {original_formatted[:150]}...")
    
    if len(original_formatted) < 100:
        print(f"\n   ❌ ERROR: Original formatting failed!")
        return
    
    # Create moment from clip (for _restructure_with_review)
    moment = {
        'id': 1,
        'start': clip['start'],
        'end': clip['end'],
        'topic': 'Test clip',
        'strength': 'high',
        'reason': 'Testing restructure'
    }
    
    # Restructure with AI
    print(f"\n{'='*70}")
    print(f"🔧 RESTRUCTURING WITH AI")
    print(f"{'='*70}")
    
    try:
        restructured = await v4._restructure_with_review(
            moment=moment,
            segments=segments,  # Full transcript for context
            story_structure=story
        )
        
        if not restructured:
            print(f"\n   ❌ Restructure returned None!")
            return
        
        print(f"\n✅ Restructure complete!")
        print(f"   Original: {len(clip['segments'])} segments")
        print(f"   Restructured: {len(restructured.get('segments', []))} segments")
        
        # Check restructured segments
        restructured_segments = restructured.get('segments', [])
        
        print(f"\n🔍 Checking restructured segments:")
        
        for i, seg in enumerate(restructured_segments[:3]):
            print(f"\n   Segment {i}:")
            print(f"      Keys: {list(seg.keys())}")
            print(f"      Has 'text': {'text' in seg}")
            
            if 'text' in seg:
                print(f"      Text: {seg['text'][:60]}...")
            else:
                print(f"      ❌ NO TEXT FIELD!")
                print(f"      Full segment: {seg}")
        
        # Format restructured
        print(f"\n📝 Formatting restructured clip...")
        restructured_formatted = v4._format_clip_for_eval(restructured)
        print(f"   Formatted length: {len(restructured_formatted)} chars")
        print(f"   Preview: {restructured_formatted[:150]}...")
        
        # CRITICAL CHECK
        print(f"\n{'='*70}")
        print(f"🎯 RESULT")
        print(f"{'='*70}")
        
        if len(restructured_formatted) < 100:
            print(f"\n   ❌ FAILED! Restructured clip lost text!")
            print(f"   Full formatted text: {restructured_formatted}")
            print(f"\n   Segments:")
            for i, seg in enumerate(restructured_segments):
                print(f"      {i}: {seg}")
        else:
            print(f"\n   ✅ SUCCESS! Text preserved!")
            print(f"   Original: {len(original_formatted)} chars")
            print(f"   Restructured: {len(restructured_formatted)} chars")
            print(f"\n   🎉 FIX WORKS! Ready for full pipeline test!")
        
    except Exception as e:
        print(f"\n❌ Error during restructure: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n💰 Estimated cost: ~$0.30-0.50")


if __name__ == '__main__':
    asyncio.run(test_single_restructure())

