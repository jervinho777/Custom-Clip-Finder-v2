# Custom Clip Finder v2 - Finale System-Architektur

## 🎯 MASTER PRINCIPLE
> "Make a video so good that people cannot physically scroll past"

---

## 📊 PIPELINE FLOW

```
LONGFORM VIDEO
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  TRANSCRIPTION (AssemblyAI)                                     │
│  - Word-level timestamps                                        │
│  - Segment generation                                           │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  DISCOVER (Multi-AI Ensemble: 5 AIs parallel)                   │
│  - Identifiziere ALLE viral-fähigen Momente                     │
│  - So viele wie MÖGLICH, so viele wie NÖTIG                     │
│  - Pattern-Erkennung: Hooks, Stories, Statements                │
│  - Output: Liste von Momenten mit Timestamps + Reasoning        │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  EARLY VALIDATE (Quick Filter)                                  │
│  - Filtere offensichtlich schwache Momente                      │
│  - Spare teure COMPOSE-Calls                                    │
│  - Output: Bereinigte Moment-Liste                              │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  COMPOSE (Multi-AI Ensemble: 5 AIs parallel)                    │
│  - Strukturiere Momente zu fertigen Clips                       │
│  - Hook Extraction wenn nötig                                   │
│  - Cross-Moment Composition wenn sinnvoll                       │
│  - Output: Clip-Strukturen mit Segment-Liste                    │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  GODMODE (1x Opus - Unabhängiger Final Review)                  │
│  - Sieht ALLE Reasonings der vorherigen AIs                     │
│  - Macht finale Entscheidung                                    │
│  - Rankt alle Clips                                             │
│  - Output: Final gerankte Clips mit Score                       │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  EXPORT                                                         │
│  - Premiere Pro XML (fertige Sequenz, neue Reihenfolge)         │
│  - MP4 (optional: FFmpeg Rohschnitt)                            │
│  - JSON (Metadaten + Reasonings)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 COMPOSE REGELN (KRITISCH!)

### ✅ ERLAUBT
- Reihenfolge von Segmenten ändern
- Sätze am Ende/Anfang/Mitte schneiden
- Segmente aus verschiedenen Video-Stellen kombinieren
- Füllwörter vorsichtig entfernen (Jump Cuts)
- Hook von hinten nach vorne ziehen

### ❌ NICHT ERLAUBT
- Wörter ändern
- Sätze umformulieren
- Text generieren oder hinzufügen
- "Bessere" Formulierungen erfinden

**Grund:** Wir arbeiten mit fertigem Videomaterial. Können physisch nichts am gesprochenen Text ändern!

---

## 🎯 HOOK STRATEGIE

### Priorität 1: Native Hook
- Prüfe ob der Moment selbst eine starke Hook hat
- Wenn ja → Clean Extraction

### Priorität 2: Hook Extraction
- Wenn native Hook schwach, aber Payoff stark
- Ziehe Payoff nach vorne als Hook
- Beispiel: "Arbeite niemals für Geld" (war am Ende, jetzt am Anfang)

### Priorität 3: Cross-Moment Hook (Ausnahme!)
- NUR wenn keine passende Hook im Part selbst
- Hook aus anderem Teil nehmen
- MUSS kontextuell Sinn machen
- Nicht nur weil Hook "gut klingt"

---

## 📏 CLIP LÄNGEN

| Typ | Länge | Automatisch erkannt |
|-----|-------|---------------------|
| Quick Insight | 30-60s | ✅ |
| Standard Story | 60-90s | ✅ |
| Extended Story | 2-10 min | ✅ (prinzipienbasiert) |

**Keine harten Grenzen!** System erkennt automatisch was der Content braucht.

### Lange Stories Strategie
1. Spannendsten/verwirrendsten Teil als "Trailer" nach vorne
2. Dann chronologische Geschichte
3. Trailer-Moment bleibt auch an Original-Position

---

## 🤖 MULTI-AI ENSEMBLE

### Stage: DISCOVER & COMPOSE
```
┌─────────────────────────────────────────────┐
│  5 AIs arbeiten parallel                    │
│  ├── GPT-4o                                 │
│  ├── Claude Sonnet                          │
│  ├── Gemini Pro                             │
│  ├── Grok                                   │
│  └── DeepSeek                               │
│                                             │
│  Debattieren → Konsens finden               │
└─────────────────────────────────────────────┘
```

### Stage: GODMODE (Final)
```
┌─────────────────────────────────────────────┐
│  1x Claude Opus (Premium, unabhängig)       │
│  ├── Sieht ALLE vorherigen Reasonings       │
│  ├── War NICHT in Debatte involviert        │
│  └── Macht finale Entscheidung              │
└─────────────────────────────────────────────┘
```

---

## 🧠 BRAIN SYSTEM

### Learning Input (Manuell)
```csv
# isolierte_clips.csv
clip_name,views,likes,shares,comments,hook_text,duration
"Arbeite niemals...",5200000,320000,45000,12000,"Arbeite niemals für Geld",59

