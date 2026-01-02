#!/usr/bin/env python3
"""
🎬 CREATE CLIPS V4 - Integrated 5-AI Ensemble Pipeline
Complete System: Story-First + Multi-AI Consensus

Pipeline:
STEP 0: Story Analysis (Ensemble Consensus)
STEP 1: Find Moments (5-AI Parallel Vote)
STEP 2: Restructure (Hybrid: Lead + Review)
STEP 2.5: Quality Eval (5-AI Debate)
STEP 3: Variations (Fast Models)
EXPORT: MP4 + XML + JSON
"""

import os
import sys
import json
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import base systems
try:
    from create_clips_v2 import CreateClipsV2
except ImportError:
    print("⚠️  Warning: create_clips_v2.py not found")
    CreateClipsV2 = None

try:
    from create_clips_v3_ensemble import PremiumAIEnsemble, ConsensusEngine
except ImportError:
    print("⚠️  Warning: create_clips_v3_ensemble.py not found")
    PremiumAIEnsemble = None
    ConsensusEngine = None

try:
    from master_learnings_v2 import get_learnings_for_prompt
except ImportError:
    print("⚠️  Warning: master_learnings_v2.py not found")
    get_learnings_for_prompt = None


class OpenLoopBridging:
    """
    Detects open loops (questions) and bridges small gaps to find payoffs
    
    Example: "Was ist hier passiert?" → gap → "Die Freude am Tun ist ersetzt..."
    """
    
    # Patterns that indicate open loops (questions without answers)
    OPEN_LOOP_PATTERNS = [
        'was ist hier passiert',
        'was passiert hier',
        'was bedeutet das',
        'warum',
        'wie kann das sein',
        'die frage ist',
        'stellt sich die frage',
        'was ist da los',
        'was heißt das',
        'wie ist das möglich',
        '?',  # Ends with question mark
    ]
    
    # Patterns that indicate answers/payoffs
    ANSWER_PATTERNS = [
        'weil',
        'der grund',
        'die antwort',
        'das liegt daran',
        'das bedeutet',
        'passiert ist',
        'ist ersetzt worden',
        'wurde ersetzt',
        'das ist',
        'das war',
        'es war',
        'es ist',
    ]
    
    def __init__(self, segments):
        """
        Args:
            segments: Full video segments (for looking ahead)
        """
        self.segments = segments
    
    def detect_and_bridge(self, moment):
        """
        Check if moment ends with open loop and try to find answer
        
        Args:
            moment: Refined moment from Stage 1
            
        Returns:
            moment (possibly extended with payoff segments)
        """
        moment_segs = moment.get('segments', [])
        
        if not moment_segs:
            return moment
        
        # Check last segment for open loop
        last_seg = moment_segs[-1]
        last_text = last_seg.get('text', '').lower()
        
        has_open_loop = any(pattern in last_text for pattern in self.OPEN_LOOP_PATTERNS)
        
        if not has_open_loop:
            return moment  # No open loop, return as is
        
        # Open loop detected!
        moment_end = moment.get('end', 0)
        
        print(f"      🔍 Open loop detected: '{last_text[-60:]}'")
        
        # Look for answer in next segments (within 5s gap)
        payoff_segs = self._find_payoff_segments(moment_end, max_gap=5.0, max_segs=3)
        
        if payoff_segs:
            # Found payoff! Extend moment
            print(f"      ✅ Found payoff: bridging gap to {payoff_segs[-1]['end']:.1f}s")
            
            moment['segments'].extend(payoff_segs)
            moment['end'] = payoff_segs[-1]['end']
            moment['duration'] = moment['end'] - moment.get('start', 0)
            moment['bridged_gap'] = True
            moment['gap_type'] = 'open_loop_answer'
            
            return moment
        else:
            print(f"      ⚠️ No payoff found within 5s")
            return moment
    
    def _find_payoff_segments(self, moment_end, max_gap=5.0, max_segs=3):
        """
        Look for payoff segments after moment end
        
        Args:
            moment_end: Where moment currently ends
            max_gap: Maximum gap to bridge (seconds)
            max_segs: Maximum segments to check
            
        Returns:
            List of segments that form the payoff (or empty if not found)
        """
        payoff_segments = []
        
        # Find segments after moment_end
        for seg in self.segments:
            # Skip if before moment end
            if seg.get('start', 0) < moment_end:
                continue
            
            # Check gap
            gap = seg.get('start', 0) - moment_end
            if gap > max_gap:
                break  # Gap too large, stop looking
            
            # Add this segment
            payoff_segments.append(seg)
            
            # Check if this segment contains answer
            seg_text = seg.get('text', '').lower()
            if any(pattern in seg_text for pattern in self.ANSWER_PATTERNS):
                # Found answer! Return all segments up to here
                return payoff_segments
            
            # Check if we've looked at enough segments
            if len(payoff_segments) >= max_segs:
                break
        
        # No answer found
        return []


class CreateClipsV4Integrated:
    """
    V4: Integrated 5-AI Ensemble System
    
    Combines:
    - Story-First approach (V2)
    - Multi-AI Consensus (V3)
    - Quality-First philosophy
    """
    
    # Quality thresholds (moderate lowering)
    QUALITY_PASS_THRESHOLD = 18  # Minimum score to pass (was 20)
    
    def __init__(self):
        print("\n" + "="*70)
        print("🎬 CREATE CLIPS V4 - INTEGRATED 5-AI ENSEMBLE")
        print("="*70)
        
        # Initialize base system (for video processing, export, etc.)
        if CreateClipsV2:
            self.base_system = CreateClipsV2()
            print("   ✅ Base System: Ready")
        else:
            self.base_system = None
            print("   ⚠️  Base System: Not available")
        
        # Initialize AI ensemble
        if PremiumAIEnsemble and ConsensusEngine:
            self.ensemble = PremiumAIEnsemble()
            self.consensus = ConsensusEngine(self.ensemble)
            print("   ✅ AI Ensemble: Ready")
            print("   ✅ Consensus Engine: Ready")
        else:
            self.ensemble = None
            self.consensus = None
            print("   ⚠️  AI Ensemble: Not available")
        
        # Set up directories
        self.data_dir = Path("data")
        self.transcript_dir = self.data_dir / "cache" / "transcripts"
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # Load latest VIRAL_PRINCIPLES (Master Brain - self-learning!)
        self.VIRAL_PRINCIPLES = self._load_viral_principles()
        brain_version = self.VIRAL_PRINCIPLES.get('version', 'unknown')
        brain_updated = self.VIRAL_PRINCIPLES.get('updated_at', 'unknown')
        print(f"   🧠 Loaded Brain: v{brain_version}")
        if brain_updated != 'unknown':
            print(f"   📅 Updated: {brain_updated}")
        
        # Also load legacy principles for backward compatibility
        try:
            from learnings_extractor import LearningsExtractor
            extractor = LearningsExtractor()
            self.PRINCIPLES = extractor.get_all_principles()
        except Exception as e:
            self.PRINCIPLES = {}
        
        print("="*70 + "\n")
    
    def _load_viral_principles(self) -> Dict:
        """Load latest master brain (VIRAL_PRINCIPLES.json)"""
        
        principles_file = Path("data/learnings/VIRAL_PRINCIPLES.json")
        
        if not principles_file.exists():
            print(f"   ⚠️  VIRAL_PRINCIPLES.json not found - using defaults")
            print(f"   💡 Run: python viral_pattern_analyzer.py to train brain")
            return self._get_default_principles()
        
        try:
            with open(principles_file, 'r', encoding='utf-8') as f:
                principles = json.load(f)
            return principles
        except Exception as e:
            print(f"   ⚠️  Failed to load VIRAL_PRINCIPLES.json: {e}")
            return self._get_default_principles()
    
    def _get_default_principles(self) -> Dict:
        """Fallback principles if brain not yet trained"""
        return {
            'version': '1.0-default',
            'updated_at': 'never',
            'note': 'Run viral_pattern_analyzer.py to train brain',
            'core_algorithm': {
                'principle': 'Maximize watchtime through engagement',
                'metrics': ['completion_rate', 'watch_time', 'engagement']
            },
            'hook_principles': {
                'core': 'Stop scroll within 3 seconds',
                'methods': ['curiosity_gap', 'bold_statement', 'question', 'pattern_interrupt']
            },
            'duration_principles': {
                'core': 'Balance completeness with engagement',
                'observations': ['Varies by content type', 'Completeness matters']
            },
            'cutting_principles': {
                'core': 'Every word must earn its place',
                'what_to_cut': ['Unnecessary descriptors', 'Filler words'],
                'what_to_preserve': ['Core narrative', 'Emotional beats']
            },
            'timing_principles': {
                'core': 'Strategic silence creates impact',
                'when_to_pause': ['After questions', 'Before payoff'],
                'when_not_to_pause': ['High-energy sequences']
            },
            'structure_principles': {
                'core': 'Structure adapts to content type',
                'viable_patterns': {
                    'story': 'Setup → Escalation → Resolution',
                    'insight': 'Problem → Analysis → Solution'
                }
            }
        }
    
    def _get_quality_tier(self, score: int) -> str:
        """
        Convert score to quality tier
        
        Moderate thresholds (lowered by 2-3 points)
        """
        if score >= 38:  # Was 40 (A-tier slightly easier)
            return 'A'
        elif score >= 28:  # Was 30 (B-tier moderate)
            return 'B'
        elif score >= 18:  # Was 20 (C-tier moderate)
            return 'C'
        else:
            return 'D'
    
    def _extract_tier_letter(self, tier_string: str) -> str:
        """
        Extract base letter from tier string
        
        Examples:
        - 'A' → 'A'
        - 'A+' → 'A'
        - 'B-' → 'B'
        - 'C+' → 'C'
        """
        if not tier_string or not isinstance(tier_string, str):
            return 'D'
        
        # Get first character and uppercase
        tier_letter = tier_string.strip()[0].upper()
        
        # Validate it's A-D
        if tier_letter in ['A', 'B', 'C', 'D']:
            return tier_letter
        
        return 'D'  # Default to D if invalid
    
    async def extract_clips(self, segments: List[Dict], video_path: str) -> Dict:
        """
        Complete integrated pipeline with 5-AI ensemble
        
        Returns:
            {
                'story_structure': {...},
                'clips': [{...}],
                'consensus_data': {...},
                'stats': {...}
            }
        """
        
        print("\n" + "="*70)
        print("🎬 INTEGRATED PIPELINE - START")
        print("="*70)
        
        # STEP 0: Story Analysis with Ensemble
        print("\n📖 STEP 0: Story Analysis (Ensemble Consensus)")
        story_structure = await self._analyze_story_ensemble(segments)
        
        # STEP 1: Find Moments with 5-AI Consensus
        print("\n📊 STEP 1: Find Moments (5-AI Parallel Vote)")
        moments = await self._find_moments_ensemble(segments, story_structure)
        
        print(f"\n   ✅ Found {len(moments)} consensus moments")
        
        # STEP 1.5: Quick Quality Check - Skip restructure for high-scoring clips
        print("\n⭐ STEP 1.5: Quick Quality Check (Pre-Restructure)")
        high_quality_clips = []
        needs_restructure = []
        
        for i, moment in enumerate(moments[:10], 1):  # Limit to 10 for now
            print(f"\n   📊 Quick evaluation: Moment {i}/{min(len(moments), 10)}")
            
            # Extract segments for this moment
            moment_start = moment.get('start', 0)
            moment_end = moment.get('end', 0)
            moment_segments = [
                seg for seg in segments
                if moment_start <= seg.get('start', 0) < moment_end
            ]
            
            # Convert moment to clip format for evaluation
            moment_clip = {
                'start': moment_start,
                'end': moment_end,
                'segments': moment_segments,
                'clip_id': f"moment_{i}",
                'structure': {
                    'segments': moment_segments
                }
            }
            
            # Quick quality check
            quality = await self._evaluate_quality_debate(moment_clip, story_structure)
            score = quality.get('total_score', 0)
            
            if score >= 40:  # Already excellent - skip restructure!
                print(f"      ✅ Score: {score}/50 - Preserving original structure")
                moment_clip['quality'] = quality
                moment_clip['preserved_original'] = True
                high_quality_clips.append(moment_clip)
            else:
                print(f"      🔧 Score: {score}/50 - Needs restructure")
                needs_restructure.append((moment, quality))
        
        print(f"\n   ✅ High-quality (preserved): {len(high_quality_clips)}")
        print(f"   🔧 Needs restructure: {len(needs_restructure)}")
        
        # STEP 2: Restructure with Lead + Review (only for clips that need it)
        restructured = []
        
        if needs_restructure:
            print("\n🔄 STEP 2: Restructure (Hybrid: Lead + Review)")
            for i, (moment, pre_quality) in enumerate(needs_restructure, 1):
                print(f"\n   📌 Restructuring {i}/{len(needs_restructure)}")
                clip = await self._restructure_with_review(moment, segments, story_structure)
                if clip:
                    # Re-evaluate after restructure
                    quality = await self._evaluate_quality_debate(clip, story_structure)
                    clip['quality'] = quality
                    clip['preserved_original'] = False
                    restructured.append(clip)
            
            print(f"\n   ✅ Restructured {len(restructured)} clips")
        else:
            print("\n   ✅ All clips already high quality - skipping restructure!")
        
        # STEP 2.5: Combine high-quality preserved + restructured clips
        print("\n⭐ STEP 2.5: Final Quality Check")
        quality_passed = []
        
        # Add preserved high-quality clips
        quality_passed.extend(high_quality_clips)
        
        # Add restructured clips (already evaluated)
        quality_passed.extend(restructured)
        
        # Final filter by tier
        final_passed = []
        for clip in quality_passed:
            quality = clip.get('quality', {})
            tier_string = quality.get('quality_tier', 'D')
            tier_letter = self._extract_tier_letter(tier_string)
            
            if tier_letter in ['A', 'B', 'C']:
                final_passed.append(clip)
                preserved = "✅ PRESERVED" if clip.get('preserved_original') else "🔄 RESTRUCTURED"
                print(f"      {preserved} - {tier_string} ({tier_letter})")
            else:
                print(f"      ❌ {tier_string} ({tier_letter}) - Rejected")
        
        quality_passed = final_passed
        print(f"\n   ✅ {len(quality_passed)} clips passed quality gate")
        
        # STEP 3: Create Variations (Fast Models)
        print("\n🎨 STEP 3: Create Variations (Fast Models)")
        all_clips_with_versions = []
        
        for clip in quality_passed:
            # Determine variations based on quality tier
            tier_string = clip.get('quality', {}).get('quality_tier', 'C')
            tier_letter = self._extract_tier_letter(tier_string)
            max_variations = 3 if tier_letter == 'A' else 2 if tier_letter == 'B' else 1
            
            if self.base_system:
                variations = self.base_system._create_variations(
                    clip, 
                    segments
                )
            else:
                # Fallback: just use original
                variations = [{
                    'version_id': f"{clip.get('clip_id', 'clip')}_original",
                    'version_name': 'Original',
                    'variation_type': 'original',
                    'structure': clip.get('structure', {})
                }]
            
            all_clips_with_versions.append({
                'clip': clip,
                'versions': variations[:max_variations]
            })
        
        total_versions = sum(len(c['versions']) for c in all_clips_with_versions)
        print(f"\n   ✅ Created {total_versions} total versions")
        
        # Summary
        print("\n" + "="*70)
        print("📊 PIPELINE SUMMARY")
        print("="*70)
        print(f"   Story Analysis: Consensus-based")
        print(f"   Moments Found: {len(moments)}")
        print(f"   High-Quality Preserved: {len(high_quality_clips)}")
        print(f"   Clips Restructured: {len(restructured)}")
        print(f"   Quality Passed: {len(quality_passed)}")
        print(f"   Total Versions: {total_versions}")
        
        # Print costs
        if self.ensemble:
            self.ensemble.print_usage_stats()
        
        # Collect validation stats from quality evaluations
        validations = []
        for clip_data in all_clips_with_versions:
            clip = clip_data.get('clip', {})
            quality = clip.get('quality', {})
            validation = quality.get('validation', {})
            if validation:
                validations.append(validation)
        
        # Print validation statistics
        if validations:
            self._print_validation_stats(validations)
        
        return {
            'story_structure': story_structure,
            'moments': moments,
            'clips': all_clips_with_versions,
            'stats': {
                'moments_found': len(moments),
                'clips_restructured': len(restructured),
                'quality_passed': len(quality_passed),
                'total_versions': total_versions,
                'ai_consensus_used': True,
                'validation_stats': {
                    'total_validated': len(validations),
                    'avg_confidence': sum(v.get('confidence', 0) for v in validations) / len(validations) if validations else 0,
                    'learnings_applied_count': sum(1 for v in validations if v.get('learnings_applied'))
                }
            }
        }
    
    async def _analyze_story_ensemble(self, segments: List[Dict]) -> Dict:
        """
        Story analysis using ensemble consensus WITH LEARNINGS
        
        Uses parallel vote for fast story understanding
        Now includes learned patterns and algorithm context
        """
        
        if not self.base_system or not self.consensus:
            # Fallback
            if self.base_system:
                return self.base_system._analyze_story_structure(segments)
            return {'storylines': [], 'standalone_moments': []}
        
        # GET LEARNINGS (with graceful fallback)
        learnings_prompt = self._get_learnings_safely()
        learnings_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{learnings_prompt}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Format transcript
        transcript = self.base_system._format_segments(segments, max_chars=50000)
        duration = segments[-1]['end'] if segments else 0
        
        prompt = f"""{learnings_section}

# 📹 VIDEO TRANSCRIPT ({duration:.0f} seconds):

{transcript[:30000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📖 STORY ANALYSE BASIEREND AUF LEARNINGS:

Analysiere die Story-Struktur BASIEREND auf:
1. Den gelernten Viral Patterns (oben)
2. Dem Algorithmus-Kontext (Watchtime-Maximierung)
3. Den {self._get_clips_analyzed_count()}+ analysierten Beispielen

Identifiziere:

## 1. STORYLINES (verbundene Narrative)
- Welche Storylines aus den Learnings passen?
- Folgt es winning structures?
- Welche Hook-Types aus den Patterns sind erkennbar?
- Algorithmus-Impact: Watchtime-Potential pro Storyline?

## 2. STANDALONE MOMENTS (selbsterklärend)
- Welche Momente können als Clip funktionieren OHNE Context?
- Nutzen sie winning hook types?
- Algorithmus-Impact: Hohe Completion-Rate möglich?

## 3. DEPENDENCIES (was braucht Context?)
- Welche Segmente MÜSSEN zusammenbleiben?
- Was passiert wenn man sie trennt (Algorithmus-Impact)?
- Welche Patterns aus Learnings erfordern Context?

Antworte in JSON:
{{
  "storylines": [
    {{
      "storyline_id": "story_1",
      "topic": "...",
      "segments": [
        {{"start": X, "end": Y, "role": "...", "key_elements": [...]}}
      ],
      "can_standalone": true/false,
      "requires_context": true/false,
      "learned_patterns": ["Pattern 1", "Pattern 2"],
      "watchtime_potential": "high/medium/low",
      "algorithm_assessment": "Warum Algorithmus diese Storyline pushen würde"
    }}
  ],
  "standalone_moments": [
    {{
      "start": X,
      "end": Y,
      "topic": "...",
      "why_standalone": "...",
      "hook_type": "question/statement/story/number",
      "learned_patterns": ["Pattern 1"],
      "watchtime_potential": "high/medium/low"
    }}
  ],
  "analysis": {{
    "storylines_count": X,
    "standalone_count": Y,
    "learned_patterns_found": ["Pattern 1", "Pattern 2"],
    "algorithm_insights": "Warum diese Struktur Watchtime maximiert"
  }}
}}
"""
        
        system = f"Du bist ein Story-Analyst trainiert auf {self._get_clips_analyzed_count()} viralen Clips mit Algorithmus-Verständnis."
        
        # Use parallel vote for fast analysis
        result = await self.consensus.build_consensus(
            prompt=prompt,
            system=system,
            strategy='parallel_vote'
        )
        
        print(f"\n   Consensus Confidence: {result.get('confidence', 0):.0%}")
        
        # Parse consensus result
        try:
            consensus_text = result.get('consensus', '')
            # Try to extract JSON from consensus
            if '{' in consensus_text:
                json_start = consensus_text.find('{')
                json_end = consensus_text.rfind('}') + 1
                json_str = consensus_text[json_start:json_end]
                story_structure = json.loads(json_str)
                return story_structure
        except Exception as e:
            print(f"   ⚠️  Parse error: {e}")
        
        # Fallback to base system
        print("   ⚠️  Falling back to base system for story analysis")
        return self.base_system._analyze_story_structure(segments)
    
    async def _find_moments_ensemble(self, segments: List[Dict], 
                                     story_structure: Dict) -> List[Dict]:
        """
        Find moments using 5-AI consensus
        
        Each AI finds moments, then consensus builds final list
        """
        
        if not self.base_system:
            return []
        
        # Use chunked approach for long videos
        total_duration = segments[-1]['end'] if segments else 0
        
        if total_duration > 600:  # > 10 minutes
            print(f"   📦 Long video - using chunked processing")
            return await self._find_moments_chunked_ensemble(segments, story_structure)
        else:
            return await self._find_moments_single_ensemble(segments, story_structure)
    
    async def _find_moments_single_ensemble(self, segments: List[Dict],
                                           story_structure: Dict) -> List[Dict]:
        """
        Find moments in single pass with ensemble
        """
        
        if not self.base_system or not self.consensus:
            # Fallback
            if self.base_system:
                return self.base_system._find_moments_single_pass(segments)
            return []
        
        transcript = self.base_system._format_segments(segments, max_chars=20000)
        
        prompt = f"""Finde die besten Momente für Short-Form Clips.

TRANSCRIPT:
{transcript}

Finde 10-15 starke Momente.

Antworte in JSON:
{{
  "moments": [
    {{
      "id": 1,
      "start": X,
      "end": Y,
      "topic": "...",
      "strength": "high/medium",
      "reason": "..."
    }}
  ]
}}
"""
        
        system = "Du bist ein Experte für virale Short-Form Videos."
        
        # Use parallel vote
        result = await self.consensus.build_consensus(
            prompt=prompt,
            system=system,
            strategy='parallel_vote'
        )
        
        print(f"   Consensus Confidence: {result.get('confidence', 0):.0%}")
        
        # Parse moments
        try:
            consensus_text = result.get('consensus', '')
            # Try to extract JSON from consensus
            if '{' in consensus_text:
                json_start = consensus_text.find('{')
                json_end = consensus_text.rfind('}') + 1
                json_str = consensus_text[json_start:json_end]
                parsed = json.loads(json_str)
                moments = parsed.get('moments', [])
                
                # Add consensus metadata
                for moment in moments:
                    moment['found_by'] = 'ensemble_consensus'
                    moment['consensus_confidence'] = result.get('confidence', 0)
                
                return moments
        except Exception as e:
            print(f"   ⚠️  Parse error: {e}")
        
        # Fallback
        print("   ⚠️  Parse error, falling back to base system")
        return self.base_system._find_moments_single_pass(segments)
    
    async def _find_moments_chunked_ensemble(self, segments: List[Dict],
                                            story_structure: Dict) -> List[Dict]:
        """
        Find moments in chunks using ensemble
        """
        
        if not self.base_system:
            return []
        
        chunk_size = 300  # 5 minutes
        total_duration = segments[-1]['end'] if segments else 0
        
        all_moments = []
        chunk_num = 1
        chunk_start = 0
        
        while chunk_start < total_duration:
            chunk_end = min(chunk_start + chunk_size, total_duration)
            
            print(f"\n   🔍 Chunk {chunk_num}: {chunk_start/60:.1f}-{chunk_end/60:.1f} min")
            
            # Get segments for chunk
            chunk_segments = [
                s for s in segments
                if chunk_start <= s['start'] < chunk_end
            ]
            
            if chunk_segments:
                # Find moments in chunk (using base system for speed)
                try:
                    chunk_moments = self.base_system._find_moments_in_chunk(
                        chunk_segments,
                        chunk_start,
                        chunk_end,
                        chunk_num
                    )
                    
                    print(f"      ✅ Found {len(chunk_moments)} moments")
                    all_moments.extend(chunk_moments)
                except Exception as e:
                    print(f"      ⚠️  Error in chunk: {e}")
                    # Fallback: use single pass for this chunk
                    try:
                        fallback_moments = self.base_system._find_moments_single_pass(chunk_segments)
                        all_moments.extend(fallback_moments)
                    except:
                        pass
            
            chunk_start = chunk_end
            chunk_num += 1
        
        return all_moments
    
    def _find_exact_hook_location(self, segments: List[Dict], hook_text: str, approximate_time: float) -> float:
        """
        Find exact location of hook text in segments
        
        Args:
            segments: All video segments
            hook_text: Text to find (from AI analysis)
            approximate_time: AI's approximate timestamp
        
        Returns:
            Exact start time of hook
        """
        # Clean hook text for matching
        hook_clean = hook_text.lower().strip()
        hook_words = hook_clean.split()[:5]  # First 5 words
        
        # Search within ±30s window of approximate time
        search_start = max(0, approximate_time - 30)
        search_end = approximate_time + 30
        
        # Find segments in search window
        candidates = [
            seg for seg in segments
            if search_start <= seg.get('start', 0) <= search_end
        ]
        
        # Try to find exact match
        for seg in candidates:
            seg_text = seg.get('text', '').lower()
            
            # Check if hook words are in this segment
            if any(word in seg_text for word in hook_words if len(word) > 3):
                return seg['start']
        
        # Fallback: find closest segment to approximate time
        if candidates:
            closest = min(candidates, key=lambda s: abs(s['start'] - approximate_time))
            return closest['start']
        
        # Last resort: use approximate time
        return approximate_time
    
    def _calculate_moment_end(self, segments: List[Dict], start_time: float, 
                              min_duration: float = 35, max_duration: float = 70) -> float:
        """
        Calculate appropriate end time for moment to include complete story
        
        Args:
            segments: All video segments
            start_time: Moment start time
            min_duration: Minimum clip length (default 35s)
            max_duration: Maximum clip length (default 70s)
        
        Returns:
            End time that includes complete thought/story
        """
        # Get segments from start time onward
        future_segments = [
            seg for seg in segments
            if seg.get('start', 0) >= start_time
        ]
        
        if not future_segments:
            return start_time + min_duration
        
        current_duration = 0
        end_time = start_time + min_duration
        
        for seg in future_segments:
            current_duration = seg.get('end', start_time) - start_time
            
            # Check if we've reached minimum and have complete sentence
            if current_duration >= min_duration:
                text = seg.get('text', '')
                
                # Look for natural ending points
                if any(text.strip().endswith(end) for end in ['.', '!', '?', '...']):
                    end_time = seg.get('end', start_time)
                    break
            
            # Don't exceed maximum
            if current_duration >= max_duration:
                end_time = seg.get('end', start_time)
                break
            
            # Update potential end time
            end_time = seg.get('end', start_time)
        
        # Ensure minimum duration
        if end_time - start_time < min_duration:
            end_time = start_time + min_duration
        
        return end_time
    
    def _extract_moment_segments(self, segments: List[Dict], start_time: float, 
                                 end_time: float) -> List[Dict]:
        """
        Extract segments for a moment with proper boundaries
        
        Args:
            segments: All video segments
            start_time: Moment start
            end_time: Moment end
        
        Returns:
            List of segments within moment boundaries
        """
        moment_segments = []
        
        for seg in segments:
            seg_start = seg.get('start', 0)
            seg_end = seg.get('end', 0)
            
            # Segment overlaps with moment
            if seg_start < end_time and seg_end > start_time:
                moment_segments.append(seg)
        
        return moment_segments
    
    def _validate_moment(self, moment: Dict) -> bool:
        """
        Validate that moment has proper structure (WITH DEBUG)
        
        Args:
            moment: Moment dict to validate
        
        Returns:
            True if valid, False otherwise
        """
        
        # Must have segments
        if not moment.get('segments'):
            return False
        
        # Must have reasonable duration
        duration = moment.get('end', 0) - moment.get('start', 0)
        if duration < 10 or duration > 120:
            return False
        
        # Must have text content
        total_text = ''.join([seg.get('text', '') for seg in moment['segments']])
        if len(total_text.strip()) < 50:  # At least 50 chars
            return False
        
        return True
    
    def _format_transcript_for_analysis(self, segments: List[Dict]) -> str:
        """Format segments for AI analysis"""
        if not self.base_system:
            return '\n'.join([f"[{s['start']:.1f}s] {s.get('text', '')}" for s in segments])
        return self.base_system._format_segments(segments, max_chars=20000)
    
    async def _find_moments_with_consensus(self, segments: List[Dict], 
                                          story: Dict) -> List[Dict]:
        """
        NEW PIPELINE: Two-Pass + Iterative Refinement
        
        STAGE 0: Coarse scan (fast, broad)
        STAGE 1: Boundary refinement (deep, adaptive)
        STAGE 2: Quality filter (mini-godmode)
        """
        
        print(f"\n{'='*70}")
        print(f"🚀 OPTIMIZED PIPELINE V4 - PRINCIPLE-BASED")
        print(f"{'='*70}")
        print(f"   Cost per video: $3.20 (74% savings vs old $12.50)")
        print(f"   Pipeline: 6 stages (principle-based)")
        print(f"{'='*70}\n")
        
        # Store segments for helper methods
        self.segments = segments
        
        # STAGE 0: Coarse scan
        print(f"\n📍 STAGE 0: Coarse Viral Scan (Fast & Broad)")
        print(f"   Strategy: Find ALL potential viral opportunities")
        
        seeds = await self.coarse_viral_scan(
            segments=segments,
            story_context=story
        )
        
        if not seeds:
            print(f"   ⚠️  No seeds found")
            return []
        
        print(f"   ✅ Found {len(seeds)} potential viral seeds")
        
        # STAGE 1: Principle-Based Batch Refinement
        print(f"\n📍 STAGE 1: Principle-Based Batch Refinement")
        print(f"   Processing {len(seeds)} seeds in batches of 5")
        
        refined_moments = await self._refine_moments_parallel(
            seeds=seeds,
            segments=segments,
            story_context=story
        )
        
        print(f"\n   💎 Total refined: {len(refined_moments)} moments")
        
        if not refined_moments:
            return []
        
        # STAGE 1.75: Open Loop Bridging
        print(f"\n📍 STAGE 1.75: Open Loop Detection & Payoff Bridging")
        print(f"   Strategy: Bridge small gaps (<5s) when open loop detected")
        
        bridger = OpenLoopBridging(segments=segments)
        
        bridged_count = 0
        for i, moment in enumerate(refined_moments):
            original_end = moment.get('end', 0)
            
            # Try to detect and bridge
            refined_moments[i] = bridger.detect_and_bridge(moment)
            
            if refined_moments[i].get('bridged_gap'):
                bridged_count += 1
                gap = refined_moments[i]['end'] - original_end
                print(f"      ✅ Moment {i+1}: Bridged {original_end:.1f}s → {refined_moments[i]['end']:.1f}s (+{gap:.1f}s)")
        
        if bridged_count > 0:
            print(f"\n   💎 Open Loop Bridging: {bridged_count} moments extended")
        
        # STAGE 2: Principle-Based Conditional Restructure
        polished_moments = await self._conditional_restructure(refined_moments)
        
        print(f"\n   ✅ Polished: {len(polished_moments)} moments")
        
        # STAGE 2.5: Comprehensive Viral Composition (Multi-AI)
        # Replaces old Stages 2.5-2.9 with intelligent holistic optimization
        composed_moments = await self._viral_composition(polished_moments, segments)
        
        print(f"\n   ✅ Viral composition complete: {len(composed_moments)} moments")
        
        # GODMODE: Batched Premium Evaluation
        viral_moments = await self._batched_godmode_evaluation(composed_moments)
        
        print(f"\n{'='*70}")
        print(f"✅ PIPELINE COMPLETE")
        print(f"{'='*70}")
        print(f"\n   Final viral moments: {len(viral_moments)}")
        print(f"   Ready for export!")
        
        # Cost Summary
        print(f"\n{'='*70}")
        print(f"💰 COST BREAKDOWN")
        print(f"{'='*70}")
        print(f"   Stage 0 (Coarse Scan):        $1.50")
        print(f"   Stage 1 (Batch Refinement):   $0.60")
        print(f"   Stage 1.75 (Open Loop):       $0.00 (rule-based)")
        print(f"   Stage 2 (Conditional):        $0.30")
        print(f"   Stage 2.5 (Viral Composition): $6.00  ← Multi-AI, Comprehensive!")
        print(f"   Godmode (Premium Evaluation): $0.80")
        print(f"   " + "-"*50)
        print(f"   TOTAL:                        $9.20")
        print(f"   (Old rigid system: $12.50)")
        print(f"   (Previous 5-stage: $19.30)")
        print(f"   💰 Savings: 52% vs 5-stage, 26% vs old!")
        print(f"{'='*70}")
        
        return viral_moments
        
        # DEBUG SUMMARY
        print(f"\n   {'='*70}")
        print(f"   🔍 DEBUG: MOMENT EXTRACTION SUMMARY")
        print(f"   {'='*70}")
        
        valid_count = 0
        invalid_count = 0
        empty_segments = 0
        too_short = 0
        too_long = 0
        no_text = 0
        
        for m in moments:
            is_valid = self._validate_moment(m)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                
                # Track why invalid
                if not m.get('segments'):
                    empty_segments += 1
                
                duration = m.get('end', 0) - m.get('start', 0)
                if duration < 10:
                    too_short += 1
                elif duration > 120:
                    too_long += 1
                
                if m.get('segments'):
                    text = ''.join([s.get('text', '') for s in m['segments']])
                    if len(text.strip()) < 50:
                        no_text += 1
        
        print(f"\n   ✅ Valid moments: {valid_count}")
        print(f"   ❌ Invalid moments: {invalid_count}")
        
        if invalid_count > 0:
            print(f"\n   ⚠️  Invalid breakdown:")
            if empty_segments > 0:
                print(f"      - No segments: {empty_segments}")
            if too_short > 0:
                print(f"      - Too short (<10s): {too_short}")
            if too_long > 0:
                print(f"      - Too long (>120s): {too_long}")
            if no_text > 0:
                print(f"      - No text (<50 chars): {no_text}")
        
        # Show first 5 moments in detail
        print(f"\n   🔍 DEBUG: First 5 moments:")
        for i, m in enumerate(moments[:5], 1):
            duration = m.get('end', 0) - m.get('start', 0)
            seg_count = len(m.get('segments', []))
            is_valid = self._validate_moment(m)
            
            status = "✅" if is_valid else "❌"
            
            print(f"\n   {status} Moment {i}:")
            print(f"      Start: {m.get('start', 0):.1f}s")
            print(f"      End: {m.get('end', 0):.1f}s")
            print(f"      Duration: {duration:.1f}s")
            print(f"      Segments: {seg_count}")
            
            if seg_count > 0:
                first_text = m['segments'][0].get('text', 'NO TEXT')[:60]
                print(f"      First text: {first_text}...")
                
                if not is_valid:
                    # Show why invalid
                    text = ''.join([s.get('text', '') for s in m['segments']])
                    if duration < 10:
                        print(f"      ⚠️  Too short: {duration:.1f}s < 10s")
                    elif duration > 120:
                        print(f"      ⚠️  Too long: {duration:.1f}s > 120s")
                    if len(text.strip()) < 50:
                        print(f"      ⚠️  Too little text: {len(text)} chars < 50")
            else:
                print(f"      ❌ NO SEGMENTS!")
        
        print(f"   {'='*70}\n")
        
        return moments
    
    async def _find_moments_chunked_fixed(self, segments: List[Dict], 
                                         story: Dict) -> List[Dict]:
        """
        Process long videos in chunks with FIXED extraction
        """
        video_duration = segments[-1]['end']
        chunk_size = 300  # 5 min chunks
        
        all_moments = []
        chunk_num = 1
        
        for chunk_start in range(0, int(video_duration), chunk_size):
            chunk_end = min(chunk_start + chunk_size, video_duration)
            
            print(f"\n   🔍 Chunk {chunk_num}: {chunk_start/60:.1f}-{chunk_end/60:.1f} min")
            
            result = await self._find_moments_chunk_fixed(
                segments=segments,
                story=story,
                chunk_start=chunk_start,
                chunk_end=chunk_end
            )
            
            moments = result.get('moments', [])
            
            print(f"      ✅ Found {len(moments)} moments")
            
            all_moments.extend(moments)
            chunk_num += 1
        
        print(f"\n   ✅ Found {len(all_moments)} consensus moments")
        
        return all_moments
    
    async def _find_moments_chunk_fixed(self, segments: List[Dict], story: Dict,
                                       chunk_start: float, chunk_end: float) -> Dict:
        """
        Find PATTERN-AWARE viral moments using MASTER_LEARNINGS (CRITICAL FIX)
        
        Now checks:
        - Hook in first 3s
        - Winning hook types (Paradox, Authority, etc)
        - Power words
        - Pattern requirements
        """
        
        print(f"\n      🔍 Processing chunk {chunk_start/60:.1f}-{chunk_end/60:.1f} min (PATTERN-AWARE)")
        
        if not self.consensus:
            return {'moments': []}
        
        # LOAD MASTER LEARNINGS for pattern-aware moment finding
        patterns_library = ""
        power_words_list = []
        winning_hook_types = []
        
        try:
            import json
            from pathlib import Path
            
            # Try MD first, then JSON
            md_path = Path("learnings/MASTER_LEARNINGS.md")
            json_path = Path("data/MASTER_LEARNINGS.json")
            
            if md_path.exists():
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                patterns_library = self._parse_markdown_patterns(md_content)
                # For MD, use defaults (will be extracted from JSON if available)
                power_words_list = ["falsch", "niemals", "schockierend", "paradox", "verheerendster", "brutal", "geheim", "radikal", "gefährlich", "tödlich"]
            elif json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    master_learnings = json.load(f)
                patterns_library = self._format_all_patterns_from_json(master_learnings)
                
                # Extract power words
                power_words_list = master_learnings.get('hook_mastery', {}).get('power_words', [])
                
                # Extract winning hook types
                hook_patterns = master_learnings.get('hook_mastery', {}).get('winning_hook_types', [])
                for pattern in hook_patterns[:10]:  # Top 10 hook types
                    if isinstance(pattern, dict):
                        hook_type = pattern.get('type', '')
                        frequency = pattern.get('frequency_in_top', '')
                        template = pattern.get('template', '')
                        if hook_type:
                            winning_hook_types.append({
                                'type': hook_type,
                                'frequency': frequency,
                                'template': template
                            })
        except Exception as e:
            print(f"      ⚠️  Error loading learnings: {e}")
            patterns_library = "\n⚠️ Master Learnings not available. Using basic patterns.\n"
            # Fallback defaults
            power_words_list = ["falsch", "niemals", "schockierend", "paradox", "verheerendster", "brutal", "geheim"]
            winning_hook_types = [
                {'type': 'Paradox Statement', 'frequency': '73%', 'template': 'Wir machen X falsch'},
                {'type': 'Authority Curiosity', 'frequency': '67%', 'template': 'Nur [Zielgruppe] wissen...'}
            ]
        
        # Get segments for this chunk
        chunk_segments = [
            seg for seg in segments
            if chunk_start <= seg.get('start', 0) < chunk_end
        ]
        
        print(f"      📚 Loaded {len(winning_hook_types)} hook types, {len(power_words_list)} power words")
        
        # Format for AI
        chunk_text = self._format_transcript_for_analysis(chunk_segments[:50])
        
        # Format power words for prompt
        power_words_str = ", ".join(power_words_list[:30]) if power_words_list else "falsch, niemals, schockierend, paradox, verheerendster, brutal, geheim, radikal"
        
        # Format winning hook types for prompt
        hook_types_str = ""
        for hook in winning_hook_types[:8]:
            hook_types_str += f"- {hook['type']} ({hook['frequency']}): {hook['template'][:60]}...\n"
        
        # PATTERN-AWARE AI PROMPT
        prompt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIND PATTERN-AWARE VIRAL MOMENTS USING MASTER_LEARNINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{patterns_library[:3000]}  # Limit to avoid token overflow

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRANSCRIPT CHUNK ({chunk_end - chunk_start:.0f}s):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chunk_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIRAL PRINCIPLES (Guide, Not Rigid Rules):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 STRONG OPENING (0-5 seconds)

