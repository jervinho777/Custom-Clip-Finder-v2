# Custom Clip Finder V2 - Performance Optimizations

## Übersicht

| Optimierung | Kostenersparnis | Geschwindigkeit |
|-------------|-----------------|-----------------|
| Prompt Caching | 90% auf Anthropic | - |
| Parallel Processing | - | 3-5x schneller |
| Structured Outputs | - | Keine Parsing-Fehler |
| Batch API (Night Mode) | 50% | Verzögert (24h) |

---

## 1. Prompt Caching (MANDATORY für Anthropic)

Cache statische Inhalte (Supreme Identity + BRAIN) für 90% Ersparnis.

### Verwendung

```python
from models.base import get_model

model = get_model("anthropic", tier="opus")

response = await model.generate(
    prompt=transcript,  # Dynamisch, nicht gecached
    system=SUPREME_IDENTITY + brain_context,  # Statisch, gecached
    cache_system=True  # ← AKTIVIERT CACHING
)

# Prüfe Cache-Nutzung
print(f"Cache Read: {response.cache_read_tokens}")  # 90% günstiger!
print(f"Cache Write: {response.cache_write_tokens}")  # Erste Call only
```

### Kosten
- Ohne Cache: $3.00/1M Input Tokens
- Cache Write: $3.75/1M (nur erste Call)
- Cache Read: $0.30/1M (90% Ersparnis!)

---

## 2. Asyncio Parallel Processing (MANDATORY)

Alle AI-Calls parallel, niemals sequentiell.

### Verwendung

```python
from pipeline.optimized import OptimizedCaller

caller = OptimizedCaller()

# 5 AIs parallel aufrufen
responses = await caller.parallel_call(
    prompt=transcript,
    system=identity + brain_context,
    providers=[
        ("anthropic", "sonnet"),
        ("openai", "flagship"),
        ("google", "flash"),
        ("xai", "flagship"),
        ("deepseek", "chat"),
    ]
)
```

### Regeln

❌ NIEMALS sequentiell:
```python
r1 = await call_claude(...)  # 3s
r2 = await call_openai(...)  # 3s
r3 = await call_gemini(...)  # 3s
# Total: 9 Sekunden
```

✅ IMMER parallel:
```python
results = await asyncio.gather(
    call_claude(...),
    call_openai(...),
    call_gemini(...),
)
# Total: 3 Sekunden
```

---

## 3. Structured Outputs mit Pydantic (MANDATORY)

Alle AI-Antworten müssen Pydantic Models verwenden.

### Definierte Schemas

- `DiscoverResponse` - DISCOVER Stage
- `ComposeResponse` - COMPOSE Stage
- `ValidateResponse` - VALIDATE Stage
- `GodmodeResponse` - GODMODE Stage

### Verwendung

```python
from models.schemas import DiscoverResponse

response = await model.generate(
    prompt=transcript,
    system=identity,
    response_model=DiscoverResponse  # ← Strukturierter Output
)

# response.parsed ist DiscoverResponse Objekt
for moment in response.parsed.moments:
    print(moment.hook_text)
```

---

## 4. Batch API (OPTIONAL - Night Mode)

50% Kostenersparnis bei Bulk-Processing.

### Wann verwenden?

✅ Batch API:
- 10+ Videos über Nacht
- Training Data Generation
- Non-urgent Bulk Analysis

❌ Kein Batch API:
- Single Video Processing
- User wartet auf Ergebnis
- Real-time Applications

---

## Checklist für jeden AI-Call

- [ ] `async/await` verwendet?
- [ ] Teil von `asyncio.gather()` wenn mehrere Calls?
- [ ] `response_model` für Pydantic Structured Output?
- [ ] `cache_system=True` für Anthropic Calls?
- [ ] Rate Limiting mit Semaphore?
- [ ] Error Handling mit `return_exceptions=True`?

---

## Beispiel: Optimierter DISCOVER

```python
from pipeline.optimized import OptimizedCaller
from models.schemas import DiscoverResponse

caller = OptimizedCaller()

# 5 AIs parallel mit Caching und Structured Output
responses = await caller.parallel_discover(
    transcript=video_transcript,
    brain_context=principles_json,
    identity_prompt=SUPREME_IDENTITY_DISCOVER
)

# Jede Response ist ein validiertes DiscoverResponse Objekt
for response in responses:
    print(f"Provider: {response.ai_provider}")
    print(f"Moments found: {len(response.moments)}")
    for moment in response.moments:
        print(f"  - {moment.hook_text} ({moment.viral_potential}/10)")

# Cache-Statistiken anzeigen
caller.print_cache_stats()
```

---

## Dependencies

```bash
# Mit uv
uv add instructor aiohttp

# Mit pip
pip install instructor aiohttp
```

