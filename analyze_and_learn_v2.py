#!/usr/bin/env python3
"""
🧠 ANALYZE & LEARN V2 - Multi-AI Ensemble Edition

IMPROVEMENTS vs V1:
- 5-AI Ensemble instead of single AI
- Progressive checkpoints (resume on crash)
- Smart clip selection (uses existing features)
- Clustering option
- Cost-optimized batching
- ETA tracking

STRATEGIES:
1. FULL: All 972 clips (100% coverage, $145, 3h)
2. CLUSTER: 300 representatives (95% coverage, $45, 1h)
3. SMART: 300 top clips (best 30%, $45, 1h)
4. QUICK: 100 outliers (top 10%, $15, 20min)
"""

import json
import os
import asyncio
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
    import pandas as pd
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

# Optional ML
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import KMeans
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False


class AnalyzeAndLearnV2:
    """
    Advanced pattern learning with 5-AI Ensemble
    """
    
    def __init__(self):
        print("="*70)
        print("🧠 ANALYZE & LEARN V2 - Multi-AI Ensemble")
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
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Output
        self.patterns_file = self.data_dir / "learned_patterns_v2.json"
        self.checkpoint_file = self.cache_dir / "learning_checkpoint.json"
        
        # Data
        self.clips = []
        self.patterns = {}
        
        print(f"   ✅ 5-AI Ensemble: {'Ready' if ENSEMBLE_AVAILABLE else 'Not available'}")
        print(f"   📈 ML: {'Available' if ML_AVAILABLE else 'Not available'}")
        print(f"   📊 NumPy: {'Available' if NUMPY_AVAILABLE else 'Not available'}")
    
    # =========================================================================
    # DATA LOADING
    # =========================================================================
    
    def load_training_data(self):
        """Load training data"""
        
        print(f"\n{'='*70}")
        print("📥 LOADING TRAINING DATA")
        print(f"{'='*70}")
        
        training_file = self.training_dir / "goat_training_data.json"
        
        if not training_file.exists():
            print(f"❌ Training data not found: {training_file}")
            return None
        
        with open(training_file, 'r') as f:
            self.clips = json.load(f)
        
        print(f"   📊 Total clips: {len(self.clips)}")
        
        # Calculate relative performance
        self._calculate_relative_performance()
        
        # Calculate composite scores from features
        self._calculate_composite_scores()
        
        print(f"✅ Loaded {len(self.clips)} clips")
        
        return self.clips
    
    def _calculate_relative_performance(self):
        """Calculate relative performance per account"""
        
        if not NUMPY_AVAILABLE:
            print("   ⚠️  NumPy not available - skipping relative performance")
            return
        
        by_account = defaultdict(list)
        for clip in self.clips:
            account = clip.get('account', 'unknown')
            by_account[account].append(clip)
        
        for account, clips in by_account.items():
            views = [c.get('performance', {}).get('views', 0) for c in clips]
            views = [v for v in views if v > 0]
            
            if views:
                median = np.median(views)
                for clip in clips:
                    v = clip.get('performance', {}).get('views', 0)
                    clip['relative_performance'] = v / median if median > 0 else 1
                    clip['is_outlier'] = clip['relative_performance'] >= 2.0
        
        outliers = sum(1 for c in self.clips if c.get('is_outlier'))
        print(f"   📊 Outliers (2x+): {outliers} clips")
    
    def _calculate_composite_scores(self):
        """Calculate composite score from features + performance"""
        
        for clip in self.clips:
            features = clip.get('features', {})
            performance = clip.get('performance', {})
            
            # Feature score (0-100)
            feature_score = (
                features.get('hook_information_gap', 0) * 20 +
                features.get('hook_has_question', 0) * 15 +
                features.get('pattern_interrupts', 0) * 2 +
                features.get('hook_completeness_score', 0) * 30 +
                (10 if features.get('hook_word_count', 0) < 15 else 0)
            )
            
            # Performance score (0-100)
            perf_score = (
                performance.get('watch_time_percentage', 0) * 50 +
                performance.get('completion_rate', 0) * 30 +
                performance.get('engagement_rate', 0) * 1000 * 20
            )
            
            # Combined (weighted)
            clip['composite_score'] = (feature_score * 0.4) + (perf_score * 0.6)
        
        # Stats
        if NUMPY_AVAILABLE:
            scores = [c['composite_score'] for c in self.clips]
            print(f"   📊 Composite scores: {np.mean(scores):.1f} avg, {np.max(scores):.1f} max")
        else:
            scores = [c['composite_score'] for c in self.clips]
            avg = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            print(f"   📊 Composite scores: {avg:.1f} avg, {max_score:.1f} max")
    
    # =========================================================================
    # SELECTION STRATEGIES
    # =========================================================================
    
    def select_clips_smart(self, n=300):
        """
        Smart selection based on features + performance
        
        Uses existing ML features to rank clips
        Selects top N for analysis
        """
        
        print(f"\n{'='*70}")
        print("🎯 SMART SELECTION")
        print(f"{'='*70}")
        
        # Sort by composite score
        ranked = sorted(
            self.clips,
            key=lambda x: x.get('composite_score', 0),
            reverse=True
        )
        
        selected = ranked[:n]
        
        print(f"   ✅ Selected top {n} clips")
        if selected:
            print(f"   📊 Score range: {selected[-1]['composite_score']:.1f} - {selected[0]['composite_score']:.1f}")
            print(f"   📊 Outliers in selection: {sum(1 for c in selected if c.get('is_outlier'))}")
        
        return selected
    
    def select_clips_cluster(self, n_clusters=300):
        """
        Cluster-based selection
        
        Groups similar clips, selects best per cluster
        Ensures diversity while reducing redundancy
        """
        
        if not ML_AVAILABLE:
            print("❌ ML not available for clustering")
            return self.select_clips_smart(n_clusters)
        
        print(f"\n{'='*70}")
        print("🔬 CLUSTER-BASED SELECTION")
        print(f"{'='*70}")
        
        print("   🔄 Generating embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        contents = [c.get('content', '')[:500] for c in self.clips]
        embeddings = model.encode(contents, show_progress_bar=False)
        
        print(f"   🔄 Clustering into {n_clusters} groups...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        
        # Select best per cluster
        representatives = []
        for cluster_id in range(n_clusters):
            cluster_clips = [
                c for c, l in zip(self.clips, labels)
                if l == cluster_id
            ]
            
            if cluster_clips:
                # Select highest performer
                best = max(
                    cluster_clips,
                    key=lambda x: x.get('performance', {}).get('views', 0)
                )
                best['cluster_id'] = cluster_id
                best['cluster_size'] = len(cluster_clips)
                representatives.append(best)
        
        print(f"   ✅ Selected {len(representatives)} representatives")
        print(f"   📊 Avg cluster size: {len(self.clips) / n_clusters:.1f}")
        
        return representatives
    
    def select_clips_outliers(self, n=100):
        """Quick selection: top outliers only"""
        
        print(f"\n{'='*70}")
        print("⚡ QUICK SELECTION - Outliers Only")
        print(f"{'='*70}")
        
        outliers = [c for c in self.clips if c.get('is_outlier')]
        
        # Sort by relative performance
        ranked = sorted(
            outliers,
            key=lambda x: x.get('relative_performance', 1),
            reverse=True
        )
        
        selected = ranked[:n]
        
        print(f"   ✅ Selected top {n} outliers")
        if selected:
            print(f"   📊 Performance: {selected[-1]['relative_performance']:.1f}x - {selected[0]['relative_performance']:.1f}x")
        
        return selected
    
    # =========================================================================
    # MULTI-AI ANALYSIS
    # =========================================================================
    
    async def analyze_batch_multi_ai(self, clips, batch_num=1):
        """
        Analyze batch with 5-AI consensus
        
        Uses debate strategy for deep pattern extraction
        """
        
        if not self.consensus:
            print("   ❌ Consensus engine not available")
            return None
        
        print(f"\n   🤖 Batch {batch_num}: Analyzing {len(clips)} clips with 5-AI Ensemble...")
        
        # Prepare data
        outliers = [c for c in clips if c.get('is_outlier')]
        normal = [c for c in clips if not c.get('is_outlier')]
        
        outlier_data = self._format_clips_for_analysis(outliers)
        normal_data = self._format_clips_for_analysis(normal)
        
        # Algorithm context
        algorithm_context = self._get_algorithm_context()
        
        prompt = f"""{algorithm_context}

---

# ANALYZE VIRAL PATTERNS FROM THIS BATCH

VIRAL CLIPS ({len(outliers)} clips, 2x+ performance):
{outlier_data}

NORMAL CLIPS ({len(normal)} clips):
{normal_data}

Extract CONCRETE patterns WITH ALGORITHM REASONING:

1. HOOK PATTERNS:
   - What hook types work? (question/statement/story/number)
   - Exact phrases that stop scrolling
   - Timing (how to use first 3 seconds)

2. STRUCTURE PATTERNS:
   - Winning content structures
   - Pattern interrupt techniques
   - Pacing strategies

3. EMOTIONAL TRIGGERS:
   - Which emotions drive watchtime?
   - Trigger phrases with examples
   - Arousal level patterns

4. LANGUAGE PATTERNS:
   - Power words (with examples)
   - Speaking style (conversational/authoritative)
   - Personal address techniques

5. PERFORMANCE FACTORS:
   - Mass appeal elements
   - Shareability triggers
   - Watch time drivers

6. ALGORITHM REASONING (WHY patterns work):
   - How does this pattern maximize Watch Time?
   - Why does algorithm favor this?
   - What metrics does it optimize?
   - How does it beat competition?

Answer in JSON with REAL EXAMPLES + ALGORITHM REASONING:
{{
  "hook_patterns": [
    {{
      "type": "question",
      "template": "Abstract template",
      "examples": ["Real example 1", "Real example 2"],
      "why_it_works": "Explanation",
      "algorithm_reasoning": "Why algorithm favors this (Watch Time impact)"
    }}
  ],
  "structure_patterns": [
    {{
      "pattern": "...",
      "algorithm_reasoning": "How it maximizes Watch Time/Completion"
    }}
  ],
  "emotional_triggers": [...],
  "language_patterns": [...],
  "key_insights": [
    "Insight 1",
    "Insight 2"
  ],
  "algorithm_insights": [
    "Why pattern X beats competition",
    "How pattern Y maximizes Watch Time"
  ]
}}
"""
        
        try:
            # 5-AI Debate for deep analysis
            result = await self.consensus.build_consensus(
                prompt=prompt,
                system="You are analyzing viral short-form content patterns from 972 training clips.",
                strategy='debate'  # Deep analysis
            )
            
            # Parse JSON from consensus
            consensus_text = result.get('consensus', '')
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', consensus_text)
            if json_match:
                patterns = json.loads(json_match.group())
                patterns['consensus_confidence'] = result.get('confidence', 0)
                patterns['analyzed_clips'] = len(clips)
                return patterns
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            import traceback
            print(f"      Detail: {traceback.format_exc()[:200]}")
            return None
        
        return None
    
    def _get_algorithm_context(self):
        """Get algorithm understanding context"""
        
        return """
# 🎯 ALGORITHM CONTEXT - CRITICAL FOR PATTERN ANALYSIS

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

## ANALYZE PATTERNS WITH THIS LENS:
Jeder Pattern muss erklären: "Warum maximiert dieser Pattern Watch Time?"
"""
    
    def _format_clips_for_analysis(self, clips):
        """Format clips for AI analysis"""
        
        formatted = []
        for clip in clips[:30]:  # Max 30 per type
            perf = clip.get('performance', {})
            content = clip.get('content', '')[:400]
            
            formatted.append(f"""
- Account: {clip.get('account')}
  Views: {perf.get('views', 0):,}
  Relative: {clip.get('relative_performance', 1):.1f}x
  Content: "{content}..."
""")
        
        return "\n".join(formatted)
    
    # =========================================================================
    # PROGRESSIVE ANALYSIS
    # =========================================================================
    
    async def analyze_progressive(self, clips, batch_size=50):
        """
        Progressive analysis with checkpoints
        
        Saves progress every batch - resume on crash
        """
        
        print(f"\n{'='*70}")
        print("🔬 PROGRESSIVE ANALYSIS")
        print(f"{'='*70}")
        
        total = len(clips)
        analyzed = 0
        all_patterns = []
        
        # Check for checkpoint
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                checkpoint = json.load(f)
                analyzed = checkpoint.get('analyzed', 0)
                all_patterns = checkpoint.get('patterns', [])
            
            print(f"   📦 Resuming from checkpoint: {analyzed}/{total}")
        
        # Process batches
        num_batches = (total - analyzed + batch_size - 1) // batch_size
        
        for i in range(analyzed, total, batch_size):
            batch = clips[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            print(f"\n🔄 Batch {batch_num}/{num_batches}")
            print(f"   Clips: {i+1}-{min(i+batch_size, total)}/{total}")
            print(f"   💰 Cost: ~${len(batch) * 0.15:.2f}")
            
            # Analyze batch
            patterns = await self.analyze_batch_multi_ai(batch, batch_num)
            
            if patterns:
                all_patterns.append(patterns)
                print(f"      ✅ Patterns extracted (confidence: {patterns.get('consensus_confidence', 0):.0%})")
            
            # Save checkpoint
            checkpoint = {
                'analyzed': min(i + batch_size, total),
                'total': total,
                'patterns': all_patterns,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            
            print(f"      💾 Checkpoint saved")
            
            # ETA
            remaining = total - min(i + batch_size, total)
            if remaining > 0:
                eta_min = (remaining / batch_size) * 3
                print(f"      ⏱️ ETA: {eta_min:.0f} minutes")
        
        print(f"\n✅ Analysis complete: {total} clips")
        
        # Merge all patterns
        merged = self._merge_all_patterns(all_patterns)
        
        return merged
    
    def _merge_all_patterns(self, pattern_list):
        """Merge patterns from multiple batches"""
        
        if not pattern_list:
            return {}
        
        print(f"\n🔄 Merging {len(pattern_list)} batches...")
        
        merged = {
            'hook_patterns': [],
            'structure_patterns': [],
            'emotional_triggers': [],
            'language_patterns': [],
            'key_insights': [],
            'metadata': {
                'batches': len(pattern_list),
                'total_clips_analyzed': sum(p.get('analyzed_clips', 0) for p in pattern_list),
                'avg_confidence': 0,
                'created_at': datetime.now().isoformat()
            }
        }
        
        # Calculate avg confidence
        confidences = [p.get('consensus_confidence', 0) for p in pattern_list if p.get('consensus_confidence')]
        if confidences:
            if NUMPY_AVAILABLE:
                merged['metadata']['avg_confidence'] = float(np.mean(confidences))
            else:
                merged['metadata']['avg_confidence'] = sum(confidences) / len(confidences)
        
        # Merge patterns
        for patterns in pattern_list:
            for key in ['hook_patterns', 'structure_patterns', 'emotional_triggers', 'language_patterns']:
                if key in patterns:
                    merged[key].extend(patterns[key])
            
            if 'key_insights' in patterns:
                merged['key_insights'].extend(patterns['key_insights'])
        
        # Deduplicate insights
        merged['key_insights'] = list(set(merged['key_insights']))
        
        print(f"   ✅ Merged patterns:")
        print(f"      Hooks: {len(merged['hook_patterns'])}")
        print(f"      Structures: {len(merged['structure_patterns'])}")
        print(f"      Emotional: {len(merged['emotional_triggers'])}")
        print(f"      Language: {len(merged['language_patterns'])}")
        print(f"      Insights: {len(merged['key_insights'])}")
        
        return merged
    
    # =========================================================================
    # SAVE
    # =========================================================================
    
    def save_patterns(self, patterns):
        """Save learned patterns"""
        
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Patterns saved: {self.patterns_file}")
        
        # Also save to deep_learned_patterns.json for master_learnings.py
        deep_file = self.data_dir / "deep_learned_patterns.json"
        with open(deep_file, 'w') as f:
            json.dump(self._convert_to_deep_format(patterns), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Deep patterns saved: {deep_file}")
    
    def _convert_to_deep_format(self, patterns):
        """Convert to format expected by master_learnings.py"""
        
        return {
            'metadata': patterns.get('metadata', {}),
            'executive_summary': {
                'key_insight_1': patterns.get('key_insights', [''])[0] if patterns.get('key_insights') else '',
                'key_insight_2': patterns.get('key_insights', ['', ''])[1] if len(patterns.get('key_insights', [])) > 1 else '',
                'key_insight_3': patterns.get('key_insights', ['', '', ''])[2] if len(patterns.get('key_insights', [])) > 2 else '',
            },
            'hook_mastery': {
                'winning_hook_types': patterns.get('hook_patterns', []),
                'hook_formulas': [p.get('template', '') for p in patterns.get('hook_patterns', [])[:10]],
                'power_words_for_hooks': self._extract_power_words(patterns),
                'hook_mistakes': []
            },
            'structure_mastery': {
                'winning_structures': patterns.get('structure_patterns', []),
                'pattern_interrupt_techniques': []
            },
            'emotional_mastery': {
                'best_emotions': patterns.get('emotional_triggers', []),
                'trigger_phrases': []
            },
            'quick_reference': {
                'do_this': patterns.get('key_insights', [])[:7],
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
    
    def _extract_power_words(self, patterns):
        """Extract power words from patterns"""
        
        power_words = []
        for pattern in patterns.get('language_patterns', []):
            if isinstance(pattern, dict) and 'examples' in pattern:
                power_words.extend(pattern['examples'][:3])
        
        return power_words[:20]


# =============================================================================
# MAIN CLI
# =============================================================================

async def main():
    """Main CLI"""
    
    analyzer = AnalyzeAndLearnV2()
    
    # Load data
    clips = analyzer.load_training_data()
    if not clips:
        return
    
    # Strategy selection
    print(f"\n{'='*70}")
    print("📊 ANALYSIS STRATEGY")
    print(f"{'='*70}")
    print("\n1. FULL - All 972 clips")
    print("   Coverage: 100% | Cost: ~$145 | Time: ~3h")
    print("\n2. CLUSTER - 300 representatives")
    print("   Coverage: 95% | Cost: ~$45 | Time: ~1h")
    print("\n3. SMART - Top 300 by features+performance")
    print("   Coverage: Best 30% | Cost: ~$45 | Time: ~1h")
    print("\n4. QUICK - Top 100 outliers")
    print("   Coverage: Top 10% | Cost: ~$15 | Time: ~20min")
    
    choice = input("\nSelect strategy (1-4): ").strip()
    
    if choice == '1':
        selected = clips
    elif choice == '2':
        selected = analyzer.select_clips_cluster(300)
    elif choice == '3':
        selected = analyzer.select_clips_smart(300)
    elif choice == '4':
        selected = analyzer.select_clips_outliers(100)
    else:
        print("Invalid choice")
        return
    
    # Confirm
    cost = len(selected) * 0.15
    time_min = len(selected) * 0.2
    
    print(f"\n💰 Estimated cost: ${cost:.2f}")
    print(f"⏱️  Estimated time: {time_min:.0f} minutes")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        return
    
    # Run analysis
    patterns = await analyzer.analyze_progressive(selected, batch_size=50)
    
    # Save
    analyzer.save_patterns(patterns)
    
    print("\n✅ ANALYSIS COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())

