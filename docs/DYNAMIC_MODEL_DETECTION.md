# Dynamic AI Model Detection

Das System verwendet **dynamische Model-Erkennung**, um immer die neuesten AI-Models zu verwenden.

## ✅ Vorteile

- **Keine veralteten Model-Strings**: System aktualisiert sich automatisch
- **Cache-basiert**: Model-Erkennung wird 24h gecached (keine teuren API-Calls)
- **Fallback-Sicher**: Wenn Erkennung fehlschlägt, werden bekannte Latest-Models verwendet

## 📖 Verwendung

### In Code

```python
from models.base import get_model

# Neuestes Opus
claude = get_model("anthropic", tier="opus")

# Neuestes GPT Flagship
gpt = get_model("openai", tier="flagship")

# Neuestes Gemini Pro
gemini = get_model("google", tier="pro")
```

### Verfügbare Tiers

| Provider | Tiers |
|----------|-------|
| `anthropic` | `opus`, `sonnet`, `haiku` |
| `openai` | `flagship`, `pro`, `mini`, `codex` |
| `gemini` | `pro`, `flash`, `flash_lite` |
| `xai` | `flagship`, `standard`, `mini` |
| `deepseek` | `chat`, `reasoner` |

## 🔧 CLI Commands

```bash
# Model-Erkennung ausführen (erstellt Cache)
python -m models.auto_detect

# Cache ignorieren und neu erkennen
python -m models.auto_detect --force

# Aktuelle Konfiguration anzeigen
python -m models.auto_detect --print
```

## 📁 Cache

- **Location**: `config/detected_models.json`
- **Dauer**: 24 Stunden
- **Format**: JSON mit `cached_at` Timestamp

## ⚠️ Wichtige Regeln

### ❌ NIEMALS hardcoden:
```python
# BAD - Wird veraltet!
model = "claude-opus-4-20250514"
model = "gpt-5.2"
```

### ✅ IMMER dynamisch:
```python
# GOOD - Immer neueste!
model = get_model("anthropic", tier="opus")
model = get_model("openai", tier="flagship")
```

## 🔄 Model-Updates

Wenn neue Models released werden:

1. **Automatisch**: System erkennt sie beim nächsten Cache-Refresh
2. **Manuell**: `models/auto_detect.py` aktualisieren mit neuen Model-Namen
3. **Fallback**: Bekannte Latest-Models werden verwendet, wenn Erkennung fehlschlägt

## 📚 API Dokumentation

- OpenAI: https://platform.openai.com/docs/models
- Anthropic: https://docs.anthropic.com/en/docs/about-claude/models
- xAI: https://docs.x.ai/docs/models
- DeepSeek: https://api-docs.deepseek.com/
- Gemini: https://ai.google.dev/gemini-api/docs/models


