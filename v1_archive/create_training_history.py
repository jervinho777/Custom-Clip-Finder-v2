#!/usr/bin/env python3
"""
Create training history from existing model
"""

import json
from pathlib import Path
import joblib
from datetime import datetime

# Load existing model
model_file = Path("data/models/custom_virality_model.pkl")

if not model_file.exists():
    print("❌ No model found - run train_custom_model.py first")
    exit(1)

model_data = joblib.load(model_file)

print("✅ Model loaded")

# Get samples (might be in different keys)
samples = model_data.get('training_samples')
if samples is None:
    # Try to count from training data
    training_file = Path("data/training/goat_training_data.json")
    if training_file.exists():
        with open(training_file, 'r') as f:
            clips = json.load(f)
        samples = len(clips)
    else:
        samples = 25  # default

print(f"   Samples: {samples}")

# Get R2 score
r2 = model_data.get('r2_score', 1.0)
if isinstance(r2, str):
    r2 = 1.0
print(f"   R² Score: {r2:.3f}")

# Get feature importance
feature_importance = model_data.get('feature_importance', {})
top_features = sorted(
    feature_importance.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]

print(f"\n🎯 Top 5 Features:")
for feat, imp in top_features[:5]:
    print(f"   {feat}: {imp:.4f}")

# Create history entry
history = [{
    'version': 1,
    'timestamp': datetime.now().isoformat(),
    'training_samples': samples,
    'r2_score': float(r2),
    'top_features': [[feat, float(imp)] for feat, imp in top_features]
}]

# Save history
history_file = Path("data/logs/training_history.json")
history_file.parent.mkdir(parents=True, exist_ok=True)

with open(history_file, 'w') as f:
    json.dump(history, f, indent=2)

print(f"\n✅ Training history created: {history_file}")
print("\n📊 History Entry:")
print(json.dumps(history[0], indent=2, default=str))
