#!/usr/bin/env python3
"""
RESTORE TRAINING DATA
Find and restore original 973 clips
"""

import json
import shutil
from pathlib import Path

def find_and_restore_data():
    """Find backup or original data and restore it"""
    
    print("="*70)
    print("🔧 RESTORING TRAINING DATA")
    print("="*70)
    
    training_file = Path("data/training/goat_training_data.json")
    
    # Check for backups
    possible_backups = [
        Path("data/training/goat_training_data_old_features_backup.json"),
        Path("data/training/goat_training_data_backup.json"),
        Path("data/training/original_goat_data.json"),
        Path("data/training/goat_clips.json"),
    ]
    
    print("\n🔍 Searching for backups...")
    
    for backup in possible_backups:
        if backup.exists():
            size = backup.stat().st_size / 1024
            print(f"\n✅ Found: {backup.name} ({size:.1f} KB)")
            
            # Load and check
            with open(backup, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                print(f"   Contains {len(data)} clips")
                
                # Show sample
                sample = data[0]
                print(f"\n   Sample keys: {list(sample.keys())}")
                
                # Restore?
                response = input(f"\n   Restore from this backup? (y/n): ")
                if response.lower() == 'y':
                    shutil.copy(backup, training_file)
                    print(f"\n✅ Restored {len(data)} clips to {training_file}")
                    return len(data)
            else:
                print(f"   ⚠️  File is empty or invalid")
    
    # Check all JSON files in training directory
    print("\n\n🔍 Checking all JSON files in data/training/...")
    training_dir = Path("data/training")
    
    if training_dir.exists():
        json_files = list(training_dir.glob("*.json"))
        print(f"   Found {len(json_files)} JSON files:")
        
        valid_files = []
        
        for f in json_files:
            size = f.stat().st_size / 1024
            print(f"\n   {f.name} ({size:.1f} KB)")
            
            try:
                with open(f, 'r') as file:
                    data = json.load(file)
                
                if isinstance(data, list):
                    count = len(data)
                    if count > 0:
                        print(f"     ✅ {count} items")
                        valid_files.append((f, count, data))
                    else:
                        print(f"     ⚠️  Empty list")
                elif isinstance(data, dict):
                    print(f"     📋 Dict with keys: {list(data.keys())[:5]}")
                    if 'clips' in data or 'videos' in data:
                        clips = data.get('clips') or data.get('videos')
                        if isinstance(clips, list):
                            print(f"     ✅ Contains {len(clips)} clips")
                            valid_files.append((f, len(clips), clips))
                else:
                    print(f"     ⚠️  Unknown format")
            
            except Exception as e:
                print(f"     ❌ Error: {e}")
        
        # Ask user to pick
        if valid_files:
            print(f"\n\n📋 Valid files found:")
            for i, (f, count, _) in enumerate(valid_files, 1):
                print(f"{i}. {f.name} - {count} clips")
            
            choice = input(f"\nPick file to restore (1-{len(valid_files)}) or 0 to cancel: ")
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(valid_files):
                    chosen_file, count, clips = valid_files[idx]
                    
                    # Save as training data
                    with open(training_file, 'w') as f:
                        json.dump(clips, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n✅ Restored {count} clips from {chosen_file.name}")
                    return count
            except ValueError:
                pass
    
    print("\n❌ No valid data found!")
    print("\n💡 Options:")
    print("   1. Check if you have original GOAT clips data elsewhere")
    print("   2. Re-run data extraction from videos")
    print("   3. Use analyze_973_clips.py to generate new data")
    
    return 0

if __name__ == "__main__":
    restored = find_and_restore_data()
    
    if restored > 0:
        print("\n" + "="*70)
        print("✅ READY TO TRAIN!")
        print("="*70)
        print(f"\nRun: python train_ultimate_system.py")
