#!/usr/bin/env python3
"""
🧪 REAL WORLD TEST: Viral Example Learning

Tests the complete pipeline with a real clip example.
"""

import json
import sys
from pathlib import Path
from learn_from_viral_example import ViralExampleLearner


def test_real_example():
    """Test with real clip example"""
    
    print("="*70)
    print("🧪 REAL WORLD TEST: Viral Example Learning")
    print("="*70)
    
    # Initialize learner
    learner = ViralExampleLearner()
    
    if not learner.client:
        print("\n⚠️  No API key - AI analysis will be limited")
        print("   Continuing with non-AI functions...")
    
    # Setup inputs
    print(f"\n📥 SETTING UP INPUTS")
    print("-" * 70)
    
    # Try to find longform transcript (prefer cached transcript over video)
    longform_candidates = [
        "data/cache/transcripts/b1cc36469f83c3caab9cc4fe7457b6a0.json",
        "data/uploads/test.mp4",
    ]
    
    longform_path = None
    for candidate in longform_candidates:
        path = Path(candidate)
        if path.exists():
            longform_path = candidate
            print(f"   ✅ Found longform: {candidate}")
            break
    
    if not longform_path:
        print("   ⚠️  No longform found, using test data")
        longform_segments = [
            {"text": "Hallo und willkommen zu diesem Video", "start": 0.0, "end": 3.0},
            {"text": "Heute sprechen wir über ein wichtiges Thema", "start": 3.0, "end": 7.0},
            {"text": "Viele Leute machen diesen Fehler", "start": 7.0, "end": 11.0},
            {"text": "Warum der größte Fehler bei Social Media ist", "start": 120.0, "end": 125.0},
            {"text": "Die meisten Menschen denken", "start": 125.0, "end": 130.0},
            {"text": "Aber die Wahrheit ist anders", "start": 130.0, "end": 135.0},
            {"text": "Hier ist warum", "start": 135.0, "end": 138.0},
            {"text": "Wenn du das verstehst", "start": 200.0, "end": 205.0},
            {"text": "Dann wirst du erfolgreich sein", "start": 205.0, "end": 210.0},
        ]
    else:
        longform_segments = None
    
    # Clip timestamps (example moment)
    clip_start = 120.0  # Start of hook moment
    clip_end = 138.0    # End of content
    
    print(f"   📍 Clip range: {clip_start}s - {clip_end}s ({clip_end - clip_start:.1f}s)")
    
    # Performance data (realistic numbers)
    performance = {
        "views": 100000,
        "watch_time": 80,
        "followers": 5000,
        "likes": 5000,
        "shares": 500,
        "comments": 300
    }
    
    print(f"   📊 Performance:")
    print(f"      Views: {performance['views']:,}")
    print(f"      Watch Time: {performance['watch_time']}%")
    print(f"      Followers: {performance['followers']:,}")
    
    notes = "Extrem emotionaler Moment mit direkter Konfrontation - Hook wurde aus der Mitte nach vorne gezogen"
    
    print(f"\n{'='*70}")
    print("🚀 RUNNING COMPLETE PIPELINE")
    print(f"{'='*70}")
    
    # Load longform
    if longform_path:
        longform_segments = learner.load_transcript(longform_path)
        if not longform_segments:
            print("❌ Failed to load longform")
            return False
    elif not longform_segments:
        print("❌ No longform data available")
        return False
    
    # Extract clip from timestamps
    clip_segments, clip_metadata = learner.load_clip_data(
        None,  # No clip file
        clip_start,
        clip_end,
        longform_segments
    )
    
    if not clip_segments:
        print("❌ Failed to extract clip")
        return False
    
    print(f"   ✅ Extracted {len(clip_segments)} clip segments")
    
    # STEP 1: Compare transcripts
    print(f"\n{'='*70}")
    print("STEP 1: COMPARING TRANSCRIPTS")
    print("-" * 70)
    
    comparison = learner.compare_transcripts(longform_segments, clip_segments)
    
    if not comparison:
        print("❌ Comparison failed")
        return False
    
    # STEP 2: Analyze restructuring
    print(f"\n{'='*70}")
    print("STEP 2: ANALYZING RESTRUCTURING")
    print("-" * 70)
    
    restructuring = learner.analyze_restructuring(comparison, clip_segments, performance)
    
    if not restructuring:
        print("❌ Restructuring analysis failed")
        return False
    
    # STEP 3: Extract hook patterns
    print(f"\n{'='*70}")
    print("STEP 3: EXTRACTING HOOK PATTERNS")
    print("-" * 70)
    
    hook_segment = None
    for seg in comparison.get('used_segments', []):
        if seg.get('role') == 'hook':
            hook_segment = seg
            break
    
    if not hook_segment and comparison.get('used_segments'):
        hook_segment = comparison['used_segments'][0]
    
    if not hook_segment:
        print("❌ No hook segment found")
        return False
    
    hook_patterns = learner.extract_hook_patterns(
        hook_segment,
        clip_segments,
        performance,
        comparison
    )
    
    if not hook_patterns:
        print("❌ Hook patterns extraction failed")
        return False
    
    # STEP 4: Extract structure patterns
    print(f"\n{'='*70}")
    print("STEP 4: EXTRACTING STRUCTURE PATTERNS")
    print("-" * 70)
    
    structure_patterns = learner.extract_structure_patterns(
        clip_segments,
        restructuring,
        performance
    )
    
    if not structure_patterns:
        print("❌ Structure patterns extraction failed")
        return False
    
    # STEP 5: AI analysis
    print(f"\n{'='*70}")
    print("STEP 5: AI ANALYSIS")
    print("-" * 70)
    
    ai_analysis = learner.ai_analyze_example(
        longform_segments,
        clip_segments,
        comparison,
        restructuring,
        performance,
        notes=notes,
        deep_analysis=False
    )
    
    # STEP 6: Create template
    print(f"\n{'='*70}")
    print("STEP 6: CREATING TEMPLATE")
    print("-" * 70)
    
    template = learner.create_template(
        hook_patterns,
        structure_patterns,
        restructuring,
        ai_analysis,
        performance
    )
    
    if not template:
        print("❌ Template creation failed")
        return False
    
    # STEP 7: Prepare example data
    from datetime import datetime
    example_id = f"example_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    example_data = {
        "example_id": example_id,
        "comparison": comparison,
        "restructuring": restructuring,
        "hook_patterns": hook_patterns,
        "structure_patterns": structure_patterns,
        "ai_analysis": ai_analysis,
        "performance": performance,
        "clip_metadata": clip_metadata,
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }
    
    # STEP 8: Save example
    output_dir = Path("data/viral_examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    example_file = output_dir / f"{example_id}.json"
    with open(example_file, 'w') as f:
        json.dump({
            "example_id": example_id,
            "template": template,
            **example_data
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Example saved: {example_file}")
    
    # STEP 9: Update Master Learnings
    print(f"\n{'='*70}")
    print("STEP 7: UPDATING MASTER LEARNINGS")
    print("-" * 70)
    
    learner.update_master_learnings(template, example_data)
    
    # STEP 10: Create markdown documentation
    print(f"\n{'='*70}")
    print("STEP 8: CREATING MARKDOWN DOCUMENTATION")
    print("-" * 70)
    
    md_path = output_dir / f"{template['template_id']}.md"
    learner.create_markdown_doc(template, example_data, md_path)
    
    # Show results
    print(f"\n{'='*70}")
    print("✅ PIPELINE COMPLETE!")
    print(f"{'='*70}")
    
    print(f"\n📊 RESULTS:")
    print(f"   Template ID: {template['template_id']}")
    print(f"   Template Name: {template['name']}")
    print(f"   Restructuring Strategy: {restructuring.get('structure_pattern', {}).get('pattern_name', 'unknown')}")
    print(f"   Hook Pattern: {hook_patterns.get('hook_type', 'unknown')}")
    print(f"   Hook Strength: {hook_patterns.get('effectiveness', {}).get('hook_strength', 0)}/10")
    print(f"   Success Rate: {template.get('success_rate', 0):.1%}")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"   • Example JSON: {example_file}")
    print(f"   • Markdown Doc: {md_path}")
    
    # Check if MASTER_LEARNINGS was updated
    master_learnings_file = Path("data/MASTER_LEARNINGS.json")
    if master_learnings_file.exists():
        with open(master_learnings_file, 'r') as f:
            master = json.load(f)
        
        viral_examples = master.get('viral_examples', [])
        print(f"\n🔄 MASTER LEARNINGS STATUS:")
        print(f"   • Total examples: {len(viral_examples)}")
        if viral_examples:
            latest = viral_examples[-1]
            print(f"   • Latest example: {latest.get('example_id', 'unknown')}")
            print(f"   • Latest template: {latest.get('template_id', 'unknown')}")
        
        hook_formulas = master.get('hook_mastery', {}).get('hook_formulas', [])
        print(f"   • Hook formulas: {len(hook_formulas)}")
        
        winning_structures = master.get('structure_mastery', {}).get('winning_structures', [])
        print(f"   • Winning structures: {len(winning_structures)}")
    
    # Show markdown preview
    if md_path.exists():
        print(f"\n📄 MARKDOWN PREVIEW (first 30 lines):")
        print("-" * 70)
        with open(md_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:30], 1):
                print(f"{i:3d}| {line.rstrip()}")
        if len(lines) > 30:
            print(f"   ... ({len(lines) - 30} more lines)")
    
    return True


if __name__ == "__main__":
    success = test_real_example()
    sys.exit(0 if success else 1)

