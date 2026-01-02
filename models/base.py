"""
Base AI Model Interface

Unified interface for all AI providers.
Based on V1 create_clips_v3_ensemble.py with verified working models.

Team:
- GPT-5.2 (OpenAI) - Reasoning, Speed, Quality
- Opus 4.5 (Anthropic) - MAXIMUM QUALITY! 💎
- Gemini 3.0 Pro (Google) - Multimodal, Long Context
- DeepSeek V3.2 (DeepSeek) - Logic, Patterns, Cost-Efficient
- Grok 4.1 (xAI) - Reasoning, Edge Cases
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AIResponse:
    """Standardized response from any AI model."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    cost: float = 0.0
    latency_ms: int = 0
    raw_response: Optional[Any] = None
    parsed: Optional[Any] = None  # Parsed Pydantic model if response_model was provided
    cache_read_tokens: int = 0  # Tokens read from cache (90% cheaper!)
    cache_write_tokens: int = 0  # Tokens written to cache


class AIModel(ABC):
    """Abstract base class for AI models."""
    
    provider: str = "unknown"
    model: str = "unknown"
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        """Generate a response from the model."""
        pass
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage. Override in subclasses."""
        return 0.0


class ClaudeModel(AIModel):
    """
    Anthropic Claude models.
    
    Primary: Opus 4.5 - MAXIMUM QUALITY! 💎
    Fallback: Sonnet 4.5
    """
    
    provider = "anthropic"
    
    # Pricing per 1M tokens (verified from V1)
    PRICING = {
        "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},  # Opus 4.5 💎
        "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},  # Sonnet 4.5
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},  # Alt name
    }
    
    MODELS = {
        "opus": "claude-opus-4-20250514",
        "sonnet": "claude-sonnet-4-5-20250929",
    }
    
    def __init__(self, model: str = "claude-opus-4-20250514"):
        # Accept short names
        if model in self.MODELS:
            model = self.MODELS[model]
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        cache_system: bool = False,
        response_model: Optional[type] = None
    ) -> AIResponse:
        """
        Generate response from Claude.
        
        Args:
            prompt: User message
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Max output tokens
            cache_system: Enable prompt caching for system prompt (90% cost savings!)
            response_model: Optional Pydantic model for structured output
        """
        from anthropic import AsyncAnthropic
        import time
        
        client = AsyncAnthropic(api_key=self.api_key)
        
        # Build system message with optional caching
        if cache_system and system:
            system_content = [{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"}  # Enable prompt caching
            }]
        else:
            system_content = system or "You are a helpful assistant."
        
        start = time.time()
        
        # Build request kwargs
        request_kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_content,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = await client.messages.create(**request_kwargs)
        latency = int((time.time() - start) * 1000)
        
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        
        # Check for cache usage
        cache_read = getattr(response.usage, 'cache_read_input_tokens', 0)
        cache_write = getattr(response.usage, 'cache_creation_input_tokens', 0)
        
        content = response.content[0].text
        
        # Parse structured output if model provided
        parsed = None
        if response_model:
            import json
            try:
                data = json.loads(content)
                parsed = response_model.model_validate(data)
            except Exception:
                pass
        
        return AIResponse(
            content=content,
            model=self.model,
            provider=self.provider,
            tokens_used=input_tokens + output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens, cache_read),
            latency_ms=latency,
            raw_response=response,
            parsed=parsed,
            cache_read_tokens=cache_read,
            cache_write_tokens=cache_write
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, cache_read_tokens: int = 0) -> float:
        """
        Calculate cost with prompt caching savings.
        
        Cache read tokens cost 90% less than normal input tokens!
        """
        pricing = self.PRICING.get(self.model, {"input": 15.0, "output": 75.0})
        
        # Regular input tokens (excluding cached)
        regular_input = input_tokens - cache_read_tokens
        
        # Cache read is 90% cheaper
        cache_read_cost = cache_read_tokens * pricing["input"] * 0.10
        regular_input_cost = regular_input * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        
        return (cache_read_cost + regular_input_cost + output_cost) / 1_000_000


class OpenAIModel(AIModel):
    """
    OpenAI GPT models.
    
    Primary: GPT-5.2 🔥
    Fallback: GPT-4o
    """
    
    provider = "openai"
    
    PRICING = {
        "gpt-5.2": {"input": 10.0, "output": 30.0},  # GPT-5.2 🔥
        "gpt-4o": {"input": 2.5, "output": 10.0},  # Fallback
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "o1": {"input": 15.0, "output": 60.0},
    }
    
    def __init__(self, model: str = "gpt-5.2"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        from openai import AsyncOpenAI
        import time
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        start = time.time()
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            # Fallback to GPT-4o if GPT-5.2 fails
            if self.model == "gpt-5.2":
                print(f"   ⚠️ GPT-5.2 failed, falling back to GPT-4o: {e}")
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                raise
        
        latency = int((time.time() - start) * 1000)
        
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        
        return AIResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            provider=self.provider,
            tokens_used=input_tokens + output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency,
            raw_response=response
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, {"input": 10.0, "output": 30.0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class GeminiModel(AIModel):
    """
    Google Gemini models.
    
    Primary: Gemini 3.0 Pro
    Fallback: Gemini 2.0 Flash
    """
    
    provider = "google"
    
    PRICING = {
        "gemini-3.0-pro": {"input": 1.50, "output": 6.0},  # Gemini 3.0 Pro
        "gemini-2.5-pro": {"input": 1.25, "output": 5.0},  # Gemini 2.5 Pro
        "gemini-2.0-flash": {"input": 0.075, "output": 0.3},  # Flash fallback
        "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.3},
    }
    
    def __init__(self, model: str = "gemini-3.0-pro"):
        self.model = model
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        from google import genai
        from google.genai import types
        import time
        
        client = genai.Client(api_key=self.api_key)
        
        start = time.time()
        
        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
        except Exception as e:
            # Fallback to 2.0 Flash if 3.0 fails
            if "3.0" in self.model or "2.5" in self.model:
                print(f"   ⚠️ {self.model} failed, falling back to gemini-2.0-flash: {e}")
                response = await client.aio.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
            else:
                raise
        
        latency = int((time.time() - start) * 1000)
        
        # Get token counts
        usage = getattr(response, 'usage_metadata', None)
        input_tokens = getattr(usage, 'prompt_token_count', 0) if usage else 0
        output_tokens = getattr(usage, 'candidates_token_count', 0) if usage else 0
        
        return AIResponse(
            content=response.text,
            model=self.model,
            provider=self.provider,
            tokens_used=input_tokens + output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency,
            raw_response=response
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, {"input": 1.5, "output": 6.0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class GrokModel(AIModel):
    """
    xAI Grok models.
    
    Primary: Grok 4.1 Fast Reasoning 🚀
    """
    
    provider = "xai"
    
    PRICING = {
        "grok-4-1-fast-reasoning": {"input": 0.20, "output": 0.50},  # Best model
        "grok-4-fast-reasoning": {"input": 0.20, "output": 0.50},  # Backup
        "grok-3": {"input": 3.0, "output": 15.0},
    }
    
    def __init__(self, model: str = "grok-4-1-fast-reasoning"):
        self.model = model
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        from openai import AsyncOpenAI
        import time
        
        # Grok uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        start = time.time()
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            # Fallback
            if self.model == "grok-4-1-fast-reasoning":
                print(f"   ⚠️ Grok 4.1 failed, trying backup: {e}")
                response = await client.chat.completions.create(
                    model="grok-4-fast-reasoning",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                raise
        
        latency = int((time.time() - start) * 1000)
        
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        
        return AIResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            provider=self.provider,
            tokens_used=input_tokens + output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency,
            raw_response=response
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, {"input": 0.20, "output": 0.50})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class DeepSeekModel(AIModel):
    """
    DeepSeek models.
    
    Primary: DeepSeek V3.2 (deepseek-chat)
    Cost-efficient verification model.
    """
    
    provider = "deepseek"
    
    PRICING = {
        "deepseek-chat": {"input": 0.27, "output": 1.10},  # V3.2
        "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    }
    
    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        from openai import AsyncOpenAI
        import time
        
        # DeepSeek uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        start = time.time()
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        latency = int((time.time() - start) * 1000)
        
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        
        return AIResponse(
            content=response.choices[0].message.content or "",
            model=self.model,
            provider=self.provider,
            tokens_used=input_tokens + output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency,
            raw_response=response
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, {"input": 0.27, "output": 1.10})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


def get_model(provider: str, model: str = None, tier: str = None) -> AIModel:
    """
    Factory function to get AI model by provider.
    
    Uses dynamic model detection to always get the latest models.
    
    Args:
        provider: anthropic, openai, google, xai, deepseek
        model: Optional model name (if provided, uses this directly)
        tier: Optional tier name (opus, sonnet, flagship, pro, etc.)
              If tier is provided, uses auto_detect to get latest model for that tier
    
    Returns:
        Configured AIModel instance
    """
    from .auto_detect import get_model as get_model_string
    
    models = {
        "anthropic": ClaudeModel,
        "openai": OpenAIModel,
        "google": GeminiModel,
        "xai": GrokModel,
        "deepseek": DeepSeekModel,
    }
    
    if provider not in models:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(models.keys())}")
    
    # If model is explicitly provided, use it
    if model:
        model_name = model
    # If tier is provided, use auto_detect
    elif tier:
        # Map provider names (google -> gemini)
        detect_provider = "gemini" if provider == "google" else provider
        model_name = get_model_string(detect_provider, tier)
    # Otherwise, use tier-based defaults
    else:
        tier_defaults = {
            "anthropic": "opus",
            "openai": "flagship",
            "google": "pro",
            "xai": "flagship",
            "deepseek": "chat",
        }
        detect_provider = "gemini" if provider == "google" else provider
        model_name = get_model_string(detect_provider, tier_defaults[provider])
    
    return models[provider](model_name)


# Convenient aliases (use dynamic detection)
def get_opus() -> ClaudeModel:
    """Get latest Opus (Maximum Quality)"""
    return get_model("anthropic", tier="opus")

def get_sonnet() -> ClaudeModel:
    """Get latest Sonnet (Balanced)"""
    return get_model("anthropic", tier="sonnet")

def get_gpt() -> OpenAIModel:
    """Get latest GPT flagship"""
    return get_model("openai", tier="flagship")

def get_gemini() -> GeminiModel:
    """Get latest Gemini Pro"""
    return get_model("google", tier="pro")

def get_grok() -> GrokModel:
    """Get latest Grok flagship"""
    return get_model("xai", tier="flagship")

def get_deepseek() -> DeepSeekModel:
    """Get latest DeepSeek chat"""
    return get_model("deepseek", tier="chat")
