#!/usr/bin/env python3
"""
📚 LEARN FROM VIRAL EXAMPLE

Analysiert erfolgreiche Clips und extrahiert Restrukturierungs-Patterns.
Von erfolgreichen Beispielen lernen für zukünftige Clip-Erstellung.
"""

import json
import os
import argparse
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None

# Import master learnings
try:
    from master_learnings import load_master_learnings, save_master_learnings
    LEARNINGS_AVAILABLE = True
except ImportError:
    LEARNINGS_AVAILABLE = False


class ViralExampleLearner:
    """
    Main class for learning from viral clip examples
    """
    
    def __init__(self):
        # API Client
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if ANTHROPIC_AVAILABLE and self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None
        
        # Paths
        self.data_dir = Path("data")
        self.examples_dir = self.data_dir / "viral_examples"
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        
        # Master Learnings
        if LEARNINGS_AVAILABLE:
            self.master_learnings = load_master_learnings()
        else:
            self.master_learnings = {}
        
        print("="*70)
        print("📚 VIRAL EXAMPLE LEARNER")
        print("="*70)
        print(f"   🤖 AI: {'Connected' if self.client else 'Not available'}")
        print(f"   🧠 Master Learnings: {'Loaded' if LEARNINGS_AVAILABLE else 'Not available'}")
    
    # =========================================================================
    # INPUT HANDLING
    # =========================================================================
    
    def load_transcript(self, input_path: str) -> List[Dict]:
        """
        Load transcript from file or video
        
        Supports:
        - JSON (Whisper format)
        - TXT (plain text)
        - Video path (will transcribe)
        
        Returns:
            List of segments with 'text', 'start', 'end'
        """
        
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"❌ File not found: {input_path}")
            return []
        
        print(f"\n📄 Loading transcript: {input_path.name}")
        
        # Check if it's a video file
        if input_path.suffix.lower() in ['.mp4', '.mov', '.m4v', '.avi']:
            return self._transcribe_video(input_path)
        
        # Load text file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                if input_path.suffix.lower() == '.json':
                    data = json.load(f)
                    
                    if 'segments' in data:
                        segments = data['segments']
                        print(f"   ✅ Loaded {len(segments)} segments (Whisper format)")
                        return segments
                    elif 'text' in data:
                        # Simple text format - create pseudo-segments
                        return self._create_segments_from_text(data['text'])
                else:
                    # Plain text
                    text = f.read()
                    return self._create_segments_from_text(text)
        
        except Exception as e:
            print(f"❌ Error loading transcript: {e}")
            return []
    
    def _transcribe_video(self, video_path: Path) -> List[Dict]:
        """Transcribe video with Whisper"""
        
        try:
            import whisper
            
            print(f"   🎤 Transcribing video...")
            model = whisper.load_model("base")
            result = model.transcribe(str(video_path), language='de', verbose=False)
            
            return result.get('segments', [])
        
        except ImportError:
            print("❌ Whisper not installed")
            return []
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return []
    
    def _create_segments_from_text(self, text: str) -> List[Dict]:
        """Create pseudo-segments from plain text"""
        
        words = text.split()
        segments = []
        chunk_size = 25  # ~10 seconds per segment
        
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i+chunk_size]
            segments.append({
                'text': ' '.join(chunk),
                'start': i / 2.5,
                'end': (i + len(chunk)) / 2.5
            })
        
        print(f"   ✅ Created {len(segments)} segments from text")
        return segments
    
    def load_clip_data(
        self,
        clip_input: Optional[str],
        clip_start: Optional[float],
        clip_end: Optional[float],
        longform_segments: List[Dict]
    ) -> Tuple[List[Dict], Dict]:
        """
        Load clip data from transcript file OR timestamps
        
        Args:
            clip_input: Path to clip transcript file (optional)
            clip_start: Start timestamp (optional)
            clip_end: End timestamp (optional)
            longform_segments: Longform segments (for timestamp extraction)
        
        Returns:
            Tuple of (clip_segments, metadata)
        """
        
        if clip_input:
            # Load from file
            print(f"\n📄 Loading clip transcript: {clip_input}")
            clip_segments = self.load_transcript(clip_input)
            
            metadata = {
                "source": "file",
                "clip_path": clip_input
            }
            
            return clip_segments, metadata
        
        elif clip_start is not None and clip_end is not None:
            # Extract from longform using timestamps
            print(f"\n⏱️  Extracting clip from timestamps: {clip_start}s - {clip_end}s")
            
            clip_segments = []
            for seg in longform_segments:
                seg_start = seg.get('start', 0)
                seg_end = seg.get('end', 0)
                
                # Check if segment overlaps with clip range
                if seg_end >= clip_start and seg_start <= clip_end:
                    # Adjust timestamps relative to clip start
                    adjusted_seg = seg.copy()
                    adjusted_seg['start'] = max(0, seg_start - clip_start)
                    adjusted_seg['end'] = min(clip_end - clip_start, seg_end - clip_start)
                    clip_segments.append(adjusted_seg)
            
            metadata = {
                "source": "timestamps",
                "clip_start": clip_start,
                "clip_end": clip_end,
                "clip_duration": clip_end - clip_start
            }
            
            print(f"   ✅ Extracted {len(clip_segments)} segments")
            return clip_segments, metadata
        
        else:
            print("❌ No clip data provided (need --clip OR --clip-start + --clip-end)")
            return [], {}
    
    def load_performance_data(
        self,
        performance_file: Optional[str],
        views: Optional[int],
        watch_time: Optional[float],
        followers: Optional[int]
    ) -> Dict:
        """
        Load performance data from JSON file OR CLI arguments
        
        Args:
            performance_file: Path to JSON file with performance data
            views: Views count (CLI)
            watch_time: Watch time percentage (CLI)
            followers: Followers gained (CLI)
        
        Returns:
            Dict with performance metrics
        """
        
        if performance_file:
            # Load from JSON
            perf_path = Path(performance_file)
            
            if not perf_path.exists():
                print(f"❌ Performance file not found: {perf_path}")
                return {}
            
            print(f"\n📊 Loading performance data: {perf_path.name}")
            
            try:
                with open(perf_path, 'r') as f:
                    data = json.load(f)
                
                # Validate required fields
                required = ['views', 'watch_time', 'followers']
                missing = [k for k in required if k not in data]
                
                if missing:
                    print(f"⚠️  Missing fields: {missing}")
                
                print(f"   ✅ Views: {data.get('views', 0):,}")
                print(f"   ✅ Watch Time: {data.get('watch_time', 0)}%")
                print(f"   ✅ Followers: {data.get('followers', 0):,}")
                
                return data
            
            except Exception as e:
                print(f"❌ Error loading performance data: {e}")
                return {}
        
        elif views is not None and watch_time is not None and followers is not None:
            # From CLI arguments
            print(f"\n📊 Performance data (CLI):")
            print(f"   ✅ Views: {views:,}")
            print(f"   ✅ Watch Time: {watch_time}%")
            print(f"   ✅ Followers: {followers:,}")
            
            return {
                "views": views,
                "watch_time": watch_time,
                "followers": followers
            }
        
        else:
            print("❌ No performance data provided")
            return {}
    
    # =========================================================================
    # COMPARISON FUNCTIONS
    # =========================================================================
    
    def compare_transcripts(
        self,
        longform_segments: List[Dict],
        clip_segments: List[Dict]
    ) -> Dict:
        """
        Vergleicht Longform vs Clip Transcript
        
        Identifiziert:
        - Welche Segmente wurden verwendet
        - Neue Reihenfolge (Restrukturierung)
        - Entfernte Teile
        
        Returns:
        {
            "used_segments": [
                {
                    "original_start": 120.5,
                    "original_end": 145.0,
                    "clip_start": 0.0,
                    "clip_end": 24.5,
                    "text": "...",
                    "role": "hook/context/content/payoff" (detected)
                }
            ],
            "removed_segments": [...],
            "restructuring": {
                "original_order": [120.5, 145.0, 200.0],
                "clip_order": [200.0, 120.5, 145.0],
                "reordered": True,
                "reorder_pattern": "payoff_first_then_context"
            },
            "coverage": {
                "original_duration": 1800.0,
                "clip_duration": 45.0,
                "coverage_percent": 2.5,
                "compression_ratio": 0.025
            }
        }
        """
        
        print(f"\n{'='*70}")
        print("🔍 COMPARING TRANSCRIPTS")
        print(f"{'='*70}")
        
        if not longform_segments or not clip_segments:
            print("❌ Missing segments")
            return {}
        
        # Calculate durations
        original_duration = longform_segments[-1].get('end', 0) if longform_segments else 0
        clip_duration = clip_segments[-1].get('end', 0) if clip_segments else 0
        
        print(f"\n📊 Durations:")
        print(f"   Original: {original_duration/60:.1f} minutes")
        print(f"   Clip: {clip_duration:.1f} seconds")
        print(f"   Compression: {clip_duration/original_duration*100:.2f}%")
        
        # Match segments (text-based matching)
        used_segments = []
        original_timestamps = []
        clip_timestamps = []
        
        print(f"\n🔍 Matching segments...")
        
        for clip_seg in clip_segments:
            clip_text = clip_seg.get('text', '').lower().strip()
            clip_start = clip_seg.get('start', 0)
            clip_end = clip_seg.get('end', 0)
            
            # Find matching segment in longform
            best_match = None
            best_score = 0
            
            for orig_seg in longform_segments:
                orig_text = orig_seg.get('text', '').lower().strip()
                orig_start = orig_seg.get('start', 0)
                orig_end = orig_seg.get('end', 0)
                
                # Simple text matching (can be improved with fuzzy matching)
                # Check if texts overlap significantly
                if clip_text in orig_text or orig_text in clip_text:
                    score = min(len(clip_text), len(orig_text)) / max(len(clip_text), len(orig_text), 1)
                    
                    if score > best_score:
                        best_score = score
                        best_match = orig_seg
            
            # Also try word-based matching
            if not best_match or best_score < 0.5:
                clip_words = set(clip_text.split())
                
                for orig_seg in longform_segments:
                    orig_text = orig_seg.get('text', '').lower().strip()
                    orig_words = set(orig_text.split())
                    
                    if len(clip_words) > 0:
                        overlap = len(clip_words & orig_words) / len(clip_words)
                        
                        if overlap > best_score:
                            best_score = overlap
                            best_match = orig_seg
            
            if best_match and best_score > 0.3:
                original_start = best_match.get('start', 0)
                original_end = best_match.get('end', 0)
                
                # Detect role based on position
                role = self._detect_segment_role(clip_seg, clip_segments)
                
                used_segments.append({
                    "original_start": original_start,
                    "original_end": original_end,
                    "clip_start": clip_start,
                    "clip_end": clip_end,
                    "text": clip_seg.get('text', ''),
                    "role": role,
                    "match_score": best_score
                })
                
                original_timestamps.append(original_start)
                clip_timestamps.append(clip_start)
        
        print(f"   ✅ Matched {len(used_segments)} segments")
        
        # Detect restructuring
        reordered = False
        if len(original_timestamps) > 1:
            # Check if order changed
            original_sorted = sorted(original_timestamps)
            clip_sorted = sorted(clip_timestamps)
            
            # Compare order
            if original_timestamps != clip_timestamps:
                reordered = True
        
        # Identify removed segments
        used_original_starts = {seg['original_start'] for seg in used_segments}
        removed_segments = []
        
        for orig_seg in longform_segments:
            orig_start = orig_seg.get('start', 0)
            if orig_start not in used_original_starts:
                removed_segments.append({
                    "start": orig_start,
                    "end": orig_seg.get('end', 0),
                    "text": orig_seg.get('text', '')[:100] + "..."
                })
        
        # Detect reorder pattern
        reorder_pattern = None
        if reordered and len(used_segments) >= 2:
            # Check if hook was moved to front
            first_clip_seg = min(used_segments, key=lambda x: x['clip_start'])
            first_orig_seg = min(used_segments, key=lambda x: x['original_start'])
            
            if first_clip_seg['original_start'] > first_orig_seg['original_start']:
                # Hook was moved forward
                if first_clip_seg['role'] == 'hook':
                    reorder_pattern = "hook_moved_to_front"
                else:
                    reorder_pattern = "payoff_first_then_context"
            else:
                reorder_pattern = "reordered"
        
        coverage_percent = (clip_duration / original_duration * 100) if original_duration > 0 else 0
        
        result = {
            "used_segments": used_segments,
            "removed_segments": removed_segments[:20],  # Limit to first 20
            "restructuring": {
                "original_order": original_timestamps,
                "clip_order": clip_timestamps,
                "reordered": reordered,
                "reorder_pattern": reorder_pattern
            },
            "coverage": {
                "original_duration": original_duration,
                "clip_duration": clip_duration,
                "coverage_percent": coverage_percent,
                "compression_ratio": clip_duration / original_duration if original_duration > 0 else 0
            }
        }
        
        print(f"\n✅ Comparison complete!")
        print(f"   📊 Used segments: {len(used_segments)}")
        print(f"   📊 Removed segments: {len(removed_segments)}")
        print(f"   📊 Reordered: {reordered}")
        if reorder_pattern:
            print(f"   📊 Pattern: {reorder_pattern}")
        
        return result
    
    def _detect_segment_role(
        self,
        segment: Dict,
        all_segments: List[Dict]
    ) -> str:
        """
        Detect role of segment (hook/context/content/payoff)
        
        Based on position and content
        """
        
        clip_start = segment.get('start', 0)
        clip_end = segment.get('end', 0)
        text = segment.get('text', '').lower()
        
        # Get clip duration
        if all_segments:
            clip_duration = all_segments[-1].get('end', 0)
        else:
            clip_duration = clip_end
        
        # Hook: First 3 seconds
        if clip_start < 3:
            # Check for hook indicators
            hook_words = ['warum', 'wie', 'was', 'der größte', 'fehler', 'geheimnis', 'niemals']
            if any(word in text for word in hook_words):
                return "hook"
            return "hook"
        
        # Payoff: Last 5 seconds
        if clip_end >= clip_duration - 5:
            return "payoff"
        
        # Context: First 15 seconds (after hook)
        if clip_start < 15:
            return "context"
        
        # Content: Everything else
        return "content"
    
    # =========================================================================
    # ANALYSIS FUNCTIONS
    # =========================================================================
    
    def analyze_restructuring(
        self,
        comparison_result: Dict,
        clip_segments: List[Dict],
        performance: Dict
    ) -> Dict:
        """
        Analysiert die Restrukturierung im Detail
        """
        
        print(f"\n{'='*70}")
        print("🔍 ANALYZING RESTRUCTURING")
        print(f"{'='*70}")
        
        used_segments = comparison_result.get('used_segments', [])
        restructuring = comparison_result.get('restructuring', {})
        
        if not used_segments:
            return {}
        
        # Find hook segment
        hook_segment = None
        for seg in used_segments:
            if seg.get('role') == 'hook':
                hook_segment = seg
                break
        
        # If no hook detected, use first segment
        if not hook_segment and used_segments:
            hook_segment = used_segments[0]
        
        # Analyze hook strategy
        hook_strategy = {}
        if hook_segment:
            original_pos = hook_segment.get('original_start', 0)
            clip_pos = hook_segment.get('clip_start', 0)
            moved_to_front = clip_pos < 3.0 and original_pos > 10.0
            
            hook_strategy = {
                "original_position": original_pos,
                "clip_position": clip_pos,
                "moved_to_front": moved_to_front,
                "hook_text": hook_segment.get('text', '')[:100],
                "hook_type": self._detect_hook_type(hook_segment.get('text', '')),
                "hook_strength": self._score_hook_strength(hook_segment.get('text', ''), performance),
                "why_effective": self._explain_hook_effectiveness(hook_segment.get('text', ''))
            }
        
        # Analyze structure pattern
        original_order = restructuring.get('original_order', [])
        clip_order = restructuring.get('clip_order', [])
        reorder_pattern = restructuring.get('reorder_pattern', 'unknown')
        
        # Detect structure pattern name
        structure_pattern_name = self._detect_structure_pattern_name(
            used_segments,
            clip_segments
        )
        
        # Calculate timing
        clip_duration = clip_segments[-1].get('end', 0) if clip_segments else 0
        hook_duration = hook_strategy.get('clip_position', 0) + 3.0 if hook_strategy else 0
        
        # Find pattern interrupts (segment changes)
        pattern_interrupts = []
        for i, seg in enumerate(clip_segments[:-1]):
            if seg.get('role') != clip_segments[i+1].get('role'):
                pattern_interrupts.append(seg.get('end', 0))
        
        structure_pattern = {
            "original": "→".join([f"{t:.1f}s" for t in original_order[:5]]),
            "clip": "→".join([f"{t:.1f}s" for t in clip_order[:5]]),
            "pattern_name": structure_pattern_name,
            "pattern_description": self._describe_pattern(structure_pattern_name),
            "timing": {
                "hook_duration": min(hook_duration, 5.0),
                "first_loop": hook_duration if hook_strategy else 0,
                "pattern_interrupts": pattern_interrupts[:5],
                "total_duration": clip_duration
            }
        }
        
        # Analyze removed parts
        removed_segments = comparison_result.get('removed_segments', [])
        
        # Detect what was removed
        removed_parts = {
            "intro": any(seg.get('start', 0) < 30 for seg in removed_segments),
            "filler": len(removed_segments) > 10,
            "repetition": False,  # Would need deeper analysis
            "slow_parts": True,
            "removed_segments_count": len(removed_segments)
        }
        
        # Compression analysis
        coverage = comparison_result.get('coverage', {})
        compression_ratio = coverage.get('compression_ratio', 0)
        
        compression_strategy = "keep_hook_and_payoff_only"
        if compression_ratio < 0.02:
            compression_strategy = "extreme_compression"
        elif compression_ratio < 0.05:
            compression_strategy = "high_compression"
        
        compression = {
            "ratio": compression_ratio,
            "strategy": compression_strategy,
            "removed_percent": (1 - compression_ratio) * 100
        }
        
        # Calculate effectiveness score based on performance
        effectiveness_score = self._calculate_effectiveness_score(performance)
        
        result = {
            "hook_strategy": hook_strategy,
            "structure_pattern": structure_pattern,
            "removed_parts": removed_parts,
            "compression": compression,
            "effectiveness_score": effectiveness_score
        }
        
        print(f"\n✅ Restructuring analysis complete!")
        print(f"   📊 Hook moved to front: {hook_strategy.get('moved_to_front', False)}")
        print(f"   📊 Structure pattern: {structure_pattern_name}")
        print(f"   📊 Effectiveness: {effectiveness_score:.2f}")
        
        return result
    
    def _detect_hook_type(self, hook_text: str) -> str:
        """Detect hook type from text"""
        text_lower = hook_text.lower()
        
        if any(word in text_lower for word in ['warum', 'why', 'wie', 'how']):
            return "question"
        elif any(word in text_lower for word in ['als', 'when', 'story', 'geschichte']):
            return "story"
        elif any(word in text_lower for word in ['fehler', 'mistake', 'falsch', 'wrong']):
            return "controversy"
        elif '?' in hook_text:
            return "question"
        else:
            return "statement"
    
    def _score_hook_strength(self, hook_text: str, performance: Dict) -> int:
        """Score hook strength 0-10 based on text and performance"""
        score = 5  # Base score
        
        # Text-based scoring
        power_words = ['warum', 'why', 'geheimnis', 'secret', 'niemals', 'never', 'größte', 'biggest']
        if any(word in hook_text.lower() for word in power_words):
            score += 2
        
        if '?' in hook_text:
            score += 1
        
        # Performance-based scoring
        watch_time = performance.get('watch_time', 0)
        if watch_time > 80:
            score += 2
        elif watch_time > 70:
            score += 1
        
        return min(score, 10)
    
    def _explain_hook_effectiveness(self, hook_text: str) -> str:
        """Simple explanation why hook is effective"""
        text_lower = hook_text.lower()
        
        if '?' in hook_text:
            return "Öffnet Information Gap durch Frage"
        elif any(word in text_lower for word in ['warum', 'why']):
            return "Kontraintuitives Statement erzeugt Neugier"
        elif any(word in text_lower for word in ['geheimnis', 'secret']):
            return "Verspricht exklusive Information"
        else:
            return "Starker erster Eindruck"
    
    def _detect_structure_pattern_name(
        self,
        used_segments: List[Dict],
        clip_segments: List[Dict]
    ) -> str:
        """Detect structure pattern name"""
        
        if not used_segments or not clip_segments:
            return "unknown"
        
        # Check if hook was moved to front
        first_used = min(used_segments, key=lambda x: x.get('clip_start', 0))
        first_original = min(used_segments, key=lambda x: x.get('original_start', 0))
        
        if first_used.get('original_start', 0) > first_original.get('original_start', 0) + 30:
            if first_used.get('role') == 'hook':
                return "hook_moved_to_front"
            else:
                return "payoff_first_then_context"
        
        # Check roles order
        roles = [seg.get('role', 'content') for seg in clip_segments[:5]]
        roles_str = "→".join(roles)
        
        if roles_str.startswith("hook→context"):
            return "hook_context_payoff"
        elif roles_str.startswith("hook→content"):
            return "hook_content_payoff"
        else:
            return "reordered"
    
    def _describe_pattern(self, pattern_name: str) -> str:
        """Describe pattern"""
        descriptions = {
            "hook_moved_to_front": "Hook aus der Mitte nach vorne gezogen",
            "payoff_first_then_context": "Stärkster Moment zuerst, dann Aufbau",
            "hook_context_payoff": "Standard-Struktur: Hook → Context → Payoff",
            "hook_content_payoff": "Direkt: Hook → Content → Payoff",
            "reordered": "Segmente neu angeordnet"
        }
        return descriptions.get(pattern_name, "Unbekanntes Pattern")
    
    def _calculate_effectiveness_score(self, performance: Dict) -> float:
        """Calculate effectiveness score 0-1 based on performance"""
        views = performance.get('views', 0)
        watch_time = performance.get('watch_time', 0)
        followers = performance.get('followers', 0)
        
        score = 0.0
        
        # Views score (0-0.4)
        if views > 1000000:
            score += 0.4
        elif views > 500000:
            score += 0.3
        elif views > 100000:
            score += 0.2
        elif views > 50000:
            score += 0.1
        
        # Watch time score (0-0.4)
        if watch_time > 85:
            score += 0.4
        elif watch_time > 75:
            score += 0.3
        elif watch_time > 65:
            score += 0.2
        elif watch_time > 50:
            score += 0.1
        
        # Followers score (0-0.2)
        if followers > 10000:
            score += 0.2
        elif followers > 5000:
            score += 0.15
        elif followers > 1000:
            score += 0.1
        elif followers > 500:
            score += 0.05
        
        return min(score, 1.0)
    
    def extract_hook_patterns(
        self,
        hook_segment: Dict,
        clip_segments: List[Dict],
        performance: Dict,
        comparison_result: Dict
    ) -> Dict:
        """
        Extrahiert Hook-Patterns aus erfolgreichem Clip
        """
        
        print(f"\n{'='*70}")
        print("🪝 EXTRACTING HOOK PATTERNS")
        print(f"{'='*70}")
        
        hook_text = hook_segment.get('text', '')
        hook_lower = hook_text.lower()
        
        # Extract first words
        words = hook_text.split()
        first_words = words[:3] if len(words) >= 3 else words
        
        # Power words detection
        power_words_list = [
            'warum', 'why', 'wie', 'how', 'was', 'what',
            'geheimnis', 'secret', 'niemals', 'never', 'immer', 'always',
            'größte', 'biggest', 'fehler', 'mistake', 'wahrheit', 'truth',
            'schockierend', 'shocking', 'unglaublich', 'unbelievable'
        ]
        
        power_words_found = [w for w in words if w.lower() in power_words_list]
        
        # Hook type
        hook_type = self._detect_hook_type(hook_text)
        
        # Emotional trigger
        emotional_trigger = self._detect_emotional_trigger(hook_text)
        
        # Information gap detection
        has_question = '?' in hook_text
        has_incomplete = any(word in hook_lower for word in ['gleich', 'später', 'dann', 'zeige'])
        information_gap = has_question or has_incomplete
        
        # Hook formula
        hook_formula = self._extract_hook_formula(hook_text)
        
        # Timing
        hook_start = hook_segment.get('clip_start', 0)
        hook_end = hook_segment.get('clip_end', hook_start + 3)
        hook_duration = hook_end - hook_start
        words_count = len(words)
        words_per_second = words_count / hook_duration if hook_duration > 0 else 0
        
        # Effectiveness
        hook_strength = self._score_hook_strength(hook_text, performance)
        watch_time = performance.get('watch_time', 0)
        watch_time_impact = "high" if watch_time > 80 else "medium" if watch_time > 65 else "low"
        
        # Matched patterns
        matched_patterns = []
        if hook_type == "controversy":
            matched_patterns.append("controversy_hook")
        if information_gap:
            matched_patterns.append("information_gap_hook")
        if hook_type == "question":
            matched_patterns.append("question_hook")
        
        effectiveness_score = hook_strength / 10.0
        
        result = {
            "hook_text": hook_text,
            "hook_type": hook_type,
            "first_words": first_words,
            "power_words": power_words_found,
            "emotional_trigger": emotional_trigger,
            "information_gap": information_gap,
            "hook_formula": hook_formula,
            "timing": {
                "duration": hook_duration,
                "words_count": words_count,
                "words_per_second": words_per_second
            },
            "effectiveness": {
                "score": effectiveness_score,
                "watch_time_impact": watch_time_impact,
                "hook_strength": hook_strength
            },
            "matched_patterns": matched_patterns
        }
        
        print(f"\n✅ Hook patterns extracted!")
        print(f"   📊 Hook type: {hook_type}")
        print(f"   📊 Power words: {len(power_words_found)}")
        print(f"   📊 Information gap: {information_gap}")
        print(f"   📊 Hook strength: {hook_strength}/10")
        
        return result
    
    def _detect_emotional_trigger(self, text: str) -> str:
        """Detect emotional trigger"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['schockierend', 'shocking', 'unglaublich']):
            return "surprise"
        elif any(word in text_lower for word in ['fehler', 'mistake', 'falsch', 'wrong']):
            return "anger"
        elif '?' in text:
            return "curiosity"
        elif any(word in text_lower for word in ['geheimnis', 'secret', 'niemals']):
            return "excitement"
        else:
            return "curiosity"
    
    def _extract_hook_formula(self, hook_text: str) -> str:
        """Extract hook formula/template"""
        text_lower = hook_text.lower()
        
        if text_lower.startswith('warum'):
            return "Warum [kontraintuitives Statement]"
        elif text_lower.startswith('wie'):
            return "Wie [Prozess/Methode]"
        elif text_lower.startswith('der größte'):
            return "Der größte Fehler bei [Topic]"
        elif '?' in hook_text:
            return "[Frage die Information Gap öffnet]"
        else:
            return "[Starker erster Satz]"
    
    def extract_structure_patterns(
        self,
        clip_segments: List[Dict],
        restructuring: Dict,
        performance: Dict
    ) -> Dict:
        """
        Extrahiert Struktur-Patterns aus erfolgreichem Clip
        """
        
        print(f"\n{'='*70}")
        print("📐 EXTRACTING STRUCTURE PATTERNS")
        print(f"{'='*70}")
        
        if not clip_segments:
            return {}
        
        clip_duration = clip_segments[-1].get('end', 0)
        
        # Extract structure phases
        hook_phase = None
        context_phase = None
        content_phase = None
        payoff_phase = None
        
        for seg in clip_segments:
            role = seg.get('role', 'content')
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            
            if role == 'hook' and not hook_phase:
                hook_phase = {"start": start, "end": end, "duration": end - start}
            elif role == 'context' and not context_phase:
                context_phase = {"start": start, "end": end, "duration": end - start}
            elif role == 'content' and not content_phase:
                content_phase = {"start": start, "end": end, "duration": end - start}
            elif role == 'payoff' and not payoff_phase:
                payoff_phase = {"start": start, "end": end, "duration": end - start}
        
        # Build structure
        structure = {}
        if hook_phase:
            structure["hook"] = {
                **hook_phase,
                "role": "hook",
                "purpose": "Stop-Trigger, Information Gap"
            }
        
        if context_phase:
            structure["context"] = {
                **context_phase,
                "role": "context",
                "purpose": "Aufbau, Loop öffnen"
            }
        
        if content_phase:
            structure["content"] = {
                **content_phase,
                "role": "content",
                "purpose": "Hauptinhalt mit Pattern Interrupts"
            }
        
        if payoff_phase:
            structure["payoff"] = {
                **payoff_phase,
                "role": "payoff",
                "purpose": "Loop schließen, Satisfying Conclusion"
            }
        
        # Calculate timing
        hook_duration = hook_phase.get('duration', 0) if hook_phase else 0
        first_loop = context_phase.get('start', hook_duration) if context_phase else hook_duration
        
        # Pattern interrupts (role changes)
        pattern_interrupts = []
        for i, seg in enumerate(clip_segments[:-1]):
            if seg.get('role') != clip_segments[i+1].get('role'):
                pattern_interrupts.append(seg.get('end', 0))
        
        timing = {
            "hook_duration": hook_duration,
            "first_loop": first_loop,
            "pattern_interrupts": pattern_interrupts[:5],
            "total_duration": clip_duration,
            "optimal_length": {
                "min": 30,
                "max": 60,
                "sweet_spot": 45
            }
        }
        
        # Tension arc
        tension_points = []
        for i, seg in enumerate(clip_segments):
            role = seg.get('role', 'content')
            time = seg.get('start', 0)
            
            # Simple tension scoring based on role
            if role == 'hook':
                level = 9
            elif role == 'payoff':
                level = 8
            elif role == 'context':
                level = 7
            else:
                level = 6
            
            tension_points.append({
                "time": time,
                "level": level,
                "reason": role
            })
        
        if tension_points:
            levels = [p['level'] for p in tension_points]
            avg_tension = sum(levels) / len(levels)
            min_tension = min(levels)
            max_tension = max(levels)
            
            # Detect arc type
            if levels[0] > levels[-1]:
                arc_type = "falling"
            elif levels[0] < levels[-1]:
                arc_type = "rising"
            else:
                arc_type = "plateau"
        else:
            avg_tension = 7.0
            min_tension = 5.0
            max_tension = 9.0
            arc_type = "plateau"
        
        tension_arc = {
            "arc_type": arc_type,
            "tension_points": tension_points[:10],
            "average_tension": avg_tension,
            "min_tension": min_tension,
            "max_tension": max_tension
        }
        
        # Structure name
        structure_name = restructuring.get('structure_pattern', {}).get('pattern_name', 'unknown')
        
        # Effectiveness
        effectiveness_score = self._calculate_effectiveness_score(performance)
        watch_time = performance.get('watch_time', 0)
        watch_time_impact = "high" if watch_time > 80 else "medium" if watch_time > 65 else "low"
        
        result = {
            "structure_name": structure_name,
            "structure": structure,
            "timing": timing,
            "tension_arc": tension_arc,
            "effectiveness": {
                "score": effectiveness_score,
                "watch_time_impact": watch_time_impact,
                "completion_rate_impact": watch_time_impact
            }
        }
        
        print(f"\n✅ Structure patterns extracted!")
        print(f"   📊 Structure: {structure_name}")
        print(f"   📊 Pattern interrupts: {len(pattern_interrupts)}")
        print(f"   📊 Tension arc: {arc_type}")
        
        return result
    
    def ai_analyze_example(
        self,
        longform_segments: List[Dict],
        clip_segments: List[Dict],
        comparison_result: Dict,
        restructuring: Dict,
        performance: Dict,
        notes: Optional[str] = None,
        deep_analysis: bool = False
    ) -> Dict:
        """
        Nutzt AI für tiefere Analyse des Beispiels
        """
        
        if not self.client:
            print("\n⚠️  No API key - skipping AI analysis")
            return {}
        
        print(f"\n{'='*70}")
        print("🧠 AI ANALYZING EXAMPLE")
        print(f"{'='*70}")
        
        if deep_analysis:
            print("   🔬 Deep analysis mode (for outliers)")
        
        # Prepare data for AI
        longform_text = self._format_segments_for_ai(longform_segments[:50])  # First 50 segments
        clip_text = self._format_segments_for_ai(clip_segments)
        
        # Build prompt
        prompt = f"""Du bist ein Elite-Content-Analyst für virale Short-Form Videos.

