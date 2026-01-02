# 📋 FUNCTION SIGNATURES - Next 5 Functions

## 1. analyze_restructuring()

```python
def analyze_restructuring(
    self,
    comparison_result: Dict,
    clip_segments: List[Dict],
    performance: Dict
) -> Dict:
    """
    Analysiert die Restrukturierung im Detail
    
    Erweitert die Vergleichs-Ergebnisse mit detaillierter Analyse:
    - Hook-Strategie (Position, Typ, Warum funktioniert)
    - Struktur-Pattern (A→B→C wurde zu C→A→B)
    - Entfernte Teile (Intro, Filler, Repetition)
    - Kompressions-Strategie
    
    Args:
        comparison_result: Ergebnis von compare_transcripts()
        clip_segments: Clip-Segmente mit Timestamps
        performance: Performance-Daten (Views, Watch Time, etc.)
    
    Returns:
    {
        "hook_strategy": {
            "original_position": 200.0,
            "clip_position": 0.0,
            "moved_to_front": True,
            "hook_text": "Der stärkste Satz...",
            "hook_type": "controversy/story/question/statement",
            "hook_strength": 9,  # 0-10
            "why_effective": "Öffnet Information Gap..."
        },
        "structure_pattern": {
            "original": "A→B→C→D",
            "clip": "C→A→B",
            "pattern_name": "payoff_first_then_context",
            "pattern_description": "Stärkster Moment zuerst, dann Aufbau",
            "timing": {
                "hook_duration": 3.0,
                "first_loop": 3.0,
                "pattern_interrupts": [10.0, 25.0],
                "total_duration": 45.0
            }
        },
        "removed_parts": {
            "intro": True,
            "filler": True,
            "repetition": True,
            "slow_parts": True,
            "removed_segments_count": 15
        },
        "compression": {
            "ratio": 0.025,
            "strategy": "keep_hook_and_payoff_only",
            "removed_percent": 97.5
        },
        "effectiveness_score": 0.92  # Basierend auf Performance
    }
    """
```

---

## 2. extract_hook_patterns()

```python
def extract_hook_patterns(
    self,
    hook_segment: Dict,
    clip_segments: List[Dict],
    performance: Dict,
    comparison_result: Dict
) -> Dict:
    """
    Extrahiert Hook-Patterns aus erfolgreichem Clip
    
    Analysiert:
    - Hook-Text und Struktur
    - Erste Wörter (Power Words)
    - Emotionaler Trigger
    - Information Gap
    - Timing
    
    Args:
        hook_segment: Das Hook-Segment aus Clip
        clip_segments: Alle Clip-Segmente
        performance: Performance-Daten
        comparison_result: Vergleichs-Ergebnisse
    
    Returns:
    {
        "hook_text": "Warum [kontraintuitives Statement]...",
        "hook_type": "controversy/story/question/statement/teaser",
        "first_words": ["Warum", "Der", "größte"],
        "power_words": ["Warum", "größte", "Fehler"],
        "emotional_trigger": "curiosity/anger/surprise/excitement/fear",
        "information_gap": True,
        "hook_formula": "Warum [kontraintuitives Statement]",
        "timing": {
            "duration": 3.0,
            "words_count": 12,
            "words_per_second": 4.0
        },
        "effectiveness": {
            "score": 0.95,  # Basierend auf Performance
            "watch_time_impact": "high",  # Wie stark beeinflusst es Watch Time
            "hook_strength": 9
        },
        "matched_patterns": [
            "controversy_hook",
            "information_gap_hook"
        ]
    }
    """
```

---

## 3. extract_structure_patterns()

