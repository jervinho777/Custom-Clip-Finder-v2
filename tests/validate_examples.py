#!/usr/bin/env python3
"""
Validation: Prüft ob das System die bekannten Viral Clips finden würde.

Bekannte Longform → Clip Paare:
1. Dieter Lange → "Arbeite niemals für Geld" (Hook Extraction)
2. Dr. Stefan Frädrich → "Lebenslinie" (Clean Extraction)
3. Chris Surel → Tiefschlaf Clips

Das System MUSS diese Momente finden, sonst funktioniert es nicht!
"""

import json
from pathlib import Path


# =====================================================
# GROUND TRUTH: Bekannte Viral Clips
# =====================================================

KNOWN_PAIRS = [
    {
        "longform": "Dieter Lange_transcript.json",
        "clip": "Dieter Lange Viral Clip_transcript.json",
        "clip_name": "Arbeite niemals für Geld",
        "original_start": 564.63,  # Geschichte beginnt
        "original_end": 655.12,    # "Arbeite niemals für Geld"
        "hook_text": "Arbeite niemals für Geld",
        "pattern": "hook_extraction",
        "note": "Payoff 'Arbeite niemals für Geld' wird zum Hook gezogen"
    },
    {
        "longform": "Dr_Stefan_Frädrich_transcript.json", 
        "clip": "Lebenslinie V2_NOCTA_transcript.json",
        "clip_name": "Lebenslinie",
        "original_start": 1066.09,  # "Dein Leben findet statt..."
        "original_end": 1165.18,    # "...probierst mal die Kellnerin aus"
        "hook_text": "Dein Leben findet statt auf einer Lebenslinie",
        "pattern": "clean_extraction",
        "note": "Hook war schon stark, wurde nur gekürzt"
    },
    {
        "longform": "Chris Surel_transcript.json",
        "clip": "top02_Chris Surel_Beliefbreaker Headline - Metapher - Wissen - Loop_transcript.json",
        "clip_name": "Tiefschlafverdichtung",
        "original_start": 112.35,  # Tiefschlafverdichtung Erklärung
        "original_end": 185.35,
        "hook_text": "Tiefschlafverdichtung",
        "pattern": "unknown",
        "note": "Vermutlich Hook Extraction oder Clean"
    },
]


def load_transcript(path: Path) -> dict:
    """Load transcript JSON."""
    with open(path) as f:
        return json.load(f)


def find_text_in_segments(segments: list, search_text: str) -> list:
    """Find segments containing search text."""
    search_lower = search_text.lower()
    matches = []
    
    for seg in segments:
        if search_lower in seg.get("text", "").lower():
            matches.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"][:100]
            })
    
    return matches


