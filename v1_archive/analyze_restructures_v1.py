#!/usr/bin/env python3
"""
Analyze Restructure Patterns v1

Uses 6-AI ensemble to analyze longform→clip pairs and extract
restructure learnings (what to keep, what to remove, timing rules)

Matching architecture of analyze_and_learn_v2.py
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys

sys.path.insert(0, str(Path(__file__).parent))

from create_clips_v3_ensemble import PremiumAIEnsemble, ConsensusEngine


class CreateClipsV3Ensemble:
    """Wrapper for ensemble + consensus engine"""
    
    def __init__(self):
        self.ensemble = PremiumAIEnsemble()
        self.consensus = ConsensusEngine(self.ensemble)
        self.usage_stats = self.ensemble.usage_stats
    
    async def build_consensus(self, prompt: str, system: str = None, strategy: str = 'parallel_vote') -> Dict:
        """Build consensus using consensus engine"""
        return await self.consensus.build_consensus(prompt, system, strategy)


class RestructureAnalyzer:
    """Analyze restructure patterns with 6-AI ensemble"""
    
    def __init__(self):
        self.ensemble = CreateClipsV3Ensemble()
        self.examples_dir = Path("data/restructure_examples")
        self.output_dir = Path("data/learnings")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.examples = []
        self.patterns = []
    
    def load_examples(self):
        """Load all prepared examples"""
        
        print(f"\n{'='*70}")
        print(f"📚 LOADING EXAMPLES")
        print(f"{'='*70}")
        
        example_dirs = sorted(self.examples_dir.glob("example_*"))
        
        for example_dir in example_dirs:
            metadata_file = example_dir / 'metadata.json'
            
            if not metadata_file.exists():
                print(f"   ⚠️  Skipping {example_dir.name} (no metadata)")
                continue
            
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            # Load transcripts
            longform_transcript_file = example_dir / 'longform_transcript.json'
            clip_transcript_file = example_dir / 'viral_clip_transcript.json'
            
            if not longform_transcript_file.exists() or not clip_transcript_file.exists():
                print(f"   ⚠️  Skipping {example_dir.name} (missing transcripts)")
                continue
            
            with open(longform_transcript_file) as f:
                longform_data = json.load(f)
            
            with open(clip_transcript_file) as f:
                clip_data = json.load(f)
            
            example = {
                'id': metadata['example_id'],
                'metadata': metadata,
                'longform': {
                    'segments': longform_data['segments'],
                    'duration': metadata['longform']['duration'],
                    'segment_count': len(longform_data['segments'])
                },
                'clip': {
                    'segments': clip_data['segments'],
                    'duration': metadata['viral_clip']['duration'],
                    'segment_count': len(clip_data['segments']),
                    'views': metadata['viral_clip'].get('views'),
                    'vir_score': metadata['viral_clip'].get('vir_score')
                }
            }
            
            self.examples.append(example)
            
            print(f"\n   ✅ {metadata['example_id']}")
            print(f"      Longform: {metadata['longform']['duration']:.1f}s ({metadata['longform']['segments']} segments)")
            print(f"      Clip: {metadata['viral_clip']['duration']:.1f}s ({metadata['viral_clip']['segments']} segments)")
            if example['clip']['views']:
                print(f"      Views: {example['clip']['views']:,}")
        
        print(f"\n   📊 Total examples loaded: {len(self.examples)}")
        
        return self.examples
    
    async def analyze_example(self, example: Dict) -> Dict:
        """
        Analyze single example with 6-AI ensemble
        
        Asks: What was kept? What was removed? Why?
        """
        
        print(f"\n{'='*70}")
        print(f"🔬 ANALYZING: {example['id']}")
        print(f"{'='*70}")
        
        # Prepare context for AIs
        longform_text = self._format_segments(example['longform']['segments'])
        clip_text = self._format_segments(example['clip']['segments'])
        
        # Find which segments were selected
        selected_info = self._find_selected_segments(
            example['longform']['segments'],
            example['clip']['segments']
        )
        
        print(f"\n   📊 Segment Selection:")
        print(f"      Longform: {example['longform']['segment_count']} segments")
        print(f"      Clip: {example['clip']['segment_count']} segments")
        print(f"      Matched: {selected_info['matched_count']} segments")
        print(f"      Coverage: {selected_info['coverage']:.0%}")
        
        # Create prompt for AI analysis
        
        # Format views safely
        views_text = f"{example['clip']['views']:,}" if example['clip']['views'] else "Unknown"
        viral_text = "(proven viral)" if example['clip']['views'] and example['clip']['views'] > 1_000_000 else ""
        
        prompt = f"""
