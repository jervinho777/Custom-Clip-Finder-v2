#!/usr/bin/env python3
"""
🧪 TEST: Export System für v2

Tests the export functions with v2 structure.
"""

import json
import sys
from pathlib import Path
from create_clips_v2 import CreateClipsV2


def create_test_result():
    """Create test result structure matching v2 output"""
    
    return {
        "analysis": {
            "total_moments_found": 2,
            "clips_restructured": 2,
            "total_versions": 4
        },
        "clips": [
            {
                "clip_id": "clip_01",
                "original_moment": {
                    "id": 1,
                    "start": 0.0,
                    "end": 15.1,
                    "topic": "Lebensverändernder Moment",
                    "strength": "high",
                    "reason": "Starker emotionaler Hook"
                },
                "versions": [
                    {
                        "version_id": "clip_01_original",
                        "version_name": "Original Structure",
                        "structure": {
                            "segments": [
                                {
                                    "role": "hook",
                                    "start": 5.0,
                                    "end": 8.0,
                                    "text": "Warum der größte Fehler bei Social Media ist",
                                    "reason": "Stärkster emotionaler Moment"
                                },
                                {
                                    "role": "context",
                                    "start": 0.0,
                                    "end": 5.0,
                                    "text": "Die meisten Menschen denken",
                                    "reason": "Setup für Hook"
                                },
                                {
                                    "role": "content",
                                    "start": 8.0,
                                    "end": 12.0,
                                    "text": "Aber die Wahrheit ist anders",
                                    "reason": "Main content"
                                },
                                {
                                    "role": "payoff",
                                    "start": 12.0,
                                    "end": 15.0,
                                    "text": "Wenn du das verstehst",
                                    "reason": "Satisfying conclusion"
                                }
                            ],
                            "total_duration": 15.0,
                            "restructured": True,
                            "strategy": "hook_from_middle"
                        },
                        "scores": {
                            "watchtime_potential": 85,
                            "virality_potential": 78,
                            "hook_strength": 9
                        },
                        "reasoning": {
                            "hook_choice": "Sentence at 5s has strongest emotional impact",
                            "reorder_strategy": "Move climax to front, add context, then payoff",
                            "watch_time_optimization": "Start strong, maintain tension"
                        }
                    },
                    {
                        "version_id": "clip_01_A",
                        "version_name": "Alternative Hook",
                        "structure": {
                            "segments": [
                                {
                                    "role": "hook",
                                    "start": 8.0,
                                    "end": 11.0,
                                    "text": "Aber die Wahrheit ist anders",
                                    "reason": "Alternative strong moment"
                                },
                                {
                                    "role": "content",
                                    "start": 0.0,
                                    "end": 8.0,
                                    "text": "Die meisten Menschen denken",
                                    "reason": "Context before hook"
                                },
                                {
                                    "role": "payoff",
                                    "start": 11.0,
                                    "end": 15.0,
                                    "text": "Wenn du das verstehst",
                                    "reason": "Conclusion"
                                }
                            ],
                            "total_duration": 15.0,
                            "restructured": True,
                            "strategy": "alternative_hook"
                        },
                        "scores": {
                            "watchtime_potential": 82,
                            "virality_potential": 75
                        },
                        "why_different": "Uses different hook from middle of moment"
                    }
                ],
                "best_version": "clip_01_original"
            },
            {
                "clip_id": "clip_02",
                "original_moment": {
                    "id": 2,
                    "start": 20.9,
                    "end": 52.1,
                    "topic": "Kreative Demenz bei Erwachsenen",
                    "strength": "high",
                    "reason": "Provokanter Begriff"
                },
                "versions": [
                    {
                        "version_id": "clip_02_original",
                        "version_name": "Original Structure",
                        "structure": {
                            "segments": [
                                {
                                    "role": "hook",
                                    "start": 25.0,
                                    "end": 30.0,
                                    "text": "Kreative Demenz bei Erwachsenen",
                                    "reason": "Provokanter Begriff"
                                },
                                {
                                    "role": "content",
                                    "start": 20.9,
                                    "end": 25.0,
                                    "text": "Setup",
                                    "reason": "Context"
                                },
                                {
                                    "role": "payoff",
                                    "start": 30.0,
                                    "end": 35.0,
                                    "text": "Conclusion",
                                    "reason": "Payoff"
                                }
                            ],
                            "total_duration": 14.1,
                            "restructured": True,
                            "strategy": "hook_from_middle"
                        },
                        "scores": {
                            "watchtime_potential": 88,
                            "virality_potential": 82,
                            "hook_strength": 9
                        }
                    }
                ],
                "best_version": "clip_02_original"
            }
        ],
        "summary": {
            "total_clips": 2,
            "total_versions": 3,
            "steps_completed": 3
        }
    }


