"""
Custom Clip Finder v2 - BRAIN System V5

Global Hook Hunting Edition - KEINE ZEITGRENZEN!

Key Functions:
- load_learned_patterns(): Get all learned patterns
- get_archetype(): Get specific archetype template
- get_hook_hunting_rule(): Get hook hunting instruction
- find_global_hooks(): Search entire transcript for hooks (NEW!)
"""

from .learn import (
    # Main load function
    load_learned_patterns,
    
    # Get functions
    get_archetypes,
    get_archetype,
    get_hook_hunting_rules,
    get_hook_hunting_rule,
    
    # NVI Scoring (V5)
    get_account_baseline,
    calculate_nvi,
    calculate_nvi_multiplier,
    calculate_weighted_score,
    calculate_engagement_multiplier,
    calculate_viral_quality,
    load_accounts_metadata,
    DEFAULT_BASELINE,
    
    # Context for prompts
    get_blueprint_context_for_prompt,
    
    # Legacy compatibility
    load_blueprints,
    load_principles,
    get_named_patterns,
    get_principle_context_for_prompt,
    scan_for_hooks,
    get_similar_clips,
    get_similar_hooks,
)

from .analyze import (
    BrainAnalyzer,
    run_analysis,
    load_learned_patterns as analyze_load_patterns,
    get_archetype_template,
    get_hook_hunting_rule as analyze_get_hook_rule,
    ARCHETYPE_DEFINITIONS,
)

from .vector_store import (
    # V5 Global Hook Hunting (NO TIME LIMITS!)
    VectorStore,
    GlobalHookCandidate,
    HookMatch,
    SentenceScanResult,
    find_global_hooks,
    scan_for_hooks as vector_scan_for_hooks,
    initialize_brain,
)

__all__ = [
    # V5 Global Hook Hunting
    "VectorStore",
    "GlobalHookCandidate",
    "HookMatch",
    "SentenceScanResult",
    "find_global_hooks",
    "initialize_brain",
    
    # V5 NVI Scoring
    "get_account_baseline",
    "calculate_nvi",
    "calculate_nvi_multiplier",
    "calculate_weighted_score",
    "calculate_engagement_multiplier",
    "calculate_viral_quality",
    "load_accounts_metadata",
    "DEFAULT_BASELINE",
    
    # V4 Core
    "load_learned_patterns",
    "get_archetypes",
    "get_archetype",
    "get_hook_hunting_rules",
    "get_hook_hunting_rule",
    "get_blueprint_context_for_prompt",
    
    # Analyzer
    "BrainAnalyzer",
    "run_analysis",
    "ARCHETYPE_DEFINITIONS",
    
    # Legacy
    "load_blueprints",
    "load_principles",
    "get_named_patterns",
    "get_principle_context_for_prompt",
    "scan_for_hooks",
    "get_similar_clips",
    "get_similar_hooks",
]
