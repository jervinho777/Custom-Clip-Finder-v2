#!/usr/bin/env python3
"""
Simplified Principle Synthesizer
Uses Anthropic API directly - no complex dependencies
"""

from dotenv import load_dotenv
load_dotenv()  # Load .env file

import json
import os
import traceback
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic

class SimplifiedSynthesizer:
    """Simplified synthesizer with direct API calls"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.learnings_dir = Path("data/learnings")
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        self.training_dir = Path("data/training")
    
    def synthesize(self):
        """Main synthesis workflow"""
        
        print(f"\n{'='*70}")
        print(f"🧠 PRINCIPLE SYNTHESIZER - Building Master Brain")
        print(f"{'='*70}")
        
        # Load data
        print(f"\n📊 Loading isolated clip patterns...")
        isolated = self._load_goat_data()
        print(f"   ✅ Loaded {len(isolated)} high-performing clips")
        
        print(f"\n🔄 Loading restructure analyses...")
        restructure = self._load_restructure_patterns()
        print(f"   ✅ Loaded {len(restructure)} transformation patterns")
        
        # Synthesize
        print(f"\n🎯 Synthesizing master principles...")
        principles = self._synthesize_with_ai(isolated, restructure)
        
        # Save
        output_file = self.learnings_dir / "VIRAL_PRINCIPLES.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(principles, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ SYNTHESIS COMPLETE")
        print(f"{'='*70}")
        print(f"   Output: {output_file}")
        print(f"   Version: {principles.get('version', 'unknown')}")
        print(f"   Ready for Composer!")
        
        return principles
    
    def _load_goat_data(self):
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
    
    def _load_restructure_patterns(self):
        """Load restructure analysis outputs"""
        
        patterns_dir = self.learnings_dir
        pattern_files = list(patterns_dir.glob("restructure_analysis_*.json"))
        
        patterns = []
        for pfile in pattern_files:
            try:
                with open(pfile, 'r', encoding='utf-8') as f:
                    patterns.append(json.load(f))
            except Exception as e:
                print(f"   ⚠️  Error loading {pfile.name}: {e}")
                pass
        
        return patterns
    
    def _synthesize_with_ai(self, isolated, restructure):
        """Use Anthropic API to synthesize principles"""
        
        # Calculate stats (don't include full transcripts!)
        total_views = sum(c['performance']['views'] for c in isolated)
        avg_views = total_views / len(isolated) if isolated else 0
        avg_completion = sum(c['performance'].get('completion_rate', 0) for c in isolated) / len(isolated) if isolated else 0
        
        # Sample durations
        durations = []
        for c in isolated[:50]:  # Sample only first 50
            if 'transcript' in c and 'segments' in c['transcript']:
                segments = c['transcript']['segments']
                if segments:
                    duration = segments[-1]['end'] - segments[0]['start']
                    durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Build SIMPLIFIED prompt with STATS only
        prompt = f"""Create viral composition principles from data analysis.

DATA ANALYZED:
- {len(isolated)} high-performing viral clips
- {len(restructure)} longform→clip transformations
- Total views analyzed: {total_views:,.0f}
- Average completion rate: {avg_completion:.1%}
- Duration range: {min_duration:.0f}s - {max_duration:.0f}s (avg: {avg_duration:.0f}s)

TASK:
Create master principles for viral clip composition.

PRINCIPLES MUST BE:
1. Flexible (not rigid templates)
2. Actionable (AI composer can apply them)
3. Content-type aware (different types need different approaches)
4. Evidence-based (from real performance data)

RESPONSE FORMAT (JSON):
{{
  "version": "2.0",
  "updated_at": "{datetime.now().isoformat()}",
  
  "core_algorithm": {{
    "principle": "Maximize watchtime through engagement",
    "goal": "Create content impossible to scroll past"
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
      "principle": "Best hooks can come from anywhere in video",
      "cross_moment_composition": true
    }},
    "context_variations": {{
      "podcast": "Conversational hooks work",
      "stage_talk": "High energy openings",
      "educational": "Clear value proposition"
    }}
  }},
  
  "duration_principles": {{
    "core": "Balance completeness with engagement",
    "flexible": true,
    "observations": [
      "High-performing clips range {min_duration:.0f}s-{max_duration:.0f}s",
      "Completeness matters more than duration",
      "Content type determines optimal length"
    ],
    "by_content_type": {{
      "story": "Complete narrative arc essential",
      "insight": "Quick if clear, longer if complex",
      "tutorial": "Completeness critical"
    }}
  }},
  
  "cutting_principles": {{
    "core": "Every word must earn its place",
    "what_to_cut": [
      "Unnecessary descriptors",
      "Verbose transitions",
      "Obvious statements",
      "Some filler (but preserve authenticity!)"
    ],
    "what_to_preserve": [
      "Core narrative beats",
      "Emotional resonance",
      "Speaker authenticity",
      "Payoff setup"
    ]
  }},
  
  "timing_principles": {{
    "core": "Strategic silence creates impact",
    "when_to_pause": [
      "After rhetorical questions",
      "Before payoffs",
      "After revelations",
      "At emotional beats"
    ],
    "context_dependent": true
  }},
  
  "structure_principles": {{
    "core": "Structure adapts to content type",
    "patterns_by_type": {{
      "story": "Setup → Escalation → Resolution",
      "insight": "Problem → Analysis → Solution",
      "rant": "Statement → Evidence → Conclusion",
      "tutorial": "Promise → Steps → Result",
      "revelation": "Question → Suspense → Answer"
    }},
    "anti_pattern": "Forcing all content into one template"
  }},
  
  "composition_workflow": {{
    "principle": "Holistic optimization",
    "approach": "AI decides what each moment needs",
    "not_forced_pipeline": true
  }}
}}

