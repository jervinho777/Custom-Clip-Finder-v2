#!/usr/bin/env python3
"""
Unified Viral Pattern Analyzer

Analyzes BOTH:
1. Isolated viral clips (with performance data)
2. Longform→Clip transformation pairs

Extracts PRINCIPLES (not rigid templates!)
Outputs: VIRAL_PRINCIPLES.json (Master Brain)
"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class ViralPatternAnalyzer:
    """
    Self-learning system that extracts principles from data
    """
    
    def __init__(self):
        self.data_dir = Path("data")
        self.output_dir = Path("data/learnings")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output files (as per diagram)
        self.isolated_patterns_file = self.output_dir / "ISOLATED_PATTERNS.json"
        self.composition_patterns_file = self.output_dir / "COMPOSITION_PATTERNS.json"
        self.viral_principles_file = self.output_dir / "VIRAL_PRINCIPLES.json"
    
    async def analyze_all(self):
        """
        Complete analysis pipeline
        """
        print(f"\n{'='*70}")
        print(f"🧠 VIRAL PATTERN ANALYZER - SELF-LEARNING SYSTEM")
        print(f"{'='*70}")
        
        # Phase 1: Analyze isolated viral clips
        print(f"\n📊 Phase 1: Analyzing Isolated Viral Clips...")
        isolated_patterns = await self.analyze_isolated_clips()
        self._save_json(isolated_patterns, self.isolated_patterns_file)
        print(f"   ✅ Saved: {self.isolated_patterns_file}")
        
        # Phase 2: Analyze longform→clip transformations
        print(f"\n🔄 Phase 2: Analyzing Longform→Clip Transformations...")
        composition_patterns = await self.analyze_transformation_pairs()
        self._save_json(composition_patterns, self.composition_patterns_file)
        print(f"   ✅ Saved: {self.composition_patterns_file}")
        
        # Phase 3: Synthesize into master principles
        print(f"\n🎯 Phase 3: Synthesizing Master Principles...")
        viral_principles = await self.synthesize_principles(
            isolated_patterns, 
            composition_patterns
        )
        self._save_json(viral_principles, self.viral_principles_file)
        print(f"   ✅ Saved: {self.viral_principles_file}")
        
        print(f"\n{'='*70}")
        print(f"✅ ANALYSIS COMPLETE - BRAIN UPDATED!")
        print(f"{'='*70}")
        
        return viral_principles
    
    async def analyze_isolated_clips(self) -> Dict:
        """
        Analyze isolated viral clips with performance data
        Extract: What makes them viral?
        """
        
        # Load goat_training_data.json
        goat_file = Path("data/training/goat_training_data.json")
        if not goat_file.exists():
            print(f"   ⚠️  goat_training_data.json not found")
            return {}
        
        with open(goat_file, 'r', encoding='utf-8') as f:
            clips = json.load(f)
        
        # Filter: High performers only (>1M views, >20% completion)
        high_performers = []
        for c in clips:
            perf = c.get('performance', {})
            views = perf.get('views', 0) or 0
            completion = perf.get('completion_rate', 0) or 0
            
            if views > 1_000_000 or completion > 0.20:
                high_performers.append(c)
        
        print(f"   Found {len(high_performers)} high-performing clips")
        
        if not high_performers:
            return {}
        
        # Analyze with AI (principle-based!)
        prompt = f"""
Analyze these {len(high_performers)} viral clips and extract PRINCIPLES.

CLIPS DATA (sample):
{json.dumps(high_performers[:3], indent=2, ensure_ascii=False)}

YOUR TASK:
Extract PRINCIPLES that explain viral success.

NOT: "Hook must be in first 3 seconds" (rigid rule)
BUT: "High-performing hooks create immediate curiosity gap" (principle)

NOT: "Duration must be 30-60s" (template)
BUT: "Duration balances completeness with engagement" (principle)

ANALYZE:
1. HOOK PATTERNS
   - What makes hooks work?
   - Different types observed?
   - Common elements?

2. DURATION INSIGHTS
   - How long are high performers?
   - Relationship to completion rate?
   - Content type differences?

3. STRUCTURE PATTERNS
   - What structures appear?
   - Are there different viable patterns?
   - Content-dependent structures?

4. ENGAGEMENT MECHANICS
   - What keeps people watching?
   - Pattern interrupts?
   - Emotional arcs?

5. CONTENT TYPE VARIATIONS
   - Do different types need different approaches?
   - Framework vs Story vs Rant patterns?

