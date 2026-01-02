#!/usr/bin/env python3
"""
🧪 TEST: Steps 2 & 3 of create_clips_v2.py

Tests:
- Step 2: _restructure_moment()
- Step 3: _create_variations()
"""

import json
import sys
from pathlib import Path
from create_clips_v2 import CreateClipsV2


def test_steps_2_3():
    """Test Steps 2 & 3 with a real moment"""
    
    print("="*70)
    print("🧪 TEST: Steps 2 & 3 - Restructure & Variations")
    print("="*70)
    
    # Initialize
    creator = CreateClipsV2()
    
    if not creator.client:
        print("\n❌ No API key - cannot test Steps 2 & 3")
        return False
    
    # Load test transcript
    transcript_path = Path("data/cache/transcripts/b1cc36469f83c3caab9cc4fe7457b6a0.json")
    
    if not transcript_path.exists():
        print(f"❌ Transcript not found: {transcript_path}")
        return False
    
    print(f"\n📄 Loading transcript: {transcript_path.name}")
    segments = creator.load_transcript(str(transcript_path))
    
    if not segments:
        print("❌ Failed to load transcript")
        return False
    
    print(f"   ✅ Loaded {len(segments)} segments")
    
    # Create a test moment (use first strong moment from v2 results if available)
    test_moment = {
        "id": 1,
        "start": 0.0,
        "end": 15.1,
        "topic": "Lebensverändernder Moment mit dem Sohn",
        "strength": "high",
        "reason": "Starker emotionaler Hook über eine wichtige Entscheidung und Selbsterkenntnis"
    }
    
    print(f"\n{'='*70}")
    print("🔧 STEP 2: RESTRUCTURE MOMENT")
    print("-" * 70)
    print(f"   Moment: {test_moment['start']:.1f}s - {test_moment['end']:.1f}s")
    print(f"   Topic: {test_moment['topic']}")
    
    # Test Step 2
    restructured = creator._restructure_moment(test_moment, segments)
    
    if not restructured:
        print("\n❌ Restructuring failed")
        return False
    
    print(f"\n✅ Restructuring successful!")
    print(f"   Clip ID: {restructured.get('clip_id', 'unknown')}")
    print(f"   Segments: {len(restructured.get('structure', {}).get('segments', []))}")
    print(f"   Duration: {restructured.get('structure', {}).get('total_duration', 0):.1f}s")
    print(f"   Strategy: {restructured.get('structure', {}).get('strategy', 'unknown')}")
    
    # Show structure
    structure_segments = restructured.get('structure', {}).get('segments', [])
    if structure_segments:
        print(f"\n   📐 Structure:")
        for seg in structure_segments:
            role = seg.get('role', 'unknown')
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            text = seg.get('text', '')[:50]
            print(f"      • {role}: {start:.1f}s-{end:.1f}s - {text}...")
    
    # Test Step 3
    print(f"\n{'='*70}")
    print("🎨 STEP 3: CREATE VARIATIONS")
    print("-" * 70)
    
    variations = creator._create_variations(restructured, segments)
    
    if not variations:
        print("\n❌ Variations creation failed")
        return False
    
    print(f"\n✅ Variations created!")
    print(f"   Total versions: {len(variations)}")
    
    for i, var in enumerate(variations, 1):
        version_id = var.get('version_id', 'unknown')
        version_name = var.get('version_name', 'Unknown')
        scores = var.get('scores', {})
        wt_score = scores.get('watchtime_potential', 0)
        vir_score = scores.get('virality_potential', 0)
        
        print(f"\n   Version {i}: {version_id}")
        print(f"      Name: {version_name}")
        print(f"      Watchtime: {wt_score}/100")
        print(f"      Virality: {vir_score}/100")
        
        if var.get('why_different'):
            print(f"      Why different: {var.get('why_different')[:80]}...")
    
    # Save results
    output_file = Path("output/test_steps_2_3_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "test_moment": test_moment,
            "restructured_clip": restructured,
            "variations": variations
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("✅ TEST COMPLETE!")
    print(f"{'='*70}")
    print(f"\n💾 Results saved: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   • Moment restructured: ✅")
    print(f"   • Variations created: {len(variations)}")
    print(f"   • Total versions: {len(variations)}")
    
    return True


if __name__ == "__main__":
    success = test_steps_2_3()
    sys.exit(0 if success else 1)