```python
def extract_structure_patterns(
    self,
    clip_segments: List[Dict],
    restructuring: Dict,
    performance: Dict
) -> Dict:
    """
    Extrahiert Struktur-Patterns aus erfolgreichem Clip
    
    Analysiert:
    - Gesamtstruktur (Hook→Context→Content→Payoff)
    - Timing jeder Phase
    - Pattern Interrupts
    - Spannungsbogen
    
    Args:
        clip_segments: Alle Clip-Segmente mit Roles
        restructuring: Ergebnis von analyze_restructuring()
        performance: Performance-Daten
    
    Returns:
    {
        "structure_name": "payoff_first_then_context",
        "structure": {
            "hook": {
                "start": 0.0,
                "end": 3.0,
                "duration": 3.0,
                "role": "hook",
                "purpose": "Stop-Trigger, Information Gap"
            },
            "context": {
                "start": 3.0,
                "end": 15.0,
                "duration": 12.0,
                "role": "context",
                "purpose": "Aufbau, Loop öffnen"
            },
            "content": {
                "start": 15.0,
                "end": 40.0,
                "duration": 25.0,
                "role": "content",
                "purpose": "Hauptinhalt mit Pattern Interrupts"
            },
            "payoff": {
                "start": 40.0,
                "end": 45.0,
                "duration": 5.0,
                "role": "payoff",
                "purpose": "Loop schließen, Satisfying Conclusion"
            }
        },
        "timing": {
            "hook_duration": 3.0,
            "first_loop": 3.0,  # Wann wird erster Loop geöffnet
            "pattern_interrupts": [10.0, 25.0],  # Mini-Payoffs
            "total_duration": 45.0,
            "optimal_length": {
                "min": 30,
                "max": 60,
                "sweet_spot": 45
            }
        },
        "tension_arc": {
            "arc_type": "rising/plateau/falling",
            "tension_points": [
                {"time": 0.0, "level": 9, "reason": "Hook"},
                {"time": 10.0, "level": 7, "reason": "Context"},
                {"time": 25.0, "level": 8, "reason": "Pattern Interrupt"}
            ],
            "average_tension": 7.5,
            "min_tension": 5.0,
            "max_tension": 9.0
        },
        "effectiveness": {
            "score": 0.92,
            "watch_time_impact": "high",
            "completion_rate_impact": "high"
        }
    }
    """
```

---

## 4. ai_analyze_example()

```python
def ai_analyze_example(
    self,
    longform_segments: List[Dict],
    clip_segments: List[Dict],
    comparison_result: Dict,
    restructuring: Dict,
    performance: Dict,
    notes: Optional[str] = None,
    deep_analysis: bool = False
) -> Dict:
    """
    Nutzt AI für tiefere Analyse des Beispiels
    
    Claude analysiert:
    - Warum dieser Clip funktioniert hat
    - Welche Patterns besonders effektiv waren
    - Was kann wiederverwendet werden
    - Erstellt Template-Vorschlag
    
    Args:
        longform_segments: Original Longform-Segmente
        clip_segments: Clip-Segmente
        comparison_result: Vergleichs-Ergebnisse
        restructuring: Restrukturierungs-Analyse
        performance: Performance-Daten
        notes: Optionale Notizen warum es funktioniert hat
        deep_analysis: True für Outliers (1M+ Views)
    
    Returns:
    {
        "analysis": {
            "why_it_worked": [
                "Hook öffnet sofort Information Gap",
                "Payoff zuerst erzeugt sofortige Spannung",
                "Pattern Interrupts halten Spannung hoch"
            ],
            "key_success_factors": [
                "Hook-Stärke: 9/10",
                "Struktur: Optimal für Topic",
                "Timing: Perfekte Pattern Interrupts"
            ],
            "unique_elements": [
                "Verwendung von Kontroverse als Hook",
                "Payoff vor Context platziert"
            ]
        },
        "patterns": {
            "hook_pattern": {...},  # Von extract_hook_patterns()
            "structure_pattern": {...},  # Von extract_structure_patterns()
            "additional_insights": [
                "Funktioniert besonders gut für [Topic]",
                "Erfordert starken Payoff-Moment"
            ]
        },
        "template_suggestion": {
            "name": "Controversy Hook + Payoff First",
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
            }
        },
        "success_rate_prediction": 0.85  # Wie wahrscheinlich ist Erfolg bei ähnlichen Videos
    }
    """
```

