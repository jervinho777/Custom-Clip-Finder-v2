# 🎬 SYSTEM ÜBERSICHT - Custom Clip Finder V4

## 📋 Inhaltsverzeichnis

1. [System-Architektur](#system-architektur)
2. [Hauptdateien](#hauptdateien)
3. [Pipeline-Struktur](#pipeline-struktur)
4. [Detaillierte Stage-Beschreibungen](#detaillierte-stage-beschreibungen)
5. [Klassen & Methoden](#klassen--methoden)
6. [Datenfluss](#datenfluss)
7. [Kosten-Breakdown](#kosten-breakdown)

---

## 🏗️ SYSTEM-ARCHITEKTUR

### Hauptkomponenten

```
create_clips_v4_integrated.py (Hauptsystem)
├── OpenLoopBridging (Stage 1.75)
├── CreateClipsV4Integrated (Hauptklasse)
│   ├── ConsensusEngine (Multi-AI Konsens)
│   ├── PremiumAIEnsemble (5-AI Ensemble)
│   └── Pipeline Stages (0 → 1 → 1.75 → 2 → 2.5 → 2.6 → 2.7 → 2.8 → Godmode)
└── Externe Abhängigkeiten
    ├── create_clips_v2.py (Basis-Funktionalität)
    ├── create_clips_v3_ensemble.py (AI-Ensemble)
    └── master_learnings_v2.py (Viral-Pattern-Learnings)
```

---

## 📁 HAUPTDATEIEN

### 1. `create_clips_v4_integrated.py` (Hauptsystem)
**Rolle:** Zentrale Pipeline für virale Clip-Erstellung
**Größe:** ~5500 Zeilen
**Enthält:**
- `OpenLoopBridging` Klasse (Stage 1.75)
- `CreateClipsV4Integrated` Klasse (Haupt-Pipeline)
- Alle 8 Pipeline-Stages
- Godmode-Evaluation

### 2. `create_clips_v3_ensemble.py`
**Rolle:** Multi-AI Konsens-Engine
**Enthält:**
- `ConsensusEngine` Klasse
- `PremiumAIEnsemble` Klasse
- Parallel-Voting-Mechanismus
- AI-Model-Management

### 3. `create_clips_v2.py`
**Rolle:** Basis-Funktionalität
**Enthält:**
- Transcription-Logik
- Segment-Verarbeitung
- Basis-Extraktion

### 4. `master_learnings_v2.py`
**Rolle:** Viral-Pattern-Datenbank
**Enthält:**
- 175 analysierte virale Clips
- Pattern-Library
- Erfolgsraten
- Optimal-Duration-Ranges

### 5. `test_2stage_cached.py`
**Rolle:** Test- & Demo-Script
**Enthält:**
- Pipeline-Tests
- Caching-Mechanismus
- Beispiel-Ausführung

---

## 🔄 PIPELINE-STRUKTUR

### Vollständiger Ablauf

```
VIDEO INPUT
    ↓
TRANSCRIPTION (Whisper)
    ↓
STAGE 0: Coarse Viral Scan
    ↓ (20-30 Seeds)
STAGE 1: Batch Refinement
    ↓ (20-30 Refined Moments)
STAGE 1.75: Open Loop Bridging
    ↓ (Extended Moments)
STAGE 2: Conditional Restructure
    ↓ (Polished Moments)
STAGE 2.5: Learning-Based Cuts
    ↓ (Viral-Optimized)
STAGE 2.6: Cross-Moment Hook Extraction
    ↓ (Hook-Enhanced)
STAGE 2.7: Micro-Level Text Optimization
    ↓ (Micro-Optimized)
STAGE 2.8: Dramatic Structure & Timing
    ↓ (Dramatically Timed)
GODMODE: Batched Premium Evaluation
    ↓ (6-10 Viral Moments, Score 40+/50)
EXPORT: MP4 + JSON Metadata
```

---

## 📊 DETAILLIERTE STAGE-BESCHREIBUNGEN

### STAGE 0: Coarse Viral Scan
**Methode:** `coarse_viral_scan()`
**Ziel:** Schnelle, breite Suche nach viralen Potenzialen
**Strategie:** Pattern-agnostisch, findet ALLE Aufmerksamkeits-Signale

**Prozess:**
1. Scant gesamtes Video (alle Segmente)
2. Identifiziert 30-50 "Seeds" (grobe Kandidaten)
3. Pre-Scoring (0-100) basierend auf Prinzipien
4. Returniert Top 20 Seeds

**Prinzipien:**
- COMPLETENESS for what it IS
- NATURAL BOUNDARIES
- EMOTIONAL INTENSITY
- PATTERN INTERRUPTS
- FORMAT FLEXIBILITY
- CONTEXT AWARENESS

**AI-Modell:** Sonnet 4.5 (1 Call)
**Kosten:** ~$1.50
**Dauer:** ~2 Minuten

**Output:**
```python
[
  {
    'start': 123.5,
    'end': 187.3,
    'viral_score': 85,
    'reason': 'Complete story with surprise twist...'
  },
  ...
]
```

---

### STAGE 1: Principle-Based Batch Refinement
**Methode:** `_refine_moments_parallel()`
**Ziel:** Findet optimale Grenzen für jeden Seed
**Strategie:** Batch-Verarbeitung (5 Seeds pro Batch)

**Prozess:**
1. Gruppiert Seeds in Batches (5 pro Batch)
2. Für jeden Batch:
   - AI analysiert alle 5 Seeds zusammen
   - Findet natürliche Start/End-Grenzen
   - Validiert Vollständigkeit (Completeness Score 0-100)
3. Self-Critique wenn Completeness < 90%
4. Returniert 20-30 refined moments

**Adaptive Analyse:**
- Identifiziert Moment-Typ (Story, Insight, Rant, etc.)
- Findet natürliche Grenzen für DIESEN Typ
- Validiert: Hat Setup? Hat Payoff? Funktioniert standalone?

**AI-Modell:** Sonnet 4.5 (4 Calls für 20 Seeds)
**Kosten:** ~$0.60
**Dauer:** ~3 Minuten

**Output:**
```python
{
  'start': 123.5,
  'end': 187.3,
  'duration': 63.8,
  'moment_type': 'parable',
  'completeness_score': 92,
  'segments': [...],
  'viral_score': 85
}
```

---

### STAGE 1.75: Open Loop Bridging
**Klasse:** `OpenLoopBridging`
**Methode:** `detect_and_bridge()`
**Ziel:** Brückt kleine Lücken (<5s) bei offenen Loops
**Strategie:** Rule-based (kein AI-Call)

**Prozess:**
1. Prüft ob Moment mit Frage endet
2. Sucht nach Antwort in nächsten Segmenten (<5s Gap)
3. Wenn gefunden: Erweitert Moment um Payoff-Segmente

**Patterns:**
- Open Loop: "Was ist hier passiert?", "Warum?", etc.
- Answer: "weil", "der Grund", "das bedeutet", etc.

**Beispiel:**
```
Vorher: Moment endet bei 52s mit "Was ist hier passiert?"
Nachher: Moment erweitert auf 59s mit "...Die Freude am Tun ist ersetzt..."
```

**Kosten:** $0.00 (rule-based)
**Dauer:** <1 Sekunde

---

### STAGE 2: Principle-Based Conditional Restructure
**Methode:** `_conditional_restructure()`
**Ziel:** Restrukturiert nur Momente, die es brauchen
**Strategie:** Pre-Check → Batch-Restructure

**Prozess:**
1. Pre-Check: `_needs_restructure()`
   - Prüft Filler-Dichte (>30% = Problem)
   - Prüft Repetition (exzessiv = Problem)
   - Prüft Rambling (langsam + lang = Problem)
2. Nur Momente mit Issues werden restrukturiert
3. Batch-Restructure (3 Momente pro Batch)
4. AI entfernt nur Problem-Bereiche

**Prinzipien:**
- COMPLETENESS: Maintain complete arc
- CLARITY: Remove noise, keep substance
- CONTEXT: Preserve speaker's style
- FORMAT: Respect the medium

**AI-Modell:** Sonnet 4.5 (4 Calls für ~12 Momente)
**Kosten:** ~$0.30
**Dauer:** ~2 Minuten

**Output:**
```python
{
  'restructured': True,
  'restructure_issues': ['high_filler_density'],
  'segments': [...],  # Nur behaltene Segmente
  'duration': 58.3  # Reduziert von 65s
}
```

---

### STAGE 2.5: Learning-Based Intelligent Cuts
**Methode:** `_learning_based_cuts()`
**Ziel:** Optimiert Duration basierend auf 175 analysierten Clips
**Strategie:** Pattern-basierte Duration-Targets

**Prozess:**
1. Detektiert Moment-Typ (Story, Insight, Rant, Parable)
2. Lädt optimal Duration-Range für diesen Typ:
   - Story: 45-65s
   - Insight: 20-40s
   - Rant: 30-50s
   - Parable: 50-70s
3. Wenn außerhalb Range: AI macht intelligente Cuts
4. Ziel: Hook in ersten 3s, Payoff in letzten 5-10s

**Beispiel:**
```
Input: 87s Parable
Target: 50-70s (optimal für Parable)
AI-Cuts: Entfernt rambling, strafft middle
Output: 59.4s (perfekt!)
```

**AI-Modell:** Sonnet 4.5 (1 Call pro Moment)
**Kosten:** ~$0.30 (für 20 Momente)
**Dauer:** ~2 Minuten

---

### STAGE 2.6: Cross-Moment Hook Extraction
**Methode:** `_cross_moment_hook_extraction()`
**Ziel:** Findet stärkste Hooks im gesamten Video
**Strategie:** Scan → Match → Pre-pend

**Prozess:**
1. `_extract_power_hooks()`: Scannt gesamtes Video
   - Findet 10 stärkste Hooks (0-100 Score)
   - Typen: Bold Statement, Question, Contrarian, etc.
2. Für jeden Moment:
   - Prüft ob bereits starker Hook vorhanden (`_has_strong_hook()`)
   - Wenn nicht: Findet besten Match (`_find_best_hook_match()`)
   - Pre-pendet Hook wenn thematisch passend

**Beispiel:**
```
Moment: Dieter Lange Story (52s)
Hook gefunden: "Arbeite niemals für Geld" (bei 120s)
Match: Thematisch passend (work/money Thema)
Result: Moment startet jetzt mit Hook (65s total)
```

**AI-Modell:** Sonnet 4.5
**Kosten:** ~$3.15 (1 Hook-Extraction + 20 Matchings)
**Dauer:** ~5 Minuten

---

### STAGE 2.7: Micro-Level Text Optimization
**Methode:** `_micro_text_optimization()`
**Ziel:** Wort-Level Präzision (nicht Segment-Level)
**Strategie:** Entfernt Filler WÖRTER, nicht ganze Segmente

**Prozess:**
1. Für jeden Moment:
   - Ziel: 5-10% Reduktion via Micro-Cuts
   - AI analysiert jeden Segment-Text
   - Entfernt:
     - Unnötige Descriptors ("wie Kinder manchmal sind")
     - Verbose Transitions ("Als der Alte am nächsten Tag kommt" → "Nächster Tag")
     - Obvious Statements ("Das ist klar")
     - Filler Words (vorsichtig!)
2. Berechnet neue Duration basierend auf Textlängen-Reduktion

**Prinzipien:**
- Every Word Earns Its Place
- Don't over-edit (Füllwörter können Authentizität hinzufügen)
- Preserve speaker's voice

**Beispiel:**
```
Vorher: "gelangweilt, wie Kinder manchmal sind"
Nachher: "gelangweilt"
Zeitersparnis: ~1.2s
```

**AI-Modell:** Sonnet 4.5 (1 Call pro Moment)
**Kosten:** ~$3.00
**Dauer:** ~3 Minuten

---

### STAGE 2.8: Dramatic Structure & Timing
**Methode:** `_dramatic_timing_optimization()`
**Ziel:** Strategische Pausen für dramatische Wirkung
**Strategie:** Question → PAUSE → Answer

**Prozess:**
1. `_analyze_timing_opportunities()`: Analysiert jeden Moment
   - Identifiziert 3 Pausen-Typen:
     - Question → Answer (1.0-2.5s, optimal 1.5s)
     - Payoff Anticipation (0.5-1.5s, optimal 0.8s)
     - Emotional Beat (0.5-1.0s)
2. `_apply_dramatic_timing()`: Fügt Pausen-Marker ein
   - Erstellt Pause-Segmente: `[PAUSE: 1.5s]`
   - Passt Timestamps an
   - Berechnet neue Duration

**Beispiel:**
```
Vorher: "Was ist hier passiert? Die Freude am Tun..."
Nachher: "Was ist hier passiert?" → [PAUSE 1.5s] → "Die Freude am Tun..."
Duration: 61.8s → 64.1s (+2.3s für Drama)
```

**AI-Modell:** Sonnet 4.5 (1 Call pro Moment)
**Kosten:** ~$3.00
**Dauer:** ~3 Minuten

---

### GODMODE: Batched Premium Evaluation
**Methode:** `_batched_godmode_evaluation()`
**Ziel:** Finale Premium-Evaluation mit Opus 4
**Strategie:** Batched Evaluation (5 Momente pro Batch)

**Prozess:**
1. Gruppiert Momente in Batches (5 pro Batch)
2. Für jeden Batch:
   - Opus 4 evaluiert alle 5 Momente zusammen
   - Scoring: 0-50 (5 Dimensionen à 0-10)
   - Verdict: Accept (40+) oder Reject (<40)
3. Returniert nur akzeptierte Momente

**Scoring-Dimensionen:**
1. HOOK STRENGTH (0-10)
2. STORY COHERENCE (0-10)
3. NATURAL FLOW (0-10)
4. WATCHTIME POTENTIAL (0-10)
5. EMOTIONAL IMPACT (0-10)

**Prinzipien:** (Gleiche 6 wie Stage 0-2.8)

**AI-Modell:** Opus 4 (Premium)
**Kosten:** ~$0.80 (4 Batches)
**Dauer:** ~5 Minuten

**Output:**
```python
{
  'godmode_score': 44,
  'godmode_verdict': 'accept',
  'godmode_strengths': ['Complete arc', 'Emotional payoff'],
  'godmode_weaknesses': ['Slightly long setup'],
  'godmode_reasoning': 'Strong moment with...'
}
```

---

## 🏛️ KLASSEN & METHODEN

### `OpenLoopBridging` Klasse

**Zweck:** Brückt kleine Lücken bei offenen Loops

**Methoden:**
- `__init__(segments)`: Initialisiert mit allen Video-Segmenten
- `detect_and_bridge(moment)`: Hauptmethode
  - Prüft ob Moment mit Frage endet
  - Sucht Antwort in nächsten Segmenten
  - Erweitert Moment wenn gefunden
- `_find_payoff_segments(moment_end, max_gap, max_segs)`: Helper

**Patterns:**
- `OPEN_LOOP_PATTERNS`: Frage-Indikatoren
- `ANSWER_PATTERNS`: Antwort-Indikatoren

---

### `CreateClipsV4Integrated` Klasse

**Zweck:** Haupt-Pipeline-Klasse

**Wichtige Attribute:**
- `self.segments`: Alle Video-Segmente
- `self.story`: Story-Context
- `self.consensus`: ConsensusEngine Instanz
- `self.ensemble`: PremiumAIEnsemble Instanz

**Haupt-Methoden:**

#### Pipeline-Methoden:
1. `_find_moments_with_consensus()`: Haupt-Pipeline
2. `coarse_viral_scan()`: Stage 0
3. `_refine_moments_parallel()`: Stage 1
4. `_conditional_restructure()`: Stage 2
5. `_learning_based_cuts()`: Stage 2.5
6. `_cross_moment_hook_extraction()`: Stage 2.6
7. `_micro_text_optimization()`: Stage 2.7
8. `_dramatic_timing_optimization()`: Stage 2.8
9. `_batched_godmode_evaluation()`: Godmode

#### Helper-Methoden:
- `_needs_restructure(moment)`: Pre-Check für Restructure
- `_batch_restructure(moments)`: Batch-Restructure
- `_extract_power_hooks(segments)`: Hook-Extraction
- `_has_strong_hook(moment)`: Hook-Check
- `_find_best_hook_match(moment, hooks)`: Hook-Matching
- `_prepend_hook(moment, hook)`: Hook-Integration
- `_apply_micro_cuts(moment, target_duration)`: Micro-Cuts
- `_analyze_timing_opportunities(moment)`: Timing-Analyse
- `_apply_dramatic_timing(moment, timing_plan)`: Timing-Application
- `_parse_json_response(response)`: JSON-Parsing
- `_format_segments_for_prompt(segments)`: Prompt-Formatting

---

## 🔀 DATENFLUSS

### Moment-Datenstruktur

```python
moment = {
    # Basis-Info
    'start': 123.5,           # Start-Zeit (Sekunden)
    'end': 187.3,            # End-Zeit
    'duration': 63.8,        # Dauer
    
    # Segmente
    'segments': [            # Liste von Segmenten
        {
            'start': 123.5,
            'end': 125.8,
            'text': 'Arbeite niemals für Geld',
            'is_pause': False  # True für Pause-Marker
        },
        ...
    ],
    
    # Metadaten
    'viral_score': 85,       # Pre-Score (Stage 0)
    'moment_type': 'parable', # Typ (Story, Insight, etc.)
    'completeness_score': 92, # Vollständigkeit (0-100)
    
    # Stage-Flags
    'bridged_gap': True,     # Stage 1.75
    'restructured': True,    # Stage 2
    'learning_cuts': True,   # Stage 2.5
    'hook_enhanced': True,   # Stage 2.6
    'micro_optimized': True, # Stage 2.7
    'dramatic_timing': True, # Stage 2.8
    
    # Hook-Info (Stage 2.6)
    'hook_text': 'Arbeite niemals für Geld',
    'hook_strength': 95,
    'hook_theme': 'work_money',
    
    # Godmode-Info
    'godmode_score': 44,     # Final Score (0-50)
    'godmode_verdict': 'accept',
    'godmode_strengths': [...],
    'godmode_weaknesses': [...],
    'godmode_reasoning': '...'
}
```

### Transformation durch Stages

```
Stage 0 Output:
  Seeds: 20-30 grobe Kandidaten
  Duration: Variabel
  Segments: Grob

Stage 1 Output:
  Refined: 20-30 Momente
  Duration: Optimiert für Typ
  Segments: Präzise Grenzen

Stage 1.75 Output:
  Extended: Einige Momente erweitert
  Duration: +2-5s wenn Payoff gefunden
  Segments: Mit Payoff-Segmenten

Stage 2 Output:
  Polished: ~60% restrukturiert
  Duration: -5-10s wenn Filler entfernt
  Segments: Nur behaltene

Stage 2.5 Output:
  Optimized: Duration angepasst
  Duration: Im optimalen Range für Typ
  Segments: Intelligente Cuts

Stage 2.6 Output:
  Hook-Enhanced: ~50% mit Hooks
  Duration: +2-5s wenn Hook pre-pended
  Segments: Mit Hook-Segmenten am Start

Stage 2.7 Output:
  Micro-Optimized: Text gestrafft
  Duration: -3-5s via Wort-Level Cuts
  Segments: Optimierter Text

Stage 2.8 Output:
  Dramatically Timed: Mit Pausen
  Duration: +1-3s für strategische Pausen
  Segments: Mit Pause-Markern

Godmode Output:
  Viral Moments: 6-10 akzeptiert
  Score: 40-50/50
  Ready for Export
```

---

## 💰 KOSTEN-BREAKDOWN

### Pro Video (30 Minuten)

| Stage | AI-Model | Calls | Cost | Dauer |
|-------|----------|-------|------|-------|
| Stage 0 | Sonnet 4.5 | 1 | $1.50 | 2 min |
| Stage 1 | Sonnet 4.5 | 4 | $0.60 | 3 min |
| Stage 1.75 | - | 0 | $0.00 | <1s |
| Stage 2 | Sonnet 4.5 | 4 | $0.30 | 2 min |
| Stage 2.5 | Sonnet 4.5 | 20 | $0.30 | 2 min |
| Stage 2.6 | Sonnet 4.5 | 21 | $3.15 | 5 min |
| Stage 2.7 | Sonnet 4.5 | 20 | $3.00 | 3 min |
| Stage 2.8 | Sonnet 4.5 | 20 | $3.00 | 3 min |
| Godmode | Opus 4 | 4 | $0.80 | 5 min |
| **TOTAL** | | | **$12.65** | **~25 min** |

### Vergleich

- **Altes System:** $12.50 (6-AI Ensemble pro Moment)
- **Neues System:** $12.65 (aber viel bessere Qualität!)
- **Optimierung:** Batch-Verarbeitung statt einzelne Calls

---

## 🎯 STRATEGIEN & LOGIK

### Prinzipien-basiert (nicht rigid)

**Kern-Prinzipien:**
1. **COMPLETENESS for what it IS**
   - Story braucht Setup + Payoff
   - Insight braucht Context + Lesson
   - Rant braucht Buildup + Climax
   - Duration variiert je nach Typ

2. **NATURAL BOUNDARIES**
   - Start/End bei natürlichen Punkten
   - Pausen, Topic-Shifts, Emotionen
   - Nicht willkürliche Zeit-Marken

3. **EMOTIONAL INTENSITY**
   - Hooks Attention (varies by format)
   - Maintains Energy (context-dependent)
   - Creates Impact (different for each clip)

4. **PATTERN INTERRUPTS**
   - Breaks Expectations
   - Creates Curiosity
   - Reveals Insights

5. **FORMAT FLEXIBILITY**
   - Stage: Long-form energy works
   - Podcast: Natural flow
   - Live: Audience reactions matter

6. **CONTEXT AWARENESS**
   - Speaker style matters
   - Setting matters
   - Audience matters

### Adaptive vs. Rigid

**❌ RIGID (alt):**
- "Hook MUST be in 0-3s"
- "Must contain exact power words"
- "Duration MUST be 30-60s"
- "Pattern interrupt every 7s"

**✅ ADAPTIVE (neu):**
- "Hook in 0-5s window (flexible)"
- "Semantic intensity (not exact words)"
- "Duration based on pattern type"
- "Natural flow (not rigid timing)"

---

## 🔧 TECHNISCHE DETAILS

### Caching-Mechanismus

**Transcript-Cache:**
- Speichert: `data/cache/transcripts/{video_name}_transcript.json`
- Format: Whisper-Output mit Segments
- Wiederverwendung: Vermeidet Re-Transcription

**Pipeline-Cache:**
- Speichert: `data/cache/pipeline/{cache_key}.json`
- Format: Komplette Pipeline-Outputs
- Wiederverwendung: Schnelle Re-Runs

### Error-Handling

**Fallback-Strategien:**
- Wenn AI-Call fehlschlägt: Fallback zu Original
- Wenn Parsing fehlschlägt: Logging + Continue
- Wenn Moment invalid: Skip + Continue

**Robustheit:**
- Try-Catch in allen AI-Calls
- Validation nach jedem Stage
- Graceful Degradation

### Parallelisierung

**Batch-Verarbeitung:**
- Stage 1: 5 Seeds pro Batch
- Stage 2: 3 Momente pro Batch
- Godmode: 5 Momente pro Batch

**Vorteile:**
- Schneller (parallel statt sequential)
- Günstiger (weniger AI-Calls)
- Bessere Qualität (AI sieht Patterns)

---

## 📈 ERWARTETE ERGEBNISSE

### Input: 30-Minuten Video

**Output:**
- 6-10 virale Momente
- Score: 40-50/50
- Duration: 20-70s (pattern-abhängig)
- Ready für Export

### Beispiel: Dieter Lange Story

**Original:** 87s Story
**Nach Stage 2.5:** 59.4s (Learning-Based Cuts)
**Nach Stage 2.6:** 65s (+Hook "Arbeite niemals für Geld")
**Nach Stage 2.7:** 61.8s (Micro-Optimization)
**Nach Stage 2.8:** 64.1s (+Pausen für Drama)
**Final Score:** 44-48/50 ✅

---

## 🚀 VERWENDUNG

### Basis-Verwendung

```python
from create_clips_v4_integrated import CreateClipsV4Integrated

# Initialisieren
system = CreateClipsV4Integrated()

# Video transcribieren
await system.transcribe_video("path/to/video.mp4")

# Pipeline ausführen
viral_moments = await system._find_moments_with_consensus(
    video_path="path/to/video.mp4",
    segments=system.segments,
    cache_key="video_name"
)

# Exportieren
for moment in viral_moments:
    # Export logic...
```

### Test-Script

```bash
python test_2stage_cached.py "data/uploads/Dieter Lange.mp4" 10
```

---

## 📚 WEITERE DOKUMENTATION

- `FUNCTION_SIGNATURES.md`: Alle Methoden-Signaturen
- `MASTER_LEARNINGS.md`: Viral-Pattern-Datenbank
- `test_*.py`: Test-Scripts für einzelne Stages

---

---

## 🧠 LEARNINGS-SYSTEM: ANALYSE & NUTZUNG

### Übersicht

Das System verwendet ein **3-stufiges Learnings-System**:

1. **ANALYSE:** Virale Clips werden analysiert → Patterns extrahiert
2. **MERGE:** Patterns werden in Master Learnings zusammengeführt
3. **NUTZUNG:** Master Learnings werden in AI-Prompts injiziert

---

### 1. ANALYSE: Wie werden Learnings analysiert?

#### Datei: `analyze_and_learn_v2.py`

**Zweck:** Analysiert virale Clips und extrahiert Patterns

**Prozess:**

```
TRAINING DATA (972 Clips)
    ↓
SELECTION STRATEGY (Smart/Cluster/Outliers)
    ↓ (300 Clips selected)
5-AI ENSEMBLE ANALYSIS
    ↓ (Parallel Analysis)
PATTERN EXTRACTION
    ↓
OUTPUT: learned_patterns_v2.json
```

**Strategien:**

1. **FULL:** Alle 972 Clips ($145, 3h)
2. **CLUSTER:** 300 Representatives (95% Coverage, $45, 1h)
3. **SMART:** 300 Top Clips (Best 30%, $45, 1h)
4. **QUICK:** 100 Outliers (Top 10%, $15, 20min)

**Analyse-Methoden:**

**A) Relative Performance Calculation:**
```python
def _calculate_relative_performance(self):
    # Gruppiert Clips nach Account
    # Berechnet Median Views pro Account
    # Relative Performance = Views / Median
    # Outlier = Relative Performance >= 2.0x
```

**B) Composite Score:**
```python
def _calculate_composite_scores(self):
    # Feature Score (0-100):
    #   - Hook Information Gap: 20 points
    #   - Hook Has Question: 15 points
    #   - Pattern Interrupts: 2 points each
    #   - Hook Completeness: 30 points
    #   - Hook Word Count < 15: 10 points
    
    # Performance Score (0-100):
    #   - Watch Time %: 50 points
    #   - Completion Rate: 30 points
    #   - Engagement Rate: 20 points
    
    # Combined Score = (Feature * 0.4) + (Performance * 0.6)
```

**C) 5-AI Ensemble Analysis:**

Für jeden Clip:
```python
prompt = f"""
Analyze this viral clip:

CONTENT: "{clip['content']}"
PERFORMANCE: {views} views, {watch_time}% watch time
OUTPERFORMANCE: {relative_perf}x average

EXTRACT:
1. Hook Type & Formula
2. Structure Pattern
3. Emotional Triggers
4. Pattern Interrupts
5. What makes it viral?
"""
```

5 AIs analysieren parallel → Konsens wird gebildet

**Output-Struktur:**
```json
{
  "metadata": {
    "clips_analyzed": 175,
    "analysis_date": "2024-12-20"
  },
  "hook_mastery": {
    "winning_hook_types": [
      {
        "type": "Paradox Statement",
        "success_rate": 73,
        "template": "Wir machen X falsch",
        "examples": ["Arbeite niemals für Geld"]
      }
    ],
    "power_words": ["niemals", "verheerendste", "geheim"],
    "hook_formulas": ["Contrarian + Universal Pain"]
  },
  "structure_mastery": {
    "winning_structures": [
      {
        "pattern": "Paradox-Explanation-Metaphor",
        "success_rate": 88,
        "duration_range": [45, 65]
      }
    ]
  },
  "executive_summary": {
    "key_insight_1": "Paradox statements haben 73% Success Rate",
    "key_insight_2": "Hook in ersten 3s ist kritisch",
    "key_insight_3": "Pattern interrupts alle 5-7s erhöhen Retention"
  }
}
```

---

### 2. MERGE: Wie werden Learnings zusammengeführt?

#### Datei: `master_learnings_v2.py`

**Zweck:** Zentralisiert ALLE Learnings in einer Datei

**Prozess:**

```
SOURCE 1: deep_learned_patterns.json (Weight: 1.0)
SOURCE 2: learned_patterns_v2.json (Weight: 0.8)
SOURCE 3: Manual Insights (Weight: 1.0)
    ↓
MERGE WITH WEIGHTING
    ↓
DEDUPLICATE & CLEAN
    ↓
OUTPUT: MASTER_LEARNINGS.json
```

**Merge-Logik:**

```python
def _merge_source_into_master(master, source, weight):
    # KEY INSIGHTS
    # Fügt neue Insights hinzu (dedupliziert)
    
    # HOOK MASTERY
    # Merged winning_hook_types (dedupliziert)
    # Merged hook_formulas (dedupliziert)
    # Merged power_words (dedupliziert)
    
    # STRUCTURE MASTERY
    # Merged winning_structures
    # Merged pattern_interrupt_techniques
    
    # EMOTIONAL MASTERY
    # Merged best_emotions
    # Merged trigger_phrases
    
    # CONTENT RULES
    # Merged do_this / never_do lists
```

**Deduplication:**
- Entfernt Duplikate
- Behält höchste Gewichtung
- Validiert Format

**Output-Struktur:**
```json
{
  "metadata": {
    "version": "2.0",
    "last_updated": "2024-12-20",
    "sources": [
      {
        "file": "deep_learned_patterns.json",
        "weight": 1.0,
        "clips_analyzed": 175
      }
    ],
    "total_clips_analyzed": 175
  },
  "algorithm_understanding": {
    "core_principle": "Watchtime maximieren",
    "metrics_priority": ["Watch Time", "Completion Rate"],
    "hook_critical": "Hook (0-3s): KRITISCH!"
  },
  "hook_mastery": {
    "winning_hook_types": [...],
    "power_words": [...],
    "hook_formulas": [...]
  },
  "structure_mastery": {
    "optimal_structure": "Hook → Loop → Content → Payoff",
    "pattern_interrupts": "Alle 5-7 Sekunden"
  }
}
```

---

### 3. NUTZUNG: Wie werden Learnings verwendet?

#### Funktion: `get_learnings_for_prompt()`

**Zweck:** Formatiert Learnings für AI-Prompt-Injection

**Prozess:**

```python
def get_learnings_for_prompt():
    # Lädt MASTER_LEARNINGS.json
    # Formatiert für Prompt:
    
    prompt = """
# 🧠 GELERNTE VIRAL PATTERNS (aus 175 analysierten Clips)

## KEY INSIGHTS:
• Paradox statements haben 73% Success Rate
• Hook in ersten 3s ist kritisch
• Pattern interrupts alle 5-7s erhöhen Retention

## WINNING HOOKS:
• Paradox Statement: "Wir machen X falsch" (73% success)
• Authority Curiosity: "Nur [Zielgruppe] wissen..." (67% success)
• Bold Claim: "Der verheerendste Satz..." (61% success)

## HOOK FORMELN:
• Contrarian + Universal Pain
• Question + Information Gap
• Authority + Proof

## STRUKTUR:
• Hook → Loop öffnen → Content mit Pattern Interrupts → Payoff
• Pattern interrupts alle 5-7 Sekunden
• Jede Sekunde muss Grund liefern weiterzuschauen

## DO THIS:
✅ Hook in ersten 3 Sekunden
✅ Pattern interrupts alle 5-7s
✅ Information Gap öffnen und schließen

## NEVER DO:
❌ Hook nach 3 Sekunden
❌ Keine Pattern Interrupts
❌ Offene Loops ohne Payoff
"""
    
    return prompt
```

**Verwendung in Pipeline:**

```python
# In create_clips_v4_integrated.py

from master_learnings_v2 import get_learnings_for_prompt

# In jedem AI-Prompt:
learnings_context = get_learnings_for_prompt()

prompt = f"""
{learnings_context}

YOUR TASK: [specific task]
"""
```

---

### 4. EINFLUSS: Welchen Einfluss haben Learnings?

#### Stage 0: Coarse Viral Scan

**Einfluss:**
- Prinzipien aus Learnings werden verwendet
- Pattern-Types werden erkannt
- Pre-Scoring basiert auf bekannten Patterns

**Beispiel:**
```python
# Learnings sagen: "Paradox Statement = 73% Success"
# AI erkennt Paradox Statement → Höheres Pre-Score
```

#### Stage 1: Batch Refinement

**Einfluss:**
- Optimal Duration Ranges aus Learnings
- Structure Requirements aus Learnings
- Completeness-Kriterien aus Learnings

**Beispiel:**
```python
# Learnings sagen: "Parable Pattern = 50-70s optimal"
# AI findet Parable → Ziel: 50-70s Duration
```

#### Stage 2.5: Learning-Based Cuts

**Einfluss:**
- **DIREKT:** Verwendet Learnings für Duration-Targets
- Pattern-spezifische Optimal-Ranges
- Hook-Timing aus Learnings (0-3s)

**Code:**
```python
PROVEN_LEARNINGS = {
    'optimal_duration': {
        'story': (45, 65),      # Aus Learnings
        'insight': (20, 40),     # Aus Learnings
        'rant': (30, 50),        # Aus Learnings
        'parable': (50, 70)      # Aus Learnings
    },
    'hook_rules': {
        'max_setup': 3.0,        # Aus Learnings
        'proven_hooks': [...]     # Aus Learnings
    }
}
```

#### Stage 2.6: Cross-Moment Hook Extraction

**Einfluss:**
- Power Words Liste aus Learnings
- Winning Hook Types aus Learnings
- Hook Strength Scoring basiert auf Learnings

**Beispiel:**
```python
# Learnings sagen: "Arbeite niemals für Geld" = 95 Strength
# System findet diesen Hook → Pre-pendet zu passendem Moment
```

#### Godmode Evaluation

**Einfluss:**
- Scoring-Weights aus Learnings
- Pattern-Erkennung basiert auf Learnings
- Success-Rates beeinflussen Scoring

**Beispiel:**
```python
# Learnings sagen: "Paradox Statement Pattern = 88% Success"
# Moment verwendet dieses Pattern → Bonus-Punkte im Scoring
```

---

### 5. ANALYSE-CODE LOGIK (Detailliert)

#### A) Clip Selection Logic

**Smart Selection:**
```python
def select_clips_smart(self, n=300):
    # 1. Sortiert alle Clips nach Composite Score
    ranked = sorted(clips, key=lambda x: x['composite_score'], reverse=True)
    
    # 2. Nimmt Top N
    selected = ranked[:n]
    
    # Composite Score = (Feature * 0.4) + (Performance * 0.6)
    # Feature Score basiert auf:
    #   - Hook Information Gap (20 pts)
    #   - Hook Has Question (15 pts)
    #   - Pattern Interrupts (2 pts each)
    #   - Hook Completeness (30 pts)
    #   - Hook Word Count < 15 (10 pts)
    
    return selected
```

**Cluster Selection:**
```python
def select_clips_cluster(self, n_clusters=300):
    # 1. Generiert Embeddings für alle Clips
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(contents)
    
    # 2. K-Means Clustering
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(embeddings)
    
    # 3. Best Per Cluster
    for cluster_id in range(n_clusters):
        cluster_clips = [c for c, l in zip(clips, labels) if l == cluster_id]
        best = max(cluster_clips, key=lambda x: x['views'])
        representatives.append(best)
    
    return representatives
```

#### B) Pattern Extraction Logic

**5-AI Ensemble Analysis:**
```python
async def analyze_clip_batch(self, clips):
    # Für jeden Clip:
    prompt = build_analysis_prompt(clip)
    
    # 5 AIs analysieren parallel
    results = await asyncio.gather(
        ai1.analyze(prompt),
        ai2.analyze(prompt),
        ai3.analyze(prompt),
        ai4.analyze(prompt),
        ai5.analyze(prompt)
    )
    
    # Konsens bilden
    consensus = self.consensus.build_consensus(results)
    
    # Patterns extrahieren
    patterns = extract_patterns(consensus)
    
    return patterns
```

**Pattern Extraction:**
```python
def extract_patterns(consensus):
    patterns = {
        'hook_type': detect_hook_type(consensus),
        'hook_formula': extract_hook_formula(consensus),
        'structure': detect_structure(consensus),
        'pattern_interrupts': find_interrupts(consensus),
        'emotional_triggers': find_emotions(consensus),
        'success_factors': identify_success_factors(consensus)
    }
    
    return patterns
```

#### C) Merge Logic

**Weighted Merge:**
```python
def _merge_source_into_master(master, source, weight):
    # Hook Types
    for hook in source['hook_mastery']['winning_hook_types']:
        if hook not in master['hook_mastery']['winning_hook_types']:
            master['hook_mastery']['winning_hook_types'].append(hook)
            # Weight wird in Metadata gespeichert
    
    # Power Words
    for word in source['hook_mastery']['power_words']:
        if word not in master['hook_mastery']['power_words']:
            master['hook_mastery']['power_words'].append(word)
    
    # Structures
    for structure in source['structure_mastery']['winning_structures']:
        # Merged mit Success Rate Vergleich
        existing = find_similar_structure(master, structure)
        if existing:
            # Behält höhere Success Rate
            if structure['success_rate'] > existing['success_rate']:
                update_structure(existing, structure)
        else:
            master['structure_mastery']['winning_structures'].append(structure)
```

**Deduplication:**
```python
def _deduplicate_and_clean(master):
    # Entfernt Duplikate
    master['hook_mastery']['winning_hook_types'] = deduplicate_list(
        master['hook_mastery']['winning_hook_types']
    )
    
    # Validiert Format
    validate_structure(master)
    
    # Sortiert nach Success Rate
    master['structure_mastery']['winning_structures'].sort(
        key=lambda x: x.get('success_rate', 0),
        reverse=True
    )
    
    return master
```

#### D) Prompt Formatting Logic

**Formatting:**
```python
def get_learnings_for_prompt():
    master = load_master_learnings()
    
    # Formatiert für Prompt
    prompt = f"""
# 🧠 GELERNTE VIRAL PATTERNS (aus {clips_analyzed} analysierten Clips)

## KEY INSIGHTS:
{format_insights(master['key_insights'])}

## WINNING HOOKS:
{format_hooks(master['hook_mastery']['winning_hook_types'][:5])}

## HOOK FORMELN:
{format_formulas(master['hook_mastery']['hook_formulas'][:5])}

## STRUKTUR:
{format_structure(master['structure_mastery'])}

## DO THIS:
{format_do_this(master['content_rules']['do_this'][:7])}

## NEVER DO:
{format_never_do(master['content_rules']['never_do'][:7])}
"""
    
    return prompt
```

---

### 6. LEARNINGS-DATENFLUSS

```
VIRAL CLIPS (972 Clips)
    ↓
analyze_and_learn_v2.py
    ↓ (Selection Strategy)
300 SELECTED CLIPS
    ↓ (5-AI Ensemble Analysis)
learned_patterns_v2.json
    ↓
master_learnings_v2.py
    ↓ (Merge + Deduplicate)
MASTER_LEARNINGS.json
    ↓
get_learnings_for_prompt()
    ↓ (Format for Prompt)
PROMPT CONTEXT
    ↓
create_clips_v4_integrated.py
    ↓ (Injected in AI Prompts)
AI DECISIONS (Pattern-Aware)
```

---

### 7. BEISPIEL: Vollständiger Learnings-Zyklus

**Schritt 1: Analyse**
```bash
python analyze_and_learn_v2.py --strategy smart --n 300
```
- Analysiert 300 Top-Clips
- Extrahiert Patterns
- Output: `learned_patterns_v2.json`

**Schritt 2: Merge**
```bash
python master_learnings_v2.py
# Option 2: Update from deep analysis
```
- Merged alle Sources
- Dedupliziert
- Output: `MASTER_LEARNINGS.json`

**Schritt 3: Nutzung**
```python
# In Pipeline automatisch:
from master_learnings_v2 import get_learnings_for_prompt

learnings = get_learnings_for_prompt()
# Wird in jedem AI-Prompt injiziert
```

**Schritt 4: Einfluss**
- Stage 2.5 verwendet Learnings für Duration-Targets
- Stage 2.6 verwendet Learnings für Hook-Extraction
- Godmode verwendet Learnings für Scoring

---

**Letzte Aktualisierung:** 2024-12-25
**Version:** V4 Integrated
**Status:** Production-Ready ✅

