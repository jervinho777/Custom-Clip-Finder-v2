#!/bin/bash

echo "🔄 AUTO-UPDATE: VIRAL PRINCIPLES BRAIN"
echo "======================================"

# Step 1: Analyze new restructure examples (if any)
echo ""
echo "📊 Step 1: Analyzing restructure examples..."
python analyze_restructures_v1.py

# Step 2: Synthesize into master principles
echo ""
echo "🧠 Step 2: Synthesizing master principles..."
python synthesize_principles.py

echo ""
echo "✅ Brain updated!"
echo "   Next composition will use latest learnings!"

