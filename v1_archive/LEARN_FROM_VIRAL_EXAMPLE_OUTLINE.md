# 📚 LEARN FROM VIRAL EXAMPLE - Script Outline

## 🎯 ZWECK
Von erfolgreichen Clip-Beispielen lernen wie man Restrukturierung macht.
Extrahiert Patterns und Templates für zukünftige Clip-Erstellung.

---

## 📋 SCRIPT STRUKTUR

### 1. IMPORTS & SETUP
```python
#!/usr/bin/env python3
"""
📚 LEARN FROM VIRAL EXAMPLE

Analysiert erfolgreiche Clips und extrahiert Restrukturierungs-Patterns.
"""

import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from master_learnings import load_master_learnings, save_master_learnings
```

---

### 2. CLASS: ViralExampleLearner

#### 2.1 __init__()
```python
def __init__(self):
    # API Client
    self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    
    # Paths
    self.data_dir = Path("data")
    self.examples_dir = self.data_dir / "viral_examples"
    self.examples_dir.mkdir(parents=True, exist_ok=True)
    
    # Master Learnings
    self.master_learnings = load_master_learnings()
```

#### 2.2 INPUT HANDLING

**load_transcript()**
- Lädt Transcript aus Datei oder erstellt aus Video
- Unterstützt: JSON (Whisper), TXT, SRT
- Returns: List of segments with timestamps

**load_clip_data()**
- Lädt Clip-Transcript ODER verwendet Timestamps
- Wenn Timestamps: Extrahiert Segmente aus Longform
- Returns: Clip segments + metadata

**load_performance_data()**
- Lädt Performance-Daten (JSON oder CLI input)
- Validates: Views, Watch Time %, Followers
- Returns: Dict mit Performance-Metriken

---

### 3. ANALYSIS FUNCTIONS

#### 3.1 compare_transcripts()
```python
def compare_transcripts(
    longform_segments: List[Dict],
    clip_segments: List[Dict]
) -> Dict:
    """
    Vergleicht Longform vs Clip Transcript
    
    Returns:
    {
        "used_segments": [
            {
                "original_start": 120.5,
                "original_end": 145.0,
                "clip_start": 0.0,
                "clip_end": 24.5,
                "text": "...",
                "role": "hook/context/content/payoff"
            }
        ],
        "removed_segments": [...],
        "restructuring": {
            "original_order": [120.5, 145.0, 200.0],
            "clip_order": [200.0, 120.5, 145.0],
            "reordered": True
        },
        "coverage": {
            "original_duration": 1800.0,
            "clip_duration": 45.0,
            "coverage_percent": 2.5
        }
    }
    """
```

**Logik:**
- Text-Matching zwischen Segments
- Timestamp-Mapping
- Identifiziert welche Teile verwendet wurden
- Erkennt neue Reihenfolge (Restrukturierung)
- Berechnet Coverage

#### 3.2 analyze_restructuring()
```python
def analyze_restructuring(comparison_result: Dict) -> Dict:
    """
    Analysiert die Restrukturierung im Detail
    
    Returns:
    {
        "hook_strategy": {
            "original_position": 200.0,
            "clip_position": 0.0,
            "moved_to_front": True,
            "hook_text": "...",
            "hook_type": "controversy/story/question"
        },
        "structure_pattern": {
            "original": "A→B→C→D",
            "clip": "C→A→B",
            "pattern": "payoff_first_then_context"
        },
        "removed_parts": {
            "intro": True,
            "filler": True,
            "repetition": True
        },
        "compression_ratio": 0.025
    }
    """
```

**Logik:**
- Identifiziert Hook-Position (original vs clip)
- Erkennt Struktur-Pattern
- Analysiert was entfernt wurde
- Berechnet Kompressions-Ratio

---

### 4. PATTERN EXTRACTION

#### 4.1 extract_hook_patterns()
```python
def extract_hook_patterns(
    hook_segment: Dict,
    performance: Dict
) -> Dict:
    """
    Extrahiert Hook-Patterns
    
    Returns:
    {
        "hook_text": "...",
        "hook_type": "controversy/story/question",
        "first_words": ["Warum", "Der", "größte"],
        "emotional_trigger": "curiosity/anger/surprise",
        "information_gap": True,
        "effectiveness": 0.95  # basierend auf Performance
    }
    """
```

