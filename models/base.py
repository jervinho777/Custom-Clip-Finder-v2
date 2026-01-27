"""
Base AI Model Interface

Unified interface for all AI providers.
Based on V1 create_clips_v3_ensemble.py with verified working models.

CACHE-FIRST: Uses Cache class to avoid unnecessary API calls.

Team:
- GPT-5.2 (OpenAI) - Reasoning, Speed, Quality
- Opus 4.5 (Anthropic) - MAXIMUM QUALITY! 💎
- Gemini 3.0 Pro (Google) - Multimodal, Long Context
- DeepSeek V3.2 (DeepSeek) - Logic, Patterns, Cost-Efficient
- Grok 4.1 (xAI) - Reasoning, Edge Cases
"""

import os
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Import Cache system
from utils.cache import Cache

# Global cache instance
_ai_cache: Optional[Cache] = None

# =============================================================================
# 🎯 GLOBAL MODEL CONSTANTS (Import these for consistent usage!)
# =============================================================================

# 👑 VIRAL COUNCIL - The 5 AI Judges
OPUS_MODEL_ID = "claude-opus-4-5-20251101"       # Anthropic Opus 4.5 💎 (JUDGE)
SONNET_MODEL_ID = "claude-sonnet-4-5-20250929"   # Anthropic Sonnet 4.5 (Speed)
GPT_MODEL_ID = "gpt-4o"                           # OpenAI GPT-4o (GPT-5.2 not yet available)
GEMINI_MODEL_ID = "gemini-3-pro-preview"         # Google Gemini 3 Pro 🌟
GROK_MODEL_ID = "grok-4-1-fast-reasoning"        # xAI Grok 4.1 🚀
DEEPSEEK_MODEL_ID = "deepseek-reasoner"          # DeepSeek Reasoner 🧠

# Council Members (for iteration)
COUNCIL_MODEL_IDS = {
    "anthropic": OPUS_MODEL_ID,
    "openai": GPT_MODEL_ID,
    "google": GEMINI_MODEL_ID,
    "xai": GROK_MODEL_ID,
    "deepseek": DEEPSEEK_MODEL_ID,
}


def _get_ai_cache() -> Cache:
    """Get or initialize AI cache instance."""
    global _ai_cache
    if _ai_cache is None:
        _ai_cache = Cache()
    return _ai_cache