Du analysierst ein erfolgreiches Clip-Beispiel und sollst verstehen WARUM es funktioniert hat.

LONGFORM TRANSCRIPT (Original):
{longform_text[:5000]}

CLIP TRANSCRIPT (Erfolgreicher Clip):
{clip_text[:3000]}

PERFORMANCE DATA:
- Views: {performance.get('views', 0):,}
- Watch Time: {performance.get('watch_time', 0)}%
- Followers: {performance.get('followers', 0):,}

RESTRUCTURING ANALYSIS:
- Hook moved to front: {restructuring.get('hook_strategy', {}).get('moved_to_front', False)}
- Structure pattern: {restructuring.get('structure_pattern', {}).get('pattern_name', 'unknown')}
- Compression ratio: {restructuring.get('compression', {}).get('ratio', 0):.3f}

{('NOTES: ' + notes) if notes else ''}

---

AUFGABE:

1. Analysiere WARUM dieser Clip funktioniert hat
2. Identifiziere die wichtigsten Success Factors
3. Erstelle ein wiederverwendbares Template
4. Definiere "when to use" Kriterien

Antworte in diesem JSON-Format:

{{
    "analysis": {{
        "why_it_worked": [
            "Hook öffnet sofort Information Gap",
            "Payoff zuerst erzeugt sofortige Spannung",
            "Pattern Interrupts halten Spannung hoch"
        ],
        "key_success_factors": [
            "Hook-Stärke: 9/10",
            "Struktur: Optimal für Topic",
            "Timing: Perfekte Pattern Interrupts"
        ],
        "unique_elements": [
            "Verwendung von Kontroverse als Hook",
            "Payoff vor Context platziert"
        ]
    }},
    "template_suggestion": {{
        "name": "Controversy Hook + Payoff First",
        "when_to_use": [
            "Video enthält kontroverse Meinung",
            "Starker Payoff-Moment vorhanden",
            "Original-Struktur langsam"
        ],
        "structure": {{
            "step_1": "Finde stärksten Payoff-Moment",
            "step_2": "Platziere als Hook (0-3s)",
            "step_3": "Füge Context hinzu (3-15s)",
            "step_4": "Rest des Contents (15-40s)",
            "step_5": "Kleiner Payoff am Ende (40-45s)"
        }}
    }},
    "success_rate_prediction": 0.85
}}"""
        
        print("\n🧠 Sending to Claude AI...")
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                ai_result = json.loads(json_match.group())
                
                print(f"\n✅ AI analysis complete!")
                print(f"   📊 Success factors: {len(ai_result.get('analysis', {}).get('key_success_factors', []))}")
                print(f"   📊 Template: {ai_result.get('template_suggestion', {}).get('name', 'Unknown')}")
                
                return ai_result
            else:
                print("⚠️  Could not parse AI response")
                return {}
        
        except Exception as e:
            print(f"❌ AI analysis error: {e}")
            return {}
    
    def _format_segments_for_ai(self, segments: List[Dict]) -> str:
        """Format segments for AI prompt"""
        text = ""
        for seg in segments:
            text += f"[{seg.get('start', 0):.1f}s-{seg.get('end', 0):.1f}s] {seg.get('text', '')}\n"
        return text
    
    def create_template(
        self,
        hook_patterns: Dict,
        structure_patterns: Dict,
        restructuring: Dict,
        ai_analysis: Dict,
        performance: Dict
    ) -> Dict:
        """
        Erstellt wiederverwendbares Template aus allen Patterns
        """
        
        print(f"\n{'='*70}")
        print("📋 CREATING TEMPLATE")
        print(f"{'='*70}")
        
        # Generate template ID
        template_id = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get template name from AI or generate
        ai_template = ai_analysis.get('template_suggestion', {})
        template_name = ai_template.get('name', f"{hook_patterns.get('hook_type', 'unknown').title()} Hook Template")
        
        # Description
        description = f"Template basierend auf erfolgreichem Clip ({performance.get('views', 0):,} Views)"
        
        # When to use (from AI or generated)
        when_to_use = ai_template.get('when_to_use', [
            f"Video enthält {hook_patterns.get('hook_type', 'starken')} Hook",
            "Starker Payoff-Moment vorhanden",
            "Original-Struktur optimierbar"
        ])
        
        # When not to use
        when_not_to_use = [
            "Video hat keinen klaren Payoff-Moment",
            "Topic zu komplex für schnellen Hook",
            "Zielgruppe erwartet langsameren Aufbau"
        ]
        
        # Structure steps
        ai_structure = ai_template.get('structure', {})
        structure_steps = {}
        
        if ai_structure:
            for step_key, step_desc in ai_structure.items():
                structure_steps[step_key] = {
                    "action": step_desc,
                    "criteria": "Basierend auf erfolgreichem Beispiel",
                    "duration": "Variabel"
                }
        else:
            # Generate from structure_patterns
            structure = structure_patterns.get('structure', {})
            step_num = 1
            
            if structure.get('hook'):
                structure_steps[f"step_{step_num}"] = {
                    "action": "Platziere Hook (0-3s)",
                    "criteria": hook_patterns.get('hook_formula', 'Starker erster Satz'),
                    "duration": f"{structure['hook'].get('duration', 3):.1f} Sekunden"
                }
                step_num += 1
            
            if structure.get('context'):
                structure_steps[f"step_{step_num}"] = {
                    "action": "Füge Context hinzu",
                    "criteria": "Erklärt warum Hook wichtig ist",
                    "duration": f"{structure['context'].get('duration', 12):.1f} Sekunden"
                }
                step_num += 1
            
            if structure.get('content'):
                structure_steps[f"step_{step_num}"] = {
                    "action": "Hauptinhalt mit Pattern Interrupts",
                    "criteria": "Alle 5-7 Sekunden Mini-Payoff",
                    "duration": f"{structure['content'].get('duration', 25):.1f} Sekunden"
                }
                step_num += 1
            
            if structure.get('payoff'):
                structure_steps[f"step_{step_num}"] = {
                    "action": "Payoff am Ende",
                    "criteria": "Loop schließen, Satisfying Conclusion",
                    "duration": f"{structure['payoff'].get('duration', 5):.1f} Sekunden"
                }
        
        # Hook formula
        hook_formula = hook_patterns.get('hook_formula', '[Starker erster Satz]')
        
        # Hook examples
        hook_examples = [
            hook_patterns.get('hook_text', '')[:100]
        ]
        
        # Optimal length
        timing = structure_patterns.get('timing', {})
        optimal_length = timing.get('optimal_length', {
            "min": 30,
            "max": 60,
            "sweet_spot": 45
        })
        
        # Success rate
        success_rate = ai_analysis.get('success_rate_prediction', restructuring.get('effectiveness_score', 0.8))
        
        # Success criteria
        success_criteria = {
            "min_views": max(100000, performance.get('views', 0) * 0.5),
            "min_watch_time": max(70, performance.get('watch_time', 0) * 0.9),
            "min_followers": max(1000, performance.get('followers', 0) * 0.5)
        }
        
        # Tags
        tags = []
        tags.append(hook_patterns.get('hook_type', 'unknown'))
        if restructuring.get('hook_strategy', {}).get('moved_to_front'):
            tags.append("hook_moved_to_front")
        if hook_patterns.get('information_gap'):
            tags.append("information_gap")
        tags.append(structure_patterns.get('tension_arc', {}).get('arc_type', 'plateau'))
        
        template = {
            "template_id": template_id,
            "name": template_name,
            "description": description,
            "created_from": {
                "performance": {
                    "views": performance.get('views', 0),
                    "watch_time": performance.get('watch_time', 0)
                }
            },
            "when_to_use": when_to_use,
            "when_not_to_use": when_not_to_use,
            "structure": structure_steps,
            "hook_formula": hook_formula,
            "hook_examples": hook_examples,
            "optimal_length": optimal_length,
            "success_rate": success_rate,
            "success_criteria": success_criteria,
            "tags": tags
        }
        
        print(f"\n✅ Template created!")
        print(f"   📊 Template ID: {template_id}")
        print(f"   📊 Name: {template_name}")
        print(f"   📊 Success rate: {success_rate:.2f}")
        print(f"   📊 Tags: {', '.join(tags)}")
        
        return template
    
    # =========================================================================
    # MASTER LEARNINGS INTEGRATION
    # =========================================================================
    
    def update_master_learnings(
        self,
        template: Dict,
        example_data: Dict
    ) -> None:
        """
        Integriert Template in MASTER_LEARNINGS.json
        """
        
        if not LEARNINGS_AVAILABLE:
            print("\n⚠️  Master Learnings not available - skipping update")
            return
        
        print(f"\n{'='*70}")
        print("🔄 UPDATING MASTER LEARNINGS")
        print(f"{'='*70}")
        
        # Load current master learnings
        master = load_master_learnings()
        
        # Create backup
        backup_file = self.data_dir / f"MASTER_LEARNINGS_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(master, f, indent=2, ensure_ascii=False)
        print(f"   💾 Backup created: {backup_file.name}")
        
        # Prepare example entry
        example_entry = {
            "example_id": example_data.get('example_id', f"example_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "template_id": template.get('template_id', 'unknown'),
            "when_to_use": template.get('when_to_use', []),
            "restructuring_strategy": example_data.get('restructuring', {}).get('structure_pattern', {}).get('pattern_name', 'unknown'),
            "hook_pattern": example_data.get('hook_patterns', {}),
            "structure_pattern": example_data.get('structure_patterns', {}),
            "performance": example_data.get('performance', {}),
            "success_rate": template.get('success_rate', 0.0),
            "learned_at": datetime.now().isoformat()
        }
        
        # Initialize viral_examples if not exists
        if 'viral_examples' not in master:
            master['viral_examples'] = []
        
        # Check for duplicates (by template_id)
        existing_ids = [ex.get('template_id') for ex in master['viral_examples']]
        if template.get('template_id') not in existing_ids:
            master['viral_examples'].append(example_entry)
            print(f"   ✅ Added example: {example_entry['example_id']}")
        else:
            print(f"   ⚠️  Template already exists: {template.get('template_id')}")
            # Update existing
            for i, ex in enumerate(master['viral_examples']):
                if ex.get('template_id') == template.get('template_id'):
                    master['viral_examples'][i] = example_entry
                    print(f"   ✅ Updated existing example")
                    break
        
        # Update hook_mastery
        hook_patterns = example_data.get('hook_patterns', {})
        if hook_patterns:
            hook_mastery = master.get('hook_mastery', {})
            
            # Add hook formula if new
            hook_formula = hook_patterns.get('hook_formula', '')
            if hook_formula and hook_formula not in hook_mastery.get('hook_formulas', []):
                if 'hook_formulas' not in hook_mastery:
                    hook_mastery['hook_formulas'] = []
                hook_mastery['hook_formulas'].append(hook_formula)
                print(f"   ✅ Added hook formula: {hook_formula[:50]}...")
            
            # Add power words if new
            power_words = hook_patterns.get('power_words', [])
            existing_power_words = set([w.lower() for w in hook_mastery.get('power_words', [])])
            new_power_words = [w for w in power_words if w.lower() not in existing_power_words]
            if new_power_words:
                if 'power_words' not in hook_mastery:
                    hook_mastery['power_words'] = []
                hook_mastery['power_words'].extend(new_power_words)
                print(f"   ✅ Added {len(new_power_words)} new power words")
            
            master['hook_mastery'] = hook_mastery
        
        # Update structure_mastery
        structure_patterns = example_data.get('structure_patterns', {})
        if structure_patterns:
            structure_mastery = master.get('structure_mastery', {})
            
            # Add winning structures if new
            structure_name = structure_patterns.get('structure_name', '')
            if structure_name and 'winning_structures' not in structure_mastery:
                structure_mastery['winning_structures'] = []
            
            if structure_name and structure_name not in structure_mastery.get('winning_structures', []):
                structure_mastery['winning_structures'].append(structure_name)
                print(f"   ✅ Added structure pattern: {structure_name}")
            
            master['structure_mastery'] = structure_mastery
        
        # Add key insights if high performance
        performance = example_data.get('performance', {})
        views = performance.get('views', 0)
        watch_time = performance.get('watch_time', 0)
        
        if views > 500000 or watch_time > 80:
            ai_analysis = example_data.get('ai_analysis', {})
            insights = ai_analysis.get('analysis', {}).get('why_it_worked', [])
            
            if insights:
                key_insights = master.get('key_insights', [])
                for insight in insights[:2]:  # Max 2 insights per example
                    if insight not in key_insights:
                        key_insights.append(insight)
                        print(f"   ✅ Added key insight: {insight[:60]}...")
                
                master['key_insights'] = key_insights[:10]  # Keep max 10 insights
        
        # Update metadata
        master['metadata']['last_updated'] = datetime.now().isoformat()
        if 'sources' not in master['metadata']:
            master['metadata']['sources'] = []
        master['metadata']['sources'].append({
            'type': 'viral_example',
            'example_id': example_entry['example_id'],
            'added_at': datetime.now().isoformat()
        })
        
        # Save updated master learnings
        save_master_learnings(master)
        
        print(f"\n✅ Master Learnings updated!")
        print(f"   📊 Total examples: {len(master.get('viral_examples', []))}")
    
    # =========================================================================
    # MARKDOWN DOCUMENTATION
    # =========================================================================
    
    def create_markdown_doc(
        self,
        template: Dict,
        example_data: Dict,
        output_path: Path
    ) -> None:
        """
        Erstellt .md Dokumentation für das Beispiel
        """
        
        print(f"\n{'='*70}")
        print("📝 CREATING MARKDOWN DOCUMENTATION")
        print(f"{'='*70}")
        
        performance = example_data.get('performance', {})
        hook_patterns = example_data.get('hook_patterns', {})
        structure_patterns = example_data.get('structure_patterns', {})
        restructuring = example_data.get('restructuring', {})
        ai_analysis = example_data.get('ai_analysis', {})
        
        # Calculate virality score
        views = performance.get('views', 0)
        watch_time = performance.get('watch_time', 0)
        virality_score = (views / 1000000) * (watch_time / 100) if views > 0 else 0
        
        # Build markdown
        md_content = f"""# 📚 Viral Example: {template.get('name', 'Unknown Template')}

