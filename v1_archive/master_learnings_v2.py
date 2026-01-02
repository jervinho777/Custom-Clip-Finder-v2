#!/usr/bin/env python3
"""
🧠 MASTER LEARNINGS V2 - Enhanced Multi-Source System

IMPROVEMENTS:
- Merges learnings from multiple sources
- Weighted by performance data
- Better prompt formatting for V4
- Tracks source quality
- Progressive updates
- Validation & deduplication

SOURCES:
1. learned_patterns_v2.json (from analyze_and_learn_v2.py)
2. deep_learned_patterns.json (from smart_sampling_v2.py)
3. Manual insights (optional)

OUTPUT: MASTER_LEARNINGS.json (optimized for V4)
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List


MASTER_LEARNINGS_FILE = Path("data/MASTER_LEARNINGS.json")


DEFAULT_LEARNINGS = {
    "metadata": {
        "version": "2.0",
        "last_updated": None,
        "sources": [],
        "total_clips_analyzed": 0
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
        "testgroup_mechanism": "Initial Test → Performance-Vergleich → Skalierung zum Gewinner",
        "watchtime_optimization": {
            "hook_critical": "Hook (0-3s): Wenn User hier abspringen, kostest du die Plattform Geld → Algorithmus stoppt Video",
            "pattern_interrupts": "Alle 5-7 Sekunden: Verhindern Drop-off → Höhere Retention → Mehr Watch Time",
            "information_gap": "Hält User dran → Höhere Completion → Algorithmus skaliert",
            "emotional_arousal": "High Arousal → Mehr Engagement → Algorithmus bevorzugt",
            "loop_mechanics": "Loop Opening/Closing: Gehirn will Abschluss → Höhere Completion → Algorithmus belohnt"
        },
        "virality_triggers": [
            "Mass Appeal - Spricht breite Masse an?",
            "Humor - Lustig?",
            "Berühmtheiten - Halo-Effekt?",
            "Headline/Hook - Öffnet Loops? Erste 3 Sekunden?",
            "Storytime - Spannende Geschichte?",
            "Kontroverse - Meinungsverschiedenheiten?",
            "Learning - Direkt anwendbar? Speichern?",
            "Shareability - Weitersenden?",
            "Einfachheit - Nach 1x schauen klar?",
            "Primacy-Recency - Erster & letzter Eindruck?",
            "Information Gap - Nach 1. Satz dranbleiben?",
            "Trend - Aktuell? Im Trend?"
        ],
        "clip_structure": {
            "hook_0_3s": "KRITISCH! Muss SOFORT Spannung aufbauen. KEIN 'Hallo', KEIN Intro, direkt rein. Stärkster Moment ZUERST.",
            "loop_3_10s": "Unvollständiger Loop öffnen (Gehirn will Abschluss). Versprechen was kommt.",
            "content_with_interrupts": "Jede Sekunde muss Grund liefern weiterzuschauen. Alle 5-7 Sekunden: Mini-Payoff oder neuer Hook. Emotionale Achterbahn statt Flatline.",
            "payoff_end": "Loop schließen. Satisfying Conclusion. Optional: Neuer Loop für nächstes Video."
        },
        "cialdini_principles": [
            "Reciprocity: Gib Wert zuerst",
            "Commitment: Kleine Zusagen",
            "Social Proof: Zahlen, Testimonials",
            "Authority: Expertise zeigen",
            "Liking: Authentisch, relatable",
            "Scarcity: FOMO erzeugen"
        ],
        "brutal_truth": "Vergiss Trends, Hashtags, Posting-Zeiten - das ist alles sekundär. Der Algorithmus wird IMMER das Video bevorzugen, das Menschen länger auf der Plattform hält. Deine Videos müssen so gut sein, dass sie zur Cashcow der Plattform werden."
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


def load_master_learnings():
    """Load master learnings"""
    
    if MASTER_LEARNINGS_FILE.exists():
        with open(MASTER_LEARNINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        save_master_learnings(DEFAULT_LEARNINGS)
        return DEFAULT_LEARNINGS


def save_master_learnings(learnings):
    """Save master learnings"""
    
    learnings['metadata']['last_updated'] = datetime.now().isoformat()
    
    MASTER_LEARNINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(MASTER_LEARNINGS_FILE, 'w') as f:
        json.dump(learnings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Master Learnings saved: {MASTER_LEARNINGS_FILE}")


def update_from_all_sources():
    """
    Update master learnings from ALL available sources
    
    Priority:
    1. deep_learned_patterns.json (detailed analysis)
    2. learned_patterns_v2.json (broad patterns)
    3. Existing MASTER_LEARNINGS.json (preserve manual edits)
    """
    
    print("\n" + "="*70)
    print("🔄 UPDATING MASTER LEARNINGS FROM ALL SOURCES")
    print("="*70)
    
    # Load current master
    master = load_master_learnings()
    
    # Source files
    sources = [
        ('deep_learned_patterns.json', 'Deep Analysis', 1.0),  # Highest weight
        ('learned_patterns_v2.json', 'Broad Patterns', 0.8),
        ('deep_learned_patterns_old.json', 'Legacy Deep', 0.5)
    ]
    
    patterns_merged = 0
    
    for filename, source_name, weight in sources:
        filepath = Path("data") / filename
        
        if not filepath.exists():
            print(f"   ⚠️  {source_name}: Not found ({filename})")
            continue
        
        print(f"\n   📄 Processing: {source_name} (weight: {weight})")
        
        try:
            with open(filepath, 'r') as f:
                source_data = json.load(f)
            
            # Merge patterns
            merged = _merge_source_into_master(master, source_data, weight)
            
            if merged:
                patterns_merged += 1
                
                # Track source
                clips_analyzed = source_data.get('metadata', {}).get('clips_analyzed', {})
                if isinstance(clips_analyzed, dict):
                    clips_total = clips_analyzed.get('total', 0)
                elif isinstance(clips_analyzed, int):
                    clips_total = clips_analyzed
                else:
                    clips_total = 0
                
                master['metadata']['sources'].append({
                    'file': filename,
                    'name': source_name,
                    'weight': weight,
                    'updated_at': datetime.now().isoformat(),
                    'clips_analyzed': clips_total
                })
                
                print(f"      ✅ Merged successfully")
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
            import traceback
            print(f"      Detail: {traceback.format_exc()[:200]}")
    
    if patterns_merged == 0:
        print("\n   ⚠️  No sources found to merge!")
        return None
    
    # Calculate total clips analyzed
    total_clips = 0
    for source in master['metadata']['sources']:
        clips_data = source.get('clips_analyzed', 0)
        if isinstance(clips_data, (int, float)):
            total_clips += int(clips_data)
    
    master['metadata']['total_clips_analyzed'] = total_clips
    
    # Deduplicate & clean
    master = _deduplicate_and_clean(master)
    
    # Save
    save_master_learnings(master)
    
    print(f"\n✅ Master Learnings updated from {patterns_merged} sources!")
    print(f"   📊 Total clips analyzed: {total_clips}")
    
    return master


def _merge_source_into_master(master, source, weight):
    """
    Merge source patterns into master with weighting
    """
    
    # === KEY INSIGHTS ===
    if 'executive_summary' in source:
        exec_sum = source['executive_summary']
        insights = [
            exec_sum.get('key_insight_1', ''),
            exec_sum.get('key_insight_2', ''),
            exec_sum.get('key_insight_3', '')
        ]
        insights = [i for i in insights if i]
        
        # Add to master (deduplicate later)
        for insight in insights:
            if insight and insight not in master['key_insights']:
                master['key_insights'].append(insight)
    
    # Also check 'key_insights' field
    if 'key_insights' in source:
        for insight in source['key_insights']:
            if insight and insight not in master['key_insights']:
                master['key_insights'].append(insight)
    
    # === HOOK MASTERY ===
    if 'hook_mastery' in source:
        hm = source['hook_mastery']
        
        # Winning hook types
        if 'winning_hook_types' in hm:
            for hook in hm['winning_hook_types']:
                if hook not in master['hook_mastery']['winning_hook_types']:
                    master['hook_mastery']['winning_hook_types'].append(hook)
        
        # Hook formulas
        if 'hook_formulas' in hm:
            for formula in hm['hook_formulas']:
                if formula and formula not in master['hook_mastery']['hook_formulas']:
                    master['hook_mastery']['hook_formulas'].append(formula)
        
        # Power words
        if 'power_words_for_hooks' in hm:
            for word in hm['power_words_for_hooks']:
                if word and word not in master['hook_mastery']['power_words']:
                    master['hook_mastery']['power_words'].append(word)
    
    # === STRUCTURE ===
    if 'structure_mastery' in source:
        sm = source['structure_mastery']
        
        if 'winning_structures' in sm:
            for structure in sm['winning_structures']:
                if structure not in master['structure_mastery'].get('winning_structures', []):
                    if 'winning_structures' not in master['structure_mastery']:
                        master['structure_mastery']['winning_structures'] = []
                    master['structure_mastery']['winning_structures'].append(structure)
    
    # === EMOTIONAL ===
    if 'emotional_mastery' in source:
        em = source['emotional_mastery']
        
        if 'best_emotions' in em:
            for emotion in em['best_emotions']:
                if emotion not in master['emotional_mastery']['best_emotions']:
                    master['emotional_mastery']['best_emotions'].append(emotion)
    
    # === RULES ===
    if 'quick_reference' in source:
        qr = source['quick_reference']
        
        if 'do_this' in qr:
            for rule in qr['do_this']:
                if rule and rule not in master['content_rules']['do_this']:
                    master['content_rules']['do_this'].append(rule)
        
        if 'never_do' in qr:
            for rule in qr['never_do']:
                if rule and rule not in master['content_rules']['never_do']:
                    master['content_rules']['never_do'].append(rule)
    
    # === SCORING WEIGHTS (use latest) ===
    if 'scoring_weights' in source:
        master['scoring_weights'] = source['scoring_weights']
    
    return True


def _deduplicate_and_clean(master):
    """
    Remove duplicates and clean up patterns
    """
    
    # Deduplicate key insights (keep first occurrence)
    seen = set()
    unique_insights = []
    for insight in master['key_insights']:
        # Normalize for comparison
        normalized = insight.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique_insights.append(insight)
    
    master['key_insights'] = unique_insights[:15]  # Keep top 15
    
    # Deduplicate hook formulas
    master['hook_mastery']['hook_formulas'] = list(dict.fromkeys(
        master['hook_mastery']['hook_formulas']
    ))[:20]  # Keep top 20
    
    # Deduplicate power words (case-insensitive)
    seen_words = set()
    unique_words = []
    for word in master['hook_mastery']['power_words']:
        word_lower = word.lower()
        if word_lower not in seen_words:
            seen_words.add(word_lower)
            unique_words.append(word)
    
    master['hook_mastery']['power_words'] = unique_words[:50]  # Keep top 50
    
    # Deduplicate rules
    master['content_rules']['do_this'] = list(dict.fromkeys(
        master['content_rules']['do_this']
    ))[:15]
    
    master['content_rules']['never_do'] = list(dict.fromkeys(
        master['content_rules']['never_do']
    ))[:15]
    
    return master


def get_learnings_for_prompt():
    """
    Get learnings formatted for AI prompt injection
    
    Optimized for V4 integration
    Includes algorithm context at TOP
    """
    
    master = load_master_learnings()
    
    # Build comprehensive prompt with algorithm context FIRST
    prompt = f"""{_format_algorithm_context(master.get('algorithm_understanding', {}))}

