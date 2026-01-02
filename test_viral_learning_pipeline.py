#!/usr/bin/env python3
"""
🧪 TEST SCRIPT: Viral Learning Pipeline

Tests the complete pipeline:
1. compare_transcripts()
2. analyze_restructuring()
3. extract_hook_patterns()
4. extract_structure_patterns()
5. ai_analyze_example()
6. create_template()
"""

import json
import sys
from pathlib import Path
from learn_from_viral_example import ViralExampleLearner


def create_test_data():
    """Create test data for pipeline testing"""
    
    # Mock longform segments
    longform_segments = [
        {"text": "Hallo und willkommen zu diesem Video", "start": 0.0, "end": 3.0},
        {"text": "Heute sprechen wir über ein wichtiges Thema", "start": 3.0, "end": 7.0},
        {"text": "Viele Leute machen diesen Fehler", "start": 7.0, "end": 11.0},
        {"text": "Warum der größte Fehler bei Social Media ist", "start": 120.0, "end": 125.0},  # Hook
        {"text": "Die meisten Menschen denken", "start": 125.0, "end": 130.0},
        {"text": "Aber die Wahrheit ist anders", "start": 130.0, "end": 135.0},
        {"text": "Hier ist warum", "start": 135.0, "end": 138.0},
        {"text": "Wenn du das verstehst", "start": 200.0, "end": 205.0},  # Payoff
        {"text": "Dann wirst du erfolgreich sein", "start": 205.0, "end": 210.0},
    ]
    
    # Mock clip segments (restructured)
    clip_segments = [
        {"text": "Warum der größte Fehler bei Social Media ist", "start": 0.0, "end": 3.0},  # Hook moved to front
        {"text": "Die meisten Menschen denken", "start": 3.0, "end": 7.0},  # Context
        {"text": "Aber die Wahrheit ist anders", "start": 7.0, "end": 12.0},  # Content
        {"text": "Wenn du das verstehst", "start": 12.0, "end": 15.0},  # Payoff
    ]
    
    # Mock performance
    performance = {
        "views": 500000,
        "watch_time": 85,
        "followers": 5000
    }
    
    return longform_segments, clip_segments, performance


def test_pipeline():
    """Test the complete pipeline"""
    
    print("="*70)
    print("🧪 TESTING VIRAL LEARNING PIPELINE")
    print("="*70)
    
    # Initialize learner
    learner = ViralExampleLearner()
    
    if not learner.client:
        print("\n⚠️  No API key - AI analysis will be skipped")
        print("   Testing non-AI functions only...")
    
    # Create test data
    print("\n📊 Creating test data...")
    longform_segments, clip_segments, performance = create_test_data()
    
    print(f"   ✅ Longform: {len(longform_segments)} segments")
    print(f"   ✅ Clip: {len(clip_segments)} segments")
    print(f"   ✅ Performance: {performance['views']:,} views, {performance['watch_time']}% watch time")
    
    # STEP 1: Compare transcripts
    print(f"\n{'='*70}")
    print("STEP 1: compare_transcripts()")
    print("-" * 70)
    
    comparison = learner.compare_transcripts(longform_segments, clip_segments)
    
    if not comparison:
        print("❌ Comparison failed")
        return False
    
    print(f"✅ Comparison successful")
    print(f"   Used segments: {len(comparison.get('used_segments', []))}")
    print(f"   Reordered: {comparison.get('restructuring', {}).get('reordered', False)}")
    
    # STEP 2: Analyze restructuring
    print(f"\n{'='*70}")
    print("STEP 2: analyze_restructuring()")
    print("-" * 70)
    
    restructuring = learner.analyze_restructuring(comparison, clip_segments, performance)
    
    if not restructuring:
        print("❌ Restructuring analysis failed")
        return False
    
    print(f"✅ Restructuring analysis successful")
    print(f"   Hook moved to front: {restructuring.get('hook_strategy', {}).get('moved_to_front', False)}")
    print(f"   Structure pattern: {restructuring.get('structure_pattern', {}).get('pattern_name', 'unknown')}")
    
    # STEP 3: Extract hook patterns
    print(f"\n{'='*70}")
    print("STEP 3: extract_hook_patterns()")
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
    
    print(f"✅ Hook patterns extracted")
    print(f"   Hook type: {hook_patterns.get('hook_type', 'unknown')}")
    print(f"   Hook strength: {hook_patterns.get('effectiveness', {}).get('hook_strength', 0)}/10")
    
    # STEP 4: Extract structure patterns
    print(f"\n{'='*70}")
    print("STEP 4: extract_structure_patterns()")
    print("-" * 70)
    
    structure_patterns = learner.extract_structure_patterns(
        clip_segments,
        restructuring,
        performance
    )
    
    if not structure_patterns:
        print("❌ Structure patterns extraction failed")
        return False
    
    print(f"✅ Structure patterns extracted")
    print(f"   Structure: {structure_patterns.get('structure_name', 'unknown')}")
    print(f"   Pattern interrupts: {len(structure_patterns.get('timing', {}).get('pattern_interrupts', []))}")
    
    # STEP 5: AI analysis (if available)
    print(f"\n{'='*70}")
    print("STEP 5: ai_analyze_example()")
    print("-" * 70)
    
    ai_analysis = {}
    if learner.client:
        ai_analysis = learner.ai_analyze_example(
            longform_segments,
            clip_segments,
            comparison,
            restructuring,
            performance,
            notes="Test example",
            deep_analysis=False
        )
        
        if ai_analysis:
            print(f"✅ AI analysis successful")
            print(f"   Success factors: {len(ai_analysis.get('analysis', {}).get('key_success_factors', []))}")
        else:
            print("⚠️  AI analysis returned empty result")
    else:
        print("⚠️  Skipped (no API key)")
    
    # STEP 6: Create template
    print(f"\n{'='*70}")
    print("STEP 6: create_template()")
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
    
    print(f"✅ Template created")
    print(f"   Template ID: {template.get('template_id', 'unknown')}")
    print(f"   Name: {template.get('name', 'unknown')}")
    print(f"   Success rate: {template.get('success_rate', 0):.2f}")
    
    # Save results
    output_file = Path("output/test_pipeline_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    results = {
        "comparison": comparison,
        "restructuring": restructuring,
        "hook_patterns": hook_patterns,
        "structure_patterns": structure_patterns,
        "ai_analysis": ai_analysis,
        "template": template
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print("✅ PIPELINE TEST COMPLETE!")
    print(f"{'='*70}")
    print(f"\n💾 Results saved: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   • Comparison: ✅")
    print(f"   • Restructuring: ✅")
    print(f"   • Hook Patterns: ✅")
    print(f"   • Structure Patterns: ✅")
    print(f"   • AI Analysis: {'✅' if ai_analysis else '⚠️ Skipped'}")
    print(f"   • Template: ✅")
    
    return True


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)