# longform_pairs.csv  
longform_name,clip_name,clip_start,clip_end,views,transformation_type
"Dieter Lange.mp4","Arbeite niemals...",564.6,655.1,5200000,hook_extraction
```

### Vector Store Struktur
```
├── Top Outliers (IMMER dabei, themenübergreifend)
│   └── Die absolut besten 10-20 Clips aller Zeiten
│
└── Themen-spezifisch (gefiltert je nach Input)
    ├── Persönlichkeitsentwicklung
    ├── Business/Finanzen
    ├── Gesundheit
    └── ...
```

### Prinzipienbasiert, NICHT Regelbasiert!
- Beispiele dienen als INSPIRATION
- KEINE 1:1 Kopie von Regeln
- Prinzipien extrahieren, nicht Formeln

---

## 📤 XML EXPORT FORMAT

```xml
<!-- Premiere Pro kompatibel (XMEML v4) -->
<sequence>
  <!-- Segment 1: Original 653s → Timeline 0s (Hook Extraction) -->
  <clipitem>
    <in>16325</in>      <!-- Frame im Quellvideo -->
    <out>16400</out>
    <start>0</start>    <!-- Position auf Timeline -->
    <end>75</end>
  </clipitem>
  
  <!-- Segment 2: Original 564s → Timeline 75s -->
  <clipitem>
    <in>14100</in>
    <out>16325</out>
    <start>75</start>
    <end>2300</end>
  </clipitem>
</sequence>
```

**Output:** Fertige Sequenz, Editor muss nur noch Effekte/Captions hinzufügen.

---

## 💰 KOSTEN-STRATEGIE

### Testing Phase
| Model | Provider | Cost/1M tokens |
|-------|----------|----------------|
| GPT-4o-mini | OpenAI | ~$0.15 |
| Claude Sonnet | Anthropic | ~$3 |
| Gemini Flash | Google | ~$0.075 |

**Budget:** <$1/Video

### Production Phase
| Model | Provider | Cost/1M tokens |
|-------|----------|----------------|
| GPT-4o | OpenAI | ~$5 |
| Claude Opus | Anthropic | ~$15 |
| Gemini Pro | Google | ~$3.50 |

**Budget:** <$10/Video

### Geplantes Feature
- Modell-Auswahl vor Ausführung
- Kosten-Preview anzeigen
- Qualität vs. Budget Slider

---

## ✅ GROUND TRUTH TEST

### Test-Video: Dieter Lange.mp4
**Pfad:** `/Users/jervinquisada/custom-clip-finder/ARCHIVED_LARGE_FILES_20260102/Dieter Lange.mp4`

### Bekannte Viral-Momente (MUSS gefunden werden):

1. **"Arbeite niemals für Geld"**
   - Original: 564s - 655s
   - Hook: "Arbeite niemals für Geld" (bei 653s)
   - Pattern: Hook Extraction

2. **"Wir sind mit Talenten geboren"**
   - Original: ~476s - 534s
   - Hook: "Aus einem Ackergaul wird kein Rennpferd"

3. **"Was willst du eigentlich mal werden?"**
   - Original: ~315s - 340s
   - Hook: "Was willst du eigentlich mal werden? Das impliziert doch, dass wir nichts sind"

### Test-Kriterien
```python
# Alle diese Hooks MÜSSEN gefunden werden
required_hooks = [
    "Arbeite niemals für Geld",
    "Ackergaul",
    "Was willst du eigentlich mal werden"
]

for hook in required_hooks:
    assert any(hook.lower() in m.hook_text.lower() for m in discovered_moments)
```


