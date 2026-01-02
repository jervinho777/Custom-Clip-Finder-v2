# Custom Clip Finder - Projekt Context

## Was es tut
Extrahiert virale Momente aus langen Videos mittels optimierter V4 Pipeline mit 9 Stages + Godmode Evaluation. Verwendet Multi-AI Ensemble (GPT, Claude, Gemini, DeepSeek, Grok) für Pattern-Erkennung und Multi-Level-Optimierung.

## Aktuelle Architektur (V4 Pipeline)

### Pipeline-Stages:
1. **Stage 0: Coarse Viral Scan** - Schnelle, breite Suche nach viralen Potenzialen (20-30 Seeds, pre-scored)
2. **Stage 1: Batch Refinement** - Optimale Grenzen finden (20-30 refined moments, batched)
3. **Stage 1.75: Open Loop Bridging** - Brückt kleine Lücken bei offenen Loops (<5s, rule-based)
4. **Stage 2: Conditional Restructure** - Restrukturiert nur Momente die es brauchen (~60%, conditional)
5. **Stage 2.5: Learning-Based Cuts** - Optimiert Duration basierend auf 175 analysierten Clips
6. **Stage 2.6: Cross-Moment Hook Extraction** - Findet stärkste Hooks im gesamten Video
7. **Stage 2.7: Micro-Level Text Optimization** - Wort-Level Präzision (5-10% Reduktion)
8. **Stage 2.8: Dramatic Structure & Timing** - Strategische Pausen für Drama
9. **Stage 2.9: Payoff Isolation** - Finale Polierung, isoliert Money Shot (⏳ noch nicht implementiert)
10. **Godmode: Batched Premium Evaluation** - Finale Opus 4 Evaluation (40+ Score)

### Prinzipien-basiert (nicht rigid):
- COMPLETENESS for what it IS
- NATURAL BOUNDARIES
- EMOTIONAL INTENSITY
- PATTERN INTERRUPTS
- FORMAT FLEXIBILITY
- CONTEXT AWARENESS

## Haupt-Entry-Points
- `create_clips_v4_integrated.py` - Main V4 Pipeline (9 Stages + Godmode)
- `test_2stage_cached.py` - Cached Pipeline Test
- `test_stage_2_5.py` - Isolierter Test für Learning-Based Cuts
- `test_stage_1_75.py` - Isolierter Test für Open Loop Bridging

## Learnings-System
- **Analyse:** `analyze_and_learn_v2.py` - Analysiert virale Clips (175+ analysiert)
- **Merge:** `master_learnings_v2.py` - Zentralisiert alle Learnings
- **Nutzung:** `get_learnings_for_prompt()` - Injiziert Learnings in AI-Prompts
- **Datenbank:** `data/MASTER_LEARNINGS.json` - Zentrale Learnings-Datenbank

## Self-Learning System (NEU! 🧠)
- **Pattern Analyzer:** `viral_pattern_analyzer.py` - Analysiert isolierte Clips + Transformation Pairs
- **Principle Synthesizer:** `synthesize_principles.py` - Synthetisiert Master Principles (VIRAL_PRINCIPLES.json)
- **Auto-Update:** `update_brain.py` / `auto_update_brain.sh` - Kontinuierliche Verbesserung
- **Composer Integration:** `create_clips_v4_integrated.py` lädt automatisch VIRAL_PRINCIPLES.json
- **Master Brain:** `data/learnings/VIRAL_PRINCIPLES.json` - Zentrale Prinzipien-Datenbank (self-learning!)

## Was funktioniert ✅
- ✅ V4 Pipeline mit 9 Stages (8 implementiert, 1 pending)
- ✅ Caching System (Transcripts + Pipeline-Outputs, 85% Effizienz)
- ✅ Multi-AI Ensemble (Consensus Engine)
- ✅ Open Loop Bridging (Stage 1.75) - Rule-based, $0 Cost
- ✅ Stage 2.5: Viral Composition - Holistic Multi-AI Optimization (ersetzt 5 separate stages)
- ✅ Cross-Moment Hook Extraction (Stage 2.6) - Findet Hooks aus anderen Momenten
- ✅ Micro-Level Text Optimization (Stage 2.7) - Wort-Level Präzision
- ✅ Dramatic Timing (Stage 2.8) - Strategische Pausen
- ✅ Batched Godmode Evaluation (Opus 4)
- ✅ Principle-based Approach (nicht rigid)
- ✅ Batch-Verarbeitung (kosteneffizient, 80% Savings)
- ✅ Conditional Processing (nur verarbeiten was nötig ist)
- ✅ Premiere XML Export
- ✅ Comprehensive Documentation (`SYSTEM_OVERVIEW.md`, `PROJECT_HISTORY.md`)
- ✅ **Self-Learning System** - Viral Pattern Analyzer + Principle Synthesizer (NEU!)
- ✅ **Auto-Update Workflow** - Kontinuierliche Verbesserung durch neue Daten (NEU!)
- ✅ **Principle-based Analysis** - `analyze_restructures_v1.py` gibt Prinzipien statt rigider Regeln aus (NEU!)