---

# 🧠 GELERNTE VIRAL PATTERNS ({master.get('metadata', {}).get('total_clips_analyzed', 0)} analysierte Clips)

## 🎯 KEY INSIGHTS:
{_format_list(master.get('key_insights', [])[:10])}

## 🪝 WINNING HOOKS:
{_format_hooks(master.get('hook_mastery', {}).get('winning_hook_types', [])[:8])}

## 📐 HOOK FORMELN:
{_format_list(master.get('hook_mastery', {}).get('hook_formulas', [])[:8])}

## 💪 POWER WORDS:
{', '.join(master.get('hook_mastery', {}).get('power_words', [])[:30])}

## 🏗️ STRUKTUR REGELN:
{_format_list(master.get('structure_mastery', {}).get('key_rules', []))}

## 😊 BESTE EMOTIONEN:
{_format_emotions(master.get('emotional_mastery', {}).get('best_emotions', [])[:5])}

## ✅ DO THIS:
{_format_list(master.get('content_rules', {}).get('do_this', [])[:10])}

## ❌ NEVER DO:
{_format_list(master.get('content_rules', {}).get('never_do', [])[:10])}

## 📊 SCORING WEIGHTS:
{json.dumps(master.get('scoring_weights', {}), indent=2)}
"""
    
    return prompt


def _format_list(items):
    """Format list for prompt"""
    if not items:
        return "Noch keine Daten"
    return "\n".join([f"• {item}" for item in items])


def _format_hooks(hooks):
    """Format hook types for prompt"""
    if not hooks:
        return "Noch keine Hooks"
    
    formatted = []
    for hook in hooks:
        if isinstance(hook, dict):
            hook_type = hook.get('type', 'Unknown')
            template = hook.get('template', '')
            example = hook.get('example', '')
            
            formatted.append(f"• {hook_type.upper()}: {template}")
            if example:
                formatted.append(f"  Beispiel: \"{example[:60]}...\"")
        else:
            formatted.append(f"• {hook}")
    
    return "\n".join(formatted)


def _format_emotions(emotions):
    """Format emotions for prompt"""
    if not emotions:
        return "Noch keine Daten"
    
    formatted = []
    for emotion in emotions:
        if isinstance(emotion, dict):
            name = emotion.get('emotion', 'unknown')
            freq = emotion.get('frequency', 0)
            formatted.append(f"• {name} ({freq}x)")
        else:
            formatted.append(f"• {emotion}")
    
    return "\n".join(formatted)


def _format_algorithm_context(algorithm_understanding):
    """Format algorithm understanding for prompt"""
    
    if not algorithm_understanding:
        return "# 🎯 ALGORITHM CONTEXT\n\nNoch keine Daten"
    
    context = f"""# 🎯 ALGORITHM CONTEXT - CRITICAL FOR PATTERN UNDERSTANDING