def test_export():
    """Test export system"""
    
    print("="*70)
    print("🧪 TEST: Export System v2")
    print("="*70)
    
    # Initialize
    creator = CreateClipsV2()
    
    # Create test result
    test_result = create_test_result()
    
    print(f"\n📊 Test Data:")
    print(f"   Clips: {len(test_result['clips'])}")
    print(f"   Total versions: {test_result['summary']['total_versions']}")
    
    # Find test video
    video_candidates = [
        "data/uploads/test.mp4",
        "data/uploads/video_20251216_213141.m4a"
    ]
    
    video_path = None
    for candidate in video_candidates:
        path = Path(candidate)
        if path.exists():
            video_path = candidate
            print(f"\n✅ Found test video: {candidate}")
            break
    
    if not video_path:
        print("\n⚠️  No test video found - export will be simulated")
        print("   Testing export logic only (no actual MP4/XML generation)")
        
        # Test export logic without actual file operations
        clips = test_result.get('clips', [])
        total_versions = sum(len(c.get('versions', [])) for c in clips)
        
        print(f"\n📦 Export Simulation:")
        print(f"   • Would export {len(clips)} clips")
        print(f"   • Would export {total_versions} versions")
        print(f"   • Each version would get: MP4 + XML + Info JSON")
        
        # Test _export_info logic
        print(f"\n📝 Testing _export_info()...")
        for clip_data in clips[:1]:  # Test first clip only
            for version in clip_data.get('versions', [])[:1]:  # First version only
                # Create temp directory
                temp_dir = Path("output/test_export_temp")
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                creator._export_info(clip_data, version, temp_dir, version['version_id'])
                
                # Check if info file was created
                info_file = temp_dir / f"{version['version_id']}_info.json"
                if info_file.exists():
                    with open(info_file, 'r') as f:
                        info_data = json.load(f)
                    
                    print(f"   ✅ Info file created")
                    print(f"      Clip ID: {info_data.get('clip_id')}")
                    print(f"      Version ID: {info_data.get('version_id')}")
                    print(f"      Original Moment: {info_data.get('original_moment', {}).get('topic', 'N/A')}")
                    print(f"      Structure segments: {len(info_data.get('structure', {}).get('segments', []))}")
                    print(f"      Reasoning: {bool(info_data.get('reasoning'))}")
                    print(f"      Scores: WT={info_data.get('scores', {}).get('watchtime_potential', 0)}")
                    
                    # Cleanup
                    info_file.unlink()
        
        print(f"\n✅ Export logic test complete!")
        return True
    
    # Real export test
    print(f"\n{'='*70}")
    print("📦 RUNNING EXPORT")
    print("-" * 70)
    
    try:
        export_dir = creator.export_clips(test_result, video_path)
        
        if export_dir:
            print(f"\n✅ Export successful!")
            print(f"   Output directory: {export_dir}")
            
            # Check exported files
            exported_files = list(export_dir.rglob("*"))
            mp4_files = [f for f in exported_files if f.suffix == '.mp4']
            xml_files = [f for f in exported_files if f.suffix == '.xml']
            json_files = [f for f in exported_files if f.suffix == '.json' and 'info' in f.name]
            
            print(f"\n📊 Exported Files:")
            print(f"   • MP4 files: {len(mp4_files)}")
            print(f"   • XML files: {len(xml_files)}")
            print(f"   • Info JSON files: {len(json_files)}")
            
            # Show sample info file
            if json_files:
                sample_info = json_files[0]
                print(f"\n📄 Sample Info File: {sample_info.name}")
                with open(sample_info, 'r') as f:
                    info = json.load(f)
                
                print(f"   Clip ID: {info.get('clip_id')}")
                print(f"   Version: {info.get('version_id')}")
                print(f"   Original Moment: {info.get('original_moment', {}).get('topic', 'N/A')[:50]}")
                print(f"   Structure segments: {len(info.get('structure', {}).get('segments', []))}")
                print(f"   Restructured: {info.get('metadata', {}).get('restructured', False)}")
                print(f"   Strategy: {info.get('metadata', {}).get('strategy', 'unknown')}")
            
            return True
        else:
            print("❌ Export returned None")
            return False
    
    except Exception as e:
        print(f"❌ Export error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_export()
    sys.exit(0 if success else 1)