## Was NICHT funktioniert / Probleme ⚠️
- ⚠️ **Kosten:** ~$9.20 pro Video (Stage 2.5 konsolidiert, aber noch nicht getestet)
- ⚠️ **Qualität:** Godmode Scores noch nicht vollständig getestet (Ziel: 46-50/50)
- ⚠️ **Stage 2.9:** Payoff Isolation noch nicht implementiert (⏳ pending)
- ⚠️ **Redundanz:** Viele alte Versionen (v1, v2, v3) noch vorhanden
- ⚠️ **Test-Coverage:** Pipeline nur auf Dieter Lange getestet, nicht auf diverse Content-Typen
- ⚠️ **Export:** Export-Funktion wurde angepasst, aber noch nicht mit vollständiger Pipeline getestet
- ⚠️ **Self-Learning System:** VIRAL_PRINCIPLES.json noch nicht initial trainiert (muss `viral_pattern_analyzer.py` ausführen)
- ⚠️ **API Refusals:** Initiale Prompt-Versionen in `synthesize_principles.py` führten zu Refusals (gelöst durch Vereinfachung)

## Nächste Schritte (Priorität)
1. [ ] **Self-Learning System initialisieren** - `python viral_pattern_analyzer.py` ausführen (erstellt VIRAL_PRINCIPLES.json)
2. [ ] **Principle Synthesizer testen** - `python synthesize_principles.py` validieren (sollte ohne Refusals laufen)
3. [ ] **Vollständiger Pipeline-Test** - Dieter Lange end-to-end mit neuen Principles ($9.20, validiere Scores)
4. [ ] **Stage 2.9 implementieren** - Payoff Isolation (30-45 min, +$0.50/video)
5. [ ] **Diverse Content-Tests** - Podcast, Educational, Stage Talk, Interview (5 Videos, $46.00)
6. [ ] **Auto-Update Workflow testen** - Neue Clips hinzufügen → `./auto_update_brain.sh` → Brain verbessert sich
7. [ ] **Projekt aufräumen** - Alte Versionen archivieren/löschen
8. [ ] **Comprehensive Logging** - Stage-Level Visibility für Debugging

## Entscheidungen (Aktuell)
| Datum | Entscheidung | Warum |
|-------|--------------|-------|
| 2024-12-25 | V4 Pipeline mit 9 Stages implementiert | Multi-Level-Optimierung für viral-ready Clips |
| 2024-12-25 | Principle-based statt rigid rules | Bessere Anpassungsfähigkeit an verschiedene Formate |
| 2024-12-25 | Batch-Verarbeitung überall | Kostenreduktion (80% Savings) |
| 2024-12-25 | Single-Gate Godmode (nicht Two-Gate) | Niedrigere False-Negative-Rate (10% vs 19%) |
| 2024-12-25 | Multi-Level-Optimization (Stages 2.5-2.9) | Viral Clips werden komponiert, nicht nur gefunden |
| 2024-12-25 | Comprehensive Documentation erstellt | Vollständiges System-Verständnis |
| 2025-01-02 | **Self-Learning System implementiert** | Kontinuierliche Verbesserung durch neue Daten, kein statisches System |
| 2025-01-02 | **Stage 2.5 zu "Viral Composition" konsolidiert** | 5 separate stages → 1 holistic stage (52% Kostenersparnis, intelligentere Optimierung) |
| 2025-01-02 | **Principle-based Analysis Output** | `analyze_restructures_v1.py` gibt Prinzipien statt rigider Regeln aus |
| 2025-01-02 | **Direct Anthropic API in Synthesizer** | Keine komplexen Dependencies, einfachere Fehlerbehandlung |
| 2025-01-02 | **Simplified Prompts (nur Stats)** | Vermeidet API Refusals, kürzere Prompts, effizienter |

