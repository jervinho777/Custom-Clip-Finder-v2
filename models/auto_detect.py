"""
Dynamic AI Model Detection

Automatically detects the latest available models from all AI providers.
Caches results for 24 hours to avoid excessive API calls.

Usage:
    from models.auto_detect import get_model
    
    claude = get_model("anthropic", "opus")
    gpt = get_model("openai", "flagship")
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import hashlib

# Cache file location
CACHE_FILE = Path(__file__).parent.parent / "config" / "detected_models.json"
CACHE_DURATION_HOURS = 24


def _get_cache() -> Dict:
    """Load cached model detection results."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                cache = json.load(f)
            # Check if cache is still valid
            cached_at = datetime.fromisoformat(cache.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_at < timedelta(hours=CACHE_DURATION_HOURS):
                return cache.get("models", {})
        except Exception:
            pass
    return {}


def _save_cache(models: Dict):
    """Save model detection results to cache."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "cached_at": datetime.now().isoformat(),
            "models": models
        }, f, indent=2)


def _detect_anthropic_models() -> Dict[str, str]:
    """Detect latest Anthropic models."""
    # Anthropic doesn't have a list_models endpoint
    # Use known latest models (updated manually when new versions release)
    # These are the latest verified working models as of 2026-01-02
    
    models = {
        "opus": "claude-opus-4-20250514",  # Opus 4.5 (latest)
        "sonnet": "claude-sonnet-4-5-20250929",  # Sonnet 4.5 (latest)
        "haiku": "claude-3-5-haiku-20241022",  # Haiku 3.5 (latest)
    }
    
    # Optional: Check API key exists (but don't make expensive calls)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY not found, using defaults")
    
    return models


def _detect_openai_models() -> Dict[str, str]:
    """Detect latest OpenAI models."""
    models = {}
    
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {}
        
        client = OpenAI(api_key=api_key)
        
        # Get list of available models
        available_models = [m.id for m in client.models.list().data]
        
        # Map to tiers
        tier_mapping = {
            "flagship": ["gpt-5.2", "gpt-5", "gpt-4o", "gpt-4-turbo"],
            "pro": ["gpt-4o", "gpt-4-turbo", "gpt-4"],
            "mini": ["gpt-4o-mini", "gpt-3.5-turbo"],
            "codex": ["gpt-4o", "gpt-4-turbo"]
        }
        
        for tier, model_names in tier_mapping.items():
            for model_name in model_names:
                if model_name in available_models:
                    models[tier] = model_name
                    break
        
    except Exception as e:
        print(f"⚠️ OpenAI detection failed: {e}")
    
    # Fallback to known latest
    if not models.get("flagship"):
        models["flagship"] = "gpt-4o"  # GPT-5.2 may not be in list yet
    if not models.get("pro"):
        models["pro"] = "gpt-4o"
    if not models.get("mini"):
        models["mini"] = "gpt-4o-mini"
    
    return models


def _detect_gemini_models() -> Dict[str, str]:
    """Detect latest Google Gemini models."""
    models = {}
    
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {}
        
        genai.configure(api_key=api_key)
        
        # List available models
        available_models = [m.name for m in genai.list_models()]
        
        # Map to tiers
        tier_mapping = {
            "pro": ["gemini-3.0-pro", "gemini-2.5-pro", "gemini-2.0-pro", "gemini-pro"],
            "flash": ["gemini-2.0-flash-exp", "gemini-2.0-flash", "gemini-1.5-flash"],
            "flash_lite": ["gemini-2.0-flash-exp", "gemini-2.0-flash"]
        }
        
        for tier, model_names in tier_mapping.items():
            for model_name in model_names:
                # Gemini models are listed as "models/gemini-3.0-pro"
                if any(f"models/{name}" in available_models or name in available_models for name in model_names):
                    # Use the first matching model name
                    models[tier] = model_names[0]
                    break
        
    except Exception as e:
        print(f"⚠️ Gemini detection failed: {e}")
    
    # Fallback
    if not models.get("pro"):
        models["pro"] = "gemini-2.0-pro"
    if not models.get("flash"):
        models["flash"] = "gemini-2.0-flash-exp"
    
    return models


def _detect_xai_models() -> Dict[str, str]:
    """Detect latest xAI (Grok) models."""
    models = {}
    
    try:
        from openai import OpenAI
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            return {}
        
        # xAI uses OpenAI-compatible API
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        
        available_models = [m.id for m in client.models.list().data]
        
        tier_mapping = {
            "flagship": ["grok-4-1-fast-reasoning", "grok-4-fast-reasoning", "grok-3"],
            "standard": ["grok-3", "grok-2"],
            "mini": ["grok-2-mini"]
        }
        
        for tier, model_names in tier_mapping.items():
            for model_name in model_names:
                if model_name in available_models:
                    models[tier] = model_name
                    break
        
    except Exception as e:
        print(f"⚠️ xAI detection failed: {e}")
    
    # Fallback
    if not models.get("flagship"):
        models["flagship"] = "grok-4-1-fast-reasoning"
    if not models.get("standard"):
        models["standard"] = "grok-3"
    
    return models


def _detect_deepseek_models() -> Dict[str, str]:
    """Detect latest DeepSeek models."""
    models = {}
    
    try:
        from openai import OpenAI
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return {}
        
        # DeepSeek uses OpenAI-compatible API
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        available_models = [m.id for m in client.models.list().data]
        
        tier_mapping = {
            "chat": ["deepseek-chat", "deepseek-v3"],
            "reasoner": ["deepseek-reasoner", "deepseek-chat"]
        }
        
        for tier, model_names in tier_mapping.items():
            for model_name in model_names:
                if model_name in available_models:
                    models[tier] = model_name
                    break
        
    except Exception as e:
        print(f"⚠️ DeepSeek detection failed: {e}")
    
    # Fallback
    if not models.get("chat"):
        models["chat"] = "deepseek-chat"
    if not models.get("reasoner"):
        models["reasoner"] = "deepseek-reasoner"
    
    return models


def detect_all_models(force: bool = False) -> Dict[str, Dict[str, str]]:
    """
    Detect all available models from all providers.
    
    Args:
        force: If True, ignore cache and force refresh
        
    Returns:
        Dict mapping provider -> tier -> model_name
    """
    # Check cache first
    if not force:
        cached = _get_cache()
        if cached:
            return cached
    
    print("🔍 Detecting latest AI models...")
    
    all_models = {
        "anthropic": _detect_anthropic_models(),
        "openai": _detect_openai_models(),
        "gemini": _detect_gemini_models(),
        "xai": _detect_xai_models(),
        "deepseek": _detect_deepseek_models()
    }
    
    # Save to cache
    _save_cache(all_models)
    
    print("✅ Model detection complete")
    return all_models


def get_model(provider: str, tier: str, force_refresh: bool = False) -> str:
    """
    Get the latest model string for a provider and tier.
    
    Args:
        provider: One of: anthropic, openai, gemini, xai, deepseek
        tier: Tier name (opus, sonnet, flagship, pro, etc.)
        force_refresh: Force refresh cache
        
    Returns:
        Model string (e.g., "claude-opus-4-20250514")
        
    Raises:
        ValueError: If provider or tier not found
    """
    models = detect_all_models(force=force_refresh)
    
    provider_models = models.get(provider.lower())
    if not provider_models:
        raise ValueError(f"Provider '{provider}' not found. Available: {list(models.keys())}")
    
    model = provider_models.get(tier.lower())
    if not model:
        raise ValueError(
            f"Tier '{tier}' not found for provider '{provider}'. "
            f"Available tiers: {list(provider_models.keys())}"
        )
    
    return model


def print_current_config():
    """Print current detected model configuration."""
    models = detect_all_models()
    
    print("\n" + "="*70)
    print("CURRENT AI MODEL CONFIGURATION")
    print("="*70)
    
    for provider, tiers in models.items():
        print(f"\n{provider.upper()}:")
        for tier, model in tiers.items():
            print(f"  {tier:15} → {model}")
    
    print("\n" + "="*70)
    print(f"Cache: {CACHE_FILE}")
    print(f"Last updated: {datetime.fromisoformat(json.load(open(CACHE_FILE))['cached_at'])}")
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if "--force" in sys.argv or "-f" in sys.argv:
        print("🔄 Forcing model refresh...")
        detect_all_models(force=True)
    elif "--print" in sys.argv or "-p" in sys.argv:
        print_current_config()
    else:
        # Default: just detect and cache
        detect_all_models()
        print_current_config()

