"""
Video Download Utility

Supports downloading from:
- YouTube
- Instagram
- TikTok
- Facebook
- Twitter/X
- And many more via yt-dlp

Based on working V1 implementation.
"""

import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


def is_url(path: str) -> bool:
    """Check if path is a URL."""
    url_patterns = [
        r'^https?://',
        r'^www\.',
        r'youtube\.com',
        r'youtu\.be',
        r'instagram\.com',
        r'tiktok\.com',
        r'facebook\.com',
        r'twitter\.com',
        r'x\.com',
    ]
    return any(re.search(pattern, path, re.IGNORECASE) for pattern in url_patterns)


def download_video(
    url: str,
    output_dir: str = "data/uploads",
    filename: Optional[str] = None
) -> Optional[Path]:
    """
    Download video from URL using yt-dlp.
    
    Supports: YouTube, Instagram, TikTok, Facebook, Twitter, etc.
    
    Args:
        url: Video URL
        output_dir: Directory to save video
        filename: Optional custom filename (without extension)
        
    Returns:
        Path to downloaded video or None on failure
    """
    print(f"\n{'='*70}")
    print("📥 DOWNLOADING VIDEO")
    print(f"{'='*70}")
    print(f"   URL: {url}")
    
    # Create uploads directory
    uploads_dir = Path(output_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}"
    
    output_template = str(uploads_dir / f"{filename}.%(ext)s")
    
    # yt-dlp command - FORCE video+audio merge
    cmd = [
        'yt-dlp',
        '--no-warnings',
        '--no-playlist',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '-o', output_template,
        url
    ]
    
    try:
        print("\n🔄 Downloading...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"   ⚠️ First attempt failed, trying alternative...")
            
            # Try alternative format
            cmd_alt = [
                'yt-dlp',
                '--no-warnings',
                '--no-playlist',
                '-f', 'best',
                '--recode-video', 'mp4',
                '-o', output_template,
                url
            ]
            result = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                print(f"❌ Download failed: {result.stderr[:200]}")
                return None
        
        # Find downloaded file
        downloaded_files = list(uploads_dir.glob(f"{filename}.*"))
        
        if not downloaded_files:
            print("❌ Could not find downloaded file")
            return None
        
        video_path = downloaded_files[0]
        
        # Verify it has video stream
        if not _verify_video(video_path):
            print("⚠️ File might be audio-only, trying to fix...")
            # Could add re-download logic here
        
        file_size = video_path.stat().st_size / 1024 / 1024
        print(f"\n✅ Downloaded: {video_path.name}")
        print(f"   Size: {file_size:.1f} MB")
        
        return video_path
        
    except subprocess.TimeoutExpired:
        print("❌ Download timed out (10 min limit)")
        return None
    except FileNotFoundError:
        print("❌ yt-dlp not found. Install with: pip install yt-dlp")
        return None
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None


def _verify_video(video_path: Path) -> bool:
    """Verify file has video stream."""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_type',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return 'video' in result.stdout
    except:
        return True  # Assume valid if can't check


def get_video_path(input_path: str) -> Tuple[Path, bool]:
    """
    Get video path, downloading if necessary.
    
    Args:
        input_path: Local path or URL
        
    Returns:
        Tuple of (video_path, was_downloaded)
    """
    if is_url(input_path):
        downloaded = download_video(input_path)
        if downloaded:
            return downloaded, True
        raise ValueError(f"Failed to download: {input_path}")
    else:
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {input_path}")
        return path, False

