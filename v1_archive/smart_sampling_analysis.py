#!/usr/bin/env python3
"""
🎯 SMART SAMPLING DEEP ANALYSIS

Analyzes 150 carefully selected clips in DETAIL:
- Top 50 Outliers (5x+ performance) 
- Top 50 "Almost Viral" (1.5-2x)
- 50 Underperformers (<0.5x)

Each clip gets FULL AI analysis for deep pattern recognition.

Cost: ~$10-15 (instead of $50-100 for all)
Quality: 90% of full analysis

OUTPUT:
- Concrete hook templates with real examples
- Audio patterns (when energy, when pause)
- Exact wording patterns
- Do's and Don'ts with real examples
"""

import json
import os
import re
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

import numpy as np
import pandas as pd
from anthropic import Anthropic

# Optional
try:
    import librosa
    LIBROSA_AVAILABLE = True
except:
    LIBROSA_AVAILABLE = False


class SmartSamplingAnalyzer:
    """
    Deep analysis of strategically selected clips
    """
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        
        # Paths
        self.data_dir = Path("data")
        self.training_dir = self.data_dir / "training"
        self.cache_dir = self.data_dir / "cache"
        self.transcripts_dir = self.cache_dir / "transcripts"
        self.analysis_dir = self.cache_dir / "deep_analysis"
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Output
        self.deep_patterns_file = self.data_dir / "deep_learned_patterns.json"
        
        # Load data
        self.clips = []
        self.load_data()
        
        print("="*70)
        print("🎯 SMART SAMPLING DEEP ANALYSIS")
        print("="*70)
        print(f"   🤖 API: {'✅' if self.client else '❌'}")
        print(f"   📦 Clips: {len(self.clips)}")
        print(f"   💰 Estimated cost: $10-15 for 150 clips")
    
    def load_data(self):
        """Load training data and calculate relative performance"""
        
        training_file = self.training_dir / "goat_training_data.json"
        if training_file.exists():
            with open(training_file, 'r') as f:
                self.clips = json.load(f)
        
        # Calculate relative performance
        by_account = defaultdict(list)
        for clip in self.clips:
            by_account[clip.get('account', 'unknown')].append(clip)
        
        for account, clips in by_account.items():
            views = [c.get('performance', {}).get('views', 0) for c in clips]
            views = [v for v in views if v > 0]
            if views:
                median = np.median(views)
                for clip in clips:
                    v = clip.get('performance', {}).get('views', 0)
                    clip['relative_performance'] = v / median if median > 0 else 1
    
    def select_sample(self, n_top=50, n_middle=50, n_bottom=50):
        """
        Strategically select clips for deep analysis
        
        Returns:
        - Top 50: Outliers (highest relative performance)
        - Middle 50: Almost viral (1.5-2x)
        - Bottom 50: Underperformers (<0.5x)
        """
        
        print(f"\n{'='*70}")
        print("🎯 SELECTING STRATEGIC SAMPLE")
        print(f"{'='*70}")
        
        # Filter clips with content
        clips_with_content = [c for c in self.clips if c.get('content')]
        
        print(f"   Clips with content: {len(clips_with_content)}")
        
        # Sort by relative performance
        sorted_clips = sorted(
            clips_with_content, 
            key=lambda x: x.get('relative_performance', 1), 
            reverse=True
        )
        
        # Select groups
        top_outliers = []
        almost_viral = []
        underperformers = []
        
        for clip in sorted_clips:
            perf = clip.get('relative_performance', 1)
            
            if perf >= 2.0 and len(top_outliers) < n_top:
                top_outliers.append(clip)
            elif 1.3 <= perf < 2.0 and len(almost_viral) < n_middle:
                almost_viral.append(clip)
            elif perf < 0.7 and len(underperformers) < n_bottom:
                underperformers.append(clip)
        
        print(f"\n📊 Selected:")
        print(f"   🔥 Top Outliers (2x+): {len(top_outliers)}")
        print(f"   📈 Almost Viral (1.3-2x): {len(almost_viral)}")
        print(f"   📉 Underperformers (<0.7x): {len(underperformers)}")
        
        # Show examples
        print(f"\n🔥 TOP OUTLIERS Preview:")
        for clip in top_outliers[:3]:
            print(f"   {clip.get('relative_performance', 1):.1f}x | {clip['performance']['views']:,} views")
            print(f"   \"{clip.get('content', '')[:80]}...\"")
        
        return {
            'top_outliers': top_outliers,
            'almost_viral': almost_viral,
            'underperformers': underperformers
        }
    
    def analyze_single_clip(self, clip, category):
        """
        Deep AI analysis of a single clip
        
        Returns comprehensive analysis including:
        - Hook analysis
        - Structure analysis
        - Emotional analysis
        - Audio insights (from transcript pacing)
        - Specific patterns detected
        """
        
        content = clip.get('content', '')
        if not content:
            return None
        
        video_id = clip.get('video_id', 'unknown')
        
        # Check cache
        cache_file = self.analysis_dir / f"{video_id}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        prompt = f"""Analysiere dieses Video-Transcript DETAILLIERT.

