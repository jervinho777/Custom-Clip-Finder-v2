#!/usr/bin/env python3
"""
Train Custom Virality Model on GOAT Clips
"""

import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib

def load_training_data():
    """Load GOAT training data"""
    data_file = Path("data/training/goat_training_data.json")
    
    if not data_file.exists():
        print(f"Training data not found: {data_file}")
        return None
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} training samples")
    return data

def prepare_features(training_data):
    """Prepare features for ML training"""
    X = []
    y = []
    feature_names = None
    
    for sample in training_data:
        features = sample['features']
        
        if feature_names is None:
            feature_names = sorted(features.keys())
        
        # Feature vector
        feature_vector = [features[name] for name in feature_names]
        X.append(feature_vector)
        
        # Target: Engagement Rate (beste Metric)
        engagement = sample['performance']['engagement_rate']
        y.append(engagement)
    
    return np.array(X), np.array(y), feature_names

def train_model(X, y, feature_names):
    """Train custom model"""
    print("\nTraining custom virality model...")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train
    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X_scaled, y)
    
    # Feature importance
    importance = dict(zip(feature_names, model.feature_importances_))
    
    print(f"\nModel R² Score: {model.score(X_scaled, y):.3f}")
    
    return model, scaler, importance

def main():
    print("🤖 CUSTOM MODEL TRAINING\n")
    
    # Load data
    training_data = load_training_data()
    if not training_data:
        return
    
    # Show summary
    print("\n📊 Training Data Summary:")
    total_views = sum(d['performance']['views'] for d in training_data)
    avg_eng = sum(d['performance']['engagement_rate'] for d in training_data) / len(training_data)
    
    print(f"  Clips: {len(training_data)}")
    print(f"  Total Views: {total_views:,.0f}")
    print(f"  Avg Engagement: {avg_eng:.2f}%")
    
    # Prepare features
    X, y, feature_names = prepare_features(training_data)
    
    print(f"\n  Features extracted: {len(feature_names)}")
    
    # Train
    model, scaler, importance = train_model(X, y, feature_names)
    
    # Show top features
    print("\n🎯 Top 10 Most Important Features:")
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for i, (feat, imp) in enumerate(sorted_features[:10], 1):
        print(f"  {i}. {feat}: {imp:.4f}")
    
    # Save model
    model_dir = Path("data/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'feature_importance': importance
    }
    
    model_path = model_dir / "custom_virality_model.pkl"
    joblib.dump(model_data, model_path)
    
    print(f"\n✅ Model saved: {model_path}")
    print("\n🎉 Training complete!")
    print("\nNext: Test on new videos with improved weights!")

if __name__ == "__main__":
    main()
