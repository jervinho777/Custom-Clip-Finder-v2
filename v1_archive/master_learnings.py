#!/usr/bin/env python3
"""
🧠 MASTER LEARNINGS SYSTEM

Eine zentrale Datei für ALLE Learnings die IMMER verwendet wird.

Features:
- Auto-Update bei neuen Analysen
- Wird von create_clips.py geladen
- Kombiniert: Deep Analysis + Basic Patterns + Manual Insights
"""

import json
from pathlib import Path
from datetime import datetime


# =============================================================================
# MASTER LEARNINGS FILE PATH
# =============================================================================

MASTER_LEARNINGS_FILE = Path("data/MASTER_LEARNINGS.json")


# =============================================================================
# DEFAULT LEARNINGS (Basis-Wissen)
# =============================================================================

DEFAULT_LEARNINGS = {
    "metadata": {
        "version": "1.0",
        "last_updated": None,
        "sources": []
    },
    
    "algorithm_understanding": {
        "core_principle": "Der Algorithmus ist ein Performance-Vergleichsmechanismus mit EINEM Ziel: Watchtime maximieren",
        "key_facts": [
            "Du kämpfst gegen ALLE anderen Videos - Algorithmus ist nur Schiedsrichter",
            "Plattformen verdienen 99% durch Ads → Mehr Watchtime = Mehr Geld",
            "Kein Shadowbanning - nur schlechtere Performance als Konkurrenz",
            "Make a video so good that people cannot physically scroll past"
        ],
        "metrics_priority": ["Watch Time", "Completion Rate", "Engagement", "Session Duration"],
        "testgroup_mechanism": "Initial Test → Performance-Vergleich → Skalierung zum Gewinner"
    },
    
    "key_insights": [],
    
    "hook_mastery": {
        "winning_hook_types": [],
        "hook_formulas": [],
        "power_words": [],
        "words_to_avoid": [],
        "timing": "0-3 Sekunden KRITISCH"
    },
    
    "structure_mastery": {
        "optimal_structure": "Hook → Loop öffnen → Content mit Pattern Interrupts → Payoff",
        "pattern_interrupts": "Alle 5-7 Sekunden",
        "emotional_arc": "Achterbahn, nicht Flatline",
        "key_rules": [
            "Jede Sekunde muss Grund liefern weiterzuschauen",
            "Keine Füller, keine Langeweile",
            "Loop öffnen vor Sekunde 3, schließen am Ende"
        ]
    },
    
    "emotional_mastery": {
        "best_emotions": [],
        "trigger_phrases": [],
        "arousal_level": "High Arousal performt besser"
    },
    
    "content_rules": {
        "do_this": [],
        "never_do": []
    },
    
    "scoring_weights": {
        "hook_strength": 0.25,
        "information_gap": 0.20,
        "emotional_intensity": 0.15,
        "mass_appeal": 0.15,
        "structure_flow": 0.10,
        "simplicity": 0.10,
        "personal_address": 0.05
    }
}


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_master_learnings():
    """
    Load master learnings - creates default if not exists
    """
    
    if MASTER_LEARNINGS_FILE.exists():
        with open(MASTER_LEARNINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Create with defaults
        save_master_learnings(DEFAULT_LEARNINGS)
        return DEFAULT_LEARNINGS


def save_master_learnings(learnings):
    """
    Save master learnings
    """
    
    learnings['metadata']['last_updated'] = datetime.now().isoformat()
    
    MASTER_LEARNINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(MASTER_LEARNINGS_FILE, 'w') as f:
        json.dump(learnings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Master Learnings saved: {MASTER_LEARNINGS_FILE}")


def update_from_deep_analysis(deep_patterns_file=None):
    """
    Update master learnings from deep analysis results
    """
    
    if deep_patterns_file is None:
        deep_patterns_file = Path("data/deep_learned_patterns.json")
    
    if not deep_patterns_file.exists():
        print(f"❌ Deep patterns file not found: {deep_patterns_file}")
        return None
    
    print(f"🔄 Updating from: {deep_patterns_file}")
    
    # Load current master learnings
    master = load_master_learnings()
    
    # Load deep patterns
    with open(deep_patterns_file, 'r') as f:
        deep = json.load(f)
    
    # === UPDATE KEY INSIGHTS ===
    if 'executive_summary' in deep:
        exec_sum = deep['executive_summary']
        master['key_insights'] = [
            exec_sum.get('key_insight_1', ''),
            exec_sum.get('key_insight_2', ''),
            exec_sum.get('key_insight_3', '')
        ]
        master['key_insights'] = [i for i in master['key_insights'] if i]
    
    # === UPDATE HOOK MASTERY ===
    if 'hook_mastery' in deep:
        hm = deep['hook_mastery']
        
        if 'winning_hook_types' in hm:
            master['hook_mastery']['winning_hook_types'] = hm['winning_hook_types']
        
        if 'hook_formulas' in hm:
            master['hook_mastery']['hook_formulas'] = hm['hook_formulas']
        
        if 'power_words_for_hooks' in hm:
            master['hook_mastery']['power_words'] = hm['power_words_for_hooks']
        
        if 'hook_mistakes' in hm:
            master['hook_mastery']['words_to_avoid'] = hm['hook_mistakes']
    
    # === UPDATE STRUCTURE ===
    if 'structure_mastery' in deep:
        sm = deep['structure_mastery']
        
        if 'winning_structures' in sm:
            master['structure_mastery']['winning_structures'] = sm['winning_structures']
        
        if 'pattern_interrupt_techniques' in sm:
            master['structure_mastery']['pattern_interrupt_techniques'] = sm['pattern_interrupt_techniques']
    
    # === UPDATE EMOTIONAL ===
    if 'emotional_mastery' in deep:
        em = deep['emotional_mastery']
        
        if 'best_emotions' in em:
            master['emotional_mastery']['best_emotions'] = em['best_emotions']
        
        if 'trigger_phrases' in em:
            master['emotional_mastery']['trigger_phrases'] = em['trigger_phrases']
    
    # === UPDATE RULES ===
    if 'quick_reference' in deep:
        qr = deep['quick_reference']
        
        if 'do_this' in qr:
            master['content_rules']['do_this'] = qr['do_this']
        
        if 'never_do' in qr:
            master['content_rules']['never_do'] = qr['never_do']
    
    # === UPDATE SCORING WEIGHTS ===
    if 'scoring_weights' in deep:
        master['scoring_weights'] = deep['scoring_weights']
    
    # === UPDATE METADATA ===
    master['metadata']['sources'].append({
        'file': str(deep_patterns_file),
        'updated_at': datetime.now().isoformat(),
        'clips_analyzed': deep.get('metadata', {}).get('clips_analyzed', {})
    })
    
    # Save
    save_master_learnings(master)
    
    print(f"✅ Master Learnings updated with deep analysis insights!")
    
    return master


def get_learnings_for_prompt():
    """
    Get learnings formatted for AI prompt injection
    
    Returns a string that can be directly inserted into prompts
    """
    
    master = load_master_learnings()
    
    # Build prompt section
    prompt = """
# 🧠 GELERNTE VIRAL PATTERNS (aus {clips_analyzed} analysierten Clips)

## KEY INSIGHTS:
{key_insights}

## WINNING HOOKS:
{hooks}

## HOOK FORMELN:
{formulas}

## STRUKTUR:
{structure}

## DO THIS:
{do_this}

## NEVER DO:
{never_do}

## SCORING WEIGHTS:
{weights}
"""
    
    # Format key insights
    key_insights = "\n".join([f"• {i}" for i in master.get('key_insights', [])])
    
    # Format hooks
    hooks = ""
    for h in master.get('hook_mastery', {}).get('winning_hook_types', [])[:5]:
        if isinstance(h, dict):
            hooks += f"• {h.get('type', 'Unknown')}: {h.get('template', '')}\n"
        else:
            hooks += f"• {h}\n"
    
    # Format formulas
    formulas = "\n".join([f"• {f}" for f in master.get('hook_mastery', {}).get('hook_formulas', [])[:5]])
    
    # Format structure
    structure_rules = master.get('structure_mastery', {}).get('key_rules', [])
    structure = "\n".join([f"• {r}" for r in structure_rules])
    
    # Format do/don't
    do_this = "\n".join([f"✅ {d}" for d in master.get('content_rules', {}).get('do_this', [])[:7]])
    never_do = "\n".join([f"❌ {d}" for d in master.get('content_rules', {}).get('never_do', [])[:7]])
    
    # Format weights
    weights = json.dumps(master.get('scoring_weights', {}), indent=2)
    
    # Get clips analyzed count
    sources = master.get('metadata', {}).get('sources', [])
    clips_analyzed = 0
    if sources:
        last_source = sources[-1]
        clips_analyzed = last_source.get('clips_analyzed', {}).get('total', 0)
    
    return prompt.format(
        clips_analyzed=clips_analyzed,
        key_insights=key_insights or "Noch keine Insights",
        hooks=hooks or "Noch keine Hooks",
        formulas=formulas or "Noch keine Formeln",
        structure=structure or "Standard-Struktur",
        do_this=do_this or "Noch keine Do's",
        never_do=never_do or "Noch keine Don'ts",
        weights=weights
    )


def print_learnings_summary():
    """
    Print a summary of current learnings
    """
    
    master = load_master_learnings()
    
    print("\n" + "="*70)
    print("🧠 MASTER LEARNINGS SUMMARY")
    print("="*70)
    
    # Metadata
    meta = master.get('metadata', {})
    print(f"\n📅 Last Updated: {meta.get('last_updated', 'Never')}")
    print(f"📊 Sources: {len(meta.get('sources', []))}")
    
    # Key Insights
    print(f"\n💡 KEY INSIGHTS:")
    for i, insight in enumerate(master.get('key_insights', [])[:5], 1):
        print(f"   {i}. {insight}")
    
    # Hooks
    print(f"\n🪝 WINNING HOOKS:")
    for h in master.get('hook_mastery', {}).get('winning_hook_types', [])[:3]:
        if isinstance(h, dict):
            print(f"   • {h.get('type', '?')}: {h.get('template', '')[:60]}...")
    
    # Do/Don't
    print(f"\n✅ DO THIS:")
    for d in master.get('content_rules', {}).get('do_this', [])[:5]:
        print(f"   • {d}")
    
    print(f"\n❌ NEVER DO:")
    for d in master.get('content_rules', {}).get('never_do', [])[:5]:
        print(f"   • {d}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("🧠 MASTER LEARNINGS SYSTEM")
    print("="*70)
    
    print("\n📝 OPTIONS:")
    print("   1. 📋 Show current learnings")
    print("   2. 🔄 Update from deep analysis")
    print("   3. 📝 Get prompt-ready learnings")
    print("   4. 🔧 Reset to defaults")
    
    choice = input("\nChoice (1-4): ").strip()
    
    if choice == '1':
        print_learnings_summary()
    
    elif choice == '2':
        update_from_deep_analysis()
        print_learnings_summary()
    
    elif choice == '3':
        prompt = get_learnings_for_prompt()
        print(prompt)
    
    elif choice == '4':
        confirm = input("⚠️ Reset all learnings? (y/n): ").strip().lower()
        if confirm == 'y':
            save_master_learnings(DEFAULT_LEARNINGS)
            print("✅ Reset to defaults")
