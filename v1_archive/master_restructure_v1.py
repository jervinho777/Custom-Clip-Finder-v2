#!/usr/bin/env python3
"""
Master Restructure V1

Integrates restructure learnings into V4 pipeline
Uses learned patterns to improve clip restructuring
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent))

from create_clips_v4_integrated import CreateClipsV4Integrated


class MasterRestructure:
    """Intelligent restructure using learned patterns"""
    
    def __init__(self):
        self.v4 = CreateClipsV4Integrated()
        self.learnings_dir = Path("data/learnings")
        
        # Load learnings
        self.restructure_learnings = self._load_restructure_learnings()
        self.viral_learnings = self._load_viral_learnings()
        
        print(f"\n{'='*70}")
        print(f"🧠 MASTER RESTRUCTURE V1 - INITIALIZED")
        print(f"{'='*70}")
        
        if self.restructure_learnings:
            print(f"\n   ✅ Restructure Learnings:")
            print(f"      Rules: {self.restructure_learnings['segment_selection']['count']}")
            print(f"      Timing patterns: {self.restructure_learnings['timing_optimization']['count']}")
            print(f"      Quality signals: {self.restructure_learnings['quality_signals']['count']}")
        else:
            print(f"\n   ⚠️  No restructure learnings found!")
            print(f"      Run: python analyze_restructures_v1.py first")
        
        if self.viral_learnings:
            print(f"\n   ✅ Viral Learnings: Available")
        else:
            print(f"\n   ⚠️  No viral learnings found!")
    
    def _load_restructure_learnings(self) -> Dict:
        """Load restructure learnings"""
        
        learnings_file = self.learnings_dir / 'RESTRUCTURE_LEARNINGS_V1.json'
        
        if not learnings_file.exists():
            return None
        
        with open(learnings_file) as f:
            return json.load(f)
    
    def _load_viral_learnings(self) -> Dict:
        """Load viral pattern learnings"""
        
        learnings_file = self.learnings_dir / 'MASTER_LEARNINGS.json'
        
        if not learnings_file.exists():
            return None
        
        with open(learnings_file) as f:
            return json.load(f)
    
    async def restructure_with_learnings(
        self,
        clip: Dict,
        story: Dict,
        clip_index: int = 0
    ) -> Dict:
        """
        Restructure clip using learned patterns
        
        Uses both restructure learnings (how to cut) and
        viral learnings (what makes viral)
        """
        
        print(f"\n{'='*70}")
        print(f"🔧 SMART RESTRUCTURE - Clip #{clip_index + 1}")
        print(f"{'='*70}")
        
        original_duration = clip['end'] - clip['start']
        original_segments = len(clip['segments'])
        
        print(f"\n   📊 Original:")
        print(f"      Duration: {original_duration:.1f}s")
        print(f"      Segments: {original_segments}")
        
        # Format clip info for AI
        clip_text = self._format_clip(clip)
        
        # Extract learned rules
        rules_summary = self._extract_rules_summary()
        
        # Create restructure prompt with learnings
        prompt = f"""
INTELLIGENT RESTRUCTURE - Using Learned Patterns

CURRENT CLIP ({original_duration:.1f}s, {original_segments} segments):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{clip_text}

LEARNED RESTRUCTURE PATTERNS (from 9 viral examples):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{rules_summary}

YOUR TASK:
Restructure this clip using the learned patterns.

RESPOND WITH JSON:
{{
  "keep_segments": [0, 2, 4],  // Indices to keep
  "reasoning": "Why these segments create viral potential",
  "improvements": [
    "Applied rule: Hook in first 3s",
    "Applied rule: Removed abstract buildup",
    "Applied rule: ..."
  ],
  "expected_score_improvement": "+5 points (from learned patterns)"
}}

Focus on ACTIONABLE cuts based on learned rules.
Be SPECIFIC about which segments to keep/remove and WHY.
"""

        system = """You are an expert video editor trained on viral restructure patterns.

You have analyzed 9 successful longform→viral clip transformations.

You understand:
- Optimal clip length (30-65s)
- Hook placement (0-3s)
- What content to keep vs remove
- Pacing and transitions
- Viral pattern application

