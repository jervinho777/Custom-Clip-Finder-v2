#!/usr/bin/env python3
"""
2-Stage Fast Pipeline - DEBUG/TEST VERSION

Stage 1: Fast pre-screening with Opus 4.5 (cheap, quick)
Stage 2: Godmode only on top candidates (focused, deep)

NOT integrated into main V4 - separate test script!
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
import sys
import re

sys.path.insert(0, str(Path(__file__).parent))

from create_clips_v4_integrated import CreateClipsV4Integrated


class FastPipelineTest:
    """2-Stage pipeline for faster testing"""
    
    def __init__(self):
        self.v4 = CreateClipsV4Integrated()
        self.stats = {
            'moments_found': 0,
            'pre_screened': 0,
            'top_selected': 0,
            'godmode_evaluated': 0,
            'clips_created': 0
        }
    
    async def quick_pre_score_opus(self, moment: Dict, segments: List[Dict]) -> Dict:
        """
        Fast single-AI pre-screening with Opus 4.5
        Returns score + reason
        """
        
        # Extract moment segments
        moment_start = moment['start']
        moment_end = moment['end']
        moment_segments = [
            seg for seg in segments
            if moment_start <= seg.get('start', 0) < moment_end
        ]
        
        if not moment_segments:
            return {'score': 0, 'reason': 'No segments'}
        
        # Format for AI (first 10 segments only for speed)
        clip_text = '\n'.join([
            f"[{seg['start']:.1f}s] {seg['text'][:100]}"
            for seg in moment_segments[:10]
        ])
        
        # Quick scoring prompt
        prompt = f"""
QUICK PRE-SCORE (0-100):

MOMENT ({moment_end - moment_start:.0f}s):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{clip_text}

Check MASTER_LEARNINGS patterns quickly:
- Hook strength (0-3s): Paradox? Power words? Direct address?
- Story potential: Loop opened? Payoff clear?
- Viral signals: Emotion? Curiosity? Universal pain point?

SCORING GUIDE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
90-100: Exceptional (strong hook + loop + emotion)
80-89:  Excellent (good hook + story)
70-79:  Good (solid potential)
60-69:  Average (some potential)
<60:    Weak (missing key patterns)

RESPOND WITH:
Score: [0-100]
Reason: [one specific line citing pattern]

Example:
Score: 85
Reason: Strong paradox hook in 0-2s + power word "niemals" + health pain point

BE STRICT. Only 80+ = worth deep evaluation.
"""

        system = """You are Opus 4.5, viral content pre-screener.