Principle: Captures attention immediately, creates curiosity or surprise
Examples: Paradox statements, bold claims, questions, unexpected contrasts
Focus: Hook viewer fast - understand the PRINCIPLE, not exact words
Different speakers use different words, same principle!

💥 EMOTIONAL INTENSITY

Principle: Language creates strong reaction, high arousal emotions
Examples: Curiosity, shock, excitement, urgency
Focus: Emotional engagement - "extrem", "krass", "heftig" work like "verheerendster"
Semantic meaning matters, not exact word matching!

📖 CLEAR PATTERN

Principle: Story has beginning, middle, end with information gap
Examples: Story with Twist, Paradox-Explanation-Metaphor, Transformation Story
Focus: Complete arc that builds curiosity and resolves tension
Structure matters, not exact formula!

⏱️ WATCHTIME OPTIMIZATION

Principle: Content maintains interest with pattern interrupts
Examples: Surprises, reveals, builds to satisfying conclusion
Focus: Keep watching - pattern interrupts prevent drop-off
Flow matters, not exact timing!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIND moments that follow these PRINCIPLES, not exact words!

From 172 analyzed clips: We learned PATTERNS, not a dictionary.
Different speakers, same principles. "extrem schlimm" = "verheerendster" semantically.

Quality over rigid compliance! Let AI understand context and principles.

Expected: 5-10 HIGH-QUALITY moments per chunk following principles.

For each moment return:
{{
  "start": timestamp_from_chunk_start,
  "end": timestamp_from_chunk_start,
  "hook_phrase": "exact hook text (first 3s)",
  "hook_type": "Paradox Statement",
  "pattern": "Paradox-Explanation-Metaphor",
  "information_gap": "what question it opens",
  "viral_reasoning": "Address these principles in your reasoning:
    * Is narrative arc complete? (beginning, middle, end with payoff)
    * Are there pattern interrupts? (twists, surprises, reveals)
    * Does information gap close properly? (builds curiosity, resolves)
    * Any filler or unnecessary content? (tight vs rambling)
    * Works standalone without context? (self-contained vs needs background)
    * Emotional engagement? (tension, relatability, universal pain)
    * Hook strength? (powerful opening vs weak start)
    * Universal relevance? (broad appeal vs niche)"
}}

IMPORTANT: In viral_reasoning, be specific about which principles the moment follows.
This helps intelligent deduplication choose the best version when moments overlap.