Create principles that are CLEAR, ACTIONABLE, and FLEXIBLE.
Base on the performance data statistics provided."""

        try:
            # Call API with simplified prompt
            print(f"   🔄 Calling Claude Sonnet 4.5...")
            print(f"   📝 Prompt length: {len(prompt)} characters")
            
            message = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            print(f"   ✅ API call successful")
            print(f"   📦 Response type: {type(message)}")
            print(f"   📦 Content type: {type(message.content)}")
            print(f"   📦 Content length: {len(message.content) if hasattr(message.content, '__len__') else 'N/A'}")
            
            # Debug: Print full message structure
            print(f"   🔍 Full message object:")
            print(f"      - id: {message.id}")
            print(f"      - model: {message.model}")
            print(f"      - role: {message.role}")
            print(f"      - stop_reason: {message.stop_reason}")
            print(f"      - stop_sequence: {message.stop_sequence}")
            print(f"      - type: {message.type}")
            print(f"      - usage: {message.usage}")
            print(f"      - content: {message.content}")
            
            # Check if there's an error in stop_reason
            if message.stop_reason and message.stop_reason != "end_turn":
                print(f"   ⚠️  Stop reason: {message.stop_reason}")
            
            # Check usage tokens
            if hasattr(message, 'usage'):
                print(f"   📊 Tokens used:")
                print(f"      - Input: {message.usage.input_tokens}")
                print(f"      - Output: {message.usage.output_tokens}")
            
            # Extract response with better error handling
            if not message.content:
                raise ValueError("Empty response from API")
            
            # Handle different response formats
            if isinstance(message.content, list):
                if len(message.content) == 0:
                    raise ValueError("Empty content list")
                first_item = message.content[0]
                if hasattr(first_item, 'text'):
                    response_text = first_item.text
                elif isinstance(first_item, str):
                    response_text = first_item
                else:
                    response_text = str(first_item)
            elif hasattr(message.content, 'text'):
                response_text = message.content.text
            elif isinstance(message.content, str):
                response_text = message.content
            else:
                response_text = str(message.content)
            
            print(f"   📝 Response length: {len(response_text)} characters")
            
            # Try to extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            # Parse JSON
            principles = json.loads(json_text)
            
            print(f"   ✅ AI synthesis successful!")
            print(f"   📊 Principles version: {principles.get('version', 'unknown')}")
            
            return principles
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parsing failed: {e}")
            if 'response_text' in locals():
                print(f"   📝 Response preview: {response_text[:500]}...")
            print(f"   → Using fallback principles")
            return self._get_fallback_principles()
            
        except Exception as e:
            print(f"   ⚠️  AI synthesis failed: {e}")
            print(f"   🔍 Error type: {type(e).__name__}")
            print(f"   📋 Traceback:")
            traceback.print_exc()
            print(f"   → Using fallback principles")
            return self._get_fallback_principles()
    
    def _get_fallback_principles(self):
        """Fallback principles if AI fails"""
        return {
            "version": "2.0-fallback",
            "updated_at": datetime.now().isoformat(),
            "note": "AI synthesis failed, using basic principles",
            "data_sources": {
                "isolated_clips": 0,
                "transformations": 0
            },
            "core_algorithm": {
                "principle": "Maximize watchtime through engagement",
                "metrics": ["completion_rate", "watch_time", "engagement"]
            },
            "hook_principles": {
                "core": "Stop scroll within 3 seconds",
                "methods": ["curiosity_gap", "bold_statement", "question", "pattern_interrupt"],
                "extraction_strategy": {
                    "principle": "Best hooks can come from anywhere in video",
                    "cross_moment_ok": True
                }
            },
            "duration_principles": {
                "core": "Balance completeness with engagement",
                "observations": [
                    "High completion clips range 20-90s",
                    "Completeness matters more than duration"
                ]
            },
            "cutting_principles": {
                "core": "Every word must earn its place",
                "what_to_cut": ["Unnecessary descriptors", "Filler words"],
                "what_to_preserve": ["Core narrative", "Emotional beats"]
            },
            "timing_principles": {
                "core": "Strategic silence creates impact",
                "when_to_pause": ["After questions", "Before payoff"]
            },
            "structure_principles": {
                "core": "Structure adapts to content type",
                "viable_patterns": {
                    "story": "Setup → Escalation → Resolution",
                    "insight": "Problem → Analysis → Solution"
                }
            }
        }


def main():
    synthesizer = SimplifiedSynthesizer()
    synthesizer.synthesize()

if __name__ == '__main__':
    main()
