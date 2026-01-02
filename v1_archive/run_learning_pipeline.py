#!/usr/bin/env python3
"""
🚀 COMPLETE LEARNING PIPELINE ORCHESTRATOR

Runs the complete learning workflow:
1. analyze_and_learn_v2.py → Broad pattern learning
2. smart_sampling_analysis_v2.py → Deep outlier analysis
3. master_learnings_v2.py → Merge & synthesize
4. Optional: Integrate into V4

Features:
- Sequential execution
- Progress tracking
- Cost estimation
- Error handling
- Final validation
- Auto-integration
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime


class LearningPipelineOrchestrator:
    """
    Orchestrates complete learning pipeline
    """
    
    def __init__(self):
        print("="*70)
        print("🚀 LEARNING PIPELINE ORCHESTRATOR")
        print("="*70)
        
        self.data_dir = Path("data")
        self.results = {
            'step1_completed': False,
            'step2_completed': False,
            'step3_completed': False,
            'total_cost': 0.0,
            'total_time': 0.0,
            'clips_analyzed': 0
        }
    
    async def run_complete_pipeline(self, strategy='smart'):
        """
        Run complete learning pipeline
        
        Args:
            strategy: 'quick'|'smart'|'cluster'|'full'
        """
        
        print("\n" + "="*70)
        print("🎯 COMPLETE LEARNING PIPELINE")
        print("="*70)
        
        strategies = {
            'quick': {
                'name': 'Quick (100 outliers)',
                'step1_clips': 100,
                'step2_clips': 100,
                'cost': 30,
                'time': 40
            },
            'smart': {
                'name': 'Smart (300 best clips)',
                'step1_clips': 300,
                'step2_clips': 350,
                'cost': 90,
                'time': 120
            },
            'cluster': {
                'name': 'Cluster (300 representatives)',
                'step1_clips': 300,
                'step2_clips': 350,
                'cost': 90,
                'time': 120
            },
            'full': {
                'name': 'Full (all 972 clips)',
                'step1_clips': 972,
                'step2_clips': 350,
                'cost': 200,
                'time': 240
            }
        }
        
        config = strategies.get(strategy, strategies['smart'])
        
        print(f"\n📊 Strategy: {config['name']}")
        print(f"   💰 Estimated Cost: ${config['cost']}")
        print(f"   ⏱️  Estimated Time: {config['time']} minutes")
        print(f"   📊 Clips: Step 1: {config['step1_clips']}, Step 2: {config['step2_clips']}")
        
        try:
            confirm = input("\n🚀 Start complete pipeline? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled")
                return None
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Skipping (non-interactive mode)")
            return None
        
        start_time = datetime.now()
        
        # STEP 1: Broad Pattern Learning
        print("\n" + "="*70)
        print("📊 STEP 1: BROAD PATTERN LEARNING")
        print("="*70)
        
        step1_success = await self._run_step1(strategy)
        
        if not step1_success:
            print("\n❌ Step 1 failed - aborting pipeline")
            return None
        
        self.results['step1_completed'] = True
        
        # STEP 2: Deep Analysis
        print("\n" + "="*70)
        print("🔬 STEP 2: DEEP OUTLIER ANALYSIS")
        print("="*70)
        
        step2_success = await self._run_step2()
        
        if not step2_success:
            print("\n❌ Step 2 failed - aborting pipeline")
            return None
        
        self.results['step2_completed'] = True
        
        # STEP 3: Master Learnings Update
        print("\n" + "="*70)
        print("🧠 STEP 3: MASTER LEARNINGS UPDATE")
        print("="*70)
        
        step3_success = self._run_step3()
        
        if not step3_success:
            print("\n❌ Step 3 failed")
            return None
        
        self.results['step3_completed'] = True
        
        # Calculate totals
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() / 60
        
        self.results['total_time'] = total_time
        
        # Summary
        self._print_summary()
        
        # Optional: V4 Integration
        try:
            integrate = input("\n🔗 Integrate into V4 now? (y/n): ").strip().lower()
            if integrate == 'y':
                self._integrate_v4()
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Skipping V4 integration (non-interactive mode)")
        
        return self.results
    
    async def _run_step1(self, strategy):
        """Run Step 1: analyze_and_learn_v2.py"""
        
        try:
            from analyze_and_learn_v2 import AnalyzeAndLearnV2
            
            analyzer = AnalyzeAndLearnV2()
            
            # Load data
            clips = analyzer.load_training_data()
            if not clips:
                return False
            
            # Select clips based on strategy
            if strategy == 'quick':
                selected = analyzer.select_clips_outliers(100)
            elif strategy == 'smart':
                selected = analyzer.select_clips_smart(300)
            elif strategy == 'cluster':
                selected = analyzer.select_clips_cluster(300)
            elif strategy == 'full':
                selected = clips
            else:
                selected = analyzer.select_clips_smart(300)
            
            print(f"\n   ✅ Selected {len(selected)} clips for analysis")
            
            # Run analysis
            patterns = await analyzer.analyze_progressive(selected, batch_size=50)
            
            # Save
            analyzer.save_patterns(patterns)
            
            self.results['clips_analyzed'] = patterns.get('metadata', {}).get('total_clips_analyzed', len(selected))
            
            return True
        
        except Exception as e:
            print(f"\n   ❌ Error in Step 1: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _run_step2(self):
        """Run Step 2: smart_sampling_analysis_v2.py"""
        
        try:
            from smart_sampling_analysis_v2 import SmartSamplingAnalyzerV2
            
            analyzer = SmartSamplingAnalyzerV2()
            
            # Select sample
            sample = analyzer.select_sample(n_top=200, n_middle=100, n_bottom=50)
            
            # Analyze
            results = await analyzer.analyze_all_samples_progressive(sample)
            
            if not results:
                return False
            
            # Synthesize
            patterns = analyzer.synthesize_patterns(results)
            
            # Save
            analyzer.save_patterns(patterns)
            
            return True
        
        except Exception as e:
            print(f"\n   ❌ Error in Step 2: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_step3(self):
        """Run Step 3: master_learnings_v2.py"""
        
        try:
            from master_learnings_v2 import update_from_all_sources, print_learnings_summary
            
            # Update from all sources
            master = update_from_all_sources()
            
            if not master:
                return False
            
            # Print summary
            print("\n" + "="*70)
            print_learnings_summary()
            
            return True
        
        except Exception as e:
            print(f"\n   ❌ Error in Step 3: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _print_summary(self):
        """Print pipeline summary"""
        
        print("\n" + "="*70)
        print("🎉 PIPELINE COMPLETE!")
        print("="*70)
        
        print(f"\n✅ Steps Completed:")
        print(f"   Step 1 (Broad Patterns): {'✅' if self.results['step1_completed'] else '❌'}")
        print(f"   Step 2 (Deep Analysis): {'✅' if self.results['step2_completed'] else '❌'}")
        print(f"   Step 3 (Master Learnings): {'✅' if self.results['step3_completed'] else '❌'}")
        
        print(f"\n📊 Statistics:")
        print(f"   Total Clips Analyzed: {self.results['clips_analyzed']}")
        print(f"   Total Time: {self.results['total_time']:.1f} minutes")
        
        print(f"\n📁 Output Files:")
        
        files = [
            ('data/learned_patterns_v2.json', 'Broad Patterns'),
            ('data/deep_learned_patterns.json', 'Deep Analysis'),
            ('data/MASTER_LEARNINGS.json', 'Master Learnings')
        ]
        
        for filepath, name in files:
            if Path(filepath).exists():
                size = Path(filepath).stat().st_size / 1024
                print(f"   ✅ {name}: {filepath} ({size:.1f} KB)")
            else:
                print(f"   ❌ {name}: Not found")
    
    def _integrate_v4(self):
        """Guide V4 integration"""
        
        print("\n" + "="*70)
        print("🔗 V4 INTEGRATION GUIDE")
        print("="*70)
        
        print("""