Respond with JSON array: [{{moment1}}, {{moment2}}]
"""
        
        # Call AI consensus with robust error handling
        try:
            result = await self.consensus.build_consensus(
                prompt=prompt,
                system="You are a viral content expert finding moments using PRINCIPLES from MASTER_LEARNINGS. Focus on understanding patterns and principles, not exact word matching. Quality over rigid compliance.",
                strategy='parallel_vote'
            )
            
            # Check if result is None
            if result is None:
                print(f"      ⚠️  Consensus returned None, skipping chunk...")
                return {'moments': []}
            
            # Extract consensus text
            if isinstance(result, dict):
                consensus_text = result.get('consensus', '')
                if not consensus_text:
                    consensus_text = result.get('content', '')
            elif isinstance(result, str):
                consensus_text = result
            else:
                print(f"      ⚠️  Unexpected result type: {type(result)}, skipping chunk...")
                return {'moments': []}
            
            if not consensus_text or consensus_text.strip() == '{}':
                print(f"      ⚠️  Empty consensus response, skipping chunk...")
                return {'moments': []}
            
            # Parse AI response with multiple format handling
            ai_moments = []
            
            try:
                # Method 1: Try parsing as JSON directly
                try:
                    data = json.loads(consensus_text)
                    if isinstance(data, list):
                        ai_moments = data
                        print(f"      🔍 DEBUG: Direct JSON array ({len(data)} moments)")
                    elif isinstance(data, dict):
                        ai_moments = data.get('moments', data.get('moments_list', []))
                        print(f"      🔍 DEBUG: JSON dict format ({len(ai_moments)} moments)")
                except json.JSONDecodeError:
                    # Method 2: Extract JSON from markdown code blocks
                    if '```json' in consensus_text:
                        json_start = consensus_text.find('```json') + 7
                        json_end = consensus_text.find('```', json_start)
                        if json_end > json_start:
                            json_text = consensus_text[json_start:json_end].strip()
                            data = json.loads(json_text)
                            if isinstance(data, list):
                                ai_moments = data
                            elif isinstance(data, dict):
                                ai_moments = data.get('moments', [])
                            print(f"      🔍 DEBUG: Extracted from ```json block ({len(ai_moments)} moments)")
                    # Method 3: Extract JSON array/object from text
                    elif '[' in consensus_text:
                        json_start = consensus_text.find('[')
                        json_end = consensus_text.rfind(']') + 1
                        if json_end > json_start:
                            json_text = consensus_text[json_start:json_end]
                            data = json.loads(json_text)
                            ai_moments = data if isinstance(data, list) else []
                            print(f"      🔍 DEBUG: Extracted array from text ({len(ai_moments)} moments)")
                    elif '{' in consensus_text:
                        json_start = consensus_text.find('{')
                        json_end = consensus_text.rfind('}') + 1
                        if json_end > json_start:
                            json_text = consensus_text[json_start:json_end]
                            # Try to fix common JSON issues
                            json_text = json_text.replace(',]', ']').replace(',}', '}')
                            data = json.loads(json_text)
                            if isinstance(data, dict):
                                ai_moments = data.get('moments', [])
                            elif isinstance(data, list):
                                ai_moments = data
                            print(f"      🔍 DEBUG: Extracted object from text ({len(ai_moments)} moments)")
                    else:
                        print(f"      ⚠️  No JSON structure found in response")
                        print(f"      Response preview: {consensus_text[:200]}...")
                        return {'moments': []}
            
            except json.JSONDecodeError as e:
                print(f"      ⚠️  JSON parsing failed: {e}")
                print(f"      Attempted JSON: {consensus_text[:300]}...")
                return {'moments': []}
            except Exception as e:
                print(f"      ⚠️  Unexpected parsing error: {e}")
                import traceback
                print(f"      Traceback: {traceback.format_exc()[:200]}")
                return {'moments': []}
        
        except Exception as e:
            print(f"      ❌ Error in consensus call: {e}")
            import traceback
            print(f"      Traceback: {traceback.format_exc()[:300]}")
            return {'moments': []}
        
        # PRINCIPLE-BASED: Extract moments (minimal validation, trust AI + Godmode)
        extracted_moments = []
        
        if not ai_moments:
            print(f"      ⚠️  No moments returned from AI")
            return {'moments': []}
        
        print(f"      🔍 Processing {len(ai_moments)} AI moments (principle-based extraction)...")
        
        for idx, ai_moment in enumerate(ai_moments, 1):
            # Skip invalid moment structures
            if not isinstance(ai_moment, dict):
                continue
            
            try:
                # Extract fields with safe type conversion (handle both old and new formats)
                # Start time: convert to float
                try:
                    approx_time_rel = float(ai_moment.get('start', ai_moment.get('timestamp', 0)))
                except (ValueError, TypeError):
                    approx_time_rel = 0.0
                
                # Hook text: convert to string
                try:
                    hook_text = str(ai_moment.get('hook_phrase', ai_moment.get('hook', ''))).strip()
                except (ValueError, TypeError):
                    hook_text = ''
                
                # If no start time, try to find hook in segments
                if approx_time_rel == 0 and hook_text:
                    for seg in chunk_segments[:20]:
                        seg_text = str(seg.get('text', '')).lower()
                        if hook_text[:20].lower() in seg_text:
                            try:
                                approx_time_rel = float(seg.get('start', 0)) - chunk_start
                            except (ValueError, TypeError):
                                pass
                            break
                
                # Basic validation: need start time
                if approx_time_rel == 0:
                    continue
                
                # Convert to absolute time (ensure float)
                try:
                    approx_time = float(approx_time_rel) + float(chunk_start)
                except (ValueError, TypeError):
                    print(f"      ⚠️  Error converting time: approx_time_rel={approx_time_rel}, chunk_start={chunk_start}")
                    continue
                
                # Find exact hook location
                exact_start = self._find_exact_hook_location(
                    segments=segments,
                    hook_text=hook_text if hook_text else "",
                    approximate_time=approx_time
                )
                
                # Calculate proper end time (pattern-aware duration)
                exact_end = self._calculate_moment_end(
                    segments=segments,
                    start_time=exact_start,
                    min_duration=30,  # Minimum for pattern-aware
                    max_duration=120  # Can be longer for transformation stories
                )
                
                # Extract segments with proper boundaries
                moment_segments = self._extract_moment_segments(
                    segments=segments,
                    start_time=exact_start,
                    end_time=exact_end
                )
                
                # Basic structure check only (duration and text presence)
                duration = exact_end - exact_start
                if duration < 10 or duration > 180:  # Too short or too long
                    continue
                
                # Check if segments have text
                has_text = any(s.get('text', '').strip() for s in moment_segments[:3])
                if not has_text:
                    continue
                
                # Extract pattern info with safe type conversion (for reference, not validation)
                try:
                    pattern = str(ai_moment.get('pattern', ai_moment.get('viral_pattern', 'Unknown'))).strip()
                except (ValueError, TypeError):
                    pattern = 'Unknown'
                
                try:
                    hook_type = str(ai_moment.get('hook_type', 'Unknown')).strip()
                except (ValueError, TypeError):
                    hook_type = 'Unknown'
                
                try:
                    viral_reasoning = str(ai_moment.get('viral_reasoning', ai_moment.get('reason', ai_moment.get('reasoning', '')))).strip()
                except (ValueError, TypeError):
                    viral_reasoning = ''
                
                try:
                    information_gap = str(ai_moment.get('information_gap', ai_moment.get('gap', ''))).strip()
                except (ValueError, TypeError):
                    information_gap = ''
                
                # Create moment object (principle-based, not strict validation)
                moment = {
                    'start': exact_start,
                    'end': exact_end,
                    'segments': moment_segments,
                    'pattern': pattern,
                    'hook_phrase': hook_text,
                    'hook_type': hook_type,
                    'information_gap': information_gap,
                    'ai_reasoning': viral_reasoning,
                    'pattern_metadata': {
                        'hook_type': hook_type,
                        'pattern': pattern,
                        'principle_based': True  # Flag that this follows principles, not strict rules
                    }
                }
                
                # Add moment (trust AI + Godmode will validate quality)
                extracted_moments.append(moment)
                
                # DEBUG OUTPUT for each moment
                print(f"\n      ✅ Moment {len(extracted_moments)}: \"{hook_text[:50] if hook_text else 'No hook'}...\"")
                print(f"         Pattern: {pattern}")
                print(f"         Hook Type: {hook_type}")
                print(f"         Duration: {duration:.1f}s")
                if viral_reasoning:
                    print(f"         Reasoning: {viral_reasoning[:80]}...")
                    
            except Exception as e:
                # Skip moments with errors, continue processing with detailed debug info
                import traceback
                error_details = {
                    'moment_index': idx,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'moment_keys': list(ai_moment.keys()) if isinstance(ai_moment, dict) else 'not_dict',
                    'moment_preview': str(ai_moment)[:200] if isinstance(ai_moment, dict) else str(ai_moment)[:200]
                }
                print(f"      ⚠️  Error processing moment {idx}: {e}")
                print(f"         Type: {error_details['error_type']}")
                print(f"         Moment keys: {error_details['moment_keys']}")
                print(f"         Preview: {error_details['moment_preview']}")
                try:
                    print(f"         Traceback: {traceback.format_exc()[:300]}")
                except:
                    pass
                continue
        
        print(f"\n      ✅ Principle-Based Extraction: {len(extracted_moments)}/{len(ai_moments)} moments extracted")
        print(f"      💡 Note: Quality validation happens in Godmode step, not here")
        
        return {'moments': extracted_moments}
    
    def _parse_markdown_patterns(self, md_content: str) -> str:
        """
        Parse MASTER_LEARNINGS.md to extract ALL patterns with full details
        
        Extracts:
        - Pattern name
        - Success rate
        - Optimal duration range
        - Structure requirements (hook, body, payoff timing)
        - Pattern interrupt frequency
        - Common mistakes to avoid
        """
        
        patterns_library = "\n## 🎯 COMPLETE VIRAL PATTERN LIBRARY (from 175 analyzed clips):\n\n"
        
        # Try to find pattern sections in markdown
        # Look for headers like "## Pattern Name" or "### Pattern Name"
        pattern_sections = re.split(r'\n(##+\s+.+?)\n', md_content, flags=re.MULTILINE)
        
        if len(pattern_sections) > 1:
            # Found markdown sections
            for i in range(1, len(pattern_sections), 2):
                header = pattern_sections[i]
                content = pattern_sections[i+1] if i+1 < len(pattern_sections) else ""
                
                # Extract pattern name
                pattern_name = re.sub(r'^##+\s+', '', header).strip()
                
                # Extract details from content
                success_rate = re.search(r'Success[:\s]+([\d.]+%)', content, re.I)
                duration = re.search(r'Duration[:\s]+([\d\-\s]+(?:seconds?|min|s))', content, re.I)
                hook_timing = re.search(r'Hook[:\s]+([^\n]+)', content, re.I)
                payoff_timing = re.search(r'Payoff[:\s]+([^\n]+)', content, re.I)
                interrupts = re.search(r'Interrupts[:\s]+([^\n]+)', content, re.I)
                mistakes = re.findall(r'❌\s*([^\n]+)', content)
                
                patterns_library += f"\n### {pattern_name}\n"
                if success_rate:
                    patterns_library += f"   Success Rate: {success_rate.group(1)}\n"
                if duration:
                    patterns_library += f"   Optimal Duration: {duration.group(1)}\n"
                if hook_timing:
                    patterns_library += f"   Hook Timing: {hook_timing.group(1)}\n"
                if payoff_timing:
                    patterns_library += f"   Payoff Timing: {payoff_timing.group(1)}\n"
                if interrupts:
                    patterns_library += f"   Pattern Interrupts: {interrupts.group(1)}\n"
                if mistakes:
                    patterns_library += f"   Common Mistakes: {', '.join(mistakes[:3])}\n"
                
                # Extract structure requirements
                structure_match = re.search(r'Structure[:\s]+([^\n]+)', content, re.I)
                if structure_match:
                    patterns_library += f"   Structure: {structure_match.group(1)}\n"
                
                patterns_library += "\n"
        else:
            # Fallback: return raw content if parsing fails
            patterns_library += "\n⚠️ Could not parse markdown structure. Using raw content.\n\n"
            patterns_library += md_content[:5000]  # Limit to avoid token overflow
        
        return patterns_library
    
    def _format_all_patterns_from_json(self, master_learnings: Dict) -> str:
        """
        Format ALL patterns from JSON (not just top 3!)
        
        Extracts complete details for each pattern:
        - Pattern name
        - Success rate / frequency
        - Optimal duration range
        - Structure requirements
        - Pattern interrupt frequency
        - Common mistakes
        """
        patterns_library = "\n## 🎯 COMPLETE VIRAL PATTERN LIBRARY (from 175 analyzed clips):\n\n"
        
        # Extract ALL hook patterns (not limited!)
        hook_patterns = master_learnings.get('hook_mastery', {}).get('winning_hook_types', [])
        structure_patterns = master_learnings.get('structure_mastery', {}).get('winning_structures', [])
        key_insights = master_learnings.get('key_insights', [])
        pattern_interrupt_rules = master_learnings.get('structure_mastery', {}).get('pattern_interrupt_techniques', [])
        content_rules = master_learnings.get('content_rules', {})
        never_do = content_rules.get('never_do', [])
        
        # Hook patterns - ALL of them
        patterns_library += "### HOOK PATTERNS (ALL):\n\n"
        for i, pattern in enumerate(hook_patterns, 1):  # NO LIMIT - ALL patterns!
            if isinstance(pattern, dict):
                pattern_type = pattern.get('type', 'Unknown')
                template = pattern.get('template', '')
                why_works = pattern.get('why_it_works', '')
                examples = pattern.get('examples', [])
                frequency = pattern.get('frequency_in_top', '')
                strength = pattern.get('strength', '')
                
                patterns_library += f"{i}. **{pattern_type}**\n"
                if frequency:
                    patterns_library += f"   Success Rate: {frequency}\n"
                if strength:
                    patterns_library += f"   Strength Score: {strength}/10\n"
                if template:
                    patterns_library += f"   Template: {template}\n"
                if why_works:
                    patterns_library += f"   Why it works: {why_works}\n"
                if examples:
                    patterns_library += f"   Examples: {', '.join(examples[:3])}\n"
                patterns_library += "\n"
        
        # Structure patterns - ALL of them
        patterns_library += "\n### STRUCTURE PATTERNS (ALL):\n\n"
        for i, pattern in enumerate(structure_patterns, 1):  # NO LIMIT - ALL structures!
            if isinstance(pattern, dict):
                pattern_name = pattern.get('name') or pattern.get('type', 'Unknown')
                flow = pattern.get('flow') or pattern.get('template', '')
                timing = pattern.get('timing', '')
                frequency = pattern.get('frequency_in_top', '')
                flow_score = pattern.get('flow_score', '')
                
                patterns_library += f"{i}. **{pattern_name}**\n"
                if frequency:
                    patterns_library += f"   Success Rate: {frequency}\n"
                if flow_score:
                    patterns_library += f"   Flow Score: {flow_score}/10\n"
                if flow:
                    patterns_library += f"   Flow: {flow}\n"
                if timing:
                    patterns_library += f"   Timing: {timing}\n"
                    # Extract duration from timing if available
                    duration_match = re.search(r'(\d+-\d+s|\d+-\d+min)', timing)
                    if duration_match:
                        patterns_library += f"   Optimal Duration: {duration_match.group(1)}\n"
                patterns_library += "\n"
        
        # Key insights - ALL of them
        patterns_library += "\n### KEY INSIGHTS (ALL):\n"
        for insight in key_insights:  # NO LIMIT - ALL insights!
            patterns_library += f"• {insight}\n"
        
        # Pattern interrupt rules
        patterns_library += f"\n### PATTERN INTERRUPT RULES:\n"
        patterns_library += f"• Frequency: Every 5-7 seconds (varies by pattern)\n"
        patterns_library += f"• Techniques: {', '.join(pattern_interrupt_rules)}\n"
        
        # Common mistakes to avoid
        if never_do:
            patterns_library += f"\n### COMMON MISTAKES TO AVOID:\n"
            for mistake in never_do:  # NO LIMIT - ALL mistakes!
                patterns_library += f"❌ {mistake}\n"
        
        return patterns_library
    
    async def _restructure_with_review(self, moment: Dict, segments: List[Dict],
                                      story_structure: Dict) -> Optional[Dict]:
        """
        Restructure with AI returning INDICES (preserves original segments with text)
        
        NOW PATTERN-AWARE: Uses full master learnings to identify viral patterns
        and apply pattern-specific optimization rules (duration, hook timing, story beats)
        """
        
        if not self.base_system or not self.consensus:
            return None
        
        # Extract segments for this moment
        moment_start = moment.get('start', 0)
        moment_end = moment.get('end', 0)
        moment_segments = [
            seg for seg in segments
            if moment_start <= seg.get('start', 0) < moment_end
        ]
        
        if not moment_segments:
            print(f"   ⚠️  No segments found for moment")
            return None
        
        # Create clip from moment
        clip = {
            'start': moment_start,
            'end': moment_end,
            'segments': moment_segments,
            'clip_id': f"moment_{moment.get('id', 'unknown')}"
        }
        
        # Format segments for AI
        segments_text = ""
        for i, seg in enumerate(moment_segments):
            text = seg.get('text', '') or seg.get('content', '')
            segments_text += f"[{i}] {seg.get('start', 0):.1f}s-{seg.get('end', 0):.1f}s: {text[:150]}\n"
        
        # LOAD COMPLETE MASTER LEARNINGS (check MD first, then JSON fallback)
        patterns_library = ""
        master_learnings = {}
        
        try:
            import json
            import re
            from pathlib import Path
            
            # PRIORITY 1: Check for learnings/MASTER_LEARNINGS.md
            md_path = Path("learnings/MASTER_LEARNINGS.md")
            json_path = Path("data/MASTER_LEARNINGS.json")
            
            if md_path.exists():
                print(f"   📚 Loading complete patterns from: {md_path}")
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Parse markdown to extract ALL patterns
                patterns_library = self._parse_markdown_patterns(md_content)
                master_learnings = {'source': 'markdown', 'file': str(md_path)}
                
            elif json_path.exists():
                print(f"   📚 Loading patterns from JSON: {json_path}")
                with open(json_path, 'r', encoding='utf-8') as f:
                    master_learnings = json.load(f)
                
                # Extract ALL patterns (not just top 3!)
                patterns_library = self._format_all_patterns_from_json(master_learnings)
                master_learnings['source'] = 'json'
                
            else:
                patterns_library = "\n⚠️ Master Learnings not found. Using default patterns.\n"
                master_learnings = {}
                
        except Exception as e:
            print(f"   ⚠️  Error loading learnings: {e}")
            import traceback
            print(f"   Detail: {traceback.format_exc()[:200]}")
            patterns_library = "\n⚠️ Could not load full learnings. Using defaults.\n"
            master_learnings = {}
        
        # Create pattern-aware prompt with improved structure
        prompt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESTRUCTURE CLIP - PATTERN-AWARE OPTIMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{patterns_library}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CURRENT CLIP TO RESTRUCTURE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Duration: {moment_end - moment_start:.1f}s
Segments: {len(moment_segments)}

{segments_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK - 3 STEP PROCESS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: ANALYZE CURRENT CLIP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyze the clip content above and answer:

1. **Which pattern(s) does this clip use?**
   - Review ALL patterns in the library above
   - Identify the PRIMARY hook pattern (e.g., "Paradox Statement", "Authority Curiosity", "Story", etc.)
   - Identify the PRIMARY structure pattern (e.g., "Paradox-Explanation-Metaphor", "Story-Arc-With-Lesson", "Transformation Story", etc.)
   - Provide confidence score (0-1)

2. **What's the core story arc?**
   - What is the main narrative?
   - What are the key story beats present?
   - What is the emotional journey?

3. **What duration does THIS pattern need?**
   - Look up the identified pattern in the library above
   - What is the optimal duration range for that pattern?
   - Don't force into arbitrary limits - use the pattern's requirements!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 2: APPLY PATTERN-SPECIFIC RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on the identified pattern, apply these pattern-specific rules:

**Hook Placement** (pattern-dependent):
- Paradox Statement: Hook at 0-3s (paradox stated)
- Transformation Story: Hook at 0-3s (before state shown)
- Authority + Proof: Hook at 0-3s (bold claim)
- Story with Twist: Hook at 0-3s (curiosity/conflict)

**Body Structure** (pattern-dependent):
- Paradox Statement: 3-40s exploration/explanation, then resolution
- Transformation Story: Setup (3s-1min) → Journey (1-7min with interrupts every 20s) → Payoff
- Authority + Proof: Credibility (3-20s) → Evidence (20-70s) → Application
- Story-Arc-With-Lesson: Setup (3-10s) → Climax (10-20s) → Lesson (20-30s)

**Pattern Interrupts** (pattern-dependent):
- Some patterns need interrupts every 5-7s (high-energy)
- Others need interrupts every 15-20s (story-driven)
- Some need minimal interrupts (authority/educational)

**Payoff Timing** (pattern-dependent):
- Some patterns need payoff at 80% mark (keeps watching)
- Others need payoff at end (resolution)
- Some need multiple payoffs (transformation stories)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 3: SELECT SEGMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Choose which segment INDICES to keep to optimize for the identified pattern:

- Ensure hook is in first 3 seconds
- Include all required story beats for the pattern
- Maintain pattern-specific structure (hook → body → payoff)
- Apply pattern interrupt frequency
- Optimize for watchtime retention, not fixed duration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPOND WITH JSON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "step1_analysis": {{
    "hook_pattern": "Paradox Statement",  // Primary hook pattern identified
    "structure_pattern": "Paradox-Explanation-Metaphor",  // Primary structure pattern
    "confidence": 0.85,  // Confidence score (0-1)
    "core_story_arc": "Brief description of main narrative...",
    "key_story_beats": ["hook", "paradox", "exploration", "resolution"],
    "pattern_optimal_duration_range": "30-60s"  // From pattern library
  }},
  "step2_pattern_rules": {{
    "optimal_duration_seconds": 45,  // Pattern-specific optimal duration
    "hook_timing": "0-3s",  // When hook should appear (pattern-dependent)
    "body_structure": {{
      "setup_timing": "3-10s",  // Pattern-dependent
      "main_content_timing": "10-40s",  // Pattern-dependent
      "pattern_interrupt_frequency": "every_5-7s",  // Pattern-dependent
      "interrupt_techniques": ["tempo_change", "paradox", "numbers"]
    }},
    "payoff_timing": "40-45s",  // Pattern-dependent (could be "end" or "80%")
    "required_beats": ["hook", "paradox_statement", "exploration", "resolution"]
  }},
  "step3_segment_selection": {{
    "keep_segments": [0, 2, 4, 7, 9],  // Array of segment INDICES to keep (0-indexed)
    "reasoning": "I identified [pattern] because [reason]. The pattern requires [duration]s with [structure]. I'm keeping segments [indices] because they contain [required beats]. Pattern interrupts will occur at segments [X, Y, Z]..."
  }}
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL INSTRUCTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**DON'T FORCE CLIPS INTO FIXED LENGTHS.**

Use the pattern library above to determine the OPTIMAL structure for THIS specific clip's pattern.

Examples:
- If clip uses "Paradox Statement" → Usually 30-60s, hook at 0-3s, payoff at end
- If clip uses "Transformation Story" → Usually 2-8min, hook at 0-3s, interrupts every 20s, payoff last 30s
- If clip uses "Authority + Proof" → Usually 45-90s, hook at 0-3s, evidence 20-70s, payoff 70-90s

Let the PATTERN determine the length, not arbitrary rules!

Watchtime retention > Fixed duration
Story coherence > Pattern forcing
Pattern requirements > Generic rules

IMPORTANT: Return segment INDICES (numbers), not new segment objects!
"""

        system = """You are an expert video editor optimizing clips for viral potential using pattern-based analysis.

You have access to 175 analyzed viral clips and their patterns. Your job:
1. Identify which viral pattern(s) the clip matches
2. Apply that pattern's specific optimization rules
3. Select segments that optimize for watchtime retention, not fixed duration

You analyze segments and select which ones to keep based on:
- Pattern identification (hook type, structure type)
- Pattern-specific duration requirements
- Hook timing rules for the pattern
- Story beat requirements for the pattern
- Pattern interrupt frequency needs
- Payoff timing for the pattern
- Watchtime optimization (retention > duration)

Return ONLY segment indices with pattern analysis, not new segment objects."""

        print(f"\n   🤖 AI analyzing {len(moment_segments)} segments...")
        
        # Get AI recommendation
        result = await self.consensus.build_consensus(
            prompt=prompt,
            system=system,
            strategy='parallel_vote'
        )
        
        # Parse response
        try:
            response_text = result.get('consensus', '')
            
            # Try to extract JSON from response (multiple methods)
            # Method 1: Look for ```json block
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                if json_end > json_start:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text
            # Method 2: Look for first { to last }
            elif '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            else:
                # No JSON found
                print(f"   ⚠️  No JSON structure found in response")
                print(f"   Response preview: {response_text[:200]}")
                return clip
            
            # Clean common issues
            json_text = json_text.strip()
            
            # Try to parse
            try:
                restructured_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"   ⚠️  JSON parsing failed: {e}")
                print(f"   Attempted JSON: {json_text[:300]}")
                
                # Try to fix common issues
                # Remove trailing commas
                json_text = json_text.replace(',]', ']').replace(',}', '}')
                
                try:
                    restructured_data = json.loads(json_text)
                    print(f"   ✅ Fixed with comma removal")
                except:
                    print(f"   ❌ Could not parse JSON, using original clip")
                    return clip
            
            # Extract pattern information (support both new 3-step and legacy format)
            step1_analysis = restructured_data.get('step1_analysis', {})
            step2_pattern_rules = restructured_data.get('step2_pattern_rules', {})
            step3_selection = restructured_data.get('step3_segment_selection', {})
            
            # Support legacy format
            if not step1_analysis:
                step1_analysis = restructured_data.get('identified_patterns', {})
            if not step2_pattern_rules:
                step2_pattern_rules = restructured_data.get('pattern_rules', {})
            if not step3_selection:
                step3_selection = {'keep_segments': restructured_data.get('keep_segments', []), 'reasoning': restructured_data.get('reasoning', '')}
            
            # Get segment indices (from step3 or legacy)
            keep_indices = step3_selection.get('keep_segments', restructured_data.get('keep_segments', []))
            
            if not keep_indices:
                print(f"   ⚠️  AI returned no segments to keep, using original")
                return clip
            
            # Use ORIGINAL segments at those indices (preserves text field!)
            new_segments = [moment_segments[i] for i in keep_indices if i < len(moment_segments)]
            
            if not new_segments:
                print(f"   ⚠️  Invalid indices returned, using original")
                return clip
            
            # Calculate durations
            final_duration = new_segments[-1]['end'] - new_segments[0]['start']
            optimal_duration = step2_pattern_rules.get('optimal_duration_seconds', final_duration)
            
            # Extract pattern details
            hook_pattern = step1_analysis.get('hook_pattern', 'Unknown')
            structure_pattern = step1_analysis.get('structure_pattern', 'Unknown')
            confidence = step1_analysis.get('confidence', 0.0)
            core_story_arc = step1_analysis.get('core_story_arc', '')
            pattern_duration_range = step1_analysis.get('pattern_optimal_duration_range', '')
            
            # Calculate original duration for comparison
            original_duration = moment_end - moment_start
            segments_removed = len(moment_segments) - len(new_segments)
            segments_kept = len(new_segments)
            
            # Extract success rate if available
            success_rate = ""
            if step1_analysis:
                # Try to find success rate from pattern library (would need to match pattern name)
                # For now, use confidence as proxy
                if confidence >= 0.8:
                    success_rate = "High confidence"
                elif confidence >= 0.6:
                    success_rate = "Medium confidence"
                else:
                    success_rate = "Low confidence"
            
            # Extract reasoning
            reasoning = step3_selection.get('reasoning', '')
            if not reasoning:
                reasoning = restructured_data.get('reasoning', 'No reasoning provided')
            
            # Format reasoning for display (truncate if too long)
            reasoning_short = reasoning[:100] + "..." if len(reasoning) > 100 else reasoning
            
            # DEBUG OUTPUT - Pattern Analysis Summary
            print(f"\n   {'='*60}")
            print(f"   🎯 PATTERN ANALYSIS SUMMARY")
            print(f"   {'='*60}")
            print(f"   🎯 Pattern: {hook_pattern} → {structure_pattern}")
            if confidence > 0:
                print(f"      Confidence: {confidence:.0%} ({success_rate})")
            if pattern_duration_range:
                print(f"      Pattern Duration Range: {pattern_duration_range}")
            print(f"\n   📏 Duration: {original_duration:.1f}s → {final_duration:.1f}s")
            if optimal_duration != final_duration:
                print(f"      Optimal for pattern: {optimal_duration:.1f}s")
            duration_change = final_duration - original_duration
            if abs(duration_change) > 1:
                change_pct = (duration_change / original_duration) * 100
                direction = "shortened" if duration_change < 0 else "lengthened"
                print(f"      Change: {abs(duration_change):.1f}s ({abs(change_pct):.0f}% {direction})")
            else:
                print(f"      Change: Minimal (optimized structure, not length)")
            
            print(f"\n   ✂️  Segments: Kept {segments_kept}/{len(moment_segments)} segments")
            if segments_removed > 0:
                print(f"      Removed: {segments_removed} segments (filler/slow parts)")
            else:
                print(f"      All segments kept (structure optimized)")
            
            if core_story_arc:
                print(f"\n   📖 Story Arc: {core_story_arc[:80]}...")
            
            # Show key story beats if available
            key_beats = step1_analysis.get('key_story_beats', [])
            if key_beats:
                print(f"\n   🎬 Key Beats: {', '.join(key_beats)}")
            
            # Show pattern-specific rules applied
            body_structure = step2_pattern_rules.get('body_structure', {})
            if body_structure:
                interrupt_freq = body_structure.get('pattern_interrupt_frequency', '')
                payoff_timing = step2_pattern_rules.get('payoff_timing', '')
                if interrupt_freq or payoff_timing:
                    print(f"\n   ⚙️  Pattern Rules Applied:")
                    if interrupt_freq:
                        print(f"      Interrupts: {interrupt_freq}")
                    if payoff_timing:
                        print(f"      Payoff: {payoff_timing}")
            
            print(f"\n   💡 Reasoning: {reasoning_short}")
            print(f"   {'='*60}\n")
            
            # Verify segments have text
            for seg in new_segments:
                if 'text' not in seg and 'content' in seg:
                    seg['text'] = seg['content']
            
            # Create restructured clip with ORIGINAL segments + PATTERN INFO
            restructured = {
                **clip,
                'segments': new_segments,  # These are original segments, not AI-generated
                'start': new_segments[0]['start'],
                'end': new_segments[-1]['end'],
                'original_indices': keep_indices,
                'restructure_method': 'pattern_aware_review',
                'ai_reasoning': step3_selection.get('reasoning', restructured_data.get('reasoning', '')),
                'pattern_analysis': {
                    'step1_analysis': step1_analysis,
                    'step2_pattern_rules': step2_pattern_rules,
                    'step3_selection': step3_selection,
                    'optimal_duration': optimal_duration,
                    'actual_duration': final_duration,
                    'pattern_duration_range': pattern_duration_range,
                    'hook_pattern': hook_pattern,
                    'structure_pattern': structure_pattern,
                    'confidence': confidence
                },
                'structure': {
                    'segments': new_segments,
                    'total_duration': final_duration,
                    'pattern': structure_pattern,
                    'hook_type': hook_pattern
                }
            }
            
            return restructured
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parsing failed: {e}")
            print(f"   Using original clip")
            return clip
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            print(f"   Using original clip")
            return clip
    
    async def _evaluate_quality_debate(self, clip: Dict, 
                                      story_structure: Dict) -> Dict:
        """
        Quality evaluation using debate strategy WITH LEARNINGS + VALIDATION
        
        Now validates that AI actually used learnings in response
        """
        
        if not self.consensus:
            # Fallback to base system
            if self.base_system:
                return self.base_system._score_clip_quality(clip, story_structure)
            return {
                'total_score': 30,
                'quality_tier': 'C',
                'scores': {},
                'reasoning': {}
            }
        
        # GET FULL LEARNINGS (maximum quality!)
        learnings_prompt = self._get_learnings_safely(mode='full')
        
        clip_text = self._format_clip_for_eval(clip)
        
        # DEBUG: Check if clip text is valid
        if not clip_text or len(clip_text) < 50:
            print(f"   ⚠️  WARNING: Clip text is empty or too short!")
            print(f"   Length: {len(clip_text)}")
            print(f"   Content: {clip_text[:200]}")
        else:
            print(f"   ✅ Clip text formatted: {len(clip_text)} chars")
        
        prompt = f"""{learnings_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🎬 CLIP ZU BEWERTEN:

{clip_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🎯 PRINCIPLE-BASED QUALITY EVALUATION

Bewerte diesen Clip nach PRINZIPIEN (nicht starren Regeln) basierend auf den Learnings oben.

⚠️ KRITISCH: Bewerte SEMANTISCH und KONTEXT-BEWUSST, nicht nach Checkliste!

## SELBST-CHECK VOR DER BEWERTUNG:

1. FORMAT-ERKENNUNG:
   - Was IST dieser Clip? (Stage/Live/Podcast/Q&A/Monolog/Dialog?)
   - Welche Erwartungen sind für DIESES Format angemessen?
   - Bin ich fair für das, was es IST?

2. PRINZIPIEN-CHECK:
   - Fängt es Aufmerksamkeit? (Konzept, nicht Checkliste)
   - Hält es Engagement? (Flow, nicht Timing)
   - Fühlt es sich vollständig an? (Zufriedenheit, nicht Struktur)
   - Erzeugt Sprache Intensität? (Semantisch, nicht exakte Wörter)

3. VERMEIDE:
   - Bestrafe ich für nicht-exakte Formel?
   - Bin ich zu starr bei Timing?
   - Übersehe ich Kontext, der Entscheidungen erklärt?
   - Wende ich Monolog-Regeln auf Dialog an?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## BEWERTUNGS-KRITERIEN (PRINZIPIEN-BASIERT):

### 1. HOOK STRENGTH (0-10) - ATTENTION CAPTURE

Bewerte: Erzeugt der Opening IMMEDIATE ENGAGEMENT?

✅ PRINZIPIEN (nicht Regeln):
- Fängt Opening Aufmerksamkeit? (0-5s flexibles Fenster, nicht starr 0-3s)
- Erzeugt sofortige Neugier oder Emotion?
- Starker Opening-Moment vorhanden?

📊 SEMANTISCHE BEWERTUNG (nicht exakte Wörter):
- "extrem krass" = gleiche Intensität wie "verheerendste"
- "brutal heftig" = hohe Arousal-Sprache
- "unglaublich" = Überraschungs-Trigger
- NICHT limitiert auf exakte Wortliste!

🎭 KONTEXT-BEWUSST:
- Dramatische Pause kann Technik sein (nicht Fehler)
- Verschiedene Formate haben verschiedene Openings
- "Und dann..." kann funktionieren wenn Spannung hoch ist

Beispiele:
- "Arbeite niemals für Geld" bei 0s = 10/10
- "Extrem krasse Sache" bei 2s = 8/10 (semantische Intensität)
- Dramatische 3s Pause dann bold claim = 7/10 (Spannungs-Technik)
- "Und dann passierte..." bei 0s = 3/10 WENN keine vorherige Spannung
- "Und dann passierte..." bei 0s = 7/10 WENN Mystery etabliert

### 2. STORY COHERENCE (0-10) - COMPLETENESS

Bewerte: Ist dies vollständig für WAS ES IST?

✅ PRINZIPIEN:
- Vollständig für SEINEN Typ? (nicht erzwungene Struktur)
- Hat notwendigen Kontext?
- Befriedigende Konklusion?
- Funktioniert standalone?

🎭 FORMAT-FLEXIBILITÄT:
- Dialog kann mid-conversation starten wenn Kontext klar
- Q&A hat andere Struktur als Monolog
- Live-Content hat anderen Rhythmus als editiert

Beispiele:
- Vollständiger Story-Arc (Setup→Konflikt→Resolution) = 9/10
- Teaching-Moment (Problem→Insight→Anwendung) = 8/10
- Q&A-Austausch (Frage→Antwort→Takeaway) = 8/10
- Dialog-Auszug (klarer Austausch) = 7/10
- Mid-conversation Fragment (unklar) = 3/10

### 3. NATURAL FLOW (0-10) - ENGAGEMENT MAINTENANCE

Bewerte: Hält das Pacing Engagement?

✅ PRINZIPIEN:
- Engagierendes Pacing? (nicht starres Timing)
- Re-Engagement-Momente?
- Vermeidet langweilige Strecken?
- Rhythmus dient dem Content?

🎭 KONTEXT-BEWUSST:
- Interrupts können sein: Reveals, Beispiele, Eskalation, Fragen
- Timing variiert nach Format (live vs editiert)
- Natürliche Sprache hat eigenen Rhythmus

Beispiele:
- Variiertes Pacing mit Reveals = 9/10
- Schnelles Pacing (11s gap close) = 8/10 (Wahl, nicht Fehler!)
- Dramatische Pausen gut genutzt = 8/10
- Monotone Delivery = 4/10
- 10s Stille ohne Payoff = 2/10

### 4. WATCHTIME POTENTIAL (0-10) - RETENTION

Bewerte: Werden Leute durchschauen?

✅ PRINZIPIEN:
- Würden Leute durchschauen?
- Hält Neugier?
- Liefert Payoff?
- Wert die Dauer?

Beispiele:
- Starker Hook + gutes Pacing + Payoff = 9/10
- Guter Hook + langsamer Middle + schwaches Ende = 5/10
- Schwacher Hook + starke Story = 6/10
- Technischer Fehler (tatsächliche dead air) = 1/10

### 5. EMOTIONAL IMPACT (0-10) - RESONANCE

Bewerte: Erzeugt es Gefühl?

✅ PRINZIPIEN:
- Erzeugt starkes Gefühl?
- Triggert Erkennung/Überraschung?
- Unvergesslich?
- Teilbar?

📊 SEMANTISCHE BEWERTUNG:
- Intensität nicht abhängig von exakten Wörtern
- Kulturelle/kontextuelle Variationen gültig
- Konzept zählt, nicht Vokabular

Beispiele:
- Universeller Pain Point + Insight = 9/10
- Relatable Situation + Reframe = 8/10
- Interessant aber nicht emotional = 5/10
- Faktisch/neutral = 3/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## WEAKNESSES REPORTING (KONSTRUKTIV):

⚠️ FOKUS AUF:
- WAS könnte verbessert werden (nicht welche Regel verletzt)
- WARUM es wichtig ist (nicht nur "bricht Regel")
- KONTEXT-BERÜCKSICHTIGUNG (nicht blinde Strafe)

Beispiele für konstruktive Weaknesses:
- "⚠️ Opening könnte stärker sein - Sprachintensität moderat (Erwägen: provokativere Formulierung?)"
- "⚠️ Hook bei 3.2s - leicht verzögerte Engagement (noch akzeptabel, aber 0-3s ideal)"
- "⚠️ 10s Pause am Start - wenn dramatische Technik: effektiv; wenn dead air: Problem (Kontext nötig)"

NICHT: "❌ Keine Power Words (verheerendste, niemals) = 0 points"
NICHT: "❌ Hook bei 3.2s statt 0-3s = FAIL"
NICHT: "❌ 10s Leerraum = Instant Kill"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Antworte in JSON:
{{
  "scores": {{
    "hook_strength": X,
    "story_coherence": X,
    "natural_flow": X,
    "watchtime_potential": X,
    "emotional_impact": X
  }},
  "total_score": X,
  "quality_tier": "A/B/C/D",
  "reasoning": {{
    "strengths": [
      "Konkrete Stärke mit Kontext",
      "Pattern-Referenz (semantisch, nicht exakt)"
    ],
    "weaknesses": [
      "Konstruktive Verbesserung (nicht Regel-Verletzung)",
      "Kontext-bewusste Kritik"
    ],
    "learned_patterns_applied": [
      "[PATTERN NAME] - semantisch erkannt"
    ],
    "algorithm_assessment": "Watchtime/Completion/Engagement Impact erklärt",
    "format_detected": "Stage/Live/Podcast/Q&A/etc",
    "context_considerations": "Format-spezifische Anpassungen berücksichtigt"
  }}
}}
"""
        
        system = f"""Du bist ein PRINZIPIEN-BASIERTER Qualitäts-Evaluator trainiert auf {self._get_clips_analyzed_count()} viralen Clips.

WICHTIG: 
- Bewerte nach PRINZIPIEN, nicht starren Regeln
- Erkenne SEMANTISCHE Äquivalente (nicht exakte Wort-Matches)
- Berücksichtige FORMAT-KONTEXT (Stage/Live/Podcast/Q&A)
- Sei KONSTRUKTIV in Kritik (Verbesserung, nicht Bestrafung)
- Nutze Learnings als GUIDELINES, nicht Checklisten

Deine Aufgabe: Finde die WAHRHEIT über viral potential, nicht ob Regeln erfüllt sind."""
        
        # Run debate
        result = await self.consensus.build_consensus(
            prompt=prompt,
            system=system,
            strategy='debate'
        )
        
        consensus_text = result.get('consensus', '')
        
        # VALIDATE learnings were actually used
        validation = self._validate_learnings_usage(consensus_text)
        
        # Print validation report
        if validation:
            print(f"\n   🔍 Validation: {validation['confidence']:.0%} confidence")
            
            if validation['confidence'] < 0.40:
                print(f"      ⚠️  Warning: Low learnings application!")
                print(f"      Patterns: {len(validation['patterns_referenced'])}")
                print(f"      Power words: {len(validation['power_words_used'])}")
            elif validation['confidence'] >= 0.70:
                print(f"      ✅ Excellent pattern application!")
        
        # Parse JSON response
        import re
        import json
        
        json_match = re.search(r'\{[\s\S]*\}', consensus_text)
        if json_match:
            try:
                quality_result = json.loads(json_match.group())
                
                # Ensure quality_tier is set based on total_score if missing or invalid
                total_score = quality_result.get('total_score', None)
                
                # SAFE DEFAULT if parsing failed
                if total_score is None:
                    print(f"   ⚠️  Could not parse score, using confidence as fallback")
                    # Use confidence as score (0-100 → 0-50)
                    confidence = result.get('confidence', 0.5)
                    total_score = int(confidence * 50)
                    quality_result['total_score'] = total_score
                    print(f"   📊 Fallback score: {total_score}/50 (from {confidence:.0%} confidence)")
                
                if 'quality_tier' not in quality_result or not quality_result.get('quality_tier'):
                    # Safety: Handle None score
                    if total_score is None:
                        print(f"   ⚠️  Could not parse score from consensus, using confidence fallback")
                        confidence = result.get('confidence', 0.5)
                        total_score = int(confidence * 50)  # Convert confidence to score
                        print(f"   📊 Fallback score: {total_score}/50 (from {confidence:.0%} confidence)")
                        quality_result['total_score'] = total_score
                    quality_result['quality_tier'] = self._get_quality_tier(total_score)
                else:
                    # Validate tier matches score (use score-based tier if score is below threshold)
                    # Safety: Handle None score
                    if total_score is None:
                        print(f"   ⚠️  Could not parse score from consensus, using confidence fallback")
                        confidence = result.get('confidence', 0.5)
                        total_score = int(confidence * 50)  # Convert confidence to score
                        print(f"   📊 Fallback score: {total_score}/50 (from {confidence:.0%} confidence)")
                        quality_result['total_score'] = total_score
                    
                    tier_from_score = self._get_quality_tier(total_score)
                    tier_from_ai = quality_result.get('quality_tier', 'D')
                    tier_letter_ai = self._extract_tier_letter(tier_from_ai)
                    
                    # If AI tier is higher than score allows, use score-based tier
                    tier_order = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
                    if tier_order.get(tier_letter_ai, 0) > tier_order.get(tier_from_score, 0):
                        quality_result['quality_tier'] = tier_from_score
                
                quality_result['consensus_confidence'] = result.get('confidence', 0)
                quality_result['validation'] = validation
                quality_result['strategy_used'] = 'debate'
                
                # Print detailed reasoning output
                tier_string = quality_result.get('quality_tier', 'D')
                total_score = quality_result.get('total_score', 0)
                passed = tier_string in ['A', 'B', 'C']
                
                print(f"      {'✅' if passed else '❌'} {tier_string} (Score: {total_score}/50) - {'Passed' if passed else 'Rejected'}")
                
                # Print detailed reasoning from consensus
                if consensus_text:
                    print(f"\n   📝 REASONING:")
                    # Try to extract score and reasoning
                    lines = consensus_text.split('\n')
                    printed_lines = 0
                    for line in lines[:15]:  # First 15 lines
                        if line.strip() and not line.startswith('{') and not line.startswith('}'):
                            print(f"      {line[:100]}")
                            printed_lines += 1
                            if printed_lines >= 10:  # Limit to 10 lines
                                break
                    
                    if len(consensus_text) > 500:
                        print(f"\n   🔍 Full consensus (first 500 chars):")
                        print(f"      {consensus_text[:500]}...")
                
                # Also print score breakdown if available
                if 'scores' in quality_result:
                    print(f"\n   📊 Score Breakdown:")
                    scores = quality_result['scores']
                    for key, val in scores.items():
                        print(f"      {key}: {val}/10")
                
                # Print reasoning details if available
                if 'reasoning' in quality_result:
                    reasoning = quality_result['reasoning']
                    if isinstance(reasoning, dict):
                        if 'strengths' in reasoning and reasoning['strengths']:
                            print(f"\n   ✅ Strengths:")
                            for strength in reasoning['strengths'][:3]:  # Top 3
                                print(f"      • {strength[:80]}")
                        
                        if 'weaknesses' in reasoning and reasoning['weaknesses']:
                            print(f"\n   ⚠️  Weaknesses:")
                            for weakness in reasoning['weaknesses'][:3]:  # Top 3
                                print(f"      • {weakness[:80]}")
                        
                        if 'learned_patterns_applied' in reasoning and reasoning['learned_patterns_applied']:
                            print(f"\n   🎯 Patterns Applied:")
                            for pattern in reasoning['learned_patterns_applied'][:5]:  # Top 5
                                print(f"      • {pattern}")
                
                return quality_result
            except json.JSONDecodeError:
                pass
        
        # Fallback
        if self.base_system:
            return self.base_system._score_clip_quality(clip, story_structure)
        
        # Use threshold-based tier for fallback
        fallback_score = 25
        return {
            'scores': {
                'hook_strength': 5,
                'story_coherence': 5,
                'natural_flow': 5,
                'watchtime_potential': 5,
                'emotional_impact': 5
            },
            'total_score': fallback_score,
            'quality_tier': self._get_quality_tier(fallback_score),
            'reasoning': {
                'strengths': ['Could not parse evaluation'],
                'weaknesses': ['Parser error'],
                'learned_patterns_applied': [],
                'algorithm_assessment': 'N/A'
            },
            'consensus_confidence': 0.5,
            'validation': validation
        }
    
    def _get_learnings_safely(self, mode='default'):
        """
        Get learnings with graceful fallback
        
        Args:
            mode: 'default' or 'full' (full includes all details)
        """
        try:
            from master_learnings_v2 import get_learnings_for_prompt
            return get_learnings_for_prompt()
        except Exception as e:
            print(f"   ⚠️  Learnings not available: {e}")
            print(f"   ℹ️  Run: python run_learning_pipeline.py first!")
            return """
# ⚠️ LEARNINGS NOT YET TRAINED

Run initial training first:
python run_learning_pipeline.py

Then learnings will be available.
"""
    
    def _validate_learnings_usage(self, response_text: str) -> Dict:
        """Validate that AI used learnings in response"""
        try:
            from master_learnings_v2 import validate_learnings_application
            return validate_learnings_application(response_text)
        except Exception as e:
            print(f"      ⚠️  Validation failed: {e}")
            return {
                'learnings_applied': False,
                'confidence': 0.0,
                'patterns_referenced': [],
                'power_words_used': [],
                'algorithm_reasoning_present': False
            }
    
    def _print_validation_stats(self, validations: List[Dict]):
        """Print aggregated validation statistics"""
        
        if not validations:
            return
        
        print(f"\n{'='*70}")
        print("🔍 LEARNINGS VALIDATION STATS")
        print(f"{'='*70}")
        
        # Calculate averages
        confidences = [v.get('confidence', 0) for v in validations if v]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Count quality scores
        quality_scores = [v.get('quality_score', 'unknown') for v in validations if v]
        excellent = quality_scores.count('excellent')
        good = quality_scores.count('good')
        fair = quality_scores.count('fair')
        poor = quality_scores.count('poor')
        
        # Pattern usage
        all_patterns = []
        all_power_words = []
        
        for v in validations:
            if v:
                all_patterns.extend(v.get('patterns_referenced', []))
                all_power_words.extend(v.get('power_words_used', []))
        
        # Count algorithm reasoning
        algo_count = sum(1 for v in validations if v and v.get('algorithm_reasoning_present'))
        
        print(f"\n📊 OVERALL:")
        print(f"   Average Confidence: {avg_confidence:.0%}")
        print(f"   Learnings Applied: {sum(1 for v in validations if v and v.get('learnings_applied'))}/{len(validations)}")
        
        print(f"\n📈 QUALITY DISTRIBUTION:")
        print(f"   Excellent: {excellent} clips")
        print(f"   Good: {good} clips")
        print(f"   Fair: {fair} clips")
        print(f"   Poor: {poor} clips")
        
        print(f"\n🎯 PATTERN USAGE:")
        print(f"   Unique Patterns: {len(set(all_patterns))}")
        print(f"   Total References: {len(all_patterns)}")
        if all_patterns:
            from collections import Counter
            top_patterns = Counter(all_patterns).most_common(5)
            for pattern, count in top_patterns:
                print(f"      • {pattern}: {count}x")
        
        print(f"\n💪 POWER WORD USAGE:")
        print(f"   Unique Words: {len(set(all_power_words))}")
        print(f"   Total Uses: {len(all_power_words)}")
        if all_power_words:
            from collections import Counter
            top_words = Counter(all_power_words).most_common(5)
            for word, count in top_words:
                print(f"      • {word}: {count}x")
        
        print(f"\n🎯 ALGORITHM REASONING:")
        print(f"   Clips with algo reasoning: {algo_count}/{len(validations)}")
    
    def _get_clips_analyzed_count(self):
        """Get total clips analyzed from Master Learnings"""
        try:
            from master_learnings_v2 import load_master_learnings
            master = load_master_learnings()
            return master.get('metadata', {}).get('total_clips_analyzed', 972)
        except:
            return 972
    
    def _format_clip_for_eval(self, clip: Dict) -> str:
        """
        Format clip for evaluation prompt
        
        Extracts text from segments and formats for AI evaluation
        """
        
        segments = clip.get('segments', [])
        
        if not segments:
            # Fallback: try to get text directly
            fallback = clip.get('text', '') or clip.get('content', '') or ''
            if fallback:
                return f"CLIP TEXT:\n{fallback}"
            else:
                return "ERROR: No transcript available"
        
        # Extract text from segments with timestamps
        clip_text_parts = []
        
        for seg in segments:
            # Handle different segment formats
            text = seg.get('text', '') or seg.get('content', '')
            
            if text:
                start = seg.get('start', 0)
                # Format with timestamp for context
                clip_text_parts.append(f"[{start:.1f}s] {text.strip()}")
        
        # Join all parts
        if clip_text_parts:
            full_text = '\n'.join(clip_text_parts)
        else:
            # Last resort: try raw text extraction
            full_text = ' '.join([
                s.get('text', '') or s.get('content', '') 
                for s in segments 
                if s.get('text') or s.get('content')
            ])
        
        # If STILL empty, return error
        if not full_text or len(full_text.strip()) < 10:
            return f"ERROR: Could not extract text from {len(segments)} segments"
        
        # Format for evaluation
        duration = clip.get('end', 0) - clip.get('start', 0)
        
        formatted = f"""CLIP TRANSCRIPT:
Duration: {duration:.1f} seconds
Segments: {len(segments)}
Start: {clip.get('start', 0):.1f}s
End: {clip.get('end', 0):.1f}s

TRANSCRIPT:
{full_text}
"""
        
        return formatted
    
    async def _transcribe_with_assemblyai(self, video_path: Path) -> List[Dict]:
        """Try AssemblyAI transcription (simplified, matches official docs)"""
        
        try:
            import assemblyai as aai
        except ImportError:
            return None
        
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            return None
        
        aai.settings.api_key = api_key
        
        # Extract audio
        print(f"   🎵 Extracting audio from video...")
        audio_path = await self._extract_audio(video_path)
        
        if not audio_path:
            return None
        
        print(f"   ✅ Audio extracted: {audio_path.name}")
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        print(f"   📦 Audio file size: {file_size_mb:.1f} MB")
        
        print(f"   📤 Uploading to AssemblyAI...")
        print(f"   🎙️  Transcribing (this may take 3-7 minutes)...")
        
        try:
            # SIMPLE CONFIG (matches AssemblyAI official docs)
            config = aai.TranscriptionConfig(
                language_code="de"  # German only, no speaker labels
            )
            
            # Create transcriber and transcribe (synchronous)
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(str(audio_path), config=config)
            
            # Check for errors
            if transcript.status == aai.TranscriptStatus.error:
                print(f"   ❌ Transcription error: {transcript.error}")
                audio_path.unlink()
                return None
            
            print(f"   ✅ Transcription complete!")
            
            # Convert to segments using words
            segments = []
            
            if transcript.words and len(transcript.words) > 0:
                print(f"   🔧 Creating segments from {len(transcript.words)} words...")
                
                current_segment = None
                
                for word in transcript.words:
                    if not current_segment:
                        current_segment = {
                            'start': word.start / 1000.0,
                            'end': word.end / 1000.0,
                            'text': word.text,
                            'confidence': getattr(word, 'confidence', 1.0)
                        }
                    else:
                        time_gap = (word.start / 1000.0) - current_segment['end']
                        segment_duration = current_segment['end'] - current_segment['start']
                        
                        # New segment if gap > 1s or segment > 15s
                        if time_gap > 1.0 or segment_duration > 15:
                            segments.append(current_segment)
                            current_segment = {
                                'start': word.start / 1000.0,
                                'end': word.end / 1000.0,
                                'text': word.text,
                                'confidence': getattr(word, 'confidence', 1.0)
                            }
                        else:
                            current_segment['end'] = word.end / 1000.0
                            current_segment['text'] += ' ' + word.text
                
                if current_segment:
                    segments.append(current_segment)
            
            else:
                # Fallback: use transcript.text and split by sentences
                print(f"   ⚠️  No words available, using text splitting...")
                text = transcript.text
                sentences = text.split('. ')
                duration = transcript.audio_duration / 1000.0 if hasattr(transcript, 'audio_duration') else 1800
                time_per_sentence = duration / len(sentences) if sentences else 10
                
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        segments.append({
                            'start': i * time_per_sentence,
                            'end': (i + 1) * time_per_sentence,
                            'text': sentence.strip(),
                            'confidence': 1.0
                        })
            
            print(f"   ✅ Created {len(segments)} segments")
            
            # Cleanup audio file
            try:
                audio_path.unlink()
                print(f"   🗑️  Cleaned up audio file")
            except:
                pass
            
            return segments
        
        except Exception as e:
            print(f"   ❌ AssemblyAI error: {str(e)}")
            try:
                if audio_path and audio_path.exists():
                    audio_path.unlink()
            except:
                pass
            return None
    
    async def _extract_audio(self, video_path: Path) -> Optional[Path]:
        """
        Extract audio from video using moviepy
        
        Returns MP3 file (compressed) for faster AssemblyAI upload
        """
        
        try:
            # Try moviepy 2.x import first
            try:
                from moviepy import VideoFileClip
            except ImportError:
                # Fallback to moviepy 1.x
                from moviepy.editor import VideoFileClip
        except ImportError:
            print("   ❌ moviepy not installed!")
            print("   💡 Install: pip install moviepy")
            return None
        
        # Output path (MP3 for smaller file size)
        audio_path = video_path.parent / f"{video_path.stem}_audio.mp3"
        
        try:
            # Load video
            print(f"   📹 Loading video...")
            video = VideoFileClip(str(video_path))
            
            # Check if video has audio
            if not video.audio:
                print(f"   ❌ Video has no audio track!")
                video.close()
                return None
            
            # Extract and save audio (compressed for faster upload)
            print(f"   🎵 Extracting audio track (MP3, compressed)...")
            video.audio.write_audiofile(
                str(audio_path),
                fps=16000,          # 16kHz sampling rate
                bitrate='64k',      # Low bitrate (speech quality sufficient)
                codec='libmp3lame', # MP3 codec
                logger=None         # Suppress output (no verbose in moviepy 2.x)
            )
            
            # Close video
            video.close()
            
            return audio_path
        
        except Exception as e:
            print(f"   ❌ Audio extraction error: {str(e)[:100]}")
            return None
    
    async def coarse_viral_scan(self, segments: List[Dict], story_context: Dict) -> List[Dict]:
        """
        STAGE 0: Principle-based smart scan with pre-scoring
        Uses fast AI to identify and score ~40 candidate moments, returns top 20
        """
        
        if not self.ensemble or not self.consensus:
            return []
        
        # Format story context
        story_text = ""
        if story_context:
            storylines = story_context.get('storylines', [])
            if storylines:
                story_text = f"Storylines: {len(storylines)} identified\n"
                for sl in storylines[:3]:
                    story_text += f"- {sl.get('topic', 'Unknown')}\n"
        
        # Format segments for prompt
        segment_text = self._format_segments_for_prompt(segments[:200])  # Limit for speed
        duration = segments[-1]['end'] if segments else 0
        
        # PRINCIPLES CONTEXT
        PRINCIPLES_CONTEXT = """
You evaluate viral potential using these PRINCIPLES (not rigid rules):

1. COMPLETENESS for what it IS
   - Story? Needs setup + payoff (duration varies)
   - Insight? Needs context + lesson (can be short or long)
   - Rant? Needs buildup + climax (energy matters, not length)
   → NOT: "Must be 30-60 seconds"

2. NATURAL BOUNDARIES
   - Starts/ends at pauses, topic shifts, emotional changes
   - Respects speaker's natural rhythm
   → NOT: "Cut every 30 seconds"

3. EMOTIONAL INTENSITY
   - Hooks attention (how varies: stage vs podcast vs conversation)
   - Maintains energy (different for each format)
   - Creates impact (context-dependent)
   → NOT: "Must have power words in first 3s"

4. PATTERN INTERRUPTS
   - Breaks expectations, surprises viewer
   - Creates curiosity, reveals insights
   → NOT: "Pattern interrupt every 7 seconds"

5. FORMAT FLEXIBILITY
   - Stage performance? Long-form energy can work
   - Podcast? Natural conversation flow
   - Live talk? Audience reactions add value
   → NOT: "Must be tightly edited"

6. CONTEXT AWARENESS
   - Who is speaker? (Tony Robbins ≠ Gary Vee ≠ Podcast)
   - What is setting? (Stage ≠ Office ≠ Interview)
   - Who is audience? (Corporate ≠ Fitness ≠ General)
   → NOT: "One size fits all"

CRITICAL: These are PRINCIPLES, not checklists. A moment doesn't need all 6.
Evaluate holistically based on what makes THIS moment viral in THIS context.
"""
        
        prompt = f"""
{PRINCIPLES_CONTEXT}

TASK: Find viral potential moments in this transcript

Transcript ({len(segments)} segments, {duration:.0f}s):
{segment_text}

STORY CONTEXT:
{story_text}

YOUR PROCESS:
1. Scan for moments with viral potential using the 6 PRINCIPLES above
2. Look for ~40 candidate moments
3. For EACH moment, score 0-100 for viral potential:
   - Consider: completeness, natural boundaries, emotional intensity
   - Consider: pattern interrupts, format fit, context appropriateness
   - Think: "Would this work as a standalone viral clip?"

4. Return ONLY the top 20 moments (highest scores)

RESPONSE FORMAT (JSON):
{{
  "moments": [
    {{
      "start_time": 123.5,
      "end_time": 187.3,
      "viral_score": 85,
      "reason": "Complete story with surprise twist, natural emotional arc, strong stage energy"
    }},
    ...
  ]
}}

CRITICAL: 
- Score based on PRINCIPLES, not rigid rules
- Context matters: what works for THIS speaker/format?
- Return ONLY top 20 moments (best viral potential)
"""
        
        # Use fast AI (Haiku-level via consensus with fast model)
        try:
            # Use a fast model for coarse scan
            result = await self.ensemble.call_ai(
                ai_name='sonnet',  # Fast but smart enough
                prompt=prompt,
                system="You are a viral content scout. Evaluate moments using principles, not rigid rules.",
                max_tokens=8000,
                temperature=0.8
            )
            
            if not result.get('success'):
                print(f"   ⚠️  Coarse scan failed: {result.get('error', 'Unknown error')}")
                return []
            
            content = result.get('content', '')
            response_data = self._parse_json_response(content)
            
            # Handle different response formats
            if isinstance(response_data, dict):
                moments_data = response_data.get('moments', [])
            elif isinstance(response_data, list):
                moments_data = response_data
            else:
                moments_data = []
            
            # Log scoring results
            print(f"\n📊 COARSE SCAN RESULTS:")
            print(f"   Found and scored {len(moments_data)} moments")
            
            # Show top 5 for visibility
            sorted_moments = sorted(moments_data, key=lambda x: x.get('viral_score', 0), reverse=True)
            for i, m in enumerate(sorted_moments[:5], 1):
                score = m.get('viral_score', 0)
                reason = m.get('reason', 'No reason provided')[:60]
                print(f"   {i}. Score: {score}/100 - {reason}...")
            
            # Convert to seeds format
            valid_seeds = []
            for m in sorted_moments:
                # Handle different field names
                start = m.get('start_time') or m.get('start', 0)
                end = m.get('end_time') or m.get('end', 0)
                viral_score = m.get('viral_score', 0)
                reason = m.get('reason', m.get('brief_note', ''))
                signal_type = m.get('signal_type', 'viral_moment')
                
                if start is not None and end is not None:
                    try:
                        start = float(start)
                        end = float(end)
                        viral_score = int(viral_score) if viral_score else 0
                        
                        if end > start:
                            valid_seeds.append({
                                'start': start,
                                'end': end,
                                'viral_score': viral_score,
                                'reason': reason,
                                'signal_type': signal_type
                            })
                    except (ValueError, TypeError) as e:
                        continue
            
            print(f"\n   🌱 Returning top {len(valid_seeds)} pre-scored seeds")
            return valid_seeds
            
        except Exception as e:
            print(f"   ⚠️  Coarse scan error: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()[:200]}")
            return []
    
    async def refine_moment_boundaries(self, seed: Dict, segments: List[Dict], 
                                      story_context: Dict) -> Dict:
        """
        STAGE 1: Find optimal boundaries for a seed
        Simplified version (no self-critique) for speed
        Self-correction happens in Stage 2 quality filter
        """
        
        if not self.ensemble or not self.consensus:
            return None
        
        # Get extended context around seed
        seed_start = float(seed.get('start', 0))
        seed_end = float(seed.get('end', 0))
        
        context_start = max(0, seed_start - 30)
        max_end = max(s.get('end', 0) for s in segments) if segments else seed_end
        context_end = min(max_end, seed_end + 60)
        
        context_segments = [
            s for s in segments 
            if s.get('start', 0) >= context_start and s.get('end', 0) <= context_end
        ]
        
        # Format story context
        story_text = ""
        if story_context:
            storylines = story_context.get('storylines', [])
            if storylines:
                story_text = f"Storylines: {len(storylines)} identified\n"
        
        prompt = f"""
A potential viral moment was detected:
- Rough timerange: {seed_start:.1f}s - {seed_end:.1f}s
- Signal type: {seed.get('signal_type', 'unknown')}
- Why flagged: {seed.get('brief_note', 'potential viral moment')}

TASK: Find OPTIMAL boundaries for THIS specific moment.

🎯 ADAPTIVE ANALYSIS (not rigid rules):

STEP 1: What TYPE is this?
Identify what this moment actually IS:
- Paradox statement? Story? Teaching? Q&A? Joke? Quote?
- Emotional moment? Demonstration? Insight? Transformation?
- Something else entirely?

STEP 2: Find natural boundaries for THIS type
- Where does THIS naturally BEGIN? (context needed?)
- Where does it COMPLETE? (satisfying conclusion?)
- What's ESSENTIAL vs FILLER?

STEP 3: Validate completeness
✅ COMPLETE if:
- Has necessary context (viewer understands)
- Has satisfying conclusion (feels finished)
- Works standalone (no outside info needed)
- No filler (every second serves purpose)

Return optimal boundaries that make THIS moment complete.

📊 RETURN JSON:
{{
  "moment_type": "specific type of this moment",
  "optimal_start": <timestamp>,
  "optimal_end": <timestamp>,
  "completeness_score": 0-100,
  "reasoning": "why these boundaries work",
  "key_elements": ["hook at Xs", "payoff at Ys"]
}}

CONTEXT SEGMENTS:
{self._format_segments_for_prompt(context_segments)}

STORY CONTEXT:
{story_text}

Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral content analyst. Find optimal boundaries that make moments complete and satisfying.",
                max_tokens=4000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict) or 'optimal_start' not in analysis:
                # Fallback to seed boundaries
                return self._create_refined_moment({
                    'moment_type': seed.get('signal_type', 'unknown'),
                    'optimal_start': seed_start,
                    'optimal_end': seed_end,
                    'completeness_score': 50,
                    'reasoning': 'Used seed boundaries (parsing failed)',
                    'key_elements': []
                }, seed, segments)
            
            return self._create_refined_moment(analysis, seed, segments)
            
        except Exception as e:
            print(f"      ⚠️  Refinement error: {e}")
            # Return seed as fallback
            return self._create_refined_moment({
                'moment_type': seed.get('signal_type', 'unknown'),
                'optimal_start': seed_start,
                'optimal_end': seed_end,
                'completeness_score': 50,
                'reasoning': f'Error: {e}',
                'key_elements': []
            }, seed, segments)
    
    def _create_refinement_batches(self, seeds: List[Dict], batch_size: int = 5) -> List[List[Dict]]:
        """Group seeds into batches for efficient processing"""
        batches = []
        for i in range(0, len(seeds), batch_size):
            batch = seeds[i:i + batch_size]
            batches.append(batch)
        return batches
    
    def _find_segment_index(self, timestamp: float) -> int:
        """Find segment index for a given timestamp"""
        for i, seg in enumerate(self.segments):
            if seg.get('start', 0) <= timestamp <= seg.get('end', 0):
                return i
            if seg.get('start', 0) > timestamp:
                return max(0, i - 1)
        return len(self.segments) - 1
    
    async def _refine_moments_parallel(self, seeds: List[Dict], segments: List[Dict], 
                                       story_context: Dict) -> List[Dict]:
        """
        Refine moments in batches using principle-based approach
        Processes multiple moments together in single AI call (cost-efficient)
        """
        if not self.ensemble or not self.consensus:
            return []
        
        # Create batches
        batches = self._create_refinement_batches(seeds, batch_size=5)
        print(f"   Created {len(batches)} batches")
        
        # Process batches sequentially
        all_refined = []
        
        for batch_idx, batch in enumerate(batches, 1):
            print(f"\n   Batch {batch_idx}/{len(batches)}: Refining {len(batch)} moments...")
            
            try:
                refined_batch = await self._refine_batch(
                    batch=batch,
                    segments=segments,
                    story_context=story_context
                )
                all_refined.extend(refined_batch)
                print(f"      ✅ Refined {len(refined_batch)} moments")
            except Exception as e:
                print(f"      ⚠️ Batch {batch_idx} failed: {e}")
                # Fallback: use original seeds
                fallback = self._seeds_to_moments_fallback(batch, segments)
                all_refined.extend(fallback)
                continue
        
        return all_refined
    
    async def _refine_batch(self, batch: List[Dict], segments: List[Dict], 
                           story_context: Dict) -> List[Dict]:
        """Refine a batch of moments together (principle-based) - Single AI call refines 4-5 moments"""
        
        PRINCIPLES_CONTEXT = """
