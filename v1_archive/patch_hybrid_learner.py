#!/usr/bin/env python3
"""
Patch hybrid_learner.py to handle missing keys
"""

from pathlib import Path

def patch_file():
    file_path = Path("backend/ai/hybrid_learner.py")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find and fix the problematic lines
    fixed_lines = []
    for i, line in enumerate(lines):
        # Fix r2_score references
        if "latest['r2_score']" in line or "entry['r2_score']" in line:
            line = line.replace(
                "['r2_score']",
                ".get('test_r2_score', .get('r2_score', 0))"
            )
        
        # Fix top_features reference
        if "latest['top_features']" in line:
            line = line.replace(
                "latest['top_features']",
                "latest.get('top_features', {})"
            )
        
        if "entry['top_features']" in line:
            line = line.replace(
                "entry['top_features']",
                "entry.get('top_features', {})"
            )
        
        fixed_lines.append(line)
    
    # Save
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ hybrid_learner.py patched!")

if __name__ == "__main__":
    patch_file()