RESPONSE (JSON):
{{
  "metadata": {{
    "analyzed_clips": {len(high_performers)},
    "avg_views": "calculated from data",
    "avg_completion": "calculated from data"
  }},
  
  "principles": {{
    "hooks": {{
      "core_principle": "...",
      "observed_patterns": [...],
      "variations_by_type": {{...}}
    }},
    
    "duration": {{
      "core_principle": "...",
      "observations": [...],
      "content_type_ranges": {{...}}
    }},
    
    "structure": {{
      "core_principle": "...",
      "viable_patterns": [...],
      "context_dependencies": {{...}}
    }},
    
    "engagement": {{
      "core_principle": "...",
      "mechanics": [...],
      "timing_patterns": {{...}}
    }}
  }},
  
  "anti_patterns": [
    "What to avoid (from failures)"
  ]
}}

Extract PRINCIPLES, not templates!
Be flexible, acknowledge variations!
Return JSON only.
"""
        
        # Call AI for analysis
        try:
            from create_clips_v4_integrated import CreateClipsV4Integrated
            system = CreateClipsV4Integrated()
            
            if not system.consensus:
                print(f"   ⚠️  AI system not available - using fallback")
                return self._fallback_isolated_analysis(high_performers)
            
            response = await system.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral content pattern analyst. Extract principles, not rigid rules.",
                max_tokens=4000,
                temperature=0.7
            )
            
            patterns = system._parse_json_response(response)
            if patterns:
                patterns['analyzed_at'] = datetime.now().isoformat()
                return patterns
            else:
                return self._fallback_isolated_analysis(high_performers)
        except Exception as e:
            print(f"   ⚠️  AI analysis failed: {e}")
            return self._fallback_isolated_analysis(high_performers)
    
    def _fallback_isolated_analysis(self, clips: List[Dict]) -> Dict:
        """Fallback analysis if AI fails"""
        return {
            'metadata': {
                'analyzed_clips': len(clips),
                'analyzed_at': datetime.now().isoformat(),
                'method': 'fallback'
            },
            'principles': {
                'hooks': {
                    'core_principle': 'Stop scroll within 3 seconds',
                    'observed_patterns': ['curiosity_gap', 'bold_statement', 'question']
                },
                'duration': {
                    'core_principle': 'Balance completeness with engagement',
                    'observations': ['Varies by content type', 'Completeness matters more than fixed duration']
                }
            }
        }
    
    async def analyze_transformation_pairs(self) -> Dict:
        """
        Analyze Longform→Clip transformations
        Extract: How to compose viral clips from longform
        """
        
        # Find all pairs
        pairs = self._find_transformation_pairs()
        
        if not pairs:
            print(f"   ⚠️  No transformation pairs found")
            return {}
        
        print(f"   Found {len(pairs)} transformation pairs")
        
        # Analyze with AI
        prompt = f"""
Analyze these Longform→Clip transformation pairs.

PAIRS:
{json.dumps([{
    'name': p.get('name', 'unknown'),
    'longform_duration': p.get('longform_duration', 0),
    'clip_duration': p.get('clip_duration', 0),
    'transformation': p.get('transformation_notes', '')
} for p in pairs], indent=2, ensure_ascii=False)}

YOUR TASK:
Extract PRINCIPLES of viral composition.

ANALYZE:
1. HOOK EXTRACTION
   - Are hooks from same location as content?
   - Cross-moment composition patterns?
   - How to identify best hooks?

2. CUTTING PATTERNS
   - What gets removed?
   - What always stays?
   - Micro-cut principles?

3. TIMING & PACING
   - Are pauses added/removed?
   - Pacing changes?
   - Rhythm patterns?

4. STRUCTURAL TRANSFORMATION
   - How is content restructured?
   - Reordering patterns?
   - Emphasis shifts?

5. CONTENT TYPE ADAPTATION
   - Do different formats transform differently?
   - Podcast vs Stage vs Interview patterns?

RESPONSE (JSON):
{{
  "metadata": {{
    "analyzed_pairs": {len(pairs)},
    "avg_reduction": "calculated",
    "avg_views": "if available"
  }},
  
  "principles": {{
    "hook_extraction": {{
      "core_principle": "...",
      "cross_moment_patterns": [...],
      "selection_criteria": {{...}}
    }},
    
    "cutting": {{
      "core_principle": "...",
      "what_to_remove": [...],
      "what_to_preserve": [...],
      "micro_cut_patterns": {{...}}
    }},
    
    "timing": {{
      "core_principle": "...",
      "pause_patterns": [...],
      "pacing_adjustments": {{...}}
    }},
    
    "restructure": {{
      "core_principle": "...",
      "transformation_patterns": [...],
      "content_type_specific": {{...}}
    }}
  }}
}}