You evaluate viral potential using these PRINCIPLES (not rigid rules):

1. COMPLETENESS for what it IS
   - Story? Needs setup + payoff (duration varies)
   - Insight? Needs context + lesson (can be short or long)
   - Rant? Needs buildup + climax (energy matters, not length)
   → NOT: "Must be 30-60 seconds"

2. NATURAL BOUNDARIES
   - Starts/ends at pauses, topic shifts, emotional changes
   - Respects speaker's natural rhythm
   → NOT: "Cut every 30 seconds"

3. EMOTIONAL INTENSITY
   - Hooks attention (how varies: stage vs podcast vs conversation)
   - Maintains energy (different for each format)
   - Creates impact (context-dependent)
   → NOT: "Must have power words in first 3s"

4. PATTERN INTERRUPTS
   - Breaks expectations, surprises viewer
   - Creates curiosity, reveals insights
   → NOT: "Pattern interrupt every 7 seconds"

5. FORMAT FLEXIBILITY
   - Stage performance? Long-form energy can work
   - Podcast? Natural conversation flow
   - Live talk? Audience reactions add value
   → NOT: "Must be tightly edited"

6. CONTEXT AWARENESS
   - Who is speaker? (Tony Robbins ≠ Gary Vee ≠ Podcast)
   - What is setting? (Stage ≠ Office ≠ Interview)
   - Who is audience? (Corporate ≠ Fitness ≠ General)
   → NOT: "One size fits all"

