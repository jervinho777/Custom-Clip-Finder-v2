#!/usr/bin/env python3
"""
DEBUG: Check Training Data Structure
"""

import json
from pathlib import Path

def check_training_data():
    """Check what's in the training file"""
    
    print("="*70)
    print("🔍 CHECKING TRAINING DATA")
    print("="*70)
    
    training_file = Path("data/training/goat_training_data.json")
    
    print(f"\n📁 File: {training_file}")
    print(f"   Exists: {training_file.exists()}")
    
    if not training_file.exists():
        print("❌ File not found!")
        print("\n🔍 Checking directory contents:")
        data_dir = Path("data/training")
        if data_dir.exists():
            files = list(data_dir.glob("*.json"))
            print(f"   Found {len(files)} JSON files:")
            for f in files:
                size = f.stat().st_size / 1024
                print(f"   - {f.name} ({size:.1f} KB)")
        return
    
    # Load and analyze
    with open(training_file, 'r') as f:
        data = json.load(f)
    
    print(f"\n📊 Data Type: {type(data)}")
    
    if isinstance(data, list):
        print(f"   Length: {len(data)} items")
        
        if len(data) > 0:
            print(f"\n🔬 First item structure:")
            first = data[0]
            for key in sorted(first.keys()):
                value = first[key]
                if isinstance(value, str):
                    preview = value[:50] + "..." if len(value) > 50 else value
                    print(f"   - {key}: '{preview}'")
                elif isinstance(value, dict):
                    print(f"   - {key}: dict with {len(value)} keys: {list(value.keys())[:5]}")
                elif isinstance(value, list):
                    print(f"   - {key}: list with {len(value)} items")
                else:
                    print(f"   - {key}: {value}")
            
            print(f"\n📝 Sample Content:")
            if 'content' in first:
                content = first['content']
                print(f"   Content: {content[:200]}...")
            if 'transcript' in first:
                transcript = first['transcript']
                print(f"   Transcript type: {type(transcript)}")
                if isinstance(transcript, dict):
                    print(f"   Transcript keys: {list(transcript.keys())}")
    
    elif isinstance(data, dict):
        print(f"   Keys: {list(data.keys())}")
        print(f"\n🔬 Checking each key:")
        for key, value in data.items():
            print(f"   - {key}: {type(value)} with {len(value) if hasattr(value, '__len__') else 'N/A'} items")
    
    else:
        print(f"   Unexpected type: {type(data)}")

if __name__ == "__main__":
    check_training_data()
