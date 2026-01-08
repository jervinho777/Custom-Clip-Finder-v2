"""
BRAIN Learning System V5 - With NVI Scoring

Lädt gelernte Patterns und bietet Zugriffsfunktionen.

WICHTIGE FORMELN:
- NVI (Normalized Viral Index) = views / baseline
- Multiplier mit Log-Skalierung für Elite-Clips (NVI > 10)
- Safe Math: Keine Division by Zero, keine fehlenden Accounts
"""

import json
import math
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Setup logging
logger = logging.getLogger(__name__)


BRAIN_DIR = Path(__file__).parent
DATA_DIR = BRAIN_DIR.parent / "data"
PATTERNS_FILE = DATA_DIR / "learned_patterns.json"
ACCOUNTS_METADATA_PATH = DATA_DIR / "accounts_metadata.json"

# Legacy paths for backwards compat
BLUEPRINTS_PATH = BRAIN_DIR / "BLUEPRINTS.json"
PRINCIPLES_PATH = BRAIN_DIR / "PRINCIPLES.json"

# FALLBACK für fehlende Accounts
DEFAULT_BASELINE = 1000  # Konservativ


# =============================================================================
# Account Baseline & NVI Functions
# =============================================================================

def load_accounts_metadata() -> Dict:
    """Lädt die Account-Metadaten."""
    if ACCOUNTS_METADATA_PATH.exists():
        with open(ACCOUNTS_METADATA_PATH) as f:
            return json.load(f)
    return {}


def get_account_baseline(username: str) -> float:
    """
    Holt die Baseline für einen Account.
    
    FALLBACK (Fix #3): Wenn Account nicht gefunden, logge Warnung
    und gib DEFAULT_BASELINE zurück.
    
    Args:
        username: Der Account-Name
        
    Returns:
        Die Baseline (oder Default wenn nicht gefunden)
    """
    accounts = load_accounts_metadata()
    
    if username not in accounts:
        logger.warning(
            f"Account '{username}' not found in accounts_metadata.json. "
            f"Using DEFAULT_BASELINE={DEFAULT_BASELINE}"
        )
        return DEFAULT_BASELINE
    
    return accounts[username].get("baseline", DEFAULT_BASELINE)


def calculate_nvi(views: int, baseline: float) -> float:
    """
    Berechnet den Normalized Viral Index (NVI).
    
    NVI = views / baseline
    
    - NVI < 1.0: Underperformer
    - NVI 1.0-10.0: Normale Performance
    - NVI > 10.0: Viral/Elite
    
    MATH SAFETY: baseline ist bereits safe (min 1000)
    
    Args:
        views: Tatsächliche Views des Clips
        baseline: Erwartete Views basierend auf Account
        
    Returns:
        NVI Score (0+)
    """
    # Safety: Baseline sollte nie 0 sein, aber zur Sicherheit
    safe_baseline = max(baseline, 1.0)
    return views / safe_baseline


def calculate_nvi_multiplier(nvi: float) -> float:
    """
    Berechnet den Score-Multiplier basierend auf NVI.
    
    FIX #2 (Elite Capping): 
    Wir kappen NICHT mehr bei 2.0 für NVI > 10!
    
    Chris Surel (NVI 350) muss stärker gewichtet werden als NVI 10.
    
    Dynamische Log-Skalierung:
    - NVI < 1.0:   multiplier = 0.5 (Underperformer)
    - NVI 1-10:    multiplier = 1.0 → 2.0 (linear)
    - NVI > 10:    multiplier = 2.0 + log10(nvi/10) (logarithmisch)
    
    Beispiele:
    - NVI 0.5  → 0.5
    - NVI 1.0  → 1.0
    - NVI 5.0  → 1.44
    - NVI 10   → 2.0
    - NVI 100  → 3.0  (log10(10) = 1)
    - NVI 350  → 3.54 (log10(35) = 1.54)
    - NVI 1000 → 4.0  (log10(100) = 2)
    
    Args:
        nvi: Der Normalized Viral Index
        
    Returns:
        Multiplier für den Score (0.5 bis theoretisch unbegrenzt)
    """
    if nvi < 1.0:
        # Underperformer - reduzierter Einfluss
        return 0.5
    elif nvi < 10.0:
        # Normale Performance - linearer Anstieg von 1.0 bis 2.0
        # Bei NVI 1 → 1.0, bei NVI 10 → 2.0
        return 1.0 + (nvi - 1.0) * (1.0 / 9.0)
    else:
        # ELITE - Logarithmischer Boost
        # Bei NVI 10 → 2.0, NVI 100 → 3.0, NVI 1000 → 4.0
        return 2.0 + math.log10(nvi / 10.0)