Fast, decisive evaluation using MASTER_LEARNINGS.
One pass only - be brutal and specific.
Cite specific learned patterns in reason."""

        try:
            # Use consensus engine with Opus
            if not self.v4.consensus:
                return {'score': 50, 'reason': 'Consensus engine not available'}
            
            # Call with single AI (Opus) for speed
            result = await self.v4.consensus.ensemble.call_ai(
                'opus',
                prompt,
                system=system,
                max_tokens=150  # Short response
            )
            
            if not result.get('success'):
                return {'score': 50, 'reason': 'AI call failed'}
            
            response = result.get('content', '')
            
            # Extract score
            score_match = re.search(r'Score:\s*(\d+)', response)
            score = int(score_match.group(1)) if score_match else 50
            
            # Extract reason
            reason_match = re.search(r'Reason:\s*(.+?)(?:\n|$)', response)
            reason = reason_match.group(1).strip() if reason_match else 'No reason given'
            
            return {
                'score': score,
                'reason': reason[:200]  # Truncate
            }
            
        except Exception as e:
            print(f"   ⚠️  Pre-score error: {e}")
            return {'score': 50, 'reason': f'Error: {str(e)[:100]}'}
    
    async def run_fast_pipeline(self, video_path: str, top_n: int = 5):
        """
        Run 2-stage fast pipeline
        
        Args:
            video_path: Path to video
            top_n: How many top clips to evaluate with Godmode (default: 5)
        """
        
        print(f"\n{'='*70}")
        print(f"🚀 2-STAGE FAST PIPELINE - DEBUG TEST")
        print(f"{'='*70}")
        print(f"\n   Video: {Path(video_path).name}")
        print(f"   Top N for Godmode: {top_n}")
        
        # Load transcript
        print(f"\n📝 Loading transcript...")
        
        video_file = Path(video_path)
        transcript_file = Path(f"data/cache/transcripts/{video_file.stem}_transcript.json")
        
        if not transcript_file.exists():
            print(f"   ❌ No transcript found!")
            print(f"   Run transcription first or use cached video")
            return
        
        with open(transcript_file) as f:
            data = json.load(f)
            segments = data['segments']
        
        print(f"   ✅ Loaded {len(segments)} segments")
        
        # STAGE 1: Find Moments
        print(f"\n{'='*70}")
        print(f"STAGE 1: FIND MOMENTS")
        print(f"{'='*70}")
        
        # Get story analysis
        story = await self.v4._analyze_story_ensemble(segments)
        
        # Find moments
        moments = await self.v4._find_moments_with_consensus(segments, story)
        
        self.stats['moments_found'] = len(moments)
        
        print(f"\n   ✅ Found {len(moments)} moments")
        
        if not moments:
            print(f"   ❌ No moments found!")
            return
        
        # STAGE 2: Fast Pre-Screening with Opus
        print(f"\n{'='*70}")
        print(f"STAGE 2: FAST PRE-SCREENING (Opus 4.5)")
        print(f"{'='*70}")
        
        scored_moments = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n   📊 Pre-scoring {i}/{len(moments)}...", end=' ', flush=True)
            
            score_result = await self.quick_pre_score_opus(moment, segments)
            
            scored_moments.append({
                **moment,
                'pre_score': score_result['score'],
                'pre_reason': score_result['reason']
            })
            
            print(f"{score_result['score']}/100")
            print(f"      └─ {score_result['reason'][:80]}")
            
            self.stats['pre_screened'] += 1
        
        # Sort by pre-score
        scored_moments.sort(key=lambda m: m['pre_score'], reverse=True)
        
        # Select top N (or all 80+)
        top_moments = [m for m in scored_moments if m['pre_score'] >= 80][:top_n]
        
        if not top_moments:
            # If none score 80+, take top N anyway
            top_moments = scored_moments[:top_n]
            print(f"\n   ⚠️  No clips scored 80+, taking top {top_n}")
        
        self.stats['top_selected'] = len(top_moments)
        
        print(f"\n   ✅ Selected {len(top_moments)} top candidates")
        print(f"   📊 Score range: {top_moments[-1]['pre_score']}-{top_moments[0]['pre_score']}")
        
        # Show top candidates
        print(f"\n   🏆 TOP CANDIDATES:")
        for i, m in enumerate(top_moments, 1):
            print(f"      {i}. Score {m['pre_score']}/100 - {m['pre_reason'][:60]}")
        
        # STAGE 3: Godmode on Top Candidates Only
        print(f"\n{'='*70}")
        print(f"STAGE 3: DEEP EVALUATION (Godmode - Top {len(top_moments)} Only)")
        print(f"{'='*70}")
        
        quality_results = []
        
        for i, moment in enumerate(top_moments, 1):
            print(f"\n   🎯 Godmode evaluation {i}/{len(top_moments)}")
            
            # Extract segments for this moment
            moment_segments = [
                seg for seg in segments
                if moment['start'] <= seg.get('start', 0) < moment['end']
            ]
            
            clip = {
                'start': moment['start'],
                'end': moment['end'],
                'segments': moment_segments,
                'video_path': str(video_path),
                'pre_score': moment['pre_score'],
                'structure': {
                    'segments': moment_segments
                }
            }
            
            # Run Godmode evaluation
            result = await self.v4._evaluate_quality_debate(clip, story)
            
            score = result.get('total_score', 0)
            tier = result.get('quality_tier', 'F')
            
            quality_results.append({
                'clip': clip,
                'score': score,
                'tier': tier,
                'pre_score': moment['pre_score'],
                'reasoning': result.get('reasoning', {})
            })
            
            print(f"      Pre-score: {moment['pre_score']}/100")
            print(f"      Godmode:   {score}/50 ({tier})")
            
            self.stats['godmode_evaluated'] += 1
        
        # Filter passing clips
        passing = [r for r in quality_results if r['score'] >= 40]
        
        self.stats['clips_created'] = len(passing)
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 RESULTS SUMMARY")
        print(f"{'='*70}")
        
        print(f"\n   STAGE 1: Find Moments")
        print(f"      Found: {self.stats['moments_found']} moments")
        
        print(f"\n   STAGE 2: Pre-Screening (Opus)")
        print(f"      Evaluated: {self.stats['pre_screened']} moments")
        print(f"      Top selected: {self.stats['top_selected']} (for Godmode)")
        
        print(f"\n   STAGE 3: Deep Evaluation (Godmode)")
        print(f"      Evaluated: {self.stats['godmode_evaluated']} clips")
        print(f"      Passed (40+): {self.stats['clips_created']} clips")
        
        # Time/Cost Comparison
        print(f"\n   💰 EFFICIENCY:")
        print(f"      Old way: {self.stats['moments_found']} × Godmode = ~{self.stats['moments_found'] * 1.5:.0f} min, ${self.stats['moments_found'] * 0.5:.1f}")
        print(f"      New way: {self.stats['pre_screened']} × Pre-screen + {self.stats['godmode_evaluated']} × Godmode")
        print(f"              = ~{self.stats['pre_screened'] * 0.1 + self.stats['godmode_evaluated'] * 1.5:.0f} min, ${self.stats['pre_screened'] * 0.05 + self.stats['godmode_evaluated'] * 0.5:.1f}")
        
        savings_time = (self.stats['moments_found'] * 1.5) - (self.stats['pre_screened'] * 0.1 + self.stats['godmode_evaluated'] * 1.5)
        savings_cost = (self.stats['moments_found'] * 0.5) - (self.stats['pre_screened'] * 0.05 + self.stats['godmode_evaluated'] * 0.5)
        
        print(f"      SAVED: ~{savings_time:.0f} min, ${savings_cost:.1f} 💎")
        
        # Show results
        if passing:
            print(f"\n   🎉 PASSING CLIPS:")
            for i, r in enumerate(passing, 1):
                print(f"      {i}. Pre: {r['pre_score']}/100 → Godmode: {r['score']}/50 ({r['tier']})")
        else:
            print(f"\n   ⚠️  No clips passed quality gate")
            if quality_results:
                print(f"   Top scored: {max([r['score'] for r in quality_results])}/50")
        
        return quality_results


async def main():
    """Main entry point"""
    
    import sys
    
    print(f"\n{'='*70}")
    print(f"🚀 2-STAGE FAST PIPELINE TESTER")
    print(f"{'='*70}")
    print(f"\nDEBUG/TEST SCRIPT - Not integrated into main V4")
    print(f"\nUsage: python test_2stage_fast.py [video_path] [top_n]")
    print(f"Example: python test_2stage_fast.py 'data/uploads/Dieter Lange.mp4' 5")
    
    # Get args
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    else:
        # Interactive
        print(f"\n{'='*70}")
        print(f"SELECT VIDEO")
        print(f"{'='*70}")
        
        videos = [
            "data/uploads/Dieter Lange.mp4",
            "data/training/Longform and Clips/Chris Surel.mp4",
            "data/training/Longform and Clips/Patric Heizmann RN2021.mp4",
            "data/training/Longform and Clips/USED_17 - Krankheit.mp4"
        ]
        
        for i, v in enumerate(videos, 1):
            exists = "✅" if Path(v).exists() else "❌"
            print(f"   {i}. {exists} {Path(v).name}")
        
        choice = input(f"\nSelect (1-{len(videos)} or path): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(videos):
            video_path = videos[int(choice) - 1]
        else:
            video_path = choice
        
        top_n_input = input(f"Top N for Godmode (default: 5): ").strip()
        top_n = int(top_n_input) if top_n_input else 5
    
    # Run
    tester = FastPipelineTest()
    await tester.run_fast_pipeline(video_path, top_n)


if __name__ == '__main__':
    asyncio.run(main())

