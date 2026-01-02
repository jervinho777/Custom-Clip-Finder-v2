#!/usr/bin/env python3
"""
Code 1: Analyze Isolated Viral Clips
Smart sampling + direct principle extraction
Output: ISOLATED_PATTERNS.json
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

class IsolatedClipsAnalyzer:
    """Analyze isolated viral clips for performance patterns"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.output_dir = Path("data/learnings")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.training_dir = Path("data/training")
    
    async def analyze(self):
        """Main analysis workflow"""
        
        print(f"\n{'='*70}")
        print(f"📊 CODE 1: ISOLATED CLIPS ANALYSIS")
        print(f"{'='*70}")
        
        # Load clips
        print(f"\n📂 Loading clips...")
        clips = self._load_clips()
        print(f"   ✅ Loaded {len(clips)} high-performing clips")
        
        if not clips:
            print(f"   ⚠️  No clips found - check goat_training_data.json")
            return {}
        
        # Smart sampling
        print(f"\n🎯 Smart sampling (Top 50 by performance)...")
        top_clips = self._smart_sample(clips, n=50)
        print(f"   ✅ Selected top {len(top_clips)} clips")
        avg_views = sum(c['performance']['views'] for c in top_clips) / len(top_clips)
        avg_completion = sum(c['performance'].get('completion_rate', 0) for c in top_clips) / len(top_clips)
        print(f"   📊 Avg views: {avg_views:,.0f}")
        print(f"   📊 Avg completion: {avg_completion:.1%}")
        
        # Batch analysis
        print(f"\n🔍 Batch analysis (4 batches)...")
        batches = self._create_batches(top_clips, batch_sizes=[15, 15, 15, 5])
        
        batch_patterns = []
        for i, batch in enumerate(batches, 1):
            print(f"\n   Batch {i}/{len(batches)} ({len(batch)} clips)...")
            pattern = await self._analyze_batch(batch, i)
            batch_patterns.append(pattern)
            print(f"      ✅ Extracted patterns")
            await asyncio.sleep(0.5)
        
        # Synthesize
        print(f"\n🎯 Synthesizing isolated patterns...")
        isolated_patterns = await self._synthesize_patterns(batch_patterns, top_clips)
        
        # Save
        output_file = self.output_dir / "ISOLATED_PATTERNS.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(isolated_patterns, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ CODE 1 COMPLETE")
        print(f"{'='*70}")
        print(f"   Output: {output_file}")
        print(f"   Clips analyzed: {len(top_clips)}")
        print(f"   Ready for Code 3!")
        
        return isolated_patterns
    
    def _load_clips(self):
        """Load high-performing clips"""
        # Try multiple possible locations
        possible_paths = [
            Path("goat_training_data.json"),
            Path("data/training/goat_training_data.json"),
            self.training_dir / "goat_training_data.json"
        ]
        
        for goat_file in possible_paths:
            if goat_file.exists():
                try:
                    with open(goat_file, 'r', encoding='utf-8') as f:
                        clips = json.load(f)
                    
                    # Filter high performers
                    high_performers = []
                    for c in clips:
                        perf = c.get('performance', {})
                        views = perf.get('views', 0) or 0
                        completion = perf.get('completion_rate', 0) or 0
                        
                        if views > 1_000_000 or completion > 0.20:
                            high_performers.append(c)
                    
                    return high_performers
                except Exception as e:
                    print(f"   ⚠️  Error loading {goat_file}: {e}")
                    continue
        
        print(f"   ⚠️  goat_training_data.json not found in any location")
        return []
    
    def _smart_sample(self, clips, n=50):
        """Smart sampling by performance score"""
        
        # Score = views × completion_rate (true performance!)
        scored = []
        for clip in clips:
            views = clip['performance']['views']
            completion = clip['performance'].get('completion_rate', 0)
            score = views * completion
            scored.append((score, clip))
        
        # Sort by score, take top N
        scored.sort(reverse=True, key=lambda x: x[0])
        return [clip for score, clip in scored[:n]]
    
    def _create_batches(self, clips, batch_sizes=[15, 15, 15, 5]):
        """Divide clips into batches"""
        batches = []
        idx = 0
        for size in batch_sizes:
            if idx < len(clips):
                batches.append(clips[idx:idx+size])
                idx += size
        return batches
    
    async def _analyze_batch(self, batch, batch_num):
        """Analyze single batch"""
        
        # Build compact stats
        batch_stats = []
        for clip in batch:
            perf = clip['performance']
            
            # Duration
            duration = 0
            if 'transcript' in clip and 'segments' in clip['transcript']:
                segs = clip['transcript']['segments']
                if segs:
                    duration = segs[-1]['end'] - segs[0]['start']
            
            # Text preview
            text_preview = ""
            if 'transcript' in clip:
                if isinstance(clip['transcript'], dict) and 'text' in clip['transcript']:
                    text_preview = clip['transcript']['text'][:150]
                elif isinstance(clip['transcript'], str):
                    text_preview = clip['transcript'][:150]
            
            batch_stats.append({
                'views': perf['views'],
                'completion': perf.get('completion_rate', 0),
                'duration': duration,
                'preview': text_preview
            })
        
        # Build prompt
        avg_views = sum(c['views'] for c in batch_stats) / len(batch_stats) if batch_stats else 0
        avg_completion = sum(c['completion'] for c in batch_stats) / len(batch_stats) if batch_stats else 0
        
        samples_text = '\n'.join([
            f"• {c['views']:,.0f} views, {c['completion']:.1%} completion, {c['duration']:.0f}s"
            + (f"\n  '{c['preview']}...'" if c['preview'] else "")
            for c in batch_stats[:5]
        ])
        
        prompt = f"""Analyze this batch of {len(batch)} viral clips and extract PRINCIPLES.

BATCH METRICS:
- Avg views: {avg_views:,.0f}
- Avg completion: {avg_completion:.1%}

TOP CLIPS:
{samples_text}

YOUR TASK:
Extract PRINCIPLES (not rigid rules!) that explain viral performance.

Focus on:
1. Hook Patterns - What makes openings stop the scroll?
2. Duration Insights - How does length relate to completion?
3. Content Patterns - What topics/styles resonate?
4. Engagement Mechanics - What keeps people watching?

CRITICAL: Extract PRINCIPLES, not templates!
❌ NOT: "Hook must be in first 3s" (rigid)
✅ BUT: "Strong hooks create immediate curiosity" (principle)

RESPONSE (JSON):
{{
  "batch_num": {batch_num},
  "principles": {{
    "hooks": {{
      "principle": "Core insight about hooks",
      "observed_patterns": ["Pattern 1", "Pattern 2"],
      "variations": ["Context 1", "Context 2"]
    }},
    "duration": {{
      "principle": "Core insight about duration",
      "observations": ["Insight 1", "Insight 2"]
    }},
    "content": {{
      "principle": "Core insight about content",
      "patterns": ["Pattern 1", "Pattern 2"]
    }},
    "engagement": {{
      "principle": "Core insight about engagement",
      "mechanics": ["Mechanic 1", "Mechanic 2"]
    }}
  }}
}}

Extract principles that are FLEXIBLE and CONTEXT-AWARE!"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response
            if isinstance(message.content, list):
                response_text = message.content[0].text
            elif hasattr(message.content, 'text'):
                response_text = message.content.text
            else:
                response_text = str(message.content)
            
            # Clean JSON
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            print(f"         ⚠️  Batch analysis failed: {e}")
            return {"batch_num": batch_num, "principles": {}}
    
    async def _synthesize_patterns(self, batch_patterns, top_clips):
        """Synthesize batch patterns into unified principles"""
        
        # Aggregate all principles
        all_hook_principles = []
        all_duration_principles = []
        all_content_principles = []
        all_engagement_principles = []
        
        for batch in batch_patterns:
            p = batch.get('principles', {})
            if 'hooks' in p:
                all_hook_principles.append(p['hooks'])
            if 'duration' in p:
                all_duration_principles.append(p['duration'])
            if 'content' in p:
                all_content_principles.append(p['content'])
            if 'engagement' in p:
                all_engagement_principles.append(p['engagement'])
        
        # Calculate overall stats
        total_views = sum(c['performance']['views'] for c in top_clips)
        avg_completion = sum(c['performance'].get('completion_rate', 0) for c in top_clips) / len(top_clips) if top_clips else 0
        
        # Build prompt with truncated data
        hook_data = json.dumps(all_hook_principles, indent=2, ensure_ascii=False)[:1500]
        duration_data = json.dumps(all_duration_principles, indent=2, ensure_ascii=False)[:1500]
        content_data = json.dumps(all_content_principles, indent=2, ensure_ascii=False)[:1500]
        engagement_data = json.dumps(all_engagement_principles, indent=2, ensure_ascii=False)[:1500]
        
        prompt = f"""Synthesize unified principles from {len(batch_patterns)} batch analyses.

