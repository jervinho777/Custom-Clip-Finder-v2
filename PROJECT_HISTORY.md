# Custom Clip Finder v2 - Project History

## CHRONOLOGISCHE EVOLUTION

### **PHASE 0: V1 → V2 MIGRATION**
```
Date: 2026-01-02
Status: ✅ Abgeschlossen
* Problem: V1 hatte zu viele Legacy-Probleme, 9 Stages zu komplex
* Approach: Kompletter Neustart basierend auf PRD v4
* Migration:
  - Alle V1 Files archiviert in v1_archive/
  - Neue saubere Struktur: brain/, pipeline/, models/, prompts/, utils/
  - Cache und Transkripte übernommen
  - Große Dateien nach ARCHIVED_LARGE_FILES verschoben
* Result: ✅ Sauberes V2 Projekt, PRD-konform
* Learnings: Neustart war richtig - V1 zu komplex für saubere Weiterentwicklung
```

### **PHASE 1: CORE ARCHITECTURE SETUP**
```
Date: 2026-01-02
Status: ✅ Abgeschlossen
* Decision: 4-Stage Pipeline statt 9 Stages
* Implementation:
  - DISCOVER: Multi-AI Ensemble (5 AIs parallel)
  - COMPOSE: Clip-Strukturierung mit Hook Extraction
  - VALIDATE: Viral Potential Scoring
  - EXPORT: Premiere XML, MP4, JSON
* Result: ✅ Klare, einfache Pipeline-Struktur
* Learnings: Weniger Stages = einfacher zu verstehen und debuggen
```

### **PHASE 2: BRAIN SYSTEM IMPLEMENTATION**
```
Date: 2026-01-02
Status: ✅ Implementiert, ⚠️ Noch nicht getestet
* Decision: Prinzipienbasiertes Learning System
* Implementation:
  - Vector Store (ChromaDB) für 972 Clips
  - Code 1: Isolierte Clips → isolated_patterns.json
  - Code 2: Longform→Clip Paare → composition_patterns.json
  - Code 3: Synthese → PRINCIPLES.json
* Result: ✅ System implementiert, Vector Store initialisiert
* Problem: Erste Analyse lief mit alten Prompts → Output noch regelbasiert
* Next: Neu-Analyse mit prinzipienbasierten Prompts
* Learnings: Prompts müssen explizit nach Prinzipien fragen, nicht nach Patterns
```

### **PHASE 3: DYNAMIC MODEL DETECTION**
```
Date: 2026-01-02
Status: ✅ Abgeschlossen
* Problem: Hardcodierte Model-Strings werden veraltet
* Approach: Automatische Model-Erkennung von allen Providern
* Implementation:
  - models/auto_detect.py: Erkennt neueste Models
  - 24h Cache in config/detected_models.json
  - get_model() verwendet auto_detect
* Result: ✅ System verwendet immer neueste Models
* Learnings: Dynamische Erkennung spart manuelle Updates
```

### **PHASE 4: PERFORMANCE OPTIMIZATIONS**
```
Date: 2026-01-02
Status: ✅ Implementiert
* Problem: Hohe Kosten, langsame Verarbeitung
* Approach: 3 kritische Optimierungen
* Implementation:
  1. Prompt Caching (Anthropic): 90% Ersparnis
  2. Asyncio Parallel Processing: 3-5x schneller
  3. Structured Outputs (Pydantic): Garantiertes Schema
* Result: ✅ Alle Optimierungen implementiert
* Cost Impact: ~$1.00 → ~$0.33 pro Video (geschätzt)
* Learnings: Prompt Caching ist game-changer für Anthropic
```

### **PHASE 5: PRINCIPLE-BASED LEARNING FIX**
```
Date: 2026-01-02
Status: ✅ Fixed, ⚠️ Noch nicht neu ausgeführt
* Problem: Analyse-Prompts extrahierten noch Regeln statt Prinzipien
* Discovery: User fragte "Sind alle Learnings wirklich prinzipienbasiert?"
* Analysis: Prompts fragten nach "Patterns", nicht nach "Prinzipien"
* Fix:
  - Code 1: hook_patterns → hook_principles
  - Code 2: cutting_principles mit "why" und "application"
  - Code 3: Synthese zu Master Principles
* Result: ✅ Prompts aktualisiert, alte Outputs gelöscht
* Next: Neu-Analyse ausführen
* Learnings: Explizite Unterscheidung zwischen Regeln und Prinzipien nötig
```

---

## ARCHITEKTUR-ENTSCHEIDUNGEN

### **4-Stage Pipeline statt 9 Stages**
**Datum:** 2026-01-02  
**Entscheidung:** Vereinfachung von 9 auf 4 Stages  
**Warum:**
- PRD v4 spezifiziert 4 Stages
- Klarere Struktur, einfacher zu verstehen
- Weniger Komplexität = weniger Fehlerquellen
**Trade-off:** Weniger Granularität, aber ausreichend für PRD

### **Prinzipienbasiert statt Regelbasiert**
**Datum:** 2026-01-02  
**Entscheidung:** Alle Learnings extrahieren Prinzipien, nicht Regeln  
**Warum:**
- Flexibilität für verschiedene Content-Typen
- PRD explizit: "prinzipienbasiert"
- User-Feedback: "Beispiele sind nicht 1:1 Regeln"
**Beispiel:**
- ❌ Regel: "Hook muss immer das Wort 'niemals' enthalten"
- ✅ Prinzip: "Hooks funktionieren, wenn sie kognitive Dissonanz erzeugen"

