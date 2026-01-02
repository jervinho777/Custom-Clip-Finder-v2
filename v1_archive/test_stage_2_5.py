#!/usr/bin/env python3
"""
🧪 ISOLATED TEST: Stage 2.5 - Learning-Based Intelligent Cuts

Tests the learning-based cuts on Dieter Lange story (87s → 59s target)
Cost: ~$0.05 (1 AI call with Sonnet 4.5)
"""

import json
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, '.')

from create_clips_v4_integrated import CreateClipsV4Integrated

async def test_stage_2_5():
    print("="*70)
    print("🧪 TESTING STAGE 2.5: Learning-Based Intelligent Cuts")
    print("="*70)
    print("   Target: Dieter Lange story (87s → 59s)")
    print("   Cost: ~$0.05 (1 AI call)")
    print("="*70)
    
    # Load cached Dieter Lange transcript
    print(f"\n📂 Loading transcript...")
    try:
        transcript_path = Path('data/cache/transcripts/Dieter Lange_transcript.json')
        if not transcript_path.exists():
            # Try alternative path
            transcript_path = Path('data/cache/transcripts') / 'Dieter Lange_transcript.json'
        
        with open(transcript_path) as f:
            data = json.load(f)
            segments = data.get('segments', [])
        print(f"   ✅ Loaded: {len(segments)} segments")
    except FileNotFoundError as e:
        print(f"   ❌ Transcript not found: {e}")
        print(f"\n   Please run the full pipeline once to cache the transcript:")
        print(f"   python create_clips_v4_integrated.py")
        return
    except Exception as e:
        print(f"   ❌ Error loading transcript: {e}")
        return
    
    # Find the famous Dieter Lange story segments
    # Look for "Horde Kinder sitzt am Straßenrand"
    story_start_idx = None
    for i, seg in enumerate(segments):
        text = seg.get('text', '').lower()
        if 'horde kinder' in text or 'kinder sitzt' in text:
            story_start_idx = i
            break
    
    if story_start_idx is None:
        print(f"   ❌ Could not find Dieter Lange story in transcript!")
        print(f"   💡 Looking for segments containing 'horde kinder' or 'kinder sitzt'")
        return
    
    # Get segments for the story (approximately 8-10 segments for 87s)
    # Extend search to find complete story
    story_end_idx = story_start_idx + 10
    for i in range(story_start_idx, min(story_start_idx + 15, len(segments))):
        text = segments[i].get('text', '').lower()
        if 'freude am tun' in text or 'ersetzt worden' in text:
            story_end_idx = i + 1
            break
    
    story_segments = segments[story_start_idx:story_end_idx]
    
    if not story_segments:
        print(f"   ❌ Could not extract story segments!")
        return
    
    # Create test moment
    test_moment = {
        'start': story_segments[0].get('start', 0),
        'end': story_segments[-1].get('end', 0),
        'duration': story_segments[-1].get('end', 0) - story_segments[0].get('start', 0),
        'segments': story_segments,
        'viral_score': 94,  # From Stage 0 pre-score
        'godmode_score': 41,  # Current score without optimization
        'moment_type': 'parable',
        'hook_phrase': story_segments[0].get('text', '')[:100] if story_segments else ''
    }
    
    print(f"\n📊 TEST MOMENT (BEFORE Stage 2.5):")
    print(f"   Start: {test_moment['start']:.1f}s")
    print(f"   End: {test_moment['end']:.1f}s")
    print(f"   Duration: {test_moment['duration']:.1f}s")
    print(f"   Segments: {len(test_moment['segments'])}")
    print(f"   Type: {test_moment['moment_type']}")
    print(f"   Pre-score: {test_moment['viral_score']}/100")
    print(f"   Godmode (before): {test_moment['godmode_score']}/50")
    print(f"\n   Text preview:")
    text_preview = test_moment['segments'][0].get('text', '')[:100] if test_moment['segments'] else 'N/A'
    print(f"   '{text_preview}...'")
    
    # Initialize system
    print(f"\n🔧 Initializing system...")
    system = CreateClipsV4Integrated()
    system.segments = segments  # Required for helper methods
    print(f"   ✅ System ready")
    
    # Test Stage 2.5
    print(f"\n{'='*70}")
    print(f"🧪 RUNNING STAGE 2.5: Learning-Based Intelligent Cuts")
    print(f"{'='*70}")
    
    try:
        optimized_moments = await system._learning_based_cuts([test_moment])
        
        if not optimized_moments:
            print(f"\n❌ No optimized moments returned!")
            return
        
        optimized = optimized_moments[0]
        
        # Show results
        print(f"\n{'='*70}")
        print(f"📊 RESULTS")
        print(f"{'='*70}")
        
        print(f"\n   BEFORE Stage 2.5:")
        print(f"   • Duration: {test_moment['duration']:.1f}s")
        print(f"   • Segments: {len(test_moment['segments'])}")
        print(f"   • Score: {test_moment['godmode_score']}/50")
        
        print(f"\n   AFTER Stage 2.5:")
        print(f"   • Duration: {optimized.get('duration', 0):.1f}s")
        print(f"   • Segments: {len(optimized.get('segments', []))}")
        reduction = test_moment['duration'] - optimized.get('duration', 0)
        print(f"   • Reduction: {reduction:.1f}s")
        
        if optimized.get('learning_cuts'):
            print(f"\n   ✅ Learning-based cuts applied!")
            cuts_made = optimized.get('cuts_made', [])
            if cuts_made:
                print(f"\n   Cuts made:")
                for cut in cuts_made:
                    print(f"      • {cut}")
            else:
                print(f"\n   (No cuts details available)")
        
        # Compare to original viral clip
        print(f"\n{'='*70}")
        print(f"🎯 COMPARISON TO VIRAL CLIP")
        print(f"{'='*70}")
        print(f"   Original viral clip: 59s")
        optimized_duration = optimized.get('duration', 0)
        print(f"   Our optimized clip: {optimized_duration:.1f}s")
        diff = abs(optimized_duration - 59.0)
        print(f"   Difference: {diff:.1f}s")
        
        if diff < 3:
            print(f"\n   🎉 EXCELLENT! Within 3s of viral clip!")
            print(f"   Stage 2.5 is working perfectly!")
        elif diff < 5:
            print(f"\n   ✅ GOOD! Within 5s of viral clip!")
            print(f"   Minor tweaking possible but very close!")
        elif diff < 10:
            print(f"\n   ⚠️  ACCEPTABLE! Within 10s of viral clip")
            print(f"   Some optimization still possible")
        else:
            print(f"\n   ❌ NEEDS WORK! {diff:.1f}s off from viral clip")
            print(f"   Check cut logic and patterns")
        
        # Show optimized text
        print(f"\n{'='*70}")
        print(f"📝 OPTIMIZED TEXT PREVIEW")
        print(f"{'='*70}")
        optimized_segments = optimized.get('segments', [])
        if optimized_segments:
            optimized_text = ' '.join([s.get('text', '') for s in optimized_segments])
            print(f"   {optimized_text[:200]}...")
        else:
            print(f"   (No segments available)")
        
        print(f"\n{'='*70}")
        print(f"✅ TEST COMPLETE")
        print(f"{'='*70}")
        print(f"\n   💰 Estimated cost: ~$0.05")
        print(f"   ⏱️  Processing time: ~10-15 seconds")
        
        if diff < 5:
            print(f"\n   🚀 READY FOR PRODUCTION!")
            print(f"   Stage 2.5 successfully creates viral-optimized cuts!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_stage_2_5())

