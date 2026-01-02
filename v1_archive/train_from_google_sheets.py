#!/usr/bin/env python3
"""
Complete Training Pipeline from Google Sheets
TOP 10 CLIPS VERSION
"""

import json
from pathlib import Path
import logging
from typing import List, Dict
import sys

from backend.utils.google_sheets import GoogleSheetsClient
from backend.utils.video_downloader import VideoDownloader
from backend.processors.video_processor import VideoProcessor
from backend.processors.transcriber import Transcriber
from backend.processors.feature_extractor import FeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GOATTrainingPipeline:
    """Complete training pipeline from Google Sheets"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient()
        self.downloader = VideoDownloader()
        self.transcriber = Transcriber(model_size="medium")
        self.feature_extractor = FeatureExtractor()
    
    def run(self, 
            top_n: int = 10,
            skip_download: bool = False,
            sort_by: str = 'views'):
        """
        Main pipeline
        
        Args:
            top_n: Number of top clips to analyze (default: 10)
            skip_download: Skip download if files exist
            sort_by: Sort clips by: 'views', 'watch_time', 'engagement', or 'order' (sheet order)
        
        Steps:
        1. Read Google Sheet
        2. Sort & select Top N clips
        3. Download videos
        4. Analyze each video
        5. Extract features
        6. Save training data
        """
        
        print("🚀 GOAT TRAINING PIPELINE - TOP {} CLIPS\n".format(top_n))
        
        # Step 1: Read Sheet
        print("=" * 60)
        print("STEP 1: Reading Google Sheet")
        print("=" * 60 + "\n")
        
        all_clips = self.sheets_client.get_goat_clips()
        
        if not all_clips:
            print("❌ No clips found in sheet")
            return
        
        print(f"✅ Found {len(all_clips)} total clips in sheet")
        
        # Step 2: Sort & Filter Top N
        print("\n" + "=" * 60)
        print(f"STEP 2: Selecting Top {top_n} Clips")
        print("=" * 60 + "\n")
        
        clips = self._select_top_clips(all_clips, top_n, sort_by)
        
        print(f"📊 Selected {len(clips)} clips based on: {sort_by}")
        print("\nTop clips:")
        for i, clip in enumerate(clips, 1):
            print(f"  {i}. {clip['name']}")
            if 'views' in clip:
                print(f"     Views: {clip['views']:,.0f}")
            if 'watch_time_percentage' in clip:
                print(f"     Watch Time: {clip['watch_time_percentage']:.1f}%")
        
        # Confirm before proceeding
        if not skip_download:
            print(f"\n⚠️  About to download {len(clips)} videos")
            confirm = input("Continue? (y/n): ")
            if confirm.lower() != 'y':
                print("Aborted.")
                return
        
        # Step 3: Download videos
        if not skip_download:
            print("\n" + "=" * 60)
            print("STEP 3: Downloading Videos")
            print("=" * 60 + "\n")
            
            for i, clip in enumerate(clips, 1):
                print(f"\n[{i}/{len(clips)}] {clip['name']}")
                print(f"URL: {clip['url'][:60]}...")
                
                filename = f"top{i:02d}_{clip['name']}"
                # Sanitize filename
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = filename[:100]  # Limit length
                
                video_path = self.downloader.download(clip['url'], filename)
                
                if video_path:
                    clip['video_path'] = video_path
                    print(f"✅ Downloaded")
                else:
                    print(f"❌ Download failed")
                    clip['video_path'] = None
        else:
            print("\n⏭️  Skipping download (using existing files)")
            # Find existing files
            clips_dir = Path("data/training/goat_clips")
            for i, clip in enumerate(clips, 1):
                # Try to match by name or index
                matches = list(clips_dir.glob(f"top{i:02d}_*.mp4"))
                if not matches:
                    matches = list(clips_dir.glob(f"*{clip['name'][:20]}*.mp4"))
                
                if matches:
                    clip['video_path'] = str(matches[0])
                    print(f"  {i}. Found: {matches[0].name}")
                else:
                    clip['video_path'] = None
                    print(f"  {i}. ❌ Not found: {clip['name']}")
        
        # Step 4: Analyze videos
        print("\n" + "=" * 60)
        print("STEP 4: Analyzing Videos")
        print("=" * 60 + "\n")
        
        training_data = []
        successful = 0
        failed = 0
        
        for i, clip in enumerate(clips, 1):
            if not clip.get('video_path'):
                logger.warning(f"Skipping {clip['name']}: No video file")
                failed += 1
                continue
            
            print(f"\n{'='*60}")
            print(f"[{i}/{len(clips)}] {clip['name']}")
            print(f"{'='*60}")
            
            try:
                result = self._analyze_clip(clip)
                if result:
                    training_data.append(result)
                    successful += 1
                    print("✅ Success")
                else:
                    failed += 1
                
            except Exception as e:
                logger.error(f"❌ Failed: {e}")
                failed += 1
                continue
        
        # Step 5: Save training data
        print("\n" + "=" * 60)
        print("STEP 5: Saving Training Data")
        print("=" * 60 + "\n")
        
        output_file = Path("data/training/goat_training_data.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(training_data, f, indent=2, default=str)
        
        print(f"✅ Saved: {output_file}")
        print(f"📊 Successful: {successful}/{len(clips)}")
        print(f"❌ Failed: {failed}/{len(clips)}")
        
        # Summary
        if training_data:
            self._print_summary(training_data)
        
        return training_data
    
    def _select_top_clips(self, clips: List[Dict], top_n: int, sort_by: str) -> List[Dict]:
        """Select top N clips based on sorting criteria"""
        
        if sort_by == 'order':
            # Use sheet order
            return clips[:top_n]
        
        elif sort_by == 'views':
            # Sort by views (highest first)
            clips_with_views = [c for c in clips if c.get('views', 0) > 0]
            clips_without = [c for c in clips if c.get('views', 0) == 0]
            
            sorted_clips = sorted(clips_with_views, key=lambda x: x.get('views', 0), reverse=True)
            # Add clips without views at end
            sorted_clips.extend(clips_without)
            
            return sorted_clips[:top_n]
        
        elif sort_by == 'watch_time':
            # Sort by watch time percentage
            clips_with_wt = [c for c in clips if c.get('watch_time_percentage', 0) > 0]
            clips_without = [c for c in clips if c.get('watch_time_percentage', 0) == 0]
            
            sorted_clips = sorted(clips_with_wt, key=lambda x: x.get('watch_time_percentage', 0), reverse=True)
            sorted_clips.extend(clips_without)
            
            return sorted_clips[:top_n]
        
        elif sort_by == 'engagement':
            # Sort by engagement rate
            clips_with_eng = [c for c in clips if c.get('engagement_rate', 0) > 0]
            clips_without = [c for c in clips if c.get('engagement_rate', 0) == 0]
            
            sorted_clips = sorted(clips_with_eng, key=lambda x: x.get('engagement_rate', 0), reverse=True)
            sorted_clips.extend(clips_without)
            
            return sorted_clips[:top_n]
        
        else:
            # Default: sheet order
            return clips[:top_n]
    
    def _analyze_clip(self, clip: Dict) -> Dict:
        """Analyze single clip"""
        
        video_path = clip['video_path']
        
        # Video Processor
        video_proc = VideoProcessor(video_path)
        
        print(f"  📹 Duration: {video_proc.metadata['duration']:.1f}s")
        print(f"  📐 Resolution: {video_proc.metadata['width']}x{video_proc.metadata['height']}")
        
        # Extract Audio
        audio_path = str(video_path).replace('.mp4', '_audio.wav')
        video_proc.extract_audio(audio_path)
        
        # Transcribe
        print("  📝 Transcribing...")
        transcript = self.transcriber.transcribe(audio_path, language="de")
        print(f"     Segments: {len(transcript['segments'])}")
        
        # Extract Features
        print("  🧠 Extracting features...")
        full_text = transcript['text']
        duration = video_proc.metadata['duration']
        is_hook = duration <= 10
        
        features = self.feature_extractor.extract_clip_features(
            transcript_segment=full_text,
            audio_path=audio_path,
            start_time=0,
            duration=duration,
            is_hook=is_hook
        )
        
        # Cleanup
        Path(audio_path).unlink(missing_ok=True)
        
        # Compile result
        result = {
            'clip_name': clip['name'],
            'url': clip['url'],
            'features': features,
            'performance': {
                'views': clip.get('views', 0),
                'watch_time_percentage': clip.get('watch_time_percentage', 0),
                'engagement_rate': clip.get('engagement_rate', 0),
            },
            'metadata': {
                'duration': duration,
                'platform': clip.get('platform', 'unknown'),
                'notes': clip.get('notes', ''),
                'resolution': f"{video_proc.metadata['width']}x{video_proc.metadata['height']}",
            },
            'text_preview': full_text[:300],
            'full_transcript': full_text
        }
        
        return result
    
    def _print_summary(self, training_data: List[Dict]):
        """Print training summary"""
        
        print("\n" + "=" * 60)
        print("📊 TRAINING DATA SUMMARY")
        print("=" * 60)
        
        if not training_data:
            print("No data to summarize")
            return
        
        # Stats
        total_views = sum(d['performance']['views'] for d in training_data)
        avg_watch_time = sum(d['performance']['watch_time_percentage'] for d in training_data) / len(training_data)
        avg_duration = sum(d['metadata']['duration'] for d in training_data) / len(training_data)
        
        print(f"\n📈 Performance:")
        print(f"  Clips Analyzed: {len(training_data)}")
        print(f"  Total Views: {total_views:,.0f}")
        print(f"  Avg Watch Time: {avg_watch_time:.1f}%")
        print(f"  Avg Duration: {avg_duration:.1f}s")
        
        # Feature averages
        all_features = [d['features'] for d in training_data]
        
        print(f"\n🎯 Feature Averages:")
        print(f"  Word Count: {sum(f['word_count'] for f in all_features) / len(all_features):.1f}")
        print(f"  Viral Keywords: {sum(f['has_viral_keywords'] for f in all_features) / len(all_features):.1f}")
        print(f"  Questions: {sum(f['question_count'] for f in all_features) / len(all_features):.1f}")
        print(f"  Exclamations: {sum(f['exclamation_count'] for f in all_features) / len(all_features):.1f}")
        print(f"  Story Markers: {sum(f['has_story_markers'] for f in all_features) / len(all_features):.1f}")
        print(f"  Emotion Words: {sum(f['emotion_word_count'] for f in all_features) / len(all_features):.1f}")
        print(f"  Audio Energy: {sum(f['avg_energy'] for f in all_features) / len(all_features):.4f}")
        
        # Top performers
        sorted_by_views = sorted(training_data, key=lambda x: x['performance']['views'], reverse=True)
        
        print(f"\n🏆 Top 3 Performers by Views:")
        for i, clip in enumerate(sorted_by_views[:3], 1):
            print(f"\n  {i}. {clip['clip_name']}")
            print(f"     Views: {clip['performance']['views']:,.0f}")
            print(f"     Watch Time: {clip['performance']['watch_time_percentage']:.1f}%")
            print(f"     Duration: {clip['metadata']['duration']:.1f}s")
            print(f"     Preview: {clip['text_preview'][:80]}...")

def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Train on GOAT clips from Google Sheets')
    parser.add_argument('--top', type=int, default=10, help='Number of top clips (default: 10)')
    parser.add_argument('--skip-download', action='store_true', help='Skip download, use existing files')
    parser.add_argument('--sort', choices=['views', 'watch_time', 'engagement', 'order'], 
                       default='views', help='Sort criteria (default: views)')
    parser.add_argument('--all', action='store_true', help='Process ALL clips (ignores --top)')
    
    args = parser.parse_args()
    
    # Determine top_n
    if args.all:
        top_n = 999  # Large number to get all
        print("⚠️  Processing ALL clips from sheet!")
    else:
        top_n = args.top
    
    # Run pipeline
    pipeline = GOATTrainingPipeline()
    
    training_data = pipeline.run(
        top_n=top_n,
        skip_download=args.skip_download,
        sort_by=args.sort
    )
    
    if training_data:
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE!")
        print("="*60)
        print(f"\n📁 Training data saved to:")
        print(f"   data/training/goat_training_data.json")
        print(f"\n📚 Next step: Train custom ML model")
        print(f"   python train_custom_model.py")
    else:
        print("\n❌ No training data generated")

if __name__ == "__main__":
    main()
