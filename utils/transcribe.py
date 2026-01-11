"""
Video Transcription using AssemblyAI

Word-level timestamps for precise clip extraction.
CACHE-FIRST: Uses Cache class to avoid unnecessary API calls.
AUDIO OPTIMIZATION: Extracts audio locally before upload for faster transfers.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Import Cache system
from utils.cache import Cache

# =============================================================================
# Configuration
# =============================================================================

AUDIO_CACHE_DIR = Path("/Users/jervinquisada/custom-clip-finder v2/data/audio")

# Ensure audio cache directory exists
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Global cache instance
_cache: Optional[Cache] = None


def _get_cache() -> Cache:
    """Get or initialize cache instance."""
    global _cache
    if _cache is None:
        _cache = Cache()
    return _cache


def _get_file_hash(file_path: Path) -> str:
    """Generate hash for file identification."""
    stat = file_path.stat()
    key = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def extract_audio(video_path: Path, file_hash: str) -> Path:
    """
    Extract audio from video for optimized upload.
    
    AUDIO CACHE:
    - MP3 at 64kbps is ~10x smaller than video
    - Faster upload to AssemblyAI
    - Cached locally for repeat transcriptions
    
    Args:
        video_path: Path to video file
        file_hash: Unique hash for caching
        
    Returns:
        Path to audio file (or original video if extraction fails)
    """
    audio_path = AUDIO_CACHE_DIR / f"{file_hash}.mp3"
    
    # Check audio cache first
    if audio_path.exists():
        print(f"   🎵 Audio Cache Hit: {audio_path.name}")
        return audio_path
    
    try:
        from moviepy.editor import VideoFileClip
        
        print(f"   🎵 Extracting audio: {video_path.name} → MP3...")
        
        video = VideoFileClip(str(video_path))
        
        # Extract audio at low bitrate for small file size
        video.audio.write_audiofile(
            str(audio_path),
            codec='mp3',
            bitrate='64k',
            verbose=False,
            logger=None  # Suppress moviepy progress bar
        )
        
        video.close()
        
        # Log size comparison
        video_size_mb = video_path.stat().st_size / (1024 * 1024)
        audio_size_mb = audio_path.stat().st_size / (1024 * 1024)
        ratio = video_size_mb / audio_size_mb if audio_size_mb > 0 else 1
        
        print(f"   ✅ Audio extracted: {audio_size_mb:.1f}MB (was {video_size_mb:.1f}MB, {ratio:.0f}x smaller)")
        
        return audio_path
        
    except Exception as e:
        print(f"   ⚠️ Audio extraction failed, using original video: {e}")
        return video_path


async def transcribe_video(
    video_path: str | Path,
    language: str = "de",
    use_cache: bool = True
) -> Dict:
    """
    Transcribe video using AssemblyAI with caching.
    
    CACHE-FIRST ARCHITECTURE:
    1. Check cache for existing transcript
    2. If found: return cached result (saves API cost!)
    3. If not: call AssemblyAI, then cache the result
    
    Args:
        video_path: Path to video file
        language: Language code (default: German)
        use_cache: Whether to use caching (default: True)
        
    Returns:
        Dict with full text, segments, and word-level timestamps
    """
    video_path = Path(video_path)
    cache = _get_cache()
    
    # =========================================================================
    # STEP 1: Check Cache First
    # =========================================================================
    if use_cache:
        cached = cache.get_transcript(video_path)
        
        if cached:
            # Handle both old and new cache formats
            transcript_data = cached.get("transcript", cached)
            
            # Validate that we have actual text
            text = transcript_data.get("text", "")
            if text and len(text) > 10:
                print(f"   ✅ Loaded transcript from cache: {video_path.name}")
                return transcript_data
            else:
                print(f"   ⚠️ Cache exists but empty/invalid, re-transcribing: {video_path.name}")
    
    # =========================================================================
    # STEP 2: Extract Audio (Optimized Upload)
    # =========================================================================
    file_hash = _get_file_hash(video_path)
    upload_path = extract_audio(video_path, file_hash)
    
    # =========================================================================
    # STEP 3: Transcribe with AssemblyAI
    # =========================================================================
    print(f"   🎤 Transcribing via AssemblyAI: {upload_path.name}")
    
    import assemblyai as aai
    
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise ValueError("ASSEMBLYAI_API_KEY not found in environment")
    
    aai.settings.api_key = api_key
    
    config = aai.TranscriptionConfig(
        language_code=language,
        punctuate=True,
        format_text=True,
    )
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(str(upload_path), config=config)
    
    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Transcription failed: {transcript.error}")
    
    # Build result
    segments = _build_segments(transcript.words or [])
    
    result = {
        "text": transcript.text or "",
        "segments": segments,
        "words": [
            {
                "text": w.text,
                "start": w.start / 1000,  # Convert to seconds
                "end": w.end / 1000,
                "confidence": w.confidence
            }
            for w in (transcript.words or [])
        ],
        "duration": (transcript.words[-1].end / 1000) if transcript.words else 0,
        "language": language
    }
    
    # =========================================================================
    # STEP 4: Save to Cache
    # =========================================================================
    if use_cache:
        cache_path = cache.set_transcript(video_path, result)
        print(f"   💾 Saved transcript to cache: {cache_path.name}")
    
    print(f"   ✅ Transcription complete: {len(result['text'])} chars, {len(segments)} segments")
    
    return result


def _build_segments(words: list, max_segment_duration: float = 10.0) -> List[Dict]:
    """
    Build segments from word-level timestamps.
    
    Segments are split on:
    - Sentence boundaries (., !, ?)
    - Max duration threshold
    """
    if not words:
        return []
    
    segments = []
    current_segment = {
        "start": words[0].start / 1000,
        "text": "",
        "words": []
    }
    
    for word in words:
        current_segment["text"] += (" " if current_segment["text"] else "") + word.text
        current_segment["words"].append(word)
        current_segment["end"] = word.end / 1000
        
        # Check for segment break
        is_sentence_end = word.text.rstrip().endswith(('.', '!', '?'))
        duration = current_segment["end"] - current_segment["start"]
        
        if is_sentence_end or duration >= max_segment_duration:
            segments.append({
                "start": current_segment["start"],
                "end": current_segment["end"],
                "text": current_segment["text"].strip()
            })
            
            # Start new segment
            current_segment = {
                "start": word.end / 1000,
                "text": "",
                "words": []
            }
    
    # Add remaining segment
    if current_segment["text"]:
        segments.append({
            "start": current_segment["start"],
            "end": current_segment["end"],
            "text": current_segment["text"].strip()
        })
    
    return segments


def transcribe_video_sync(
    video_path: str | Path,
    language: str = "de",
    use_cache: bool = True
) -> Dict:
    """
    Synchronous wrapper for transcribe_video.
    """
    import asyncio
    return asyncio.run(transcribe_video(video_path, language, use_cache))


def clear_transcript_cache():
    """Clear all cached transcripts."""
    cache = _get_cache()
    cache.clear("transcripts")
    print("🗑️ Transcript cache cleared")


def get_cache_stats() -> Dict:
    """Get cache statistics."""
    cache = _get_cache()
    return cache.stats()
