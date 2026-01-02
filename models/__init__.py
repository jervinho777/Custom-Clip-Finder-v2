"""
Custom Clip Finder v2 - AI Models

Unified interface for all AI providers.
Uses dynamic model detection to always use the latest models.
"""

from .base import AIModel, AIResponse, get_model
from .ensemble import AIEnsemble
from .auto_detect import get_model as get_model_string, detect_all_models, print_current_config

__all__ = [
    "AIModel",
    "AIResponse", 
    "AIEnsemble",
    "get_model",  # Factory function to create AIModel instances
    "get_model_string",  # Get model string from auto_detect
    "detect_all_models",  # Force refresh model detection
    "print_current_config",  # Print current model config
]