**Template ID:** `{template.get('template_id', 'unknown')}`  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Success Rate:** {template.get('success_rate', 0):.1%}

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Views** | {views:,} |
| **Watch Time** | {watch_time}% |
| **Followers Gained** | {performance.get('followers', 0):,} |
| **Virality Score** | {virality_score:.2f}x |

**Effectiveness Score:** {restructuring.get('effectiveness_score', 0):.2f}/1.0

---

## 🪝 Hook Analysis

### Hook Text
> "{hook_patterns.get('hook_text', 'N/A')[:200]}"

### Hook Characteristics

- **Type:** {hook_patterns.get('hook_type', 'unknown').title()}
- **Strength:** {hook_patterns.get('effectiveness', {}).get('hook_strength', 0)}/10
- **First Words:** {', '.join(hook_patterns.get('first_words', [])[:5])}
- **Power Words:** {', '.join(hook_patterns.get('power_words', [])[:5])}
- **Emotional Trigger:** {hook_patterns.get('emotional_trigger', 'unknown').title()}
- **Information Gap:** {'✅ Yes' if hook_patterns.get('information_gap') else '❌ No'}

### Hook Formula
```
{hook_patterns.get('hook_formula', 'N/A')}
```

### Why It Works
{hook_patterns.get('effectiveness', {}).get('watch_time_impact', 'unknown').title()} impact on watch time.

