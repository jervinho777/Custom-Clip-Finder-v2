"""
BRAIN Learning System

Loads principles and provides similarity search.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


BRAIN_DIR = Path(__file__).parent
PRINCIPLES_PATH = BRAIN_DIR / "PRINCIPLES.json"


def load_principles() -> Dict:
    """
    Load PRINCIPLES.json.
    
    Returns:
        Dict with all principles
    """
    if not PRINCIPLES_PATH.exists():
        return {}
    
    with open(PRINCIPLES_PATH) as f:
        return json.load(f)


def get_hook_patterns() -> List[Dict]:
    """
    Get hook patterns from PRINCIPLES.
    
    Returns:
        List of hook pattern dicts
    """
    principles = load_principles()
    hook_patterns = principles.get("hook_patterns", {})
    
    return [
        {"type": key, **value}
        for key, value in hook_patterns.items()
    ]


def get_transformation_patterns() -> Dict:
    """
    Get transformation patterns for COMPOSE stage.
    
    Returns:
        Dict with transformation patterns
    """
    principles = load_principles()
    return principles.get("transformation_patterns", {})


def get_cutting_principles() -> Dict:
    """
    Get cutting principles for COMPOSE stage.
    
    Returns:
        Dict with cutting principles
    """
    principles = load_principles()
    return principles.get("cutting_principles", {})


def get_quality_signals() -> Dict:
    """
    Get quality signals for VALIDATE stage.
    
    Returns:
        Dict with quality signals
    """
    principles = load_principles()
    return principles.get("quality_signals", {})


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


def get_principle_summary() -> str:
    """
    Get a summary of key principles for prompts.
    
    Returns:
        Formatted string summary
    """
    principles = load_principles()
    
    summary = "KEY PRINCIPLES:\n"
    
    # Algorithm understanding
    algo = principles.get("algorithm_understanding", {})
    summary += f"• Core: {algo.get('core_principle', 'N/A')}\n"
    
    # Top hook patterns
    hooks = principles.get("hook_patterns", {})
    summary += "• Top Hook Patterns:\n"
    for name, pattern in list(hooks.items())[:3]:
        freq = pattern.get("frequency_in_top", "N/A")
        summary += f"  - {name}: {freq} of top performers\n"
    
    # Anti-patterns
    anti = principles.get("anti_patterns", [])[:3]
    summary += "• Avoid:\n"
    for a in anti:
        summary += f"  - {a}\n"
    
    return summary

