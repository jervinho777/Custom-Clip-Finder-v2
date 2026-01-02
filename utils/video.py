"""
Video Processing Utilities

FFmpeg-based video extraction and processing.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Optional


def get_video_info(video_path: str | Path) -> Dict:
    """
    Get video metadata using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dict with duration, fps, width, height, codec info
    """
    video_path = Path(video_path)
    
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        video_stream = next(
            (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
            None
        )
        audio_stream = next(
            (s for s in data.get('streams', []) if s.get('codec_type') == 'audio'),
            None
        )
        
        duration = float(data.get('format', {}).get('duration', 0))
        
        fps = 25.0
        if video_stream and 'r_frame_rate' in video_stream:
            fps_str = video_stream['r_frame_rate']
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                fps = num / den if den > 0 else 25.0
        
        return {
            'duration': duration,
            'fps': fps,
            'width': video_stream.get('width', 1920) if video_stream else 1920,
            'height': video_stream.get('height', 1080) if video_stream else 1080,
            'video_codec': video_stream.get('codec_name') if video_stream else None,
            'audio_codec': audio_stream.get('codec_name') if audio_stream else None,
            'sample_rate': int(audio_stream.get('sample_rate', 48000)) if audio_stream else 48000,
            'path': str(video_path.absolute()),
            'filename': video_path.name,
            'size_mb': Path(video_path).stat().st_size / (1024 * 1024)
        }
    except Exception as e:
        return {
            'duration': 0,
            'fps': 25.0,
            'width': 1920,
            'height': 1080,
            'error': str(e)
        }


def extract_clip(
    source_path: str | Path,
    output_path: str | Path,
    start_time: float,
    end_time: float,
    codec: str = "copy",
    audio_codec: str = "copy"
) -> Optional[Path]:
    """
    Extract a clip from a video file.
    
    Args:
        source_path: Path to source video
        output_path: Path for output clip
        start_time: Start timestamp in seconds
        end_time: End timestamp in seconds
        codec: Video codec (default: copy for fast extraction)
        audio_codec: Audio codec (default: copy)
        
    Returns:
        Path to extracted clip or None on failure
    """
    source_path = Path(source_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    duration = end_time - start_time
    
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(start_time),
        '-i', str(source_path),
        '-t', str(duration),
        '-c:v', codec,
        '-c:a', audio_codec,
        '-avoid_negative_ts', 'make_zero',
        str(output_path)
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            check=True
        )
        return output_path if output_path.exists() else None
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return None


def extract_audio(
    video_path: str | Path,
    output_path: str | Path,
    sample_rate: int = 16000
) -> Optional[Path]:
    """
    Extract audio from video for transcription.
    
    Args:
        video_path: Path to video file
        output_path: Path for output audio (wav)
        sample_rate: Audio sample rate (16kHz for most ASR)
        
    Returns:
        Path to extracted audio or None on failure
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-vn',  # No video
        '-acodec', 'pcm_s16le',
        '-ar', str(sample_rate),
        '-ac', '1',  # Mono
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_path if output_path.exists() else None
    except subprocess.CalledProcessError:
        return None