**Matched Patterns:** {', '.join(hook_patterns.get('matched_patterns', []))}

---

## 🔄 Restructuring Strategy

### Original vs Optimized

**Original Order:**
```
{restructuring.get('structure_pattern', {}).get('original', 'N/A')}
```

**Optimized Order:**
```
{restructuring.get('structure_pattern', {}).get('clip', 'N/A')}
```

### Restructuring Details

- **Pattern:** {restructuring.get('structure_pattern', {}).get('pattern_name', 'unknown').replace('_', ' ').title()}
- **Hook Moved to Front:** {'✅ Yes' if restructuring.get('hook_strategy', {}).get('moved_to_front') else '❌ No'}
- **Compression Ratio:** {restructuring.get('compression', {}).get('ratio', 0):.3f}
- **Removed Parts:** {restructuring.get('removed_parts', {}).get('removed_segments_count', 0)} segments

### What Was Removed

- **Intro:** {'✅ Yes' if restructuring.get('removed_parts', {}).get('intro') else '❌ No'}
- **Filler:** {'✅ Yes' if restructuring.get('removed_parts', {}).get('filler') else '❌ No'}
- **Slow Parts:** {'✅ Yes' if restructuring.get('removed_parts', {}).get('slow_parts') else '❌ No'}

---

## 📐 Structure Pattern

