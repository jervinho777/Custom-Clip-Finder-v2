"""
Account Metadata Extractor & Baseline Calculator

Extrahiert Account-Daten und berechnet sichere Baselines für NVI-Berechnung.

MATH SAFETY:
- Division by Zero wird durch min(1000) verhindert
- Log von 0 wird durch safe_followers verhindert
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


DATA_DIR = Path(__file__).parent.parent / "data"
TRAINING_DATA_PATH = DATA_DIR / "training" / "goat_training_data.json"
ACCOUNTS_METADATA_PATH = DATA_DIR / "accounts_metadata.json"


@dataclass
class AccountMetadata:
    """Metadata für einen Account."""
    username: str
    followers: int
    avg_views: int
    baseline: float
    clip_count: int
    total_views: int


def calculate_baseline(followers: int) -> float:
    """
    Berechnet die sichere Baseline für einen Account.
    
    Formel:
        baseline = followers * (0.15 / log10(safe_followers))
    
    Die 0.15 ist ein empirischer Faktor der die durchschnittliche
    Erwartung für Views basierend auf Followern widerspiegelt.
    
    MATH SAFETY:
    - safe_followers = max(followers, 1000) verhindert:
      - Division by zero (log10(0) = undefined)
      - Negative logs (log10(<1) = negative)
      - Unrealistisch hohe Baselines für kleine Accounts
    
    Args:
        followers: Anzahl der Follower des Accounts
        
    Returns:
        Berechnete Baseline (minimum erwartete Views)
    """
    # MATH SAFETY: Minimum 1000 um Division/Log Fehler zu vermeiden
    safe_followers = max(followers, 1000)
    
    # Log-skalierte Baseline
    # Je mehr Follower, desto höher die absolute Erwartung
    # Aber die Rate sinkt logarithmisch (große Accounts haben relativ weniger Views)
    baseline = followers * (0.15 / math.log10(safe_followers))
    
    return baseline


def extract_accounts_from_training_data() -> Dict[str, AccountMetadata]:
    """
    Extrahiert Account-Metadaten aus den Training-Daten.
    
    Returns:
        Dict mit username -> AccountMetadata
    """
    if not TRAINING_DATA_PATH.exists():
        print(f"⚠️ Training data not found: {TRAINING_DATA_PATH}")
        return {}
    
    with open(TRAINING_DATA_PATH) as f:
        clips = json.load(f)
    
    # Aggregiere nach Account
    accounts: Dict[str, Dict] = {}
    
    for clip in clips:
        username = clip.get("account", "unknown")
        if username == "unknown":
            continue
        
        views = clip.get("performance", {}).get("views", 0)
        followers = clip.get("account_metadata", {}).get("followers", 0)
        
        if username not in accounts:
            accounts[username] = {
                "username": username,
                "followers": followers,
                "total_views": 0,
                "clip_count": 0,
                "all_views": []
            }
        
        # Update mit höchster Follower-Zahl (falls variiert)
        if followers > accounts[username]["followers"]:
            accounts[username]["followers"] = followers
        
        accounts[username]["total_views"] += views
        accounts[username]["clip_count"] += 1
        accounts[username]["all_views"].append(views)
    
    # Berechne Baselines und erstelle Metadata-Objekte
    result = {}
    
    for username, data in accounts.items():
        followers = data["followers"]
        avg_views = data["total_views"] // max(data["clip_count"], 1)
        
        # Sichere Baseline-Berechnung
        baseline = calculate_baseline(followers)
        
        result[username] = AccountMetadata(
            username=username,
            followers=followers,
            avg_views=avg_views,
            baseline=baseline,
            clip_count=data["clip_count"],
            total_views=data["total_views"]
        )
    
    return result


def save_accounts_metadata(accounts: Dict[str, AccountMetadata]) -> Path:
    """
    Speichert Account-Metadaten als JSON.
    
    Args:
        accounts: Dict mit AccountMetadata Objekten
        
    Returns:
        Path zur gespeicherten Datei
    """
    output = {}
    
    for username, meta in accounts.items():
        output[username] = {
            "username": meta.username,
            "followers": meta.followers,
            "avg_views": meta.avg_views,
            "baseline": round(meta.baseline, 2),
            "clip_count": meta.clip_count,
            "total_views": meta.total_views
        }
    
    # Sortiere nach Baseline (höchste zuerst)
    sorted_output = dict(sorted(
        output.items(), 
        key=lambda x: x[1]["baseline"], 
        reverse=True
    ))
    
    ACCOUNTS_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ACCOUNTS_METADATA_PATH, "w") as f:
        json.dump(sorted_output, f, indent=2)
    
    print(f"✅ Saved {len(sorted_output)} accounts to {ACCOUNTS_METADATA_PATH}")
    return ACCOUNTS_METADATA_PATH


def get_account_baseline(username: str) -> float:
    """
    Holt die Baseline für einen Account.
    
    FALLBACK: Wenn Account nicht gefunden, gibt DEFAULT_BASELINE zurück.
    
    Args:
        username: Der Account-Name
        
    Returns:
        Die Baseline (oder Default wenn nicht gefunden)
    """
    DEFAULT_BASELINE = 1000  # Konservativ
    
    if not ACCOUNTS_METADATA_PATH.exists():
        print(f"⚠️ accounts_metadata.json not found. Using default baseline: {DEFAULT_BASELINE}")
        return DEFAULT_BASELINE
    
    with open(ACCOUNTS_METADATA_PATH) as f:
        accounts = json.load(f)
    
    if username not in accounts:
        print(f"⚠️ Account '{username}' not found in metadata. Using default baseline: {DEFAULT_BASELINE}")
        return DEFAULT_BASELINE
    
    return accounts[username].get("baseline", DEFAULT_BASELINE)


def recalculate_baselines_only() -> None:
    """
    Lädt existierende accounts_metadata.json und berechnet NUR die baselines neu.
    
    Fasst die followers-Zahlen NICHT an!
    
    Logik:
    1. Lade existierende JSON
    2. Für jeden Account: Berechne baseline aus followers
    3. Speichere zurück
    """
    print("="*60)
    print("🔄 Baseline Recalculation")
    print("="*60)
    
    if not ACCOUNTS_METADATA_PATH.exists():
        print(f"❌ File not found: {ACCOUNTS_METADATA_PATH}")
        return
    
    # Lade existierende Daten
    with open(ACCOUNTS_METADATA_PATH) as f:
        accounts = json.load(f)
    
    print(f"\n📂 Loaded {len(accounts)} accounts")
    print("\n📊 Recalculating baselines...")
    print("-" * 50)
    
    for username, data in accounts.items():
        followers = data.get("followers", 0)
        old_baseline = data.get("baseline", 0)
        
        # Berechne neue Baseline mit sicherer Formel
        new_baseline = calculate_baseline(followers)
        
        # Update
        accounts[username]["baseline"] = round(new_baseline, 2)
        
        print(f"   {username:25s} | Followers: {followers:>10,} | Baseline: {old_baseline:>10,.0f} → {new_baseline:>10,.0f}")
    
    # Speichere zurück
    print("\n💾 Saving updated baselines...")
    with open(ACCOUNTS_METADATA_PATH, "w") as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Done! Updated {len(accounts)} baselines in {ACCOUNTS_METADATA_PATH}")


def main():
    """Extrahiert und speichert Account-Metadaten."""
    print("="*60)
    print("📊 Account Metadata Extractor")
    print("="*60)
    
    print("\n1. Extracting accounts from training data...")
    accounts = extract_accounts_from_training_data()
    
    if not accounts:
        print("❌ No accounts found!")
        return
    
    print(f"   Found {len(accounts)} accounts")
    
    # Top 10 nach Baseline
    print("\n2. Top 10 Accounts by Baseline:")
    sorted_accounts = sorted(accounts.values(), key=lambda x: x.baseline, reverse=True)
    
    for i, acc in enumerate(sorted_accounts[:10]):
        print(f"   {i+1}. {acc.username}")
        print(f"      Followers: {acc.followers:,} | Baseline: {acc.baseline:,.0f} | Avg Views: {acc.avg_views:,}")
    
    print("\n3. Saving metadata...")
    save_accounts_metadata(accounts)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--recalc":
        # Nur Baselines neu berechnen
        recalculate_baselines_only()
    else:
        # Vollständige Extraktion
        main()