#### 4.2 extract_structure_patterns()
```python
def extract_structure_patterns(
    restructuring: Dict,
    performance: Dict
) -> Dict:
    """
    Extrahiert Struktur-Patterns
    
    Returns:
    {
        "pattern_name": "payoff_first_then_context",
        "structure": {
            "hook": "0-3s",
            "context": "3-15s",
            "content": "15-40s",
            "payoff": "40-45s"
        },
        "timing": {
            "hook_duration": 3.0,
            "first_loop": 3.0,
            "pattern_interrupts": [10.0, 25.0],
            "total_duration": 45.0
        },
        "effectiveness": 0.92
    }
    """
```

#### 4.3 extract_tension_arc()
```python
def extract_tension_arc(
    clip_segments: List[Dict],
    performance: Dict
) -> Dict:
    """
    Analysiert Spannungsbogen
    
    Returns:
    {
        "arc_type": "rising/plateau/falling",
        "tension_points": [
            {"time": 0.0, "level": 9, "reason": "Hook"},
            {"time": 10.0, "level": 7, "reason": "Context"},
            {"time": 25.0, "level": 8, "reason": "Pattern Interrupt"}
        ],
        "average_tension": 7.5,
        "min_tension": 5.0,
        "max_tension": 9.0
    }
    """
```

---

### 5. TEMPLATE CREATION

#### 5.1 create_template()
```python
def create_template(
    patterns: Dict,
    restructuring: Dict,
    performance: Dict
) -> Dict:
    """
    Erstellt wiederverwendbares Template
    
    Returns:
    {
        "template_id": "template_001",
        "name": "Controversy Hook + Payoff First",
        "description": "Für Videos mit kontroversen Aussagen",
        "when_to_use": [
            "Video enthält kontroverse Meinung",
            "Starker Payoff-Moment vorhanden",
            "Original-Struktur langsam"
        ],
        "structure": {
            "step_1": "Finde stärksten Payoff-Moment",
            "step_2": "Platziere als Hook (0-3s)",
            "step_3": "Füge Context hinzu (3-15s)",
            "step_4": "Rest des Contents (15-40s)",
            "step_5": "Kleiner Payoff am Ende (40-45s)"
        },
        "hook_formula": "Warum [kontraintuitives Statement]",
        "optimal_length": {
            "min": 30,
            "max": 60,
            "sweet_spot": 45
        },
        "success_rate": 0.92,
        "examples": ["example_001"]
    }
    """
```

**Logik:**
- Kombiniert alle extrahierten Patterns
- Erstellt anwendbare Anleitung
- Definiert "when to use" Kriterien
- Berechnet Success Rate basierend auf Performance

---

### 6. AI-POWERED ANALYSIS

#### 6.1 ai_analyze_example()
```python
def ai_analyze_example(
    longform_segments: List[Dict],
    clip_segments: List[Dict],
    performance: Dict,
    notes: Optional[str] = None
) -> Dict:
    """
    Nutzt AI für tiefere Analyse
    
    Prompt:
    - Vergleich beider Transcripts
    - Performance-Kontext
    - Extrahiere Patterns
    - Erstelle Template
    
    Returns: Vollständige Analyse mit Patterns
    """
```

**Prompt-Struktur:**
```
Du bist ein Elite-Content-Analyst.

LONGFORM TRANSCRIPT:
[full transcript]

CLIP TRANSCRIPT:
[clip transcript]

PERFORMANCE:
- Views: X
- Watch Time: Y%
- Followers: Z

AUFGABE:
1. Vergleiche beide Transcripts
2. Identifiziere Restrukturierung
3. Extrahiere Hook-Patterns
4. Analysiere Struktur
5. Erstelle wiederverwendbares Template

[...]
```

---

### 7. MASTER LEARNINGS INTEGRATION

#### 7.1 update_master_learnings()
```python
def update_master_learnings(
    example_data: Dict
) -> None:
    """
    Fügt Beispiel zu MASTER_LEARNINGS hinzu
    
    Neue Section:
    {
        "viral_examples": [
            {
                "example_id": "...",
                "learned_at": "...",
                "performance": {...},
                "patterns": {...},
                "template": {...}
            }
        ]
    }
    """
```

**Logik:**
- Lädt aktuelle MASTER_LEARNINGS
- Fügt neues Beispiel hinzu
- Aktualisiert Hook-Mastery wenn neues Pattern
- Aktualisiert Structure-Mastery
- Speichert zurück

---

### 8. CLI INTERFACE