RESTRUCTURE ANALYSIS - Longform → Viral Clip

LONGFORM VIDEO ({example['longform']['duration']:.0f}s, {example['longform']['segment_count']} segments):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{longform_text[:3000]}
[...full {example['longform']['segment_count']} segments]

VIRAL CLIP ({example['clip']['duration']:.0f}s, {example['clip']['segment_count']} segments):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{clip_text}

SELECTION INFO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Selected segments: {selected_info['selected_indices']}
Compression ratio: {example['clip']['duration']/example['longform']['duration']:.1%}
Views: {views_text} {viral_text}

YOUR TASK:
Extract PRINCIPLES (not rigid templates!) from this transformation.

CRITICAL: 
❌ NOT: "Clip must be 30-60 seconds" (rigid rule)
✅ BUT: "Duration balances completeness with engagement" (principle)

❌ NOT: "Hook in first 3 seconds always" (template)
✅ BUT: "Strong opening captures attention immediately" (principle)

RESPOND WITH JSON:
{{
  "composition_principles": {{
    "hook_extraction": {{
      "principle": "Best hooks can come from anywhere in video",
      "observations": [
        "Cross-moment composition works (e.g., hook from min 10, story from min 9)",
        "Thematic relevance matters more than proximity",
        "Hook strength trumps location"
      ],
      "context_variations": {{
        "content_type_differences": "Different types may need different approaches"
      }}
    }},
    
    "cutting_principles": {{
      "principle": "Every word must earn its place",
      "what_to_cut": [
        "Unnecessary descriptors without value",
        "Verbose transitions",
        "Obvious statements",
        "Filler (but preserve authenticity!)"
      ],
      "what_to_preserve": [
        "Core narrative beats",
        "Emotional resonance",
        "Speaker's natural voice",
        "Setup that makes payoff land"
      ],
      "micro_cut_patterns": [
        "Observed micro-cuts and their reasoning"
      ]
    }},
    
    "duration_principles": {{
      "principle": "Duration serves content, not arbitrary targets",
      "observations": [
        "This clip: {example['clip']['duration']:.0f}s works because...",
        "Compression: {example['clip']['duration']/example['longform']['duration']:.1%} - why this ratio?",
        "Completeness vs engagement balance"
      ],
      "content_type_context": "How content type affects duration"
    }},
    
    "timing_principles": {{
      "principle": "Strategic timing creates impact",
      "pause_patterns": [
        "Where pauses were added/removed and why"
      ],
      "pacing_observations": [
        "How pacing changed and impact"
      ],
      "context_dependent": "Timing varies by content type"
    }},
    
    "structure_principles": {{
      "principle": "Structure adapts to content type",
      "observed_pattern": "What structure was used (story/insight/etc)",
      "why_it_works": "Why this structure serves this content",
      "variations": "How it might differ for other content types"
    }}
  }},
  
  "anti_patterns": [
    "What was avoided and why",
    "Common mistakes this transformation avoided"
  ],
  
  "transferability": {{
    "universal_principles": ["Principles that apply to all content"],
    "content_specific": ["What's specific to this type"],
    "adaptation_guidance": "How to adapt to different content"
  }}
}}

Focus on PRINCIPLES that can adapt to different content!
Acknowledge variations and context-dependencies!
Evidence-based but flexible!
"""

        system = """You are an expert video editor and viral content analyst.

You analyze successful longform→clip restructures to extract PRINCIPLES (not rigid rules!).