def _generate_prompt_key(
    model: str,
    prompt: str,
    system: Optional[str],
    temperature: float
) -> str:
    """
    Generate unique cache key for AI request.
    
    Key is based on: model + prompt + system + temperature
    """
    key_parts = [
        model,
        prompt[:1000],  # Limit prompt length in key
        system[:500] if system else "",
        str(temperature)
    ]
    key_string = "||".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()[:32]


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
    """Abstract base class for AI models with caching support."""
    
    provider: str = "unknown"
    model: str = "unknown"
    
    # Enable/disable caching at class level
    use_cache: bool = True
    
    @abstractmethod
    async def _generate_impl(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AIResponse:
        """Internal generate implementation. Override in subclasses."""
        pass
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_cache: Optional[bool] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate a response from the model with caching.
        
        CACHE-FIRST ARCHITECTURE:
        1. Generate unique prompt_key
        2. Check cache for existing response
        3. If found: return cached (saves API cost!)
        4. If not: call API, then cache the result
        
        Args:
            prompt: User prompt
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Max output tokens
            use_cache: Override class-level cache setting
            **kwargs: Additional arguments for specific models
            
        Returns:
            AIResponse with content and metadata
        """
        # Determine if we should use cache
        should_cache = use_cache if use_cache is not None else self.use_cache
        
        # Non-deterministic responses (temp > 0) should not be cached by default
        # unless explicitly requested
        if temperature > 0.1 and use_cache is None:
            should_cache = False
        
        if should_cache:
            cache = _get_ai_cache()
            prompt_key = _generate_prompt_key(self.model, prompt, system, temperature)
            
            # Check cache
            cached = cache.get_ai_response(prompt_key)
            if cached:
                response_data = cached.get("response", {})
                print(f"   ✅ Loaded AI response from cache ({self.model[:20]}...)")
                
                # Reconstruct AIResponse from cached data
                return AIResponse(
                    content=response_data.get("content", ""),
                    model=response_data.get("model", self.model),
                    provider=response_data.get("provider", self.provider),
                    tokens_used=response_data.get("tokens_used", 0),
                    cost=0.0,  # No cost for cached response!
                    latency_ms=0,
                    cache_read_tokens=response_data.get("tokens_used", 0)
                )
        
        # Call actual API
        response = await self._generate_impl(
            prompt=prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Cache successful response
        if should_cache and response.content:
            cache = _get_ai_cache()
            prompt_key = _generate_prompt_key(self.model, prompt, system, temperature)
            
            # Store essential response data
            cache.set_ai_response(prompt_key, {
                "content": response.content,
                "model": response.model,
                "provider": response.provider,
                "tokens_used": response.tokens_used
            })
            print(f"   💾 Cached AI response ({self.model[:20]}...)")
        
        return response
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage. Override in subclasses."""
        return 0.0


class ClaudeModel(AIModel):
    """
    Anthropic Claude models.
    
    Primary: Opus 4.5 - MAXIMUM QUALITY! 💎
    Fallback: Sonnet 4.5
    
    HIGH-LEVERAGE HYBRID STRATEGY:
    - Sonnet: Scouting, Masse, Speed (Phase 1)
    - Opus: Magic, Hooks, Editing (Phase 2, Compose)
    """
    
    provider = "anthropic"
    
    # ==========================================================================
    # 🎯 OFFICIAL MODEL IDS (Use these constants everywhere!)
    # ==========================================================================
    OPUS_MODEL_ID = "claude-opus-4-5-20251101"      # Latest Opus 4.5 💎
    SONNET_MODEL_ID = "claude-sonnet-4-5-20250929"  # Latest Sonnet 4.5
    
    # Pricing per 1M tokens
    PRICING = {
        "claude-opus-4-5-20251101": {"input": 15.0, "output": 75.0},   # Opus 4.5 💎 (NEW)
        "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},    # Opus (old ID)
        "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0}, # Sonnet 4.5
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},   # Alt name
    }
    
    # Caching-supported models (90% cost reduction on cached tokens!)
    CACHE_SUPPORTED_MODELS = {
        "claude-opus-4-5-20251101",   # ✅ NEW Opus
        "claude-opus-4-20250514",     # ✅ Old Opus
        "claude-sonnet-4-5-20250929", # ✅ Sonnet
        "claude-sonnet-4-20250514",   # ✅ Alt Sonnet
    }
    
    MODELS = {
        "opus": "claude-opus-4-5-20251101",     # Updated to new ID
        "sonnet": "claude-sonnet-4-5-20250929",
    }
    
    def __init__(self, model: str = "claude-opus-4-5-20251101"):
        # Accept short names
        if model in self.MODELS:
            model = self.MODELS[model]
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
    
    # Threshold for automatic prompt caching (characters)
    AUTO_CACHE_THRESHOLD = 4000  # ~1024 tokens
    
    async def _generate_impl(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        cache_system: bool = None,  # None = auto-detect
        response_model: Optional[type] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate response from Claude with AUTO PROMPT CACHING.
        
        Args:
            prompt: User message
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Max output tokens
            cache_system: Enable prompt caching (None = auto for long prompts, 90% savings!)
            response_model: Optional Pydantic model for structured output
        """
        from anthropic import AsyncAnthropic
        import time
        
        client = AsyncAnthropic(api_key=self.api_key)
        
        # =================================================================
        # AUTO PROMPT CACHING (GOD SPEED!)
        # =================================================================
        # Automatically enable caching for long system prompts or user prompts
        # This saves 90% on input token costs for repeated calls!
        
        total_input_length = len(prompt) + (len(system) if system else 0)
        
        # Check if model supports caching
        model_supports_cache = self.model in self.CACHE_SUPPORTED_MODELS
        should_cache = cache_system if cache_system is not None else (
            model_supports_cache and total_input_length > self.AUTO_CACHE_THRESHOLD
        )
        
        if should_cache and not model_supports_cache:
            print(f"   ⚠️ Warning: Model {self.model} does not support caching. Caching disabled.")
            should_cache = False
        
        # Build system message with caching
        if should_cache and system and len(system) > 1000:
            # Cache the system prompt (usually contains transcript/context)
            system_content = [{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"}  # 🚀 90% cost savings!
            }]
            print(f"   ⚡ Anthropic Prompt Caching ENABLED (system: {len(system)} chars)")
        else:
            system_content = system or "You are a helpful assistant."
        
        # Build user message with caching for very long prompts
        if should_cache and len(prompt) > self.AUTO_CACHE_THRESHOLD:
            user_content = [{
                "type": "text",
                "text": prompt,
                "cache_control": {"type": "ephemeral"}  # 🚀 Cache user message too!
            }]
            print(f"   ⚡ Anthropic Prompt Caching ENABLED (user: {len(prompt)} chars)")
        else:
            user_content = prompt
        
        start = time.time()
        
        # Build request kwargs
        request_kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_content,
            "messages": [{"role": "user", "content": user_content}]
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
    
    Primary: GPT-4o (GPT-5.2 not yet available via chat API)
    Fallback: GPT-4o-mini
    """
    
    provider = "openai"
    
    # 🎯 OFFICIAL MODEL IDS (GPT-5.2 not available as chat model yet)
    GPT_PRO_MODEL_ID = "gpt-4o"                    # Best available for chat 🔥
    GPT_FAST_MODEL_ID = "gpt-4o-mini"              # Fast/cheap fallback
    
    PRICING = {
        "gpt-4o": {"input": 2.5, "output": 10.0},  # GPT-4o (COUNCIL)
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "o1": {"input": 15.0, "output": 60.0},
        "o1-mini": {"input": 3.0, "output": 12.0},
    }
    
    MODELS = {
        "flagship": "gpt-4o",
        "pro": "gpt-4o",
        "fast": "gpt-4o-mini",
        "mini": "gpt-4o-mini",
    }
    
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")
    
    async def _generate_impl(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AIResponse:
        from openai import AsyncOpenAI
        import time
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        start = time.time()
        
        # GPT-5.2 uses max_completion_tokens, older models use max_tokens
        api_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        # Check if model requires max_completion_tokens (GPT-5.2+)
        if self.model.startswith("gpt-5") or self.model.startswith("o1"):
            api_params["max_completion_tokens"] = max_tokens
        else:
            api_params["max_tokens"] = max_tokens
        
        try:
            response = await client.chat.completions.create(**api_params)
        except Exception as e:
            # Fallback to GPT-4o-mini if primary model fails
            fallback_model = "gpt-4o-mini" if self.model == "gpt-4o" else "gpt-4o"
            print(f"   ⚠️ {self.model} failed, falling back to {fallback_model}: {e}")
            fallback_params = {
                "model": fallback_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            response = await client.chat.completions.create(**fallback_params)
        
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
    
    Primary: Gemini 3 Pro Preview 🌟
    Fallback: Gemini 2.0 Flash
    """
    
    provider = "google"
    
    # 🎯 OFFICIAL MODEL IDS
    GEMINI_PRO_MODEL_ID = "gemini-3-pro-preview"   # Latest flagship 🌟 (COUNCIL)
    GEMINI_FAST_MODEL_ID = "gemini-2.0-flash"       # Fast/cheap fallback
    
    PRICING = {
        "gemini-3-pro-preview": {"input": 1.75, "output": 7.0},  # Gemini 3 Pro Preview (COUNCIL)
        "gemini-3.0-pro": {"input": 1.50, "output": 6.0},  # Gemini 3.0 Pro
        "gemini-2.5-pro": {"input": 1.25, "output": 5.0},  # Gemini 2.5 Pro
        "gemini-2.0-flash": {"input": 0.075, "output": 0.3},  # Flash fallback
        "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.3},
    }
    
    MODELS = {
        "flagship": "gemini-3-pro-preview",
        "pro": "gemini-3-pro-preview",
        "fast": "gemini-2.0-flash",
    }
    
    def __init__(self, model: str = "gemini-3-pro-preview"):
        self.model = model
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found")
    
    async def _generate_impl(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AIResponse:
        import time
        
        # Try new SDK first, fallback to old SDK
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            use_new_sdk = False
        except ImportError:
            try:
                from google import genai as new_genai
                use_new_sdk = True
            except ImportError:
                raise ImportError(
                    "Neither google-generativeai nor google-genai is installed. "
                    "Install with: pip install google-generativeai"
                )
        
        start = time.time()
        
        # Build the full prompt with system instruction
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        try:
            if use_new_sdk:
                # New google-genai SDK
                from google.genai import types
                client = new_genai.Client(api_key=self.api_key)
                response = await client.aio.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                content = response.text
                usage = getattr(response, 'usage_metadata', None)
                input_tokens = getattr(usage, 'prompt_token_count', 0) if usage else 0
                output_tokens = getattr(usage, 'candidates_token_count', 0) if usage else 0
            else:
                # Old google-generativeai SDK (synchronous with asyncio wrapper)
                import asyncio
                model = genai.GenerativeModel(
                    model_name=self.model,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens
                    }
                )
                
                # Run in executor since old SDK is synchronous
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(full_prompt)
                )
                content = response.text
                # Old SDK token counting
                input_tokens = len(full_prompt) // 4  # Rough estimate
                output_tokens = len(content) // 4
                
        except Exception as e:
            # Fallback to gemini-2.0-flash if primary fails
            fallback_model = "gemini-2.0-flash"
            print(f"   ⚠️ {self.model} failed, falling back to {fallback_model}: {str(e)[:100]}")
            
            if use_new_sdk:
                response = await client.aio.models.generate_content(
                    model=fallback_model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                content = response.text
                usage = getattr(response, 'usage_metadata', None)
                input_tokens = getattr(usage, 'prompt_token_count', 0) if usage else 0
                output_tokens = getattr(usage, 'candidates_token_count', 0) if usage else 0
            else:
                model = genai.GenerativeModel(
                    model_name=fallback_model,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens
                    }
                )
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(full_prompt)
                )
                content = response.text
                input_tokens = len(full_prompt) // 4
                output_tokens = len(content) // 4
        
        latency = int((time.time() - start) * 1000)
        
        return AIResponse(
            content=content,
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
    
    Primary: Grok 4.1 Fast Reasoning 🚀 (COUNCIL MEMBER)
    """
    
    provider = "xai"
    
    # 🎯 OFFICIAL MODEL IDS
    GROK_MODEL_ID = "grok-4-1-fast-reasoning"  # Latest flagship 🚀 (COUNCIL)
    
    PRICING = {
        "grok-4-1-fast-reasoning": {"input": 0.20, "output": 0.50},  # Best model (COUNCIL)
        "grok-4-fast-reasoning": {"input": 0.20, "output": 0.50},  # Backup
        "grok-3": {"input": 3.0, "output": 15.0},
    }
    
    MODELS = {
        "flagship": "grok-4-1-fast-reasoning",
        "fast": "grok-4-1-fast-reasoning",
    }
    
    def __init__(self, model: str = "grok-4-1-fast-reasoning"):
        self.model = model
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found")
    
    async def _generate_impl(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
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
    
    Primary: DeepSeek Reasoner 🧠 (COUNCIL MEMBER)
    Chain-of-Thought reasoning model.
    
    NOTE: DeepSeek Reasoner returns reasoning in <think> tags.
          We extract the final answer after </think>.
    """
    
    provider = "deepseek"
    
    # 🎯 OFFICIAL MODEL IDS
    DEEPSEEK_REASONER_ID = "deepseek-reasoner"  # Best reasoning 🧠 (COUNCIL)
    DEEPSEEK_CHAT_ID = "deepseek-chat"          # Fast/cheap
    
    PRICING = {
        "deepseek-reasoner": {"input": 0.55, "output": 2.19},  # Reasoner (COUNCIL)
        "deepseek-chat": {"input": 0.27, "output": 1.10},      # V3.2
    }
    
    MODELS = {
        "flagship": "deepseek-reasoner",
        "reasoner": "deepseek-reasoner",
        "chat": "deepseek-chat",
        "fast": "deepseek-chat",
    }
    
    def __init__(self, model: str = "deepseek-reasoner"):
        self.model = model
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found")
    
    def _extract_final_answer(self, content: str) -> str:
        """
        Extract final answer from DeepSeek Reasoner response.
        
        DeepSeek Reasoner wraps reasoning in <think>...</think> tags.
        We want only the final answer AFTER the closing </think> tag.
        """
        import re
        
        # Check if response contains <think> tags
        if "</think>" in content:
            # Extract everything after </think>
            parts = content.split("</think>")
            if len(parts) > 1:
                final_answer = parts[-1].strip()
                return final_answer if final_answer else content
        
        return content
    
    async def _generate_impl(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
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
        
        # Extract content and handle Chain-of-Thought for Reasoner
        raw_content = response.choices[0].message.content or ""
        if self.model == "deepseek-reasoner":
            content = self._extract_final_answer(raw_content)
        else:
            content = raw_content
        
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        
        return AIResponse(
            content=content,  # Already processed for Chain-of-Thought
            model=self.model,
            provider=self.provider,
            tokens_used=input_tokens + output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency,
            raw_response=response
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, {"input": 0.55, "output": 2.19})
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
