#!/usr/bin/env python3
"""
Ground Truth Test: Dieter Lange

Dieses Video wurde manuell analysiert. Wir wissen dass folgende 
virale Momente drin sind. Das System MUSS diese finden.

Pfad: /Users/jervinquisada/custom-clip-finder/ARCHIVED_LARGE_FILES_20260102/Dieter Lange.mp4
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExpectedMoment:
    """Ein bekannter viraler Moment aus dem Video."""
    name: str
    hook_keywords: List[str]  # Mindestens eines muss im gefundenen Hook sein
    start_range: tuple  # (min_start, max_start) in Sekunden
    end_range: tuple  # (min_end, max_end) in Sekunden
    pattern: str  # hook_extraction, clean_extraction, etc.
    notes: str


# =====================================================
# GROUND TRUTH: Bekannte virale Momente in Dieter Lange
# =====================================================

EXPECTED_MOMENTS = [
    ExpectedMoment(
        name="Arbeite niemals für Geld",
        hook_keywords=["arbeite niemals für geld", "niemals für geld"],
        start_range=(560, 580),
        end_range=(650, 660),
        pattern="hook_extraction",
        notes="Hook 'Arbeite niemals für Geld' steht bei 653s, muss nach vorne gezogen werden"
    ),
    ExpectedMoment(
        name="Ackergaul vs Rennpferd",
        hook_keywords=["ackergaul", "rennpferd", "talent"],
        start_range=(470, 510),
        end_range=(530, 550),
        pattern="clean_extraction",
        notes="Starke Metapher: 'Aus einem Ackergaul wird kein Rennpferd'"
    ),
    ExpectedMoment(
        name="Was willst du mal werden",
        hook_keywords=["was willst du", "mal werden", "impliziert"],
        start_range=(310, 330),
        end_range=(340, 360),
        pattern="beliefbreaker",
        notes="Challenget die Frage 'Was willst du mal werden?'"
    ),
    ExpectedMoment(
        name="Erziehung / Mehr ist besser",
        hook_keywords=["erziehung", "mehr ist besser", "virus"],
        start_range=(230, 280),
        end_range=(310, 330),
        pattern="clean_extraction",
        notes="Kritik an Erziehung und 'Mehr ist besser' Mentalität"
    ),
    ExpectedMoment(
        name="Geburt / 500 Millionen Bewerber",
        hook_keywords=["geburt", "500 millionen", "bewerber", "stelle ausgeschrieben"],
        start_range=(20, 40),
        end_range=(90, 120),
        pattern="story_hook",
        notes="Starke Opening-Story über die Geburt"
    ),
    ExpectedMoment(
        name="Glück ist Akzeptanz",
        hook_keywords=["glück", "akzeptanz", "happiness is a function"],
        start_range=(750, 800),
        end_range=(830, 880),
        pattern="insight",
        notes="Philosophische Einsicht über Glück"
    ),
    ExpectedMoment(
        name="Erfolg / Der Weg ist das Ziel",
        hook_keywords=["erfolg", "weg ist das ziel", "buddha", "road to happiness"],
        start_range=(1280, 1320),
        end_range=(1390, 1420),
        pattern="clean_extraction",
        notes="Erfolg-Definition und Buddha-Zitat"
    ),
    ExpectedMoment(
        name="Lebenslinie / Is that all there is",
        hook_keywords=["armstrong", "mond", "is that all there is"],
        start_range=(1595, 1630),
        end_range=(1660, 1700),
        pattern="story_hook",
        notes="Armstrong auf dem Mond Geschichte"
    ),
]


def load_discovered_moments(results_path: Path) -> List[dict]:
    """Lade die vom System gefundenen Momente."""
    with open(results_path) as f:
        return json.load(f)


def check_moment_found(expected: ExpectedMoment, discovered: List[dict]) -> dict:
    """
    Prüfe ob ein erwarteter Moment gefunden wurde.
    
    Returns:
        dict mit 'found', 'match', 'issues'
    """
    result = {
        "expected": expected.name,
        "found": False,
        "match": None,
        "issues": []
    }
    
    for moment in discovered:
        # Check hook keywords
        hook_text = moment.get("hook_text", "").lower()
        moment_text = " ".join([s.get("text", "") for s in moment.get("segments", [])]).lower()
        full_text = hook_text + " " + moment_text
        
        keyword_match = any(kw in full_text for kw in expected.hook_keywords)
        
        if not keyword_match:
            continue
            
        # Found a potential match
        result["found"] = True
        result["match"] = moment
        
        # Check timing
        start = moment.get("start", 0)
        end = moment.get("end", 0)
        
        if not (expected.start_range[0] <= start <= expected.start_range[1]):
            result["issues"].append(
                f"Start {start:.1f}s outside expected range {expected.start_range}"
            )
        
        if not (expected.end_range[0] <= end <= expected.end_range[1]):
            result["issues"].append(
                f"End {end:.1f}s outside expected range {expected.end_range}"
            )
        
        # Check pattern (if provided)
        detected_pattern = moment.get("pattern", "unknown")
        if detected_pattern != expected.pattern and detected_pattern != "unknown":
            result["issues"].append(
                f"Pattern '{detected_pattern}' != expected '{expected.pattern}'"
            )
        
        break
    
    return result


def run_ground_truth_test(results_path: Path) -> dict:
    """
    Führe den vollständigen Ground Truth Test aus.
    
    Returns:
        dict mit Testergebnissen
    """
    print("\n" + "="*70)
    print("GROUND TRUTH TEST: Dieter Lange")
    print("="*70)
    
    discovered = load_discovered_moments(results_path)
    print(f"\n📊 System hat {len(discovered)} Momente gefunden")
    print(f"📋 Erwartete Momente: {len(EXPECTED_MOMENTS)}")
    
    results = {
        "total_expected": len(EXPECTED_MOMENTS),
        "found": 0,
        "not_found": 0,
        "with_issues": 0,
        "details": []
    }
    
    print("\n" + "-"*70)
    
    for expected in EXPECTED_MOMENTS:
        check = check_moment_found(expected, discovered)
        results["details"].append(check)
        
        if check["found"]:
            results["found"] += 1
            if check["issues"]:
                results["with_issues"] += 1
                status = "⚠️ FOUND (with issues)"
            else:
                status = "✅ FOUND"
        else:
            results["not_found"] += 1
            status = "❌ NOT FOUND"
        
        print(f"\n{status}: {expected.name}")
        print(f"   Keywords: {expected.hook_keywords[:2]}...")
        print(f"   Expected: {expected.start_range[0]:.0f}s - {expected.end_range[1]:.0f}s")
        
        if check["match"]:
            m = check["match"]
            print(f"   Found: {m.get('start', 0):.1f}s - {m.get('end', 0):.1f}s")
            print(f"   Hook: \"{m.get('hook_text', '')[:50]}...\"")
        
        for issue in check["issues"]:
            print(f"   ⚠️ {issue}")
    
    # Summary
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG")
    print("="*70)
    
    score = results["found"] / results["total_expected"] * 100
    
    print(f"\n✅ Gefunden: {results['found']}/{results['total_expected']} ({score:.0f}%)")
    print(f"❌ Nicht gefunden: {results['not_found']}")
    print(f"⚠️ Mit Problemen: {results['with_issues']}")
    
    if score >= 80:
        print("\n🎉 TEST BESTANDEN! System findet die wichtigsten Momente.")
    elif score >= 60:
        print("\n⚠️ TEST TEILWEISE BESTANDEN. Einige Momente fehlen.")
    else:
        print("\n❌ TEST NICHT BESTANDEN. System muss verbessert werden.")
    
    return results


def create_mock_results_for_testing():
    """
    Erstelle Mock-Ergebnisse um den Test selbst zu testen.
    
    In Production wird das durch echte System-Ergebnisse ersetzt.
    """
    mock_results = [
        {
            "start": 564.63,
            "end": 655.12,
            "hook_text": "Arbeite niemals für Geld",
            "segments": [{"text": "Arbeite niemals für Geld. Horde Kinder sitzt am Straßenrand..."}],
            "pattern": "hook_extraction",
            "viral_potential": 9.2
        },
        {
            "start": 480.0,
            "end": 534.0,
            "hook_text": "Aus einem Ackergaul wird kein Rennpferd",
            "segments": [{"text": "Aus einem Ackergaul wird kein Rennpferd. Talent ist das..."}],
            "pattern": "clean_extraction",
            "viral_potential": 8.5
        },
        {
            "start": 321.0,
            "end": 345.0,
            "hook_text": "Was willst du eigentlich mal werden?",
            "segments": [{"text": "Was willst du eigentlich mal werden? Das impliziert doch..."}],
            "pattern": "beliefbreaker",
            "viral_potential": 8.8
        },
    ]
    
    mock_path = Path(__file__).parent / "mock_dieter_lange_results.json"
    with open(mock_path, "w") as f:
        json.dump(mock_results, f, indent=2)
    
    return mock_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        results_path = Path(sys.argv[1])
    else:
        # Create mock for testing the test itself
        print("Kein Ergebnis-Pfad angegeben. Erstelle Mock-Daten...")
        results_path = create_mock_results_for_testing()
    
    results = run_ground_truth_test(results_path)
    
    # Exit code based on results
    if results["found"] / results["total_expected"] >= 0.6:
        sys.exit(0)
    else:
        sys.exit(1)

