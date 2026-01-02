"""
GODMODE Evaluation

Premium-Tier finale Evaluation mit Opus 4.5.
Wird am Ende von VALIDATE verwendet für finale Entscheidungen.

Logik aus V1 übernommen - funktioniert gut als finaler Quality Gate.

Wann einsetzen (laut PRD):
- Nach VALIDATE Stage
- Für finale "Approve/Reject" Entscheidung
- Nur auf Clips die VALIDATE bestanden haben
- Batched für Kosteneffizienz
"""

from typing import List, Dict
from dataclasses import dataclass

from models.base import ClaudeModel
from prompts.identities import QUALITY_ORACLE, ALGORITHM_CONTEXT


@dataclass
class GodmodeResult:
    """Result of Godmode evaluation."""
    clip_id: str
    score: int  # 0-50
    verdict: str  # "viral", "good", "weak", "reject"
    reasoning: str
    strengths: List[str]
    weaknesses: List[str]


async def godmode_evaluate(
    clips: List[Dict],
    batch_size: int = 4
) -> List[GodmodeResult]:
    """
    Premium Godmode Evaluation mit Opus 4.5.
    
    Bewertet Clips final und gibt Score 0-50.
    
    Args:
        clips: List of validated clips
        batch_size: Clips per batch (für Kosteneffizienz)
        
    Returns:
        List of GodmodeResult
    """
    print(f"\n{'='*70}")
    print("💎 GODMODE EVALUATION (Opus 4.5)")
    print(f"{'='*70}")
    print(f"   Clips to evaluate: {len(clips)}")
    print(f"   Batch size: {batch_size}")
    
    # Use Opus for premium evaluation
    model = ClaudeModel("claude-opus-4-20250514")
    
    results = []
    
    # Process in batches
    for i in range(0, len(clips), batch_size):
        batch = clips[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(clips) + batch_size - 1) // batch_size
        
        print(f"\n   Batch {batch_num}/{total_batches}...")
        
        batch_results = await _evaluate_batch(model, batch)
        results.extend(batch_results)
    
    # Summary
    viral = sum(1 for r in results if r.verdict == "viral")
    good = sum(1 for r in results if r.verdict == "good")
    weak = sum(1 for r in results if r.verdict == "weak")
    reject = sum(1 for r in results if r.verdict == "reject")
    
    print(f"\n   Results:")
    print(f"   🔥 Viral (45+): {viral}")
    print(f"   ✅ Good (35-44): {good}")
    print(f"   ⚠️ Weak (25-34): {weak}")
    print(f"   ❌ Reject (<25): {reject}")
    
    return results


async def _evaluate_batch(
    model: ClaudeModel,
    clips: List[Dict]
) -> List[GodmodeResult]:
    """Evaluate a batch of clips."""
    
    # Build batch prompt
    clips_text = ""
    for i, clip in enumerate(clips, 1):
        clips_text += f"""
═══════════════════════════════════════════════════════════
CLIP {i}
═══════════════════════════════════════════════════════════
Hook: "{clip.get('hook_text', 'N/A')[:150]}"
Dauer: {clip.get('total_duration', 0):.1f}s
Struktur: {clip.get('structure_type', 'unknown')}
Reasoning: {clip.get('reasoning', 'N/A')[:200]}
"""
    
    system = f"""{ALGORITHM_CONTEXT}

{QUALITY_ORACLE}

DU BIST DER FINALE RICHTER.
Dein Urteil entscheidet ob ein Clip veröffentlicht wird oder nicht.
Sei STRENG aber FAIR. Nutze deine 50.000+ Clip Erfahrung."""

    prompt = f"""
FINALE GODMODE EVALUATION

Bewerte jeden Clip auf einer Skala von 0-50:
- 45-50: 🔥 VIRAL - Wird definitiv viral gehen
- 35-44: ✅ GOOD - Solide Performance erwartet
- 25-34: ⚠️ WEAK - Braucht Verbesserung
- 0-24: ❌ REJECT - Nicht veröffentlichen

{clips_text}

BEWERTUNGSKRITERIEN:
1. Hook Power (0-15): Stoppt der Hook den Scroll in 3 Sekunden?
2. Content Quality (0-15): Gibt jede Sekunde Grund weiterzuschauen?
3. Completion Potential (0-10): Werden Viewer bis zum Ende schauen?
4. Viral Factors (0-10): Wird geteilt/gespeichert werden?

Für jeden Clip, antworte mit:
```json
[
  {{
    "clip_index": 1,
    "score": 42,
    "verdict": "good",
    "reasoning": "Starker paradoxer Hook, aber Mittelteil könnte straffer sein",
    "strengths": ["Hook öffnet sofort Loop", "Emotionale Payoff"],
    "weaknesses": ["Transition bei 0:15 etwas langsam"]
  }}
]
```

WICHTIG: Sei EHRLICH. Lieber ein Clip weniger als ein schlechter Clip draußen.
"""

    response = await model.generate(
        prompt=prompt,
        system=system,
        temperature=0.3,
        max_tokens=4096
    )
    
    # Parse response
    results = []
    try:
        import json
        import re
        json_match = re.search(r'\[[\s\S]*\]', response.content)
        if json_match:
            evaluations = json.loads(json_match.group())
            
            for eval_data in evaluations:
                idx = eval_data.get("clip_index", 1) - 1
                if 0 <= idx < len(clips):
                    results.append(GodmodeResult(
                        clip_id=clips[idx].get("clip_id", f"clip_{idx+1}"),
                        score=eval_data.get("score", 0),
                        verdict=eval_data.get("verdict", "reject"),
                        reasoning=eval_data.get("reasoning", ""),
                        strengths=eval_data.get("strengths", []),
                        weaknesses=eval_data.get("weaknesses", [])
                    ))
    except Exception as e:
        print(f"   ⚠️ Parse error: {e}")
    
    # Fill in missing results
    for i, clip in enumerate(clips):
        if not any(r.clip_id == clip.get("clip_id", f"clip_{i+1}") for r in results):
            results.append(GodmodeResult(
                clip_id=clip.get("clip_id", f"clip_{i+1}"),
                score=0,
                verdict="reject",
                reasoning="Evaluation failed",
                strengths=[],
                weaknesses=["Could not evaluate"]
            ))
    
    return results


def filter_by_godmode(
    clips: List[Dict],
    results: List[GodmodeResult],
    min_score: int = 35
) -> List[Dict]:
    """
    Filter clips based on Godmode scores.
    
    Args:
        clips: Original clips
        results: Godmode results
        min_score: Minimum score to pass (default 35 = "good")
        
    Returns:
        Filtered clips that passed
    """
    passed = []
    
    for clip in clips:
        clip_id = clip.get("clip_id", "")
        result = next((r for r in results if r.clip_id == clip_id), None)
        
        if result and result.score >= min_score:
            clip["godmode_score"] = result.score
            clip["godmode_verdict"] = result.verdict
            clip["godmode_reasoning"] = result.reasoning
            passed.append(clip)
    
    return passed