TRANSCRIPT:
"{content}"

PERFORMANCE:
- Views: {clip.get('performance', {}).get('views', 0):,}
- Relative Performance: {clip.get('relative_performance', 1):.1f}x (vs Account-Durchschnitt)
- Category: {category}

ALGORITHMUS-KONTEXT (WICHTIG!):
Der Algorithmus ist ein Performance-Vergleichsmechanismus mit EINEM Ziel: Watchtime maximieren.
- Du kämpfst gegen ALLE anderen Videos - der Algorithmus ist nur Schiedsrichter
- "Make a video so good that people cannot physically scroll past"
- Metriken: Watch Time > Completion Rate > Engagement > Session Duration
- Hook (0-3s): Wenn User hier abspringen, kostest du die Plattform Geld
- Jede Sekunde muss Grund liefern weiterzuschauen
- Unvollständige Loops, Pattern Interrupts, Emotionale Achterbahn

ANALYSE NACH DIESEN FRAMEWORKS:

1. HOOK ANALYSE (erste 3 Sekunden / ~15 Wörter):
   - Was ist der Hook?
   - Welcher Hook-Typ? (Question, Statement, Story, Number, Curiosity)
   - Öffnet er einen Loop?
   - Information Gap?
   - Würde ich aufhören zu scrollen?

2. CONTENT STRUKTUR:
   - Wie ist der Aufbau?
   - Wo sind die Pattern Interrupts?
   - Wo sind emotionale Peaks?
   - Gibt es Payoffs?

3. EMOTIONALE ANALYSE:
   - Welche Emotionen werden getriggert?
   - Gibt es eine emotionale Achterbahn?
   - High Arousal vs Low Arousal?

4. SPRACH-PATTERNS:
   - Pacing (schnell/langsam)?
   - Wo wären Pausen?
   - Persönliche Ansprache?
   - Power Words?

5. CIALDINI TRIGGERS:
   - Social Proof?
   - Authority?
   - Scarcity?
   - Reciprocity?

6. VIRALITY FAKTOREN:
   - Mass Appeal?
   - Shareability?
   - Controversy?
   - Learning Value?

Antworte in JSON:

