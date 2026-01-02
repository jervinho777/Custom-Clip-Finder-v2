"""
AI Ensemble System

Multi-AI consensus for higher quality results.
5 AIs vote in parallel, consensus is extracted.
"""

import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from collections import Counter

from .base import AIModel, AIResponse, get_model


@dataclass
class EnsembleResponse:
    """Response from AI ensemble."""
    consensus: str
    confidence: float
    votes: List[Dict]
    total_cost: float
    total_tokens: int
    total_latency_ms: int


class AIEnsemble:
    """
    5-AI Ensemble for consensus-based responses.
    
    Uses:
    - Claude Sonnet (synthesis)
    - GPT-4o (pattern recognition)
    - Gemini Flash (context analysis)
    - Grok (edge cases)
    - DeepSeek (cost-efficient verification)
    """
    
    # Use dynamic model detection - always latest models
    DEFAULT_MODELS = [
        ("anthropic", None, "opus"),      # Latest Opus
        ("openai", None, "flagship"),    # Latest GPT flagship
        ("google", None, "pro"),          # Latest Gemini Pro
        ("xai", None, "flagship"),       # Latest Grok flagship
        ("deepseek", None, "chat"),      # Latest DeepSeek chat
    ]
    
    def __init__(self, models: Optional[List[tuple]] = None):
        """
        Initialize ensemble.
        
        Args:
            models: Optional list of (provider, model) tuples.
                   Defaults to 5-AI ensemble.
        """
        self.model_configs = models or self.DEFAULT_MODELS
        self._models: List[AIModel] = []
        self._init_errors: List[str] = []
        
        # Initialize models (skip unavailable ones)
        for config in self.model_configs:
            try:
                # Support both old format (provider, model) and new format (provider, model, tier)
                if len(config) == 2:
                    provider, model = config
                    ai_model = get_model(provider, model=model)
                elif len(config) == 3:
                    provider, model, tier = config
                    if model is None:
                        ai_model = get_model(provider, tier=tier)
                    else:
                        ai_model = get_model(provider, model=model)
                else:
                    raise ValueError(f"Invalid config format: {config}")
                
                self._models.append(ai_model)
            except ValueError as e:
                self._init_errors.append(f"{config[0]}: {e}")
        
        if not self._models:
            raise ValueError(f"No models available. Errors: {self._init_errors}")
    
    @property
    def available_models(self) -> List[str]:
        """List of available model names."""
        return [f"{m.provider}:{m.model}" for m in self._models]
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        min_consensus: int = 3
    ) -> EnsembleResponse:
        """
        Generate consensus response from all models.
        
        Args:
            prompt: The prompt to send
            system: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Max output tokens
            min_consensus: Minimum votes needed for consensus
            
        Returns:
            EnsembleResponse with consensus and vote details
        """
        # Run all models in parallel
        tasks = [
            model.generate(prompt, system, temperature, max_tokens)
            for model in self._models
        ]
        
        responses: List[AIResponse] = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful responses
        votes = []
        total_cost = 0.0
        total_tokens = 0
        total_latency = 0
        
        for i, resp in enumerate(responses):
            model = self._models[i]
            if isinstance(resp, Exception):
                votes.append({
                    "provider": model.provider,
                    "model": model.model,
                    "error": str(resp),
                    "content": None
                })
            else:
                votes.append({
                    "provider": resp.provider,
                    "model": resp.model,
                    "content": resp.content,
                    "tokens": resp.tokens_used,
                    "cost": resp.cost,
                    "latency_ms": resp.latency_ms
                })
                total_cost += resp.cost
                total_tokens += resp.tokens_used
                total_latency = max(total_latency, resp.latency_ms)  # Parallel, so take max
        
        # Extract consensus
        successful_votes = [v for v in votes if v.get("content")]
        
        if len(successful_votes) < min_consensus:
            # Not enough votes, use first successful response
            consensus = successful_votes[0]["content"] if successful_votes else ""
            confidence = len(successful_votes) / len(self._models)
        else:
            # Use Claude to synthesize consensus
            consensus, confidence = await self._synthesize_consensus(successful_votes, system)
        
        return EnsembleResponse(
            consensus=consensus,
            confidence=confidence,
            votes=votes,
            total_cost=total_cost,
            total_tokens=total_tokens,
            total_latency_ms=total_latency
        )
    
    async def _synthesize_consensus(
        self,
        votes: List[Dict],
        original_system: Optional[str]
    ) -> tuple[str, float]:
        """
        Synthesize consensus from multiple AI responses.
        
        Uses Claude to find common ground and resolve conflicts.
        """
        # Find Claude model or use first available
        claude = next((m for m in self._models if m.provider == "anthropic"), self._models[0])
        
        synthesis_prompt = f"""Du hast {len(votes)} AI-Antworten auf die gleiche Frage erhalten.

ANTWORTEN:
"""
        for i, vote in enumerate(votes, 1):
            synthesis_prompt += f"\n--- AI {i} ({vote['provider']}) ---\n{vote['content'][:2000]}\n"
        
        synthesis_prompt += """
DEINE AUFGABE:
1. Identifiziere wo ALLE oder die MEHRHEIT übereinstimmen
2. Bei Konflikten: Wähle die fundierteste Antwort
3. Erstelle eine SYNTHESE die das Beste aus allen kombiniert

WICHTIG: Gib NUR die synthetisierte Antwort zurück, keine Meta-Kommentare."""

        response = await claude.generate(
            synthesis_prompt,
            system="Du bist ein Synthesizer. Kombiniere mehrere AI-Antworten zu einer optimalen Antwort.",
            temperature=0.3
        )
        
        # Calculate confidence based on agreement
        # (simplified - in production you'd analyze semantic similarity)
        confidence = len(votes) / len(self._models)
        
        return response.content, confidence
    
    async def vote(
        self,
        prompt: str,
        options: List[str],
        system: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Have all models vote on options.
        
        Args:
            prompt: Context prompt
            options: List of options to vote on
            system: Optional system prompt
            
        Returns:
            Dict mapping options to vote counts
        """
        vote_prompt = f"""{prompt}

OPTIONEN:
{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(options))}

Antworte NUR mit der Nummer deiner Wahl (1-{len(options)})."""

        responses = await asyncio.gather(*[
            model.generate(vote_prompt, system, temperature=0.1, max_tokens=10)
            for model in self._models
        ], return_exceptions=True)
        
        votes = Counter()
        for resp in responses:
            if isinstance(resp, AIResponse):
                try:
                    choice = int(resp.content.strip().split()[0]) - 1
                    if 0 <= choice < len(options):
                        votes[options[choice]] += 1
                except (ValueError, IndexError):
                    pass
        
        return dict(votes)

