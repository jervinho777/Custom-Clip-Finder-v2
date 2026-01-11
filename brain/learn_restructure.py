"""
BRAIN Transformation Learner V3 - Robust Delta Analysis Engine

Der strategisch wichtigste Teil: Wir haben den UNFAIREN VORTEIL.
Wir besitzen Rohdaten (Longform) UND das Ergebnis (Viral Clip).

V3 IMPROVEMENTS:
- KEINE Duration-Constraints mehr
- Aggressive Text-Normalisierung für robustes Matching
- Automatische Transkript-Erstellung via AssemblyAI
- _ensure_transcripts_ready() vor Analyse
- Cache-First Architektur (Geld sparen)

Output: data/editing_patterns.json
"""

import os
import json
import difflib
import asyncio
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from collections import Counter

from dotenv import load_dotenv
load_dotenv()

# Transcription (AssemblyAI)
from utils.transcribe import transcribe_video

# Fuzzy Matching
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("⚠️ rapidfuzz not installed. Run: uv add rapidfuzz")

# Anthropic
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# =============================================================================
# Logger Setup
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Constants (KEINE DURATION LIMITS!)
# =============================================================================

# Hardcoded Paths
BASE_PATH = Path("/Users/jervinquisada/custom-clip-finder v2/data/training/Longform and Clips")
CACHE_DIR = Path("/Users/jervinquisada/custom-clip-finder v2/data/cache/transcripts")
PAIRS_CONFIG = Path("/Users/jervinquisada/custom-clip-finder v2/data/training/pairs_config.json")
OUTPUT_FILE = Path("/Users/jervinquisada/custom-clip-finder v2/data/editing_patterns.json")

# Video Extensions
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}

# Opus 4.5 Model ID
OPUS_MODEL = "claude-opus-4-5-20251101"

# Fuzzy Matching Configuration
SOURCE_MIN_CHARS = 3000  # Sources have > 3000 chars
CLIP_MAX_CHARS = 3000    # Clips have < 3000 chars
FUZZY_MATCH_THRESHOLD = 70  # Lowered from 85 - clips are heavily edited (jump cuts)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class VideoPair:
    """Ein Paar aus Longform und Clip Video-Dateien (vor Transkription)."""
    pair_id: str
    longform_video: Path
    clip_video: Path
    pattern_hint: str = ""
    notes: str = ""


@dataclass
class TranscriptPair:
    """Ein Paar aus Longform und Clip Transkript (nach Transkription)."""
    pair_id: str
    longform_path: str
    clip_path: str
    longform_text: str
    clip_text: str
    longform_file_size: int
    clip_file_size: int
    pattern_hint: str = ""
    notes: str = ""


@dataclass
class AlignmentResult:
    """Ergebnis der Text-Alignment-Analyse."""
    match_found: bool
    match_ratio: float
    start_word_index: int
    end_word_index: int
    matched_source_text: str
    source_word_count: int
    clip_word_count: int
    compression_ratio: float
    matching_blocks: int
    longest_match_words: int


@dataclass
class EditingPattern:
    """Ein gelerntes Editing-Pattern."""
    pair_id: str
    pattern_type: str
    source_text: str
    result_text: str
    match_ratio: float
    compression_ratio: float
    hook_was_moved: bool
    sentences_removed: int
    ai_reasoning: str
    editing_rules: List[str]
    micro_edits: List[Dict]
    confidence: float
    longform_source: str
    clip_source: str


# =============================================================================
# Opus Client
# =============================================================================