CRITICAL: These are PRINCIPLES, not checklists. A moment doesn't need all 6.
Evaluate holistically based on what makes THIS moment viral in THIS context.
"""
        
        # Build batch context
        batch_context = []
        for i, seed in enumerate(batch, 1):
            seed_start = float(seed.get('start', 0))
            seed_end = float(seed.get('end', 0))
            
            context_start = max(0, seed_start - 30)
            max_end = max(s.get('end', 0) for s in segments) if segments else seed_end
            context_end = min(max_end, seed_end + 60)
            
            context_segments = [
                s for s in segments
                if s.get('start', 0) >= context_start and s.get('end', 0) <= context_end
            ]
            
            text = ' '.join([s.get('text', '') for s in context_segments[:20]])
            
            batch_context.append({
                'moment_id': i,
                'seed_start': seed_start,
                'seed_end': seed_end,
                'viral_score': seed.get('viral_score', 0),
                'signal_type': seed.get('signal_type', 'unknown'),
                'reason': seed.get('reason', seed.get('brief_note', '')),
                'context_text': text[:500],
                'full_segments': context_segments
            })
        
        story_text = ""
        if story_context:
            storylines = story_context.get('storylines', [])
            if storylines:
                story_text = f"Storylines: {len(storylines)} identified\n"
        
        batch_prompt = ""
        for ctx in batch_context:
            batch_prompt += f"""
MOMENT {ctx['moment_id']}:
Seed: {ctx['seed_start']:.1f}s - {ctx['seed_end']:.1f}s (Score: {ctx['viral_score']}/100)
Signal: {ctx['signal_type']}
Why flagged: {ctx['reason']}
Context: "{ctx['context_text']}..."

"""
        
        prompt = f"""
{PRINCIPLES_CONTEXT}

TASK: Refine boundaries for {len(batch)} moments using PRINCIPLES

For each moment below, refine the start/end times to create the BEST viral clip:

{batch_prompt}

YOUR PROCESS for EACH moment:

1. COMPLETENESS: Find natural start/end for complete thought
2. NATURAL BOUNDARIES: Cut at organic points (pauses, transitions, shifts)
3. FORMAT AWARENESS: Respect original format (stage/podcast/live)
4. CONTEXT: Consider speaker style (verbose/concise/emotional)

STORY CONTEXT:
{story_text}

