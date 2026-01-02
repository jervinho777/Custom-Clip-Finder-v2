"""
Custom Clip Finder v2 - BRAIN System

Dynamic knowledge base for viral patterns.
- PRINCIPLES.json: Compact rules
- Vector Store: 972+ clips for similarity search
- Weekly updates from performance data
"""

from .learn import load_principles, get_similar_clips
from .vector_store import VectorStore

__all__ = [
    "load_principles",
    "get_similar_clips",
    "VectorStore",
]