def analyze_pair(pair: dict, transcripts_dir: Path):
    """Analyze a longform→clip pair."""
    print(f"\n{'='*70}")
    print(f"PAIR: {pair['clip_name']}")
    print(f"{'='*70}")
    
    longform_path = transcripts_dir / pair["longform"]
    clip_path = transcripts_dir / pair["clip"]
    
    # Load transcripts
    if not longform_path.exists():
        print(f"  ⚠️ Longform nicht gefunden: {longform_path.name}")
        return None
        
    longform = load_transcript(longform_path)
    segments = longform.get("segments", [])
    
    print(f"\n📹 LONGFORM: {pair['longform']}")
    print(f"   Segments: {len(segments)}")
    duration = segments[-1]["end"] if segments else 0
    print(f"   Dauer: {duration/60:.1f} min")
    
    # Find hook in longform
    print(f"\n🎯 HOOK SUCHE: '{pair['hook_text']}'")
    matches = find_text_in_segments(segments, pair["hook_text"])
    
    if matches:
        for m in matches:
            print(f"   ✅ Gefunden bei {m['start']:.1f}s: \"{m['text']}...\"")
    else:
        # Try partial match
        words = pair["hook_text"].split()[:3]
        partial = " ".join(words)
        matches = find_text_in_segments(segments, partial)
        if matches:
            print(f"   ⚠️ Partial match '{partial}':")
            for m in matches:
                print(f"      {m['start']:.1f}s: \"{m['text']}...\"")
        else:
            print(f"   ❌ Nicht gefunden!")
    
    # Expected location
    print(f"\n📍 EXPECTED LOCATION:")
    print(f"   Original: {pair['original_start']:.1f}s - {pair['original_end']:.1f}s")
    print(f"   Duration: {pair['original_end'] - pair['original_start']:.1f}s")
    print(f"   Pattern: {pair['pattern']}")
    
    # Load clip if exists
    if clip_path.exists():
        clip = load_transcript(clip_path)
        clip_segments = clip.get("segments", [])
        clip_duration = clip_segments[-1]["end"] if clip_segments else 0
        
        print(f"\n📱 VIRAL CLIP: {pair['clip']}")
        print(f"   Dauer: {clip_duration:.1f}s")
        
        # First sentence of clip
        if clip_segments:
            first = clip_segments[0]["text"][:100]
            print(f"   Hook: \"{first}...\"")
    
    print(f"\n📝 SYSTEM MUSS:")
    print(f"   1. Diesen Moment im DISCOVER Stage finden")
    print(f"   2. Als '{pair['pattern']}' klassifizieren in COMPOSE")
    print(f"   3. Hook Strength >= 8 vergeben")
    
    return {
        "name": pair["clip_name"],
        "found": len(matches) > 0,
        "pattern": pair["pattern"]
    }


def main():
    """Run validation."""
    print("\n" + "="*70)
    print("SYSTEM VALIDATION: Bekannte Viral Clips")
    print("="*70)
    print("\nPrüft ob das System die bekannten erfolgreichen Clips finden würde.")
    
    transcripts_dir = Path(__file__).parent.parent / "data" / "cache" / "transcripts"
    
    if not transcripts_dir.exists():
        print(f"\n❌ Transcripts dir not found: {transcripts_dir}")
        return
    
    files = list(transcripts_dir.glob("*.json"))
    print(f"\n📁 Gefundene Transcripts: {len(files)}")
    
    # Categorize
    longforms = [f for f in files if not f.stem.startswith("top") and "Viral" not in f.stem and "NOCTA" not in f.stem]
    clips = [f for f in files if f.stem.startswith("top") or "Viral" in f.stem or "NOCTA" in f.stem]
    
    print(f"   Longforms: {len(longforms)}")
    print(f"   Clips: {len(clips)}")
    
    # Analyze known pairs
    results = []
    for pair in KNOWN_PAIRS:
        result = analyze_pair(pair, transcripts_dir)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG")
    print("="*70)
    
    found = sum(1 for r in results if r["found"])
    print(f"\n✅ Gefunden: {found}/{len(results)} bekannte Viral-Momente")
    
    if found == len(results):
        print("\n🎉 Das System SOLLTE diese Clips finden können!")
    else:
        print("\n⚠️ Einige Clips wurden nicht gefunden - System prüfen!")
    
    print("\n" + "="*70)
    print("KRITISCHE PATTERNS DIE FUNKTIONIEREN MÜSSEN:")
    print("="*70)
    print("""
1. HOOK EXTRACTION (Dieter Lange)
   - Payoff-Statement am ENDE der Story erkennen
   - Als starken Hook bewerten
   - Vorschlagen: "Ziehe diesen Satz nach vorne"

2. CLEAN EXTRACTION (Frädrich Lebenslinie)  
   - Starken natürlichen Hook erkennen
   - Story-Arc identifizieren
   - Saubere Grenzen finden

3. DYNAMISCHE CLIP-ANZAHL
   - NICHT pauschal 15 Clips
   - So viele wie MÖGLICH, so viele wie NÖTIG
   - Qualität > Quantität
""")


if __name__ == "__main__":
    main()