class OpusAnalyzer:
    """Claude Opus 4.5 für Editing-Analyse."""
    
    def __init__(self):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: uv add anthropic")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=api_key)
        self.model = OPUS_MODEL
        logger.info(f"🤖 OpusAnalyzer initialized: {self.model}")
    
    async def analyze_transformation(
        self,
        source_text: str,
        clip_text: str,
        pair_id: str,
        pattern_hint: str = "",
        match_ratio: float = 0.0
    ) -> Dict:
        """Analysiert die Transformation von Longform zu Clip."""
        system_prompt = """You are an ELITE VIDEO EDITOR analyzing the transformation from raw source to viral clip.

YOUR MISSION: Reverse-engineer what the editor did.

ANALYZE THESE MICRO-EDITS:

1. HOOK RESTRUCTURING
   - Did they move the ending/conclusion to the START?
   - Did they extract a "punchline" and front-load it?

2. PACING CUTS
   - Did they remove the host's question?
   - Did they cut fillers?

3. COMPRESSION
   - Did they cut "fluff" INSIDE sentences?
   - What % of the original was kept?

4. TENSION BUILDING
   - Did they remove context that "explains too much"?

OUTPUT FORMAT (JSON ONLY):
{
  "pattern_type": "hook_restructure" | "compression" | "clean_cut" | "pacing",
  "hook_was_moved": true/false,
  "hook_original_position": "end" | "middle" | "start" | "none",
  
  "editing_rules": [
    "RULE 1: ...",
    "RULE 2: ..."
  ],
  
  "micro_edits": [
    {"edit_type": "...", "description": "...", "impact": "..."}
  ],
  
  "compression_analysis": {
    "kept_percentage": 0.65,
    "removed_types": ["filler_words", "repetitions"],
    "key_cuts": ["..."]
  },
  
  "reasoning": "Brief explanation."
}"""

        hint_text = f"\nPATTERN HINT: {pattern_hint}" if pattern_hint else ""
        match_info = f"\nMATCH QUALITY: {match_ratio:.0%}" if match_ratio > 0 else ""
        
        user_prompt = f"""PAIR ID: {pair_id}
{hint_text}{match_info}

═══════════════════════════════════════════════════════════════
SOURCE (Raw Longform Section):
═══════════════════════════════════════════════════════════════
{source_text[:4000]}

═══════════════════════════════════════════════════════════════
RESULT (Viral Clip):
═══════════════════════════════════════════════════════════════
{clip_text[:3000]}

═══════════════════════════════════════════════════════════════
TASK: Analyze what the editor changed. Output ONLY valid JSON.
═══════════════════════════════════════════════════════════════"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.0,
                messages=[{"role": "user", "content": user_prompt}],
                system=system_prompt
            )
            
            content = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No JSON in response")
                
        except Exception as e:
            logger.error(f"Opus analysis failed for {pair_id}: {e}")
            return {
                "pattern_type": "unknown",
                "hook_was_moved": False,
                "editing_rules": [],
                "micro_edits": [],
                "reasoning": f"Analysis failed: {str(e)}",
                "error": True
            }


# =============================================================================
# Text Normalization (AGGRESSIVE!)
# =============================================================================

def normalize_text(text: str) -> str:
    """
    Aggressive Text-Normalisierung für robustes Matching.
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# =============================================================================
# Transformation Learner V3
# =============================================================================

