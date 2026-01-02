import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

async def test_grok():
    print("\n🧪 Testing Grok with Credits...\n")
    
    client = AsyncOpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    
    test_models = [
        'grok-beta',
        'grok-4-1-fast-reasoning',
        'grok-4-fast-reasoning',
        'grok-3'
    ]
    
    for model in test_models:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=5
            )
            print(f"✅ {model}: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ {model}: {str(e)[:100]}")

asyncio.run(test_grok())