### Structure Name
**{structure_patterns.get('structure_name', 'unknown').replace('_', ' ').title()}**

### Phase Breakdown

"""
        
        # Add structure phases
        structure = structure_patterns.get('structure', {})
        for phase_name, phase_data in structure.items():
            md_content += f"""
#### {phase_name.title()}

- **Duration:** {phase_data.get('duration', 0):.1f}s
- **Start:** {phase_data.get('start', 0):.1f}s
- **End:** {phase_data.get('end', 0):.1f}s
- **Purpose:** {phase_data.get('purpose', 'N/A')}
"""
        
        # Timing
        timing = structure_patterns.get('timing', {})
        md_content += f"""
### Timing Analysis

- **Hook Duration:** {timing.get('hook_duration', 0):.1f}s
- **First Loop:** {timing.get('first_loop', 0):.1f}s
- **Pattern Interrupts:** {len(timing.get('pattern_interrupts', []))} at {', '.join([f'{t:.1f}s' for t in timing.get('pattern_interrupts', [])[:5]]) if timing.get('pattern_interrupts') else 'None'}
- **Total Duration:** {timing.get('total_duration', 0):.1f}s

**Optimal Length:** {timing.get('optimal_length', {}).get('sweet_spot', 45)}s (range: {timing.get('optimal_length', {}).get('min', 30)}-{timing.get('optimal_length', {}).get('max', 60)}s)