class TransformationLearner:
    """
    Delta-Analyse Engine V3: 
    - Automatische Transkript-Erstellung
    - Robust gegen Transkript-Fehler
    - Cache-First Architektur
    """
    
    def __init__(self):
        self.base_path = BASE_PATH
        self.cache_dir = CACHE_DIR
        self.pairs_config = PAIRS_CONFIG
        self.output_file = OUTPUT_FILE
        
        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.opus: Optional[OpusAnalyzer] = None
        self.pairs: List[TranscriptPair] = []
        self.patterns: List[EditingPattern] = []
    
    # =========================================================================
    # TRANSCRIPT MANAGEMENT
    # =========================================================================
    
    def _get_cache_path(self, video_path: Path) -> Path:
        """Generiert konsistenten Cache-Pfad für ein Video."""
        # Nutze stem (Dateiname ohne Extension) + _transcript.json
        cache_name = f"{video_path.stem}_transcript.json"
        return self.cache_dir / cache_name
    
    def _transcript_exists(self, video_path: Path) -> bool:
        """Prüft ob Transkript im Cache existiert und valide ist."""
        cache_path = self._get_cache_path(video_path)
        
        if not cache_path.exists():
            return False
        
        # Prüfe ob JSON valide und Text enthält
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            text = data.get("text", "")
            if len(text) < 50:
                logger.warning(f"Cache exists but text too short: {cache_path.name}")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Invalid cache file {cache_path.name}: {e}")
            return False
    
    def _load_transcript(self, video_path: Path) -> Dict:
        """Lädt Transkript aus Cache."""
        cache_path = self._get_cache_path(video_path)
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _transcribe_video(self, video_path: Path) -> Dict:
        """
        Transkribiert ein Video via AssemblyAI und speichert im Cache.
        """
        cache_path = self._get_cache_path(video_path)
        
        print(f"      🎤 Transcribing: {video_path.name}")
        print(f"         (This may take a few minutes...)")
        
        try:
            # Nutze die existierende transcribe_video Funktion
            result = await transcribe_video(str(video_path), language="de")
            
            # Speichere im Cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"      ✅ Saved to cache: {cache_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed for {video_path.name}: {e}")
            return {"text": "", "segments": [], "error": str(e)}
    
    async def _ensure_transcripts_ready(self, video_paths: List[Path]) -> Dict[Path, Dict]:
        """
        Stellt sicher, dass alle Videos transkribiert sind.
        
        - Prüft Cache zuerst (spart Geld!)
        - Transkribiert nur fehlende Videos
        - Gibt Dict von video_path -> transcript_data zurück
        """
        print(f"\n📝 Ensuring transcripts ready for {len(video_paths)} videos...")
        
        transcripts = {}
        to_transcribe = []
        
        # Phase 1: Check Cache
        for video_path in video_paths:
            if self._transcript_exists(video_path):
                print(f"   ✅ Cache hit: {video_path.name}")
                transcripts[video_path] = self._load_transcript(video_path)
            else:
                print(f"   ❌ Cache miss: {video_path.name}")
                to_transcribe.append(video_path)
        
        print(f"\n   📊 Summary: {len(transcripts)} cached, {len(to_transcribe)} need transcription")
        
        # Phase 2: Transcribe missing
        if to_transcribe:
            print(f"\n   🎤 Transcribing {len(to_transcribe)} videos via AssemblyAI...")
            
            for i, video_path in enumerate(to_transcribe):
                print(f"\n   [{i+1}/{len(to_transcribe)}] {video_path.name}")
                
                result = await self._transcribe_video(video_path)
                transcripts[video_path] = result
                
                # Kleine Pause zwischen Transkriptionen
                if i < len(to_transcribe) - 1:
                    await asyncio.sleep(1)
        
        return transcripts
    
    # =========================================================================
    # VIDEO DISCOVERY
    # =========================================================================
    
    def _discover_videos(self) -> List[Path]:
        """Findet alle Videos im Training-Ordner."""
        videos = []
        
        if not self.base_path.exists():
            logger.warning(f"Base path not found: {self.base_path}")
            return videos
        
        for ext in VIDEO_EXTENSIONS:
            videos.extend(self.base_path.glob(f"*{ext}"))
            videos.extend(self.base_path.glob(f"*{ext.upper()}"))
        
        return sorted(videos, key=lambda p: p.stat().st_size, reverse=True)
    
    def _create_pairs_from_videos(
        self, 
        videos: List[Path], 
        transcripts: Dict[Path, Dict]
    ) -> List[TranscriptPair]:
        """
        Erstellt Paare aus Videos basierend auf Dateigröße.
        
        Größte Datei = Longform
        Alle anderen = potentielle Clips
        """
        if len(videos) < 2:
            return []
        
        # Sortiert nach Größe (größte zuerst)
        sorted_videos = sorted(videos, key=lambda p: p.stat().st_size, reverse=True)
        
        longform = sorted_videos[0]
        clips = sorted_videos[1:]
        
        pairs = []
        longform_data = transcripts.get(longform, {})
        longform_text = longform_data.get("text", "")
        
        if not longform_text:
            logger.warning(f"Longform has no text: {longform.name}")
            return pairs
        
        for clip in clips:
            clip_data = transcripts.get(clip, {})
            clip_text = clip_data.get("text", "")
            
            if not clip_text:
                logger.warning(f"Clip has no text, skipping: {clip.name}")
                continue
            
            pair = TranscriptPair(
                pair_id=f"auto_{clip.stem}",
                longform_path=str(self._get_cache_path(longform)),
                clip_path=str(self._get_cache_path(clip)),
                longform_text=longform_text,
                clip_text=clip_text,
                longform_file_size=longform.stat().st_size,
                clip_file_size=clip.stat().st_size
            )
            pairs.append(pair)
        
        return pairs
    
    async def _load_pairs_from_config(self, transcripts: Dict[Path, Dict]) -> List[TranscriptPair]:
        """Lädt Paare aus pairs_config.json."""
        pairs = []
        
        if not self.pairs_config.exists():
            return pairs
        
        with open(self.pairs_config) as f:
            config = json.load(f)
        
        transcripts_dir = self.cache_dir
        
        for pair_config in config.get("pairs", []):
            longform_file = transcripts_dir / pair_config["longform"]
            clip_file = transcripts_dir / pair_config["clip"]
            
            if not longform_file.exists() or not clip_file.exists():
                continue
            
            try:
                with open(longform_file) as f:
                    longform_data = json.load(f)
                with open(clip_file) as f:
                    clip_data = json.load(f)
                
                longform_text = longform_data.get("text", "")
                clip_text = clip_data.get("text", "")
                
                if not longform_text or not clip_text:
                    logger.warning(f"Empty text for pair: {pair_config['id']}")
                    continue
                
                pairs.append(TranscriptPair(
                    pair_id=pair_config["id"],
                    longform_path=str(longform_file),
                    clip_path=str(clip_file),
                    longform_text=longform_text,
                    clip_text=clip_text,
                    longform_file_size=longform_file.stat().st_size,
                    clip_file_size=clip_file.stat().st_size,
                    pattern_hint=pair_config.get("pattern", ""),
                    notes=pair_config.get("notes", "")
                ))
                print(f"      ✅ Loaded pair: {pair_config['id']}")
                
            except Exception as e:
                logger.warning(f"Error loading pair {pair_config['id']}: {e}")
        
        return pairs
    
    # =========================================================================
    # AUTOMATIC FUZZY MATCHING (V3.1)
    # =========================================================================
    
    def _load_all_transcripts_from_cache(self) -> Dict[str, Dict]:
        """
        Lädt ALLE JSON-Transkripte aus dem Cache-Verzeichnis.
        
        Returns:
            Dict mapping filename -> transcript data
        """
        transcripts = {}
        
        if not self.cache_dir.exists():
            logger.warning(f"Cache dir not found: {self.cache_dir}")
            return transcripts
        
        json_files = list(self.cache_dir.glob("*.json"))
        print(f"   📂 Found {len(json_files)} JSON files in cache")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                text = data.get("text", "")
                if text and len(text) > 50:  # Minimum viable text
                    transcripts[json_file.name] = {
                        "path": json_file,
                        "text": text,
                        "char_count": len(text),
                        "data": data
                    }
                else:
                    logger.debug(f"Skipping empty/short transcript: {json_file.name}")
                    
            except Exception as e:
                logger.warning(f"Failed to load {json_file.name}: {e}")
        
        return transcripts
    
    def _classify_transcripts(
        self, 
        transcripts: Dict[str, Dict]
    ) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Klassifiziert Transkripte in Sources (lang) und Clips (kurz).
        
        Sources: > 3000 chars (Longform Videos)
        Clips: < 3000 chars (Viral Clips)
        """
        sources = {}
        clips = {}
        
        for name, data in transcripts.items():
            char_count = data["char_count"]
            
            if char_count > SOURCE_MIN_CHARS:
                sources[name] = data
            elif char_count < CLIP_MAX_CHARS:
                clips[name] = data
            else:
                # Edge case: exactly 3000 chars - treat as clip
                clips[name] = data
        
        return sources, clips
    
    def _fuzzy_match_pairs(
        self,
        sources: Dict[str, Dict],
        clips: Dict[str, Dict]
    ) -> List[TranscriptPair]:
        """
        Führt automatisches Fuzzy-Matching zwischen Clips und Sources durch.
        
        Für jeden Clip wird die beste passende Source gesucht.
        Nur Matches mit Score > FUZZY_MATCH_THRESHOLD werden akzeptiert.
        """
        if not RAPIDFUZZ_AVAILABLE:
            logger.error("rapidfuzz not available! Run: uv add rapidfuzz")
            return []
        
        pairs = []
        matched_clips = set()
        
        print(f"\n   🔍 Fuzzy Matching: {len(clips)} clips × {len(sources)} sources")
        print(f"   📊 Threshold: {FUZZY_MATCH_THRESHOLD}%")
        
        for clip_name, clip_data in clips.items():
            clip_text = clip_data["text"]
            best_score = 0
            best_source_name = None
            best_source_data = None
            
            # Compare against all sources
            for source_name, source_data in sources.items():
                source_text = source_data["text"]
                
                # Use partial_ratio for substring matching
                # This is ideal for finding clips within longform videos
                score = fuzz.partial_ratio(clip_text, source_text)
                
                if score > best_score:
                    best_score = score
                    best_source_name = source_name
                    best_source_data = source_data
            
            # Check threshold
            if best_score >= FUZZY_MATCH_THRESHOLD and best_source_name:
                print(f"   🔗 Matched '{clip_name[:30]}...' → '{best_source_name[:30]}...' (Score: {best_score}%)")
                
                pair = TranscriptPair(
                    pair_id=f"fuzzy_{clip_name.replace('.json', '')}",
                    longform_path=str(best_source_data["path"]),
                    clip_path=str(clip_data["path"]),
                    longform_text=best_source_data["text"],
                    clip_text=clip_text,
                    longform_file_size=best_source_data["path"].stat().st_size,
                    clip_file_size=clip_data["path"].stat().st_size,
                    pattern_hint=f"fuzzy_match_{best_score}",
                    notes=f"Auto-matched with score {best_score}%"
                )
                pairs.append(pair)
                matched_clips.add(clip_name)
            else:
                # Better logging: show best candidate for debugging
                if best_source_name:
                    print(f"   ⚠️ No match for '{clip_name[:35]}'. Best candidate was '{best_source_name[:25]}' (Score: {best_score}%)")
                else:
                    print(f"   ⚠️ No match for '{clip_name[:40]}' - no sources available")
        
        # Summary
        match_rate = len(pairs) / len(clips) * 100 if clips else 0
        print(f"\n   📊 Matching Summary:")
        print(f"      Matched: {len(pairs)}/{len(clips)} clips ({match_rate:.0f}%)")
        print(f"      Unmatched: {len(clips) - len(pairs)}")
        
        return pairs
    
    # =========================================================================
    # TEXT ALIGNMENT (ROBUST!)
    # =========================================================================
    
    def _align_texts_robust(self, pair: TranscriptPair) -> AlignmentResult:
        """
        Robustes Text-Alignment mit aggressiver Normalisierung.
        """
        longform_norm = normalize_text(pair.longform_text)
        clip_norm = normalize_text(pair.clip_text)
        
        if not longform_norm or not clip_norm:
            return AlignmentResult(
                match_found=False,
                match_ratio=0,
                start_word_index=0,
                end_word_index=0,
                matched_source_text="",
                source_word_count=len(longform_norm.split()) if longform_norm else 0,
                clip_word_count=len(clip_norm.split()) if clip_norm else 0,
                compression_ratio=1.0,
                matching_blocks=0,
                longest_match_words=0
            )
        
        longform_words = longform_norm.split()
        clip_words = clip_norm.split()
        
        best_ratio = 0
        best_start = 0
        best_end = 0
        best_match_text = ""
        
        window_size = len(clip_words) + min(100, len(clip_words))
        step_size = max(1, len(clip_words) // 10)
        
        for i in range(0, max(1, len(longform_words) - len(clip_words) // 2), step_size):
            window_end = min(i + window_size, len(longform_words))
            window_words = longform_words[i:window_end]
            
            matcher = difflib.SequenceMatcher(
                None, 
                clip_words, 
                window_words,
                autojunk=False
            )
            
            ratio = matcher.ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_start = i
                best_end = window_end
                
                original_words = pair.longform_text.split()
                if best_start < len(original_words):
                    actual_end = min(best_end, len(original_words))
                    best_match_text = " ".join(original_words[best_start:actual_end])
        
        final_matcher = difflib.SequenceMatcher(
            None, 
            clip_words, 
            longform_words[best_start:best_end] if best_end > best_start else [],
            autojunk=False
        )
        matching_blocks = final_matcher.get_matching_blocks()
        longest_match = max((b.size for b in matching_blocks), default=0)
        
        source_word_count = best_end - best_start if best_end > best_start else len(longform_words)
        clip_word_count = len(clip_words)
        compression = clip_word_count / source_word_count if source_word_count > 0 else 1.0
        
        return AlignmentResult(
            match_found=best_ratio > 0.25,  # 25% Threshold
            match_ratio=best_ratio,
            start_word_index=best_start,
            end_word_index=best_end,
            matched_source_text=best_match_text,
            source_word_count=source_word_count,
            clip_word_count=clip_word_count,
            compression_ratio=compression,
            matching_blocks=len(matching_blocks) - 1,
            longest_match_words=longest_match
        )
    
    def _count_removed_sentences(self, source: str, result: str) -> int:
        """Zählt entfernte Sätze."""
        source_sentences = len(re.split(r'[.!?]+', source))
        result_sentences = len(re.split(r'[.!?]+', result))
        return max(0, source_sentences - result_sentences)
    
    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================
    
    async def run_delta_analysis(self) -> Dict:
        """
        Hauptfunktion: Führt die komplette Delta-Analyse durch.
        
        1. Entdecke alle Videos
        2. Stelle sicher, dass alle transkribiert sind (_ensure_transcripts_ready)
        3. Erstelle Paare
        4. Analysiere mit Opus 4.5
        5. Speichere Patterns
        """
        print("\n" + "="*70)
        print("🔬 TRANSFORMATION LEARNER V3 - Robust Delta Analysis")
        print("="*70)
        print(f"   Base Path: {self.base_path}")
        print(f"   Cache Dir: {self.cache_dir}")
        print(f"   ⚠️  NO DURATION LIMITS - Automatic Transcription")
        
        # Initialize Opus
        try:
            self.opus = OpusAnalyzer()
        except Exception as e:
            print(f"❌ Failed to initialize Opus: {e}")
            return {}
        
        # Step 1: Discover all videos
        print("\n📹 Step 1: Discovering videos...")
        videos = self._discover_videos()
        print(f"   Found {len(videos)} video files")
        
        for v in videos[:5]:
            size_mb = v.stat().st_size / 1024 / 1024
            print(f"      - {v.name} ({size_mb:.1f} MB)")
        if len(videos) > 5:
            print(f"      ... and {len(videos) - 5} more")
        
        if not videos:
            print("❌ No videos found. Exiting.")
            return {}
        
        # Step 2: Ensure all transcripts ready
        print("\n📝 Step 2: Ensuring transcripts...")
        transcripts = await self._ensure_transcripts_ready(videos)
        
        # Count valid transcripts
        valid_transcripts = {k: v for k, v in transcripts.items() if v.get("text")}
        print(f"\n   ✅ {len(valid_transcripts)}/{len(videos)} videos have valid transcripts")
        
        if len(valid_transcripts) < 2:
            print("❌ Need at least 2 valid transcripts for pairing. Exiting.")
            return {}
        
        # Step 3: Create pairs via FUZZY MATCHING
        print("\n🔗 Step 3: Automatic Fuzzy Matching...")
        
        # Load ALL transcripts from cache (not just the videos we just processed)
        print("   📂 Loading all cached transcripts...")
        all_cached_transcripts = self._load_all_transcripts_from_cache()
        
        if not all_cached_transcripts:
            print("   ⚠️ No transcripts in cache. Falling back to video-based pairing...")
            valid_videos = [v for v in videos if v in valid_transcripts]
            self.pairs = self._create_pairs_from_videos(valid_videos, transcripts)
        else:
            # Classify into sources and clips
            print(f"   📊 Classifying {len(all_cached_transcripts)} transcripts by length...")
            sources, clips = self._classify_transcripts(all_cached_transcripts)
            print(f"      Sources (>{SOURCE_MIN_CHARS} chars): {len(sources)}")
            print(f"      Clips (<{CLIP_MAX_CHARS} chars): {len(clips)}")
            
            if not sources or not clips:
                print("   ⚠️ Need both sources and clips for matching. Falling back...")
                valid_videos = [v for v in videos if v in valid_transcripts]
                self.pairs = self._create_pairs_from_videos(valid_videos, transcripts)
            else:
                # Perform fuzzy matching
                self.pairs = self._fuzzy_match_pairs(sources, clips)
        
        print(f"\n   ✅ Created {len(self.pairs)} pairs via fuzzy matching")
        
        if not self.pairs:
            print("❌ No pairs created. Exiting.")
            return {}
        
        # Step 4: Alignment & Analysis
        print("\n🔍 Step 4: Alignment & Delta Analysis...")
        
        for i, pair in enumerate(self.pairs):
            print(f"\n   [{i+1}/{len(self.pairs)}] Analyzing: {pair.pair_id}")
            
            # Validate texts
            if not pair.longform_text or not pair.clip_text:
                print(f"      ⚠️ SKIPPING: Empty text detected!")
                print(f"         Longform: {len(pair.longform_text)} chars")
                print(f"         Clip: {len(pair.clip_text)} chars")
                continue
            
            # Alignment
            alignment = self._align_texts_robust(pair)
            
            if alignment.match_found:
                print(f"      ✅ Match found!")
                print(f"         Ratio: {alignment.match_ratio:.1%}")
                print(f"         Compression: {alignment.compression_ratio:.1%}")
            else:
                print(f"      ⚠️ Low match ({alignment.match_ratio:.1%}) - using full comparison")
            
            # AI Analysis
            print(f"      🤖 Running Opus 4.5 analysis...")
            
            source_for_ai = alignment.matched_source_text if alignment.match_found else pair.longform_text[:4000]
            
            ai_result = await self.opus.analyze_transformation(
                source_text=source_for_ai,
                clip_text=pair.clip_text,
                pair_id=pair.pair_id,
                pattern_hint=pair.pattern_hint,
                match_ratio=alignment.match_ratio
            )
            
            pattern = EditingPattern(
                pair_id=pair.pair_id,
                pattern_type=ai_result.get("pattern_type", "unknown"),
                source_text=source_for_ai[:2000],
                result_text=pair.clip_text[:2000],
                match_ratio=alignment.match_ratio,
                compression_ratio=alignment.compression_ratio,
                hook_was_moved=ai_result.get("hook_was_moved", False),
                sentences_removed=self._count_removed_sentences(source_for_ai, pair.clip_text),
                ai_reasoning=ai_result.get("reasoning", ""),
                editing_rules=ai_result.get("editing_rules", []),
                micro_edits=ai_result.get("micro_edits", []),
                confidence=alignment.match_ratio,
                longform_source=pair.longform_path,
                clip_source=pair.clip_path
            )
            
            self.patterns.append(pattern)
            
            print(f"      Pattern: {pattern.pattern_type}")
            print(f"      Hook moved: {pattern.hook_was_moved}")
            if pattern.editing_rules:
                print(f"      Rules: {len(pattern.editing_rules)}")
            
            await asyncio.sleep(0.5)
        
        # Step 5: Save
        print("\n💾 Step 5: Saving results...")
        result = self._save_patterns()
        
        self._print_summary()
        
        return result
    
    def _save_patterns(self) -> Dict:
        """Speichert die gelernten Patterns."""
        all_rules = []
        all_micro_edits = []
        
        for p in self.patterns:
            all_rules.extend(p.editing_rules)
            all_micro_edits.extend(p.micro_edits)
        
        rule_counts = Counter(all_rules)
        edit_type_counts = Counter(e.get("edit_type", "unknown") for e in all_micro_edits)
        pattern_types = Counter(p.pattern_type for p in self.patterns)
        
        hook_moved_count = sum(1 for p in self.patterns if p.hook_was_moved)
        hook_move_rate = hook_moved_count / len(self.patterns) if self.patterns else 0
        avg_match = sum(p.match_ratio for p in self.patterns) / len(self.patterns) if self.patterns else 0
        
        result = {
            "version": "3.0-robust",
            "model": OPUS_MODEL,
            "generated_at": datetime.now().isoformat(),
            
            "statistics": {
                "total_pairs_analyzed": len(self.patterns),
                "avg_match_ratio": f"{avg_match:.1%}",
                "hook_move_rate": f"{hook_move_rate:.1%}",
                "avg_compression": f"{sum(p.compression_ratio for p in self.patterns) / len(self.patterns):.1%}" if self.patterns else "N/A",
                "pattern_distribution": dict(pattern_types),
                "micro_edit_distribution": dict(edit_type_counts)
            },
            
            "top_rules": [
                {"rule": rule, "occurrences": count}
                for rule, count in rule_counts.most_common(20)
            ],
            
            "patterns": [asdict(p) for p in self.patterns],
            
            "actionable_insights": self._generate_insights()
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to: {self.output_file}")
        return result
    
    def _generate_insights(self) -> List[Dict]:
        """Generiert actionable insights."""
        insights = []
        
        hook_patterns = [p for p in self.patterns if p.hook_was_moved]
        if hook_patterns:
            rate = len(hook_patterns) / len(self.patterns) if self.patterns else 0
            insights.append({
                "insight": "Hook Restructuring is Critical",
                "detail": f"{len(hook_patterns)} of {len(self.patterns)} clips ({rate:.0%}) moved the hook.",
                "action": "ALWAYS check if the ending contains a better hook.",
                "priority": "HIGH"
            })
        
        if self.patterns:
            avg_compression = sum(p.compression_ratio for p in self.patterns) / len(self.patterns)
            if avg_compression < 0.7:
                insights.append({
                    "insight": "Heavy Compression Applied",
                    "detail": f"Average: {avg_compression:.0%} of original kept.",
                    "action": "Be aggressive in cutting filler words and context.",
                    "priority": "HIGH"
                })
        
        return insights
    
    def _print_summary(self):
        """Druckt Zusammenfassung."""
        print("\n" + "="*70)
        print("✅ TRANSFORMATION LEARNING V3 COMPLETE")
        print("="*70)
        
        print(f"\n📊 STATISTICS:")
        print(f"   Pairs analyzed: {len(self.patterns)}")
        
        if self.patterns:
            avg_match = sum(p.match_ratio for p in self.patterns) / len(self.patterns)
            print(f"   Avg match ratio: {avg_match:.1%}")
            
            hook_moved = sum(1 for p in self.patterns if p.hook_was_moved)
            print(f"   Hook restructured: {hook_moved}/{len(self.patterns)}")
        
        print(f"\n📁 Output: {self.output_file}")


# =============================================================================
# Helper Functions
# =============================================================================

def load_editing_patterns() -> Dict:
    """Lädt die gelernten Editing-Patterns."""
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            return json.load(f)
    return {}


def get_top_rules(n: int = 10) -> List[str]:
    """Gibt die Top-N Editing Rules zurück."""
    patterns = load_editing_patterns()
    return [r["rule"] for r in patterns.get("top_rules", [])[:n]]


# =============================================================================
# CLI
# =============================================================================

async def run_learning():
    """Entry point."""
    learner = TransformationLearner()
    return await learner.run_delta_analysis()


if __name__ == "__main__":
    print("🔬 Starting Transformation Learner V3")
    print("   ✅ Automatic Transcription via AssemblyAI")
    print("   ✅ Cache-First Architecture")
    print("   ✅ Aggressive Text Normalization")
    asyncio.run(run_learning())
