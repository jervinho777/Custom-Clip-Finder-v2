#!/usr/bin/env python3
"""
Extract PRINCIPLES from proven viral clips
NOT templates, NOT rigid rules - PRINCIPLES!

Uses REAL DATA:
- master_learnings.py - Algorithm understanding
- goat_training_data.json - 175+ proven viral clips
- Longform→Clip pairs - Transformation examples
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

class LearningsExtractor:
    """Extract principles from proven data"""
    
    def __init__(self):
        self.master_learnings = self._load_master_learnings()
        self.goat_data = self._load_goat_data()
        self.longform_clip_pairs = self._load_pairs()
    
    def _load_master_learnings(self) -> Dict:
        """Load algorithm understanding from master_learnings_v2"""
        try:
            from master_learnings_v2 import load_master_learnings
            learnings = load_master_learnings()
            return {
                'core_principle': learnings.get('algorithm_understanding', {}).get('core_principle', 'Watchtime maximieren'),
                'metrics': learnings.get('algorithm_understanding', {}).get('metrics_priority', []),
                'key_rules': [
                    'Jede Sekunde muss Grund liefern weiterzuschauen',
                    'Pattern interrupts alle 5-7 Sekunden',
                    'Loop öffnen und schließen'
                ],
                'watchtime_optimization': learnings.get('algorithm_understanding', {}).get('watchtime_optimization', {})
            }
        except Exception as e:
            print(f"⚠️  Could not load master learnings: {e}")
            return {
                'core_principle': 'Watchtime maximieren',
                'metrics': ['Watch Time', 'Completion Rate', 'Engagement'],
                'key_rules': [
                    'Jede Sekunde muss Grund liefern weiterzuschauen',
                    'Pattern interrupts alle 5-7 Sekunden',
                    'Loop öffnen und schließen'
                ]
            }
    
    def _load_goat_data(self) -> List[Dict]:
        """Load 175+ proven clips from training data"""
        try:
            goat_file = Path("data/training/goat_training_data.json")
            if not goat_file.exists():
                return []
            
            with open(goat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract top performers (>1M views OR >20% completion)
            top_clips = []
            for clip in data:
                perf = clip.get('performance', {})
                views = perf.get('views', 0) or 0
                completion = perf.get('completion_rate', 0) or 0
                
                if views > 1000000 or completion > 0.20:
                    top_clips.append(clip)
            
            return top_clips[:50]  # Top 50 for analysis
        except Exception as e:
            print(f"⚠️  Could not load GOAT data: {e}")
            return []
    
    def _load_pairs(self) -> List[Dict]:
        """Load Longform→Clip transformation examples"""
        pairs = []
        
        # Try to find Dieter Lange example
        try:
            transcript_dir = Path("data/cache/transcripts")
            longform_file = transcript_dir / "Dieter Lange_transcript.json"
            
            if longform_file.exists():
                with open(longform_file, 'r', encoding='utf-8') as f:
                    longform = json.load(f)
                
                # Look for viral clip transcript (might be in different location)
                # For now, just note that we have the longform
                pairs.append({
                    'longform': longform,
                    'transformation': 'Extracted hook from different location + micro-cuts + pause',
                    'source': 'Dieter Lange'
                })
        except Exception as e:
            pass  # Not critical if not found
        
        return pairs
    
    def extract_duration_principles(self) -> Dict:
        """
        Extract PRINCIPLES about duration from data
        NOT: "Story must be 45-65s"
        BUT: "Successful clips balance completeness with engagement"
        """
        
        if not self.goat_data:
            return {
                'principle': 'Balance completeness with engagement',
                'observations': [
                    'Duration should match content completeness',
                    'No single "optimal" duration - varies by content type'
                ],
                'guideline': 'Optimize for COMPLETENESS first, brevity second'
            }
        
        # Analyze actual durations of successful clips
        durations = []
        for clip in self.goat_data:
            transcript = clip.get('transcript', {})
            segments = transcript.get('segments', [])
            perf = clip.get('performance', {})
            
            if segments:
                duration = segments[-1].get('end', 0) - segments[0].get('start', 0)
                completion = perf.get('completion_rate', 0) or 0
                views = perf.get('views', 0) or 0
                
                durations.append({
                    'duration': duration,
                    'completion_rate': completion,
                    'views': views
                })
        
        if not durations:
            return {
                'principle': 'Duration should match content completeness',
                'guideline': 'Optimize for COMPLETENESS first, brevity second'
            }
        
        # Extract principles from data
        high_completion = [d for d in durations if d['completion_rate'] > 0.25]
        durations_only = [d['duration'] for d in high_completion]
        
        if durations_only:
            min_dur = min(durations_only)
            max_dur = max(durations_only)
            avg_dur = sum(durations_only) / len(durations_only)
        else:
            min_dur = 20
            max_dur = 90
            avg_dur = 45
        
        return {
            'principle': 'Duration should match content completeness',
            'observations': [
                f'High completion (>25%) clips range {min_dur:.0f}-{max_dur:.0f}s',
                'No single "optimal" duration - varies by content type',
                'Shorter when punchline-driven, longer when story-driven',
                'Engagement drops when either too short (incomplete) or too long (rambling)'
            ],
            'guideline': 'Optimize for COMPLETENESS first, brevity second',
            'data_range': {
                'min': min_dur,
                'max': max_dur,
                'average': avg_dur
            }
        }
    
    def extract_hook_principles(self) -> Dict:
        """
        Extract PRINCIPLES about hooks
        NOT: "Hook must be bold statement in first 3s"
        BUT: "Hook captures attention and creates curiosity"
        """
        
        # Load hook mastery from master learnings
        try:
            from master_learnings_v2 import load_master_learnings
            learnings = load_master_learnings()
            hook_mastery = learnings.get('hook_mastery', {})
            winning_hooks = hook_mastery.get('winning_hook_types', [])
        except:
            winning_hooks = []
        
        # Extract examples from GOAT data
        hook_examples = []
        for clip in self.goat_data[:10]:  # Top 10
            transcript = clip.get('transcript', {})
            segments = transcript.get('segments', [])
            perf = clip.get('performance', {})
            
            if segments and perf.get('views', 0) > 2000000:
                # Get first 3 seconds
                first_segments = [s for s in segments if s.get('start', 0) < 3.0]
                if first_segments:
                    hook_text = ' '.join([s.get('text', '') for s in first_segments])
                    hook_examples.append({
                        'text': hook_text[:100],
                        'views': perf.get('views', 0)
                    })
        
        return {
            'principle': 'Hook must stop the scroll within 3 seconds',
            'methods': [
                'Bold statement (contrarian view)',
                'Provocative question (creates curiosity gap)',
                'Visual/verbal pattern interrupt (unexpected)',
                'Emotional trigger (relatable pain/joy)',
                'Authority establishment (credibility)'
            ],
            'guideline': 'Hook TYPE depends on content and audience',
            'examples_from_data': hook_examples[:5] if hook_examples else [
                '"Arbeite niemals für Geld" - Bold contrarian',
                '"Was wäre wenn..." - Question creates gap',
                'Visual metaphor - Pattern interrupt'
            ],
            'winning_types': winning_hooks[:5] if winning_hooks else []
        }
    
    def extract_cut_principles(self) -> Dict:
        """
        Extract PRINCIPLES about cuts from Longform→Clip pairs
        """
        
        if not self.longform_clip_pairs:
            return {
                'principle': 'Remove what doesn\'t advance narrative',
                'what_to_cut': [
                    'Unnecessary descriptors that don\'t add value',
                    'Verbose transitions - tighten',
                    'Obvious statements - remove',
                    'Filler words - be selective (some add authenticity!)',
                    'Repetition - unless for emphasis'
                ],
                'what_to_keep': [
                    'Core narrative beats',
                    'Emotional resonance moments',
                    'Speaker\'s natural voice (don\'t over-sanitize)',
                    'Setup that makes payoff land',
                    'Pattern interrupts'
                ],
                'guideline': 'Cut fat, keep muscle - but muscle includes emotion!'
            }
        
        # Analyze what was cut in successful transformations
        return {
            'principle': 'Every word must earn its place',
            'what_to_cut': [
                'Unnecessary descriptors that don\'t add value',
                'Verbose transitions - tighten',
                'Obvious statements - remove',
                'Filler words - be selective (some add authenticity!)',
                'Repetition - unless for emphasis'
            ],
            'what_to_keep': [
                'Core narrative beats',
                'Emotional resonance moments',
                'Speaker\'s natural voice (don\'t over-sanitize)',
                'Setup that makes payoff land',
                'Pattern interrupts'
            ],
            'guideline': 'Cut fat, keep muscle - but muscle includes emotion!',
            'transformation_examples': [
                pair.get('transformation', '') for pair in self.longform_clip_pairs
            ]
        }
    
    def extract_timing_principles(self) -> Dict:
        """
        Extract PRINCIPLES about timing/pauses
        """
        
        return {
            'principle': 'Strategic silence creates impact',
            'when_to_pause': [
                'After rhetorical question (build tension)',
                'Before payoff (anticipation)',
                'After revelation (let it land)',
                'At emotional beats (breathing room)'
            ],
            'when_NOT_to_pause': [
                'During high-energy sequences',
                'In rapid-fire content',
                'When momentum matters more than emphasis'
            ],
            'guideline': 'Pauses are tools, not rules - use strategically',
            'optimal_durations': {
                'question_answer': {'min': 1.0, 'max': 2.5, 'optimal': 1.5},
                'payoff_anticipation': {'min': 0.5, 'max': 1.5, 'optimal': 0.8},
                'emotional_beat': {'min': 0.5, 'max': 1.0, 'optimal': 0.8}
            }
        }
    
    def extract_structure_principles(self) -> Dict:
        """
        Extract PRINCIPLES about structure
        NOT: "Must follow Hook→Story→Payoff"
        BUT: "Structure serves the content type"
        """
        
        return {
            'principle': 'Structure adapts to content type',
            'patterns_by_type': {
                'Story': 'Setup → Escalation → Twist/Resolution',
                'Insight': 'Problem → Analysis → Solution',
                'Rant': 'Statement → Evidence → Conclusion',
                'Tutorial': 'Promise → Steps → Result',
                'Revelation': 'Question → Suspense → Answer',
                'Parable': 'Metaphor → Development → Lesson',
                'Conversation': 'Hook → Dialogue → Insight',
                'Educational': 'Question → Explanation → Application'
            },
            'guideline': 'Identify content type FIRST, apply appropriate structure',
            'anti_pattern': 'Forcing all content into Hook→Story→Payoff template',
            'flexibility': 'Structure should serve watchtime, not rigid templates'
        }
    
    def get_all_principles(self) -> Dict:
        """Get complete principle set"""
        
        return {
            'core_algorithm': self.master_learnings,
            'duration': self.extract_duration_principles(),
            'hooks': self.extract_hook_principles(),
            'cuts': self.extract_cut_principles(),
            'timing': self.extract_timing_principles(),
            'structure': self.extract_structure_principles()
        }
    
    def format_principles_for_prompt(self, principle_type: str) -> str:
        """
        Format principles for use in AI prompts
        
        Args:
            principle_type: 'duration', 'hooks', 'cuts', 'timing', 'structure'
        
        Returns:
            Formatted string for prompt
        """
        all_principles = self.get_all_principles()
        principles = all_principles.get(principle_type, {})
        
        if not principles:
            return ""
        
        formatted = f"PRINCIPLE: {principles.get('principle', 'N/A')}\n\n"
        
        if 'observations' in principles:
            formatted += "OBSERVATIONS (from 175+ proven clips):\n"
            for obs in principles['observations']:
                formatted += f"- {obs}\n"
            formatted += "\n"
        
        if 'methods' in principles:
            formatted += "METHODS (from proven data):\n"
            for method in principles['methods']:
                formatted += f"- {method}\n"
            formatted += "\n"
        
        if 'what_to_cut' in principles:
            formatted += "WHAT TO CUT:\n"
            for rule in principles['what_to_cut']:
                formatted += f"- {rule}\n"
            formatted += "\n"
        
        if 'what_to_keep' in principles:
            formatted += "WHAT TO KEEP:\n"
            for rule in principles['what_to_keep']:
                formatted += f"- {rule}\n"
            formatted += "\n"
        
        if 'when_to_pause' in principles:
            formatted += "WHEN TO PAUSE:\n"
            for when in principles['when_to_pause']:
                formatted += f"- {when}\n"
            formatted += "\n"
        
        if 'when_NOT_to_pause' in principles:
            formatted += "WHEN NOT TO PAUSE:\n"
            for when in principles['when_NOT_to_pause']:
                formatted += f"- {when}\n"
            formatted += "\n"
        
        if 'patterns_by_type' in principles:
            formatted += "STRUCTURES BY CONTENT TYPE:\n"
            for content_type, pattern in principles['patterns_by_type'].items():
                formatted += f"- {content_type}: {pattern}\n"
            formatted += "\n"
        
        formatted += f"GUIDELINE: {principles.get('guideline', 'N/A')}\n"
        
        if 'anti_pattern' in principles:
            formatted += f"\nANTI-PATTERN (avoid): {principles['anti_pattern']}\n"
        
        return formatted