DATA ANALYZED:
- {len(top_clips)} top-performing clips
- {total_views:,.0f} total views
- {avg_completion:.1%} avg completion rate

HOOK PRINCIPLES:
{hook_data}

DURATION PRINCIPLES:
{duration_data}

CONTENT PRINCIPLES:
{content_data}

ENGAGEMENT PRINCIPLES:
{engagement_data}

YOUR TASK:
Synthesize into unified PERFORMANCE PRINCIPLES.

RESPONSE (JSON):
{{
  "data_source": {{
    "clips_analyzed": {len(top_clips)},
    "total_views": {total_views},
    "avg_completion": {avg_completion}
  }},
  
  "hook_patterns": {{
    "principle": "Unified principle",
    "observed_types": [...],
    "context_variations": {{...}}
  }},
  
  "duration_insights": {{
    "principle": "Unified principle",
    "performance_ranges": {{...}},
    "observations": [...]
  }},
  
  "content_patterns": {{
    "principle": "Unified principle",
    "successful_types": [...]
  }},
  
  "engagement_mechanics": {{
    "principle": "Unified principle",
    "retention_strategies": [...]
  }}
}}

Create ACTIONABLE principles for viral composition!"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response
            if isinstance(message.content, list):
                response_text = message.content[0].text
            elif hasattr(message.content, 'text'):
                response_text = message.content.text
            else:
                response_text = str(message.content)
            
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            principles = json.loads(response_text)
            principles['analyzed_at'] = datetime.now().isoformat()
            
            return principles
            
        except Exception as e:
            print(f"   ⚠️  Synthesis failed: {e}")
            return {
                "data_source": {"clips_analyzed": len(top_clips)},
                "error": str(e),
                "analyzed_at": datetime.now().isoformat()
            }


async def main():
    analyzer = IsolatedClipsAnalyzer()
    await analyzer.analyze()

if __name__ == '__main__':
    asyncio.run(main())