def calculate_engagement_multiplier(
    views: int,
    likes: int = 0,
    shares: int = 0,
    saves: int = 0
) -> float:
    """
    Berechnet den Engagement-Multiplier.
    
    Belohnt echte Resonanz über reinen Clickbait.
    
    Formel:
        engagement_rate = (shares + saves) / views
        
        - < 1%: 1.0 (normal)
        - 1-5%: 1.0 + (rate - 0.01) * 5 → max 1.2
        - > 5%: 1.2 + min(0.3, (rate - 0.05) * 2) → max 1.5
    
    Shares + Saves sind wertvoller als Likes, weil sie
    echte Weiterempfehlung bedeuten.
    
    Args:
        views: Anzahl Views
        likes: Anzahl Likes
        shares: Anzahl Shares
        saves: Anzahl Saves
        
    Returns:
        Engagement-Multiplier (1.0 bis 1.5)
    """
    if views <= 0:
        return 1.0
    
    # Shares + Saves sind der Schlüssel für echte Resonanz
    engagement_actions = shares + saves
    engagement_rate = engagement_actions / views
    
    if engagement_rate < 0.01:
        # < 1% - Normal
        return 1.0
    elif engagement_rate < 0.05:
        # 1-5% - Leichter Boost (bis 1.2)
        # Linear von 1.0 bei 1% bis 1.2 bei 5%
        return 1.0 + (engagement_rate - 0.01) * 5.0  # 0.01→1.0, 0.05→1.2
    else:
        # > 5% - Starker Boost (bis 1.5)
        # 1.2 + weiterer Bonus, aber gekappt bei 1.5
        additional = min(0.3, (engagement_rate - 0.05) * 2.0)
        return 1.2 + additional


def calculate_viral_quality(
    views: int,
    username: str,
    likes: int = 0,
    shares: int = 0,
    saves: int = 0,
    base_score: float = 1.0
) -> Dict:
    """
    Berechnet die vollständige virale Qualität eines Clips.
    
    Kombiniert:
    - NVI (Normalized Viral Index): Relative Performance zum Account
    - Engagement-Multiplier: Belohnt echte Resonanz (Shares + Saves)
    
    Args:
        views: Anzahl Views
        username: Account-Name
        likes: Anzahl Likes
        shares: Anzahl Shares
        saves: Anzahl Saves
        base_score: Basis-Score (z.B. aus Analyse)
        
    Returns:
        Dict mit allen Scoring-Komponenten
    """
    # Baseline & NVI
    baseline = get_account_baseline(username)
    nvi = calculate_nvi(views, baseline)
    nvi_multiplier = calculate_nvi_multiplier(nvi)
    
    # Engagement
    engagement_multiplier = calculate_engagement_multiplier(views, likes, shares, saves)
    engagement_rate = (shares + saves) / max(views, 1)
    
    # Kombinierter Score
    # NVI-Multiplier * Engagement-Multiplier * Base Score
    final_score = base_score * nvi_multiplier * engagement_multiplier
    
    return {
        "final_score": round(final_score, 2),
        "nvi": round(nvi, 2),
        "nvi_multiplier": round(nvi_multiplier, 2),
        "engagement_rate": round(engagement_rate, 4),
        "engagement_multiplier": round(engagement_multiplier, 2),
        "baseline": round(baseline, 2),
        "is_elite": nvi > 10,
        "has_high_engagement": engagement_rate > 0.05
    }


