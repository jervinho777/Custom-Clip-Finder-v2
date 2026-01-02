#!/usr/bin/env python3
"""
🗂️ CLEANUP & ORGANIZE PROJECT

Moves old/unused scripts to Archiv folder
Creates clean project structure
"""

from pathlib import Path
import shutil

def cleanup_project():
    """Organize project files"""
    
    print("="*70)
    print("🗂️ ORGANIZING PROJECT STRUCTURE")
    print("="*70)
    
    # Create Archiv folder
    archiv = Path("Archiv")
    archiv.mkdir(exist_ok=True)
    
    # Files to archive (old versions, test files, etc.)
    files_to_archive = [
        # Old converter versions
        "convert_goat_csv.py",
        "convert_goat_csv_v2.py",
        "convert_goat_csv_v3.py",
        
        # Old training versions
        "train_ultimate_system.py",
        "train_ultimate_system_fixed.py",
        "train_improved_v2.py",
        "train_ai_powered_v3.py",
        
        # Old analyzer versions
        "ultimate_analyzer_v4.py",
        "complete_system_v5.py",
        "clip_extractor_v1.py",
        
        # Debug/test scripts
        "debug_mp4_matching.py",
        "check_transcripts.py",
        "check_env.py",
        "find_test_files.py",
        "find_any_data.py",
        "find_original_data.py",
        "test_extraction.py",
        "create_test_dataset.py",
        
        # Old analysis files
        "analyze_973_clips.py",
        "demo_natural_clips.py",
    ]
    
    archived = []
    not_found = []
    
    for filename in files_to_archive:
        source = Path(filename)
        if source.exists():
            dest = archiv / filename
            shutil.move(str(source), str(dest))
            archived.append(filename)
            print(f"   📦 Archived: {filename}")
        else:
            not_found.append(filename)
    
    print(f"\n✅ Archived {len(archived)} files to /Archiv")
    
    # Show current structure
    print(f"\n📁 CLEAN PROJECT STRUCTURE:")
    print("="*70)
    
    print("""
custom-clip-finder/
├── 📊 WORKFLOW 1: ANALYZE & LEARN
│   └── analyze_and_learn.py      ← Train/Update ML + AI patterns
│
├── 🎬 WORKFLOW 2: CREATE CLIPS  
│   └── create_clips.py           ← Extract clips from new videos
│
├── data/
│   ├── training/
│   │   ├── goat_clips.csv        ← Source performance data
│   │   ├── goat_clips/           ← 973 MP4 training videos
│   │   └── goat_training_data.json
│   ├── cache/
│   │   └── transcripts/          ← Cached transcripts
│   └── learned_patterns.json     ← AI learned patterns (THE BRAIN)
│
├── output/
│   └── clips/                    ← Exported clips
│
├── Archiv/                       ← Old scripts (for reference)
│
└── .env                          ← API keys
""")
    
    return archived

if __name__ == "__main__":
    cleanup_project()
    
    print("\n" + "="*70)
    print("🚀 NEXT: Run the new streamlined scripts")
    print("="*70)
    print("\n1. To analyze/learn: python analyze_and_learn.py")
    print("2. To create clips:  python create_clips.py")
