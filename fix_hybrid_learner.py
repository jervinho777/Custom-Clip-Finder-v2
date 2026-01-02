#!/usr/bin/env python3
"""
Fix hybrid_learner.py to handle new model format
"""

import re
from pathlib import Path

def fix_hybrid_learner():
    file_path = Path("backend/ai/hybrid_learner.py")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find and replace the problematic line
    old_pattern = r"Latest Training: \{latest\['training_samples'\]\} clips, R²=\{latest\['r2_score'\]:.3f\}"
    new_pattern = "Latest Training: {latest['training_samples']} clips, R²={latest.get('test_r2_score', latest.get('r2_score', 0)):.3f}"
    
    content = re.sub(old_pattern, new_pattern, content)
    
    # Also fix any other r2_score references
    # Replace direct access with .get()
    content = content.replace(
        "latest['r2_score']",
        "latest.get('test_r2_score', latest.get('r2_score', 0))"
    )
    
    content = content.replace(
        "entry['r2_score']",
        "entry.get('test_r2_score', entry.get('r2_score', 0))"
    )
    
    # Save
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ hybrid_learner.py fixed!")

if __name__ == "__main__":
    fix_hybrid_learner()
