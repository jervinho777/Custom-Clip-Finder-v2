#!/usr/bin/env python3
"""
Batch process multiple videos with Full AI
"""

from pathlib import Path
from process_video_full_ai import process_video
import time

def batch_process(video_dir: str, max_videos: int = 800):
    """
    Process all videos in directory
    """
    
    videos = list(Path(video_dir).glob("*.mp4"))
    
    print(f"🎬 Found {len(videos)} videos")
    print(f"💰 Estimated cost: ${len(videos) * 0.08:.2f}")
    print(f"⏱️  Estimated time: {len(videos) * 20 / 60:.1f} minutes\n")
    
    confirm = input("Continue? (y/n): ")
    if confirm.lower() != 'y':
        return
    
    successful = 0
    failed = 0
    
    for i, video in enumerate(videos[:max_videos], 1):
        print(f"\n[{i}/{len(videos)}] Processing: {video.name}")
        
        try:
            result = process_video(str(video))
            successful += 1
            print(f"   ✅ {len(result['ai_variants'])} variants")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            failed += 1
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"✅ Complete: {successful} success, {failed} failed")
    print(f"💰 Total cost: ${successful * 0.08:.2f}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_process_ai.py <video_directory>")
        sys.exit(1)
    
    batch_process(sys.argv[1])
