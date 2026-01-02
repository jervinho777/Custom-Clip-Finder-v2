from pathlib import Path

file_path = Path("backend/ai/hybrid_learner.py")

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find and replace the method
new_lines = []
in_method = False
skip_until_next_def = False

for i, line in enumerate(lines):
    if 'def _format_features' in line:
        # Replace entire method
        new_lines.append('    def _format_features(self, features) -> str:\n')
        new_lines.append('        """Format feature list - handles dict or list"""\n')
        new_lines.append('        if not features:\n')
        new_lines.append('            return "No features"\n')
        new_lines.append('        \n')
        new_lines.append('        # Handle dict\n')
        new_lines.append('        if isinstance(features, dict):\n')
        new_lines.append('            features = sorted(features.items(), key=lambda x: x[1], reverse=True)\n')
        new_lines.append('        \n')
        new_lines.append('        lines = []\n')
        new_lines.append('        for feat, importance in features[:5]:\n')
        new_lines.append('            lines.append(f"  - {feat}: {importance:.4f}")\n')
        new_lines.append('        return "\\n".join(lines)\n')
        in_method = True
        skip_until_next_def = True
        continue
    
    if skip_until_next_def:
        if line.strip().startswith('def '):
            skip_until_next_def = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("✅ _format_features fixed!")
