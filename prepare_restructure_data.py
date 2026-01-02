#!/usr/bin/env python3
"""
Smart Restructure Data Prep - Auto-matches longforms with clips
Scans a folder of mixed videos, transcribes all, finds which clips
came from which longforms using SMART SIMILARITY MATCHING (not just duration)

IMPROVED: Now matches based on transcript similarity, not just duration!
- Handles edge cases like 10-min "shortform" that's actually a clip
- Matches ALL pairs by similarity
- Shorter video = clip, longer video = longform
"""

import asyncio
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent))

from create_clips_v4_integrated import CreateClipsV4Integrated


class SmartRestructurePrep:
    """Auto-detect and match longforms with clips"""
    
    def __init__(self):
        self.examples_dir = Path("data/restructure_examples")
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        self.v4 = CreateClipsV4Integrated()
    
    async def scan_and_prepare(
        self,
        source_folder: str,
        min_longform_duration: float = 300.0,  # 5 min
        max_clip_duration: float = 120.0  # 2 min
    ):
        """
        Scan folder, transcribe all videos, auto-match clips to longforms
        """
        
        source_path = Path(source_folder)
        
        if not source_path.exists():
            print(f"❌ Folder not found: {source_folder}")
            return
        
        print(f"\n{'='*70}")
        print(f"🔍 SCANNING FOLDER")
        print(f"{'='*70}")
        print(f"\n   Path: {source_path}")
        
        # Find all MP4 files
        video_files = list(source_path.glob("*.mp4")) + list(source_path.glob("*.MP4"))
        
        print(f"\n   Found {len(video_files)} videos")
        
        if not video_files:
            print(f"\n❌ No MP4 files found!")
            return
        
        # Transcribe all videos
        print(f"\n{'='*70}")
        print(f"📝 TRANSCRIBING ALL VIDEOS")
        print(f"{'='*70}")
        
        transcripts = []
        
        for i, video_file in enumerate(video_files, 1):
            print(f"\n[{i}/{len(video_files)}] {video_file.name}")
            
            # Check if transcript already exists
            cache_name = video_file.stem + "_transcript.json"
            cache_path = Path("data/cache/transcripts") / cache_name
            
            if cache_path.exists():
                print(f"   ✅ Loading cached transcript...")
                with open(cache_path) as f:
                    data = json.load(f)
                    segments = data['segments']
            else:
                print(f"   🎙️  Transcribing (may take 3-7 min)...")
                segments = await self.v4._transcribe_with_assemblyai(video_file)
                
                if not segments:
                    print(f"   ❌ Transcription failed, skipping...")
                    continue
                
                # Cache it
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_path, 'w') as f:
                    json.dump({
                        'video_path': str(video_file),
                        'segments': segments,
                        'service': 'assemblyai'
                    }, f, indent=2)
                print(f"   ✅ Cached transcript")
            
            # Calculate duration
            duration = segments[-1]['end'] if segments else 0
            
            # Store ALL videos with metadata (classification is just a hint, not used for matching!)
            video_data = {
                'file': video_file,
                'name': video_file.name,
                'transcript_path': cache_path,
                'segments': segments,
                'duration': duration,
                'segment_count': len(segments),
                # Just a hint, not used for matching!
                'likely_type': 'clip' if duration < min_longform_duration else 'longform'
            }
            
            transcripts.append(video_data)
            
            print(f"   ✅ {len(segments)} segments, {duration:.1f}s → {video_data['likely_type'].upper()}")
        
        if len(transcripts) < 2:
            print(f"\n❌ Need at least 2 videos to match!")
            return
        
        # Match ALL pairs by similarity (not pre-classified groups)
        print(f"\n{'='*70}")
        print(f"🔗 SMART MATCHING (Similarity-based)")
        print(f"{'='*70}")
        print(f"\n   Comparing ALL {len(transcripts)} videos...")
        print(f"   Not limited by duration classification!")
        
        matches = []
        
        for i, video_a in enumerate(transcripts):
            for j, video_b in enumerate(transcripts):
                # Skip same video and duplicates (only check each pair once)
                if i >= j:
                    continue
                
                # Calculate similarity between ANY two videos
                similarity_result = self._calculate_similarity(
                    video_a['segments'],
                    video_b['segments']
                )
                
                if not similarity_result:
                    continue
                
                similarity = similarity_result['similarity']
                matched_segs = similarity_result['matched_count']
                
                # Match if similarity > 40% (lower threshold for edge cases)
                if similarity > 0.40:
                    # Determine which is clip/longform by duration
                    # Shorter video = clip, longer video = longform
                    if video_a['duration'] < video_b['duration']:
                        clip = video_a
                        longform = video_b
                    else:
                        clip = video_b
                        longform = video_a
                    
                    matches.append({
                        'clip': clip,
                        'longform': longform,
                        'similarity': similarity,
                        'matched_segments': matched_segs
                    })
                    
                    print(f"\n   ✅ MATCH FOUND:")
                    print(f"      Clip: {clip['name']}")
                    print(f"      Longform: {longform['name']}")
                    print(f"      Similarity: {similarity:.0%}")
                    print(f"      Matched: {matched_segs}/{clip['segment_count']} segments")
                    
                    # Flag edge cases where "longform by duration" is actually a clip
                    if clip['likely_type'] == 'longform':
                        print(f"      💡 Edge case: Clip classified as longform by duration!")
                        print(f"         (Duration: {clip['duration']:.1f}s > {min_longform_duration:.0f}s threshold)")
        
        if not matches:
            print(f"\n❌ No matches found!")
            print(f"\n💡 This could mean:")
            print(f"   - Clips are from different videos not in folder")
            print(f"   - Transcription quality too low")
            print(f"   - Need to adjust matching threshold")
            return
        
        # Create examples
        print(f"\n{'='*70}")
        print(f"📦 CREATING EXAMPLES")
        print(f"{'='*70}")
        
        # Get max existing example number
        existing = list(self.examples_dir.glob("example_*"))
        if existing:
            try:
                next_num = max([int(d.name.split('_')[1]) for d in existing if d.is_dir()]) + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1
        
        print(f"\n   Starting from example_{next_num:03d}")
        
        created_examples = []
        
        for match in matches:
            # Check if THIS SPECIFIC MATCH already exists
            if self._match_already_exists(match):
                print(f"\n   ⚠️  Match already exists:")
                print(f"      Longform: {match['longform']['name']}")
                print(f"      Clip: {match['clip']['name']}")
                print(f"      Skipping...")
                continue
            
            example_id = f"example_{next_num:03d}"
            
            print(f"\n   Creating {example_id}...")
            
            example = await self._create_example_from_match(
                example_id=example_id,
                match=match
            )
            
            if example:
                created_examples.append(example)
                next_num += 1  # Increment after successful creation
        
        # Summary
        print(f"\n{'='*70}")
        print(f"✅ PREPARATION COMPLETE")
        print(f"{'='*70}")
        print(f"\n   Total examples: {len(created_examples)}")
        
        if len(created_examples) >= 5:
            print(f"\n   🎉 You have {len(created_examples)} examples!")
            print(f"\n   Next step:")
            print(f"   python analyze_restructures_v1.py")
        else:
            print(f"\n   ⚠️  Need {5 - len(created_examples)} more examples")
            print(f"   Add more videos to the folder and run again")
        
        return created_examples
    
    def _calculate_similarity(
        self,
        segments_a: List[Dict],
        segments_b: List[Dict]
    ) -> Dict:
        """
        Calculate similarity between two sets of segments
        
        Uses text matching to find how many segments match
        Returns similarity score and matched count
        """
        
        if not segments_a or not segments_b:
            return None
        
        # Count how many segments_a match segments_b
        matched_count = 0
        total_similarity = 0
        
        for seg_a in segments_a:
            text_a = seg_a.get('text', '').lower()
            words_a = set(text_a.split())
            
            if not words_a:
                continue
            
            # Find best matching segment in segments_b
            best_jaccard = 0
            found_match = False
            
            for seg_b in segments_b:
                text_b = seg_b.get('text', '').lower()
                words_b = set(text_b.split())
                
                if not words_b:
                    continue
                
                # Jaccard similarity
                intersection = len(words_a & words_b)
                union = len(words_a | words_b)
                jaccard = intersection / union if union > 0 else 0
                
                # ALSO check substring match (more lenient for exact clips)
                text_a_clean = ''.join(text_a.split()).lower()
                text_b_clean = ''.join(text_b.split()).lower()
                substring_match = text_a_clean in text_b_clean if len(text_a_clean) > 15 else False
                
                # Match if EITHER good Jaccard OR substring found
                if jaccard > 0.4 or substring_match:
                    found_match = True
                    # Boost similarity for substring matches
                    best_jaccard = max(jaccard, 0.7 if substring_match else 0)
                    break  # Found match for this segment
            
            if found_match:
                matched_count += 1
                total_similarity += best_jaccard
        
        # Calculate overall similarity
        if matched_count > 0:
            avg_similarity = total_similarity / matched_count
            coverage = matched_count / len(segments_a)
            overall_similarity = avg_similarity * coverage
            
            return {
                'similarity': overall_similarity,
                'matched_count': matched_count,
                'coverage': coverage
            }
        
        return None
    
    def _match_already_exists(self, match: Dict) -> bool:
        """Check if this specific longform+clip pair already exists"""
        longform_name = match['longform']['name']
        clip_name = match['clip']['name']
        
        for example_dir in self.examples_dir.glob("example_*"):
            if not example_dir.is_dir():
                continue
            
            metadata_file = example_dir / 'metadata.json'
            if not metadata_file.exists():
                continue
            
            try:
                with open(metadata_file) as f:
                    existing = json.load(f)
                
                # Check if filenames match
                existing_longform = existing.get('longform', {}).get('filename')
                existing_clip = existing.get('viral_clip', {}).get('filename')
                
                if (existing_longform == longform_name and 
                    existing_clip == clip_name):
                    return True
            except (json.JSONDecodeError, KeyError, AttributeError):
                # Skip corrupted metadata files
                continue
        
        return False
    
    async def _create_example_from_match(
        self,
        example_id: str,
        match: Dict
    ) -> Dict:
        """Create example directory from match"""
        
        example_dir = self.examples_dir / example_id
        example_dir.mkdir(exist_ok=True)
        
        longform = match['longform']
        clip = match['clip']
        
        # Copy videos
        longform_dest = example_dir / "longform.mp4"
        clip_dest = example_dir / "viral_clip.mp4"
        
        shutil.copy2(longform['file'], longform_dest)
        shutil.copy2(clip['file'], clip_dest)
        
        # Copy transcripts
        longform_transcript_dest = example_dir / "longform_transcript.json"
        clip_transcript_dest = example_dir / "viral_clip_transcript.json"
        
        shutil.copy2(longform['transcript_path'], longform_transcript_dest)
        shutil.copy2(clip['transcript_path'], clip_transcript_dest)
        
        # Create metadata
        metadata = {
            'example_id': example_id,
            'created_at': datetime.now().isoformat(),
            'source_files': {
                'longform_original': str(longform['file']),
                'clip_original': str(clip['file'])
            },
            'longform': {
                'filename': longform['name'],
                'video': str(longform_dest),
                'transcript': str(longform_transcript_dest),
                'duration': longform['duration'],
                'segments': longform['segment_count']
            },
            'viral_clip': {
                'filename': clip['name'],
                'video': str(clip_dest),
                'transcript': str(clip_transcript_dest),
                'duration': clip['duration'],
                'segments': clip['segment_count'],
                'views': None,  # TODO: Ask user for views
                'vir_score': None
            },
            'match_info': {
                'similarity': match['similarity'],
                'matched_segments': match['matched_segments'],
                'total_clip_segments': len(clip['segments']),
                'was_edge_case': clip['likely_type'] == 'longform'
            },
            'status': 'ready'
        }
        
        metadata_file = example_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n   ✅ Created {example_id}")
        print(f"      Longform: {longform['name']} ({longform['duration']:.1f}s)")
        print(f"      Clip: {clip['name']} ({clip['duration']:.1f}s)")
        print(f"      Similarity: {match['similarity']:.0%}")
        
        # Notify about edge cases
        if clip['likely_type'] == 'longform':
            print(f"      💡 Edge case handled: Clip was >5min but matched by similarity!")
        
        return metadata


async def main():
    """Main entry point"""
    
    prep = SmartRestructurePrep()
    
    # Use the folder you specified
    source_folder = "/Users/jervinquisada/custom-clip-finder/data/training/Longform and Clips"
    
    print(f"\n{'='*70}")
    print(f"🤖 SMART RESTRUCTURE DATA PREP")
    print(f"{'='*70}")
    print(f"\nThis will:")
    print(f"  1. Scan all videos in folder")
    print(f"  2. Transcribe each one (cached if already done)")
    print(f"  3. Match ALL pairs by transcript similarity")
    print(f"  4. Determine clip/longform per pair (shorter=clip, longer=longform)")
    print(f"  5. Create organized training examples")
    print(f"\n💡 NEW: Smart similarity matching handles edge cases!")
    print(f"   (e.g., 10-min 'shortform' that's actually a clip)")
    
    response = input(f"\nReady to scan {source_folder}? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Cancelled.")
        return
    
    # Scan and prepare
    await prep.scan_and_prepare(source_folder)


if __name__ == '__main__':
    asyncio.run(main())
