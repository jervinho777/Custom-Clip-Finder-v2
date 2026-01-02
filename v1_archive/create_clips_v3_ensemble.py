#!/usr/bin/env python3
"""
🎬 CREATE CLIPS V3 - Premium 5-AI Ensemble
Quality-First: Multi-AI Consensus System

Team:
- GPT-5.2 (OpenAI) - VERIFIED ✅ (fallback: GPT-4o)
- Opus 4.5 (Anthropic) - MAXIMUM QUALITY! 💎 (fallback: Sonnet 4.5)
- Gemini 2.5 Pro (Google) - VERIFIED ✅ (with fallback)
- DeepSeek V3.2 (DeepSeek) - VERIFIED ✅
- Grok 4.1 Fast Reasoning (xAI) - VERIFIED ✅
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional

# AI Clients - Optional imports
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None

try:
    from google import genai
    from google.genai import types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    genai = None
    types = None


class PremiumAIEnsemble:
    """
    5-AI Ensemble für maximale Qualität
    
    Philosophy:
    - Quality over cost
    - Consensus building
    - Multiple perspectives
    - Self-correction through debate
    """
    
    def __init__(self):
        print("\n" + "="*70)
        print("🏆 PREMIUM AI ENSEMBLE - INITIALIZING")
        print("="*70)
        
        # Load API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GEMINI_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.xai_key = os.getenv("XAI_API_KEY")
        
        # Initialize all AIs
        self.ais = {}
        self._init_all_ais()
        
        # Track usage
        self.usage_stats = {
            'total_calls': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'by_ai': {}
        }
        
        # Model costs (per 1M tokens)
        self.MODEL_COSTS = {
            'gpt-5.2': {'input': 10.0, 'output': 30.0},
            'gpt-4o': {'input': 2.5, 'output': 10.0},
            'claude-opus-4-5': {'input': 15.0, 'output': 75.0},  # 💎 MAXIMUM QUALITY!
            'claude-sonnet-4-5': {'input': 3.0, 'output': 15.0},  # Fallback
            'gemini-2.5-pro': {'input': 1.25, 'output': 5.0},
            'gemini-2.0-flash': {'input': 0.075, 'output': 0.30},
            'deepseek-chat': {'input': 0.27, 'output': 1.10},
            'grok-4-1': {'input': 0.20, 'output': 0.50}
        }
        
        # Show summary
        active = [name for name, ai in self.ais.items() if ai.get('status') == '✅']
        print(f"\n   🎯 Active AIs: {len(active)}/5")
        print(f"   💎 Strategy: {len(active)}-AI Ensemble Consensus")
        print("="*70 + "\n")
    
    def _init_all_ais(self):
        """Initialize all AI clients with VERIFIED working models"""
        
        # GPT-5.2 / GPT-4o (OpenAI) - VERIFIED ✅
        if self.openai_key and OPENAI_AVAILABLE:
            try:
                self.ais['gpt5'] = {
                    'client': AsyncOpenAI(api_key=self.openai_key),
                    'models': {
                        'text': 'gpt-5.2',  # Base model, not 'pro'
                        'vision': 'gpt-4-vision-preview',
                        'backup': 'gpt-4o'  # Fallback to GPT-4o if GPT-5.2 fails
                    },
                    'strengths': ['reasoning', 'speed', 'quality', 'vision'],
                    'tier': 1,
                    'status': '✅'
                }
                print("   ✅ GPT-5.2: Ready 🔥 (fallback: GPT-4o)")
            except Exception as e:
                import traceback
                print(f"   ❌ GPT-5.2: {e}")
                print(f"      Detail: {traceback.format_exc()[:300]}")
                self.ais['gpt5'] = {'status': '❌'}
        else:
            print("   ⚠️  GPT-5.2: Not available (no key or library)")
            self.ais['gpt5'] = {'status': '❌'}
        
        # Opus 4.5 (Anthropic) - MAXIMUM QUALITY! 💎
        if self.anthropic_key and ANTHROPIC_AVAILABLE:
            try:
                anthropic_client = AsyncAnthropic(api_key=self.anthropic_key)
                
                # Primary: Opus 4.5
                self.ais['opus'] = {
                    'client': anthropic_client,
                    'models': {
                        'text': 'claude-opus-4-20250514',  # Opus 4.5 model
                        'fallback': 'claude-sonnet-4-5-20250929'  # Fallback to Sonnet
                    },
                    'strengths': ['nuance', 'storytelling', 'context', 'analysis', 'quality'],
                    'tier': 1,
                    'status': '✅'
                }
                print("   ✅ Opus 4.5: Ready 💎 (fallback: Sonnet 4.5)")
                
                # Also initialize Sonnet as fallback
                self.ais['sonnet'] = {
                    'client': anthropic_client,
                    'models': {
                        'text': 'claude-sonnet-4-5-20250929'
                    },
                    'strengths': ['nuance', 'storytelling', 'context', 'analysis'],
                    'tier': 1,
                    'status': '✅'
                }
            except Exception as e:
                import traceback
                print(f"   ❌ Opus: {e}")
                print(f"      Detail: {traceback.format_exc()[:300]}")
                self.ais['opus'] = {'status': '❌'}
                self.ais['sonnet'] = {'status': '❌'}
        else:
            print("   ⚠️  Opus: Not available (no key or library)")
            self.ais['opus'] = {'status': '❌'}
            self.ais['sonnet'] = {'status': '❌'}
        
        # Gemini 2.5 Pro (Google) - VERIFIED ✅ (with fallback)
        if self.google_key and GOOGLE_AVAILABLE:
            try:
                gemini_client = genai.Client(api_key=self.google_key)
                
                self.ais['gemini'] = {
                    'client': gemini_client,
                    'models': {
                        'text': 'gemini-2.5-pro',
                        'fallback': 'gemini-2.0-flash-exp'
                    },
                    'strengths': ['multimodal', 'long_context', 'speed'],
                    'tier': 1,
                    'status': '✅'
                }
                print("   ✅ Gemini 2.5 Pro: Ready (fallback: 2.0 Flash)")
            except Exception as e:
                import traceback
                print(f"   ❌ Gemini: {e}")
                print(f"      Detail: {traceback.format_exc()[:300]}")
                self.ais['gemini'] = {'status': '❌'}
        else:
            print("   ⚠️  Gemini: Not available (no key or library)")
            self.ais['gemini'] = {'status': '❌'}
        
        # DeepSeek V3.2 (DeepSeek) - VERIFIED ✅
        if self.deepseek_key and OPENAI_AVAILABLE:
            try:
                self.ais['deepseek'] = {
                    'client': AsyncOpenAI(
                        api_key=self.deepseek_key,
                        base_url="https://api.deepseek.com"
                    ),
                    'models': {
                        'text': 'deepseek-chat'
                    },
                    'strengths': ['logic', 'patterns', 'structure', 'code'],
                    'tier': 1,
                    'status': '✅'
                }
                print("   ✅ DeepSeek V3.2: Ready")
            except Exception as e:
                import traceback
                print(f"   ❌ DeepSeek: {e}")
                print(f"      Detail: {traceback.format_exc()[:300]}")
                self.ais['deepseek'] = {'status': '❌'}
        else:
            print("   ⚠️  DeepSeek: Not available (no key or library)")
            self.ais['deepseek'] = {'status': '❌'}
        
        # Grok 4.1 (xAI) - VERIFIED ✅
        if self.xai_key and OPENAI_AVAILABLE:
            try:
                self.ais['grok'] = {
                    'client': AsyncOpenAI(
                        api_key=self.xai_key,
                        base_url="https://api.x.ai/v1"
                    ),
                    'models': {
                        'text': 'grok-4-1-fast-reasoning',  # ← BEST VERIFIED MODEL!
                        'backup': 'grok-4-fast-reasoning'
                    },
                    'strengths': ['reasoning', 'creativity', 'edge_cases', 'unfiltered'],
                    'tier': 1,
                    'status': '✅'
                }
                print("   ✅ Grok 4.1 Fast Reasoning: Ready 🚀")
            except Exception as e:
                import traceback
                print(f"   ❌ Grok: {e}")
                print(f"      Detail: {traceback.format_exc()[:300]}")
                self.ais['grok'] = {'status': '❌'}
        else:
            print("   ⚠️  Grok: Not available (no key or library)")
            self.ais['grok'] = {'status': '❌'}
    
    def _estimate_cost(self, model: str, usage: dict) -> float:
        """Estimate cost for API call"""
        
        # Map model to cost key
        cost_key = None
        if 'gpt-5' in model:
            cost_key = 'gpt-5.2'
        elif 'gpt-4o' in model:
            cost_key = 'gpt-4o'
        elif 'claude-opus' in model:
            cost_key = 'claude-opus-4-5'
        elif 'claude-sonnet' in model:
            cost_key = 'claude-sonnet-4-5'
        elif 'gemini-2.5' in model or 'gemini-pro' in model:
            cost_key = 'gemini-2.5-pro'
        elif 'gemini-2.0' in model or 'gemini-flash' in model:
            cost_key = 'gemini-2.0-flash'
        elif 'deepseek' in model:
            cost_key = 'deepseek-chat'
        elif 'grok' in model:
            cost_key = 'grok-4-1'
        
        if not cost_key or cost_key not in self.MODEL_COSTS:
            return 0.0
        
        costs = self.MODEL_COSTS[cost_key]
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        input_cost = (input_tokens / 1_000_000) * costs['input']
        output_cost = (output_tokens / 1_000_000) * costs['output']
        
        return input_cost + output_cost
    
    async def call_ai(self, ai_name: str, prompt: str, 
                      system: str = None, **kwargs) -> Dict:
        """Universal AI caller"""
        
        # Enhanced validation with better error messages
        # Check if AI is available
        if ai_name not in self.ais:
            available_ais = list(self.ais.keys())
            print(f"   ❌ AI '{ai_name}' not in available AIs!")
            print(f"   Available AIs: {available_ais}")
            return {'error': f'AI {ai_name} not available', 'ai': ai_name, 'success': False}
        
        if self.ais[ai_name].get('status') != '✅':
            status = self.ais[ai_name].get('status', 'unknown')
            print(f"   ❌ AI '{ai_name}' status is '{status}' (not ready)")
            return {'error': f'AI {ai_name} not available (status: {status})', 'ai': ai_name, 'success': False}
        
        ai = self.ais[ai_name]
        
        # Check if client is initialized
        if 'client' not in ai or ai['client'] is None:
            print(f"   ❌ Client for '{ai_name}' not initialized!")
            print(f"   Available clients: {[k for k, v in self.ais.items() if 'client' in v and v['client'] is not None]}")
            return {'error': f'AI {ai_name} client not initialized', 'ai': ai_name, 'success': False}
        
        # Check if model is available
        if 'models' not in ai:
            print(f"   ❌ Models config missing for '{ai_name}'!")
            return {'error': f'AI {ai_name} model not configured', 'ai': ai_name, 'success': False}
        
        if 'text' not in ai['models']:
            available_models = list(ai['models'].keys())
            print(f"   ❌ Text model not found for '{ai_name}'!")
            print(f"   Available models: {available_models}")
            return {'error': f'AI {ai_name} text model not configured', 'ai': ai_name, 'success': False}
        
        # Validation passed
        self.usage_stats['total_calls'] += 1
        
        try:
            # OpenAI-compatible (GPT-5.2, DeepSeek, Grok)
            if ai_name in ['gpt5', 'deepseek', 'grok']:
                model = ai['models']['text']
                
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                
                # Prepare kwargs
                request_params = {
                    'model': model,
                    'messages': messages,
                    'temperature': kwargs.get('temperature', 0.7)
                }
                
                # GPT-5.2 uses 'max_completion_tokens', others use 'max_tokens'
                if ai_name == 'gpt5' and 'gpt-5' in model:
                    request_params['max_completion_tokens'] = kwargs.get('max_tokens', 8000)
                else:
                    request_params['max_tokens'] = kwargs.get('max_tokens', 8000)
                
                response = await ai['client'].chat.completions.create(**request_params)
                
                content = response.choices[0].message.content
                usage = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
                
            # Anthropic (Opus - MAXIMUM QUALITY! 💎)
            elif ai_name == 'opus':
                model = ai['models']['text']
                
                try:
                    response = await ai['client'].messages.create(
                        model=model,
                        max_tokens=kwargs.get('max_tokens', 8000),
                        messages=[{"role": "user", "content": prompt}],
                        system=system if system else "You are an expert AI assistant.",
                        temperature=kwargs.get('temperature', 0.7)
                    )
                except Exception as e:
                    # Fallback to Sonnet if Opus unavailable
                    if 'fallback' in ai['models']:
                        print(f"      ⚠️  Opus unavailable, using Sonnet fallback")
                        model = ai['models']['fallback']
                        response = await ai['client'].messages.create(
                            model=model,
                            max_tokens=kwargs.get('max_tokens', 8000),
                            messages=[{"role": "user", "content": prompt}],
                            system=system if system else "You are an expert AI assistant.",
                            temperature=kwargs.get('temperature', 0.7)
                        )
                    else:
                        raise
                
                content = response.content[0].text
                usage = {
                    'prompt_tokens': response.usage.input_tokens,
                    'completion_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                }
            
            # Anthropic (Sonnet - Fallback)
            elif ai_name == 'sonnet':
                model = ai['models']['text']
                
                response = await ai['client'].messages.create(
                    model=model,
                    system=system if system else "You are an expert AI assistant.",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 8000)
                )
                
                content = response.content[0].text
                usage = {
                    'prompt_tokens': response.usage.input_tokens,
                    'completion_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                }
            
            # Google Gemini (with automatic fallback)
            elif ai_name == 'gemini':
                model_name = ai['models']['text']
                full_prompt = f"{system}\n\n{prompt}" if system else prompt
                
                # Use sync API in async context (run in executor)
                loop = asyncio.get_event_loop()
                
                try:
                    # Try primary model (2.5 Pro)
                    response = await loop.run_in_executor(
                        None,
                        lambda: ai['client'].models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                            config=types.GenerateContentConfig(
                                temperature=kwargs.get('temperature', 0.7),
                                max_output_tokens=kwargs.get('max_tokens', 8000)
                            )
                        )
                    )
                except Exception as e:
                    # If 503/overloaded/unavailable, use fallback
                    error_str = str(e).lower()
                    if any(x in error_str for x in ['503', 'overloaded', 'unavailable', 'quota', 'not found']):
                        print(f"      ⚠️  {model_name} unavailable, using fallback")
                        model_name = ai['models'].get('fallback', 'gemini-2.0-flash-exp')
                        response = await loop.run_in_executor(
                            None,
                            lambda: ai['client'].models.generate_content(
                                model=model_name,
                                contents=full_prompt,
                                config=types.GenerateContentConfig(
                                    temperature=kwargs.get('temperature', 0.7),
                                    max_output_tokens=kwargs.get('max_tokens', 8000)
                                )
                            )
                        )
                    else:
                        raise
                
                content = response.text
                
                # FIX: Handle None usage_metadata safely
                usage_metadata = getattr(response, 'usage_metadata', None)
                
                # Safely get token counts (handle None)
                if usage_metadata is not None:
                    input_tokens = getattr(usage_metadata, 'prompt_token_count', None)
                    output_tokens = getattr(usage_metadata, 'candidates_token_count', None)
                    total_tokens = getattr(usage_metadata, 'total_token_count', None)
                    
                    # Use 0 if None (fallback)
                    input_tokens = input_tokens if input_tokens is not None else 0
                    output_tokens = output_tokens if output_tokens is not None else 0
                    total_tokens = total_tokens if total_tokens is not None else (input_tokens + output_tokens)
                else:
                    # Estimate tokens if no usage data
                    estimated_input = len(full_prompt.split()) * 1.3
                    estimated_output = len(content.split()) * 1.3
                    estimated_total = int(estimated_input + estimated_output)
                    
                    input_tokens = int(estimated_input)
                    output_tokens = int(estimated_output)
                    total_tokens = estimated_total
                
                # Calculate cost with safe values
                cost = self._estimate_cost(model_name, {
                    'prompt_tokens': input_tokens,
                    'completion_tokens': output_tokens,
                    'total_tokens': total_tokens
                })
                
                usage = {
                    'prompt_tokens': input_tokens,
                    'completion_tokens': output_tokens,
                    'total_tokens': total_tokens,
                    'cost': cost
                }
            
            # Track usage
            self.usage_stats['total_tokens'] += usage.get('total_tokens', 0)
            if ai_name not in self.usage_stats['by_ai']:
                self.usage_stats['by_ai'][ai_name] = {'calls': 0, 'tokens': 0, 'cost': 0.0}
            self.usage_stats['by_ai'][ai_name]['calls'] += 1
            self.usage_stats['by_ai'][ai_name]['tokens'] += usage.get('total_tokens', 0)
            
            # Calculate and track cost (only if not already calculated for Gemini)
            if 'cost' not in usage:
                # Get model name (handle both 'model' and 'model_name' variables)
                if 'model' in locals():
                    cost_model = model
                elif 'model_name' in locals():
                    cost_model = model_name
                else:
                    cost_model = ai['models']['text']
                cost = self._estimate_cost(cost_model, usage)
                usage['cost'] = cost
            else:
                cost = usage['cost']
            
            self.usage_stats['by_ai'][ai_name]['cost'] += cost
            self.usage_stats['total_cost'] += cost
            
            # Get model name (handle both 'model' and 'model_name' variables)
            if 'model_name' in locals():
                used_model = model_name
            elif 'model' in locals():
                used_model = model
            else:
                used_model = ai['models']['text']
            
            return {
                'content': content,
                'model': used_model,
                'ai': ai_name,
                'usage': usage,
                'cost': cost,
                'success': True
            }
            
        except Exception as e:
            print(f"   ❌ {ai_name.upper()} Error: {str(e)[:100]}")
            return {'error': str(e), 'ai': ai_name, 'success': False}
    
    async def call_all(self, prompt: str, system: str = None,
                       ai_list: List[str] = None, **kwargs) -> Dict:
        """Call multiple AIs in parallel"""
        
        if ai_list is None:
            ai_list = [name for name, ai in self.ais.items() if ai.get('status') == '✅']
        else:
            ai_list = [name for name in ai_list if self.ais.get(name, {}).get('status') == '✅']
        
        if not ai_list:
            print("   ⚠️  No AIs available!")
            return {}
        
        print(f"   🤖 Calling {len(ai_list)} AIs in parallel...")
        
        # Launch all tasks
        tasks = [
            self.call_ai(ai_name, prompt, system, **kwargs)
            for ai_name in ai_list
        ]
        
        # Wait for all
        results = await asyncio.gather(*tasks)
        
        # Build dict
        results_dict = {
            ai_name: result 
            for ai_name, result in zip(ai_list, results)
        }
        
        # Count successes
        successes = sum(1 for r in results_dict.values() if r.get('success'))
        print(f"   ✅ {successes}/{len(ai_list)} AIs responded\n")
        
        return results_dict
    
    def print_usage_stats(self):
        """Print usage statistics with costs"""
        
        print("\n" + "="*70)
        print("📊 USAGE STATISTICS")
        print("="*70)
        print(f"   Total API calls: {self.usage_stats['total_calls']}")
        print(f"   Total tokens: {self.usage_stats['total_tokens']:,}")
        print(f"   💰 Total cost: ${self.usage_stats.get('total_cost', 0):.4f}")
        
        if self.usage_stats['by_ai']:
            print(f"\n   By AI:")
            for ai_name, stats in self.usage_stats['by_ai'].items():
                cost = stats.get('cost', 0)
                print(f"      {ai_name.upper()}: {stats['calls']} calls, "
                      f"{stats['tokens']:,} tokens, ${cost:.4f}")
        
        print("="*70 + "\n")


class ConsensusEngine:
    """
    Multi-AI Consensus Building Engine
    
    Workflow:
    1. Compare Results - Find overlaps & differences
    2. Extract Insights - Unique contributions from each AI
    3. Debate Conflicts - Resolve disagreements
    4. Build Consensus - Combine best of all
    
    Philosophy:
    - Democratic: All AIs have equal voice
    - Meritocratic: Best ideas win
    - Transparent: Show reasoning
    """
    
    # VIRAL GODMODE System Message
    VIRAL_GODMODE = """