Your analysis must be:
- PRINCIPLE-BASED (flexible guidelines, not rigid templates)
- EVIDENCE-BASED (based on this specific example)
- CONTEXT-AWARE (acknowledges variations by content type)
- TRANSFERABLE (applies to other videos but adapts)

CRITICAL DIFFERENCES:
❌ NOT: "Hook must be in first 3 seconds" (rigid rule)
✅ BUT: "Strong opening captures attention immediately" (principle)

❌ NOT: "Clip must be 30-60 seconds" (template)
✅ BUT: "Duration balances completeness with engagement" (principle)

You understand:
- What makes clips go viral (2.4M views)
- How to cut content for maximum retention
- Timing and pacing optimization
- Story structure in short-form
- Different content types need different approaches

CRITICAL: Return ONLY valid JSON, no preamble."""

        print(f"\n   🤖 Querying 6-AI ensemble...")
        
        # Get consensus from 6 AIs
        result = await self.ensemble.build_consensus(
            prompt=prompt,
            system=system,
            strategy='parallel_vote'
        )
        
        print(f"\n   ✅ Consensus confidence: {result.get('confidence', 0):.0%}")
        
        # Parse response
        try:
            # Try to extract JSON from response
            response_text = result.get('consensus', '')
            
            # Find JSON in response
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
            
            analysis = json.loads(json_text)
            
            print(f"   ✅ Analysis extracted")
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parsing failed: {e}")
            print(f"   Response preview: {response_text[:200]}...")
            analysis = {
                'error': 'Failed to parse',
                'raw_response': response_text[:500]
            }
        
        # Add metadata
        analysis['example_id'] = example['id']
        analysis['selection_info'] = selected_info
        analysis['compression_ratio'] = example['clip']['duration'] / example['longform']['duration']
        analysis['views'] = example['clip']['views']
        analysis['confidence'] = result.get('confidence', 0)
        
        return analysis
    
    def _format_segments(self, segments: List[Dict]) -> str:
        """Format segments for prompt"""
        
        formatted = []
        for i, seg in enumerate(segments):
            formatted.append(f"[{seg['start']:.1f}s] {seg['text']}")
        
        return '\n'.join(formatted)
    
    def _find_selected_segments(self, longform_segs: List[Dict], clip_segs: List[Dict]) -> Dict:
        """Find which longform segments were used in clip"""
        
        selected_indices = []
        matched_count = 0
        
        for clip_seg in clip_segs:
            clip_words = set(clip_seg['text'].lower().split())
            
            best_match_idx = None
            best_similarity = 0
            
            for i, long_seg in enumerate(longform_segs):
                long_words = set(long_seg['text'].lower().split())
                
                intersection = len(clip_words & long_words)
                union = len(clip_words | long_words)
                similarity = intersection / union if union > 0 else 0
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_idx = i
            
            if best_similarity > 0.3:
                selected_indices.append(best_match_idx)
                matched_count += 1
        
        return {
            'selected_indices': sorted(set(selected_indices)),
            'matched_count': matched_count,
            'coverage': matched_count / len(clip_segs) if clip_segs else 0
        }
    
    async def analyze_all(self):
        """Analyze all examples"""
        
        analyses = []
        
        for i, example in enumerate(self.examples, 1):
            print(f"\n{'='*70}")
            print(f"📊 EXAMPLE {i}/{len(self.examples)}")
            print(f"{'='*70}")
            
            analysis = await self.analyze_example(example)
            analyses.append(analysis)
            
            # Save individual analysis
            output_file = self.output_dir / f"restructure_analysis_{example['id']}.json"
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print(f"\n   💾 Saved: {output_file.name}")
        
        return analyses
    
    def synthesize_learnings(self, analyses: List[Dict]) -> Dict:
        """
        Synthesize all analyses into master learnings
        
        Combines patterns from all examples (principle-based format)
        """
        
        print(f"\n{'='*70}")
        print(f"🧠 SYNTHESIZING MASTER LEARNINGS")
        print(f"{'='*70}")
        
        # Collect all principle-based patterns
        all_composition_principles = []
        all_anti_patterns = []
        all_transferability = []
        
        # Also collect legacy format for backward compatibility
        all_selection_rules = []
        all_timing_patterns = []
        all_content_patterns = []
        all_quality_indicators = []
        
        for analysis in analyses:
            if 'error' in analysis:
                continue
            
            # New principle-based format
            if 'composition_principles' in analysis:
                all_composition_principles.append(analysis['composition_principles'])
            
            if 'anti_patterns' in analysis:
                all_anti_patterns.extend(analysis['anti_patterns'])
            
            if 'transferability' in analysis:
                all_transferability.append(analysis['transferability'])
            
            # Legacy format (for backward compatibility)
            all_selection_rules.extend(analysis.get('segment_selection_rules', []))
            
            timing = analysis.get('timing_patterns', {})
            if timing:
                all_timing_patterns.append(timing)
            
            content = analysis.get('content_patterns', {})
            if content:
                all_content_patterns.append(content)
            
            quality = analysis.get('quality_indicators', {})
            if quality:
                all_quality_indicators.append(quality)
        
        # Synthesize (principle-based + legacy)
        learnings = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'examples_analyzed': len(analyses),
                'version': 'v2.0-principle-based',
                'format': 'principle-based with legacy compatibility'
            },
            'composition_principles': {
                'patterns': all_composition_principles,
                'count': len(all_composition_principles)
            },
            'anti_patterns': {
                'patterns': list(set(all_anti_patterns)),
                'count': len(all_anti_patterns)
            },
            'transferability': {
                'patterns': all_transferability,
                'count': len(all_transferability)
            },
            # Legacy format (for backward compatibility)
            'segment_selection': {
                'rules': list(set(all_selection_rules)),
                'count': len(all_selection_rules)
            },
            'timing_optimization': {
                'patterns': all_timing_patterns,
                'count': len(all_timing_patterns)
            },
            'content_characteristics': {
                'patterns': all_content_patterns,
                'count': len(all_content_patterns)
            },
            'quality_signals': {
                'patterns': all_quality_indicators,
                'count': len(all_quality_indicators)
            },
            'examples': [
                {
                    'id': a['example_id'],
                    'compression': a.get('compression_ratio', 0),
                    'views': a.get('views'),
                    'confidence': a.get('confidence', 0),
                    'has_principles': 'composition_principles' in a
                }
                for a in analyses if 'error' not in a
            ]
        }
        
        print(f"\n   📊 Statistics:")
        print(f"      Composition principles: {len(all_composition_principles)}")
        print(f"      Anti-patterns: {len(all_anti_patterns)}")
        print(f"      Transferability patterns: {len(all_transferability)}")
        print(f"      (Legacy: Selection rules: {len(all_selection_rules)})")
        
        return learnings
    
    async def run(self):
        """Run complete analysis pipeline"""
        
        print(f"\n{'='*70}")
        print(f"🧠 RESTRUCTURE PATTERN ANALYZER V1")
        print(f"{'='*70}")
        
        # Load examples
        self.load_examples()
        
        if not self.examples:
            print(f"\n❌ No examples found!")
            print(f"   Run: python prepare_restructure_data.py first")
            return
        
        if len(self.examples) < 3:
            print(f"\n⚠️  Only {len(self.examples)} examples")
            print(f"   Recommend 5+ for good patterns")
            response = input("\nContinue anyway? (y/n): ").strip().lower()
            if response != 'y':
                return
        
        # Analyze all
        print(f"\n{'='*70}")
        print(f"🔬 STARTING AI ANALYSIS")
        print(f"{'='*70}")
        print(f"\n   Using 6-AI ensemble:")
        print(f"   • GPT-5.2")
        print(f"   • Opus 4.5")
        print(f"   • Sonnet 4.5")
        print(f"   • Gemini 2.5 Pro")
        print(f"   • DeepSeek V3.2")
        print(f"   • Grok 4.1")
        
        analyses = await self.analyze_all()
        
        # Synthesize learnings
        learnings = self.synthesize_learnings(analyses)
        
        # Save master learnings (legacy format)
        learnings_file = self.output_dir / 'RESTRUCTURE_LEARNINGS_V1.json'
        with open(learnings_file, 'w') as f:
            json.dump(learnings, f, indent=2)
        
        # NEW: Synthesize into COMPOSITION_PATTERNS.json for Code 3
        print(f"\n{'='*70}")
        print(f"🔄 CODE 2: SYNTHESIZING COMPOSITION PATTERNS")
        print(f"{'='*70}")
        composition_patterns = await self._synthesize_composition_patterns(analyses)
        
        # Save COMPOSITION_PATTERNS.json
        composition_file = self.output_dir / 'COMPOSITION_PATTERNS.json'
        with open(composition_file, 'w', encoding='utf-8') as f:
            json.dump(composition_patterns, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ CODE 2 COMPLETE")
        print(f"{'='*70}")
        print(f"\n   💾 Master learnings: {learnings_file}")
        print(f"   💾 Composition patterns: {composition_file}")
        print(f"   📊 Examples analyzed: {len(analyses)}")
        print(f"   🧠 Patterns extracted: {learnings['segment_selection']['count']}")
        
        # Show cost
        total_cost = self.ensemble.ensemble.usage_stats.get('total_cost', 0)
        print(f"\n   💰 Total cost: ${total_cost:.2f}")
        
        print(f"\n{'='*70}")
        print(f"🎯 NEXT STEPS")
        print(f"{'='*70}")
        print(f"\n   1. Review learnings: {learnings_file}")
        print(f"   2. Integrate into V4 restructure logic")
        print(f"   3. Test on new videos!")
        
        return learnings
    
    async def _synthesize_composition_patterns(self, analyses: List[Dict]) -> Dict:
        """
        Synthesize all pair analyses into COMPOSITION_PATTERNS.json
        Format optimized for Code 3 merger
        """
        
        # Collect all composition principles
        all_hook_extraction = []
        all_cutting_principles = []
        all_timing_patterns = []
        all_structural_transformations = []
        all_anti_patterns = []
        
        for analysis in analyses:
            if 'error' in analysis:
                continue
            
            # Extract composition principles
            comp = analysis.get('composition_principles', {})
            
            if 'hook_extraction' in comp:
                all_hook_extraction.append(comp['hook_extraction'])
            
            if 'cutting_principles' in comp:
                all_cutting_principles.append(comp['cutting_principles'])
            
            if 'timing_principles' in comp:
                all_timing_patterns.append(comp['timing_principles'])
            
            if 'structure_principles' in comp:
                all_structural_transformations.append(comp['structure_principles'])
            
            if 'anti_patterns' in analysis:
                all_anti_patterns.extend(analysis.get('anti_patterns', []))
        
        # Build composition patterns structure
        composition_patterns = {
            "data_source": {
                "pairs_analyzed": len(analyses),
                "analyzed_at": datetime.now().isoformat()
            },
            "hook_extraction": {
                "principle": "Best hooks can come from anywhere in video",
                "patterns": all_hook_extraction,
                "count": len(all_hook_extraction)
            },
            "cutting_principles": {
                "principle": "Every word must earn its place",
                "patterns": all_cutting_principles,
                "count": len(all_cutting_principles)
            },
            "timing_patterns": {
                "principle": "Strategic timing creates impact",
                "patterns": all_timing_patterns,
                "count": len(all_timing_patterns)
            },
            "structural_transformations": {
                "principle": "Structure adapts to content type",
                "patterns": all_structural_transformations,
                "count": len(all_structural_transformations)
            },
            "anti_patterns": {
                "patterns": list(set(all_anti_patterns)),
                "count": len(all_anti_patterns)
            }
        }
        
        return composition_patterns


async def main():
    """Main entry point"""
    
    analyzer = RestructureAnalyzer()
    await analyzer.run()


if __name__ == '__main__':
    asyncio.run(main())

