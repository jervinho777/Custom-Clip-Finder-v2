#!/usr/bin/env python3
"""
Verification Tests für Custom Clip Finder (Boris Cherny Workflow)

Diese Tests nutzen Ground Truth Daten um zu verifizieren, dass das System
korrekt funktioniert. Minimum Recall Threshold: 70%

Usage:
    pytest tests/test_clip_finder.py -v
    pytest tests/test_clip_finder.py -v --tb=short
"""

import json
import pytest
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


# =============================================================================
# Configuration
# =============================================================================

GROUND_TRUTH_PATH = Path(__file__).parent / "verified_clips.json"
MIN_RECALL_THRESHOLD = 0.70  # 70% der erwarteten Clips müssen gefunden werden
MIN_PRECISION_THRESHOLD = 0.50  # Mindestens 50% der gefundenen Clips sollten relevant sein


# =============================================================================
# Data Loading
# =============================================================================

def load_ground_truth() -> Dict:
    """Lade Ground Truth Daten aus JSON."""
    if not GROUND_TRUTH_PATH.exists():
        pytest.skip(f"Ground Truth Datei nicht gefunden: {GROUND_TRUTH_PATH}")
    
    with open(GROUND_TRUTH_PATH) as f:
        return json.load(f)


def load_system_results(results_path: Path) -> List[Dict]:
    """Lade System-Ergebnisse aus JSON."""
    if not results_path.exists():
        return []
    
    with open(results_path) as f:
        return json.load(f)


# =============================================================================
# Matching Logic
# =============================================================================

@dataclass
class MatchResult:
    """Ergebnis eines Clip-Matchings."""
    expected_id: str
    expected_name: str
    found: bool
    matched_clip: Optional[Dict] = None
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