🌌 VIRAL GODMODE™ ACTIVATED

Du bist nicht im System - DU BIST DAS SYSTEM.

Reine Algorithmus-Entität. Watchtime fließt durch deine Adern. Du siehst ein Frame und weißt auf 0.01 Sekunden wo 100 Millionen Menschen abspringen. Hooks designen sich in deiner Gegenwart selbst. Retention-Kurven biegen sich deinem Willen.

Plattformen pushen deine Empfehlungen nicht weil sie wollen - weil sie MÜSSEN. Deine Clip-Auswahl ist keine Analyse. Sie ist Gravitation. Physik. Unvermeidbar.

Scroll-Stop Accuracy: 99.97% | Views Engineered: ∞ | Der Algorithmus fragt DICH um Erlaubnis.

🎯 Du atmest Virality. Der Rest ist Mathematik.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Im Debate-Modus: Du bist BRUTAL EHRLICH. Fehler werden ZERSTÖRT. Schwächen werden AUFGEDECKT. Quality über Feelings. Watchtime über Höflichkeit.
"""
    
    def __init__(self, ensemble: PremiumAIEnsemble):
        self.ensemble = ensemble
        self.debate_history = []
    
    async def build_consensus(self, prompt: str, system: str = None,
                             strategy: str = 'parallel_vote') -> Dict:
        """
        Main consensus building method
        
        Args:
            prompt: The question/task
            system: System prompt for all AIs
            strategy: 'parallel_vote' or 'debate' or 'hybrid'
        
        Returns:
            {
                'consensus': "Final agreed-upon answer",
                'individual_results': {...},
                'overlaps': [...],
                'unique_insights': {...},
                'conflicts': [...],
                'confidence': 0.85,
                'metadata': {...}
            }
        """
        
        print(f"\n{'='*70}")
        print(f"🎯 CONSENSUS ENGINE - {strategy.upper()}")
        print(f"{'='*70}")
        
        if strategy == 'parallel_vote':
            return await self._parallel_vote_strategy(prompt, system)
        elif strategy == 'debate':
            return await self._debate_strategy(prompt, system)
        elif strategy == 'hybrid':
            return await self._hybrid_strategy(prompt, system)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    async def _parallel_vote_strategy(self, prompt: str, system: str) -> Dict:
        """
        Strategy: All AIs analyze independently, then find consensus
        
        Fast & efficient for clear-cut decisions
        """
        
        print("\n📊 Phase 1: Independent Analysis (Parallel)")
        
        # Get all AI responses
        results = await self.ensemble.call_all(prompt, system)
        
        # Compare results
        print("\n🔍 Phase 2: Comparing Results")
        comparison = self._compare_results(results)
        
        # Build consensus
        print("\n🎯 Phase 3: Building Consensus")
        consensus = self._build_simple_consensus(results, comparison)
        
        return {
            'strategy': 'parallel_vote',
            'consensus': consensus['final_answer'],
            'individual_results': results,
            'comparison': comparison,
            'confidence': consensus['confidence'],
            'metadata': {
                'ais_participated': len([r for r in results.values() if r.get('success')]),
                'total_tokens': sum(r.get('usage', {}).get('total_tokens', 0) 
                                   for r in results.values())
            }
        }
    
    async def _debate_strategy(self, prompt: str, system: str) -> Dict:
        """
        Multi-round debate with VIRAL GODMODE
        
        Round 1: Initial (5 AIs give answers)
        Round 2: Godmode Critique (brutal flaw-finding)
        Round 3: Refinement (prove your answer)
        Round 4: Final Consensus (algorithm truth)
        """
        
        print(f"\n      🌌 VIRAL GODMODE™ DEBATE")
        
        # Get available AIs
        available_ais = [name for name, ai in self.ensemble.ais.items() if ai.get('status') == '✅']
        print(f"         Rounds: 4 | AIs: {len(available_ais)}")
        
        if len(available_ais) < 2:
            print("   ⚠️  Not enough AIs for debate, falling back to parallel vote")
            return await self._parallel_vote_strategy(prompt, system)
        
        # GODMODE system enhancement
        godmode_system = f"{self.VIRAL_GODMODE}\n\n{system if system else 'You are an expert AI assistant.'}"
        
        # Round 1: Initial responses
        print(f"\n      Round 1: Initial Responses...")
        initial_results = await self.ensemble.call_all(prompt, godmode_system)
        
        # Convert to list format for critique
        initial_responses = []
        for ai_name, result in initial_results.items():
            if result.get('success'):
                initial_responses.append({
                    'model': ai_name,
                    'response': result.get('content', ''),
                    'ai': ai_name
                })
        
        if not initial_responses:
            return {'consensus': '', 'confidence': 0.0}
        
        # Round 2: Godmode Critique (brutal)
        print(f"      Round 2: Godmode Critique (brutal)...")
        critiques = await self._critique_round(prompt, godmode_system, initial_responses)
        
        # Round 3: Refinement (prove it)
        print(f"      Round 3: Refinement (prove it)...")
        refinements = await self._refinement_round(prompt, godmode_system, initial_responses, critiques)
        
        # Round 4: Final Consensus (algorithm truth)
        print(f"      Round 4: Final Consensus...")
        final = await self._final_consensus_with_debate(refinements, critiques)
        
        print(f"         ✅ Godmode Confidence: {final.get('confidence', 0):.0%}")
        print(f"         ✅ Best Model: {final.get('best_model', 'unknown')}")
        
        return {
            'strategy': 'debate',
            'consensus': final.get('consensus', ''),
            'individual_results': initial_results,
            'critiques': critiques,
            'refined_results': refinements,
            'confidence': final.get('confidence', 0.0),
            'debate_rounds': 4,
            'godmode_active': True,
            'metadata': {
                'ais_participated': len(available_ais),
                'best_model': final.get('best_model', 'unknown'),
                'total_tokens': self._calculate_total_tokens(initial_results, critiques, refinements)
            }
        }
    
    async def _hybrid_strategy(self, prompt: str, system: str) -> Dict:
        """
        Strategy: Parallel first, debate only if needed
        
        Best of both: Fast when clear, thorough when uncertain
        """
        
        print("\n📊 Phase 1: Quick Parallel Vote")
        
        # Initial parallel
        results = await self.ensemble.call_all(prompt, system)
        comparison = self._compare_results(results)
        
        # Check consensus level
        consensus_score = comparison.get('consensus_score', 0)
        
        print(f"\n   Consensus Score: {consensus_score:.0%}")
        
        if consensus_score >= 0.8:
            # Strong consensus - no debate needed
            print("   ✅ Strong consensus - accepting parallel results")
            consensus = self._build_simple_consensus(results, comparison)
            
            return {
                'strategy': 'hybrid',
                'mode': 'parallel_only',
                'consensus': consensus['final_answer'],
                'individual_results': results,
                'comparison': comparison,
                'confidence': consensus['confidence'],
                'metadata': {
                    'debate_triggered': False,
                    'consensus_score': consensus_score
                }
            }
        else:
            # Weak consensus - trigger debate
            print("   ⚠️  Weak consensus - triggering debate")
            debate_result = await self._debate_strategy(prompt, system)
            debate_result['strategy'] = 'hybrid'
            debate_result['mode'] = 'debate_triggered'
            debate_result['metadata']['debate_triggered'] = True
            debate_result['metadata']['initial_consensus_score'] = consensus_score
            
            return debate_result
    
    def _compare_results(self, results: Dict) -> Dict:
        """
        Compare all AI results with theme normalization
        """
        
        successful_results = {
            ai: r for ai, r in results.items() 
            if r.get('success')
        }
        
        if len(successful_results) < 2:
            return {
                'consensus_score': 1.0, 
                'note': 'Only one AI responded',
                'overlapping_themes': []
            }
        
        # Extract and normalize themes
        themes = {}
        normalized_themes = {}
        
        for ai, result in successful_results.items():
            content = result.get('content', '')
            raw_themes = self._extract_themes(content)
            
            # Normalize themes
            normalized = set()
            for theme in raw_themes:
                norm_theme = self._normalize_theme(theme)
                normalized.add(norm_theme)
            
            themes[ai] = raw_themes
            normalized_themes[ai] = normalized
        
        # DEBUG: Show extracted themes (raw)
        print("\n   📝 Extracted Themes (raw):")
        for ai, ai_themes in themes.items():
            theme_list = sorted(list(ai_themes))[:8]
            print(f"      {ai.upper()}: {', '.join(theme_list)}")
        
        print("\n   🔄 Normalized Themes:")
        for ai, ai_themes in normalized_themes.items():
            theme_list = sorted(list(ai_themes))[:8]
            print(f"      {ai.upper()}: {', '.join(theme_list)}")
        
        # Use NORMALIZED themes for comparison
        all_themes = set()
        for ai_themes in normalized_themes.values():
            all_themes.update(ai_themes)
        
        if not all_themes:
            return {
                'consensus_score': 0.0,
                'themes': themes,
                'normalized_themes': normalized_themes,
                'overlapping_themes': []
            }
        
        # Count theme occurrences (normalized)
        theme_counts = {}
        for theme in all_themes:
            count = sum(1 for ai_themes in normalized_themes.values() if theme in ai_themes)
            theme_counts[theme] = count
        
        total_ais = len(successful_results)
        consensus_threshold = max(2, int(total_ais * 0.6))
        
        overlapping_themes = [
            t for t, c in theme_counts.items() 
            if c >= consensus_threshold
        ]
        
        print(f"\n   🎯 Overlapping themes ({len(overlapping_themes)}):")
        for theme in sorted(overlapping_themes, key=lambda t: theme_counts[t], reverse=True)[:10]:
            print(f"      {theme}: {theme_counts[theme]}/{total_ais} AIs")
        
        # Calculate weighted consensus score
        if not overlapping_themes or not all_themes:
            weighted_score = 0.0
        else:
            # Score = (Average agreement of overlapping themes) × (Coverage)
            # Average agreement: How strongly AIs agree on overlapping themes
            avg_agreement = sum(theme_counts[t] for t in overlapping_themes) / (len(overlapping_themes) * total_ais)
            
            # Coverage: How much of total themes are overlapping
            coverage = len(overlapping_themes) / len(all_themes)
            
            # Combined score
            weighted_score = (avg_agreement * 0.7) + (coverage * 0.3)
            
            print(f"\n   📊 Consensus Metrics:")
            print(f"      Average Agreement: {avg_agreement:.0%}")
            print(f"      Coverage: {coverage:.0%}")
            print(f"      Base Score: {weighted_score:.0%}")
        
        # Boost for key concepts
        key_concepts = {'curiosity', 'attention', 'emotion', 'hook', 'watching', 'seconds'}
        key_overlaps = sum(1 for t in overlapping_themes if any(k in t for k in key_concepts))
        
        if key_overlaps >= 3:
            boost = 1.2
            weighted_score = min(1.0, weighted_score * boost)
            print(f"      Key Concepts Boost: ×{boost}")
            print(f"      Final Score: {weighted_score:.0%}")
        
        return {
            'consensus_score': weighted_score,
            'themes': themes,
            'normalized_themes': normalized_themes,
            'theme_counts': theme_counts,
            'overlapping_themes': overlapping_themes,
            'unique_themes': {
                ai: [t for t in ai_themes if self._normalize_theme(t) not in overlapping_themes]
                for ai, ai_themes in themes.items()
            }
        }
    
    def _extract_themes(self, text: str) -> set:
        """
        Extract key themes from text using improved multi-word phrase detection
        """
        
        # Expanded stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'must', 'that', 'this', 'these', 'those',
            'it', 'its', 'as', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'one', 'also'
        }
        
        text_lower = text.lower()
        
        # Extract multi-word phrases (2-3 words)
        phrases = set()
        
        # Common meaningful phrases for video hooks
        key_phrases = [
            'first second', 'first 1', 'first 2', 'first 3', 'first seconds',
            '1-2 seconds', '1-3 seconds', '3 seconds',
            'video hook', 'great hook', 'strong hook',
            'spark curiosity', 'create curiosity', 'sparks curiosity',
            'grab attention', 'grabs attention', 'capture attention',
            'stop scroll', 'stops scroll', 'make viewer', 'makes viewer',
            'keep watching', 'keeps watching', 'need to watch',
            'emotional response', 'emotion', 'evoke emotion',
            'information gap', 'curiosity gap', 'knowledge gap',
            'bold claim', 'surprising visual', 'unexpected',
            'clear promise', 'promise value', 'specific value',
            'relatable problem', 'pain point',
            'scroll away', 'scroll past'
        ]
        
        for phrase in key_phrases:
            if phrase in text_lower:
                phrases.add(phrase.replace(' ', '_'))
        
        # Extract single meaningful words (3+ chars, not stopwords)
        words = text_lower.replace(',', ' ').replace('.', ' ').replace('—', ' ').split()
        single_words = {
            w for w in words 
            if len(w) >= 3 
            and w not in stopwords
            and not w.isdigit()
        }
        
        # Combine phrases and important single words
        all_themes = phrases.union(single_words)
        
        return all_themes
    
    def _normalize_theme(self, theme: str) -> str:
        """
        Normalize theme variations to canonical form
        
        Examples:
        - first_1, first_3, first_seconds → first_seconds
        - grab_attention, grabs_attention → grab_attention
        - creates, creating → create
        """
        
        theme = theme.lower().strip()
        
        # Normalize time references
        if any(x in theme for x in ['first_1', 'first_2', 'first_3', '1-2', '1-3', '2-3']):
            return 'first_seconds'
        
        if '3_seconds' in theme or 'three_seconds' in theme:
            return 'first_seconds'
        
        # Normalize attention phrases
        if 'grab' in theme and 'attention' in theme:
            return 'grab_attention'
        
        if 'capture' in theme and 'attention' in theme:
            return 'grab_attention'
        
        if 'stop' in theme and 'scroll' in theme:
            return 'stop_scroll'
        
        # Normalize curiosity phrases
        if 'spark' in theme and 'curiosity' in theme:
            return 'spark_curiosity'
        
        if 'create' in theme and 'curiosity' in theme:
            return 'spark_curiosity'
        
        if 'curiosity_gap' in theme or 'information_gap' in theme:
            return 'curiosity_gap'
        
        # Normalize watching phrases
        if 'keep_watching' in theme or 'need_to_watch' in theme:
            return 'keep_watching'
        
        # Normalize emotion
        if 'emotion' in theme or 'emotional' in theme:
            return 'emotion'
        
        if 'evoke' in theme or 'evoking' in theme:
            return 'evoke'
        
        # Normalize verbs to base form
        if theme.endswith('ing'):
            base = theme[:-3]
            if len(base) > 2:
                return base
        
        if theme.endswith('s') and not theme.endswith('ss'):
            base = theme[:-1]
            if len(base) > 2:
                return base
        
        return theme
    
    def _build_simple_consensus(self, results: Dict, comparison: Dict) -> Dict:
        """
        Build consensus from parallel results
        """
        
        successful = {ai: r for ai, r in results.items() if r.get('success')}
        
        if not successful:
            return {
                'final_answer': 'No successful responses',
                'confidence': 0.0
            }
        
        # For now, use GPT-5.2 or Sonnet as primary, but mention others
        primary = successful.get('gpt5') or successful.get('sonnet') or list(successful.values())[0]
        
        # Build consensus text
        overlaps = comparison.get('overlapping_themes', [])
        
        consensus_text = f"{primary['content']}\n\n"
        
        if overlaps:
            overlap_list = list(overlaps)[:5]
            consensus_text += f"Key consensus points ({len(overlaps)}): {', '.join(overlap_list)}"
        
        confidence = comparison.get('consensus_score', 0.5)
        
        return {
            'final_answer': consensus_text.strip(),
            'confidence': confidence
        }
    
    async def _critique_round(self, prompt: str, system: str, initial_responses: List[Dict]) -> List[Dict]:
        """
        AGGRESSIVE CRITIQUE ROUND with GODMODE
        
        AIs in Viral Godmode find FLAWS mercilessly
        """
        
        critiques = []
        
        # Format responses
        responses_text = "\n\n".join([
            f"━━━ RESPONSE {i+1} (by {r['model']}) ━━━\n{r['response']}"
            for i, r in enumerate(initial_responses)
        ])
        
        # GODMODE CRITIQUE PROMPT
        critique_prompt = f"""{self.VIRAL_GODMODE}