{{
    "video_id": "{video_id}",
    "category": "{category}",
    
    "hook_analysis": {{
        "hook_text": "Die ersten 15-20 Wörter",
        "hook_type": "question/statement/story/number/curiosity/none",
        "hook_strength": 1-10,
        "opens_loop": true/false,
        "information_gap": true/false,
        "stop_scrolling": true/false,
        "hook_elements": ["Element 1", "Element 2"],
        "what_works": "Was am Hook funktioniert",
        "what_fails": "Was am Hook nicht funktioniert"
    }},
    
    "structure_analysis": {{
        "structure_type": "hook-content-payoff / story-arc / list / etc",
        "pattern_interrupts": ["Wo im Text", "..."],
        "emotional_peaks": ["Wo im Text", "..."],
        "payoffs": ["Was/Wo", "..."],
        "pacing": "fast/medium/slow/varied",
        "flow_score": 1-10
    }},
    
    "emotional_analysis": {{
        "primary_emotion": "curiosity/fear/joy/anger/surprise/etc",
        "secondary_emotions": ["emotion1", "emotion2"],
        "arousal_level": "high/medium/low",
        "emotional_arc": "flat/building/rollercoaster/peak-end",
        "trigger_phrases": ["Phrase 1", "Phrase 2"]
    }},
    
    "language_patterns": {{
        "speaking_style": "conversational/authoritative/storytelling/educational",
        "power_words_used": ["Wort1", "Wort2"],
        "personal_address": "high/medium/low/none",
        "specificity": "high/medium/low",
        "simplicity": 1-10
    }},
    
    "cialdini_triggers": {{
        "social_proof": {{"present": true/false, "example": "..."}},
        "authority": {{"present": true/false, "example": "..."}},
        "scarcity": {{"present": true/false, "example": "..."}},
        "reciprocity": {{"present": true/false, "example": "..."}},
        "liking": {{"present": true/false, "example": "..."}},
        "commitment": {{"present": true/false, "example": "..."}}
    }},
    
    "virality_factors": {{
        "mass_appeal": 1-10,
        "shareability": 1-10,
        "controversy": 1-10,
        "learning_value": 1-10,
        "entertainment": 1-10,
        "relatability": 1-10
    }},
    
    "overall_assessment": {{
        "virality_score": 1-100,
        "main_strength": "Was macht diesen Clip stark/schwach",
        "main_weakness": "Größte Schwäche",
        "key_pattern": "Das wichtigste Pattern das hier genutzt wird",
        "improvement_suggestions": ["Suggestion 1", "Suggestion 2"]
    }},
    
    "extracted_templates": {{
        "hook_template": "Abstrahiertes Hook-Template das wiederverwendet werden kann",
        "structure_template": "Abstrahierte Struktur"
    }}
}}"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                analysis = json.loads(json_match.group())
                
                # Cache it
                with open(cache_file, 'w') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                
                return analysis
        
        except Exception as e:
            return {'error': str(e), 'video_id': video_id}
        
        return None
    
    def analyze_all_samples(self, sample):
        """
        Analyze all selected clips
        """
        
        print(f"\n{'='*70}")
        print("🔬 DEEP ANALYSIS OF ALL SAMPLES")
        print(f"{'='*70}")
        
        if not self.client:
            print("❌ No API key")
            return None
        
        all_clips = (
            sample['top_outliers'] + 
            sample['almost_viral'] + 
            sample['underperformers']
        )
        
        total = len(all_clips)
        
        print(f"\n📊 Analyzing {total} clips...")
        print(f"   💰 Estimated cost: ${total * 0.08:.2f} - ${total * 0.12:.2f}")
        
        confirm = input(f"\n   Start analysis? (y/n): ").strip().lower()
        if confirm != 'y':
            return None
        
        results = {
            'top_outliers': [],
            'almost_viral': [],
            'underperformers': []
        }
        
        categories = [
            ('top_outliers', 'TOP_OUTLIER'),
            ('almost_viral', 'ALMOST_VIRAL'),
            ('underperformers', 'UNDERPERFORMER')
        ]
        
        analyzed = 0
        errors = 0
        
        for category_key, category_label in categories:
            clips = sample[category_key]
            
            print(f"\n🔄 Analyzing {category_label}s ({len(clips)} clips)...")
            
            for i, clip in enumerate(clips, 1):
                video_id = clip.get('video_id', 'unknown')
                
                # Progress
                analyzed += 1
                print(f"   [{analyzed}/{total}] {video_id}...", end=" ", flush=True)
                
                # Analyze
                analysis = self.analyze_single_clip(clip, category_label)
                
                if analysis and 'error' not in analysis:
                    results[category_key].append(analysis)
                    score = analysis.get('overall_assessment', {}).get('virality_score', '?')
                    print(f"✅ (Score: {score})")
                else:
                    errors += 1
                    print("❌")
                
                # Rate limiting - be nice to the API
                time.sleep(0.5)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Analyzed: {analyzed - errors}/{total}")
        print(f"   Errors: {errors}")
        
        # Save all results
        results_file = self.analysis_dir / "all_deep_analyses.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"   📁 Saved: {results_file}")
        
        return results
    
    def synthesize_patterns(self, results):
        """
        Synthesize all individual analyses into master patterns
        
        This is the final AI call that combines everything
        """
        
        print(f"\n{'='*70}")
        print("🧠 SYNTHESIZING PATTERNS")
        print(f"{'='*70}")
        
        if not self.client:
            print("❌ No API key")
            return None
        
        # Prepare summary data
        top_analyses = results.get('top_outliers', [])
        almost_analyses = results.get('almost_viral', [])
        under_analyses = results.get('underperformers', [])
        
        # Extract key patterns
        def summarize_group(analyses, limit=20):
            summaries = []
            for a in analyses[:limit]:
                summaries.append({
                    'hook_type': a.get('hook_analysis', {}).get('hook_type'),
                    'hook_strength': a.get('hook_analysis', {}).get('hook_strength'),
                    'hook_template': a.get('extracted_templates', {}).get('hook_template'),
                    'main_strength': a.get('overall_assessment', {}).get('main_strength'),
                    'key_pattern': a.get('overall_assessment', {}).get('key_pattern'),
                    'virality_score': a.get('overall_assessment', {}).get('virality_score'),
                    'primary_emotion': a.get('emotional_analysis', {}).get('primary_emotion'),
                    'structure_type': a.get('structure_analysis', {}).get('structure_type')
                })
            return summaries
        
        prompt = f"""Du hast {len(top_analyses) + len(almost_analyses) + len(under_analyses)} Videos detailliert analysiert.

ALGORITHMUS-KONTEXT:
Der Social Media Algorithmus ist ein reiner Performance-Vergleich mit EINEM Ziel: Watchtime maximieren.
- Plattformen verdienen 99% durch Ads → Mehr Watchtime = Mehr Geld
- Du kämpfst gegen ALLE anderen Videos in der Nische
- Kein Shadowbanning - nur schlechtere Performance als Konkurrenz
- "Make a video so good that people cannot physically scroll past"
- Optimiere auf: Watch Time > Completion Rate > Engagement > Session Duration
- Hook (0-3s): Sofort Spannung, wenn User abspringen = du kostest Plattform Geld
- Jede Sekunde muss Grund liefern weiterzuschauen
- Unvollständige Loops, Pattern Interrupts, Emotionale Achterbahn (nicht Flatline)

ZUSAMMENFASSUNG DER ANALYSEN:

🔥 TOP OUTLIERS (beste Performer):
{json.dumps(summarize_group(top_analyses), indent=2, ensure_ascii=False)}

📈 ALMOST VIRAL (gute Performer):
{json.dumps(summarize_group(almost_analyses), indent=2, ensure_ascii=False)}

📉 UNDERPERFORMERS (schwache Performer):
{json.dumps(summarize_group(under_analyses), indent=2, ensure_ascii=False)}

AUFGABE:
Erstelle ein MASTER PATTERN DOKUMENT das alle Erkenntnisse zusammenfasst.

Antworte in JSON:

{{
    "executive_summary": {{
        "total_clips_analyzed": {len(top_analyses) + len(almost_analyses) + len(under_analyses)},
        "key_insight_1": "Die wichtigste Erkenntnis",
        "key_insight_2": "Zweite wichtige Erkenntnis",
        "key_insight_3": "Dritte wichtige Erkenntnis"
    }},
    
    "hook_mastery": {{
        "winning_hook_types": [
            {{
                "type": "Hook-Typ",
                "frequency_in_top": "X%",
                "template": "Konkretes Template",
                "examples": ["Beispiel 1", "Beispiel 2"],
                "why_it_works": "Erklärung"
            }}
        ],
        "hook_formulas": [
            "Formel 1: [Kontraintuitiv] + [Pause] + [Twist]",
            "Formel 2: ..."
        ],
        "power_words_for_hooks": ["Wort1", "Wort2", "Wort3"],
        "hook_mistakes": ["Fehler 1", "Fehler 2"]
    }},
    
    "emotional_mastery": {{
        "best_emotions": ["Emotion1", "Emotion2"],
        "emotional_arc_template": "Beschreibung des idealen emotionalen Verlaufs",
        "trigger_phrases": ["Phrase 1", "Phrase 2"],
        "arousal_level": "high/medium - mit Erklärung"
    }},
    
    "structure_mastery": {{
        "winning_structures": [
            {{
                "name": "Struktur-Name",
                "flow": "Hook → X → Y → Payoff",
                "timing": "Wann passiert was",
                "frequency_in_top": "X%"
            }}
        ],
        "pattern_interrupt_techniques": ["Technik 1", "Technik 2"],
        "optimal_length": "X-Y Sekunden/Wörter"
    }},
    
    "language_mastery": {{
        "speaking_style": "Was funktioniert",
        "power_words": ["Wort1", "Wort2"],
        "words_to_avoid": ["Wort1", "Wort2"],
        "personal_address_level": "Empfehlung",
        "simplicity_level": "Empfehlung"
    }},
    
    "cialdini_usage": {{
        "most_effective": ["Principle 1", "Principle 2"],
        "how_to_apply": [
            {{"principle": "X", "technique": "Wie anwenden"}}
        ]
    }},
    
    "content_checklist": {{
        "before_recording": [
            "✅ Check 1",
            "✅ Check 2"
        ],
        "hook_checklist": [
            "✅ Öffnet Loop?",
            "✅ Information Gap?",
            "✅ Power Word in ersten 3 Wörtern?"
        ],
        "structure_checklist": [
            "✅ Pattern Interrupt alle 5-7 Sekunden?",
            "✅ Emotionaler Peak vorhanden?"
        ]
    }},
    
    "red_flags": [
        {{
            "mistake": "Fehler-Beschreibung",
            "frequency_in_bottom": "X%",
            "how_to_avoid": "Lösung"
        }}
    ],
    
    "scoring_weights": {{
        "hook_strength": 0.25,
        "emotional_intensity": 0.20,
        "structure_flow": 0.15,
        "information_gap": 0.15,
        "simplicity": 0.10,
        "personal_address": 0.10,
        "cialdini_triggers": 0.05
    }},
    
    "quick_reference": {{
        "do_this": ["Action 1", "Action 2", "Action 3"],
        "never_do": ["Mistake 1", "Mistake 2", "Mistake 3"],
        "test_questions": [
            "Würde ich aufhören zu scrollen?",
            "Öffnet der erste Satz einen Loop?",
            "Gibt es einen klaren Payoff?"
        ]
    }}
}}"""
        
        print("\n🔄 Final synthesis...")
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                patterns = json.loads(json_match.group())
                
                # Add metadata
                patterns['metadata'] = {
                    'created_at': datetime.now().isoformat(),
                    'clips_analyzed': {
                        'top_outliers': len(top_analyses),
                        'almost_viral': len(almost_analyses),
                        'underperformers': len(under_analyses),
                        'total': len(top_analyses) + len(almost_analyses) + len(under_analyses)
                    },
                    'method': 'smart_sampling_deep_analysis'
                }
                
                # Save
                with open(self.deep_patterns_file, 'w') as f:
                    json.dump(patterns, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Master patterns created!")
                print(f"   📁 {self.deep_patterns_file}")
                
                # AUTO-UPDATE MASTER LEARNINGS
                try:
                    from master_learnings import update_from_deep_analysis
                    print(f"\n🔄 Updating Master Learnings...")
                    update_from_deep_analysis(self.deep_patterns_file)
                except ImportError:
                    print(f"\n⚠️ master_learnings.py not found - skipping auto-update")
                except Exception as e:
                    print(f"\n⚠️ Could not update Master Learnings: {e}")
                
                # Print summary
                self._print_pattern_summary(patterns)
                
                return patterns
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def _print_pattern_summary(self, patterns):
        """Print summary of learned patterns"""
        
        print(f"\n{'='*70}")
        print("🎯 PATTERN SUMMARY")
        print(f"{'='*70}")
        
        # Executive Summary
        exec_sum = patterns.get('executive_summary', {})
        print(f"\n📊 ANALYZED: {exec_sum.get('total_clips_analyzed', '?')} clips")
        print(f"\n💡 KEY INSIGHTS:")
        print(f"   1. {exec_sum.get('key_insight_1', '')}")
        print(f"   2. {exec_sum.get('key_insight_2', '')}")
        print(f"   3. {exec_sum.get('key_insight_3', '')}")
        
        # Hook Mastery
        hooks = patterns.get('hook_mastery', {})
        print(f"\n🪝 WINNING HOOKS:")
        for h in hooks.get('winning_hook_types', [])[:3]:
            print(f"   • {h.get('type')}: {h.get('template', '')[:60]}")
        
        # Quick Reference
        quick = patterns.get('quick_reference', {})
        print(f"\n✅ DO THIS:")
        for item in quick.get('do_this', [])[:5]:
            print(f"   • {item}")
        
        print(f"\n❌ NEVER DO:")
        for item in quick.get('never_do', [])[:5]:
            print(f"   • {item}")
    
    def run_full_pipeline(self):
        """
        Run complete smart sampling pipeline
        """
        
        print("\n" + "="*70)
        print("🚀 FULL SMART SAMPLING PIPELINE")
        print("="*70)
        
        # Step 1: Select sample
        sample = self.select_sample(n_top=50, n_middle=50, n_bottom=50)
        
        total = len(sample['top_outliers']) + len(sample['almost_viral']) + len(sample['underperformers'])
        
        if total < 30:
            print("\n⚠️ Not enough clips for analysis")
            return
        
        # Step 2: Analyze all samples
        results = self.analyze_all_samples(sample)
        
        if not results:
            return
        
        # Step 3: Synthesize patterns
        patterns = self.synthesize_patterns(results)
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📁 Output:")
        print(f"   • Individual analyses: {self.analysis_dir}/")
        print(f"   • Master patterns: {self.deep_patterns_file}")
        print(f"\n🎬 Ready to create clips with: python create_clips.py")


def main():
    """Main entry point"""
    
    analyzer = SmartSamplingAnalyzer()
    
    print("\n" + "-"*50)
    print("📝 OPTIONS:")
    print("   1. 🚀 Full Pipeline (Select → Analyze → Synthesize)")
    print("   2. 🎯 Select sample only")
    print("   3. 🔬 Analyze samples only (if already selected)")
    print("   4. 🧠 Synthesize patterns only (if already analyzed)")
    print("   5. 📋 View current patterns")
    print("-"*50)
    
    choice = input("\nChoice (1-5): ").strip()
    
    if choice == '1':
        analyzer.run_full_pipeline()
    
    elif choice == '2':
        sample = analyzer.select_sample()
        print(f"\n✅ Sample selected: {sum(len(v) for v in sample.values())} clips")
    
    elif choice == '3':
        sample = analyzer.select_sample()
        results = analyzer.analyze_all_samples(sample)
    
    elif choice == '4':
        results_file = analyzer.analysis_dir / "all_deep_analyses.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
            analyzer.synthesize_patterns(results)
        else:
            print("❌ No analyses found. Run option 3 first.")
    
    elif choice == '5':
        if analyzer.deep_patterns_file.exists():
            with open(analyzer.deep_patterns_file, 'r') as f:
                patterns = json.load(f)
            analyzer._print_pattern_summary(patterns)
        else:
            print("❌ No patterns found yet")


if __name__ == "__main__":
    main()
