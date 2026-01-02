"""
Base AI Model Interface

Unified interface for all AI providers (Claude, GPT, Gemini, Grok, DeepSeek).
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
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
    """Anthropic Claude models."""
    
    provider = "anthropic"
    
    # Pricing per 1M tokens (as of 2025)
    PRICING = {
        "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    }
    
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        import anthropic
        import time
        
        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        
        start = time.time()
        response = await client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        latency = int((time.time() - start) * 1000)
        
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        
        return AIResponse(
            content=response.content[0].text,
            model=self.model,
            provider=self.provider,
            tokens_used=input_tokens + output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency,
            raw_response=response
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class OpenAIModel(AIModel):
    """OpenAI GPT models."""
    
    provider = "openai"
    
    PRICING = {
        "gpt-4o": {"input": 2.5, "output": 10.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "o1": {"input": 15.0, "output": 60.0},
    }
    
    def __init__(self, model: str = "gpt-4o"):
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
        pricing = self.PRICING.get(self.model, {"input": 2.5, "output": 10.0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class GeminiModel(AIModel):
    """Google Gemini models."""
    
    provider = "google"
    
    PRICING = {
        "gemini-2.0-flash": {"input": 0.075, "output": 0.3},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
    }
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        import google.generativeai as genai
        import time
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(
            self.model,
            system_instruction=system
        )
        
        start = time.time()
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        latency = int((time.time() - start) * 1000)
        
        # Gemini doesn't always provide token counts
        tokens = getattr(response, 'usage_metadata', None)
        input_tokens = getattr(tokens, 'prompt_token_count', 0) if tokens else 0
        output_tokens = getattr(tokens, 'candidates_token_count', 0) if tokens else 0
        
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
        pricing = self.PRICING.get(self.model, {"input": 0.075, "output": 0.3})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class GrokModel(AIModel):
    """xAI Grok models."""
    
    provider = "xai"
    
    PRICING = {
        "grok-3": {"input": 3.0, "output": 15.0},
        "grok-3-fast": {"input": 5.0, "output": 25.0},
    }
    
    def __init__(self, model: str = "grok-3"):
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
        pricing = self.PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class DeepSeekModel(AIModel):
    """DeepSeek models."""
    
    provider = "deepseek"
    
    PRICING = {
        "deepseek-chat": {"input": 0.27, "output": 1.10},
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


def get_model(provider: str, model: str) -> AIModel:
    """Factory function to get AI model by provider."""
    models = {
        "anthropic": ClaudeModel,
        "openai": OpenAIModel,
        "google": GeminiModel,
        "xai": GrokModel,
        "deepseek": DeepSeekModel,
    }
    
    if provider not in models:
        raise ValueError(f"Unknown provider: {provider}")
    
    return models[provider](model)

