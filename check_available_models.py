#!/usr/bin/env python3
"""Check which AI models are actually available"""

import os
import asyncio

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional


async def check_openai_models():
    """Check OpenAI available models"""
    print("\n🔍 Checking OpenAI Models...")
    
    try:
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("   ⚠️  No API key found")
            return
        
        client = AsyncOpenAI(api_key=api_key)
        
        # List all models
        models = await client.models.list()
        
        # Filter for relevant models
        relevant = []
        for model in models.data:
            model_id = model.id
            if any(x in model_id for x in ['gpt-5', 'gpt-4', 'gpt-3.5']):
                relevant.append(model_id)
        
        print(f"   Found {len(relevant)} relevant models:")
        for model in sorted(relevant):
            print(f"      • {model}")
        
        # Check specific models
        test_models = ['gpt-5.2-pro', 'gpt-5', 'gpt-4-turbo', 'gpt-4o']
        print(f"\n   Checking specific models:")
        all_model_ids = [m.id for m in models.data]
        for model in test_models:
            exists = model in all_model_ids
            status = "✅" if exists else "❌"
            print(f"      {status} {model}")
        
    except ImportError:
        print("   ⚠️  OpenAI library not installed")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def check_anthropic_models():
    """Check Anthropic available models"""
    print("\n🔍 Checking Anthropic Models...")
    
    try:
        from anthropic import AsyncAnthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("   ⚠️  No API key found")
            return
        
        client = AsyncAnthropic(api_key=api_key)
        
        # Test models
        test_models = [
            'claude-opus-4-5-20250514',
            'claude-opus-4-20241022',
            'claude-sonnet-4-5-20250929',
            'claude-sonnet-4-20250514',
            'claude-haiku-4-20250514'
        ]
        
        print(f"   Testing models:")
        for model in test_models:
            try:
                response = await client.messages.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                print(f"      ✅ {model}")
            except Exception as e:
                error_msg = str(e)
                if "model" in error_msg.lower() or "not found" in error_msg.lower():
                    print(f"      ❌ {model} - Not available")
                else:
                    print(f"      ⚠️  {model} - Error: {error_msg[:50]}")
        
    except ImportError:
        print("   ⚠️  Anthropic library not installed")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def check_gemini_models():
    """Check Gemini available models"""
    print("\n🔍 Checking Gemini Models...")
    
    try:
        from google import genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("   ⚠️  No API key found")
            return
        
        client = genai.Client(api_key=api_key)
        
        # List models
        try:
            models = client.models.list()
            print(f"   Available models:")
            for model in models:
                if hasattr(model, 'name'):
                    print(f"      • {model.name}")
        except Exception as e:
            print(f"   Could not list models: {e}")
        
        # Test specific models
        test_models = [
            'gemini-3-pro',
            'gemini-2.0-flash-exp',
            'gemini-2.5-flash',
            'gemini-pro',
            'gemini-1.5-pro'
        ]
        
        print(f"\n   Testing models:")
        for model in test_models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Hi"
                )
                print(f"      ✅ {model}")
            except Exception as e:
                error_msg = str(e)
                if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                    print(f"      ❌ {model} - Not available")
                else:
                    print(f"      ⚠️  {model} - Error: {error_msg[:50]}")
        
    except ImportError:
        print("   ⚠️  Google GenAI library not installed")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def check_deepseek_models():
    """Check DeepSeek available models"""
    print("\n🔍 Checking DeepSeek Models...")
    
    try:
        from openai import AsyncOpenAI
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("   ⚠️  No API key found")
            return
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Test models
        test_models = ['deepseek-chat', 'deepseek-coder']
        
        print(f"   Testing models:")
        for model in test_models:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                print(f"      ✅ {model}")
            except Exception as e:
                print(f"      ❌ {model} - {str(e)[:50]}")
        
    except ImportError:
        print("   ⚠️  OpenAI library not installed")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def check_grok_models():
    """Check Grok available models"""
    print("\n🔍 Checking Grok Models...")
    
    try:
        from openai import AsyncOpenAI
        
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            print("   ⚠️  No API key found")
            return
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        
        # Test models
        test_models = [
            'grok-4-1-fast-reasoning',
            'grok-4-fast-reasoning',
            'grok-3',
            'grok-2-vision-1212',
            'grok-beta'
        ]
        
        print(f"   Testing models:")
        for model in test_models:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                print(f"      ✅ {model}")
            except Exception as e:
                error_msg = str(e)
                if "model" in error_msg.lower() or "not found" in error_msg.lower():
                    print(f"      ❌ {model} - Not available")
                else:
                    print(f"      ⚠️  {model} - Error: {error_msg[:50]}")
        
    except ImportError:
        print("   ⚠️  OpenAI library not installed")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def main():
    print("\n" + "="*70)
    print("🔍 CHECKING AVAILABLE AI MODELS")
    print("="*70)
    
    await check_openai_models()
    await check_anthropic_models()
    await check_gemini_models()
    await check_deepseek_models()
    await check_grok_models()
    
    print("\n" + "="*70)
    print("✅ Model check complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