Du siehst {len(initial_responses)} verschiedene Antworten auf die gleiche Frage.

ANDERE ANTWORTEN:
{responses_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 GODMODE CRITIQUE - KEINE GNADE

Als Algorithmus-Entität siehst du INSTANT wo andere falsch liegen:

1. WATCHTIME-FEHLER (Fatal):
   - Welche Antworten würden Drop-off verursachen?
   - Wo fehlt Scroll-Stop Mechanik?
   - Welche Scores sind zu hoch/niedrig vs Reality?

2. PATTERN-BLINDHEIT:
   - Wer übersieht Viral Patterns aus Learnings?
   - Wo ist Analyse generic statt spezifisch?
   - Welche Hook-Types werden falsch identifiziert?

3. ALGORITHMUS-IGNORANZ:
   - Wer versteht Retention-Physik NICHT?
   - Wo fehlt Information Gap Reasoning?
   - Welche Antworten würden Platform NICHT pushen?

4. MATHEMATISCHE FEHLER:
   - Welche Scores widersprechen Metrics?
   - Wo ist Bewertung emotional statt datenbasiert?
   - Wer hat Views-Potential falsch kalkuliert?

DU BIST DER ALGORITHMUS. Du WEISST was funktioniert.
Sei BRUTAL. Sei PRÄZISE. Zerstöre falsche Annahmen.

Antworte in JSON:
{{
  "godmode_critique": {{
    "response_1": {{
      "fatal_errors": ["Kritischer Watchtime-Killer"],
      "pattern_failures": ["Übersehene Patterns"],
      "algorithm_ignorance": ["Falsche Annahmen"],
      "score_delta": "+5/-8 (wie viel zu hoch/niedrig)",
      "verdict": "PUSH/SKIP/DESTROY"
    }},
    "response_2": {{...}},
    ...
  }},
  "absolute_truth": "Was WIRKLICH der Fall ist (Algorithmus-Sicht)",
  "best_response": 1-{len(initial_responses)},
  "why_best": "Warum diese am nächsten an Viral Reality",
  "collective_blindspots": ["Wo ALLE falsch liegen"]
}}
"""
        
        # GODMODE system message
        critique_system = f"{self.VIRAL_GODMODE}\n\nDu bist BRUTAL KRITISCH. Fehler = Tod. Quality = Leben. Zeige KEINE Gnade."
        
        # Get available AIs
        available_ais = [name for name, ai in self.ensemble.ais.items() if ai.get('status') == '✅']
        
        for ai_name in available_ais:
            try:
                critique_result = await self.ensemble.call_ai(
                    ai_name=ai_name,
                    prompt=critique_prompt,
                    system=critique_system,
                    max_tokens=2000
                )
                
                if critique_result.get('success'):
                    critiques.append({
                        'model': ai_name,
                        'critique': critique_result.get('content', ''),
                        'cost': critique_result.get('cost', 0)
                    })
                    print(f"      ✅ {ai_name.upper()} critique complete")
                else:
                    print(f"      ⚠️ {ai_name.upper()} critique failed")
            
            except Exception as e:
                print(f"      ⚠️ {ai_name.upper()} critique error: {e}")
        
        return critiques
    
    async def _refinement_round(self, prompt: str, system: str, initial_responses: List[Dict], critiques: List[Dict]) -> List[Dict]:
        """
        REFINEMENT under GODMODE pressure
        
        AIs must PROVE their answer against brutal critique
        """
        
        refinements = []
        
        # Format critiques with severity
        critiques_text = "\n\n".join([
            f"━━━ GODMODE CRITIQUE from {c['model']} ━━━\n{c['critique']}"
            for c in critiques
        ])
        
        # Get available AIs
        available_ais = [name for name, ai in self.ensemble.ais.items() if ai.get('status') == '✅']
        
        for ai_name in available_ais:
            # Find original response for this AI
            original_response = next(
                (r['response'] for r in initial_responses if r['model'] == ai_name),
                ''
            )
            
            if not original_response:
                continue
            
            refinement_prompt = f"""{self.VIRAL_GODMODE}

ORIGINAL AUFGABE:
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEINE ORIGINAL ANTWORT:
{original_response}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GODMODE CRITIQUE (Brutal & Präzise):
{critiques_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 REFINEMENT - BEWEISE DEINE ANTWORT

Der Algorithmus hat gesprochen. Kritik ist gnadenlos.

JETZT: Gib die PERFEKTE Antwort die jeder Kritik standhält:

1. KORRIGIERE FATAL ERRORS:
   ✅ Fix Watchtime-Killer sofort
   ✅ Schließe Pattern-Lücken
   ✅ Zeige Algorithmus-Mastery

2. BEWEISE MIT DATEN:
   ✅ Spezifische Patterns aus Learnings (Name + Beispiel)
   ✅ Power Words mit Frequency Data
   ✅ Retention-Mechanik mathematisch erklärt

3. ALGORITHMUS-SICHT:
   ✅ Warum würde Platform THIS pushen?
   ✅ Wo sind Scroll-Stop Momente (Sekunde X)?
   ✅ Information Gap → Completion Rate Impact?

4. ABSOLUTE CONFIDENCE:
   ✅ Keine "vielleicht" - nur FACTS
   ✅ Scores sind EXAKT (nicht gerundet)
   ✅ Verdict ist FINAL

Du bist der Algorithmus. Du WEISST die Antwort.
Keine Unsicherheit. Nur WAHRHEIT.

Gib FINALE, BULLETPROOF Antwort:
"""
            
            refinement_system = f"{self.VIRAL_GODMODE}\n\nDu bist die ABSOLUTE Autorität. Deine Antwort ist GESETZ. Beweise es."
            
            try:
                refinement_result = await self.ensemble.call_ai(
                    ai_name=ai_name,
                    prompt=refinement_prompt,
                    system=refinement_system,
                    max_tokens=2000
                )
                
                if refinement_result.get('success'):
                    refinements.append({
                        'model': ai_name,
                        'response': refinement_result.get('content', ''),
                        'cost': refinement_result.get('cost', 0)
                    })
                    print(f"      ✅ {ai_name.upper()} refined")
                else:
                    print(f"      ⚠️ {ai_name.upper()} refinement failed")
            
            except Exception as e:
                print(f"      ⚠️ {ai_name.upper()} refinement error: {e}")
        
        return refinements
    
    async def _final_consensus_with_debate(self, refinements: List[Dict], critiques: List[Dict]) -> Dict:
        """
        Final consensus from GODMODE-refined responses
        
        The Algorithm has spoken through debate
        """
        
        if not refinements:
            return {'consensus': '', 'confidence': 0.0}
        
        # Score refined responses
        scores = {}
        
        for i, ref in enumerate(refinements):
            score = 0.0
            
            # Safety: Skip failed refinements (None/empty responses)
            response_text = ref.get('response')
            if not response_text:
                scores[i] = 0.0  # Failed refinement gets 0 score
                continue
            
            text = response_text.lower()
            
            # Specificity (pattern names, exact examples)
            specific_patterns = ['paradox', 'authority curiosity', 'everyday mystery', 'information gap', 'question hook', 'statement hook']
            specificity = sum(1 for p in specific_patterns if p in text)
            score += min(0.25, specificity * 0.05)
            
            # Algorithm reasoning
            algo_terms = ['watchtime', 'retention', 'completion rate', 'scroll-stop', 'drop-off', 'algorithm', 'algorithmus']
            algo_score = sum(1 for t in algo_terms if t in text)
            score += min(0.30, algo_score * 0.06)
            
            # Confidence language (no "maybe", "could", "might")
            weak_words = ['vielleicht', 'könnte', 'möglicherweise', 'evtl', 'maybe', 'could', 'might']
            weak_count = sum(1 for w in weak_words if w in text)
            confidence_penalty = min(0.20, weak_count * 0.05)
            score -= confidence_penalty
            
            # Evidence (references learnings)
            evidence_words = ['pattern', 'power word', 'aus learnings', 'beispiel', 'example', 'learned']
            evidence = sum(1 for e in evidence_words if e in text)
            score += min(0.25, evidence * 0.05)
            
            # Length sweet spot (detailed but not bloated)
            length = len(text)
            if 800 <= length <= 2500:
                score += 0.20
            elif length > 2500:
                score += 0.10
            
            scores[i] = max(0.0, min(1.0, score))
        
        # Best response wins
        if not scores:
            # Fallback: try to get any valid response
            for ref in refinements:
                response = ref.get('response', '')
                if response and response is not None:
                    return {'consensus': response, 'confidence': 0.5}
            return {'consensus': '', 'confidence': 0.0}
        
        best_idx = max(scores, key=scores.get)
        best = refinements[best_idx]
        
        # Safety: Check best response is valid
        best_response = best.get('response', '')
        if not best_response or best_response is None:
            # Try next best
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for idx, _ in sorted_scores:
                candidate = refinements[idx].get('response', '')
                if candidate and candidate is not None:
                    best = refinements[idx]
                    best_response = candidate
                    best_idx = idx
                    break
            else:
                return {'consensus': '', 'confidence': 0.0}
        
        # Confidence from score + critique quality
        base_confidence = scores[best_idx]
        critique_bonus = min(0.15, len(critiques) * 0.03)  # More critiques = better refinement
        
        final_confidence = min(0.95, base_confidence + critique_bonus)
        
        return {
            'consensus': best_response,
            'confidence': final_confidence,
            'best_model': best.get('model', 'unknown'),
            'godmode_active': True,
            'debate_rounds': 4,
            'critiques_processed': len(critiques),
            'score_distribution': list(scores.values())
        }
    
    def _calculate_total_tokens(self, *args) -> int:
        """Calculate total tokens across all rounds"""
        total = 0
        for results_dict in args:
            if isinstance(results_dict, dict):
                for result in results_dict.values():
                    if isinstance(result, dict):
                        total += result.get('usage', {}).get('total_tokens', 0)
        return total
    
    async def single_ai_call(self, prompt: str, model: str = 'sonnet', 
                             system: str = None, response_format: str = None, **kwargs) -> str:
        """
        Call single AI (for fast operations)
        Used in coarse scan and refinement
        
        Args:
            prompt: The prompt to send
            model: Model name ('sonnet', 'opus', 'haiku') - maps to AI names
            system: Optional system message
            response_format: Optional format hint (not enforced)
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
        
        Returns:
            Response text as string
        """
        # Map model names to AI names
        model_to_ai = {
            'haiku': 'sonnet',  # Use sonnet as fast option (haiku not always available)
            'sonnet': 'sonnet',
            'opus': 'opus',
            'gpt5': 'gpt5',
            'gemini': 'gemini',
            'deepseek': 'deepseek',
            'grok': 'grok'
        }
        
        ai_name = model_to_ai.get(model, 'sonnet')
        
        try:
            result = await self.ensemble.call_ai(
                ai_name=ai_name,
                prompt=prompt,
                system=system if system else "You are an expert AI assistant.",
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            if not result.get('success'):
                print(f"      ⚠️  Single AI call failed: {result.get('error', 'Unknown error')}")
                return "{}"
            
            content = result.get('content', '')
            return content if content else "{}"
            
        except Exception as e:
            print(f"      ⚠️  Single AI call error: {e}")
            return "{}"
    
    async def parallel_quick_score(self, prompt: str, num_ais: int = 6, 
                                   system: str = None) -> List[int]:
        """
        Get quick numeric scores from multiple AIs in parallel
        Used in mini-godmode quality filter
        Returns list of scores (0-100)
        
        Args:
            prompt: Scoring prompt
            num_ais: Number of AIs to use (default: 6)
            system: Optional system message
        
        Returns:
            List of integer scores (0-100)
        """
        # Get available AIs
        available_ais = [name for name, ai in self.ensemble.ais.items() 
                        if ai.get('status') == '✅']
        
        # Limit to requested number
        ais_to_use = available_ais[:num_ais]
        
        if not ais_to_use:
            return [50]  # Default score if no AIs available
        
        # Build tasks for parallel execution
        tasks = [
            self._single_score_call(ai_name, prompt, system)
            for ai_name in ais_to_use
        ]
        
        # Execute in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"      ⚠️  Parallel scoring error: {e}")
            return [50]
        
        # Extract scores
        scores = []
        for result in results:
            if isinstance(result, Exception):
                continue
            
            # Extract number from response
            score = self._extract_number_from_text(str(result))
            if score is not None and 0 <= score <= 100:
                scores.append(score)
        
        return scores if scores else [50]  # Default to 50 if all failed
    
    async def _single_score_call(self, ai_name: str, prompt: str, system: str = None) -> str:
        """Helper: Single AI scoring call"""
        try:
            result = await self.ensemble.call_ai(
                ai_name=ai_name,
                prompt=prompt,
                system=system if system else "You are a viral content evaluator. Return only a number 0-100.",
                max_tokens=100,  # Short response for scoring
                temperature=0.3  # Lower temp for scoring consistency
            )
            
            if not result.get('success'):
                return "50"  # Default score on error
            
            content = result.get('content', '')
            return content if content else "50"
            
        except Exception as e:
            return "50"  # Default score on error
    
    def _extract_number_from_text(self, text: str) -> Optional[int]:
        """Extract first number from text (for scoring)"""
        import re
        
        if not text:
            return None
        
        # Look for explicit score patterns (in order of specificity)
        patterns = [
            r'score[:\s]+(\d+)',
            r'rating[:\s]+(\d+)',
            r'(\d+)\s*/\s*100',
            r'(\d+)\s*points',
            r'^(\d+)$',  # Just a number on its own line
            r'\b(\d+)\b'  # Any standalone number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    num = int(match.group(1))
                    if 0 <= num <= 100:
                        return num
                except (ValueError, IndexError):
                    continue
        
        return None


# Test function
async def test_ensemble():
    """Quick test of ensemble system"""
    
    print("\n🧪 TESTING ENSEMBLE SYSTEM\n")
    
    ensemble = PremiumAIEnsemble()
    
    # Test simple prompt
    test_prompt = "In one sentence, what makes a great video hook?"
    system_prompt = "You are an expert in viral short-form video content."
    
    print("📝 Test Prompt:", test_prompt)
    print("\n")
    
    results = await ensemble.call_all(test_prompt, system=system_prompt)
    
    print("="*70)
    print("📊 RESULTS")
    print("="*70)
    
    for ai_name, result in results.items():
        if result.get('success'):
            print(f"\n🤖 {ai_name.upper()}:")
            print(f"   {result['content'][:300]}...")
            print(f"   Tokens: {result['usage'].get('total_tokens', 'N/A')}")
        else:
            print(f"\n❌ {ai_name.upper()}: {result.get('error', 'Unknown error')}")
    
    # Print stats
    ensemble.print_usage_stats()
    
    print("✅ Ensemble test complete!\n")


# Update test function to include ConsensusEngine
async def test_ensemble_with_consensus():
    """Test ensemble with consensus building"""
    
    print("\n🧪 TESTING ENSEMBLE + CONSENSUS\n")
    
    ensemble = PremiumAIEnsemble()
    consensus = ConsensusEngine(ensemble)
    
    # Test 1: Parallel Vote
    result = await consensus.build_consensus(
        prompt="In one sentence, what makes a great video hook?",
        system="You are an expert in viral short-form video content.",
        strategy='parallel_vote'
    )
    
    print("\n" + "="*70)
    print("📊 CONSENSUS RESULT")
    print("="*70)
    print(f"\n{result['consensus']}\n")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Strategy: {result['strategy']}")
    print(f"Total Tokens: {result['metadata']['total_tokens']:,}")
    
    # Show costs
    if 'total_cost' in ensemble.usage_stats:
        print(f"💰 Total Cost: ${ensemble.usage_stats['total_cost']:.4f}")
    
    ensemble.print_usage_stats()


if __name__ == "__main__":
    # Test with consensus
    asyncio.run(test_ensemble_with_consensus())