### Tension Arc

**Type:** {structure_patterns.get('tension_arc', {}).get('arc_type', 'unknown').title()}

- **Average Tension:** {structure_patterns.get('tension_arc', {}).get('average_tension', 0):.1f}/10
- **Min Tension:** {structure_patterns.get('tension_arc', {}).get('min_tension', 0):.1f}/10
- **Max Tension:** {structure_patterns.get('tension_arc', {}).get('max_tension', 0):.1f}/10

---

## 📋 Template: How to Replicate

### When to Use

"""
        
        for use_case in template.get('when_to_use', []):
            md_content += f"- ✅ {use_case}\n"
        
        md_content += "\n### When NOT to Use\n\n"
        
        for not_use_case in template.get('when_not_to_use', []):
            md_content += f"- ❌ {not_use_case}\n"
        
        md_content += "\n### Structure Steps\n\n"
        
        # Add structure steps
        structure_steps = template.get('structure', {})
        for step_key, step_data in sorted(structure_steps.items()):
            if isinstance(step_data, dict):
                md_content += f"""
**{step_key.replace('_', ' ').title()}**

- **Action:** {step_data.get('action', 'N/A')}
- **Criteria:** {step_data.get('criteria', 'N/A')}
- **Duration:** {step_data.get('duration', 'N/A')}
"""
        
        md_content += f"""
