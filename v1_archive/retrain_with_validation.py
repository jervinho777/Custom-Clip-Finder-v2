#!/usr/bin/env python3
"""
Re-train model with proper validation split
Fixes R²=1.0 overfitting issue
"""

import json
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score

def retrain_with_validation():
    # Load training data
    training_file = Path("data/training/goat_training_data.json")
    with open(training_file, 'r') as f:
        clips = json.load(f)
    
    print(f"📊 Loaded {len(clips)} clips")
    
    # Prepare data
    feature_names = [
        'pitch_variance', 'spectral_centroid_var', 'avg_energy', 
        'max_energy', 'person_mentions', 'question_marks', 
        'duration', 'char_count', 'word_count', 'tempo'
    ]
    
    X = []
    y = []
    
    for clip in clips:
        features = clip.get('features', {})
        performance = clip.get('performance', {})
        
        if not features or not performance:
            continue
        
        # Extract features
        feature_vector = [features.get(f, 0) for f in feature_names]
        target = performance.get('engagement_rate', 0)
        
        X.append(feature_vector)
        y.append(target)
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"✅ Prepared {len(X)} samples")
    
    # Train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n📊 SPLIT:")
    print(f"   Training: {len(X_train)} samples")
    print(f"   Testing: {len(X_test)} samples")
    
    # Train model
    print(f"\n🤖 Training RandomForest...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,  # Limit depth to prevent overfitting
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"\n📈 SCORES:")
    print(f"   Training R²: {train_score:.4f}")
    print(f"   Testing R²: {test_score:.4f}")
    
    if test_score < 0.7:
        print(f"\n⚠️  Test score low - model may need more data or different features")
    elif train_score - test_score > 0.1:
        print(f"\n⚠️  Gap between train/test = overfitting")
    else:
        print(f"\n✅ Good generalization!")
    
    # Cross-validation
    print(f"\n🔄 5-Fold Cross-Validation:")
    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"   CV Scores: {cv_scores}")
    print(f"   Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    feature_importance = dict(zip(feature_names, model.feature_importances_))
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n🎯 FEATURE IMPORTANCE:")
    for feat, imp in sorted_features:
        print(f"   {feat:30s} {imp:.4f} ({imp*100:.1f}%)")
    
    # Save model
    model_data = {
        'model': model,
        'feature_names': feature_names,
        'version': 2,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'train_r2_score': train_score,
        'test_r2_score': test_score,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'feature_importance': feature_importance,
        'trained_at': datetime.now().isoformat()
    }
    
    model_file = Path("data/models/custom_virality_model.pkl")
    joblib.dump(model_data, model_file)
    
    print(f"\n✅ Model v2 saved: {model_file}")
    
    # Update history
    history_file = Path("data/logs/training_history.json")
    history = []
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    history.append({
        'version': 2,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'train_r2_score': train_score,
        'test_r2_score': test_score,
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'timestamp': datetime.now().isoformat()
    })
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"✅ History updated")
    
    return model_data

if __name__ == "__main__":
    print("="*70)
    print("🔧 RE-TRAINING WITH VALIDATION SPLIT")
    print("="*70)
    print()
    
    retrain_with_validation()
    
    print("\n" + "="*70)
    print("✅ COMPLETE - Model now properly validated!")
    print("="*70)

