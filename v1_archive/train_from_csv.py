#!/usr/bin/env python3
"""
CSV Training Pipeline - angepasst für GOAT Sheet
"""

import csv
import json
from pathlib import Path
import logging

from backend.utils.video_downloader import VideoDownloader
from backend.processors.video_processor import VideoProcessor
from backend.processors.transcriber import Transcriber
from backend.processors.feature_extractor import FeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_german_number(value):
    """Parse German number format: 6.400.000 -> 6400000"""
    if not value or not isinstance(value, str):
        return 0
    try:
        value = value.replace('.', '')
        value = value.replace(',', '.')
        return float(value)
    except:
        return 0

def load_clips_from_csv(csv_path: str):
    """Load clips from GOAT CSV"""
    clips = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            url = row.get('URL', '').strip()
            if not url or not url.startswith('http'):
                continue
            
            uploaded = row.get('Hochgeladen?', '').strip().upper()
            if uploaded != 'TRUE':
                continue
            
            clip = {
                'name': row.get('Framework', f'Clip {i}').strip(),
                'url': url,
                'views': parse_german_number(row.get('VIEWS', '0')),
                'likes': parse_german_number(row.get('LIKES', '0')),
                'comments': parse_german_number(row.get('COMMENTS', '0')),
                'shares': parse_german_number(row.get('SHARES', '0')),
                'saves': parse_german_number(row.get('SAVES', '0')),
                'platform': row.get('PLATTFORM', 'unknown').strip().lower(),
                'account': row.get('ACCOUNT', '').strip(),
                'framework': row.get('Framework', '').strip()
            }
            
            if clip['views'] > 0:
                engagement = (clip['likes'] + clip['comments'] + clip['shares'] + clip['saves'])
                clip['engagement_rate'] = (engagement / clip['views']) * 100
            else:
                clip['engagement_rate'] = 0
            
            clips.append(clip)
    
    logger.info(f"Loaded {len(clips)} clips")
    return clips

def main():
    print("🎯 GOAT CLIPS TRAINING PIPELINE\n")
    
    csv_path = Path("data/training/goat_clips.csv")
    
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return
    
    try:
        all_clips = load_clips_from_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    if not all_clips:
        print("No clips found")
        return
    
    all_clips.sort(key=lambda x: x['views'], reverse=True)
    
    print(f"Found {len(all_clips)} clips\n")
    print("Top 20 by views:\n")
    
    for i, clip in enumerate(all_clips[:20], 1):
        print(f"  {i}. {clip['name'][:50]}")
        print(f"     Platform: {clip['platform']} | Account: {clip['account']}")
        print(f"     Views: {clip['views']:,.0f} | Engagement: {clip['engagement_rate']:.2f}%")
        print()
    
    if len(all_clips) > 20:
        print(f"... and {len(all_clips) - 20} more\n")
    
    try:
        num = input(f"How many to analyze? (default: 10): ").strip()
        num = int(num) if num else 10
        num = min(num, len(all_clips))
    except:
        num = 10
    
    clips = all_clips[:num]
    
    print(f"\nWill analyze TOP {len(clips)} clips")
    confirm = input("Continue? (y/n): ")
    if confirm.lower() != 'y':
        return
    
    downloader = VideoDownloader()
    transcriber = Transcriber(model_size="medium")
    feature_extractor = FeatureExtractor()
    
    training_data = []
    successful = 0
    failed = 0
    
    for i, clip in enumerate(clips, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(clips)}] {clip['name']}")
        print(f"{'='*70}")
        print(f"Platform: {clip['platform']} | Views: {clip['views']:,.0f}")
        
        try:
            print(f"\nDownloading...")
            filename = f"top{i:02d}_{clip['account']}_{clip['name']}"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_'))[:100]
            
            video_path = downloader.download(clip['url'], filename)
            
            if not video_path:
                print("Download failed")
                failed += 1
                continue
            
            print(f"Analyzing...")
            video_proc = VideoProcessor(video_path)
            
            audio_path = video_path.replace('.mp4', '_audio.wav')
            video_proc.extract_audio(audio_path)
            
            print(f"Transcribing...")
            transcript = transcriber.transcribe(audio_path, language="de")
            
            print(f"Extracting features...")
            features = feature_extractor.extract_clip_features(
                transcript_segment=transcript['text'],
                audio_path=audio_path,
                start_time=0,
                duration=video_proc.metadata['duration'],
                is_hook=video_proc.metadata['duration'] <= 10
            )
            
            Path(audio_path).unlink(missing_ok=True)
            
            training_data.append({
                'clip_name': clip['name'],
                'url': clip['url'],
                'account': clip['account'],
                'platform': clip['platform'],
                'framework': clip['framework'],
                'features': features,
                'performance': {
                    'views': clip['views'],
                    'likes': clip['likes'],
                    'comments': clip['comments'],
                    'shares': clip['shares'],
                    'saves': clip['saves'],
                    'engagement_rate': clip['engagement_rate']
                },
                'metadata': {
                    'duration': video_proc.metadata['duration']
                },
                'full_transcript': transcript['text']
            })
            
            successful += 1
            print("Success!")
            
        except Exception as e:
            logger.error(f"Failed: {e}")
            failed += 1
    
    output_file = Path("data/training/goat_training_data.json")
    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2, default=str)
    
    print(f"\nSaved: {output_file}")
    print(f"Results: {successful} success / {failed} failed")
    
    if training_data:
        total_views = sum(d['performance']['views'] for d in training_data)
        avg_engagement = sum(d['performance']['engagement_rate'] for d in training_data) / len(training_data)
        
        print(f"\nTotal Views: {total_views:,.0f}")
        print(f"Avg Engagement: {avg_engagement:.2f}%")
    
    print("\nPipeline complete!")

if __name__ == "__main__":
    main()