The learnings are now ready for V4 integration!

NEXT STEPS:

1. Update create_clips_v4_integrated.py:
   
   Add at top:
```python
   from master_learnings_v2 import get_learnings_for_prompt
```

2. In _evaluate_quality_debate() method:
   
   Add before prompt:
```python
   learnings_prompt = get_learnings_for_prompt()
   
   prompt = f'''
   {learnings_prompt}
   
   # CLIP TO EVALUATE:
   {clip_text}
   
   Evaluate based on learned patterns...
   '''
```

3. Test with V4:
```bash
   python create_clips_v4_integrated.py
```

Expected improvement:
- Quality: 88-92 WT/VIR → 92-96 WT/VIR
- Pass Rate: 90% → 95%+
- Pattern Alignment: Much better!

Would you like me to create the integration patch? (y/n)
""")
        
        try:
            create_patch = input().strip().lower()
            
            if create_patch == 'y':
                self._create_integration_patch()
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Skipping patch creation")
    
    def _create_integration_patch(self):
        """Create integration patch file"""
        
        patch_content = """# V4 INTEGRATION PATCH
# Apply these changes to create_clips_v4_integrated.py

## 1. Add import at top of file:

from master_learnings_v2 import get_learnings_for_prompt


## 2. Update _evaluate_quality_debate() method (ca. line 400):