### Hook Examples

"""
        
        for example in template.get('hook_examples', [])[:3]:
            md_content += f"- \"{example[:100]}...\"\n"
        
        md_content += f"""
---

## ✅ Success Criteria

| Metric | Minimum | This Example |
|--------|---------|--------------|
| Views | {template.get('success_criteria', {}).get('min_views', 0):,} | {views:,} {'✅' if views >= template.get('success_criteria', {}).get('min_views', 0) else '❌'} |
| Watch Time | {template.get('success_criteria', {}).get('min_watch_time', 0)}% | {watch_time}% {'✅' if watch_time >= template.get('success_criteria', {}).get('min_watch_time', 0) else '❌'} |
| Followers | {template.get('success_criteria', {}).get('min_followers', 0):,} | {performance.get('followers', 0):,} {'✅' if performance.get('followers', 0) >= template.get('success_criteria', {}).get('min_followers', 0) else '❌'} |

---

## 🏷️ Tags & Related

**Tags:** {', '.join([f'`{tag}`' for tag in template.get('tags', [])])}

**Success Rate Prediction:** {template.get('success_rate', 0):.1%}

---

## 💡 Key Insights

"""
        
        # Add AI insights if available
        if ai_analysis:
            why_it_worked = ai_analysis.get('analysis', {}).get('why_it_worked', [])
            for insight in why_it_worked[:5]:
                md_content += f"- {insight}\n"
        
        md_content += f"""
---

