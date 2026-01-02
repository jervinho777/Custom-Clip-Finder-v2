#!/usr/bin/env python3
"""
FAST WITH CACHE - 2-stage pipeline with caching

First run: ~12 min, $4
Re-runs: ~3 min, $1 (cached!)
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
import sys
import hashlib

sys.path.insert(0, str(Path(__file__).parent))

from test_2stage_fast import FastPipelineTest


def calculate_viral_potential(moment: Dict) -> int:
    """
    Calculate viral potential score based on 8 core principles
    
    Analyzes moment's viral_reasoning, hook_type, pattern, and other metadata
    to score how well it follows viral content principles.
    
    Args:
        moment: Moment dictionary with 'viral_reasoning', 'hook_type', 'pattern', etc.
    
    Returns:
        Integer score (can be negative!) - higher = more viral potential
    
    Principles scored:
    1. Complete Narrative Arc (+15 / -10)
    2. Hook Strength (+12 / -8)
    3. Pattern Interrupts (+10 / -6)
    4. Emotional Engagement (+10 / -5)
    5. Information Gap Management (+8 / -5)
    6. Content Density (+8 / -10)
    7. Universal Relevance (+6 / -4)
    8. Context Independence (+5 / -8)
    """
    score = 0
    
    # Get reasoning text (case-insensitive search)
    reasoning = str(moment.get('viral_reasoning', moment.get('ai_reasoning', ''))).lower()
    hook_type = str(moment.get('hook_type', '')).lower()
    pattern = str(moment.get('pattern', '')).lower()
    
    # Combine all text for analysis
    all_text = f"{reasoning} {hook_type} {pattern}".lower()
    
    # PRINCIPLE 1: Complete Narrative Arc
    arc_positive = any(phrase in all_text for phrase in [
        'complete', 'full arc', 'payoff', 'resolution', 'closes loop',
        'satisfying conclusion', 'complete story', 'full narrative'
    ])
    arc_negative = any(phrase in all_text for phrase in [
        'incomplete', 'cut off', 'missing payoff', 'no resolution',
        'unfinished', 'abrupt', 'no closure'
    ])
    if arc_positive:
        score += 15
    elif arc_negative:
        score -= 10
    
    # PRINCIPLE 2: Hook Strength
    strong_hook_types = ['paradox', 'bold claim', 'question', 'authority', 'story', 'contrast']
    hook_positive = any(ht in hook_type for ht in strong_hook_types) or any(phrase in all_text for phrase in [
        'strong hook', 'powerful opening', 'compelling start', 'grab attention'
    ])
    hook_negative = any(phrase in all_text for phrase in [
        'weak hook', 'slow start', 'boring opening', 'no hook'
    ])
    if hook_positive:
        score += 12
    elif hook_negative:
        score -= 8
    
    # PRINCIPLE 3: Pattern Interrupts
    interrupt_positive = any(phrase in all_text for phrase in [
        'pattern interrupt', 'twist', 'surprise', 'escalation', 'reveal',
        'unexpected', 'plot twist', 'turns', 'shift'
    ])
    interrupt_negative = any(phrase in all_text for phrase in [
        'no pattern interrupt', 'monotone', 'predictable', 'linear', 'no surprises'
    ])
    if interrupt_positive:
        score += 10
    elif interrupt_negative:
        score -= 6
    
    # PRINCIPLE 4: Emotional Engagement
    emotional_positive = any(phrase in all_text for phrase in [
        'emotional', 'tension', 'curiosity', 'shock', 'relatability',
        'universal pain', 'resonates', 'feels', 'impact', 'engaging'
    ])
    emotional_negative = any(phrase in all_text for phrase in [
        'emotionally flat', 'no emotion', 'detached', 'cold'
    ])
    if emotional_positive:
        score += 10
    elif emotional_negative:
        score -= 5
    
    # PRINCIPLE 5: Information Gap Management
    gap_positive = any(phrase in all_text for phrase in [
        'information gap', 'curiosity gap', 'gap closes', 'payoff delivers',
        'builds curiosity', 'resolves question', 'answers'
    ])
    gap_negative = any(phrase in all_text for phrase in [
        'gap closes too early', 'no gap', 'immediate answer', 'no curiosity'
    ])
    if gap_positive:
        score += 8
    elif gap_negative:
        score -= 5
    
    # PRINCIPLE 6: Content Density
    density_positive = any(phrase in all_text for phrase in [
        'tight', 'dense', 'efficient', 'no waste', 'concise', 'packed',
        'every word counts', 'lean'
    ])
    density_negative = any(phrase in all_text for phrase in [
        'filler', 'rambling', 'repetitive', 'slow', 'drags', 'padded',
        'unnecessary', 'verbose', 'bloated'
    ])
    if density_positive:
        score += 8
    elif density_negative:
        score -= 10
    
    # PRINCIPLE 7: Universal Relevance
    universal_positive = any(phrase in all_text for phrase in [
        'universal', 'relatable', 'common', 'shared experience', 'pain point',
        'everyone', 'many people', 'broad appeal', 'general'
    ])
    universal_negative = any(phrase in all_text for phrase in [
        'niche', 'specific audience', 'limited appeal', 'narrow'
    ])
    if universal_positive:
        score += 6
    elif universal_negative:
        score -= 4
    
    # PRINCIPLE 8: Context Independence
    standalone_positive = any(phrase in all_text for phrase in [
        'standalone', 'self-contained', 'works alone', 'no context needed',
        'independent', 'complete on its own'
    ])
    standalone_negative = any(phrase in all_text for phrase in [
        'needs context', 'unclear without', 'requires background', 'depends on',
        'confusing without'
    ])
    if standalone_positive:
        score += 5
    elif standalone_negative:
        score -= 8
    
    return score


def deduplicate_moments(moments: List[Dict], overlap_threshold: float = 0.8) -> List[Dict]:
    """
    Remove duplicate moments using principle-based scoring (INTELLIGENT DEDUP)
    
    Args:
        moments: List of moment dictionaries with 'start', 'end', 'viral_reasoning', etc.
        overlap_threshold: Maximum overlap ratio (0.0-1.0) to consider duplicates (default: 0.8 = 80%)
    
    Returns:
        Deduplicated list of moments (keeps higher-scoring moments based on viral principles)
    
    Algorithm:
    - Calculate overlap ratio between all moment pairs
    - If overlap > threshold, calculate viral_potential score for both
    - Keep the moment with HIGHER score (not longer/shorter)
    - Replaces simple "first occurrence" with intelligent quality-based selection
    - Preserves all moment metadata and structure
    """
    if not moments or len(moments) <= 1:
        return moments
    
    # Sort moments by start time for consistent processing
    sorted_moments = sorted(moments, key=lambda m: m.get('start', 0))
    
    deduplicated = []
    removed_count = 0
    replaced_count = 0
    replaced_count = 0
    
    for i, current_moment in enumerate(sorted_moments):
        current_start = current_moment.get('start', 0)
        current_end = current_moment.get('end', 0)
        current_duration = current_end - current_start
        
        if current_duration <= 0:
            # Skip invalid moments
            continue
        
        is_duplicate = False
        replaced_existing = False
        
        # Check overlap with all already-kept moments
        for j, kept_moment in enumerate(deduplicated):
            kept_start = kept_moment.get('start', 0)
            kept_end = kept_moment.get('end', 0)
            kept_duration = kept_end - kept_start
            
            if kept_duration <= 0:
                continue
            
            # Calculate overlap
            overlap_start = max(current_start, kept_start)
            overlap_end = min(current_end, kept_end)
            overlap_duration = max(0, overlap_end - overlap_start)
            
            # Calculate overlap ratio (overlap / min(duration1, duration2))
            min_duration = min(current_duration, kept_duration)
            overlap_ratio = overlap_duration / min_duration if min_duration > 0 else 0
            
            # If overlap exceeds threshold, use principle-based scoring to decide
            if overlap_ratio >= overlap_threshold:
                # Calculate viral potential for both moments
                kept_score = calculate_viral_potential(kept_moment)
                current_score = calculate_viral_potential(current_moment)
                
                # Get hook phrases for debug output
                kept_hook = str(kept_moment.get('hook_phrase', ''))[:40] or 'No hook'
                current_hook = str(current_moment.get('hook_phrase', ''))[:40] or 'No hook'
                
                # Keep the one with HIGHER score (not longer/shorter)
                if current_score > kept_score:
                    # Replace kept moment with current (better score)
                    deduplicated[j] = current_moment
                    replaced_existing = True
                    replaced_count += 1
                    print(f"      🔄 Overlap: Moment A ({kept_duration:.0f}s, score {kept_score}) \"{kept_hook}...\"")
                    print(f"                vs B ({current_duration:.0f}s, score {current_score}) \"{current_hook}...\"")
                    print(f"                → Keep B (better score: +{current_score - kept_score})")
                    break
                else:
                    # Keep existing, skip current
                    is_duplicate = True
                    removed_count += 1
                    print(f"      🔄 Overlap: Moment A ({kept_duration:.0f}s, score {kept_score}) \"{kept_hook}...\"")
                    print(f"                vs B ({current_duration:.0f}s, score {current_score}) \"{current_hook}...\"")
                    print(f"                → Keep A (better score: +{kept_score - current_score})")
                    break
        
        # Keep moment if not duplicate and didn't replace existing
        if not is_duplicate and not replaced_existing:
            deduplicated.append(current_moment)
    
    if replaced_count > 0:
        print(f"\n   📊 Deduplication: {removed_count} removed, {replaced_count} replaced (better scores)")
    
    return deduplicated


class CachedFastPipeline(FastPipelineTest):
    """2-stage pipeline with comprehensive caching"""
    
    def __init__(self):
        super().__init__()
        self.cache_dir = Path("data/cache/pipeline")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load caches
        self.story_cache = self._load_cache("story_cache.json")
        self.moments_cache = self._load_cache("moments_cache.json")
        self.prescores_cache = self._load_cache("prescores_cache.json")
        self.godmode_cache = self._load_cache("godmode_cache.json")
    
    def _load_cache(self, filename: str) -> Dict:
        """Load cache file"""
        cache_file = self.cache_dir / filename
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return {}
    
    def _save_cache(self, filename: str, data: Dict):
        """Save cache file"""
        cache_file = self.cache_dir / filename
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_video_hash(self, video_path: str) -> str:
        """Get hash for video"""
        return hashlib.md5(str(video_path).encode()).hexdigest()[:8]
    
    def _get_moment_hash(self, moment: Dict) -> str:
        """Get hash for moment based on content"""
        start = moment.get('start', 0)
        end = moment.get('end', 0)
        segments = moment.get('segments', [])
        text = ''.join([s.get('text', '')[:100] for s in segments[:3]])
        content = f"{start:.1f}_{end:.1f}_{text}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    async def run_cached_pipeline(self, video_path: str, top_n: int = 5):
        """Run pipeline with caching"""
        
        print(f"\n{'='*70}")
        print(f"⚡ 2-STAGE CACHED PIPELINE")
        print(f"{'='*70}")
        
        video_hash = self._get_video_hash(video_path)
        
        story_cached = f"{video_hash}_story" in self.story_cache
        moments_cached = video_hash in self.moments_cache
        
        print(f"\n   Video: {Path(video_path).name}")
        print(f"   💾 Cache Status:")
        print(f"      Story: {'HIT ✅' if story_cached else 'MISS 🆕'}")
        print(f"      Moments: {'HIT ✅' if moments_cached else 'MISS 🆕'}")
        
        video_file = Path(video_path)
        transcript_file = Path(f"data/cache/transcripts/{video_file.stem}_transcript.json")
        
        with open(transcript_file) as f:
            data = json.load(f)
            segments = data['segments']
        
        print(f"   ✅ Loaded {len(segments)} segments")
        
        # STAGE 0: Story (cached)
        print(f"\n{'='*70}")
        print(f"STAGE 0: STORY ANALYSIS")
        print(f"{'='*70}")
        
        story_key = f"{video_hash}_story"
        
        if story_cached:
            print(f"   ✅ Using cached story")
            story = self.story_cache[story_key]
        else:
            print(f"   🆕 Analyzing story...")
            story = await self.v4._analyze_story_ensemble(segments)
            self.story_cache[story_key] = story
            self._save_cache("story_cache.json", self.story_cache)
        
        # STAGE 1: Moments (cached)
        print(f"\n{'='*70}")
        print(f"STAGE 1: FIND MOMENTS")
        print(f"{'='*70}")
        
        if moments_cached:
            print(f"   ✅ Using cached moments")
            moments = self.moments_cache[video_hash]
        else:
            print(f"   🆕 Finding moments...")
            moments = await self.v4._find_moments_with_consensus(segments, story)
            self.moments_cache[video_hash] = moments
            self._save_cache("moments_cache.json", self.moments_cache)
        
        print(f"\n   Found: {len(moments)} moments")
        
        # DEDUPLICATION: Remove overlapping moments
        print(f"\n{'='*70}")
        print(f"STAGE 1.25: DEDUPLICATION")
        print(f"{'='*70}")
        
        moments_before = len(moments)
        moments = deduplicate_moments(moments, overlap_threshold=0.8)
        moments_after = len(moments)
        removed = moments_before - moments_after
        
        print(f"\n   📊 Before: {moments_before} moments")
        print(f"   ✂️  After: {moments_after} unique moments")
        if removed > 0:
            print(f"   🗑️  Removed: {removed} duplicate moments (>80% overlap)")
        else:
            print(f"   ✅ No duplicates found (all moments unique)")
        
        # STAGE 1.5: RESTRUCTURE ALL MOMENTS (NEW!)
        print(f"\n{'='*70}")
        print(f"STAGE 1.5: RESTRUCTURE MOMENTS")
        print(f"{'='*70}")
        
        print(f"\n   🔧 Restructuring {len(moments)} moments with learnings...")
        
        restructured_moments = []
        restructure_cached = 0
        restructure_new = 0
        
        for i, moment in enumerate(moments, 1):
            # Create hash for caching
            moment_hash = self._get_moment_hash(moment)
            restructure_key = f"restructure_{moment_hash}"
            
            # Check cache
            if restructure_key in self.moments_cache:
                restructured = self.moments_cache[restructure_key]
                restructure_cached += 1
                status = "💾"
            else:
                # Restructure with AI + learnings
                restructured = await self.v4._restructure_with_review(
                    moment=moment,
                    segments=segments,
                    story_structure=story
                )
                
                # If restructure fails, keep original
                if restructured is None:
                    restructured = moment
                
                # Cache the result
                self.moments_cache[restructure_key] = restructured
                self._save_cache("moments_cache.json", self.moments_cache)
                restructure_new += 1
                status = "🆕"
            
            restructured_moments.append(restructured)
            print(f"   {status} {i}/{len(moments)}: Restructured", end='\r')
        
        moments = restructured_moments
        
        print(f"\n   ✅ Restructured {len(moments)} moments")
        print(f"   💾 Cache: {restructure_cached} cached, {restructure_new} new")
        
        # STAGE 2: Pre-screen (cached)
        print(f"\n{'='*70}")
        print(f"STAGE 2: PRE-SCREENING")
        print(f"{'='*70}")
        
        scored_moments = []
        cached_count = 0
        new_count = 0
        
        for i, moment in enumerate(moments, 1):
            moment_hash = self._get_moment_hash(moment)
            
            if moment_hash in self.prescores_cache:
                score_result = self.prescores_cache[moment_hash]
                cached_count += 1
                status = "💾"
            else:
                score_result = await self.quick_pre_score_opus(moment, segments)
                self.prescores_cache[moment_hash] = score_result
                self._save_cache("prescores_cache.json", self.prescores_cache)
                new_count += 1
                status = "🆕"
            
            scored_moments.append({
                **moment,
                'pre_score': score_result['score'],
                'pre_reason': score_result['reason']
            })
            
            print(f"   {status} {i}/{len(moments)}: {score_result['score']}/100", end='\r')
        
        print(f"\n   Pre-scored: {len(scored_moments)} ({cached_count} cached, {new_count} new)")
        
        scored_moments.sort(key=lambda m: m['pre_score'], reverse=True)
        top_moments = [m for m in scored_moments if m['pre_score'] >= 70][:top_n]
        
        if not top_moments:
            top_moments = scored_moments[:top_n]
        
        print(f"   Selected: {len(top_moments)} candidates")
        
        # STAGE 3: Godmode (cached)
        print(f"\n{'='*70}")
        print(f"STAGE 3: GODMODE")
        print(f"{'='*70}")
        
        results = []
        cached_eval = 0
        new_eval = 0
        
        for i, moment in enumerate(top_moments, 1):
            moment_hash = self._get_moment_hash(moment)
            
            if moment_hash in self.godmode_cache:
                result = self.godmode_cache[moment_hash]
                cached_eval += 1
                status = "💾"
            else:
                print(f"\n   🆕 {i}/{len(top_moments)}: Evaluating...")
                
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
                
                story_eval = {'storylines': [], 'standalone_moments': []}
                result = await self.v4._evaluate_quality_debate(clip, story_eval)
                
                self.godmode_cache[moment_hash] = result
                self._save_cache("godmode_cache.json", self.godmode_cache)
                new_eval += 1
                status = "🆕"
            
            results.append({
                'clip': moment,
                'score': result.get('total_score', result.get('score', 0)),
                'tier': result.get('quality_tier', 'F'),
                'pre_score': moment['pre_score']
            })
            
            print(f"   {status} {i}/{len(top_moments)}: {moment['pre_score']}/100 → {result.get('total_score', result.get('score', 0))}/50")
        
        # Summary
        passing = [r for r in results if r['score'] >= 40]
        
        print(f"\n{'='*70}")
        print(f"📊 RESULTS")
        print(f"{'='*70}")
        
        print(f"\n   ✅ Passed (40+): {len(passing)}")
        
        if passing:
            for i, r in enumerate(passing, 1):
                print(f"      {i}. {r['pre_score']}/100 → {r['score']}/50 ({r['tier']})")
        
        # Cache stats
        total = 2 + len(moments) + len(top_moments)
        cached = (1 if story_cached else 0) + (1 if moments_cached else 0) + cached_count + cached_eval
        rate = cached / total * 100 if total > 0 else 0
        
        print(f"\n   💾 Cache: {rate:.0f}%")
        
        if rate > 80:
            print(f"   ⚡ Next run: ~3 min, $1")
        elif rate > 50:
            print(f"   ✅ Next run: ~6 min, $2")
        else:
            print(f"   🆕 First run: ~12 min, $4")
            print(f"   🔄 Next run will be faster!")
        
        return results


async def main():
    video = sys.argv[1] if len(sys.argv) > 1 else "data/uploads/Dieter Lange.mp4"
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    tester = CachedFastPipeline()
    await tester.run_cached_pipeline(video, top_n)


if __name__ == '__main__':
    asyncio.run(main())