## Was ich behalten will
- ✅ 5-AI Ensemble Logik (Consensus Engine)
- ✅ Caching System (Transcripts + Pipeline)
- ✅ Premiere XML Export
- ✅ Learnings-System (Analyse → Merge → Nutzung)
- ✅ Principle-based Approach
- ✅ Batch-Verarbeitung
- ✅ Conditional Processing
- ✅ Multi-Level-Optimization (Stages 2.5-2.9)

## Was weg kann
- ❌ Alte Versionen (v1, v2 wo v4 existiert)
- ❌ Test/Debug Scripts die nicht mehr gebraucht werden
- ❌ Fix-Scripts die bereits angewendet wurden
- ❌ Backup-Dateien (außer wichtige)

## Wichtige Dateien
- `create_clips_v4_integrated.py` - Haupt-Pipeline (5500+ Zeilen)
- `SYSTEM_OVERVIEW.md` - Vollständige System-Dokumentation
- `PROJECT_HISTORY.md` - Vollständige Entwicklungs-History, alle Entscheidungen, Learnings
- `master_learnings_v2.py` - Learnings-Management
- `create_clips_v3_ensemble.py` - Consensus Engine
- `data/MASTER_LEARNINGS.json` - Zentrale Learnings-Datenbank

## Kosten-Übersicht (pro 30-Minuten Video)
- **Stage 0:** $1.50 (Coarse Scan, pre-scored)
- **Stage 1:** $0.60 (Batch Refinement, 4 batches)
- **Stage 1.75:** $0.00 (Rule-based, keine AI)
- **Stage 2:** $0.30 (Conditional Restructure, nur ~60%)
- **Stage 2.5:** $6.00 (Viral Composition - Holistic Multi-AI, ersetzt Stages 2.5-2.9)
- **Godmode:** $0.80 (Batched Evaluation, 4 batches)
- **TOTAL:** ~$9.20 pro Video (vs. $12.65 vorher, 27% Reduktion durch Konsolidierung)

**Kosten pro viralem Clip:**
- Alt: $6.25-12.50 pro viral clip (10% Pass-Rate)
- Neu: $1.58-2.11 pro viral clip (40% Pass-Rate geschätzt)
- **75% Verbesserung pro viralem Clip!**

## Dokumentation
- `SYSTEM_OVERVIEW.md` - Vollständige System-Übersicht, alle Stages, Datenfluss
- `PROJECT_HISTORY.md` - Vollständige Entwicklungs-History, alle Entscheidungen, Fehlschläge, Learnings
- `FUNCTION_SIGNATURES.md` - Alle Methoden-Signaturen
- `LEARN_FROM_VIRAL_EXAMPLE_OUTLINE.md` - Learnings-Prozess

## Key Insights
1. **Viral Clips werden komponiert, nicht nur gefunden** - Multi-Level-Optimization erforderlich
2. **Principle-based > Rigid Rules** - Anpassungsfähigkeit ist kritisch
3. **Batch Processing = 80% Kostenersparnis** - Und bessere Qualität!
4. **Multiple Gates erhöhen False Negatives** - Single Gate besser
5. **Kosten pro viral Clip > Kosten pro Video** - Wichtigerer Metric

## Aktuelle Herausforderungen
1. **Cost Creep:** $12.65 nahe am ursprünglichen $12.50, aber bessere Qualität
2. **Komplexität:** 9 Stages = mehr Failure Points, schwerer zu debuggen
3. **Nicht production-getestet:** Nur Dieter Lange getestet, Generalisierung unklar
4. **Stage 2.9 fehlt:** Payoff Isolation noch nicht implementiert

## Nächste kritische Schritte
1. **Stage 2.9 implementieren** (30-45 min)
2. **Full Pipeline Test** auf Dieter Lange ($12.65, validiere Scores)
3. **Diverse Content Tests** (5 Videos, $63.25)
4. **Hook Matching optimieren** (Batch statt Individual, $2.40 Savings)

---

**Für vollständige History, alle Entscheidungen und Learnings → siehe `PROJECT_HISTORY.md`**

