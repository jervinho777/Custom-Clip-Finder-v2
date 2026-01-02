#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("🔍 CLAUDE API DEBUG")
print("="*60)

# Check API Key
api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print(f"✅ API Key found: {api_key[:20]}...")
else:
    print("❌ API Key NOT found")
    exit(1)

# Check anthropic package
try:
    from anthropic import Anthropic
    print("✅ anthropic package installed")
except ImportError:
    print("❌ anthropic package NOT installed")
    print("   Run: pip install anthropic")
    exit(1)

# Test API connection
try:
    client = Anthropic(api_key=api_key)
    print("✅ Anthropic client created")
    
    # Test simple call
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[
            {"role": "user", "content": "Say 'Hello!' in one word"}
        ]
    )
    
    response = message.content[0].text
    print(f"✅ API Response: {response}")
    print(f"💰 Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
    
except Exception as e:
    print(f"❌ API Error: {e}")
    exit(1)

print("\n" + "="*60)
print("✅ ALL CHECKS PASSED!")
print("="*60)

# Now test HybridLearner
print("\n🧠 Testing HybridLearner...\n")

from backend.ai.hybrid_learner import HybridLearner

learner = HybridLearner()

if learner.has_claude:
    print("✅ Claude available in HybridLearner")
    
    # Try analysis
    insights = learner.analyze_training_evolution()
    
    if insights:
        learner.print_insights()
    else:
        print("⚠️ No insights generated")
else:
    print("❌ Claude NOT available in HybridLearner")
