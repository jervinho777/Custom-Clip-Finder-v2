"""
Custom Clip Finder v2 - Pipeline

4-Stage Pipeline:
1. DISCOVER - Find viral moments
2. COMPOSE - Restructure for maximum impact
3. VALIDATE - Quality scoring using BRAIN
4. EXPORT - Generate MP4 + XML + JSON
"""

from .discover import discover_moments
from .compose import compose_clip
from .validate import validate_clip
from .export import export_clip

__all__ = [
    "discover_moments",
    "compose_clip",
    "validate_clip",
    "export_clip",
]

