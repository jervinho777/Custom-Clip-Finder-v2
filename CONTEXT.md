# Custom Clip Finder v2 - Projekt Context

## Was es tut
AI-powered viral clip extraction system mit 4-Stage Pipeline (DISCOVER → COMPOSE → VALIDATE → EXPORT) + optional GODMODE Evaluation. Verwendet Multi-AI Ensemble (5 AIs parallel) und prinzipienbasiertes BRAIN System für kontinuierliche Verbesserung.

## Aktuelle Architektur (V2 Pipeline)

### Pipeline-Stages:
1. **DISCOVER** - Multi-AI Ensemble (5 AIs parallel) findet alle viral-fähigen Momente
2. **COMPOSE** - Strukturiert Momente zu fertigen Clips (Hook Extraction, Cross-Moment Composition)
3. **VALIDATE** - Bewertet Clips auf Viral-Potential
4. **EXPORT** - Generiert Premiere Pro XML, MP4, JSON
5. **GODMODE** (Optional) - Premium Opus Evaluation für finale Qualitätskontrolle

### BRAIN System (Lernphase):
- **Code 1:** Analysiert isolierte virale Clips → `isolated_patterns.json`
- **Code 2:** Analysiert Longform→Clip Paare → `composition_patterns.json`
- **Code 3:** Synthetisiert zu Master Principles → `PRINCIPLES.json`

### Prinzipien-basiert (nicht rigid):
- **Prinzipien statt Regeln:** System extrahiert WARUM etwas funktioniert, nicht WAS es ist
- **Flexibel und kontextabhängig:** Keine starren Templates oder feste Sekunden
- **Master Principle:** "Make a video so good that people cannot physically scroll past"

## Haupt-Entry-Points
- `main.py` - CLI Interface mit Commands:
  - `python main.py process <video>` - Vollständige Pipeline
  - `python main.py init-brain` - Vector Store initialisieren
  - `python main.py analyze-brain` - BRAIN Analyse ausführen
  - `python main.py test-apis` - API-Verbindungen testen

## Tech Stack
- **Package Manager:** `uv` (statt pip)
- **AI Models:** Dynamische Erkennung (immer neueste Models)
- **Vector Store:** ChromaDB (972 Clips)
- **Transcription:** AssemblyAI (word-level timestamps)
- **Video Processing:** FFmpeg
- **URL Download:** yt-dlp (YouTube, Instagram, TikTok, etc.)

## Performance Optimierungen
- **Prompt Caching (Anthropic):** 90% Kostenersparnis auf wiederholte Calls
- **Asyncio Parallel Processing:** 3-5x Geschwindigkeitsverbesserung
- **Structured Outputs (Pydantic):** Garantiertes Schema, keine Parsing-Fehler
- **Batch API (Optional):** 50% Ersparnis für Bulk-Processing

## Was funktioniert ✅
- ✅ **4-Stage Pipeline** vollständig implementiert
- ✅ **Multi-AI Ensemble** mit 5 AIs parallel (DISCOVER & COMPOSE)
- ✅ **BRAIN System** mit Vector Store (972 Clips initialisiert)
- ✅ **Prinzipienbasiertes Learning** - Extrahiert Prinzipien, nicht Regeln
- ✅ **Dynamische Model-Erkennung** - Immer neueste AI Models
- ✅ **Performance Optimierungen** - Prompt Caching, Parallel Processing, Structured Outputs
- ✅ **URL Support** - Videos von YouTube, Instagram, TikTok downloaden
- ✅ **AssemblyAI Integration** - Word-level timestamps für präzise Cuts
- ✅ **Premiere Pro XML Export** - Fertige Sequenz mit neuer Reihenfolge
- ✅ **Godmode Evaluation** - Optional Premium Opus Review
- ✅ **Training Data Pairs** - 9 verifizierte Longform→Clip Paare dokumentiert
- ✅ **Ground Truth Test** - Test-Script für bekannte virale Momente

## Was NICHT funktioniert / Probleme ⚠️
- ⚠️ **BRAIN Analyse:** Bereit für vollständige Analyse aller 972 Clips (muss noch ausgeführt werden)
- ⚠️ **Testing:** Noch kein vollständiger End-to-End Test mit echtem Video
- ⚠️ **Dependencies:** `instructor` und `aiohttp` müssen noch installiert werden
- ⚠️ **Vector Store:** Initialisiert, aber noch nicht in Production verwendet
- ⚠️ **Cost Tracking:** Cache-Statistiken werden getrackt, aber noch nicht in Reports integriert

