"""
GODMODE Evaluation

Premium-Tier finale Evaluation mit Opus 4.5.
Wird am Ende von VALIDATE verwendet für finale Entscheidungen.

UPGRADE: Jetzt Brain-Infused (nutzt learned_patterns für Bewertung).
"""

from typing import List, Dict
from dataclasses import dataclass
import json
import re

from models.base import ClaudeModel
from prompts.identities import QUALITY_ORACLE, ALGORITHM_CONTEXT
from brain import load_principles


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
    Nutzt PROJEKT-BRAIN für kontextbezogene Bewertung.
    
    Args:
        clips: List of validated clips
        batch_size: Clips per batch
        
    Returns:
        List of GodmodeResult
    """
    print(f"\n{'='*70}")
    print("💎 GODMODE EVALUATION (Opus 4.5 + Brain Infused)")
    print(f"{'='*70}")
    print(f"   Clips to evaluate: {len(clips)}")
    
    # 1. Load Brain Knowledge
    principles = load_principles()
    viral_patterns = principles.get("viral_patterns", [])  # Archetypes
    learned_rules = principles.get("editing_patterns", {}).get("rules", [])
    
    brain_context = {
        "top_archetypes": viral_patterns[:3],  # Top 3 archetypes
        "critical_rules": learned_rules[:5]    # Top 5 rules
    }
    
    # Use Opus (dynamic detection)
    from models.base import get_model
    model = get_model("anthropic", tier="opus")
    
    results = []
    
    # Process in batches
    for i in range(0, len(clips), batch_size):
        batch = clips[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(clips) + batch_size - 1) // batch_size
        
        print(f"\n   Batch {batch_num}/{total_batches}...")
        
        batch_results = await _evaluate_batch(model, batch, brain_context)
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
    clips: List[Dict],
    brain_context: Dict
) -> List[GodmodeResult]:
    """Evaluate a batch of clips using Brain context."""
    
    # Build batch prompt with simplified structure
    clips_data = []
    for i, clip in enumerate(clips, 1):
        clips_data.append({
            "index": i,
            "hook": clip.get('hook_text', 'N/A'),
            "duration": f"{clip.get('total_duration', 0):.1f}s",
            "structure": clip.get('structure_type', 'unknown'),
            "creator_reasoning": clip.get('reasoning', 'N/A')
        })
    
    system = f"""{ALGORITHM_CONTEXT}

{QUALITY_ORACLE}

<brain_knowledge>
Das sind die gelernten Erfolgsmuster dieses Creators (BRAIN):
{json.dumps(brain_context, ensure_ascii=False, indent=2)}
</brain_knowledge>

DU BIST DER FINALE RICHTER.
Dein Urteil entscheidet ob ein Clip veröffentlicht wird.
Nutze dein allgemeines Wissen UND die <brain_knowledge> oben.
"""

    prompt = f"""
FINALE GODMODE EVALUATION

Bewerte diese Clips auf Skala 0-50.
Prüfe besonders, ob sie gegen die "critical_rules" aus dem Brain verstoßen.

<candidates>
{json.dumps(clips_data, ensure_ascii=False, indent=2)}
</candidates>

<scoring_guide>
- 45-50: 🔥 VIRAL (Perfekter Hook + Brain Match)
- 35-44: ✅ GOOD (Stark, kleine Schwächen)
- 25-34: ⚠️ WEAK (Refinement nötig)
- 0-24: ❌ REJECT
</scoring_guide>

Antworte strikt mit JSON:
```json
[
  {{
    "clip_index": 1,
    "score": 42,
    "verdict": "good",
    "reasoning": "Hook ist stark, passt zum Archetyp X...",
    "strengths": ["..."],
    "weaknesses": ["..."]
  }}
]
```
"""

    response = await model.generate(
        prompt=prompt,
        system=system,
        temperature=0.3,
        max_tokens=4096,
        cache_system=True  # Enable caching for the heavy system prompt
    )

    # Parse response
    results = []
    try:
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

    # Fill missing
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
    """Filter clips based on Godmode scores."""
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