*Generated automatically from viral example analysis*  
*Template ID: {template.get('template_id', 'unknown')}*
"""
        
        # Write markdown file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n✅ Markdown documentation created!")
        print(f"   📄 File: {output_path}")


def parse_args():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(
        description="Learn from viral clip examples - Extract restructuring patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using timestamps:
  python learn_from_viral_example.py \\
    --longform transcript.json \\
    --clip-start 120.5 --clip-end 165.0 \\
    --views 500000 --watch-time 85 --followers 5000
  
  # Using clip transcript file:
  python learn_from_viral_example.py \\
    --longform longform.json \\
    --clip clip.json \\
    --performance performance.json
  
  # With deep analysis:
  python learn_from_viral_example.py \\
    --longform transcript.json \\
    --clip-start 120.5 --clip-end 165.0 \\
    --views 1000000 --watch-time 90 --followers 10000 \\
    --deep-analysis
        """
    )
    
    # Longform input (required)
    parser.add_argument(
        "--longform",
        required=True,
        help="Path to longform video or transcript file"
    )
    
    # Clip input (either file OR timestamps)
    clip_group = parser.add_mutually_exclusive_group(required=True)
    clip_group.add_argument(
        "--clip",
        help="Path to clip transcript file"
    )
    clip_group.add_argument(
        "--clip-start",
        type=float,
        help="Clip start timestamp (requires --clip-end)"
    )
    
    parser.add_argument(
        "--clip-end",
        type=float,
        help="Clip end timestamp (requires --clip-start)"
    )
    
    # Performance data (either file OR individual metrics)
    perf_group = parser.add_argument_group("Performance Data")
    perf_group.add_argument(
        "--performance",
        help="Path to JSON file with performance data"
    )
    perf_group.add_argument(
        "--views",
        type=int,
        help="Views count"
    )
    perf_group.add_argument(
        "--watch-time",
        type=float,
        dest="watch_time",
        help="Watch time percentage (0-100)"
    )
    perf_group.add_argument(
        "--followers",
        type=int,
        help="Followers gained"
    )
    
    # Optional
    parser.add_argument(
        "--notes",
        help="Optional notes why it worked"
    )
    
    parser.add_argument(
        "--deep-analysis",
        action="store_true",
        help="Deep analysis for outliers (1M+ views)"
    )
    
    parser.add_argument(
        "--output",
        default="data/viral_examples",
        help="Output directory (default: data/viral_examples)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    
    args = parse_args()
    
    # Validate clip input
    if args.clip_start is not None and args.clip_end is None:
        print("❌ --clip-start requires --clip-end")
        return
    
    if args.clip_end is not None and args.clip_start is None:
        print("❌ --clip-end requires --clip-start")
        return
    
    # Validate performance input
    has_perf_file = args.performance is not None
    has_perf_cli = all([args.views is not None, args.watch_time is not None, args.followers is not None])
    
    if not has_perf_file and not has_perf_cli:
        print("❌ Performance data required: --performance OR (--views --watch-time --followers)")
        return
    
    # Initialize learner
    learner = ViralExampleLearner()
    
    if not learner.client:
        print("❌ No API key - AI analysis will be limited")
    
    print(f"\n{'='*70}")
    print("🚀 LEARNING FROM VIRAL EXAMPLE")
    print(f"{'='*70}")
    
    # 1. Load inputs
    print(f"\n📥 STEP 1: LOADING INPUTS")
    print("-" * 70)
    
    longform_segments = learner.load_transcript(args.longform)
    
    if not longform_segments:
        print("❌ Failed to load longform transcript")
        return
    
    clip_segments, clip_metadata = learner.load_clip_data(
        args.clip,
        args.clip_start,
        args.clip_end,
        longform_segments
    )
    
    if not clip_segments:
        print("❌ Failed to load clip data")
        return
    
    performance = learner.load_performance_data(
        args.performance,
        args.views,
        args.watch_time,
        args.followers
    )
    
    if not performance:
        print("❌ Failed to load performance data")
        return
    
    # 2. Compare transcripts
    print(f"\n📥 STEP 2: COMPARING TRANSCRIPTS")
    print("-" * 70)
    
    comparison = learner.compare_transcripts(longform_segments, clip_segments)
    
    if not comparison:
        print("❌ Comparison failed")
        return
    
    # 3. Analyze restructuring
    print(f"\n📥 STEP 3: ANALYZING RESTRUCTURING")
    print("-" * 70)
    
    restructuring = learner.analyze_restructuring(comparison, clip_segments, performance)
    
    if not restructuring:
        print("❌ Restructuring analysis failed")
        return
    
    # 4. Extract hook patterns
    print(f"\n📥 STEP 4: EXTRACTING HOOK PATTERNS")
    print("-" * 70)
    
    hook_segment = None
    for seg in comparison.get('used_segments', []):
        if seg.get('role') == 'hook':
            hook_segment = seg
            break
    
    if not hook_segment and comparison.get('used_segments'):
        hook_segment = comparison['used_segments'][0]
    
    if not hook_segment:
        print("❌ No hook segment found")
        return
    
    hook_patterns = learner.extract_hook_patterns(
        hook_segment,
        clip_segments,
        performance,
        comparison
    )
    
    if not hook_patterns:
        print("❌ Hook patterns extraction failed")
        return
    
    # 5. Extract structure patterns
    print(f"\n📥 STEP 5: EXTRACTING STRUCTURE PATTERNS")
    print("-" * 70)
    
    structure_patterns = learner.extract_structure_patterns(
        clip_segments,
        restructuring,
        performance
    )
    
    if not structure_patterns:
        print("❌ Structure patterns extraction failed")
        return
    
    # 6. AI analysis
    print(f"\n📥 STEP 6: AI ANALYSIS")
    print("-" * 70)
    
    ai_analysis = learner.ai_analyze_example(
        longform_segments,
        clip_segments,
        comparison,
        restructuring,
        performance,
        notes=args.notes,
        deep_analysis=args.deep_analysis
    )
    
    # 7. Create template
    print(f"\n📥 STEP 7: CREATING TEMPLATE")
    print("-" * 70)
    
    template = learner.create_template(
        hook_patterns,
        structure_patterns,
        restructuring,
        ai_analysis,
        performance
    )
    
    if not template:
        print("❌ Template creation failed")
        return
    
    # 8. Prepare example data
    example_id = f"example_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    example_data = {
        "example_id": example_id,
        "comparison": comparison,
        "restructuring": restructuring,
        "hook_patterns": hook_patterns,
        "structure_patterns": structure_patterns,
        "ai_analysis": ai_analysis,
        "performance": performance,
        "clip_metadata": clip_metadata,
        "notes": args.notes,
        "created_at": datetime.now().isoformat()
    }
    
    # 9. Save example
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    example_file = output_dir / f"{example_id}.json"
    with open(example_file, 'w') as f:
        json.dump({
            "example_id": example_id,
            "template": template,
            **example_data
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Example saved: {example_file}")
    
    # 10. Update Master Learnings
    print(f"\n📥 STEP 8: UPDATING MASTER LEARNINGS")
    print("-" * 70)
    
    learner.update_master_learnings(template, example_data)
    
    # 11. Create markdown documentation
    print(f"\n📥 STEP 9: CREATING MARKDOWN DOCUMENTATION")
    print("-" * 70)
    
    md_path = output_dir / f"{template['template_id']}.md"
    learner.create_markdown_doc(template, example_data, md_path)
    
    print(f"\n{'='*70}")
    print("✅ LEARNING COMPLETE!")
    print(f"{'='*70}")
    print(f"\n📁 Output files:")
    print(f"   • Example JSON: {example_file}")
    print(f"   • Markdown Doc: {md_path}")
    print(f"   • Master Learnings: Updated")
    print(f"\n📊 Summary:")
    print(f"   • Template ID: {template['template_id']}")
    print(f"   • Success Rate: {template['success_rate']:.1%}")
    print(f"   • Hook Strength: {hook_patterns.get('effectiveness', {}).get('hook_strength', 0)}/10")


if __name__ == "__main__":
    main()

