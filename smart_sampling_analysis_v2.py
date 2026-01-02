#!/usr/bin/env python3
"""
🎯 SMART SAMPLING DEEP ANALYSIS V2 - Multi-AI Edition

IMPROVEMENTS vs V1:
- 5-AI Ensemble for deep analysis
- 350 clips instead of 150 (more coverage)
- Progressive checkpoints
- Parallel processing where possible
- Better pattern extraction

SAMPLES:
- 200 Top Outliers (5x+ performance)
- 100 Almost Viral (1.5-2x)
- 50 Underperformers (<0.5x)
= 350 total (36% of 972 clips)

OUTPUT: deep_learned_patterns.json
"""

import json
import os
import asyncio
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Import 5-AI Ensemble
import sys
sys.path.append(str(Path(__file__).parent))
try:
    from create_clips_v3_ensemble import PremiumAIEnsemble, ConsensusEngine
    ENSEMBLE_AVAILABLE = True
except ImportError:
    ENSEMBLE_AVAILABLE = False
    PremiumAIEnsemble = None
    ConsensusEngine = None


class SmartSamplingAnalyzerV2:
    """
    Deep analysis with 5-AI Ensemble
    """
    
    def __init__(self):
        print("="*70)
        print("🎯 SMART SAMPLING DEEP ANALYSIS V2")
        print("="*70)
        
        # Initialize 5-AI Ensemble
        if ENSEMBLE_AVAILABLE:
            self.ensemble = PremiumAIEnsemble()
            self.consensus = ConsensusEngine(self.ensemble)
        else:
            self.ensemble = None
            self.consensus = None
            print("   ⚠️  5-AI Ensemble: Not available")
        
        # Paths
        self.data_dir = Path("data")
        self.training_dir = self.data_dir / "training"
        self.cache_dir = self.data_dir / "cache"
        self.analysis_dir = self.cache_dir / "deep_analysis_v2"
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Output
        self.deep_patterns_file = self.data_dir / "deep_learned_patterns.json"
        self.checkpoint_file = self.cache_dir / "deep_analysis_checkpoint.json"
        
        # Load data
        self.clips = []
        self.load_data()
        
        print(f"   ✅ 5-AI Ensemble: {'Ready' if ENSEMBLE_AVAILABLE else 'Not available'}")
        print(f"   📦 Clips loaded: {len(self.clips)}")
        print(f"   💰 Estimated cost: $45-55 for 350 clips")
    
    def load_data(self):
        """Load training data"""
        
        training_file = self.training_dir / "goat_training_data.json"
        if training_file.exists():
            with open(training_file, 'r') as f:
                self.clips = json.load(f)
        
        if not NUMPY_AVAILABLE:
            print("   ⚠️  NumPy not available - skipping relative performance calculation")
            return
        
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
    
    def select_sample(self, n_top=200, n_middle=100, n_bottom=50):
        """
        Select strategic sample for deep analysis
        
        Args:
            n_top: Top outliers (5x+)
            n_middle: Almost viral (1.5-2x)
            n_bottom: Underperformers (<0.5x)
        """
        
        print(f"\n{'='*70}")
        print("🎯 SELECTING STRATEGIC SAMPLE")
        print(f"{'='*70}")
        
        # Sort by relative performance
        sorted_clips = sorted(
            self.clips,
            key=lambda x: x.get('relative_performance', 1),
            reverse=True
        )
        
        # Top outliers (5x+)
        top_outliers = [
            c for c in sorted_clips
            if c.get('relative_performance', 1) >= 5.0
        ][:n_top]
        
        # Almost viral (1.5-2x)
        almost_viral = [
            c for c in sorted_clips
            if 1.5 <= c.get('relative_performance', 1) < 2.0
        ][:n_middle]
        
        # Underperformers (<0.5x)
        underperformers = [
            c for c in sorted_clips
            if c.get('relative_performance', 1) < 0.5
        ][:n_bottom]
        
        print(f"   ✅ Top Outliers (5x+): {len(top_outliers)}")
        print(f"   ✅ Almost Viral (1.5-2x): {len(almost_viral)}")
        print(f"   ✅ Underperformers (<0.5x): {len(underperformers)}")
        print(f"   📊 Total sample: {len(top_outliers) + len(almost_viral) + len(underperformers)}")
        
        return {
            'top_outliers': top_outliers,
            'almost_viral': almost_viral,
            'underperformers': underperformers
        }
    
    async def analyze_single_clip(self, clip, category):
        """
        Deep analysis of single clip with 5-AI Ensemble
        
        Uses parallel_vote for speed (vs debate)
        """
        
        if not self.consensus:
            return {'error': 'Consensus engine not available', 'video_id': clip.get('video_id', 'unknown')}
        
        video_id = clip.get('video_id', 'unknown')
        content = clip.get('content', '')
        performance = clip.get('performance', {})
        
        # Check cache
        cache_file = self.analysis_dir / f"{video_id}_analysis.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        
        # Algorithm context
        algorithm_context = self._get_algorithm_context()
        
        prompt = f"""{algorithm_context}

---

# DEEP ANALYSIS: {category} CLIP

CONTENT:
{content}

PERFORMANCE:
- Views: {performance.get('views', 0):,}
- Watch Time: {performance.get('watch_time_percentage', 0):.1%}
- Completion: {performance.get('completion_rate', 0):.1%}
- Relative Performance: {clip.get('relative_performance', 1):.1f}x

Analyze WITH ALGORITHM REASONING:

1. HOOK (first 3 seconds / ~15 words):
   - What is the hook?
   - Hook type? (Question/Statement/Story/Number/Curiosity)
   - Opens loop? Information gap?
   - Would you stop scrolling?

2. STRUCTURE:
   - Content structure?
   - Pattern interrupts? Where?
   - Emotional peaks? Where?
   - Payoffs?

3. EMOTIONAL ANALYSIS:
   - Primary emotions triggered?
   - Emotional arc? (flat/building/rollercoaster)
   - High/low arousal?

4. LANGUAGE PATTERNS:
   - Speaking style?
   - Power words used?
   - Personal address level?
   - Pacing?

5. WHY IT PERFORMED THIS WAY (Algorithm View):
   - Main success/failure factors
   - How did it maximize/minimize Watch Time?
   - Why did algorithm favor/reject it?
   - What metrics did it optimize?
   - What could be improved?
   - Reusable patterns?

Answer in JSON:
{{
  "video_id": "{video_id}",
  "category": "{category}",
  "hook_analysis": {{
    "hook_text": "First 15-20 words",
    "hook_type": "question/statement/story/number/curiosity",
    "hook_strength": 1-10,
    "opens_loop": true/false,
    "stop_scrolling": true/false,
    "what_works": "...",
    "what_fails": "..."
  }},
  "structure_analysis": {{
    "structure_type": "hook-content-payoff / story-arc / list",
    "pattern_interrupts": ["Where in text"],
    "emotional_peaks": ["Where in text"],
    "pacing": "fast/medium/slow/varied",
    "flow_score": 1-10
  }},
  "emotional_analysis": {{
    "primary_emotion": "curiosity/fear/joy/anger/surprise",
    "arousal_level": "high/medium/low",
    "emotional_arc": "flat/building/rollercoaster"
  }},
  "language_patterns": {{
    "speaking_style": "conversational/authoritative/storytelling",
    "power_words": ["word1", "word2"],
    "personal_address": "high/medium/low"
  }},
  "performance_factors": {{
    "main_strength": "Why it worked/failed",
    "main_weakness": "Biggest weakness",
    "key_pattern": "Reusable pattern",
    "virality_score": 1-100,
    "algorithm_reasoning": {{
      "watch_time_impact": "How it maximized Watch Time",
      "completion_driver": "What drove completion rate",
      "why_algorithm_favored": "Why algorithm scaled this",
      "competition_advantage": "How it beat other videos"
    }}
  }},
  "extracted_templates": {{
    "hook_template": "Abstract reusable hook template",
    "structure_template": "Abstract structure pattern",
    "algorithm_why": "Why this template works (Watch Time logic)"
  }}
}}
"""
        
        try:
            # Use parallel_vote for speed (faster than debate)
            result = await self.consensus.build_consensus(
                prompt=prompt,
                system="You are analyzing viral short-form video patterns.",
                strategy='parallel_vote'
            )
            
            # Parse JSON
            import re
            consensus_text = result.get('consensus', '')
            json_match = re.search(r'\{[\s\S]*\}', consensus_text)
            
            if json_match:
                analysis = json.loads(json_match.group())
                analysis['consensus_confidence'] = result.get('confidence', 0)
                
                # Cache it
                with open(cache_file, 'w') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                
                return analysis
        
        except Exception as e:
            import traceback
            return {'error': str(e), 'video_id': video_id, 'traceback': traceback.format_exc()[:200]}
        
        return None
    
    def _get_algorithm_context(self):
        """Get algorithm understanding context"""
        
        return """
# 🎯 ALGORITHM CONTEXT - CRITICAL FOR DEEP ANALYSIS

## CORE PRINCIPLE:
Der Algorithmus ist ein Performance-Vergleichsmechanismus mit EINEM Ziel: Watchtime maximieren.
- Plattformen verdienen 99% durch Ads → Mehr Watchtime = Mehr Geld
- Du kämpfst gegen ALLE anderen Videos - Algorithmus ist nur Schiedsrichter
- Kein Shadowbanning - nur schlechtere Performance als Konkurrenz
- "Make a video so good that people cannot physically scroll past"

## METRICS PRIORITY (what algorithm optimizes):
1. Watch Time (absolute Priorität) - Länge × Retention
2. Completion Rate - % die bis Ende schauen
3. Engagement - Likes/Comments/Shares (Indikator für Interesse)
4. Session Duration - Wie lange bleiben User NACH deinem Video

## TESTGROUP MECHANISM:
1. Initial Test → Video wird kleiner Testgruppe gezeigt
2. Performance-Vergleich → Metriken vs ALLE anderen Videos
3. Skalierung → Video mit höchster Watchtime gewinnt

## WHY PATTERNS WORK (Algorithm View):
- Hook (0-3s): Wenn User hier abspringen → kostest Plattform Geld → Algorithmus stoppt Video
- Pattern Interrupts (alle 5-7s): Verhindern Drop-off → Höhere Retention → Mehr Watch Time
- Information Gap: Hält User dran → Höhere Completion → Algorithmus skaliert
- Emotional Arousal: High Arousal → Mehr Engagement → Algorithmus bevorzugt
- Loop Opening/Closing: Gehirn will Abschluss → Höhere Completion → Algorithmus belohnt

## ANALYZE WITH THIS LENS:
Jede Analyse muss erklären: "Warum maximiert/minimiert dieser Clip Watch Time?"
"""
    
    async def analyze_all_samples_progressive(self, sample):
        """
        Progressive analysis with checkpoints
        """
        
        print(f"\n{'='*70}")
        print("🔬 DEEP ANALYSIS - PROGRESSIVE")
        print(f"{'='*70}")
        
        all_clips = (
            sample['top_outliers'] +
            sample['almost_viral'] +
            sample['underperformers']
        )
        
        total = len(all_clips)
        
        print(f"\n📊 Total clips to analyze: {total}")
        print(f"   💰 Estimated cost: ${total * 0.15:.2f}")
        print(f"   ⏱️  Estimated time: {total * 0.3:.0f} minutes")
        
        try:
            confirm = input("\nProceed? (y/n): ").strip().lower()
            if confirm != 'y':
                return None
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Skipping (non-interactive mode)")
            return None
        
        # Check checkpoint
        analyzed = 0
        results = {
            'top_outliers': [],
            'almost_viral': [],
            'underperformers': []
        }
        
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                checkpoint = json.load(f)
                analyzed = checkpoint.get('analyzed', 0)
                results = checkpoint.get('results', results)
            
            print(f"\n📦 Resuming from checkpoint: {analyzed}/{total}")
        
        # Categories
        categories = [
            ('top_outliers', 'TOP_OUTLIER', sample['top_outliers']),
            ('almost_viral', 'ALMOST_VIRAL', sample['almost_viral']),
            ('underperformers', 'UNDERPERFORMER', sample['underperformers'])
        ]
        
        # Process
        for category_key, category_label, clips in categories:
            # Skip if already done
            already_done = len(results[category_key])
            if already_done >= len(clips):
                print(f"\n✅ {category_label}: Already complete ({already_done} clips)")
                continue
            
            print(f"\n🔄 Analyzing {category_label}s...")
            
            for i, clip in enumerate(clips[already_done:], already_done + 1):
                video_id = clip.get('video_id', 'unknown')
                
                analyzed += 1
                print(f"   [{analyzed}/{total}] {video_id}...", end=" ", flush=True)
                
                # Analyze
                analysis = await self.analyze_single_clip(clip, category_label)
                
                if analysis and 'error' not in analysis:
                    results[category_key].append(analysis)
                    score = analysis.get('performance_factors', {}).get('virality_score', '?')
                    conf = analysis.get('consensus_confidence', 0)
                    print(f"✅ (Score:{score}, Conf:{conf:.0%})")
                else:
                    print("❌")
                
                # Save checkpoint every 10 clips
                if analyzed % 10 == 0:
                    checkpoint = {
                        'analyzed': analyzed,
                        'total': total,
                        'results': results,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    with open(self.checkpoint_file, 'w') as f:
                        json.dump(checkpoint, f, indent=2)
                    
                    print(f"      💾 Checkpoint saved")
                    
                    # ETA
                    remaining = total - analyzed
                    eta_min = remaining * 0.3
                    print(f"      ⏱️ ETA: {eta_min:.0f} minutes")
        
        print(f"\n✅ Analysis complete!")
        print(f"   Top Outliers: {len(results['top_outliers'])}")
        print(f"   Almost Viral: {len(results['almost_viral'])}")
        print(f"   Underperformers: {len(results['underperformers'])}")
        
        return results
    
    def synthesize_patterns(self, results):
        """
        Synthesize patterns from all analyses
        """
        
        print(f"\n{'='*70}")
        print("🧠 SYNTHESIZING PATTERNS")
        print(f"{'='*70}")
        
        all_analyses = (
            results['top_outliers'] +
            results['almost_viral'] +
            results['underperformers']
        )
        
        # Extract patterns
        hook_patterns = []
        structure_patterns = []
        emotional_patterns = []
        language_patterns = []
        key_insights = []
        
        # Hook patterns
        for analysis in results['top_outliers']:
            hook = analysis.get('hook_analysis', {})
            template = analysis.get('extracted_templates', {}).get('hook_template', '')
            
            if template:
                hook_patterns.append({
                    'type': hook.get('hook_type', 'unknown'),
                    'template': template,
                    'example': hook.get('hook_text', ''),
                    'strength': hook.get('hook_strength', 0),
                    'why_works': hook.get('what_works', '')
                })
        
        # Structure patterns
        for analysis in results['top_outliers']:
            structure = analysis.get('structure_analysis', {})
            template = analysis.get('extracted_templates', {}).get('structure_template', '')
            
            if template:
                structure_patterns.append({
                    'type': structure.get('structure_type', 'unknown'),
                    'template': template,
                    'flow_score': structure.get('flow_score', 0)
                })
        
        # Emotional patterns
        emotion_counts = defaultdict(int)
        for analysis in results['top_outliers']:
            emotion = analysis.get('emotional_analysis', {}).get('primary_emotion', '')
            if emotion:
                emotion_counts[emotion] += 1
        
        emotional_patterns = [
            {'emotion': e, 'frequency': c}
            for e, c in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Language patterns
        power_words_all = []
        for analysis in results['top_outliers']:
            words = analysis.get('language_patterns', {}).get('power_words', [])
            power_words_all.extend(words)
        
        # Count frequency
        word_counts = defaultdict(int)
        for word in power_words_all:
            word_counts[word.lower()] += 1
        
        top_power_words = [
            w for w, c in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:50]
        ]
        
        # Key insights
        key_insights = [
            "Top hooks open loops and create information gaps",
            "Pattern interrupts every 5-7 seconds maintain attention",
            "High arousal emotions (curiosity, surprise) outperform low arousal",
            f"Most common hook type: {hook_patterns[0]['type'] if hook_patterns else 'unknown'}",
            f"Best performing emotion: {emotional_patterns[0]['emotion'] if emotional_patterns else 'unknown'}"
        ]
        
        print(f"   ✅ Hook patterns: {len(hook_patterns)}")
        print(f"   ✅ Structure patterns: {len(structure_patterns)}")
        print(f"   ✅ Emotional patterns: {len(emotional_patterns)}")
        print(f"   ✅ Power words: {len(top_power_words)}")
        
        return {
            'metadata': {
                'clips_analyzed': {
                    'total': len(all_analyses),
                    'top_outliers': len(results['top_outliers']),
                    'almost_viral': len(results['almost_viral']),
                    'underperformers': len(results['underperformers'])
                },
                'created_at': datetime.now().isoformat(),
                'version': 'v2_multi_ai'
            },
            'executive_summary': {
                'key_insight_1': key_insights[0] if len(key_insights) > 0 else '',
                'key_insight_2': key_insights[1] if len(key_insights) > 1 else '',
                'key_insight_3': key_insights[2] if len(key_insights) > 2 else ''
            },
            'hook_mastery': {
                'winning_hook_types': hook_patterns[:20],
                'hook_formulas': [p['template'] for p in hook_patterns[:10]],
                'power_words_for_hooks': top_power_words,
                'hook_mistakes': []
            },
            'structure_mastery': {
                'winning_structures': structure_patterns[:15],
                'pattern_interrupt_techniques': []
            },
            'emotional_mastery': {
                'best_emotions': emotional_patterns[:10],
                'trigger_phrases': []
            },
            'quick_reference': {
                'do_this': key_insights[:7],
                'never_do': []
            },
            'scoring_weights': {
                'hook_strength': 0.25,
                'information_gap': 0.20,
                'emotional_intensity': 0.15,
                'mass_appeal': 0.15,
                'structure_flow': 0.10,
                'simplicity': 0.10,
                'personal_address': 0.05
            }
        }
    
    def save_patterns(self, patterns):
        """Save deep patterns"""
        
        self.deep_patterns_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.deep_patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Deep patterns saved: {self.deep_patterns_file}")


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Main CLI"""
    
    analyzer = SmartSamplingAnalyzerV2()
    
    # Select sample
    sample = analyzer.select_sample(n_top=200, n_middle=100, n_bottom=50)
    
    # Analyze
    results = await analyzer.analyze_all_samples_progressive(sample)
    
    if not results:
        return
    
    # Synthesize patterns
    patterns = analyzer.synthesize_patterns(results)
    
    # Save
    analyzer.save_patterns(patterns)
    
    print("\n✅ DEEP ANALYSIS COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())

