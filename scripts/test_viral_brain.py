#!/usr/bin/env python3
"""
Test Script: Viral Brain Prompt Generator

Verifies that the Fusion Engine correctly combines:
- Strategic insights from learned_patterns.json (967+ clips)
- Tactical rules from editing_patterns.json (pair deep-dives)

Usage:
    uv run python scripts/test_viral_brain.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from prompts.viral_editor import ViralBrainPrompt, build_viral_prompt


# =============================================================================
# Test Data
# =============================================================================

DUMMY_TRANSCRIPT = """
Hallo zusammen und herzlich willkommen zu meinem Vortrag. Ich freue mich sehr, 
dass ihr alle hier seid. Bevor wir anfangen, möchte ich kurz erzählen, wie ich 
hierher gekommen bin.

Also, ich war vor einigen Jahren in einer schwierigen Situation. Ich hatte meinen 
Job verloren, meine Beziehung war am Ende, und ich wusste nicht mehr weiter. 
Jeden Tag saß ich zu Hause und dachte: "Warum passiert mir das alles?"

Aber dann, eines Tages, traf ich einen alten Mann in einem Café. Er sah mich an 
und sagte etwas, das mein Leben für immer verändert hat. Er sagte: "Junger Mann, 
das Problem ist nicht, dass du Geld verdienen musst. Das Problem ist, dass du 
für Geld arbeitest. Arbeite niemals für Geld."

Ich habe ihn erst nicht verstanden. Was meinte er damit? Aber nach Wochen des 
Nachdenkens wurde mir klar: Er meinte, dass Leidenschaft und Wert-Schöpfung 
vor dem Gehalt kommen müssen. Wenn du das tust, was du liebst, und dabei Wert 
für andere schaffst, wird das Geld von alleine kommen.

Und genau das habe ich dann gemacht. Ich habe aufgehört, nur für das Gehalt zu 
arbeiten, und angefangen, an meiner Vision zu arbeiten. Drei Jahre später habe 
ich mein eigenes Unternehmen gegründet, und heute sind wir profitabel.

Die Lektion? Arbeite niemals für Geld. Arbeite für deinen Traum.

Vielen Dank fürs Zuhören!
"""


# =============================================================================
# Test Functions
# =============================================================================

def test_initialization():
    """Test that the generator initializes correctly."""
    print("\n" + "="*70)
    print("🧪 TEST 1: Initialization")
    print("="*70)
    
    generator = ViralBrainPrompt()
    stats = generator.get_stats()
    
    print(f"\n📊 Loaded Data:")
    print(f"   Archetypes: {stats['archetypes_loaded']}")
    print(f"   Rules: {stats['rules_loaded']}")
    print(f"   Examples: {stats['examples_loaded']}")
    print(f"   learned_patterns.json: {'✅' if stats['learned_patterns_available'] else '❌'}")
    print(f"   editing_patterns.json: {'✅' if stats['editing_patterns_available'] else '❌'}")
    
    return generator


def test_prompt_generation(generator: ViralBrainPrompt):
    """Test prompt generation with dummy transcript."""
    print("\n" + "="*70)
    print("🧪 TEST 2: Prompt Generation")
    print("="*70)
    
    prompt = generator.build(DUMMY_TRANSCRIPT)
    
    print(f"\n📝 Generated Prompt Length: {len(prompt)} characters")
    print(f"   Lines: {prompt.count(chr(10))}")
    
    # Verify sections exist
    sections_found = {
        "Identity & Strategy": "IDENTITY & STRATEGY" in prompt,
        "Tactical Rules": "TACTICAL EXECUTION RULES" in prompt,
        "Few-Shot Examples": "LEARNING FROM EXAMPLES" in prompt,
        "Task": "YOUR TASK" in prompt,
        "Transcript Included": "Arbeite niemals für Geld" in prompt,
        "Output Format": "archetype" in prompt and "edited_transcript" in prompt,
    }
    
    print(f"\n🔍 Section Verification:")
    all_passed = True
    for section, found in sections_found.items():
        status = "✅" if found else "❌"
        print(f"   {status} {section}")
        if not found:
            all_passed = False
    
    return prompt, all_passed


def test_archetypes_in_prompt(prompt: str, generator: ViralBrainPrompt):
    """Verify archetypes from learned_patterns.json appear in prompt."""
    print("\n" + "="*70)
    print("🧪 TEST 3: Strategic Insights (from 967+ clips)")
    print("="*70)
    
    if not generator.archetypes:
        print("\n   ⚠️ No archetypes loaded - skipping test")
        return True
    
    print(f"\n📋 Checking for {len(generator.archetypes)} archetypes:")
    
    found_count = 0
    for arch in generator.archetypes[:5]:
        found = arch.name in prompt
        status = "✅" if found else "❌"
        print(f"   {status} {arch.name}")
        if found:
            found_count += 1
    
    print(f"\n   Found {found_count}/{len(generator.archetypes[:5])} archetypes in prompt")
    return found_count > 0


def test_rules_in_prompt(prompt: str, generator: ViralBrainPrompt):
    """Verify tactical rules from editing_patterns.json appear in prompt."""
    print("\n" + "="*70)
    print("🧪 TEST 4: Tactical Rules (from pair deep-dives)")
    print("="*70)
    
    if not generator.top_rules:
        print("\n   ⚠️ No rules loaded - skipping test")
        return True
    
    print(f"\n📋 Checking for {len(generator.top_rules)} rules:")
    
    found_count = 0
    for rule in generator.top_rules[:5]:
        # Check if rule text appears in prompt
        found = rule.rule[:30] in prompt if rule.rule else False
        status = "✅" if found else "❌"
        print(f"   {status} {rule.rule[:50]}...")
        if found:
            found_count += 1
    
    print(f"\n   Found {found_count}/{len(generator.top_rules[:5])} rules in prompt")
    return found_count > 0


def print_full_prompt(prompt: str):
    """Print the complete generated prompt."""
    print("\n" + "="*70)
    print("📄 FULL GENERATED PROMPT")
    print("="*70)
    print(prompt)
    print("\n" + "="*70)
    print("📄 END OF PROMPT")
    print("="*70)


# =============================================================================
# Main
# =============================================================================

def main():
    print("\n" + "🧠"*35)
    print("   VIRAL BRAIN PROMPT GENERATOR - TEST SUITE")
    print("🧠"*35)
    
    # Test 1: Initialization
    generator = test_initialization()
    
    # Test 2: Prompt Generation
    prompt, sections_ok = test_prompt_generation(generator)
    
    # Test 3: Archetypes (Strategic)
    archetypes_ok = test_archetypes_in_prompt(prompt, generator)
    
    # Test 4: Rules (Tactical)
    rules_ok = test_rules_in_prompt(prompt, generator)
    
    # Print full prompt for inspection
    print_full_prompt(prompt)
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    stats = generator.get_stats()
    
    tests = {
        "Data Loading": stats['archetypes_loaded'] > 0 or stats['rules_loaded'] > 0,
        "Section Structure": sections_ok,
        "Strategic Insights (Archetypes)": archetypes_ok,
        "Tactical Rules": rules_ok,
    }
    
    all_passed = all(tests.values())
    
    for test_name, passed in tests.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Fusion Engine is operational!")
    else:
        print("⚠️ SOME TESTS FAILED - Check data files")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

