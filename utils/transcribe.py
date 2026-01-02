"""
Video Transcription using AssemblyAI

Word-level timestamps for precise clip extraction.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


async def transcribe_video(
    video_path: str | Path,
    language: str = "de"
) -> Dict:
    """
    Transcribe video using AssemblyAI.
    
    Args:
        video_path: Path to video file
        language: Language code (default: German)
        
    Returns:
        Dict with full text, segments, and word-level timestamps
    """
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
    transcript = transcriber.transcribe(str(video_path), config=config)
    
    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Transcription failed: {transcript.error}")
    
    # Build segments from words
    segments = _build_segments(transcript.words or [])
    
    return {
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
    language: str = "de"
) -> Dict:
    """
    Synchronous wrapper for transcribe_video.
    """
    import asyncio
    return asyncio.run(transcribe_video(video_path, language))