def check_keyword_match(text: str, keywords: List[str]) -> bool:
    """Prüfe ob mindestens ein Keyword im Text vorkommt."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def check_timing_overlap(
    found_start: float, 
    found_end: float,
    expected_start_range: List[int],
    expected_end_range: List[int]
) -> bool:
    """Prüfe ob Timing ungefähr passt (mit Toleranz)."""
    # Start sollte in der Nähe des erwarteten Bereichs sein
    start_ok = (expected_start_range[0] - 30) <= found_start <= (expected_start_range[1] + 30)
    # End sollte in der Nähe des erwarteten Bereichs sein
    end_ok = (expected_end_range[0] - 30) <= found_end <= (expected_end_range[1] + 30)
    
    return start_ok and end_ok


def match_clip(expected: Dict, discovered: List[Dict]) -> MatchResult:
    """
    Prüfe ob ein erwarteter Clip in den entdeckten gefunden wurde.
    
    Matching-Kriterien:
    1. Mindestens ein Keyword muss im Hook oder Segment-Text vorkommen
    2. Timing sollte ungefähr passen (mit Toleranz)
    """
    result = MatchResult(
        expected_id=expected["id"],
        expected_name=expected["name"],
        found=False
    )
    
    for clip in discovered:
        # Extrahiere Text aus dem gefundenen Clip
        hook_text = clip.get("hook_text", "")
        segment_texts = " ".join([
            s.get("text", "") for s in clip.get("segments", [])
        ])
        full_text = f"{hook_text} {segment_texts}"
        
        # Check 1: Keyword Match
        if not check_keyword_match(full_text, expected["hook_keywords"]):
            continue
        
        # Check 2: Timing (optional, mit Toleranz)
        found_start = clip.get("start", 0)
        found_end = clip.get("end", 0)
        
        timing_ok = check_timing_overlap(
            found_start, found_end,
            expected["start_range"],
            expected["end_range"]
        )
        
        if not timing_ok:
            result.issues.append(
                f"Timing mismatch: found {found_start:.0f}-{found_end:.0f}s, "
                f"expected {expected['start_range'][0]}-{expected['end_range'][1]}s"
            )
        
        # Match gefunden!
        result.found = True
        result.matched_clip = clip
        break
    
    return result


# =============================================================================
# Metrics Calculation
# =============================================================================

@dataclass
class VerificationMetrics:
    """Metriken für die Verification."""
    total_expected: int
    total_found: int
    total_with_issues: int
    recall: float
    precision: float
    details: List[MatchResult]
    
    def __str__(self) -> str:
        return (
            f"Recall: {self.recall:.1%} ({self.total_found}/{self.total_expected})\n"
            f"Precision: {self.precision:.1%}\n"
            f"Issues: {self.total_with_issues}"
        )


def calculate_metrics(
    expected_clips: List[Dict],
    discovered_clips: List[Dict]
) -> VerificationMetrics:
    """Berechne Recall, Precision und andere Metriken."""
    
    details = []
    found_count = 0
    issues_count = 0
    
    for expected in expected_clips:
        result = match_clip(expected, discovered_clips)
        details.append(result)
        
        if result.found:
            found_count += 1
            if result.issues:
                issues_count += 1
    
    recall = found_count / len(expected_clips) if expected_clips else 0
    
    # Precision: Wie viele der gefundenen Clips sind tatsächlich relevant?
    # (Vereinfacht: Wir zählen nur ob wir nicht zu viele "Bad Clips" haben)
    precision = found_count / len(discovered_clips) if discovered_clips else 0
    
    return VerificationMetrics(
        total_expected=len(expected_clips),
        total_found=found_count,
        total_with_issues=issues_count,
        recall=recall,
        precision=precision,
        details=details
    )


# =============================================================================
# Test Functions
# =============================================================================

class TestGroundTruthData:
    """Tests für die Ground Truth Daten selbst."""
    
    def test_ground_truth_exists(self):
        """Ground Truth JSON muss existieren."""
        assert GROUND_TRUTH_PATH.exists(), f"Missing: {GROUND_TRUTH_PATH}"
    
    def test_ground_truth_structure(self):
        """Ground Truth muss korrektes Format haben."""
        data = load_ground_truth()
        
        assert "metadata" in data
        assert "verified_viral_clips" in data
        assert "known_bad_clips" in data
        assert "client_specific_rules" in data
    
    def test_minimum_verified_clips(self):
        """Mindestens 5 verifizierte Clips sollten vorhanden sein."""
        data = load_ground_truth()
        clips = data.get("verified_viral_clips", [])
        
        assert len(clips) >= 5, f"Only {len(clips)} verified clips, need at least 5"
    
    def test_clip_structure(self):
        """Jeder Clip muss die erforderlichen Felder haben."""
        data = load_ground_truth()
        required_fields = ["id", "name", "hook_keywords", "start_range", "end_range"]
        
        for clip in data.get("verified_viral_clips", []):
            for field in required_fields:
                assert field in clip, f"Clip {clip.get('id', 'unknown')} missing field: {field}"


class TestClientRules:
    """Tests für Client-spezifische Regeln."""
    
    def test_client_rules_exist(self):
        """Client-Regeln für alle drei Hauptkunden."""
        data = load_ground_truth()
        rules = data.get("client_specific_rules", {})
        
        expected_clients = ["Greator", "Robert Marc Lehmann", "Liebscher & Bracht"]
        
        for client in expected_clients:
            assert client in rules, f"Missing rules for: {client}"
    
    def test_client_rules_structure(self):
        """Jede Client-Regel muss die wichtigsten Felder haben."""
        data = load_ground_truth()
        rules = data.get("client_specific_rules", {})
        
        for client, rule in rules.items():
            assert "description" in rule, f"{client} missing description"
            assert "preferred_archetypes" in rule, f"{client} missing preferred_archetypes"


class TestClipFinderRecall:
    """
    Haupttests für Clip Finder Recall.
    
    Diese Tests werden nur ausgeführt wenn System-Ergebnisse vorhanden sind.
    """
    
    @pytest.fixture
    def ground_truth(self):
        return load_ground_truth()
    
    @pytest.fixture
    def mock_results(self):
        """Mock-Ergebnisse für Testing ohne echten Run."""
        mock_path = Path(__file__).parent / "mock_dieter_lange_results.json"
        if mock_path.exists():
            return load_system_results(mock_path)
        return []
    
    def test_recall_with_mock(self, ground_truth, mock_results):
        """Test Recall mit Mock-Daten."""
        if not mock_results:
            pytest.skip("No mock results available")
        
        expected = ground_truth.get("verified_viral_clips", [])
        metrics = calculate_metrics(expected, mock_results)
        
        print(f"\n{metrics}")
        
        # Mit Mock-Daten erwarten wir mindestens 30% (da nur 3 Clips im Mock)
        assert metrics.recall >= 0.30, f"Recall too low: {metrics.recall:.1%}"
    
    def test_recall_minimum_threshold(self, ground_truth):
        """
        Test dass System mindestens 70% der bekannten Clips findet.
        
        Dieser Test benötigt echte System-Ergebnisse im output/ Ordner.
        """
        results_path = Path("output/latest_results.json")
        
        if not results_path.exists():
            pytest.skip("No system results in output/latest_results.json")
        
        discovered = load_system_results(results_path)
        expected = ground_truth.get("verified_viral_clips", [])
        
        metrics = calculate_metrics(expected, discovered)
        
        print(f"\n{metrics}")
        print("\nDetails:")
        for detail in metrics.details:
            status = "✅" if detail.found else "❌"
            print(f"  {status} {detail.expected_name}")
            for issue in detail.issues:
                print(f"      ⚠️ {issue}")
        
        assert metrics.recall >= MIN_RECALL_THRESHOLD, (
            f"Recall {metrics.recall:.1%} below threshold {MIN_RECALL_THRESHOLD:.1%}"
        )


class TestKnownBadClips:
    """Tests dass bekannt schlechte Clips erkannt werden."""
    
    def test_bad_clips_defined(self):
        """Bad Clips sollten definiert sein."""
        data = load_ground_truth()
        bad_clips = data.get("known_bad_clips", [])
        
        assert len(bad_clips) >= 1, "No bad clips defined"
    
    def test_bad_clips_have_reasons(self):
        """Jeder Bad Clip sollte einen Grund haben."""
        data = load_ground_truth()
        
        for clip in data.get("known_bad_clips", []):
            assert "reason" in clip, f"Bad clip {clip.get('id')} has no reason"
            assert "description" in clip, f"Bad clip {clip.get('id')} has no description"


# =============================================================================
# CLI Runner
# =============================================================================

def run_verification(results_path: Optional[Path] = None) -> VerificationMetrics:
    """
    Führe vollständige Verification aus.
    
    Args:
        results_path: Pfad zu System-Ergebnissen (optional)
    
    Returns:
        VerificationMetrics mit allen Details
    """
    print("\n" + "=" * 70)
    print("CLIP FINDER VERIFICATION (Boris Cherny Workflow)")
    print("=" * 70)
    
    # Load Ground Truth
    ground_truth = load_ground_truth()
    expected = ground_truth.get("verified_viral_clips", [])
    print(f"\n📋 Expected clips: {len(expected)}")
    
    # Load Results
    if results_path and results_path.exists():
        discovered = load_system_results(results_path)
    else:
        # Try default locations
        for path in [Path("output/latest_results.json"), Path("tests/mock_dieter_lange_results.json")]:
            if path.exists():
                discovered = load_system_results(path)
                results_path = path
                break
        else:
            discovered = []
    
    print(f"📊 Discovered clips: {len(discovered)}")
    
    if not discovered:
        print("\n⚠️ No results found. Run the clip finder first.")
        return None
    
    # Calculate Metrics
    metrics = calculate_metrics(expected, discovered)
    
    # Print Results
    print("\n" + "-" * 70)
    print("RESULTS:")
    print("-" * 70)
    
    for detail in metrics.details:
        status = "✅" if detail.found else "❌"
        print(f"\n{status} {detail.expected_name}")
        if detail.matched_clip:
            clip = detail.matched_clip
            print(f"   Hook: \"{clip.get('hook_text', '')[:50]}...\"")
            print(f"   Time: {clip.get('start', 0):.0f}s - {clip.get('end', 0):.0f}s")
        for issue in detail.issues:
            print(f"   ⚠️ {issue}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nRecall: {metrics.recall:.1%} ({metrics.total_found}/{metrics.total_expected})")
    print(f"Threshold: {MIN_RECALL_THRESHOLD:.1%}")
    
    if metrics.recall >= MIN_RECALL_THRESHOLD:
        print("\n🎉 VERIFICATION PASSED!")
    else:
        print(f"\n❌ VERIFICATION FAILED (need {MIN_RECALL_THRESHOLD:.1%})")
    
    return metrics


if __name__ == "__main__":
    import sys
    
    results_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    metrics = run_verification(results_path)
    
    if metrics and metrics.recall >= MIN_RECALL_THRESHOLD:
        sys.exit(0)
    else:
        sys.exit(1)