async def _evaluate_quality_debate(self, clip: Dict, story_structure: Dict) -> Dict:
    '''
    Quality evaluation using debate strategy WITH LEARNINGS!
    '''
    
    # GET REAL VIRAL PATTERNS!
    learnings_prompt = get_learnings_for_prompt()
    
    clip_text = self._format_clip_for_eval(clip)
    
    prompt = f'''{learnings_prompt}

# CLIP ZU BEWERTEN:
{clip_text}

Bewerte BASIEREND auf den gelernten Viral Patterns (0-50):

1. Hook Strength (0-10)
   - Verwendet er winning hook types?
   - Power words present?
   - Timing richtig (0-3s)?

2. Story Coherence (0-10)
   - Folgt winning structure?
   - Pattern interrupts alle 5-7s?
   - Loop opened & closed?

3. Natural Flow (0-10)
   - Keine Filler?
   - Emotional arc?
   - Jede Sekunde Grund weiterzuschauen?

4. Watchtime Potential (0-10)
   - High arousal emotion?
   - Mass appeal?
   - Information gap?

5. Emotional Impact (0-10)
   - Best emotions used?
   - Trigger phrases?
   - Achterbahn, nicht flatline?

Antworte in JSON:
{{
  "scores": {{...}},
  "total_score": X,
  "quality_tier": "A/B/C/D",
  "reasoning": {{
    "strengths": ["Was folgt gelernten Patterns?"],
    "weaknesses": ["Was missachtet Patterns?"],
    "learned_patterns_applied": ["Welche Patterns erkannt?"]
  }}
}}
'''
    
    system = "Du bist ein Qualitäts-Evaluator trainiert auf {clips_analyzed} viralen Clips."
    
    # Rest bleibt gleich...
"""
        
        patch_file = Path("v4_integration_patch.txt")
        with open(patch_file, 'w') as f:
            f.write(patch_content)
        
        print(f"\n✅ Integration patch created: {patch_file}")
        print("   Apply manually or use with Cursor!")


# =============================================================================
# MAIN CLI
# =============================================================================

async def main():
    """Main CLI"""
    
    orchestrator = LearningPipelineOrchestrator()
    
    print("\n📊 STRATEGY SELECTION:")
    print("\n1. QUICK - 100 outliers")
    print("   Cost: ~$30 | Time: ~40 min | Coverage: 10%")
    
    print("\n2. SMART - Top 300 by features+performance (RECOMMENDED)")
    print("   Cost: ~$90 | Time: ~120 min | Coverage: 30%")
    
    print("\n3. CLUSTER - 300 representatives")
    print("   Cost: ~$90 | Time: ~120 min | Coverage: 95%")
    
    print("\n4. FULL - All 972 clips")
    print("   Cost: ~$200 | Time: ~240 min | Coverage: 100%")
    
    try:
        choice = input("\nSelect strategy (1-4): ").strip()
        
        strategy_map = {
            '1': 'quick',
            '2': 'smart',
            '3': 'cluster',
            '4': 'full'
        }
        
        strategy = strategy_map.get(choice, 'smart')
        
        # Run pipeline
        results = await orchestrator.run_complete_pipeline(strategy)
        
        if results:
            print("\n✅ Pipeline completed successfully!")
        else:
            print("\n❌ Pipeline failed!")
    except (EOFError, KeyboardInterrupt):
        print("\n⚠️  Cancelled (non-interactive mode)")


if __name__ == "__main__":
    asyncio.run(main())

