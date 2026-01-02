#!/usr/bin/env python3
"""
🔄 CONTINUOUS LEARNING SYSTEM

Self-improving AI brain that:
1. Monitors for new viral videos
2. Auto-analyzes when threshold reached
3. Incrementally updates Master Learnings
4. Tracks improvement over time
5. Never stops learning!

WORKFLOW:
- Add new videos → Auto-detect outliers → Analyze → Update brain
- Brain gets smarter with every batch
- Old patterns weighted down, new patterns weighted up
- Version control for learnings (v1, v2, v3...)

USAGE:
python continuous_learning_system.py --add-videos "path/to/new_videos.csv"
python continuous_learning_system.py --auto-analyze
python continuous_learning_system.py --status
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from collections import defaultdict
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    from analyze_and_learn_v2 import AnalyzeAndLearnV2
    ANALYZE_AVAILABLE = True
except ImportError:
    ANALYZE_AVAILABLE = False
    AnalyzeAndLearnV2 = None

try:
    from smart_sampling_analysis_v2 import SmartSamplingAnalyzerV2
    SAMPLING_AVAILABLE = True
except ImportError:
    SAMPLING_AVAILABLE = False
    SmartSamplingAnalyzerV2 = None

try:
    from master_learnings_v2 import (
        load_master_learnings,
        save_master_learnings,
        update_from_all_sources
    )
    MASTER_AVAILABLE = True
except ImportError:
    MASTER_AVAILABLE = False
    load_master_learnings = None
    save_master_learnings = None
    update_from_all_sources = None


class ContinuousLearningSystem:
    """
    Self-improving learning system
    
    Monitors new videos, auto-analyzes, updates brain
    """
    
    def __init__(self):
        print("="*70)
        print("🔄 CONTINUOUS LEARNING SYSTEM")
        print("="*70)
        
        self.data_dir = Path("data")
        self.training_dir = self.data_dir / "training"
        self.versions_dir = self.data_dir / "learning_versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        # Files
        self.training_data_file = self.training_dir / "goat_training_data.json"
        self.new_videos_queue = self.data_dir / "new_videos_queue.json"
        self.learning_log = self.data_dir / "learning_log.json"
        
        # Thresholds
        self.auto_analysis_threshold = 50  # Auto-analyze after 50 new outliers
        self.outlier_threshold = 2.0  # 2x+ relative performance
        
        # Load data
        self.training_data = self._load_training_data()
        self.queue = self._load_queue()
        self.log = self._load_log()
        
        print(f"   📊 Training clips: {len(self.training_data)}")
        print(f"   📥 Queue: {len(self.queue)} new videos")
        print(f"   📜 Learning cycles: {len(self.log.get('cycles', []))}")
    
    def _load_training_data(self):
        """Load existing training data"""
        if self.training_data_file.exists():
            with open(self.training_data_file) as f:
                return json.load(f)
        return []
    
    def _load_queue(self):
        """Load new videos queue"""
        if self.new_videos_queue.exists():
            with open(self.new_videos_queue) as f:
                return json.load(f)
        return []
    
    def _load_log(self):
        """Load learning log"""
        if self.learning_log.exists():
            with open(self.learning_log) as f:
                return json.load(f)
        return {'cycles': [], 'total_analyzed': len(self.training_data)}
    
    def _save_queue(self):
        """Save queue"""
        with open(self.new_videos_queue, 'w') as f:
            json.dump(self.queue, f, indent=2)
    
    def _save_log(self):
        """Save log"""
        with open(self.learning_log, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    # =========================================================================
    # ADD NEW VIDEOS
    # =========================================================================
    
    def add_new_videos(self, csv_path=None, video_data=None):
        """
        Add new videos to queue for analysis
        
        Args:
            csv_path: Path to CSV with new videos
            video_data: Or direct list of video dicts
        """
        
        print(f"\n{'='*70}")
        print("📥 ADDING NEW VIDEOS TO QUEUE")
        print(f"{'='*70}")
        
        new_clips = []
        
        if csv_path:
            if not PANDAS_AVAILABLE:
                print("   ❌ Pandas not available - cannot read CSV")
                return []
            
            # Load from CSV
            df = pd.read_csv(csv_path)
            print(f"   📄 CSV: {len(df)} rows")
            
            for idx, row in df.iterrows():
                clip = {
                    'video_id': self._extract_video_id(row.get('URL', '')),
                    'url': row.get('URL', ''),
                    'account': row.get('ACCOUNT', 'unknown'),
                    'platform': row.get('PLATTFORM', 'unknown'),
                    'performance': {
                        'views': int(row.get('VIEWS', 0)),
                        'likes': int(row.get('LIKES', 0)),
                        'comments': int(row.get('COMMENTS', 0))
                    },
                    'added_at': datetime.now().isoformat(),
                    'analyzed': False
                }
                new_clips.append(clip)
        
        elif video_data:
            new_clips = video_data
        
        # Calculate relative performance
        self._calculate_relative_performance(new_clips)
        
        # Filter outliers
        outliers = [c for c in new_clips if c.get('is_outlier', False)]
        
        print(f"\n   ✅ New clips: {len(new_clips)}")
        print(f"   🔥 Outliers (2x+): {len(outliers)}")
        
        # Add to queue
        self.queue.extend(outliers)
        self._save_queue()
        
        print(f"   📥 Queue updated: {len(self.queue)} clips waiting")
        
        # Check auto-analysis threshold
        if len(self.queue) >= self.auto_analysis_threshold:
            print(f"\n   ⚡ THRESHOLD REACHED! ({len(self.queue)} >= {self.auto_analysis_threshold})")
            
            try:
                auto = input("   🤖 Run auto-analysis now? (y/n): ").strip().lower()
                if auto == 'y':
                    asyncio.run(self.run_incremental_analysis())
            except (EOFError, KeyboardInterrupt):
                print("\n   ⚠️  Skipping auto-analysis (non-interactive mode)")
        
        return outliers
    
    def _extract_video_id(self, url):
        """Extract video ID from URL"""
        import re
        
        if not url:
            return f"unknown_{hash(str(url)) % 10000}"
        
        if 'instagram.com' in url:
            match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
            if match: return f"ig_{match.group(1)}"
        elif 'tiktok.com' in url:
            match = re.search(r'/video/(\d+)', url)
            if match: return f"tt_{match.group(1)}"
        elif 'youtube.com' in url or 'youtu.be' in url:
            match = re.search(r'/shorts/([A-Za-z0-9_-]+)', url)
            if match: return f"yt_{match.group(1)}"
        
        return f"unknown_{hash(url) % 10000}"
    
    def _calculate_relative_performance(self, clips):
        """Calculate relative performance per account"""
        
        if not NUMPY_AVAILABLE:
            print("   ⚠️  NumPy not available - skipping relative performance")
            return
        
        # Get existing training data for baseline
        by_account = defaultdict(list)
        
        for clip in self.training_data:
            account = clip.get('account', 'unknown')
            by_account[account].append(clip)
        
        # Add new clips
        for clip in clips:
            account = clip.get('account', 'unknown')
            by_account[account].append(clip)
        
        # Calculate relative performance
        for account, account_clips in by_account.items():
            views = [c.get('performance', {}).get('views', 0) for c in account_clips]
            views = [v for v in views if v > 0]
            
            if views:
                median = np.median(views)
                
                for clip in clips:
                    if clip.get('account') == account:
                        v = clip.get('performance', {}).get('views', 0)
                        clip['relative_performance'] = v / median if median > 0 else 1
                        clip['is_outlier'] = clip['relative_performance'] >= self.outlier_threshold
    
    # =========================================================================
    # INCREMENTAL ANALYSIS
    # =========================================================================
    
    async def run_incremental_analysis(self, batch_size=50):
        """
        Run incremental analysis on queued videos
        
        Uses 5-AI Ensemble to analyze new outliers
        Updates Master Learnings incrementally
        """
        
        print(f"\n{'='*70}")
        print("🔬 INCREMENTAL ANALYSIS")
        print(f"{'='*70}")
        
        if not self.queue:
            print("   ℹ️  Queue empty - nothing to analyze")
            return
        
        if not ANALYZE_AVAILABLE:
            print("   ❌ AnalyzeAndLearnV2 not available")
            return
        
        print(f"\n   📊 Queue size: {len(self.queue)}")
        print(f"   💰 Estimated cost: ${len(self.queue) * 0.15:.2f}")
        print(f"   ⏱️  Estimated time: {len(self.queue) * 0.3:.0f} minutes")
        
        try:
            confirm = input("\n   Proceed with incremental analysis? (y/n): ").strip().lower()
            if confirm != 'y':
                return
        except (EOFError, KeyboardInterrupt):
            print("\n   ⚠️  Skipping (non-interactive mode)")
            return
        
        # Create learning cycle entry
        cycle = {
            'cycle_id': len(self.log['cycles']) + 1,
            'started_at': datetime.now().isoformat(),
            'clips_to_analyze': len(self.queue),
            'status': 'running'
        }
        
        # Backup current Master Learnings
        self._create_version_backup()
        
        # Analyze with 5-AI Ensemble
        print("\n   🤖 Analyzing with 5-AI Ensemble...")
        
        analyzer = AnalyzeAndLearnV2()
        analyzer.clips = self.training_data + self.queue
        
        # Analyze queue
        patterns = await analyzer.analyze_progressive(
            clips=self.queue,
            batch_size=batch_size
        )
        
        # Save incremental patterns
        incremental_file = self.data_dir / f"incremental_patterns_cycle{cycle['cycle_id']}.json"
        with open(incremental_file, 'w') as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)
        
        print(f"\n   ✅ Incremental patterns saved: {incremental_file}")
        
        # Merge into training data
        self.training_data.extend(self.queue)
        
        with open(self.training_data_file, 'w') as f:
            json.dump(self.training_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Training data updated: {len(self.training_data)} total clips")
        
        # Update Master Learnings (weighted merge)
        if MASTER_AVAILABLE:
            print("\n   🧠 Updating Master Learnings...")
            
            master = load_master_learnings()
            
            # Weighted merge (new patterns get higher weight)
            self._weighted_merge_patterns(master, patterns, new_weight=1.2)
            
            save_master_learnings(master)
        else:
            print("\n   ⚠️  Master Learnings not available - skipping update")
        
        # Complete cycle
        cycle['completed_at'] = datetime.now().isoformat()
        cycle['clips_analyzed'] = len(self.queue)
        cycle['total_clips_now'] = len(self.training_data)
        cycle['patterns_file'] = str(incremental_file)
        cycle['status'] = 'completed'
        
        self.log['cycles'].append(cycle)
        self.log['total_analyzed'] = len(self.training_data)
        self._save_log()
        
        # Clear queue
        self.queue = []
        self._save_queue()
        
        print(f"\n✅ INCREMENTAL LEARNING COMPLETE!")
        print(f"   🧠 Brain version: {len(self.log['cycles'])}")
        print(f"   📊 Total clips learned from: {len(self.training_data)}")
        
        self._print_improvement_stats()
    
    def _weighted_merge_patterns(self, master, new_patterns, new_weight=1.2):
        """
        Merge new patterns into master with higher weight
        
        Newer patterns get priority over older ones
        """
        
        # New patterns get boosted
        # Old patterns stay but with lower effective weight
        
        # Merge with priority to new patterns
        if 'key_insights' in new_patterns:
            new_insights = new_patterns['key_insights']
            # Add new insights at front (higher priority)
            master['key_insights'] = new_insights + master.get('key_insights', [])
            # Deduplicate keeping first occurrence
            seen = set()
            unique = []
            for insight in master['key_insights']:
                normalized = insight.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)
                    unique.append(insight)
            master['key_insights'] = unique[:15]  # Keep top 15
        
        # Hook patterns
        if 'hook_patterns' in new_patterns:
            new_hooks = new_patterns['hook_patterns']
            existing_hooks = master.get('hook_mastery', {}).get('winning_hook_types', [])
            # Prepend new hooks
            master.setdefault('hook_mastery', {})['winning_hook_types'] = new_hooks + existing_hooks
            # Deduplicate
            seen = set()
            unique = []
            for hook in master['hook_mastery']['winning_hook_types']:
                hook_id = str(hook.get('type', '')) + str(hook.get('template', ''))
                if hook_id not in seen:
                    seen.add(hook_id)
                    unique.append(hook)
            master['hook_mastery']['winning_hook_types'] = unique[:20]
        
        # Power words
        if 'language_patterns' in new_patterns:
            # Extract power words from language patterns
            new_words = []
            for pattern in new_patterns['language_patterns']:
                if isinstance(pattern, dict) and 'power_words' in pattern:
                    new_words.extend(pattern['power_words'])
            
            existing_words = master.get('hook_mastery', {}).get('power_words', [])
            # Prepend new words
            master.setdefault('hook_mastery', {})['power_words'] = new_words + existing_words
            # Deduplicate (case-insensitive)
            seen = set()
            unique = []
            for word in master['hook_mastery']['power_words']:
                word_lower = word.lower()
                if word_lower not in seen:
                    seen.add(word_lower)
                    unique.append(word)
            master['hook_mastery']['power_words'] = unique[:50]
        
        # Similar for other sections...
        # New patterns get priority, old patterns kept but ranked lower
    
    def _create_version_backup(self):
        """Create versioned backup of current Master Learnings"""
        
        if not MASTER_AVAILABLE:
            return
        
        master = load_master_learnings()
        version = len(self.log['cycles']) + 1
        
        backup_file = self.versions_dir / f"MASTER_LEARNINGS_v{version}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(master, f, indent=2, ensure_ascii=False)
        
        print(f"\n   💾 Version backup created: v{version}")
    
    def _print_improvement_stats(self):
        """Print learning improvement statistics"""
        
        print(f"\n{'='*70}")
        print("📈 LEARNING IMPROVEMENT STATS")
        print(f"{'='*70}")
        
        cycles = self.log.get('cycles', [])
        
        if len(cycles) < 2:
            print("   ℹ️  Need at least 2 cycles for comparison")
            return
        
        # Compare last cycle with first cycle
        first = cycles[0]
        last = cycles[-1]
        
        print(f"\n   📊 Cycle 1 → Cycle {len(cycles)}:")
        print(f"      Clips: {first.get('clips_analyzed', 0)} → {last.get('total_clips_now', 0)}")
        print(f"      Growth: +{last.get('total_clips_now', 0) - first.get('clips_analyzed', 0)} clips")
        
        # Check Master Learnings growth
        if MASTER_AVAILABLE:
            master = load_master_learnings()
            
            print(f"\n   🧠 Brain Size:")
            print(f"      Key Insights: {len(master.get('key_insights', []))}")
            print(f"      Hook Patterns: {len(master.get('hook_mastery', {}).get('winning_hook_types', []))}")
            print(f"      Power Words: {len(master.get('hook_mastery', {}).get('power_words', []))}")
    
    # =========================================================================
    # STATUS & MONITORING
    # =========================================================================
    
    def print_status(self):
        """Print system status"""
        
        print(f"\n{'='*70}")
        print("📊 CONTINUOUS LEARNING SYSTEM STATUS")
        print(f"{'='*70}")
        
        print(f"\n🧠 BRAIN STATUS:")
        print(f"   Total clips learned from: {len(self.training_data)}")
        print(f"   Learning cycles completed: {len(self.log.get('cycles', []))}")
        cycles = self.log.get('cycles', [])
        if cycles:
            print(f"   Latest cycle: {cycles[-1].get('completed_at', 'Never')}")
        else:
            print(f"   Latest cycle: Never")
        
        print(f"\n📥 QUEUE:")
        print(f"   Clips waiting: {len(self.queue)}")
        print(f"   Auto-analysis threshold: {self.auto_analysis_threshold}")
        print(f"   Status: {'🔴 Threshold reached!' if len(self.queue) >= self.auto_analysis_threshold else '🟢 Below threshold'}")
        
        print(f"\n📈 GROWTH:")
        if len(self.log.get('cycles', [])) > 0:
            first_total = self.log['cycles'][0].get('clips_analyzed', 0)
            current_total = len(self.training_data)
            growth = current_total - first_total
            growth_pct = (growth / first_total * 100) if first_total > 0 else 0
            
            print(f"   Initial clips: {first_total}")
            print(f"   Current clips: {current_total}")
            print(f"   Growth: +{growth} clips (+{growth_pct:.1f}%)")
        
        if MASTER_AVAILABLE:
            master = load_master_learnings()
            print(f"\n🧠 BRAIN INTELLIGENCE:")
            print(f"   Version: {len(self.log.get('cycles', []))}")
            print(f"   Key Insights: {len(master.get('key_insights', []))}")
            print(f"   Hook Patterns: {len(master.get('hook_mastery', {}).get('winning_hook_types', []))}")
            print(f"   Structures: {len(master.get('structure_mastery', {}).get('winning_structures', []))}")
            print(f"   Power Words: {len(master.get('hook_mastery', {}).get('power_words', []))}")
        
        print(f"\n💾 VERSION HISTORY:")
        versions = list(self.versions_dir.glob("MASTER_LEARNINGS_v*.json"))
        print(f"   Backups available: {len(versions)}")
        for v in sorted(versions)[-5:]:
            print(f"      • {v.name}")


# =============================================================================
# CLI
# =============================================================================

async def main():
    """Main CLI"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous Learning System")
    parser.add_argument('--add-videos', type=str, help='CSV file with new videos')
    parser.add_argument('--auto-analyze', action='store_true', help='Run incremental analysis')
    parser.add_argument('--status', action='store_true', help='Show system status')
    
    args = parser.parse_args()
    
    system = ContinuousLearningSystem()
    
    if args.add_videos:
        system.add_new_videos(csv_path=args.add_videos)
    
    elif args.auto_analyze:
        await system.run_incremental_analysis()
    
    elif args.status:
        system.print_status()
    
    else:
        # Interactive mode
        print("\n📋 OPTIONS:")
        print("   1. Add new videos (CSV)")
        print("   2. Run incremental analysis")
        print("   3. Show status")
        print("   4. Exit")
        
        try:
            choice = input("\nChoice (1-4): ").strip()
            
            if choice == '1':
                csv_path = input("CSV path: ").strip()
                system.add_new_videos(csv_path=csv_path)
            
            elif choice == '2':
                await system.run_incremental_analysis()
            
            elif choice == '3':
                system.print_status()
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Cancelled (non-interactive mode)")


if __name__ == "__main__":
    asyncio.run(main())