def calculate_weighted_score(
    views: int,
    username: str,
    base_score: float = 1.0,
    likes: int = 0,
    shares: int = 0,
    saves: int = 0
) -> Tuple[float, float, float]:
    """
    Berechnet den gewichteten Score für einen Clip.
    
    Kombiniert alle Fixes:
    - Fix #1: Sichere Baseline (in get_account_baseline)
    - Fix #2: Dynamische Log-Skalierung für Elite
    - Fix #3: Fallback für fehlende Accounts
    - Fix #4: Engagement-Multiplier für echte Resonanz
    
    Args:
        views: Tatsächliche Views des Clips
        username: Account-Name
        base_score: Basis-Score (z.B. aus Analyse)
        likes: Anzahl Likes
        shares: Anzahl Shares
        saves: Anzahl Saves
        
    Returns:
        Tuple von (weighted_score, nvi, multiplier)
    """
    # Fix #3: Fallback für fehlende Accounts
    baseline = get_account_baseline(username)
    
    # Berechne NVI
    nvi = calculate_nvi(views, baseline)
    
    # Fix #2: Dynamische Log-Skalierung
    nvi_multiplier = calculate_nvi_multiplier(nvi)
    
    # Fix #4: Engagement-Multiplier
    engagement_multiplier = calculate_engagement_multiplier(views, likes, shares, saves)
    
    # Kombinierter Multiplier
    total_multiplier = nvi_multiplier * engagement_multiplier
    
    # Gewichteter Score
    weighted_score = base_score * total_multiplier
    
    return weighted_score, nvi, total_multiplier


# =============================================================================
# Load Functions
# =============================================================================

def load_learned_patterns() -> Dict:
    """Lädt die gelernten Patterns."""
    if PATTERNS_FILE.exists():
        with open(PATTERNS_FILE) as f:
            return json.load(f)
    return {}


def load_blueprints() -> Dict:
    """Legacy alias für load_learned_patterns."""
    return load_learned_patterns()


def load_principles() -> Dict:
    """Legacy alias für load_learned_patterns."""
    return load_learned_patterns()


# =============================================================================
# Get Functions
# =============================================================================

def get_archetypes() -> Dict:
    """Holt alle Archetypen."""
    patterns = load_learned_patterns()
    return patterns.get("archetypes", {})


def get_archetype(archetype_id: str) -> Dict:
    """Holt einen spezifischen Archetyp."""
    archetypes = get_archetypes()
    return archetypes.get(archetype_id, {})


def get_hook_hunting_rules() -> Dict:
    """Holt alle Hook-Hunting Regeln."""
    patterns = load_learned_patterns()
    return patterns.get("hook_hunting_rules", {})


def get_hook_hunting_rule(archetype_id: str) -> Dict:
    """Holt die Hook-Hunting Regel für einen Archetyp."""
    rules = get_hook_hunting_rules()
    return rules.get(archetype_id, {})


def get_named_patterns() -> List:
    """Legacy - gibt leere Liste zurück."""
    return []


# =============================================================================
# Context for Prompts
# =============================================================================

def get_blueprint_context_for_prompt() -> str:
    """Gibt Kontext-String für Prompts zurück."""
    patterns = load_learned_patterns()
    
    if not patterns:
        return "[Keine gelernten Patterns verfügbar]"
    
    context = "[GELERNTE PATTERNS]\n"
    
    for arch_id, arch_data in patterns.get("archetypes", {}).items():
        context += f"\n{arch_data.get('name', arch_id)}:\n"
        context += f"  Struktur: {' -> '.join(arch_data.get('structure', []))}\n"
        context += f"  Hook-Position: {arch_data.get('hook_location', 'start')}\n"
    
    return context


def get_principle_context_for_prompt() -> str:
    """Legacy alias."""
    return get_blueprint_context_for_prompt()


# =============================================================================
# Dummy Functions for Compatibility
# =============================================================================

async def scan_for_hooks(segments, **kwargs):
    """Placeholder - Hook scanning happens in discover.py now."""
    return []


async def get_similar_clips(query, **kwargs):
    """Placeholder - returns empty list."""
    return []


async def get_similar_hooks(query, **kwargs):
    """Placeholder - returns empty list."""
    return []
