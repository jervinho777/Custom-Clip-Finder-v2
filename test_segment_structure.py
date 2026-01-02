#!/usr/bin/env python3
"""
Test segment structure preservation - NO AI CALLS
Zero cost debugging
"""

import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from create_clips_v4_integrated import CreateClipsV4Integrated


async def test_segment_preservation():
    """Test if restructure preserves segment text"""
    
    v4 = CreateClipsV4Integrated()
    
    print(f"\n{'='*70}")
    print(f"🔍 SEGMENT STRUCTURE TEST (Zero Cost)")
    print(f"{'='*70}")
    
    # Load Dieter Lange transcript
    transcript_file = Path("data/cache/transcripts/Dieter Lange_transcript.json")
    
    if not transcript_file.exists():
        print(f"❌ Transcript not found!")
        return
    
    with open(transcript_file) as f:
        data = json.load(f)
        segments = data['segments']
    
    print(f"\n📊 Original segments: {len(segments)}")
    print(f"\n   First segment structure:")
    print(f"   Keys: {list(segments[0].keys())}")
    print(f"   Has 'text': {'text' in segments[0]}")
    print(f"   Has 'content': {'content' in segments[0]}")
    
    if 'text' in segments[0]:
        print(f"   Text: {segments[0]['text'][:80]}...")
    
    # Create test clip (no AI)
    clip = {
        'start': 0,
        'end': segments[4]['end'],
        'segments': segments[:5],  # First 5 segments
        'video_path': 'test',
        'original_indices': [0, 1, 2, 3, 4]
    }
    
    print(f"\n📝 Test clip created: {len(clip['segments'])} segments")
    
    # Test 1: Format for evaluation (what Step 1.5 does)
    print(f"\n{'='*70}")
    print(f"TEST 1: Format for Evaluation (like Step 1.5)")
    print(f"{'='*70}")
    
    formatted_text = v4._format_clip_for_eval(clip)
    
    print(f"\n   Formatted text length: {len(formatted_text)}")
    print(f"   Preview: {formatted_text[:200]}...")
    
    if len(formatted_text) < 100:
        print(f"\n   ❌ PROBLEM: Formatted text too short!")
        print(f"   Full text: {formatted_text}")
    else:
        print(f"\n   ✅ Formatting works!")
    
    # Test 2: Simulate restructure
    print(f"\n{'='*70}")
    print(f"TEST 2: Simulate Restructure")
    print(f"{'='*70}")
    
    # Manually create restructured clip (like _restructure_clip_hybrid does)
    keep_indices = [0, 2, 4]  # Keep 3 segments
    new_segments = [clip['segments'][i] for i in keep_indices]
    
    restructured = {
        **clip,
        'segments': new_segments,
        'start': new_segments[0]['start'],
        'end': new_segments[-1]['end'],
        'original_indices': keep_indices
    }
    
    print(f"\n   Original: {len(clip['segments'])} segments")
    print(f"   Restructured: {len(restructured['segments'])} segments")
    
    # Check segment structure
    print(f"\n   Restructured segment 0:")
    print(f"   Keys: {list(restructured['segments'][0].keys())}")
    print(f"   Has 'text': {'text' in restructured['segments'][0]}")
    
    if 'text' in restructured['segments'][0]:
        print(f"   Text: {restructured['segments'][0]['text'][:80]}...")
    else:
        print(f"   ❌ NO TEXT FIELD!")
    
    # Test 3: Format restructured clip
    print(f"\n{'='*70}")
    print(f"TEST 3: Format Restructured Clip")
    print(f"{'='*70}")
    
    formatted_restructured = v4._format_clip_for_eval(restructured)
    
    print(f"\n   Formatted text length: {len(formatted_restructured)}")
    print(f"   Preview: {formatted_restructured[:200]}...")
    
    if len(formatted_restructured) < 100:
        print(f"\n   ❌ PROBLEM: Restructured formatting lost text!")
        print(f"   Full text: {formatted_restructured}")
    else:
        print(f"\n   ✅ Restructure preserves text!")
    
    # Test 4: Check _format_clip_for_eval logic
    print(f"\n{'='*70}")
    print(f"TEST 4: Inspect _format_clip_for_eval()")
    print(f"{'='*70}")
    
    # Manually run the logic
    clip_segments = restructured.get('segments', [])
    clip_text_parts = []
    
    print(f"\n   Segments to format: {len(clip_segments)}")
    
    for i, seg in enumerate(clip_segments):
        print(f"\n   Segment {i}:")
        print(f"      Keys: {list(seg.keys())}")
        
        # This is what _format_clip_for_eval does:
        text = seg.get('text', '') or seg.get('content', '')
        
        print(f"      Text extracted: {len(text)} chars")
        if text:
            print(f"      Preview: {text[:60]}...")
            clip_text_parts.append(f"[{seg.get('start', 0):.1f}s] {text.strip()}")
        else:
            print(f"      ❌ NO TEXT FOUND!")
    
    full_text = '\n'.join(clip_text_parts)
    
    print(f"\n   Final assembled text: {len(full_text)} chars")
    
    if len(full_text) < 100:
        print(f"\n   ❌ PROBLEM FOUND!")
        print(f"   _format_clip_for_eval is not extracting text properly!")
    else:
        print(f"\n   ✅ Text extraction works!")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"🎯 DIAGNOSIS")
    print(f"{'='*70}")
    
    if len(formatted_restructured) >= 100:
        print(f"\n   ✅ NO BUG FOUND IN BASIC RESTRUCTURE!")
        print(f"   Restructure preserves segments correctly")
        print(f"   Problem must be in AI restructure logic")
    else:
        print(f"\n   ❌ BUG CONFIRMED!")
        print(f"   Restructure or formatting losing text")
        print(f"   Check segment field names and extraction logic")


if __name__ == '__main__':
    asyncio.run(test_segment_preservation())