## Nächste Schritte (Priorität)
1. [ ] **Vollständige BRAIN Analyse** - `./run_full_brain.sh` (alle 972 Clips, ~$5-10, 30-60 min)
2. [ ] **Dependencies installieren** - `uv sync` (instructor, aiohttp)
3. [ ] **Vollständiger Production-Test** - Dieter Lange.mp4 durch komplette Pipeline
4. [ ] **Ground Truth Validation** - Prüfen ob "Arbeite niemals für Geld" gefunden wird
5. [ ] **Performance Monitoring** - Cache-Statistiken in Reports integrieren
6. [ ] **Diverse Content-Tests** - Verschiedene Video-Typen testen
7. [ ] **Documentation** - API-Dokumentation für alle Stages

## BRAIN Analyse über Nacht ausführen
```bash
cd "/Users/jervinquisada/custom-clip-finder v2"
./run_full_brain.sh           # Foreground
# ODER
nohup ./run_full_brain.sh &   # Background (über Nacht)
```

Analysiert alle 972 Clips in 49 Batches mit **OPUS 4.5** (beste Qualität):
- **Dauer:** 45-90 Minuten
- **Kosten:** ~$25-40 (Opus 4.5 💎 - lohnt sich, BRAIN wird einmal erstellt!)
- **Output:** `isolated_patterns.json`, `composition_patterns.json`, `PRINCIPLES.json`

## Entscheidungen (Aktuell)
| Datum | Entscheidung | Warum |
|-------|--------------|-------|
| 2026-01-02 | **V2 Neustart** - Komplett neues Projekt basierend auf PRD | V1 hatte zu viele Legacy-Probleme, sauberer Neustart |
| 2026-01-02 | **4-Stage Pipeline** statt 9 Stages | Vereinfachung, klarere Struktur, PRD-konform |
| 2026-01-02 | **Prinzipienbasiert statt regelbasiert** | Flexibilität, bessere Anpassungsfähigkeit |
| 2026-01-02 | **Dynamische Model-Erkennung** | Immer neueste Models, keine veralteten Strings |
| 2026-01-02 | **uv statt pip** | Moderner Package Manager, schnellere Installs |
| 2026-01-02 | **Prompt Caching implementiert** | 90% Kostenersparnis auf Anthropic Calls |
| 2026-01-02 | **Asyncio Parallel Processing** | 3-5x Geschwindigkeitsverbesserung |
| 2026-01-02 | **Structured Outputs mit Pydantic** | Garantiertes Schema, keine Parsing-Fehler |
| 2026-01-02 | **BRAIN System mit Vector Store** | Kontinuierliches Learning aus neuen Daten |
| 2026-01-02 | **Prinzipienbasiertes Learning** | Extrahiert WARUM, nicht WAS |
| 2026-01-02 | **URL Download Support** | Videos von öffentlichen Links verarbeiten |
| 2026-01-02 | **Training Data Pairs dokumentiert** | 9 verifizierte Paare für System-Validierung |

## Wichtige Dateien
- `main.py` - CLI Entry Point
- `brain/analyze.py` - BRAIN Analyse-Phase
- `brain/vector_store.py` - ChromaDB Vector Store
- `brain/PRINCIPLES.json` - Master Principles (prinzipienbasiert)
- `pipeline/discover.py` - DISCOVER Stage
- `pipeline/compose.py` - COMPOSE Stage
- `pipeline/validate.py` - VALIDATE Stage
- `pipeline/godmode.py` - GODMODE Evaluation
- `pipeline/optimized.py` - Performance-optimierte AI Calls
- `models/auto_detect.py` - Dynamische Model-Erkennung
- `models/schemas.py` - Pydantic Response Schemas
- `prompts/identities.py` - Supreme Identity Prompts
- `data/training/pairs_config.json` - Longform→Clip Paare Konfiguration

## Dokumentation
- `docs/SYSTEM_ARCHITECTURE_FINAL.md` - Vollständige Pipeline-Architektur
- `docs/PERFORMANCE_OPTIMIZATIONS.md` - Performance-Optimierungen Guide
- `docs/DYNAMIC_MODEL_DETECTION.md` - Dynamische Model-Erkennung
- `docs/TRAINING_DATA_PAIRS.md` - Verifizierte Training Data Paare
- `tests/test_dieter_lange.py` - Ground Truth Test