Focus on PRINCIPLES that work across content types!
Acknowledge variations where needed!
Return JSON only.
"""
        
        try:
            from create_clips_v4_integrated import CreateClipsV4Integrated
            system = CreateClipsV4Integrated()
            
            if not system.consensus:
                return self._fallback_composition_analysis(pairs)
            
            response = await system.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a viral composition analyst. Extract transformation principles.",
                max_tokens=4000,
                temperature=0.7
            )
            
            patterns = system._parse_json_response(response)
            if patterns:
                patterns['analyzed_at'] = datetime.now().isoformat()
                return patterns
            else:
                return self._fallback_composition_analysis(pairs)
        except Exception as e:
            print(f"   ⚠️  AI analysis failed: {e}")
            return self._fallback_composition_analysis(pairs)
    
    def _fallback_composition_analysis(self, pairs: List[Dict]) -> Dict:
        """Fallback analysis if AI fails"""
        return {
            'metadata': {
                'analyzed_pairs': len(pairs),
                'analyzed_at': datetime.now().isoformat(),
                'method': 'fallback'
            },
            'principles': {
                'hook_extraction': {
                    'core_principle': 'Best hooks may be anywhere in video',
                    'cross_moment_patterns': ['Thematic matching', 'Emotional resonance']
                },
                'cutting': {
                    'core_principle': 'Every word must earn its place',
                    'what_to_remove': ['Unnecessary descriptors', 'Filler words'],
                    'what_to_preserve': ['Core narrative', 'Emotional beats']
                }
            }
        }
    
    async def synthesize_principles(self, 
                                   isolated: Dict, 
                                   composition: Dict) -> Dict:
        """
        Synthesize both analyses into master principles
        This is the BRAIN that the composer uses!
        """
        
        isolated_principles = isolated.get('principles', {})
        composition_principles = composition.get('principles', {})
        
        prompt = f"""
Synthesize these two analyses into MASTER PRINCIPLES.

ISOLATED CLIP ANALYSIS:
{json.dumps(isolated_principles, indent=2, ensure_ascii=False)}

COMPOSITION ANALYSIS:
{json.dumps(composition_principles, indent=2, ensure_ascii=False)}

YOUR TASK:
Create UNIFIED principles that combine both perspectives.
The composer will use these principles to create viral clips.

Principles must be:
- Clear and actionable
- Flexible (not rigid templates)
- Context-aware (different content types)
- Evidence-based (from actual data)

RESPONSE (JSON):
{{
  "version": "2.0",
  "updated_at": "{datetime.now().isoformat()}",
  "core_algorithm": {{
    "principle": "Maximize watchtime through engagement",
    "metrics": ["completion_rate", "watch_time", "engagement"],
    "goal": "Make video impossible to scroll past"
  }},
  "hook_principles": {{
    "core": "Stop scroll within 3 seconds",
    "methods": [
      "Create curiosity gap",
      "Bold contrarian statement",
      "Provocative question",
      "Pattern interrupt",
      "Emotional trigger"
    ],
    "extraction": {{
      "principle": "Best hooks may be anywhere in video",
      "cross_moment_ok": true,
      "selection_criteria": ["strength", "thematic_match", "emotional_resonance"]
    }},
    "context_variations": {{
      "podcast": "More conversational, less aggressive",
      "stage_talk": "High energy, audience reactions matter",
      "educational": "Clarity over punchiness"
    }}
  }},
  "duration_principles": {{
    "core": "Balance completeness with engagement",
    "not_rigid_range": "Duration serves content, not template",
    "observations": [
      "High completion clips range 20-90s",
      "No single optimal duration",
      "Completeness matters more than brevity"
    ],
    "content_type_guidance": {{
      "story": "Complete arc matters more than duration",
      "insight": "Quick delivery if clear",
      "tutorial": "Completeness critical"
    }}
  }},
  "cutting_principles": {{
    "core": "Every word must earn its place",
    "what_to_cut": [
      "Unnecessary descriptors",
      "Verbose transitions",
      "Obvious statements",
      "Filler words (selective)",
      "Repetition (unless emphasis)"
    ],
    "what_to_preserve": [
      "Core narrative beats",
      "Emotional resonance moments",
      "Speaker authenticity",
      "Setup for payoff",
      "Pattern interrupts"
    ],
    "micro_cut_guidance": {{
      "principle": "Cut fat, keep muscle - but muscle includes emotion",
      "preserve_authenticity": true
    }}
  }},
  "timing_principles": {{
    "core": "Strategic silence creates impact",
    "when_to_pause": [
      "After rhetorical question (build tension)",
      "Before payoff (anticipation)",
      "After revelation (let it land)",
      "At emotional beats (breathing room)"
    ],
    "when_not_to_pause": [
      "During high-energy sequences",
      "In rapid-fire content",
      "When momentum matters more"
    ],
    "context_dependent": true
  }},
  "structure_principles": {{
    "core": "Structure adapts to content type",
    "viable_patterns": {{
      "story": "Setup → Escalation → Twist/Resolution",
      "insight": "Problem → Analysis → Solution",
      "rant": "Statement → Evidence → Conclusion",
      "tutorial": "Promise → Steps → Result",
      "revelation": "Question → Suspense → Answer",
      "parable": "Metaphor → Development → Lesson"
    }},
    "anti_pattern": "Forcing all content into one template"
  }},
  "composition_workflow": {{
    "principle": "Holistic optimization",
    "steps": [
      "Analyze content type",
      "Identify what's needed",
      "Apply relevant principles",
      "Optimize holistically",
      "Validate watchtime potential"
    ]
  }}
}}