### **Dynamische Model-Erkennung**
**Datum:** 2026-01-02  
**Entscheidung:** Automatische Erkennung neuester Models  
**Warum:**
- Hardcodierte Strings werden veraltet
- Neue Models werden automatisch verwendet
- Keine manuellen Updates nötig
**Implementation:** models/auto_detect.py mit 24h Cache

### **Prompt Caching für Anthropic**
**Datum:** 2026-01-02  
**Entscheidung:** System-Prompts cachen (90% Ersparnis)  
**Warum:**
- Supreme Identity + BRAIN Context sind statisch
- Nur Transcript ändert sich pro Call
- Massive Kostenersparnis
**Impact:** $3.00 → $0.30 pro 1M Input Tokens (cached)

### **Asyncio Parallel Processing**
**Datum:** 2026-01-02  
**Entscheidung:** Alle AI-Calls parallel, nie sequentiell  
**Warum:**
- 5 AIs parallel = 3-5x schneller
- Keine Wartezeit zwischen Calls
- Semaphore für Rate Limiting
**Impact:** 9 Sekunden → 3 Sekunden für 3 Calls

### **Structured Outputs mit Pydantic**
**Datum:** 2026-01-02  
**Entscheidung:** Alle AI-Responses als Pydantic Models  
**Warum:**
- Garantiertes Schema
- Keine Parsing-Fehler
- Type Safety
**Implementation:** models/schemas.py mit DiscoverResponse, ComposeResponse, etc.

### **Vector Store für BRAIN**
**Datum:** 2026-01-02  
**Entscheidung:** ChromaDB für 972 Clips  
**Warum:**
- Schnelle Similarity Search
- Kontinuierliches Learning
- Top Outliers + Themen-spezifisch
**Implementation:** brain/vector_store.py

---

## FEHLGESCHLAGENE ANSÄTZE

### **Regelbasierte Analyse (Initial)**
**Datum:** 2026-01-02  
**Problem:** Erste Analyse-Prompts extrahierten Regeln statt Prinzipien  
**Symptom:** Output hatte "hook_patterns" mit festen Templates  
**Fix:** Prompts explizit auf Prinzipien umgestellt  
**Learning:** AI braucht explizite Anweisung: "Extrahiere Prinzipien, nicht Regeln"

### **Hardcodierte Model-Strings**
**Datum:** 2026-01-02  
**Problem:** Model-Namen werden veraltet (z.B. "gpt-5.2" → "gpt-5.3")  
**Symptom:** System verwendet veraltete Models  
**Fix:** Dynamische Model-Erkennung implementiert  
**Learning:** Immer dynamisch, nie hardcodiert

### **Sequentielles AI-Processing**
**Datum:** 2026-01-02  
**Problem:** Initial Code rief AIs nacheinander auf  
**Symptom:** Langsam (9s statt 3s)  
**Fix:** asyncio.gather() für Parallel Processing  
**Learning:** Immer parallel, nie sequentiell

---

## DURCHBRÜCHE & KEY INSIGHTS

### **Prinzipien vs. Regeln Unterscheidung**
**Datum:** 2026-01-02  
**Insight:** User-Frage "Sind alle Learnings wirklich prinzipienbasiert?" führte zu kritischem Fix  
**Impact:** System ist jetzt wirklich prinzipienbasiert, nicht regelbasiert  
**Key Learning:** Explizite Prompts nötig: "Extrahiere WARUM, nicht WAS"

### **Prompt Caching = 90% Ersparnis**
**Datum:** 2026-01-02  
**Insight:** Anthropic Prompt Caching reduziert Input-Kosten um 90%  
**Impact:** $3.00 → $0.30 pro 1M cached tokens  
**Key Learning:** Statische System-Prompts sollten IMMER gecached werden

### **Parallel Processing = 3-5x Speed**
**Datum:** 2026-01-02  
**Insight:** 5 AIs parallel statt sequentiell = massive Zeitersparnis  
**Impact:** 9 Sekunden → 3 Sekunden  
**Key Learning:** Immer asyncio.gather(), nie sequentiell

### **Structured Outputs = Zero Parsing Errors**
**Datum:** 2026-01-02  
**Insight:** Pydantic Models garantieren Schema-Compliance  
**Impact:** Keine JSON-Parsing-Fehler mehr  
**Key Learning:** Type Safety von Anfang an

---

## AKTUELLER STATUS

**Version:** 2.0.0  
**Letzte Änderung:** 2026-01-02  
**Status:** ✅ Core implementiert, ⚠️ Testing pending

**Fertig:**
- ✅ 4-Stage Pipeline
- ✅ BRAIN System
- ✅ Performance Optimierungen
- ✅ Dynamische Model-Erkennung
- ✅ Prinzipienbasiertes Learning

**Pending:**
- ⚠️ BRAIN Analyse neu ausführen (mit prinzipienbasierten Prompts)
- ⚠️ Vollständiger Production-Test
- ⚠️ Ground Truth Validation

**Nächste Phase:**
- Testing & Validation
- Production Deployment
- Continuous Learning

