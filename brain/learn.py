"""
BRAIN Learning System V2

Loads hierarchical principles and provides principle-based guidance.

WICHTIG: Arbeitet NUR mit Prinzipien (WARUM), nicht mit Regeln (WAS).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


BRAIN_DIR = Path(__file__).parent
PRINCIPLES_PATH = BRAIN_DIR / "BRAIN_PRINCIPLES.json"
LEGACY_PRINCIPLES_PATH = BRAIN_DIR / "PRINCIPLES.json"  # Fallback


def load_principles() -> Dict:
    """
    Load BRAIN_PRINCIPLES.json (oder legacy PRINCIPLES.json als Fallback).
    
    Returns:
        Dict with hierarchical principles
    """
    if PRINCIPLES_PATH.exists():
        with open(PRINCIPLES_PATH) as f:
            return json.load(f)
    elif LEGACY_PRINCIPLES_PATH.exists():
        print("⚠️ Using legacy PRINCIPLES.json - run brain analysis to update!")
        with open(LEGACY_PRINCIPLES_PATH) as f:
            return json.load(f)
    return {}


def get_core_principles() -> List[Dict]:
    """
    Get the fundamental core principles.
    
    Returns:
        List of core principle dicts with principle, why_works, application
    """
    principles = load_principles()
    return principles.get("core_principles", [])


def get_hook_principles() -> List[Dict]:
    """
    Get hook creation principles.
    
    Returns:
        List of hook principle dicts
    """
    principles = load_principles()
    return principles.get("hook_principles", [])


def get_transformation_principles() -> List[Dict]:
    """
    Get transformation principles for COMPOSE stage.
    
    Returns:
        List of transformation principle dicts
    """
    principles = load_principles()
    return principles.get("transformation_principles", [])


def get_quality_principles() -> List[Dict]:
    """
    Get quality principles for VALIDATE stage.
    
    Returns:
        List of quality principle dicts
    """
    principles = load_principles()
    return principles.get("quality_principles", [])


def get_master_principle() -> str:
    """
    Get the master principle.
    
    Returns:
        The master principle string
    """
    principles = load_principles()
    return principles.get(
        "master_principle", 
        "Make a video so good that people cannot physically scroll past"
    )


async def get_similar_clips(
    query: str,
    n_results: int = 5,
    min_views: int = 100000
) -> List[Dict]:
    """
    Find similar clips from vector store.
    
    Args:
        query: Text to search for
        n_results: Number of results
        min_views: Minimum views filter
        
    Returns:
        List of similar clips with metadata
    """
    from .vector_store import VectorStore
    
    store = VectorStore()
    
    if not store.is_initialized():
        return []
    
    results = await store.search(query, n_results=n_results * 2)
    
    # Filter by views
    filtered = [
        r for r in results
        if r.get("metadata", {}).get("views", 0) >= min_views
    ]
    
    return filtered[:n_results]


def get_principle_context_for_prompt() -> str:
    """
    Get a formatted context string with all principles for AI prompts.
    
    This is used to inject the learned principles into the pipeline prompts.
    
    Returns:
        Formatted string with all relevant principles
    """
    principles = load_principles()
    
    # Master principle
    master = principles.get("master_principle", "Maximize watchtime")
    
    # Core principles
    core = principles.get("core_principles", [])
    
    # Hook principles
    hooks = principles.get("hook_principles", [])
    
    # Transformation principles
    transforms = principles.get("transformation_principles", [])
    
    context = f"""
[BRAIN PRINCIPLES - Learned from {principles.get('data_sources', {}).get('isolated_clips', 0)} viral clips]

🎯 MASTER PRINCIPLE:
{master}

📍 CORE PRINCIPLES (Fundamental truths about viral content):
"""
    
    for i, p in enumerate(core[:5], 1):
        context += f"""
{i}. {p.get('principle', 'N/A')}
   WARUM: {p.get('why_works', 'N/A')}
   ANWENDUNG: {p.get('application', 'N/A')}
"""
    
    context += """
🔥 HOOK PRINCIPLES (Why hooks work):
"""
    
    for i, p in enumerate(hooks[:5], 1):
        freq = p.get('frequency', 'N/A')
        context += f"""
{i}. {p.get('principle', 'N/A')} ({freq})
   WARUM: {p.get('why_works', 'N/A')}
   WANN ANWENDEN: {p.get('when_to_apply', 'N/A')}
"""
    
    context += """
🔄 TRANSFORMATION PRINCIPLES (How to restructure content):
"""
    
    for i, p in enumerate(transforms[:5], 1):
        context += f"""
{i}. {p.get('principle', 'N/A')}
   WARUM: {p.get('why_works', 'N/A')}
   WANN ANWENDEN: {p.get('when_to_apply', 'N/A')}
"""
    
    context += """
⚠️ KEINE STARREN REGELN:
- Keine festen Zeitangaben ("Hook muss in 3 Sekunden sein")
- Keine Template-Strukturen ("Immer Hook→Story→Payoff")
- Nur Prinzipien anwenden, die zum KONTEXT passen!
"""
    
    return context


def get_principle_summary() -> str:
    """
    Get a brief summary of key principles for prompts.
    
    Returns:
        Short formatted string summary
    """
    principles = load_principles()
    
    summary = f"MASTER: {principles.get('master_principle', 'Maximize watchtime')}\n"
    
    # Top 3 core principles
    core = principles.get("core_principles", [])[:3]
    for i, p in enumerate(core, 1):
        summary += f"CORE {i}: {p.get('principle', 'N/A')}\n"
    
    return summary