These principles will guide the Multi-AI Composer.
Make them clear, actionable, and flexible!
Return JSON only.
"""
        
        try:
            from create_clips_v4_integrated import CreateClipsV4Integrated
            system = CreateClipsV4Integrated()
            
            if not system.consensus:
                return self._fallback_synthesis(isolated, composition)
            
            response = await system.consensus.single_ai_call(
                prompt=prompt,
                model='sonnet',
                system="You are a master principle synthesizer. Create unified, flexible principles.",
                max_tokens=5000,
                temperature=0.7
            )
            
            principles = system._parse_json_response(response)
            if principles:
                return principles
            else:
                return self._fallback_synthesis(isolated, composition)
        except Exception as e:
            print(f"   ⚠️  Synthesis failed: {e}")
            return self._fallback_synthesis(isolated, composition)
    
    def _fallback_synthesis(self, isolated: Dict, composition: Dict) -> Dict:
        """Fallback synthesis if AI fails"""
        return {
            'version': '2.0-fallback',
            'updated_at': datetime.now().isoformat(),
            'core_algorithm': {
                'principle': 'Maximize watchtime through engagement',
                'metrics': ['completion_rate', 'watch_time', 'engagement']
            },
            'hook_principles': {
                'core': 'Stop scroll within 3 seconds',
                'methods': ['curiosity_gap', 'bold_statement', 'question']
            },
            'duration_principles': {
                'core': 'Balance completeness with engagement'
            },
            'cutting_principles': {
                'core': 'Every word must earn its place'
            },
            'timing_principles': {
                'core': 'Strategic silence creates impact'
            },
            'structure_principles': {
                'core': 'Structure adapts to content type'
            }
        }
    
    def _find_transformation_pairs(self) -> List[Dict]:
        """Find all Longform→Clip pairs"""
        
        pairs = []
        
        # Example: Dieter Lange pair
        try:
            transcript_dir = Path("data/cache/transcripts")
            longform_file = transcript_dir / "Dieter Lange_transcript.json"
            
            if longform_file.exists():
                with open(longform_file, 'r', encoding='utf-8') as f:
                    longform = json.load(f)
                
                # Check if we have segment data
                segments = longform.get('segments', [])
                if segments:
                    pairs.append({
                        'name': 'Dieter_Lange',
                        'longform_duration': segments[-1].get('end', 0),
                        'longform_segments': len(segments),
                        'transformation_notes': 'Hook from different location, micro-cuts, 1.68s pause',
                        'source': 'Dieter Lange example'
                    })
        except Exception as e:
            pass  # Not critical if not found
        
        # TODO: Add more pairs as they become available
        # Could scan data/viral_examples/ for more pairs
        
        return pairs
    
    def _save_json(self, data: Dict, filepath: Path):
        """Save JSON with pretty formatting"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# CLI for running analysis
# ═══════════════════════════════════════════════════════════════

async def main():
    analyzer = ViralPatternAnalyzer()
    await analyzer.analyze_all()

if __name__ == '__main__':
    asyncio.run(main())

