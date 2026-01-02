"""
Custom Clip Finder v2 - BRAIN System

Dynamic knowledge base for viral patterns.

Phase 1: Analyse (Learning)
- Code 1: Isolierte Clips → isolated_patterns.json
- Code 2: Longform→Clip Paare → composition_patterns.json
- Code 3: Zusammenführen → PRINCIPLES.json

Phase 2: Produktion
- PRINCIPLES.json + Vector Store → Pipeline
"""

from .learn import load_principles, get_similar_clips
from .vector_store import VectorStore
from .analyze import BrainAnalyzer, run_analysis

__all__ = [
    "load_principles",
    "get_similar_clips",
    "VectorStore",
    "BrainAnalyzer",
    "run_analysis",
]