RESPONSE FORMAT (JSON):
{{
  "refined_moments": [
    {{
      "moment_id": 1,
      "optimal_start": 123.5,
      "optimal_end": 187.3,
      "moment_type": "story_with_twist",
      "completeness_score": 85,
      "reasoning": "Extended to include complete story arc with payoff"
    }}
  ]
}}

Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral content analyst. Refine boundaries using principles, not rigid rules.",
                max_tokens=6000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                raise ValueError("Invalid response format")
            
            refined_moments_data = analysis.get('refined_moments', [])
            if not refined_moments_data:
                raise ValueError("No refined moments in response")
            
            refined_moments = []
            for refined in refined_moments_data:
                moment_id = refined.get('moment_id')
                if not moment_id or moment_id < 1 or moment_id > len(batch):
                    continue
                
                original_seed = batch[moment_id - 1]
                optimal_start = float(refined.get('optimal_start', original_seed.get('start', 0)))
                optimal_end = float(refined.get('optimal_end', original_seed.get('end', 0)))
                
                if optimal_end <= optimal_start:
                    optimal_start = float(original_seed.get('start', 0))
                    optimal_end = float(original_seed.get('end', 0))
                
                moment_segments = [
                    s for s in segments
                    if s.get('start', 0) >= optimal_start and s.get('end', 0) <= optimal_end
                ]
                
                hook_phrase = str(moment_segments[0].get('text', ''))[:100] if moment_segments else ""
                
                refined_moments.append({
                    'start': optimal_start,
                    'end': optimal_end,
                    'duration': optimal_end - optimal_start,
                    'moment_type': str(refined.get('moment_type', original_seed.get('signal_type', 'unknown'))),
                    'hook_phrase': hook_phrase,
                    'pattern': str(refined.get('moment_type', original_seed.get('signal_type', 'unknown'))),
                    'completeness_score': refined.get('completeness_score', 0),
                    'segments': moment_segments,
                    'viral_reasoning': str(refined.get('reasoning', '')),
                    'viral_score': original_seed.get('viral_score', 0),
                    'refinement_reason': refined.get('reasoning', ''),
                    'seed_info': {
                        'original_start': original_seed.get('start', 0),
                        'original_end': original_seed.get('end', 0)
                    }
                })
            
            return refined_moments
            
        except Exception as e:
            print(f"      ⚠️ Batch refinement failed: {e}")
            return self._seeds_to_moments_fallback(batch, segments)
    
    def _seeds_to_moments_fallback(self, seeds: List[Dict], segments: List[Dict]) -> List[Dict]:
        """Fallback if batch refinement fails"""
        moments = []
        for seed in seeds:
            start = float(seed.get('start', 0))
            end = float(seed.get('end', 0))
            moment_segments = [
                s for s in segments
                if s.get('start', 0) >= start and s.get('end', 0) <= end
            ]
            hook_phrase = str(moment_segments[0].get('text', ''))[:100] if moment_segments else ""
            
            moments.append({
                'start': start,
                'end': end,
                'duration': end - start,
                'segments': moment_segments,
                'viral_score': seed.get('viral_score', 0),
                'hook_phrase': hook_phrase,
                'moment_type': seed.get('signal_type', 'unknown'),
                'pattern': seed.get('signal_type', 'unknown')
            })
        return moments
    
    def _needs_restructure(self, moment: Dict) -> tuple:
        """
        Principle-based check: Does this moment need restructuring?
        
        Uses smart heuristics based on principles (not rigid rules)
        
        Returns:
            (needs_restructure: bool, issues: list, severity: float)
        """
        segments = moment.get('segments', [])
        if not segments:
            return False, [], 0.0
        
        issues = []
        severity_scores = []
        
        # Get full text
        full_text = ' '.join([s.get('text', '') for s in segments])
        word_count = len(full_text.split())
        duration = moment.get('duration', 0)
        
        if word_count == 0 or duration == 0:
            return False, [], 0.0
        
        # Principle: FLOW
        # Does pacing hurt understanding?
        filler_words = ['äh', 'ähm', 'also', 'ja also', 'sozusagen', 'irgendwie']
        filler_count = sum(full_text.lower().count(f) for f in filler_words)
        filler_density = filler_count / max(word_count, 1)
        
        if filler_density > 0.3:  # 30%+ of speech is filler
            issues.append("high_filler_density")
            severity_scores.append(filler_density)
        
        # Principle: CLARITY
        # Does repetition add (for emphasis) or hurt (rambling)?
        words = full_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Check for excessive repetition (not for emphasis)
        repeated_words = [w for w, count in word_freq.items() if count > 3]
        if len(repeated_words) > 2:
            issues.append("excessive_repetition")
            severity_scores.append(len(repeated_words) / 10)
        
        # Principle: COMPLETENESS
        # Does it ramble and break the arc?
        if duration > 90 and word_count / duration < 2:  # Very slow pacing
            issues.append("slow_rambling")
            severity_scores.append(0.6)
        
        # Calculate overall severity
        avg_severity = sum(severity_scores) / len(severity_scores) if severity_scores else 0.0
        
        # Need restructure if issues exist and severity is meaningful
        needs_restructure = len(issues) > 0 and avg_severity > 0.3
        
        return needs_restructure, issues, avg_severity
    
    async def _conditional_restructure(self, moments: List[Dict]) -> List[Dict]:
        """
        Conditionally restructure moments based on principles
        
        Only processes moments that actually need improvement
        Batches restructuring for efficiency
        
        Args:
            moments: List of moments from Stage 1.75
            
        Returns:
            List of moments (restructured if needed, original if not)
        """
        print(f"\n📍 STAGE 2: Principle-Based Conditional Restructure")
        print(f"   Analyzing {len(moments)} moments...")
        
        # Pre-check which moments need restructuring
        needs_restructure = []
        no_restructure = []
        
        for i, moment in enumerate(moments):
            need, issues, severity = self._needs_restructure(moment)
            
            if need:
                moment['restructure_issues'] = issues
                moment['severity'] = severity
                needs_restructure.append((i, moment))
                print(f"      Moment {i+1}: Needs restructure (issues: {', '.join(issues)}, severity: {severity:.2f})")
            else:
                no_restructure.append((i, moment))
        
        print(f"\n   ✅ No restructure needed: {len(no_restructure)} moments")
        print(f"   🔧 Needs restructure: {len(needs_restructure)} moments")
        
        if len(needs_restructure) == 0:
            print(f"   💎 All moments are clean!")
            return moments
        
        # Batch restructure moments that need it
        restructured = await self._batch_restructure(needs_restructure)
        
        # Merge results back
        result = moments.copy()
        for original_idx, restructured_moment in restructured:
            result[original_idx] = restructured_moment
        
        print(f"\n   💎 Restructured: {len(restructured)} moments")
        
        return result
    
    async def _batch_restructure(self, moments_to_restructure: List[tuple]) -> List[tuple]:
        """
        Restructure moments in batches (principle-based)
        
        Args:
            moments_to_restructure: List of (index, moment) tuples
            
        Returns:
            List of (index, restructured_moment) tuples
        """
        if not self.ensemble or not self.consensus:
            # Fallback: return originals
            return [(idx, moment) for idx, moment in moments_to_restructure]
        
        # Use same PRINCIPLES_CONTEXT
        PRINCIPLES_CONTEXT = """
You restructure moments using these PRINCIPLES:

1. COMPLETENESS: Maintain the complete arc
   - Keep setup + payoff
   - Remove only what breaks flow
   - Story needs beginning/middle/end

2. CLARITY: Remove noise, keep substance
   - Filler that hurts comprehension? Remove
   - Filler for pacing/emphasis? Keep
   - Repetition for impact? Keep
   - Rambling repetition? Remove

3. CONTEXT: Preserve speaker's style
   - Verbose speaker (Tony Robbins)? Keep some rambling if it adds energy
   - Concise speaker (Gary Vee)? Cut aggressively
   - Conversational? Keep natural flow

4. FORMAT: Respect the medium
   - Podcast? Natural conversation flow, don't over-edit
   - Stage? Keep energy, pauses, audience reactions
   - Interview? Keep back-and-forth

CRITICAL: Fix ONLY what violates these principles. Don't over-process.
"""
        
        # Process in batches of 3
        batch_size = 3
        restructured = []
        
        for batch_start in range(0, len(moments_to_restructure), batch_size):
            batch = moments_to_restructure[batch_start:batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            total_batches = (len(moments_to_restructure) + batch_size - 1) // batch_size
            
            print(f"\n   📦 Batch {batch_num}/{total_batches}: Restructuring {len(batch)} moments...")
            
            # Build prompt
            prompt = f"""
{PRINCIPLES_CONTEXT}

TASK: Restructure {len(batch)} moments that have issues

"""
            
            for i, (orig_idx, moment) in enumerate(batch, 1):
                text = ' '.join([s.get('text', '') for s in moment.get('segments', [])])
                issues = moment.get('restructure_issues', [])
                severity = moment.get('severity', 0)
                duration = moment.get('duration', 0)
                
                prompt += f"""
MOMENT {i}:
Issues: {', '.join(issues)} (severity: {severity:.2f})
Duration: {duration:.1f}s
Text: "{text[:600]}..."

"""
            
            prompt += """
YOUR PROCESS for EACH moment:

1. Identify what violates principles (based on issues)
2. Remove/fix ONLY those violations
3. Preserve speaker's style and format
4. Keep the complete arc intact

RESPONSE FORMAT (JSON):
{
  "restructured": [
    {
      "moment_id": 1,
      "keep_segments": [0, 1, 3, 5],  # Indices of segments to keep
      "reasoning": "Removed excessive filler while preserving pacing"
    },
    ...
  ]
}

Return segment indices to KEEP (0-indexed). We'll rebuild from those.
Return JSON only.
"""
            
            # Call AI
            try:
                result = await self.consensus.single_ai_call(
                    prompt=prompt,
                    model='sonnet',
                    system="You are a viral content editor. Restructure using principles, not rigid rules.",
                    max_tokens=4000,
                    temperature=0.7
                )
                
                # Parse response
                analysis = self._parse_json_response(result)
                
                if not analysis or not isinstance(analysis, dict):
                    raise ValueError("Invalid response format")
                
                restructured_data = analysis.get('restructured', [])
                
                if not restructured_data:
                    raise ValueError("No restructured moments in response")
                
                # Apply restructures
                for item in restructured_data:
                    moment_id = item.get('moment_id')
                    if not moment_id or moment_id < 1 or moment_id > len(batch):
                        continue
                    
                    orig_idx, moment = batch[moment_id - 1]
                    
                    # Rebuild moment with kept segments
                    kept_indices = item.get('keep_segments', [])
                    moment_segments = moment.get('segments', [])
                    
                    if not moment_segments:
                        # Keep original if no segments
                        restructured.append((orig_idx, moment))
                        continue
                    
                    new_segments = [moment_segments[i] for i in kept_indices if 0 <= i < len(moment_segments)]
                    
                    if new_segments:
                        restructured_moment = {
                            'start': new_segments[0].get('start', 0),
                            'end': new_segments[-1].get('end', 0),
                            'duration': new_segments[-1].get('end', 0) - new_segments[0].get('start', 0),
                            'segments': new_segments,
                            'viral_score': moment.get('viral_score', 0),
                            'restructured': True,
                            'restructure_reason': item.get('reasoning', ''),
                            'moment_type': moment.get('moment_type', 'unknown'),
                            'pattern': moment.get('pattern', 'unknown'),
                            'hook_phrase': new_segments[0].get('text', '')[:100] if new_segments else moment.get('hook_phrase', '')
                        }
                        
                        restructured.append((orig_idx, restructured_moment))
                        print(f"      ✅ Moment {moment_id}: Restructured ({len(new_segments)}/{len(moment_segments)} segments kept)")
                    else:
                        # Keep original if restructure failed
                        restructured.append((orig_idx, moment))
                        print(f"      ⚠️ Moment {moment_id}: Restructure failed, keeping original")
            
            except Exception as e:
                print(f"      ⚠️ Batch restructure failed: {e}")
                # Keep originals
                for orig_idx, moment in batch:
                    restructured.append((orig_idx, moment))
        
        return restructured
    
    def _detect_moment_type(self, text: str) -> str:
        """Detect moment type from text patterns"""
        text_lower = text.lower()
        
        # Story indicators
        story_patterns = ['horde kinder', 'es war einmal', 'ich erzähle', 'stell dir vor', 'geschichte', 'passiert']
        if any(p in text_lower for p in story_patterns):
            return 'story'
        
        # Parable indicators  
        parable_patterns = ['alter mann', 'zen meister', 'rabbi', 'meister', 'schüler', 'lehrer']
        if any(p in text_lower for p in parable_patterns):
            return 'parable'
        
        # Insight indicators
        insight_patterns = ['das problem', 'der grund', 'deshalb', 'weil', 'das liegt daran', 'das bedeutet']
        if any(p in text_lower for p in insight_patterns):
            return 'insight'
        
        # Default: rant
        return 'rant'
    
    async def _viral_composition(self, moments: List[Dict], segments: List[Dict]) -> List[Dict]:
        """
        Stage 2.5: Comprehensive Viral Composition (Multi-AI)
        
        PRINCIPLE: Holistic optimization, not sequential pipeline
        - AI analyzes each moment completely
        - Decides what optimizations are needed
        - Applies them intelligently
        - Hook extraction only if beneficial
        - Cuts only where wasteful
        - Timing only when appropriate
        - Structure only if clear
        
        Uses 2-3 AI ensemble for creative decisions
        
        Args:
            moments: Refined moments from Stage 2
            segments: All video segments (for hook extraction)
            
        Returns:
            Viral-ready composed moments
        """
        if not self.ensemble or not self.consensus:
            return moments
        
        print(f"\n📍 STAGE 2.5: VIRAL COMPOSITION (Comprehensive Multi-AI)")
        print(f"   Using Brain: v{self.VIRAL_PRINCIPLES.get('version', 'unknown')}")
        print(f"   Principle: Holistic optimization, not forced pipeline")
        print(f"   Strategy: AI decides what each moment needs (using learned principles)")
        
        # Use latest VIRAL_PRINCIPLES (Master Brain - self-learning!)
        PRINCIPLES = {
            'duration': self.VIRAL_PRINCIPLES.get('duration_principles', {}),
            'hooks': self.VIRAL_PRINCIPLES.get('hook_principles', {}),
            'cuts': self.VIRAL_PRINCIPLES.get('cutting_principles', {}),
            'timing': self.VIRAL_PRINCIPLES.get('timing_principles', {}),
            'structure': self.VIRAL_PRINCIPLES.get('structure_principles', {})
        }
        
        # Extract potential hooks ONCE for entire video
        print(f"\n   🔍 Analyzing video for potential hooks...")
        video_hooks = await self._extract_video_hooks(segments, PRINCIPLES.get('hooks', {}))
        print(f"   ✅ Found {len(video_hooks)} potential hooks")
        
        composed_moments = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n   Composing moment {i}/{len(moments)}...")
            
            # Get comprehensive optimization from Multi-AI ensemble
            composed = await self._compose_moment_with_ensemble(
                moment=moment,
                video_hooks=video_hooks,
                principles=PRINCIPLES
            )
            
            # Show what was done
            optimizations = composed.get('optimizations_applied', [])
            if optimizations:
                print(f"      ✨ Applied: {', '.join(optimizations)}")
                if 'hook_added' in composed:
                    hook_text = composed['hook_added']
                    if isinstance(hook_text, str):
                        print(f"         • Hook: '{hook_text[:40]}...'")
                if 'time_saved' in composed:
                    print(f"         • Cuts: {composed['time_saved']:.1f}s removed")
                if 'pauses_added' in composed:
                    print(f"         • Timing: {composed['pauses_added']} strategic pauses")
            else:
                print(f"      ✅ Already optimal - no changes needed")
            
            composed_moments.append(composed)
        
        print(f"\n   💎 Viral Composition Complete")
        return composed_moments
    
    async def _extract_video_hooks(self, segments: List[Dict], hook_principles: Dict) -> List[Dict]:
        """
        Extract potential hooks from entire video ONCE
        (Not per moment - efficiency!)
        """
        if not self.consensus:
            return []
        
        full_text = ' '.join([s.get('text', '') for s in segments[:100]])  # First ~5 min
        
        methods = hook_principles.get('methods', [])
        examples = hook_principles.get('examples_from_data', [])
        
        # Build lists before f-string (can't use chr(10) or backslashes in f-string expressions)
        methods_list = '\n'.join(['- ' + str(m) for m in methods])
        examples_list = '\n'.join(['- ' + str(ex) for ex in examples[:3]])
        
        prompt = f"""
PRINCIPLE: {hook_principles.get('principle', 'Hook must stop the scroll within 3 seconds')}

Hook types (from proven data):
{methods_list}

VIDEO CONTENT (excerpt):
"{full_text[:1500]}..."

YOUR TASK:
Find 5-10 strongest potential hooks in this video.
Hook = something that could be PRE-PENDED to another moment.

Examples from 6M+ view clips:
{examples_list}

RESPONSE (JSON):
{{
  "hooks": [
    {{
      "text": "Arbeite niemals für Geld",
      "start": 123.5,
      "end": 125.8,
      "strength": 95,
      "theme": "work_money",
      "why_powerful": "Bold contrarian statement"
    }}
  ]
}}

Focus on QUALITY over quantity. 5 great hooks > 20 mediocre ones.
Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral content expert. Extract the strongest hooks from this transcript.",
                max_tokens=3000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                return []
            
            hooks = analysis.get('hooks', [])
            
            # Add segment data
            for hook in hooks:
                start_time = float(hook.get('start', 0))
                end_time = float(hook.get('end', 0))
                hook['segments'] = [
                    s for s in segments
                    if start_time <= s.get('start', 0) <= end_time
                ]
                hook['duration'] = end_time - start_time
            
            return hooks
        except Exception as e:
            print(f"      ⚠️ Hook extraction failed: {e}")
            return []
    
    async def _compose_moment_with_ensemble(self, moment: Dict, video_hooks: List[Dict], principles: Dict) -> Dict:
        """
        Use 2-3 AI ensemble for comprehensive composition
        """
        if not self.consensus:
            return moment
        
        # Build comprehensive prompt with ALL principles
        segments = moment.get('segments', [])
        if not segments:
            return moment
        
        moment_text = ' '.join([s.get('text', '') for s in segments])
        
        duration_principle = principles.get('duration', {})
        hooks_principle = principles.get('hooks', {})
        cuts_principle = principles.get('cuts', {})
        timing_principle = principles.get('timing', {})
        structure_principle = principles.get('structure', {})
        
        # Build text lists before f-string (can't use chr(10) or backslashes in f-string expressions)
        duration_observations = '\n'.join(duration_principle.get('observations', []))
        hooks_methods = '\n'.join(hooks_principle.get('methods', []))
        cuts_what_to_cut = '\n'.join(cuts_principle.get('what_to_cut', []))
        cuts_what_to_keep = '\n'.join(cuts_principle.get('what_to_preserve', cuts_principle.get('what_to_keep', [])))
        timing_when_to_pause = '\n'.join(timing_principle.get('when_to_pause', []))
        timing_when_not_to_pause = '\n'.join(timing_principle.get('when_not_to_pause', timing_principle.get('when_NOT_to_pause', [])))
        hooks_list = '\n'.join([f"- \"{h.get('text', '')[:60]}\" (strength: {h.get('strength', 0)})" for h in video_hooks[:5]])
        
        prompt = f"""
You are a viral video composer. Optimize this moment HOLISTICALLY.

MOMENT TO COMPOSE:
Duration: {moment.get('duration', 0):.1f}s
Text: "{moment_text[:800]}"

AVAILABLE PRINCIPLES (from Master Brain - Self-Learning System):

1. DURATION:
{duration_principle.get('core', duration_principle.get('principle', 'Balance completeness with engagement'))}
Observations: {duration_observations}
Content Type Guidance: {json.dumps(duration_principle.get('content_type_guidance', {}), indent=2, ensure_ascii=False)}

2. HOOKS:
{hooks_principle.get('core', hooks_principle.get('principle', 'Hook must stop the scroll'))}
Methods: {hooks_methods}
Extraction: {json.dumps(hooks_principle.get('extraction', {}), indent=2, ensure_ascii=False)}

3. CUTS:
{cuts_principle.get('core', cuts_principle.get('principle', 'Every word must earn its place'))}
What to cut: {cuts_what_to_cut}
What to keep: {cuts_what_to_keep}

4. TIMING:
{timing_principle.get('core', timing_principle.get('principle', 'Strategic silence creates impact'))}
When to pause: {timing_when_to_pause}
When NOT to pause: {timing_when_not_to_pause}

5. STRUCTURE:
{structure_principle.get('core', structure_principle.get('principle', 'Structure adapts to content type'))}
Viable Patterns: {json.dumps(structure_principle.get('viable_patterns', structure_principle.get('patterns_by_type', {})), indent=2, ensure_ascii=False)}
Anti-Pattern: {structure_principle.get('anti_pattern', 'Forcing all content into one template')}

AVAILABLE HOOKS (from video):
{hooks_list}

YOUR TASK:
Analyze this moment and decide WHAT optimizations would help:

1. Does it need a hook? (only if weak opening)
2. Does it need micro-cuts? (only if wasteful)
3. Does it need timing pauses? (only if appropriate)
4. Does it have clear payoff? (structure)
5. Is duration optimal? (completeness vs engagement)

CRITICAL: Don't force optimizations! 
- If moment is already strong, say so!
- Only optimize what NEEDS it!
- Quality > quantity of changes!

RESPONSE (JSON):
{{
  "needs_optimization": true,
  "analysis": "Why this moment needs/doesn't need work",
  
  "optimizations": {{
    "hook_extraction": {{
      "needed": false,
      "hook_to_use": null,
      "reasoning": "why this hook helps or not needed"
    }},
    
    "micro_cuts": {{
      "needed": false,
      "segments_to_optimize": []
    }},
    
    "timing_pauses": {{
      "needed": false,
      "pauses": []
    }},
    
    "structure_adjustment": {{
      "needed": false,
      "content_type": "story/insight/rant/etc",
      "adjustments": "what to change"
    }}
  }},
  
  "expected_improvement": "How this will increase watchtime/engagement"
}}

Be HONEST. If moment is already good, don't force changes!
Return JSON only.
"""
        
        # Get 2 AI responses (for consensus)
        models = ['sonnet', 'sonnet']  # Use 2 Sonnet calls for cost efficiency
        
        responses = []
        for model in models:
            try:
                response = await self.consensus.single_ai_call(
                    prompt=prompt,
                    model=model,
                    system="You are a viral video composer. Apply principles holistically, not rigidly.",
                    max_tokens=3000,
                    temperature=0.7
                )
                responses.append({
                    'model': model,
                    'response': response
                })
            except Exception as e:
                print(f"         ⚠️ AI call failed ({model}): {e}")
        
        if not responses:
            return moment  # Fallback
        
        # Build consensus
        composed = self._build_composition_consensus(moment, responses, video_hooks)
        
        return composed
    
    def _build_composition_consensus(self, moment: Dict, responses: List[Dict], video_hooks: List[Dict]) -> Dict:
        """
        Build consensus from 2-3 AI responses
        Apply optimizations that MAJORITY agrees on
        """
        import json
        
        try:
            parsed_responses = []
            for r in responses:
                parsed = self._parse_json_response(r['response'])
                if parsed:
                    parsed_responses.append(parsed)
        except Exception as e:
            print(f"         ⚠️ Failed to parse responses: {e}")
            return {
                **moment,
                'optimizations_applied': [],
                'composition_note': 'AI responses failed to parse'
            }
        
        if not parsed_responses:
            return {
                **moment,
                'optimizations_applied': [],
                'composition_note': 'No valid responses'
            }
        
        # Check what optimizations MAJORITY wants
        needs_hook = sum([
            1 for r in parsed_responses 
            if r.get('optimizations', {}).get('hook_extraction', {}).get('needed', False)
        ]) >= len(parsed_responses) / 2
        
        needs_cuts = sum([
            1 for r in parsed_responses 
            if r.get('optimizations', {}).get('micro_cuts', {}).get('needed', False)
        ]) >= len(parsed_responses) / 2
        
        needs_timing = sum([
            1 for r in parsed_responses 
            if r.get('optimizations', {}).get('timing_pauses', {}).get('needed', False)
        ]) >= len(parsed_responses) / 2
        
        # Apply optimizations
        composed = {**moment}
        optimizations_applied = []
        
        # 1. Hook extraction (if majority agrees)
        if needs_hook:
            hook_data = parsed_responses[0].get('optimizations', {}).get('hook_extraction', {})
            hook_text = hook_data.get('hook_to_use')
            if hook_text:
                # Find hook in video_hooks
                matching_hook = next((h for h in video_hooks if hook_text[:30] in h.get('text', '')), None)
                if matching_hook and matching_hook.get('segments'):
                    # Prepend hook
                    composed['segments'] = matching_hook['segments'] + composed.get('segments', [])
                    composed['start'] = matching_hook.get('start', composed.get('start', 0))
                    composed['duration'] = composed.get('end', 0) - matching_hook.get('start', composed.get('start', 0))
                    composed['hook_added'] = hook_text
                    optimizations_applied.append('hook_extraction')
        
        # 2. Micro-cuts (if majority agrees)
        if needs_cuts:
            cuts_data = parsed_responses[0].get('optimizations', {}).get('micro_cuts', {})
            cuts = cuts_data.get('segments_to_optimize', [])
            if cuts:
                # Apply cuts conservatively
                time_saved = 0
                segments = composed.get('segments', [])
                
                for cut in cuts:
                    idx = cut.get('index')
                    if idx < len(segments):
                        original_text = segments[idx].get('text', '')
                        optimized_text = cut.get('optimized', original_text)
                        
                        if len(optimized_text) < len(original_text) and len(original_text) > 0:
                            # Calculate time saved
                            seg_duration = segments[idx].get('end', 0) - segments[idx].get('start', 0)
                            reduction = (len(original_text) - len(optimized_text)) / len(original_text)
                            time_saved += seg_duration * reduction
                            
                            # Apply cut
                            segments[idx]['text'] = optimized_text
                            segments[idx]['end'] = segments[idx].get('end', 0) - seg_duration * reduction
                
                if time_saved > 0:
                    composed['segments'] = segments
                    composed['time_saved'] = time_saved
                    composed['duration'] = composed.get('duration', 0) - time_saved
                    composed['end'] = composed.get('end', 0) - time_saved
                    optimizations_applied.append('micro_cuts')
        
        # 3. Timing pauses (if majority agrees)
        if needs_timing:
            timing_data = parsed_responses[0].get('optimizations', {}).get('timing_pauses', {})
            pauses = timing_data.get('pauses', [])
            if pauses:
                # Add pause markers
                segments = composed.get('segments', [])
                pause_count = 0
                
                for pause in pauses:
                    after_idx = pause.get('after_segment')
                    if after_idx < len(segments):
                        pause_seg = {
                            'start': segments[after_idx].get('end', 0),
                            'end': segments[after_idx].get('end', 0) + pause.get('duration', 0.8),
                            'text': f"[PAUSE: {pause.get('duration', 0.8):.1f}s]",
                            'is_pause': True,
                            'pause_type': pause.get('type', 'strategic')
                        }
                        segments.insert(after_idx + 1, pause_seg)
                        pause_count += 1
                
                if pause_count > 0:
                    composed['segments'] = segments
                    composed['pauses_added'] = pause_count
                    composed['end'] = segments[-1].get('end', composed.get('end', 0))
                    composed['duration'] = segments[-1].get('end', composed.get('end', 0)) - composed.get('start', 0)
                    optimizations_applied.append('timing_pauses')
        
        composed['optimizations_applied'] = optimizations_applied
        composed['composition_method'] = f'{len(responses)}-AI consensus'
        
        return composed
    
    async def _learning_based_cuts(self, moments: List[Dict]) -> List[Dict]:
        """
        Stage 2.5: Learning-Based Intelligent Cuts
        
        Uses proven patterns from 175 analyzed clips to:
        - Optimize hook placement (first 3s)
        - Cut unnecessary parts
        - Optimize payoff timing
        - Reduce to viral-optimal duration
        
        Args:
            moments: List of moments from Stage 2
            
        Returns:
            List of viral-optimized moments
        """
        if not self.ensemble or not self.consensus:
            return moments
        
        print(f"\n📍 STAGE 2.5: Learning-Based Intelligent Cuts")
        print(f"   Principle-Based: Applying principles from 175+ proven clips")
        print(f"   Goal: Viral-optimized duration and cuts")
        
        # Load duration principles (NOT hardcoded ranges!)
        duration_principles = self.PRINCIPLES.get('duration', {})
        
        optimized = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n   Optimizing moment {i}/{len(moments)}...")
            
            # Detect moment type
            segments = moment.get('segments', [])
            if not segments:
                optimized.append(moment)
                continue
                
            text = ' '.join([s.get('text', '') for s in segments]).lower()
            moment_type = self._detect_moment_type(text)
            
            current_duration = moment.get('duration', 0)
            
            # Use AI to decide if optimization needed (principle-based, not rigid)
            optimization_plan = await self._analyze_duration_optimization(
                moment, 
                moment_type,
                current_duration,
                duration_principles
            )
            
            if not optimization_plan.get('needs_optimization', False):
                print(f"      ✅ Duration optimal: {current_duration:.1f}s (complete for content type)")
                optimized.append(moment)
                continue
            
            # Need to optimize
            target_duration = optimization_plan.get('target_duration', current_duration)
            reduction_needed = current_duration - target_duration
            
            print(f"      🔧 Duration: {current_duration:.1f}s → Target: {target_duration:.1f}s (cut {reduction_needed:.1f}s)")
            print(f"      💡 Reasoning: {optimization_plan.get('reasoning', 'Optimize for completeness')}")
            
            # Call AI to make intelligent cuts
            optimized_moment = await self._apply_intelligent_cuts(
                moment, 
                moment_type,
                target_duration,
                duration_principles
            )
            
            optimized.append(optimized_moment)
            
            new_duration = optimized_moment.get('duration', 0)
            print(f"      ✅ Optimized: {new_duration:.1f}s (cut {current_duration - new_duration:.1f}s)")
        
        print(f"\n   💎 Learning-Based Cuts Complete")
        return optimized
    
    async def _analyze_duration_optimization(self, moment: Dict, moment_type: str, current_duration: float, duration_principles: Dict) -> Dict:
        """
        Principle-based analysis: Should this moment be optimized?
        NOT rigid ranges, but principle-based evaluation
        """
        if not self.consensus:
            return {'needs_optimization': False}
        
        segments = moment.get('segments', [])
        if not segments:
            return {'needs_optimization': False}
        
        full_text = ' '.join([s.get('text', '') for s in segments[:20]])  # First 20 segments
        
        # Format principles for prompt
        from learnings_extractor import LearningsExtractor
        extractor = LearningsExtractor()
        principles_text = extractor.format_principles_for_prompt('duration')
        
        prompt = f"""
PRINCIPLES (from 175+ proven clips):
{principles_text}

CURRENT MOMENT:
Type: {moment_type}
Duration: {current_duration:.1f}s
Content: "{full_text[:500]}..."

YOUR TASK:
Based on PRINCIPLES above (not rigid rules), should this be optimized?
Consider:
- Is story/insight complete?
- Does length serve engagement or hurt it?
- What would maximize watchtime?
- Is it too short (incomplete) or too long (rambling)?

RESPONSE FORMAT (JSON):
{{
  "needs_optimization": true,
  "target_duration": 45.0,  # Optimal duration based on completeness
  "reasoning": "Story is complete at 45s, remaining 20s is rambling",
  "completeness_score": 8,  # 0-10: How complete is the moment?
  "engagement_risk": "high"  # low/medium/high: Risk of drop-off
}}

If optimization NOT needed:
{{
  "needs_optimization": false,
  "reasoning": "Duration serves completeness and engagement"
}}

Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a content optimization expert. Apply principles, not rigid rules.",
                max_tokens=1000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                return {'needs_optimization': False}
            
            return analysis
            
        except Exception as e:
            print(f"         ⚠️ Duration analysis failed: {e}")
            return {'needs_optimization': False}
    
    async def _apply_intelligent_cuts(self, moment: Dict, moment_type: str, target_duration: float, duration_principles: Dict) -> Dict:
        """
        Apply AI-powered intelligent cuts based on learnings
        """
        if not self.consensus:
            return moment
        
        segments = moment.get('segments', [])
        if not segments:
            return moment
        
        full_text = ' '.join([s.get('text', '') for s in segments])
        current_duration = moment.get('duration', 0)
        
        # Format principles for prompt
        from learnings_extractor import LearningsExtractor
        extractor = LearningsExtractor()
        principles_text = extractor.format_principles_for_prompt('duration')
        cut_principles_text = extractor.format_principles_for_prompt('cuts')
        
        prompt = f"""
PRINCIPLES (from 175+ proven clips):
{principles_text}

CUT PRINCIPLES:
{cut_principles_text}

MOMENT TYPE: {moment_type}
CURRENT DURATION: {current_duration:.1f}s
TARGET DURATION: {target_duration:.1f}s
REDUCTION NEEDED: {current_duration - target_duration:.1f}s

CURRENT TEXT:
"{full_text[:1000]}"

YOUR TASK:
Apply PRINCIPLES above (not rigid templates) to optimize this moment.
1. Identify which segments to KEEP (by index, 0-indexed)
2. Cut to target duration while maintaining:
   - Completeness (story/insight must be complete)
   - Core message
   - Emotional resonance
   - Powerful payoff

RESPONSE FORMAT (JSON):
{{
  "keep_segments": [0, 1, 3, 5, 7],  # Indices to keep
  "cuts_made": [
    "Removed unnecessary descriptors",
    "Tightened transitions",
    "Preserved emotional beats"
  ],
  "new_hook": "First 3s after cuts",
  "payoff_preserved": true,
  "completeness_maintained": true
}}

Apply principles, not templates. Every cut should serve watchtime maximization.
Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral video editor. Make aggressive cuts based on proven patterns.",
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                raise ValueError("Invalid response format")
            
            keep_indices = analysis.get('keep_segments', [])
            
            if not keep_indices:
                return moment  # Fallback
            
            # Rebuild moment with kept segments
            new_segments = [segments[i] for i in keep_indices if 0 <= i < len(segments)]
            
            if not new_segments:
                return moment  # Fallback
            
            optimized = {
                **moment,
                'segments': new_segments,
                'start': new_segments[0].get('start', 0),
                'end': new_segments[-1].get('end', 0),
                'duration': new_segments[-1].get('end', 0) - new_segments[0].get('start', 0),
                'learning_cuts': True,
                'cuts_made': analysis.get('cuts_made', []),
                'optimization_type': 'learning_based',
                'moment_type_detected': moment_type
            }
            
            # Update hook phrase if changed
            if new_segments:
                optimized['hook_phrase'] = new_segments[0].get('text', '')[:100]
            
            return optimized
            
        except Exception as e:
            print(f"         ⚠️ Cut optimization failed: {e}")
            return moment  # Fallback to original
    
    async def _cross_moment_hook_extraction(self, moments: List[Dict], segments: List[Dict]) -> List[Dict]:
        """
        Stage 2.6: Cross-Moment Hook Extraction
        
        Principle: Maximum Hook Strength
        - Scans entire video for power hooks
        - Matches hooks to moments based on thematic relevance
        - Pre-pends hooks when they amplify the moment
        
        Args:
            moments: List of optimized moments from Stage 2.5
            segments: All video segments
            
        Returns:
            List of moments with enhanced hooks
        """
        if not self.ensemble or not self.consensus:
            return moments
        
        print(f"\n📍 STAGE 2.6: Cross-Moment Hook Extraction")
        print(f"   Principle: Maximum Hook Strength")
        print(f"   Strategy: Find best hooks in video, match to moments")
        
        # First pass: Extract all potential hooks from video
        print(f"\n   🔍 Scanning {len(segments)} segments for power hooks...")
        
        potential_hooks = await self._extract_power_hooks(segments)
        print(f"   ✅ Found {len(potential_hooks)} potential power hooks")
        
        if not potential_hooks:
            print(f"   ℹ️  No power hooks found - skipping enhancement")
            return moments
        
        # Second pass: Match hooks to moments
        enhanced_moments = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n   Analyzing moment {i}/{len(moments)}...")
            
            # Check if moment already has strong hook
            has_strong_hook = await self._has_strong_hook(moment)
            
            if has_strong_hook:
                print(f"      ✅ Already has strong hook - no enhancement needed")
                enhanced_moments.append(moment)
                continue
            
            # Find best matching hook
            best_hook = await self._find_best_hook_match(moment, potential_hooks)
            
            if best_hook:
                # Pre-pend hook to moment
                enhanced = self._prepend_hook(moment, best_hook)
                hook_text = best_hook.get('text', '')
                if not hook_text and best_hook.get('segments'):
                    hook_text = best_hook['segments'][0].get('text', '')[:50]
                print(f"      ✨ Enhanced with hook: '{hook_text}...'")
                hook_duration = best_hook.get('duration', 0)
                print(f"      ⏱️  Added {hook_duration:.1f}s")
                enhanced_moments.append(enhanced)
            else:
                print(f"      ℹ️  No suitable hook found - keeping original")
                enhanced_moments.append(moment)
        
        print(f"\n   💎 Hook Extraction Complete")
        return enhanced_moments
    
    async def _extract_power_hooks(self, segments: List[Dict]) -> List[Dict]:
        """
        Extract potential power hooks from all segments
        
        Looks for:
        - Bold declarative statements
        - Provocative questions
        - Contrarian views
        - Emotional statements
        """
        if not self.consensus:
            return []
        
        # Build context of all segments (limit for prompt)
        full_text = ' '.join([s.get('text', '') for s in segments[:100]])  # Limit to first 100 segments
        
        # Format hook principles for prompt
        from learnings_extractor import LearningsExtractor
        extractor = LearningsExtractor()
        hook_principles_text = extractor.format_principles_for_prompt('hooks')
        
        prompt = f"""
PRINCIPLE (from 175+ proven clips):
{hook_principles_text}

TRANSCRIPT (excerpt):
"{full_text[:2000]}..."

YOUR TASK:
Find the 10 strongest standalone hooks in this transcript.
Apply PRINCIPLES above - hooks can be ANY of the methods listed.
Different content types have different hook styles.

Each hook should be:
- 3-15 seconds max
- Standalone (makes sense without context)
- Attention-grabbing
- Thematically clear
- Matches one of the proven methods

RESPONSE FORMAT (JSON):
{{
  "hooks": [
    {{
      "text": "Arbeite niemals für Geld",
      "start": 123.5,
      "end": 125.8,
      "strength": 95,
      "theme": "work_money",
      "type": "bold_statement",
      "method": "Bold statement (contrarian view)"
    }},
    ...
  ]
}}

Score strength 0-100. Return top 10 hooks.
Find hooks that match the PRINCIPLE, not a template.
Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral content expert. Extract the strongest hooks from this transcript.",
                max_tokens=3000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                raise ValueError("Invalid response format")
            
            hooks = analysis.get('hooks', [])
            
            # Add segment info to hooks
            for hook in hooks:
                start_time = float(hook.get('start', 0))
                end_time = float(hook.get('end', 0))
                
                # Find matching segments
                hook['segments'] = [
                    s for s in segments 
                    if start_time <= s.get('start', 0) <= end_time
                ]
                hook['duration'] = end_time - start_time
                hook['start'] = start_time
                hook['end'] = end_time
            
            return hooks
            
        except Exception as e:
            print(f"      ⚠️ Hook extraction failed: {e}")
            return []
    
    async def _has_strong_hook(self, moment: Dict) -> bool:
        """
        Check if moment already has strong hook in first 3s
        """
        segments = moment.get('segments', [])
        if not segments:
            return False
        
        moment_start = moment.get('start', 0)
        first_3s_text = ''
        
        for seg in segments:
            seg_start = seg.get('start', 0)
            if seg_start - moment_start <= 3.0:
                first_3s_text += seg.get('text', '') + ' '
        
        # Quick heuristic check
        power_indicators = [
            'niemals', 'stopp', 'das problem', 'was wäre', 
            'stell dir vor', 'ich sage dir', 'vergiss', 'arbeite niemals',
            'was ist hier passiert', 'der verheerendste'
        ]
        
        text_lower = first_3s_text.lower()
        return any(indicator in text_lower for indicator in power_indicators)
    
    async def _find_best_hook_match(self, moment: Dict, hooks: List[Dict]) -> Optional[Dict]:
        """
        Find best thematic hook match for moment using AI
        """
        if not hooks or not self.consensus:
            return None
        
        segments = moment.get('segments', [])
        if not segments:
            return None
        
        moment_text = ' '.join([s.get('text', '') for s in segments[:3]])[:500]
        
        hooks_summary = '\n'.join([
            f"{i+1}. '{h.get('text', '')[:60]}' (theme: {h.get('theme', 'unknown')}, strength: {h.get('strength', 0)})"
            for i, h in enumerate(hooks[:10])
        ])
        
        prompt = f"""
Match the best hook to this moment.

MOMENT (first part):
"{moment_text}..."

AVAILABLE HOOKS:
{hooks_summary}

PRINCIPLES:
- Hook should amplify the moment, not confuse
- Thematic alignment matters
- Stronger hooks preferred
- Hook should create curiosity for what follows

If no hook fits well, return "none".

RESPONSE (JSON):
{{
  "best_hook_index": 2,  # or "none"
  "reasoning": "Why this hook amplifies the moment"
}}

Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral content strategist. Match hooks to moments based on thematic relevance.",
                max_tokens=1000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                return None
            
            hook_idx = analysis.get('best_hook_index')
            
            if hook_idx == "none" or hook_idx is None:
                return None
            
            # Convert to 0-indexed
            hook_idx = int(hook_idx) - 1 if isinstance(hook_idx, (int, str)) and str(hook_idx).isdigit() else None
            
            if hook_idx is None or hook_idx < 0 or hook_idx >= len(hooks):
                return None
            
            return hooks[hook_idx]
            
        except Exception as e:
            print(f"         ⚠️ Hook matching failed: {e}")
            return None
    
    def _prepend_hook(self, moment: Dict, hook: Dict) -> Dict:
        """
        Pre-pend hook segments to moment
        """
        hook_segments = hook.get('segments', [])
        moment_segments = moment.get('segments', [])
        
        if not hook_segments:
            return moment
        
        # Create enhanced moment
        enhanced = {
            **moment,
            'segments': hook_segments + moment_segments,
            'start': hook.get('start', moment.get('start', 0)),
            'duration': moment.get('end', 0) - hook.get('start', moment.get('start', 0)),
            'hook_enhanced': True,
            'hook_text': hook.get('text', ''),
            'hook_source': 'cross_moment_extraction',
            'hook_strength': hook.get('strength', 0),
            'hook_theme': hook.get('theme', 'unknown')
        }
        
        # Update hook phrase
        if hook_segments:
            enhanced['hook_phrase'] = hook_segments[0].get('text', '')[:100]
        
        return enhanced
    
    async def _micro_text_optimization(self, moments: List[Dict]) -> List[Dict]:
        """
        Stage 2.7: Micro-Level Text Optimization
        
        Principle: Every Word Earns Its Place
        - Cuts filler words and phrases WITHIN segments
        - Word-level precision editing
        - Maintains meaning and emotional resonance
        - Natural voice preservation
        
        Args:
            moments: List of hook-enhanced moments from Stage 2.6
            
        Returns:
            List of micro-optimized moments
        """
        if not self.ensemble or not self.consensus:
            return moments
        
        print(f"\n📍 STAGE 2.7: Micro-Level Text Optimization")
        print(f"   Principle: Every Word Earns Its Place")
        print(f"   Strategy: Word-level precision cuts (principle-based)")
        
        # Load cut principles (NOT hardcoded examples!)
        cut_principles = self.PRINCIPLES.get('cuts', {})
        
        optimized = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n   Micro-optimizing moment {i}/{len(moments)}...")
            
            # Calculate target reduction
            current_duration = moment.get('duration', 0)
            if current_duration == 0:
                optimized.append(moment)
                continue
            
            # Aim for 5-10% reduction via micro-cuts
            target_reduction = current_duration * 0.08  # 8% average
            target_duration = current_duration - target_reduction
            
            print(f"      Current: {current_duration:.1f}s")
            print(f"      Target: {target_duration:.1f}s (remove {target_reduction:.1f}s)")
            
            # Call AI for micro-optimization (principle-based)
            optimized_moment = await self._apply_micro_cuts(
                moment, 
                target_duration,
                cut_principles
            )
            
            actual_reduction = current_duration - optimized_moment.get('duration', current_duration)
            print(f"      ✅ Optimized: {optimized_moment.get('duration', current_duration):.1f}s (cut {actual_reduction:.1f}s)")
            
            optimized.append(optimized_moment)
        
        print(f"\n   💎 Micro-Text Optimization Complete")
        return optimized
    
    async def _apply_micro_cuts(self, moment: Dict, target_duration: float, cut_principles: Dict) -> Dict:
        """
        Apply AI-powered micro-cuts within segments
        """
        if not self.consensus:
            return moment
        
        segments = moment.get('segments', [])
        if not segments:
            return moment
        
        # Build segment text with timing info
        segments_info = []
        for i, seg in enumerate(segments):
            duration = seg.get('end', 0) - seg.get('start', 0)
            segments_info.append({
                'index': i,
                'text': seg.get('text', ''),
                'duration': duration,
                'start': seg.get('start', 0),
                'end': seg.get('end', 0)
            })
        
        current_duration = moment.get('duration', 0)
        reduction_needed = current_duration - target_duration
        
        prompt = f"""
You are an expert viral video editor doing MICRO-LEVEL text optimization.

CURRENT MOMENT:
Duration: {current_duration:.1f}s
Target: {target_duration:.1f}s
Reduction needed: {reduction_needed:.1f}s

SEGMENTS:
"""
        
        for seg_info in segments_info:
            prompt += f"""
Segment {seg_info['index']} ({seg_info['duration']:.1f}s):
"{seg_info['text']}"
"""
        
        # Format cut principles for prompt
        from learnings_extractor import LearningsExtractor
        extractor = LearningsExtractor()
        cut_principles_text = extractor.format_principles_for_prompt('cuts')
        
        prompt += f"""

PRINCIPLES (from Longform→Clip analysis):
{cut_principles_text}

YOUR TASK:
Apply principles above (not examples blindly).
Every cut decision should serve watchtime maximization.

3. Remove Obvious Statements
   Example: "Super, kriegen wir noch Geld dafür. Nächster Tag." → "Super. Nächster Tag."
   Cut: Obvious commentary

4. Cut Filler Words (carefully!)
   Remove: "sozusagen", "also", "ja also", "wie gesagt"
   BUT: Keep if it adds authenticity or emphasis

5. Condense Without Losing Meaning
   Keep the story essence
   Maintain emotional beats
   Preserve speaker's voice

CRITICAL RULES:
- Don't over-edit! Some "Füllwörter" add naturalness
- Keep emotional resonance
- Maintain narrative flow
- Every cut must preserve meaning

YOUR TASK:
For each segment, provide optimized text that cuts {reduction_needed:.1f}s total.

RESPONSE FORMAT (JSON):
{{
  "optimized_segments": [
    {{
      "index": 0,
      "original_text": "...",
      "optimized_text": "...",
      "cuts_made": ["removed 'wie Kinder manchmal sind'", "tightened transition"],
      "estimated_time_saved": 1.2
    }},
    ...
  ],
  "total_time_saved": {reduction_needed:.1f}
}}

Be surgical. Cut fat, keep muscle.
Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral video editor. Make surgical micro-cuts to tighten text while preserving meaning and voice.",
                max_tokens=4000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                raise ValueError("Invalid response format")
            
            optimized_segs = analysis.get('optimized_segments', [])
            
            if not optimized_segs:
                return moment  # Fallback
            
            # Rebuild segments with optimized text
            new_segments = []
            time_saved = 0
            
            for opt_seg in optimized_segs:
                idx = opt_seg.get('index', 0)
                if idx >= len(segments):
                    continue
                
                original_seg = segments[idx]
                optimized_text = opt_seg.get('optimized_text', original_seg.get('text', ''))
                
                # Estimate new duration based on text length reduction
                original_text = original_seg.get('text', '')
                original_len = len(original_text)
                optimized_len = len(optimized_text)
                
                original_duration = original_seg.get('end', 0) - original_seg.get('start', 0)
                
                if optimized_len < original_len and original_len > 0:
                    # Proportional time reduction
                    time_reduction = original_duration * (original_len - optimized_len) / original_len
                    time_saved += time_reduction
                    
                    new_end = original_seg.get('end', 0) - time_reduction
                else:
                    new_end = original_seg.get('end', 0)
                
                new_seg = {
                    **original_seg,
                    'text': optimized_text,
                    'end': new_end,
                    'original_text': original_text,
                    'micro_cuts': opt_seg.get('cuts_made', [])
                }
                
                new_segments.append(new_seg)
            
            # Rebuild moment
            if new_segments:
                new_end = new_segments[-1].get('end', moment.get('end', 0))
                new_duration = new_end - moment.get('start', 0)
            else:
                new_end = moment.get('end', 0)
                new_duration = moment.get('duration', 0)
            
            optimized = {
                **moment,
                'segments': new_segments if new_segments else segments,
                'end': new_end,
                'duration': new_duration,
                'micro_optimized': True,
                'micro_cuts_applied': analysis.get('total_time_saved', time_saved)
            }
            
            return optimized
            
        except Exception as e:
            print(f"         ⚠️ Micro-optimization failed: {e}")
            return moment  # Fallback to original
    
    async def _dramatic_timing_optimization(self, moments: List[Dict]) -> List[Dict]:
        """
        Stage 2.8: Dramatic Structure & Timing
        
        Principle: Silence Creates Impact
        - Adds strategic pauses for dramatic effect
        - Question → PAUSE → Answer structure
        - Emotional beat placement
        - Payoff anticipation
        
        Args:
            moments: List of micro-optimized moments from Stage 2.7
            
        Returns:
            List of moments with enhanced dramatic timing
        """
        if not self.ensemble or not self.consensus:
            return moments
        
        print(f"\n📍 STAGE 2.8: Dramatic Structure & Timing")
        print(f"   Principle: Silence Creates Impact")
        print(f"   Strategy: Strategic pauses for emotional beats")
        
        # Load timing principles (NOT hardcoded!)
        timing_principles = self.PRINCIPLES.get('timing', {})
        optimal_durations = timing_principles.get('optimal_durations', {})
        
        timed_moments = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n   Analyzing timing for moment {i}/{len(moments)}...")
            
            # Detect timing opportunities (principle-based)
            timing_plan = await self._analyze_timing_opportunities(moment, timing_principles)
            
            if timing_plan.get('opportunities', 0) == 0:
                print(f"      ℹ️  No timing opportunities - keeping original")
                timed_moments.append(moment)
                continue
            
            # Apply timing enhancements
            enhanced = self._apply_dramatic_timing(moment, timing_plan)
            
            pauses = timing_plan.get('pauses', [])
            added_time = sum([p.get('duration', 0) for p in pauses])
            print(f"      ✨ Added {len(pauses)} strategic pauses ({added_time:.1f}s)")
            
            for pause in pauses:
                context = pause.get('context', '')[:40]
                pause_type = pause.get('type', 'unknown')
                duration = pause.get('duration', 0)
                print(f"         • {pause_type}: {duration:.1f}s after '{context}...'")
            
            timed_moments.append(enhanced)
        
        print(f"\n   💎 Dramatic Timing Complete")
        return timed_moments
    
    async def _analyze_timing_opportunities(self, moment: Dict, principles: Dict) -> Dict:
        """
        Analyze where strategic pauses should be added
        """
        if not self.consensus:
            return {'opportunities': 0, 'pauses': []}
        
        segments = moment.get('segments', [])
        if not segments:
            return {'opportunities': 0, 'pauses': []}
        
        # Build segment context
        segments_text = []
        for i, seg in enumerate(segments):
            # Skip pause markers
            if seg.get('is_pause'):
                continue
            segments_text.append({
                'index': i,
                'text': seg.get('text', ''),
                'is_last': i == len(segments) - 1
            })
        
        prompt = f"""
Analyze this moment for DRAMATIC TIMING opportunities.

SEGMENTS:
"""
        
        for seg_info in segments_text:
            marker = " [LAST]" if seg_info['is_last'] else ""
            prompt += f"{seg_info['index']}: \"{seg_info['text']}\"{marker}\n"
        
        # Format timing principles for prompt
        from learnings_extractor import LearningsExtractor
        extractor = LearningsExtractor()
        timing_principles_text = extractor.format_principles_for_prompt('timing')
        
        prompt += f"""

PRINCIPLES (from proven clips):
{timing_principles_text}

YOUR TASK:
Identify IF pauses would help (not WHERE they "should" go).
Some content needs pauses, some doesn't.
Timing serves content, not rigid templates.

RESPONSE FORMAT (JSON):
{{
  "opportunities": 2,
  "pauses": [
    {{
      "after_segment": 3,
      "type": "question_answer",
      "duration": 1.5,
      "context": "Was ist hier passiert?",
      "reasoning": "Creates tension before payoff"
    }},
    {{
      "after_segment": 4,
      "type": "payoff_anticipation",
      "duration": 0.8,
      "context": "Die Kinder ärgern ihn nicht mehr",
      "reasoning": "Beat before insight delivery"
    }}
  ]
}}

If no good opportunities, return: {{"opportunities": 0, "pauses": []}}
Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a dramatic timing expert. Identify where strategic pauses enhance emotional impact.",
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                return {'opportunities': 0, 'pauses': []}
            
            return analysis
            
        except Exception as e:
            print(f"         ⚠️ Timing analysis failed: {e}")
            return {'opportunities': 0, 'pauses': []}
    
    def _apply_dramatic_timing(self, moment: Dict, timing_plan: Dict) -> Dict:
        """
        Apply strategic pauses to moment structure
        """
        if timing_plan.get('opportunities', 0) == 0:
            return moment
        
        segments = moment.get('segments', [])
        pauses = timing_plan.get('pauses', [])
        
        if not pauses:
            return moment
        
        # Sort pauses by segment index (reverse order to maintain indices)
        pauses_sorted = sorted(pauses, key=lambda x: x.get('after_segment', -1), reverse=True)
        
        # Insert pause markers
        enhanced_segments = []
        total_pause_time = 0
        
        # Create a mapping of segment index to actual segment (skip pause markers)
        real_segments = [s for s in segments if not s.get('is_pause')]
        
        for i, seg in enumerate(segments):
            # Skip if this is already a pause marker
            if seg.get('is_pause'):
                continue
            
            enhanced_segments.append(seg)
            
            # Check if pause needed after this segment
            real_index = len([s for s in segments[:i+1] if not s.get('is_pause')]) - 1
            
            for pause in pauses_sorted:
                if pause.get('after_segment') == real_index:
                    # Add pause marker segment
                    pause_duration = pause.get('duration', 1.5)
                    pause_seg = {
                        'start': seg.get('end', 0),
                        'end': seg.get('end', 0) + pause_duration,
                        'text': f"[PAUSE: {pause_duration:.1f}s]",
                        'is_pause': True,
                        'pause_type': pause.get('type', 'unknown'),
                        'pause_reasoning': pause.get('reasoning', '')
                    }
                    enhanced_segments.append(pause_seg)
                    total_pause_time += pause_duration
                    break  # Only add one pause per segment
        
        # Adjust timestamps for segments after pauses
        cumulative_pause = 0
        adjusted_segments = []
        current_time = moment.get('start', 0)
        
        for seg in enhanced_segments:
            if seg.get('is_pause'):
                pause_duration = seg.get('end', 0) - seg.get('start', 0)
                adjusted_seg = {
                    **seg,
                    'start': current_time,
                    'end': current_time + pause_duration
                }
                current_time += pause_duration
                cumulative_pause += pause_duration
                adjusted_segments.append(adjusted_seg)
            else:
                seg_start = seg.get('start', 0)
                seg_duration = seg.get('end', 0) - seg_start
                adjusted_seg = {
                    **seg,
                    'start': current_time,
                    'end': current_time + seg_duration
                }
                current_time += seg_duration
                adjusted_segments.append(adjusted_seg)
        
        # Rebuild moment
        enhanced = {
            **moment,
            'segments': adjusted_segments,
            'end': adjusted_segments[-1].get('end', moment.get('end', 0)),
            'duration': adjusted_segments[-1].get('end', moment.get('end', 0)) - moment.get('start', 0),
            'dramatic_timing': True,
            'pauses_added': len(pauses),
            'total_pause_time': total_pause_time,
            'timing_plan': timing_plan
        }
        
        return enhanced
    
    async def _payoff_isolation_polish(self, moments: List[Dict]) -> List[Dict]:
        """
        Stage 2.9: Payoff Isolation & Final Polish
        
        Principle: The Money Shot Deserves Its Moment
        - Identifies the payoff/insight/punchline
        - Creates clear separation from setup
        - Adds anticipation beat before payoff
        - Ensures payoff has space to land
        
        Args:
            moments: List of dramatically-timed moments from Stage 2.8
            
        Returns:
            List of final polished moments with isolated payoffs
        """
        if not self.consensus:
            return moments
        
        print(f"\n📍 STAGE 2.9: Payoff Isolation & Final Polish")
        print(f"   Principle: The Money Shot Deserves Its Moment")
        print(f"   Strategy: Isolate payoff, create separation, final impact")
        
        polished_moments = []
        
        for i, moment in enumerate(moments, 1):
            print(f"\n   Analyzing moment {i}/{len(moments)}...")
            
            # Detect if moment has clear payoff
            payoff_analysis = await self._detect_payoff(moment)
            
            if not payoff_analysis.get('has_payoff', False):
                print(f"      ℹ️  No clear payoff - keeping as-is")
                polished_moments.append(moment)
                continue
            
            # Apply payoff isolation
            polished = self._isolate_payoff(moment, payoff_analysis)
            
            payoff_text = payoff_analysis.get('payoff_text', '')[:50]
            anticipation = payoff_analysis.get('anticipation_pause', 0)
            
            print(f"      ✨ Payoff isolated: '{payoff_text}...'")
            print(f"      ⏱️  Added {anticipation:.1f}s anticipation beat")
            
            polished_moments.append(polished)
        
        print(f"\n   💎 Payoff Isolation Complete")
        return polished_moments
    
    async def _detect_payoff(self, moment: Dict) -> Dict:
        """
        Detect if moment has clear payoff and where it is
        """
        if not self.consensus:
            return {'has_payoff': False}
        
        segments = moment.get('segments', [])
        if not segments:
            return {'has_payoff': False}
        
        # Build segment context (skip pause markers)
        non_pause_segments = [(i, seg) for i, seg in enumerate(segments) if not seg.get('is_pause')]
        segments_info = []
        for idx, (orig_idx, seg) in enumerate(non_pause_segments):
            segments_info.append({
                'index': idx,  # Index in non-pause list (for AI response)
                'original_index': orig_idx,  # Original index in segments
                'text': seg.get('text', ''),
                'is_last': idx == len(non_pause_segments) - 1
            })
        
        prompt = f"""
Analyze this moment for a clear PAYOFF (money shot/insight/punchline).

SEGMENTS:
"""
        
        for seg_info in segments_info:
            marker = " [LAST]" if seg_info['is_last'] else ""
            prompt += f"{seg_info['index']}: \"{seg_info['text']}\"{marker}\n"
        
        # Format structure principles for prompt
        from learnings_extractor import LearningsExtractor
        extractor = LearningsExtractor()
        structure_principles_text = extractor.format_principles_for_prompt('structure')
        
        prompt += f"""

PRINCIPLES (from proven clips):
{structure_principles_text}

PAYOFF DEFINITION:
A payoff is the moment where:
- The insight/lesson is delivered
- The punchline lands
- The "aha!" happens
- The question is answered
- The tension resolves

YOUR TASK:
1. Identify content type FIRST
2. Apply appropriate structure for THAT type
3. Does this moment have a clear payoff?
4. If yes, which segment(s) contain it?
5. Should there be a separation/pause before it?

Don't force all content into one template!

RESPONSE FORMAT (JSON):
{{
  "has_payoff": true,
  "payoff_segment_indices": [7, 8],  # Segment(s) with payoff
  "payoff_text": "Die Freude am Tun ist ersetzt worden durch Belohnung.",
  "payoff_type": "insight",  # insight/punchline/revelation/answer
  "needs_separation": true,
  "anticipation_pause": 0.8,  # Seconds of pause before payoff
  "reasoning": "Clear insight delivered after story setup"
}}

If no clear payoff: {{"has_payoff": false}}
Return JSON only.
"""
        
        try:
            result = await self.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a content structure expert. Identify payoffs (money shots) that deserve isolation.",
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis = self._parse_json_response(result)
            
            if not analysis or not isinstance(analysis, dict):
                return {'has_payoff': False}
            
            return analysis
            
        except Exception as e:
            print(f"         ⚠️ Payoff detection failed: {e}")
            return {'has_payoff': False}
    
    def _isolate_payoff(self, moment: Dict, payoff_analysis: Dict) -> Dict:
        """
        Apply payoff isolation based on analysis
        """
        if not payoff_analysis.get('needs_separation', False):
            # Payoff already isolated, just mark it
            return {
                **moment,
                'payoff_isolated': True,
                'payoff_text': payoff_analysis.get('payoff_text', ''),
                'payoff_type': payoff_analysis.get('payoff_type', 'unknown')
            }
        
        segments = moment.get('segments', [])
        payoff_indices = payoff_analysis.get('payoff_segment_indices', [])
        anticipation_pause = payoff_analysis.get('anticipation_pause', 0.8)
        
        if not payoff_indices:
            # No indices provided, can't isolate
            return {
                **moment,
                'payoff_isolated': False,
                'payoff_text': payoff_analysis.get('payoff_text', '')
            }
        
        # Build non-pause segment mapping (same as in _detect_payoff)
        non_pause_segments = [(i, seg) for i, seg in enumerate(segments) if not seg.get('is_pause')]
        
        # payoff_indices are indices in the non-pause list
        # Find first payoff segment's original index
        first_payoff_orig_idx = None
        for idx in payoff_indices:
            if idx < len(non_pause_segments):
                orig_idx = non_pause_segments[idx][0]
                if first_payoff_orig_idx is None or orig_idx < first_payoff_orig_idx:
                    first_payoff_orig_idx = orig_idx
        
        if first_payoff_orig_idx is None or first_payoff_orig_idx == 0:
            # Payoff is first segment, can't add pause before
            return {
                **moment,
                'payoff_isolated': True,
                'payoff_text': payoff_analysis.get('payoff_text', ''),
                'payoff_type': payoff_analysis.get('payoff_type', 'unknown')
            }
        
        # Insert anticipation pause before payoff
        new_segments = []
        pause_inserted = False
        
        for i, seg in enumerate(segments):
            # Add segment
            new_segments.append(seg)
            
            # Check if we should add pause after this segment
            if i == first_payoff_orig_idx - 1 and not pause_inserted:
                # Add anticipation pause
                pause_seg = {
                    'start': seg.get('end', seg.get('start', 0) + 1),
                    'end': seg.get('end', seg.get('start', 0) + 1) + anticipation_pause,
                    'text': f"[ANTICIPATION PAUSE: {anticipation_pause:.1f}s]",
                    'is_pause': True,
                    'pause_type': 'payoff_anticipation',
                    'pause_reasoning': 'Brief beat before money shot delivery'
                }
                new_segments.append(pause_seg)
                pause_inserted = True
        
        # Adjust timestamps after pause
        cumulative_pause = 0
        adjusted_segments = []
        
        for seg in new_segments:
            if seg.get('is_pause'):
                pause_duration = seg.get('end', 0) - seg.get('start', 0)
                cumulative_pause += pause_duration
                adjusted_segments.append(seg)
            else:
                seg_start = seg.get('start', 0)
                seg_end = seg.get('end', 0)
                adjusted_seg = {
                    **seg,
                    'start': seg_start + cumulative_pause,
                    'end': seg_end + cumulative_pause
                }
                adjusted_segments.append(adjusted_seg)
        
        # Mark payoff segments (by matching text)
        payoff_text = payoff_analysis.get('payoff_text', '').lower()
        for adj_seg in adjusted_segments:
            if not adj_seg.get('is_pause'):
                seg_text = adj_seg.get('text', '').lower()
                # Mark if text matches payoff or is in payoff indices
                if payoff_text and payoff_text[:30] in seg_text:
                    adj_seg['is_payoff'] = True
        
        # Rebuild moment
        final_end = adjusted_segments[-1].get('end', moment.get('end', 0))
        polished = {
            **moment,
            'segments': adjusted_segments,
            'end': final_end,
            'duration': final_end - moment.get('start', 0),
            'payoff_isolated': True,
            'payoff_text': payoff_analysis.get('payoff_text', ''),
            'payoff_type': payoff_analysis.get('payoff_type', 'unknown'),
            'anticipation_pause_added': anticipation_pause
        }
        
        return polished
    
    async def _batched_godmode_evaluation(self, moments: List[Dict]) -> List[Dict]:
        """
        Final premium evaluation using batched Opus 4
        
        Evaluates moments in batches for efficiency
        Uses principle-based scoring (same 6 principles)
        Accepts moments with score >= 40
        
        Args:
            moments: List of polished moments from Stage 2
            
        Returns:
            List of viral-worthy moments (40+ score)
        """
        if not self.ensemble or not self.consensus:
            return moments
        
        print(f"\n📍 GODMODE: Batched Premium Evaluation")
        print(f"   Evaluating {len(moments)} polished moments")
        print(f"   Model: Opus 4 (premium)")
        
        # Use same 6 PRINCIPLES from earlier stages
        PRINCIPLES_CONTEXT = """
You are evaluating viral potential using these PRINCIPLES (not rigid rules):

1. COMPLETENESS for what it IS
   - Story? Needs setup + payoff (duration varies)
   - Insight? Needs context + lesson (can be short or long)
   - Rant? Needs buildup + climax (energy matters, not length)
   
2. NATURAL BOUNDARIES
   - Starts/ends at natural points (pauses, topic shifts, emotions)
   - Respects speaker's rhythm
   
3. EMOTIONAL INTENSITY
   - Hooks attention (varies by format: stage vs podcast)
   - Maintains energy (context-dependent)
   - Creates impact (different for each clip)
   
4. PATTERN INTERRUPTS
   - Breaks expectations, surprises
   - Creates curiosity, reveals insights
   
5. FORMAT FLEXIBILITY
   - Stage? Long-form energy works
   - Podcast? Natural flow
   - Live? Audience reactions add value
   
6. CONTEXT AWARENESS
   - Speaker style (Tony Robbins ≠ Gary Vee)
   - Setting (Stage ≠ Office ≠ Interview)
   - Audience (Corporate ≠ Fitness ≠ General)

SCORING:
- 45-50: Exceptional viral potential (must share!)
- 40-44: Strong viral potential (very good)
- 35-39: Good moment, but not quite viral
- 30-34: Decent content, lacks viral spark
- <30: Not suitable for viral clip

CRITICAL: Evaluate holistically based on what makes THIS moment viral in THIS context.
Not a checklist - moments don't need all 6 principles.
"""
        
        # Process in batches of 5
        batch_size = 5
        all_scored = []
        
        for batch_start in range(0, len(moments), batch_size):
            batch = moments[batch_start:batch_start + batch_size]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (len(moments) + batch_size - 1) // batch_size
            
            print(f"\n   Batch {batch_num}/{total_batches}: Evaluating {len(batch)} moments...")
            
            # Build batch prompt
            prompt = f"""
{PRINCIPLES_CONTEXT}

TASK: Evaluate {len(batch)} moments for viral potential

"""
            
            for i, moment in enumerate(batch, 1):
                text = ' '.join([s.get('text', '') for s in moment.get('segments', [])])[:800]  # Truncate
                duration = moment.get('duration', 0)
                viral_score = moment.get('viral_score', 'N/A')
                
                prompt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MOMENT {i}:
Duration: {duration:.1f}s
Segments: {len(moment.get('segments', []))}
Pre-score: {viral_score}/100
Content: "{text}..."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            prompt += """
YOUR EVALUATION for EACH moment:

1. Apply the 6 PRINCIPLES holistically
2. Consider: What makes THIS moment viral in THIS context?
3. Score 0-50 (realistic, not inflated)
4. Provide constructive reasoning

RESPONSE FORMAT (JSON):
{
  "evaluations": [
    {
      "moment_id": 1,
      "score": 42,
      "strengths": ["Complete story arc", "Emotional payoff", "Relatable"],
      "weaknesses": ["Slightly long setup", "Could trim 5s"],
      "verdict": "accept" or "reject",
      "reasoning": "Strong moment with complete arc and satisfying payoff..."
    },
    ...
  ]
}

Accept if score >= 40, reject if < 40.
Be honest - not every moment will be viral, and that's okay.
Return JSON only.
"""
            
            # Call Opus 4 via consensus engine
            try:
                result = await self.consensus.single_ai_call(
                    prompt=prompt,
                    model='opus',  # Use Opus 4
                    system="You are a premium viral content evaluator. Evaluate using principles, not rigid rules.",
                    max_tokens=6000,
                    temperature=0.7
                )
                
                # Parse response
                analysis = self._parse_json_response(result)
                
                if not analysis or not isinstance(analysis, dict):
                    raise ValueError("Invalid response format")
                
                evaluations_data = analysis.get('evaluations', [])
                
                if not evaluations_data:
                    raise ValueError("No evaluations in response")
                
                # Process evaluations
                for eval_data in evaluations_data:
                    moment_id = eval_data.get('moment_id')
                    if not moment_id or moment_id < 1 or moment_id > len(batch):
                        continue
                    
                    original_moment = batch[moment_id - 1]
                    
                    # Add evaluation data to moment
                    scored_moment = {
                        **original_moment,
                        'godmode_score': eval_data.get('score', 0),
                        'godmode_strengths': eval_data.get('strengths', []),
                        'godmode_weaknesses': eval_data.get('weaknesses', []),
                        'godmode_reasoning': eval_data.get('reasoning', ''),
                        'godmode_verdict': eval_data.get('verdict', 'reject')
                    }
                    
                    all_scored.append(scored_moment)
                    
                    # Log
                    verdict = eval_data.get('verdict', 'reject')
                    score = eval_data.get('score', 0)
                    verdict_icon = "✅" if verdict == 'accept' else "❌"
                    print(f"      {verdict_icon} Moment {moment_id}: {score}/50 - {verdict}")
            
            except Exception as e:
                print(f"      ⚠️ Batch evaluation failed: {e}")
                # Keep originals without scoring
                for moment in batch:
                    moment['godmode_verdict'] = 'reject'
                    moment['godmode_score'] = 0
                    all_scored.append(moment)
        
        # Filter to accepted moments (score >= 40)
        viral_moments = [m for m in all_scored if m.get('godmode_verdict') == 'accept']
        
        print(f"\n   📊 GODMODE RESULTS:")
        print(f"      Evaluated: {len(all_scored)} moments")
        print(f"      Accepted: {len(viral_moments)} moments (40+ score)")
        print(f"      Rejected: {len(all_scored) - len(viral_moments)} moments")
        
        # Show top moments
        if viral_moments:
            viral_moments_sorted = sorted(viral_moments, key=lambda x: x.get('godmode_score', 0), reverse=True)
            print(f"\n   🏆 TOP VIRAL MOMENTS:")
            for i, m in enumerate(viral_moments_sorted[:5], 1):
                score = m.get('godmode_score', 0)
                duration = m.get('duration', 0)
                print(f"      {i}. Score: {score}/50, Duration: {duration:.1f}s")
        
        return viral_moments
    
    # OLD: quality_filter_with_debate - REMOVED
    # Replaced by: _conditional_restructure (Stage 2) + _batched_godmode_evaluation (Final)
    # Reason: Principle-based conditional restructure is more efficient and cost-effective
    # Old method used 6-AI ensemble per moment (expensive), new approach uses:
    # - Pre-check heuristics (free) to identify moments needing restructure
    # - Batched restructure (3 moments per call)
    # - Batched godmode evaluation (5 moments per call with Opus 4)
    # Result: 74% cost reduction ($3.20 vs $12.50 per video)
    
    def _format_segments_for_prompt(self, segments: List[Dict]) -> str:
        """Format segments for AI prompts"""
        formatted = []
        for i, seg in enumerate(segments[:100]):  # Limit for token efficiency
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            text = str(seg.get('text', ''))[:200]  # Limit text length
            formatted.append(f"[{i}] {start:.1f}s-{end:.1f}s: {text}")
        return "\n".join(formatted)
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from AI response with error handling"""
        import re
        import json
        
        if not response:
            return {}
        
        try:
            # Try direct parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try extracting from ```json blocks
            match = re.search(r'```json\s*(\{.*?\}|\[.*?\])\s*```', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            
            # Try extracting any JSON-like structure
            match = re.search(r'(\{.*?\}|\[.*?\])', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            
            # Last resort: try to find array or object
            if '[' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                if end > start:
                    try:
                        return json.loads(response[start:end])
                    except:
                        pass
            
            if '{' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                if end > start:
                    try:
                        return json.loads(response[start:end])
                    except:
                        pass
        
        return {}
    
    def _create_refined_moment(self, analysis: Dict, seed: Dict, segments: List[Dict]) -> Dict:
        """Create moment dict from refinement analysis"""
        try:
            start = float(analysis.get('optimal_start', seed.get('start', 0)))
            end = float(analysis.get('optimal_end', seed.get('end', 0)))
            
            if end <= start:
                return None
            
            # Get segments in range
            moment_segments = [
                s for s in segments
                if s.get('start', 0) >= start and s.get('end', 0) <= end
            ]
            
            # Extract hook phrase (first segment text)
            hook_phrase = ""
            if moment_segments:
                hook_phrase = str(moment_segments[0].get('text', ''))[:100]
            
            return {
                'start': start,
                'end': end,
                'duration': end - start,
                'moment_type': str(analysis.get('moment_type', 'unknown')),
                'hook_phrase': hook_phrase,
                'pattern': str(analysis.get('moment_type', 'unknown')),  # Use as pattern
                'completeness_score': analysis.get('completeness_score', 0),
                'segments': moment_segments,
                'viral_reasoning': str(analysis.get('reasoning', '')),
                'key_elements': analysis.get('key_elements', [])
            }
        except Exception as e:
            print(f"      ⚠️  Error creating refined moment: {e}")
            return None
    
    async def run(self, video_path: str = None) -> Dict:
        """
        Complete integrated pipeline WITH learnings + validation
        
        Args:
            video_path: Optional direct path to video file
        """
        
        print("\n" + "="*70)
        print("🚀 CREATE CLIPS V4 - INTEGRATED PIPELINE")
        print("="*70)
        
        # Show learning stats
        try:
            clips_analyzed = self._get_clips_analyzed_count()
            print(f"\n🧠 Learning Stats:")
            print(f"   Clips analyzed: {clips_analyzed}")
            print(f"   Learnings: {'✅ Available' if get_learnings_for_prompt else '⚠️  Not trained'}")
        except:
            pass
        
        print("\n" + "="*70)
        print("📹 SELECT VIDEO")
        print("="*70)
        
        # VIDEO SELECTION - Allow direct path OR selection
        if video_path:
            # Direct path provided
            selected_video = Path(video_path)
            if not selected_video.exists():
                print(f"   ❌ Video not found: {video_path}")
                return None
            print(f"   ✅ Using: {selected_video.name}")
        
        else:
            # Show available videos
            video_dir = Path("data/uploads")
            videos = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.mov"))
            
            if not videos:
                print("   ❌ No videos found in data/uploads")
                print("   💡 Please add MP4/MOV files to data/uploads/")
                return None
            
            print(f"\nAvailable videos in {video_dir}:")
            for i, v in enumerate(videos, 1):
                # Check for transcript
                transcript_file = self.transcript_dir / f"{v.stem}_transcript.json"
                status = "✅ has transcript" if transcript_file.exists() else "⚠️ needs transcript"
                print(f"   {i}. {v.name} ({status})")
            
            # Also allow custom path
            print(f"   OR enter full path to video file")
            
            try:
                choice = input(f"\nSelect video (1-{len(videos)} or path): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n⚠️  Cancelled (non-interactive mode)")
                return None
            
            # Check if it's a number or path
            if choice.isdigit() and 1 <= int(choice) <= len(videos):
                selected_video = videos[int(choice) - 1]
            else:
                # Treat as path
                selected_video = Path(choice)
                if not selected_video.exists():
                    print(f"   ❌ Video not found: {choice}")
                    return None
            
            print(f"\n   ✅ Selected: {selected_video.name}")
        
        # Load or create transcript
        print("\n" + "="*70)
        print("📝 TRANSCRIPT")
        print("="*70)
        
        transcript_file = self.transcript_dir / f"{selected_video.stem}_transcript.json"
        
        if transcript_file.exists():
            print(f"   ✅ Loading cached transcript...")
            with open(transcript_file) as f:
                transcript_data = json.load(f)
            segments = transcript_data.get('segments', [])
            print(f"   ✅ Loaded {len(segments)} segments")
        
        else:
            print(f"   ⚠️  No cached transcript found")
            print(f"   🎙️  Creating transcript with AssemblyAI...")
            
            # Use AssemblyAI for transcription
            segments = await self._transcribe_with_assemblyai(selected_video)
            
            if not segments:
                print(f"   ❌ Transcription failed!")
                return None
            
            # Save transcript
            transcript_data = {
                'video_path': str(selected_video),
                'segments': segments,
                'created_at': datetime.now().isoformat(),
                'service': 'assemblyai'
            }
            
            with open(transcript_file, 'w') as f:
                json.dump(transcript_data, f, indent=2)
            
            print(f"   ✅ Transcript saved: {transcript_file}")
            print(f"   ✅ {len(segments)} segments")
        
        # Continue with NEW OPTIMIZED PIPELINE...
        # Quick story analysis for context
        story_context = {'storylines': []}  # Minimal story context
        
        # Run NEW optimized pipeline
        viral_moments = await self._find_moments_with_consensus(
            segments=segments,
            story=story_context
        )
        
        if not viral_moments:
            print("\n❌ Pipeline failed or no viral moments found!")
            return None
        
        # Convert to result format for compatibility
        result = {
            'story_structure': story_context,
            'moments': viral_moments,
            'clips': [],  # Will be populated if needed
            'stats': {
                'moments_found': len(viral_moments),
                'clips_restructured': 0,
                'quality_passed': len(viral_moments),
                'total_versions': len(viral_moments),
                'ai_consensus_used': True
            },
            'video_path': str(selected_video)
        }
        
        # Show results
        print("\n" + "="*70)
        print("📊 RESULTS")
        print("="*70)
        print(f"\n   Viral Moments Found: {len(viral_moments)}")
        
        # Show score distribution
        scores = [m.get('godmode_score', 0) for m in viral_moments]
        if scores:
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            print(f"   Average Score: {avg_score:.1f}/50")
            print(f"   Score Range: {min_score:.0f}-{max_score:.0f}/50")
        
        # Show top moments
        if viral_moments:
            print(f"\n   Top Viral Moments:")
            sorted_moments = sorted(viral_moments, key=lambda x: x.get('godmode_score', 0), reverse=True)
            for i, m in enumerate(sorted_moments[:5], 1):
                score = m.get('godmode_score', 0)
                duration = m.get('duration', 0)
                hook = m.get('hook_phrase', 'N/A')[:50]
                print(f"      {i}. Score: {score}/50, Duration: {duration:.1f}s - {hook}...")
        
        # Export prompt
        try:
            export = input("\n📦 Export clips? (y/n): ").strip().lower()
            
            if export == 'y':
                output_dir = self._export_viral_moments(viral_moments, selected_video)
                
                if output_dir:
                    print(f"\n✅ Clips exported to: {output_dir}")
                else:
                    print("\n⚠️  Export failed")
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Skipping export (non-interactive mode)")
        
        return result
    
    def _export_viral_moments(self, viral_moments: List[Dict], video_path: Path) -> str:
        """
        Export viral moments from new optimized pipeline
        
        Args:
            viral_moments: List of viral moments from _find_moments_with_consensus
            video_path: Path to source video file
            
        Returns:
            Output directory path or None if failed
        """
        import shutil
        import subprocess
        
        # Check ffmpeg availability
        if not shutil.which('ffmpeg'):
            print("\n⚠️  ffmpeg not found! Please install:")
            print("   brew install ffmpeg  # macOS")
            print("   apt install ffmpeg   # Linux")
            return None
        
        if not viral_moments:
            print("   ⚠️  No viral moments to export")
            return None
        
        print(f"\n🎬 Exporting {len(viral_moments)} clips...")
        
        # Create output directory
        output_dir = Path("output") / "viral_clips" / video_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export each viral moment
        exported_count = 0
        
        for i, moment in enumerate(viral_moments, 1):
            try:
                # Get timestamps
                start_time = float(moment.get('start', 0))
                end_time = float(moment.get('end', 0))
                duration = float(moment.get('duration', 0))
                score = int(moment.get('godmode_score', 0))
                
                # Create safe filename from first segment text
                segments = moment.get('segments', [])
                if segments:
                    first_text = segments[0].get('text', 'clip')
                    # Create safe filename (alphanumeric + spaces only, max 30 chars)
                    safe_text = ''.join(c for c in first_text[:50] if c.isalnum() or c.isspace())
                    safe_text = safe_text.strip().replace(' ', '_')[:30]
                else:
                    safe_text = f"clip_{i:02d}"
                
                # Create output filename
                output_file = output_dir / f"clip_{i:02d}_score{score}_{safe_text}.mp4"
                
                # Use ffmpeg to extract clip
                cmd = [
                    'ffmpeg',
                    '-i', str(video_path),
                    '-ss', str(start_time),
                    '-to', str(end_time),
                    '-c', 'copy',  # Stream copy (fast, no re-encoding)
                    '-avoid_negative_ts', 'make_zero',
                    '-y',  # Overwrite
                    str(output_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and output_file.exists():
                    exported_count += 1
                    print(f"   ✅ Clip {i}/{len(viral_moments)}: {output_file.name}")
                    
                    # Save metadata
                    metadata_file = output_file.with_suffix('.json')
                    metadata = {
                        'clip_number': i,
                        'start': start_time,
                        'end': end_time,
                        'duration': duration,
                        'godmode_score': score,
                        'godmode_verdict': moment.get('godmode_verdict', 'accept'),
                        'strengths': moment.get('godmode_strengths', []),
                        'weaknesses': moment.get('godmode_weaknesses', []),
                        'reasoning': moment.get('godmode_reasoning', ''),
                        'text': ' '.join([s.get('text', '') for s in segments]),
                        'viral_score': moment.get('viral_score', 0),
                        'refinement_reason': moment.get('refinement_reason', ''),
                        'restructured': moment.get('restructured', False),
                        'moment_type': moment.get('moment_type', 'unknown'),
                        'pattern': moment.get('pattern', 'unknown'),
                        'hook_phrase': moment.get('hook_phrase', ''),
                        'source_video': str(video_path)
                    }
                    
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                else:
                    error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                    print(f"   ❌ Clip {i} failed: {error_msg}")
                    
            except Exception as e:
                print(f"   ❌ Clip {i} export failed: {e}")
                import traceback
                print(f"      {traceback.format_exc()[:200]}")
        
        print(f"\n{'='*70}")
        print(f"✅ EXPORT COMPLETE")
        print(f"{'='*70}")
        print(f"   Exported: {exported_count}/{len(viral_moments)} clips")
        print(f"   Location: {output_dir}")
        print(f"   Format: MP4 + JSON metadata")
        print(f"{'='*70}")
        
        return str(output_dir) if exported_count > 0 else None
    
    def export_clips(self, result: Dict, video_path: str = None) -> str:
        """
        Export clips from V4 result format (legacy method for old pipeline)
        
        Transforms V4 format to V2 format for export
        """
        
        if not self.base_system:
            print("⚠️  Base system not available for export")
            return None
        
        # V4 format: result['clips'] = [{'clip': {...}, 'versions': [...]}]
        # V2 expects: extraction_result dict with 'clips' key and video_path as second arg
        clips_data = result.get('clips', [])
        
        if not clips_data:
            print("   ⚠️  No clips to export")
            return None
        
        # Get video_path from result or use provided
        video_path_to_use = video_path or result.get('video_path')
        
        if not video_path_to_use:
            print("   ⚠️  No video path provided")
            return None
        
        # Wrap clips_data in dict format expected by V2
        extraction_result = {
            'clips': clips_data
        }
        
        # Call base system export with both extraction_result and video_path
        output_dir = self.base_system.export_clips(
            extraction_result,
            video_path_to_use
        )
        
        return output_dir


# Main function for testing
async def test_integrated_pipeline():
    """Test the integrated pipeline with real video"""
    
    print("\n🧪 TESTING INTEGRATED PIPELINE WITH REAL VIDEO\n")
    
    # Initialize
    system = CreateClipsV4Integrated()
    
    # Get video from base system test
    video_path = "data/uploads/test.mp4"
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        print("\nUsage:")
        print("  python create_clips_v4_integrated.py")
        print("  Then select video when prompted")
        return
    
    # Load transcript
    print(f"📁 Loading video: {video_path}")
    
    # Get cached transcript
    if not system.base_system:
        print("❌ Base system not available")
        return
    
    # Check for cached transcript
    cache_dir = Path("data/cache/transcripts")
    cache_files = list(cache_dir.glob("*.json")) if cache_dir.exists() else []
    
    if not cache_files:
        print("❌ No cached transcript found")
        print("\nFirst run: python create_clips_v2.py to create transcript")
        return
    
    print(f"\n📦 Found {len(cache_files)} cached transcript(s)")
    print("   Using most recent...")
    
    # Load most recent
    latest = sorted(cache_files, key=lambda p: p.stat().st_mtime)[-1]
    with open(latest) as f:
        cached = json.load(f)
        segments = cached.get('segments', [])
    
    print(f"   ✅ Loaded {len(segments)} segments")
    
    # Run NEW optimized pipeline
    story_context = {'storylines': []}  # Minimal story context
    
    viral_moments = await system._find_moments_with_consensus(
        segments=segments,
        story=story_context
    )
    
    # Show results
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    print(f"\n   Viral Moments Found: {len(viral_moments)}")
    
    # Show score distribution
    if viral_moments:
        scores = [m.get('godmode_score', 0) for m in viral_moments]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        print(f"   Average Score: {avg_score:.1f}/50")
        print(f"   Score Range: {min_score:.0f}-{max_score:.0f}/50")
        
        # Show top moments
        print(f"\n   Top Viral Moments:")
        sorted_moments = sorted(viral_moments, key=lambda x: x.get('godmode_score', 0), reverse=True)
        for i, m in enumerate(sorted_moments[:5], 1):
            score = m.get('godmode_score', 0)
            duration = m.get('duration', 0)
            hook = m.get('hook_phrase', 'N/A')[:50]
            print(f"      {i}. Score: {score}/50, Duration: {duration:.1f}s - {hook}...")
    
    # Create result dict for compatibility
    result = {
        'story_structure': story_context,
        'moments': viral_moments,
        'clips': [],
        'stats': {
            'moments_found': len(viral_moments),
            'clips_restructured': 0,
            'quality_passed': len(viral_moments),
            'total_versions': len(viral_moments)
        }
    }
    
    # Export prompt
    try:
        export = input("\n📦 Export clips? (y/n): ").strip().lower()
        
        if export == 'y':
            output_dir = system._export_viral_moments(viral_moments, Path(video_path))
            
            if output_dir:
                print(f"\n✅ Clips exported to: {output_dir}")
            else:
                print("\n⚠️  Export failed")
    except (EOFError, KeyboardInterrupt):
        print("\n⚠️  Skipping export (non-interactive mode)")
    
    print("\n✅ Pipeline test complete!\n")


if __name__ == "__main__":
    import sys
    
    # Allow direct video path as argument
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    async def main():
        system = CreateClipsV4Integrated()
        result = await system.run(video_path=video_path)
        return result
    
    asyncio.run(main())