## CORE PRINCIPLE:
{algorithm_understanding.get('core_principle', 'N/A')}

## KEY FACTS:
{_format_list(algorithm_understanding.get('key_facts', []))}

## METRICS PRIORITY (what algorithm optimizes):
{_format_list(algorithm_understanding.get('metrics_priority', []))}

## TESTGROUP MECHANISM:
{algorithm_understanding.get('testgroup_mechanism', 'N/A')}

## WATCHTIME OPTIMIZATION (why patterns work):
"""
    
    wt_opt = algorithm_understanding.get('watchtime_optimization', {})
    if wt_opt:
        context += f"""
- Hook (0-3s): {wt_opt.get('hook_critical', 'N/A')}
- Pattern Interrupts: {wt_opt.get('pattern_interrupts', 'N/A')}
- Information Gap: {wt_opt.get('information_gap', 'N/A')}
- Emotional Arousal: {wt_opt.get('emotional_arousal', 'N/A')}
- Loop Mechanics: {wt_opt.get('loop_mechanics', 'N/A')}
"""
    
    context += f"""
## VIRALITY TRIGGERS (12 factors):
{_format_list(algorithm_understanding.get('virality_triggers', [])[:12])}

## CLIP STRUCTURE FOR MAX WATCHTIME:
"""
    
    structure = algorithm_understanding.get('clip_structure', {})
    if structure:
        context += f"""
