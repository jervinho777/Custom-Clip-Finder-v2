# Workflow: Neue virale Clips hinzufügen

Dieses Dokument beschreibt, wie du neue virale Clips zum BRAIN hinzufügen kannst, nachdem sie auf Social Media viral gegangen sind.

## Wann hinzufügen?

✅ **Hinzufügen wenn:**
- Clip hat >500k Views erreicht
- Clip hat >30% Completion Rate
- Du hast das Original-Longform Video

❌ **Nicht hinzufügen wenn:**
- Clip ist noch nicht getestet/gepostet
- Keine Metriken verfügbar
- Kein Longform vorhanden (für Paare)

---

## Option 1: Isolierten Clip hinzufügen

Für virale Clips ohne Longform-Original.

### Schritt 1: Clip-Info zur CSV hinzufügen

```csv
# Öffne: data/training/goat_clips.csv
# Füge neue Zeile hinzu:

url,views,completion_rate,source
https://tiktok.com/@user/video/123,1500000,0.42,tiktok
```

### Schritt 2: Transkript generieren (falls nicht vorhanden)

```bash
python main.py transcribe "path/to/clip.mp4"
```

### Schritt 3: Zur goat_training_data.json hinzufügen

Die Clips werden automatisch beim nächsten Brain-Update verarbeitet.

---

## Option 2: Longform + Clip Paar hinzufügen

Für virale Clips MIT dem Original-Longform Video.

### Schritt 1: Videos vorbereiten

```
data/training/Longform and Clips/
├── Longform_Name.mp4
└── Viral_Clip_Name.mp4
```

### Schritt 2: Transkripte generieren

```bash
python main.py transcribe "data/training/Longform and Clips/Longform_Name.mp4"
python main.py transcribe "data/training/Longform and Clips/Viral_Clip_Name.mp4"
```

### Schritt 3: Paar zur Config hinzufügen

Öffne `data/training/pairs_config.json` und füge hinzu:

```json
{
  "id": "unique_id",
  "longform": "Longform_Name_transcript.json",
  "clip": "Viral_Clip_Name_transcript.json",
  "pattern": "hook_extraction",
  "notes": "Beschreibung warum dieser Clip viral ging"
}
```

**Pattern-Typen:**
- `hook_extraction` - Payoff wurde zum Hook
- `clean_extraction` - Natürlicher Hook war stark
- `metaphor_hook` - Metapher als Hook
- `beliefbreaker` - Kontraintuitive Aussage
- `shock_story` - Schockierender/absurder Moment
- `paradox_statement` - Paradoxe Behauptung
- `everyday_mystery` - Alltags-Enthüllung

---

## Schritt 4: Brain neu analysieren

Nach dem Hinzufügen neuer Clips/Paare:

```bash
./run_brain_analysis.sh
```

**Hinweis:** 
- Die Analyse dauert 30-60 Minuten
- Kosten: ~$15-20 (Claude Opus)
- Am besten über Nacht laufen lassen

---

## Verzeichnisstruktur

```
data/
├── training/
│   ├── goat_clips.csv          # Clip-Links + Metriken
│   ├── goat_training_data.json # Alle Clips mit Transkripten
│   ├── pairs_config.json       # LF+SF Paar-Definitionen
│   └── Longform and Clips/     # Video-Dateien
│
├── cache/
│   └── transcripts/            # Generierte Transkripte
│
└── learnings/
    ├── isolated_analysis.json  # Clip-Analyse
    └── pairs_analysis.json     # Paar-Analyse
```

---

## Tipps

1. **Qualität vor Quantität**: Lieber 10 echte virale Hits als 100 mittelmäßige Clips

2. **Metriken dokumentieren**: Speichere Views, Completion Rate, Engagement

3. **Pattern notieren**: Schreibe auf WARUM der Clip viral ging (hilft beim Lernen)

4. **Regelmäßig updaten**: Nach 10-20 neuen Clips → Brain neu analysieren



