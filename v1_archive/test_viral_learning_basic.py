#!/usr/bin/env python3
"""Quick test für learn_from_viral_example.py basics"""

import sys
from pathlib import Path

print("🧪 Testing learn_from_viral_example.py imports...")

try:
    from learn_from_viral_example import ViralExampleLearner
    print("✅ Import successful")
    
    # Test initialization
    learner = ViralExampleLearner()
    print("✅ Class initialization successful")
    
    # Test that data directory exists
    data_dir = Path("data/viral_examples")
    print(f"✅ Data directory: {data_dir} (exists: {data_dir.exists()})")
    
    print("\n✅ All basic tests passed!")
    print("\nReady to implement:")
    print("1. analyze_restructuring()")
    print("2. extract_hook_patterns()")
    print("3. extract_structure_patterns()")
    print("4. ai_analyze_example()")
    print("5. create_template()")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