- HOOK (0-3s): {structure.get('hook_0_3s', 'N/A')}
- LOOP (3-10s): {structure.get('loop_3_10s', 'N/A')}
- CONTENT: {structure.get('content_with_interrupts', 'N/A')}
- PAYOFF: {structure.get('payoff_end', 'N/A')}
"""
    
    context += f"""
## CIALDINI PRINCIPLES:
{_format_list(algorithm_understanding.get('cialdini_principles', []))}

## BRUTAL TRUTH:
{algorithm_understanding.get('brutal_truth', 'N/A')}
"""
    
    return context


def print_learnings_summary():
    """Print summary of current learnings"""
    
    master = load_master_learnings()
    
    print("\n" + "="*70)
    print("🧠 MASTER LEARNINGS SUMMARY")
    print("="*70)
    
    # Metadata
    meta = master.get('metadata', {})
    print(f"\n📅 Last Updated: {meta.get('last_updated', 'Never')}")
    print(f"📊 Sources: {len(meta.get('sources', []))}")
    print(f"📊 Total Clips Analyzed: {meta.get('total_clips_analyzed', 0)}")
    
    # Key Insights
    print(f"\n💡 KEY INSIGHTS ({len(master.get('key_insights', []))}):")
    for i, insight in enumerate(master.get('key_insights', [])[:5], 1):
        print(f"   {i}. {insight[:80]}...")
    
    # Hooks
    hooks = master.get('hook_mastery', {}).get('winning_hook_types', [])
    print(f"\n🪝 WINNING HOOKS ({len(hooks)}):")
    for hook in hooks[:3]:
        if isinstance(hook, dict):
            print(f"   • {hook.get('type', '?')}: {hook.get('template', '')[:60]}...")
    
    # Power Words
    words = master.get('hook_mastery', {}).get('power_words', [])
    print(f"\n💪 POWER WORDS ({len(words)}):")
    print(f"   {', '.join(words[:20])}")
    
    # Do/Don't
    print(f"\n✅ DO THIS ({len(master.get('content_rules', {}).get('do_this', []))}):")
    for rule in master.get('content_rules', {}).get('do_this', [])[:5]:
        print(f"   • {rule[:70]}...")
    
    print(f"\n❌ NEVER DO ({len(master.get('content_rules', {}).get('never_do', []))}):")
    for rule in master.get('content_rules', {}).get('never_do', [])[:5]:
        print(f"   • {rule[:70]}...")


# =============================================================================
# CLI
# =============================================================================

def validate_learnings_application(response_text: str) -> Dict:
    """
    Validate that AI actually used learnings in response
    
    Checks for:
    - Pattern references (hook types, structures)
    - Power word usage
    - Algorithm reasoning
    
    Returns confidence score 0-1
    """
    
    master = load_master_learnings()
    
    validation = {
        'learnings_applied': False,
        'patterns_referenced': [],
        'power_words_used': [],
        'algorithm_reasoning_present': False,
        'confidence': 0.0,
        'quality_score': 'unknown'
    }
    
    response_lower = response_text.lower()
    
    # 1. Check for pattern references
    hook_types = master.get('hook_mastery', {}).get('winning_hook_types', [])
    for hook in hook_types:
        if isinstance(hook, dict):
            hook_type = hook.get('type', '').lower()
            if hook_type in response_lower:
                validation['patterns_referenced'].append(hook_type)
        elif isinstance(hook, str):
            if hook.lower() in response_lower:
                validation['patterns_referenced'].append(hook)
    
    # 2. Check for power words
    power_words = master.get('hook_mastery', {}).get('power_words', [])
    for word in power_words[:30]:  # Check top 30
        if word.lower() in response_lower:
            validation['power_words_used'].append(word)
    
    # 3. Check for algorithm reasoning
    algo_keywords = [
        'watchtime', 'watch time', 'watch-time',
        'completion', 'completion rate',
        'algorithm', 'algorithmus',
        'drop-off', 'retention',
        'session duration',
        'scroll', 'scrolling',
        'information gap', 'loop'
    ]
    
    algo_count = 0
    for keyword in algo_keywords:
        if keyword in response_lower:
            algo_count += 1
            validation['algorithm_reasoning_present'] = True
    
    # 4. Calculate confidence score
    score = 0.0
    
    # Patterns referenced (40% weight)
    if len(validation['patterns_referenced']) >= 2:
        score += 0.40
    elif len(validation['patterns_referenced']) == 1:
        score += 0.20
    
    # Power words used (30% weight)
    if len(validation['power_words_used']) >= 3:
        score += 0.30
    elif len(validation['power_words_used']) >= 1:
        score += 0.15
    
    # Algorithm reasoning (30% weight)
    if algo_count >= 2:
        score += 0.30
    elif algo_count >= 1:
        score += 0.15
    
    validation['confidence'] = score
    validation['learnings_applied'] = score >= 0.40  # Threshold
    
    # Quality assessment
    if score >= 0.70:
        validation['quality_score'] = 'excellent'
    elif score >= 0.50:
        validation['quality_score'] = 'good'
    elif score >= 0.30:
        validation['quality_score'] = 'fair'
    else:
        validation['quality_score'] = 'poor'
    
    return validation


def print_validation_report(validation: Dict):
    """Print validation report"""
    
    print(f"\n   🔍 VALIDATION REPORT:")
    print(f"      Confidence: {validation['confidence']:.0%}")
    print(f"      Quality: {validation['quality_score'].upper()}")
    print(f"      Learnings Applied: {'✅' if validation['learnings_applied'] else '❌'}")
    
    if validation['patterns_referenced']:
        print(f"      Patterns: {', '.join(validation['patterns_referenced'][:3])}")
    
    if validation['power_words_used']:
        print(f"      Power Words: {', '.join(validation['power_words_used'][:5])}")
    
    if validation['algorithm_reasoning_present']:
        print(f"      Algorithm: ✅")


if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("🧠 MASTER LEARNINGS V2")
    print("="*70)
    
    print("\n📋 OPTIONS:")
    print("   1. 📋 Show current learnings")
    print("   2. 🔄 Update from all sources")
    print("   3. 📝 Get prompt-ready learnings")
    print("   4. 🔧 Reset to defaults")
    
    try:
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == '1':
            print_learnings_summary()
        
        elif choice == '2':
            update_from_all_sources()
            print_learnings_summary()
        
        elif choice == '3':
            prompt = get_learnings_for_prompt()
            print(prompt)
        
        elif choice == '4':
            confirm = input("⚠️ Reset all learnings? (y/n): ").strip().lower()
            if confirm == 'y':
                save_master_learnings(DEFAULT_LEARNINGS)
                print("✅ Reset to defaults")
        
        else:
            print("Invalid choice")
    except (EOFError, KeyboardInterrupt):
        print("\n⚠️  Skipping (non-interactive mode)")