Apply learned rules PRECISELY to maximize viral potential.

Return ONLY valid JSON."""

        print(f"\n   🤖 Analyzing with learned patterns...")
        
        # Get AI recommendation
        result = await self.v4.consensus.build_consensus(
            prompt=prompt,
            system=system,
            strategy='parallel_vote'
        )
        
        # Parse response
        try:
            response_text = result.get('consensus', '')
            
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            recommendation = json.loads(json_text)
            
            print(f"\n   ✅ Recommendation received")
            print(f"      Confidence: {result.get('confidence', 0):.0%}")
            
            # Apply recommendation
            keep_indices = recommendation.get('keep_segments', [])
            
            if not keep_indices:
                print(f"   ⚠️  No segments recommended, keeping original")
                return clip
            
            # Create restructured clip
            new_segments = [clip['segments'][i] for i in keep_indices if i < len(clip['segments'])]
            
            if not new_segments:
                print(f"   ⚠️  Invalid indices, keeping original")
                return clip
            
            restructured = {
                **clip,
                'segments': new_segments,
                'start': new_segments[0]['start'],
                'end': new_segments[-1]['end'],
                'original_indices': keep_indices,
                'restructure_reasoning': recommendation.get('reasoning', ''),
                'improvements': recommendation.get('improvements', []),
                'learned_restructure': True
            }
            
            new_duration = restructured['end'] - restructured['start']
            
            print(f"\n   ✅ Restructured:")
            print(f"      Duration: {original_duration:.1f}s → {new_duration:.1f}s ({new_duration - original_duration:+.1f}s)")
            print(f"      Segments: {original_segments} → {len(new_segments)}")
            
            print(f"\n   💡 Improvements applied:")
            for imp in recommendation.get('improvements', [])[:5]:
                print(f"      • {imp[:80]}")
            
            return restructured
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parsing failed: {e}")
            print(f"   Using original clip")
            return clip
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            print(f"   Using original clip")
            return clip
    
    def _format_clip(self, clip: Dict) -> str:
        """Format clip for prompt"""
        
        formatted = []
        for i, seg in enumerate(clip['segments']):
            formatted.append(f"[{i}] {seg['start']:.1f}s: {seg['text'][:100]}")
        
        return '\n'.join(formatted)
    
    def _extract_rules_summary(self) -> str:
        """Extract concise rules summary"""
        
        if not self.restructure_learnings:
            return "No learned patterns available"
        
        rules = []
        
        # Selection rules (top 10)
        selection_rules = self.restructure_learnings['segment_selection']['rules'][:10]
        rules.append("SEGMENT SELECTION:")
        for rule in selection_rules:
            rules.append(f"  • {rule[:100]}")
        
        # Timing patterns
        if self.restructure_learnings['timing_optimization']['patterns']:
            rules.append("\nTIMING OPTIMIZATION:")
            for pattern in self.restructure_learnings['timing_optimization']['patterns'][:3]:
                if isinstance(pattern, dict):
                    if 'clip_length_optimal' in pattern:
                        rules.append(f"  • Optimal length: {pattern['clip_length_optimal']}")
                    if 'hook_position' in pattern:
                        rules.append(f"  • Hook position: {pattern['hook_position']}")
        
        # Quality signals
        if self.restructure_learnings['quality_signals']['patterns']:
            rules.append("\nQUALITY SIGNALS:")
            for pattern in self.restructure_learnings['quality_signals']['patterns'][:2]:
                if isinstance(pattern, dict) and 'what_makes_good_cut' in pattern:
                    for signal in pattern['what_makes_good_cut'][:3]:
                        rules.append(f"  ✅ {signal[:80]}")
        
        return '\n'.join(rules)
    
    async def test_on_viral_clip(self):
        """Test restructure on proven viral clip (Dieter Lange)"""
        
        print(f"\n{'='*70}")
        print(f"🧪 TESTING ON PROVEN VIRAL CLIP")
        print(f"{'='*70}")
        
        # Load Dieter Lange viral clip
        clip_path = Path("output/clips/Dieter Lange Viral Clip.mp4")
        
        if not clip_path.exists():
            print(f"\n❌ Viral clip not found: {clip_path}")
            return
        
        # Load transcript
        transcript_file = Path("data/cache/transcripts/Dieter Lange Viral Clip_transcript.json")
        
        if not transcript_file.exists():
            print(f"\n❌ Transcript not found!")
            return
        
        with open(transcript_file) as f:
            data = json.load(f)
            segments = data['segments']
        
        # Create clip dict
        clip = {
            'start': 0,
            'end': segments[-1]['end'],
            'segments': segments,
            'video_path': str(clip_path),
            'original_indices': list(range(len(segments)))
        }
        
        story = {'storylines': [], 'standalone_moments': []}
        
        print(f"\n   Original clip: 2.4M views proven viral")
        print(f"   Previous test: 47/50 (original) → 41/50 (old restructure)")
        
        # Test 1: Evaluate original
        print(f"\n{'='*70}")
        print(f"📊 TEST 1: ORIGINAL (No Restructure)")
        print(f"{'='*70}")
        
        result_original = await self.v4._evaluate_quality_debate(clip, story)
        score_original = result_original.get('score', 0)
        
        print(f"\n   ✅ Score: {score_original}/50")
        
        # Test 2: Smart restructure with learnings
        print(f"\n{'='*70}")
        print(f"📊 TEST 2: SMART RESTRUCTURE (With Learnings)")
        print(f"{'='*70}")
        
        restructured = await self.restructure_with_learnings(clip, story, 0)
        
        result_restructured = await self.v4._evaluate_quality_debate(restructured, story)
        score_restructured = result_restructured.get('score', 0)
        
        print(f"\n   ✅ Score: {score_restructured}/50")
        
        # Comparison
        print(f"\n{'='*70}")
        print(f"📊 RESULTS")
        print(f"{'='*70}")
        
        delta = score_restructured - score_original
        
        print(f"\n   ORIGINAL:     {score_original}/50")
        print(f"   RESTRUCTURED: {score_restructured}/50")
        print(f"   DELTA:        {delta:+.1f} points")
        
        if delta > 0:
            print(f"\n   ✅ SUCCESS! Learned restructure IMPROVES score!")
            print(f"   System is working! 🎉")
        elif delta == 0:
            print(f"\n   ≈ NEUTRAL - No degradation at least")
        else:
            print(f"\n   ⚠️  Restructure still damages score")
            print(f"   Need more examples or better rules")
        
        return {
            'original_score': score_original,
            'restructured_score': score_restructured,
            'delta': delta
        }


async def main():
    """Main entry point"""
    
    master = MasterRestructure()
    
    if not master.restructure_learnings:
        print(f"\n❌ Cannot proceed without restructure learnings!")
        print(f"   Run: python analyze_restructures_v1.py first")
        return
    
    # Test on viral clip
    print(f"\n{'='*70}")
    print(f"🎯 TESTING LEARNED RESTRUCTURE")
    print(f"{'='*70}")
    print(f"\nThis will:")
    print(f"  1. Load Dieter Lange viral clip (2.4M views)")
    print(f"  2. Evaluate original (should be ~47/50)")
    print(f"  3. Apply learned restructure patterns")
    print(f"  4. Evaluate restructured version")
    print(f"  5. Compare scores!")
    
    response = input(f"\nReady to test? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Cancelled.")
        return
    
    results = await master.test_on_viral_clip()
    
    if results:
        print(f"\n{'='*70}")
        print(f"🎯 FINAL VERDICT")
        print(f"{'='*70}")
        
        if results['delta'] >= 0:
            print(f"\n   ✅ SYSTEM WORKS!")
            print(f"   Learned restructure preserves/improves quality")
            print(f"\n   🚀 Ready to integrate into production V4!")
        else:
            print(f"\n   ⚠️  NEEDS MORE TRAINING")
            print(f"   Add more examples and re-analyze")
            print(f"   Target: 20+ examples for production")


if __name__ == '__main__':
    asyncio.run(main())