---

## 5. create_template()

```python
def create_template(
    self,
    hook_patterns: Dict,
    structure_patterns: Dict,
    restructuring: Dict,
    ai_analysis: Dict,
    performance: Dict
) -> Dict:
    """
    Erstellt wiederverwendbares Template aus allen Patterns
    
    Kombiniert alle extrahierten Patterns zu einem anwendbaren Template.
    Template kann später für ähnliche Videos verwendet werden.
    
    Args:
        hook_patterns: Ergebnis von extract_hook_patterns()
        structure_patterns: Ergebnis von extract_structure_patterns()
        restructuring: Ergebnis von analyze_restructuring()
        ai_analysis: Ergebnis von ai_analyze_example()
        performance: Performance-Daten
    
    Returns:
    {
        "template_id": "template_001",
        "name": "Controversy Hook + Payoff First",
        "description": "Für Videos mit kontroversen Aussagen - Payoff zuerst als Hook",
        "created_from": {
            "example_id": "example_001",
            "performance": {
                "views": 500000,
                "watch_time": 85
            }
        },
        "when_to_use": [
            "Video enthält kontroverse Meinung",
            "Starker Payoff-Moment vorhanden (emotional/intense)",
            "Original-Struktur langsam im Aufbau",
            "Topic eignet sich für Information Gap"
        ],
        "when_not_to_use": [
            "Video hat keinen klaren Payoff-Moment",
            "Topic zu komplex für schnellen Hook",
            "Zielgruppe erwartet langsameren Aufbau"
        ],
        "structure": {
            "step_1": {
                "action": "Finde stärksten Payoff-Moment",
                "criteria": "Emotional, kontrovers, überraschend",
                "duration": "3-5 Sekunden"
            },
            "step_2": {
                "action": "Platziere als Hook (0-3s)",
                "criteria": "Muss sofort Information Gap öffnen",
                "duration": "3 Sekunden"
            },
            "step_3": {
                "action": "Füge Context hinzu (3-15s)",
                "criteria": "Erklärt warum Hook wichtig ist",
                "duration": "12 Sekunden"
            },
            "step_4": {
                "action": "Rest des Contents (15-40s)",
                "criteria": "Mit Pattern Interrupts alle 5-7s",
                "duration": "25 Sekunden"
            },
            "step_5": {
                "action": "Kleiner Payoff am Ende (40-45s)",
                "criteria": "Loop schließen, Satisfying Conclusion",
                "duration": "5 Sekunden"
            }
        },
        "hook_formula": "Warum [kontraintuitives Statement]",
        "hook_examples": [
            "Warum der größte Fehler bei [Topic]...",
            "Warum [Person] falsch liegt..."
        ],
        "optimal_length": {
            "min": 30,
            "max": 60,
            "sweet_spot": 45
        },
        "success_rate": 0.92,  # Basierend auf Performance
        "success_criteria": {
            "min_views": 100000,
            "min_watch_time": 70,
            "min_followers": 1000
        },
        "variations": [
            {
                "name": "Story Hook Variante",
                "hook_formula": "Als ich [dramatisches Event]...",
                "when_to_use": "Wenn Story vorhanden statt Kontroverse"
            }
        ],
        "tags": ["controversy", "payoff_first", "information_gap", "high_tension"]
    }
    """
```

---

## 📊 DATA FLOW

```
compare_transcripts()
    ↓
analyze_restructuring()
    ↓
extract_hook_patterns() ──┐
    ↓                      │
extract_structure_patterns() ──┐
    ↓                          │
ai_analyze_example() ───────────┤
    ↓                           │
create_template() ←─────────────┘
    ↓
update_master_learnings()
```

---

## ✅ READY TO IMPLEMENT

Alle Signaturen sind definiert. Soll ich mit der Implementierung beginnen?

