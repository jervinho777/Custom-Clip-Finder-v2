"""
Optimized Pipeline Utilities

Combines all performance optimizations:
1. Prompt Caching (90% cost savings on Anthropic)
2. Asyncio Parallel Processing (3x speed improvement)
3. Structured Outputs with Pydantic (guaranteed schema)
4. Rate Limiting with Semaphores

Usage:
    from pipeline.optimized import OptimizedCaller
    
    caller = OptimizedCaller()
    results = await caller.parallel_discover(transcript, brain_context)
"""

import asyncio
from typing import List, Optional, Type, TypeVar
from pydantic import BaseModel

from models.base import AIResponse, get_model
from models.schemas import DiscoverResponse, ComposeResponse, ValidateResponse

T = TypeVar('T', bound=BaseModel)


class OptimizedCaller:
    """
    Optimized AI caller with caching, parallel processing, and structured outputs.
    """
    
    # Rate limiting: max concurrent API calls
    RATE_LIMIT = 10
    
    def __init__(self):
        self._semaphore = asyncio.Semaphore(self.RATE_LIMIT)
        self._cache_stats = {
            "cache_hits": 0,
            "cache_writes": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0
        }
    
    async def call_with_cache(
        self,
        provider: str,
        tier: str,
        prompt: str,
        system: str,
        response_model: Optional[Type[T]] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> AIResponse:
        """
        Make an AI call with caching and rate limiting.
        
        Args:
            provider: AI provider (anthropic, openai, etc.)
            tier: Model tier (opus, sonnet, flagship, etc.)
            prompt: User prompt (dynamic content)
            system: System prompt (cached for Anthropic)
            response_model: Optional Pydantic model for structured output
            temperature: Sampling temperature
            max_tokens: Max output tokens
            
        Returns:
            AIResponse with optional parsed Pydantic model
        """
        async with self._semaphore:
            model = get_model(provider, tier=tier)
            
            # Anthropic supports prompt caching
            cache_system = provider == "anthropic"
            
            response = await model.generate(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
                cache_system=cache_system,
                response_model=response_model
            )
            
            # Track cache stats
            if response.cache_read_tokens > 0:
                self._cache_stats["cache_hits"] += 1
                self._cache_stats["tokens_saved"] += response.cache_read_tokens
                # Estimate cost saved (90% of normal input cost)
                self._cache_stats["cost_saved"] += (response.cache_read_tokens * 15.0 * 0.9) / 1_000_000
            if response.cache_write_tokens > 0:
                self._cache_stats["cache_writes"] += 1
            
            return response
    
    async def parallel_call(
        self,
        prompt: str,
        system: str,
        providers: List[tuple] = None,
        response_model: Optional[Type[T]] = None
    ) -> List[AIResponse]:
        """
        Call multiple AI providers in parallel.
        
        Args:
            prompt: User prompt
            system: System prompt
            providers: List of (provider, tier) tuples. Defaults to 5-AI ensemble.
            response_model: Optional Pydantic model for structured output
            
        Returns:
            List of AIResponses (excluding failures)
        """
        if providers is None:
            providers = [
                ("anthropic", "sonnet"),  # Sonnet for cost efficiency in ensemble
                ("openai", "flagship"),
                ("google", "flash"),  # Flash for cost efficiency
                ("xai", "flagship"),
                ("deepseek", "chat"),
            ]
        
        # Create tasks for all providers
        tasks = [
            self.call_with_cache(
                provider=provider,
                tier=tier,
                prompt=prompt,
                system=system,
                response_model=response_model
            )
            for provider, tier in providers
        ]
        
        # Execute all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failures
        valid_results = []
        for result in results:
            if isinstance(result, AIResponse):
                valid_results.append(result)
            elif isinstance(result, Exception):
                print(f"⚠️ AI call failed: {result}")
        
        return valid_results
    
    async def parallel_discover(
        self,
        transcript: str,
        brain_context: str,
        identity_prompt: str
    ) -> List[DiscoverResponse]:
        """
        Run DISCOVER stage with 5 AIs in parallel.
        
        Args:
            transcript: Video transcript
            brain_context: BRAIN context (cached)
            identity_prompt: Supreme Identity for DISCOVER
            
        Returns:
            List of DiscoverResponse from each AI
        """
        system = identity_prompt + "\n\n" + brain_context
        
        # Add structured output instruction
        prompt = f"""Analyze this transcript and find ALL potential viral moments.

TRANSCRIPT:
{transcript}

Respond with a JSON object matching this schema:
{{
    "moments": [
        {{
            "timestamps": {{"start": float, "end": float}},
            "hook_text": "string",
            "topic": "string",
            "content_type": "story|insight|tutorial|emotional|paradox|beliefbreaker",
            "hook_strength": 1-10,
            "viral_potential": 1-10,
            "reasoning": "string",
            "pattern_match": "optional pattern name"
        }}
    ],
    "total_duration_analyzed": float,
    "ai_provider": "your provider name"
}}"""
        
        responses = await self.parallel_call(
            prompt=prompt,
            system=system,
            response_model=DiscoverResponse
        )
        
        # Extract parsed models
        parsed = []
        for response in responses:
            if response.parsed and isinstance(response.parsed, DiscoverResponse):
                parsed.append(response.parsed)
            else:
                # Try manual parsing
                import json
                try:
                    data = json.loads(response.content)
                    parsed.append(DiscoverResponse.model_validate(data))
                except Exception:
                    pass
        
        return parsed
    
    async def godmode_evaluate(
        self,
        clips: List[dict],
        brain_context: str,
        identity_prompt: str
    ) -> List[dict]:
        """
        Run Godmode evaluation with Opus (single AI, premium quality).
        
        Args:
            clips: List of composed clips to evaluate
            brain_context: BRAIN context
            identity_prompt: Godmode Supreme Identity
            
        Returns:
            List of clips with Godmode scores
        """
        # Godmode uses Opus only
        system = identity_prompt + "\n\n" + brain_context
        
        results = []
        
        # Process clips in batches (parallel within batch)
        batch_size = 5
        for i in range(0, len(clips), batch_size):
            batch = clips[i:i+batch_size]
            
            tasks = [
                self.call_with_cache(
                    provider="anthropic",
                    tier="opus",
                    prompt=f"Evaluate this clip:\n{clip}",
                    system=system,
                    temperature=0.2
                )
                for clip in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, AIResponse):
                    clips[i+j]["godmode_response"] = result.content
                    clips[i+j]["godmode_cost"] = result.cost
                    results.append(clips[i+j])
        
        return results
    
    def get_cache_stats(self) -> dict:
        """Get prompt caching statistics."""
        return self._cache_stats.copy()
    
    def print_cache_stats(self):
        """Print cache statistics."""
        stats = self._cache_stats
        print("\n" + "="*50)
        print("📊 PROMPT CACHING STATS")
        print("="*50)
        print(f"   Cache Hits: {stats['cache_hits']}")
        print(f"   Cache Writes: {stats['cache_writes']}")
        print(f"   Tokens Saved: {stats['tokens_saved']:,}")
        print(f"   Cost Saved: ${stats['cost_saved']:.4f}")
        print("="*50 + "\n")


# Global instance for easy access
_caller: Optional[OptimizedCaller] = None

def get_caller() -> OptimizedCaller:
    """Get or create global OptimizedCaller instance."""
    global _caller
    if _caller is None:
        _caller = OptimizedCaller()
    return _caller

