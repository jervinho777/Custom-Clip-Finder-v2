# Training Data: Longform → Viral Clip Paare

## Vollständige Übersicht der Beispiel-Daten

Diese Datei dokumentiert alle bekannten Longform → Clip Paare für System-Validierung.

---

## ✅ VERIFIZIERTE PAARE

### 1. Dieter Lange: "Arbeite niemals für Geld"
| | |
|---|---|
| **Longform** | `Dieter Lange_transcript.json` (30 min) |
| **Clip** | `Dieter Lange Viral Clip_transcript.json` (59s) |
| **Original Position** | 564s - 655s |
| **Pattern** | **HOOK EXTRACTION** |
| **Hook** | "Arbeite niemals für Geld" (stand im Original AM ENDE!) |
| **Learning** | Payoff-Statement wird zum Hook |

### 2. Dr. Stefan Frädrich: "Lebenslinie"
| | |
|---|---|
| **Longform** | `Dr_Stefan_Frädrich_transcript.json` (20 min) |
| **Clip** | `Lebenslinie V2_NOCTA_transcript.json` (72s) |
| **Original Position** | 1066s - 1165s |
| **Pattern** | **CLEAN EXTRACTION** |
| **Hook** | "Dein Leben findet statt auf einer Lebenslinie" |
| **Learning** | Hook war schon stark, nur gekürzt |

### 3. Chris Surel: "Schlafen ist wie Fußball"
| | |
|---|---|
| **Longform** | `Chris Surel_transcript.json` (18 min) |
| **Clip** | `top02_Chris Surel_Beliefbreaker...` (42s) |
| **Original Position** | ~278s - 340s |
| **Pattern** | **METAPHOR HOOK** |
| **Hook** | "Schlafen ist so wie Fußball spielen. Es ist ein Spiel, was 90 Minuten dauert." |
| **Learning** | Starke Metaphern = starke Hooks |

### 4. Chris Surel: "Hört auf auszuschlafen"
| | |
|---|---|
| **Longform** | `Chris Surel_transcript.json` (18 min) |
| **Clip** | `top06_Greator__transcript.json` (37s) |
| **Original Position** | ~907s - 966s |
| **Pattern** | **BELIEFBREAKER** |
| **Hook** | "Hört bitte auf am Wochenende auszuschlafen" |
| **Learning** | Gegen-Intuitive Aussagen = instant Attention |

### 5. Robert Marc Lehmann: "Mondfisch mit Kindersocken"
| | |
|---|---|
| **Longform** | `Meeresbiologe Robert Marc Lehmann über Zoos 3nach9_transcript.json` (16 min) |
| **Clip** | `top10_Robert Marc Lehmann__transcript.json` (38s) |
| **Original Position** | ~474s - 520s |
| **Pattern** | **SHOCK STORY** |
| **Hook** | "Die Flossen sind ihm vergammelt. Meine Chefin fand die aberwitzige Idee ganz gut, ihm Socken, Kindersocken über die Flossen zu stülpen..." |
| **Learning** | Schock-Element + Absurdität = viral |

---

## 📂 NOCH ZU MATCHENDE CLIPS

| Clip | Vermutetes Longform | Notes |
|------|---------------------|-------|
| `top09_Greator__transcript.json` | ? | |
| `top14_Robert Marc Lehmann__transcript.json` | Robert Marc Lehmann | |
| `top19_Greator__transcript.json` | ? | |
| `top37_Gereon Jörn__transcript.json` | ? (kein Longform vorhanden) | |
| `USED_17 - Krankheit_transcript.json` | ? | |

---

## 📊 LONGFORMS OHNE GEMATCHE CLIPS

| Longform | Duration | Potential Clips |
|----------|----------|-----------------|
| `CWBeziehung_transcript.json` | ~18 min | Beziehungs-Tipps, Tools |
| `Tobi Beck_transcript.json` | ~18 min | "Ruth" Geschichte (SEHR emotional!) |
| `Patric Heizmann RN2021_transcript.json` | ? | |
| `Ruth LONG V1_SHORTS_transcript.json` | ? | (könnte schon Clip sein) |

---

## 🎯 PATTERN LIBRARY

### 1. HOOK EXTRACTION
- Starkes Statement am ENDE einer Story
- Wird nach VORNE gezogen im Clip
- Beispiel: "Arbeite niemals für Geld"

### 2. CLEAN EXTRACTION
- Hook ist schon am Anfang stark
- Nur saubere Grenzen finden
- Beispiel: "Dein Leben findet statt auf einer Lebenslinie"

### 3. METAPHOR HOOK
- Starker Vergleich erzeugt sofortige Aufmerksamkeit
- "X ist wie Y" Struktur
- Beispiel: "Schlafen ist wie Fußball spielen"

### 4. BELIEFBREAKER
- Gegen-intuitive Aussage
- Widerspricht Common Sense
- Beispiel: "Hört auf auszuschlafen"

### 5. SHOCK STORY
- Absurde/schockierende Details
- Emotionale Reaktion garantiert
- Beispiel: "Kindersocken an Fischflossen"

---

## ⚙️ SYSTEM-VALIDIERUNG

Das System MUSS in der Lage sein:
1. **DISCOVER**: Alle 5 verifizierten Clip-Momente zu finden
2. **COMPOSE**: Korrekte Patterns zuzuweisen
3. **VALIDATE**: Hook Strength >= 8 zu vergeben
4. **EXPORT**: Saubere In/Out Points zu setzen

### Test-Kommando:
```bash
python tests/validate_examples.py
```

Erwartetes Ergebnis: `✅ Gefunden: 5/5 bekannte Viral-Momente`