#### 8.1 argparse Setup
```python
parser = argparse.ArgumentParser(
    description="Learn from viral clip examples"
)

parser.add_argument(
    "--longform",
    required=True,
    help="Path to longform video or transcript"
)

parser.add_argument(
    "--clip",
    required=True,
    help="Path to clip transcript OR timestamps (start:end)"
)

parser.add_argument(
    "--performance",
    required=True,
    help="Performance data: views,watch_time,followers OR JSON file"
)

parser.add_argument(
    "--notes",
    help="Optional notes why it worked"
)

parser.add_argument(
    "--output",
    default="data/viral_examples",
    help="Output directory"
)
```

#### 8.2 main()
```python
def main():
    args = parse_args()
    
    learner = ViralExampleLearner()
    
    # 1. Load inputs
    longform = learner.load_transcript(args.longform)
    clip = learner.load_clip_data(args.clip, longform)
    performance = learner.load_performance_data(args.performance)
    
    # 2. Analyze
    comparison = learner.compare_transcripts(longform, clip)
    restructuring = learner.analyze_restructuring(comparison)
    
    # 3. Extract patterns
    hook_patterns = learner.extract_hook_patterns(...)
    structure_patterns = learner.extract_structure_patterns(...)
    tension_arc = learner.extract_tension_arc(...)
    
    # 4. AI Analysis
    ai_analysis = learner.ai_analyze_example(...)
    
    # 5. Create template
    template = learner.create_template(...)
    
    # 6. Save example
    example_data = {
        "example_id": generate_id(),
        "original_length": ...,
        "clip_length": ...,
        "performance": performance,
        "restructuring": restructuring,
        "patterns": {
            "hook": hook_patterns,
            "structure": structure_patterns,
            "tension": tension_arc
        },
        "template": template,
        "learned_at": datetime.now().isoformat()
    }
    
    learner.save_example(example_data)
    learner.update_master_learnings(example_data)
    
    print("✅ Example learned and integrated!")
```

---

## 📁 OUTPUT STRUCTURE

### data/viral_examples/
```
viral_examples/
├── example_001.json
├── example_002.json
└── index.json
```

### data/MASTER_LEARNINGS.json
```json
{
    "...existing sections...",
    "viral_examples": [
        {
            "example_id": "example_001",
            "learned_at": "2025-01-XX",
            "performance": {...},
            "patterns": {...},
            "template": {...}
        }
    ]
}
```

---

## 🔄 WORKFLOW

```
1. INPUT
   ├── Longform Transcript
   ├── Clip Transcript/Timestamps
   ├── Performance Data
   └── Optional Notes

2. COMPARISON
   ├── Map Segments
   ├── Identify Used Parts
   └── Detect Restructuring

3. ANALYSIS
   ├── Hook Analysis
   ├── Structure Analysis
   └── Tension Arc Analysis

4. PATTERN EXTRACTION
   ├── Hook Patterns
   ├── Structure Patterns
   └── Timing Patterns

5. TEMPLATE CREATION
   └── Reusable Template

6. INTEGRATION
   ├── Save Example
   └── Update MASTER_LEARNINGS
```

---

## 🎯 KEY FEATURES

✅ **Flexible Input**: Video, Transcript, oder Timestamps
✅ **AI-Powered**: Tiefe Analyse mit Claude
✅ **Pattern Extraction**: Automatische Pattern-Erkennung
✅ **Template Creation**: Wiederverwendbare Templates
✅ **Master Learnings Integration**: Automatisches Update
✅ **CLI Interface**: Einfache Nutzung
✅ **Error Handling**: Robust gegen Fehler

---

## 📊 EXAMPLE OUTPUT

```json
{
    "example_id": "example_001",
    "original_length": 1800.0,
    "clip_length": 45.0,
    "performance": {
        "views": 500000,
        "watch_time_percent": 85,
        "followers_gained": 5000
    },
    "restructuring": {
        "hook_strategy": {
            "original_position": 200.0,
            "clip_position": 0.0,
            "moved_to_front": true
        },
        "structure_pattern": "payoff_first_then_context"
    },
    "patterns": {
        "hook": {...},
        "structure": {...},
        "tension": {...}
    },
    "template": {
        "name": "Controversy Hook + Payoff First",
        "when_to_use": [...],
        "structure": {...}
    }
}
```

---

## ✅ NEXT STEPS

1. Implementiere alle Funktionen
2. Teste mit realen Beispielen
3. Integriere in create_clips_v2.py
4. Nutze Templates für automatische Restrukturierung

