#!/usr/bin/env python3
"""
Replace _prepare_evolution_summary with robust version
"""

from pathlib import Path
import re

new_method = '''    def _prepare_evolution_summary(self, all_clips, history):
        """Prepare summary of model evolution - ROBUST VERSION"""
        
        summary = "MODEL TRAINING EVOLUTION:\\n\\n"
        
        if not history:
            summary += "No training history available.\\n"
            return summary
        
        # Get latest entry
        latest = history[-1]
        
        # Handle both old and new formats - SAFE
        samples = latest.get('training_samples', 'unknown')
        test_r2 = latest.get('test_r2_score', latest.get('r2_score', 0))
        train_r2 = latest.get('train_r2_score', test_r2)
        
        summary += f"Latest Training: {samples} clips\\n"
        summary += f"  Train R²: {train_r2:.3f}\\n"
        summary += f"  Test R²: {test_r2:.3f}\\n"
        
        # CV scores if available
        if 'cv_mean' in latest:
            summary += f"  CV Mean: {latest['cv_mean']:.3f} ± {latest.get('cv_std', 0):.3f}\\n"
        
        # Show evolution if multiple versions
        if len(history) > 1:
            summary += "\\nVersion History:\\n"
            for i, entry in enumerate(history, 1):
                r2 = entry.get('test_r2_score', entry.get('r2_score', 0))
                s = entry.get('training_samples', 'unknown')
                summary += f"  v{i}: {s} samples, R²={r2:.3f}\\n"
        
        # Top features if available
        top_features = latest.get('top_features', {})
        if top_features:
            summary += "\\nTop Features (latest):\\n"
            sorted_features = sorted(top_features.items(), key=lambda x: x[1], reverse=True)
            for feat, imp in sorted_features[:5]:
                summary += f"  {feat}: {imp:.4f}\\n"
        
        # Dataset summary
        summary += f"\\nDataset Size: {len(all_clips)} clips\\n"
        
        return summary
'''

# Read file
file_path = Path("backend/ai/hybrid_learner.py")
with open(file_path, 'r') as f:
    content = f.read()

# Find and replace the method
pattern = r'def _prepare_evolution_summary\(self, all_clips, history\):.*?return summary'
content = re.sub(pattern, new_method.strip(), content, flags=re.DOTALL)

# Save
with open(file_path, 'w') as f:
    f.write(content)

print("✅ _prepare_evolution_summary replaced with robust version!")
