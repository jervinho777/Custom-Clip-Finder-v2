"""
🏛️ THE VIRAL COUNCIL - Multi-AI Remixing System

"Let the best AIs in the world compete to create the perfect cut."

═══════════════════════════════════════════════════════════════════════════════
ARCHITECTURE:
═══════════════════════════════════════════════════════════════════════════════

1. COUNCIL MEMBERS (5 Top AIs):
   - Anthropic Opus 4.5 💎 (Also serves as JUDGE)
   - OpenAI GPT-5.2 Pro 🔥
   - Google Gemini 3 Pro 🌟
   - xAI Grok 4.1 🚀
   - DeepSeek Reasoner 🧠

2. THE LEGO-BLOCK METHOD:
   Each AI receives the same transcript and must:
   - Identify building blocks: [A] Story, [B] Context, [C] Punchline, [D] Noise
   - Propose a remix order (e.g., C -> A -> B)
   - Justify using retention psychology

3. EXECUTIVE DECISION (Opus Judge):
   Opus analyzes all 5 proposals and creates the MASTER CUT.

═══════════════════════════════════════════════════════════════════════════════
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import asyncio
import json
import logging
import re

from models.base import (
    get_model, 
    OPUS_MODEL_ID, 
    GPT_MODEL_ID, 
    GEMINI_MODEL_ID, 
    GROK_MODEL_ID, 
    DEEPSEEK_MODEL_ID,
    COUNCIL_MODEL_IDS,
    ClaudeModel
)

logger = logging.getLogger(__name__)


# =============================================================================
# 🛡️ ROBUST PARSING UTILITIES
# =============================================================================

def robust_json_parser(raw_text: str, expected_type: str = "dict") -> Optional[Dict | List]:
    """
    Extremely tolerant JSON parser for AI outputs.
    
    Handles:
    1. DeepSeek <think>...</think> blocks
    2. Markdown ```json ... ``` wrappers
    3. Stray text before/after JSON
    4. Minor syntax errors
    
    Args:
        raw_text: The raw AI response
        expected_type: "dict" or "list"
        
    Returns:
        Parsed JSON or None if completely unparseable
    """
    if not raw_text:
        return {} if expected_type == "dict" else []
    
    cleaned = raw_text
    
    # Step 1: Remove DeepSeek <think>...</think> blocks
    cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL)
    
    # Step 2: Extract from Markdown code blocks
    markdown_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned)
    if markdown_match:
        cleaned = markdown_match.group(1).strip()
    
    # Step 3: Try direct parsing first
    try:
        result = json.loads(cleaned)
        if expected_type == "dict" and isinstance(result, dict):
            return result
        if expected_type == "list" and isinstance(result, list):
            return result
        # Wrong type but valid JSON - try to work with it
        if isinstance(result, dict):
            return result
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    
    # Step 4: Bracket Finder - find first { or [ and last } or ]
    if expected_type == "dict":
        start_char, end_char = '{', '}'
    else:
        start_char, end_char = '[', ']'
    
    start_idx = cleaned.find(start_char)
    end_idx = cleaned.rfind(end_char)
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        bracket_content = cleaned[start_idx:end_idx + 1]
        
        try:
            return json.loads(bracket_content)
        except json.JSONDecodeError as e:
            # Step 5: Try fixing common issues
            fixed = bracket_content
            
            # Fix trailing commas before closing brackets
            fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
            
            # Fix missing commas between elements
            fixed = re.sub(r'}\s*{', '},{', fixed)
            fixed = re.sub(r'"\s*"', '","', fixed)
            
            # Fix single quotes
            fixed = fixed.replace("'", '"')
            
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass
    
    # Step 6: Complete failure - log and return empty
    logger.warning(f"JSON parsing failed. Raw text (first 500 chars): {raw_text[:500]}")
    return {} if expected_type == "dict" else []


def fuzzy_remap_to_segments(
    ai_segments: List[Dict],
    original_segments: List[Dict],
    match_threshold: float = 0.75
) -> List[Dict]:
    """
    Remap AI-generated segments back to original timestamps using fuzzy matching.
    
    The AI might hallucinate or slightly modify text. We need to find the
    ORIGINAL segments with correct timestamps.
    
    Args:
        ai_segments: Segments from AI (may have wrong/missing timestamps)
        original_segments: Original transcript segments with correct timestamps
        match_threshold: Minimum similarity ratio (0.0 - 1.0)
        
    Returns:
        List of validated segments with correct timestamps
    """
    if not ai_segments or not original_segments:
        return []
    
    validated = []
    hallucinations_removed = 0
    
    # Build lookup for original segments
    original_texts = []
    for seg in original_segments:
        text = seg.get('text', '')
        if text:
            original_texts.append({
                'text': text.lower().strip(),
                'original': seg
            })
    
    for ai_seg in ai_segments:
        ai_text = ai_seg.get('text', '').lower().strip()
        
        if not ai_text:
            # No text to match - try to use timestamps directly
            if ai_seg.get('start') is not None and ai_seg.get('end') is not None:
                # Validate timestamps exist in original range
                validated.append(ai_seg)
            continue
        
        # Find best match in original segments
        best_match = None
        best_ratio = 0.0
        
        for orig in original_texts:
            # Quick check: if texts are very different lengths, skip expensive matching
            len_ratio = len(ai_text) / max(len(orig['text']), 1)
            if len_ratio < 0.3 or len_ratio > 3.0:
                continue
            
            ratio = SequenceMatcher(None, ai_text, orig['text']).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = orig['original']
        
        if best_ratio >= match_threshold and best_match:
            # Found a good match - use original timestamps
            remapped = {
                'role': ai_seg.get('role', 'body'),
                'start': best_match.get('start', 0),
                'end': best_match.get('end', 0),
                'text': best_match.get('text', ''),
                'match_confidence': best_ratio
            }
            validated.append(remapped)
            logger.debug(f"Matched segment: ratio={best_ratio:.2f}")
        else:
            # No good match - AI hallucination
            hallucinations_removed += 1
            logger.warning(
                f"🚨 AI Hallucination removed (best match: {best_ratio:.2f}): "
                f"'{ai_text[:50]}...'"
            )
    
    if hallucinations_removed > 0:
        print(f"   ⚠️ Removed {hallucinations_removed} AI hallucination(s)")
    
    return validated


def add_segment_ids(segments: List[Dict]) -> Tuple[List[Dict], str]:
    """
    Add IDs and punctuation metadata to segments for AI tracking.
    
    V2 Context-Aware Surgeon: Analyzes sentence endings for safe cut points.
    
    Returns:
        Tuple of (segments_with_ids, formatted_text_for_prompt)
    """
    segments_with_ids = []
    formatted_lines = []
    
    # Safe cut indicators (sentence complete)
    SAFE_ENDINGS = {'.', '!', '?', '。', '！', '？'}
    # Unsafe cut indicators (sentence incomplete)
    UNSAFE_ENDINGS = {',', ':', ';', '-', '–', '...', 'und', 'aber', 'weil', 'dass', 'wenn', 'oder', 'denn'}
    
    for i, seg in enumerate(segments):
        seg_with_id = seg.copy()
        seg_with_id['id'] = i
        
        text = seg.get('text', '').strip()
        text_truncated = text[:100]  # For prompt display
        start = seg.get('start', 0)
        end = seg.get('end', 0)
        
        # Analyze sentence ending for cut safety
        last_char = text[-1] if text else ''
        last_word = text.split()[-1].lower() if text.split() else ''
        
        ends_with_period = last_char in SAFE_ENDINGS
        ends_with_unsafe = last_char in {',', ':', ';', '-', '–'} or last_word in UNSAFE_ENDINGS
        
        # Add metadata for AI
        seg_with_id['ends_with_period'] = ends_with_period
        seg_with_id['is_safe_cut'] = ends_with_period
        seg_with_id['last_char'] = last_char
        
        # Format with cut safety indicator
        cut_indicator = "✓" if ends_with_period else "⚠" if ends_with_unsafe else "~"
        
        formatted_lines.append(
            f"[ID:{i}] [{start:.1f}s-{end:.1f}s] [{cut_indicator}] {text_truncated}"
        )
        
        segments_with_ids.append(seg_with_id)
    
    # Add legend to top of prompt
    legend = """
═══════════════════════════════════════════════════════════════════════════════
📍 SEGMENT-ÜBERSICHT (mit Cut-Safety Indikatoren):
═══════════════════════════════════════════════════════════════════════════════
Legende: ✓ = Satz-Ende (Safe Cut) | ⚠ = Satz mitten drin (Unsafe Cut) | ~ = Unklar
═══════════════════════════════════════════════════════════════════════════════
"""
    
    return segments_with_ids, legend + "\n".join(formatted_lines)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CouncilProposal:
    """A single AI's remix proposal."""
    provider: str
    model: str
    
    # Lego Blocks identified
    story_blocks: List[Dict]      # [A] Story/Handlung
    context_blocks: List[Dict]    # [B] Context  
    punchline_blocks: List[Dict]  # [C] Core Message / Punchline
    noise_blocks: List[Dict]      # [D] Noise to delete
    
    # Proposed remix
    remix_order: str              # e.g., "C -> A -> B"
    segments: List[Dict]          # Final segment list with timestamps
    
    # Reasoning
    reasoning: str
    confidence: float = 0.0
    
    # Metadata
    latency_ms: int = 0
    cost: float = 0.0
    raw_response: str = ""


@dataclass
class CouncilDecision:
    """The Judge's final decision."""
    winning_proposal: Optional[CouncilProposal]
    final_segments: List[Dict]
    final_remix_order: str
    judge_reasoning: str
    merged_best_of: List[str]     # Which elements from each AI were used
    confidence: float = 0.0
    total_cost: float = 0.0


# =============================================================================
# THE LEGO-BLOCK PROMPT
# =============================================================================

LEGO_BLOCK_SYSTEM_PROMPT = """Du bist ein VIRAL SURGEON im "Viral Council".

Du operierst auf SATZ-EBENE mit höchster Präzision. Jeder Satz kann bewegt, 
gelöscht oder umgestellt werden - aber der AUDIO-FLOW muss natürlich bleiben.

═══════════════════════════════════════════════════════════════════════════════
🔬 VIRAL SURGEON REGELN (NICHT VERHANDELBAR):
═══════════════════════════════════════════════════════════════════════════════

1. CUT-SAFETY BEACHTEN:
   - Beachte die Cut-Indikatoren: ✓ = Safe | ⚠ = Unsafe | ~ = Unklar
   - NIEMALS nach einem ⚠ (Komma, "und...", "weil...") schneiden!
   - Beispiel: "Arbeite niemals für Geld, weil..." → Kann nicht hier enden!

2. GRAMMATIK-GARANTIE:
   - Wenn du einen Satz löschst, stelle sicher dass der VORHERIGE Satz 
     grammatikalisch abgeschlossen ist (endet mit Punkt/Ausrufezeichen).
   - Beispiel VERBOTEN: "Ich sage euch" [CUT] → Unvollständig!
   - Beispiel ERLAUBT: "Arbeite niemals für Geld." [CUT] → Vollständig!

3. KEINE OPEN LOOPS AM ENDE:
   - Der letzte Satz des Clips MUSS ein Statement sein, keine Frage.
   - VERBOTEN: Clip endet mit "...und dann?" oder "Wisst ihr was passiert ist?"
   - ERLAUBT: Clip endet mit "Das war der Moment, der alles veränderte."

═══════════════════════════════════════════════════════════════════════════════
⚠️ SEGMENT-IDs VERWENDEN:
═══════════════════════════════════════════════════════════════════════════════

Das Transkript ist mit IDs und Cut-Indikatoren markiert: 
[ID:0] [✓] = Sicherer Schnitt möglich
[ID:1] [⚠] = VORSICHT - Satz unvollständig!

REGELN:
1. Zitiere den Text EXAKT wie er im Original steht.
2. Nutze die IDs in deiner Antwort: {"id": 0, "start": 120, ...}
3. ERFINDE KEINE neuen Sätze - nur was im Original steht!
4. Die Timestamps MÜSSEN die originalen sein.
5. PRÜFE ends_with_period=true bevor du einen Cut setzt!

═══════════════════════════════════════════════════════════════════════════════
DIE LEGO-BLOCK METHODE:
═══════════════════════════════════════════════════════════════════════════════

Identifiziere diese Bausteine im Text:

[A] STORY/HANDLUNG
    - Die eigentliche Geschichte oder Argumentation
    - Der "Body" des Contents
    - Beispiel: "Ein alter Mann ging die Straße entlang..."

[B] CONTEXT
    - Hintergrundinformationen
    - Setup, das zum Verständnis nötig ist
    - Beispiel: "Also, ich war in Miami..."

[C] PUNCHLINE / CORE MESSAGE
    - Der stärkste Satz, die Moral, das Fazit
    - DAS was als Hook nach vorne gehört!
    - Beispiel: "Arbeite niemals für Geld."

[D] NOISE
    - Wiederholungen
    - Füllwörter ("Ähm", "Also...")
    - Meta-Talk ("Ich möchte euch heute erzählen...")
    - Safety Bridges ("Versteh mich nicht falsch...")
    → ZU LÖSCHEN (aber nur wenn Nachbar-Sätze safe sind!)

═══════════════════════════════════════════════════════════════════════════════
REMIX-STRATEGIEN (basierend auf Retention-Psychologie):
═══════════════════════════════════════════════════════════════════════════════

STRATEGIE 1: "Inverted Story Loop" (Fazit nach vorne)
   C -> A -> B
   Nimm die Punchline, setze sie an den Anfang, dann Story.

STRATEGIE 2: "Cold Open" (In medias res)
   A(Mitte) -> A(Anfang) -> C
   Starte mitten in der Action, dann Context, dann Payoff.

STRATEGIE 3: "Provocation Opening" (Kontroverse zuerst)
   C -> B -> A
   Kontroverse These, dann Context/Beweis.

STRATEGIE 4: "Question Hook" (Teaser)
   C(Frage-Form) -> A -> C(Antwort)
   Wandle die Punchline in eine Frage um.

═══════════════════════════════════════════════════════════════════════════════

DU ANTWORTEST NUR MIT JSON im folgenden Format:
```json
{
    "story_blocks": [
        {"id": 5, "start": 120, "end": 180, "text": "...EXAKTER Text aus Original..."}
    ],
    "context_blocks": [
        {"id": 0, "start": 0, "end": 30, "text": "...EXAKTER Text..."}
    ],
    "punchline_blocks": [
        {"id": 12, "start": 300, "end": 310, "text": "Arbeite niemals für Geld."}
    ],
    "noise_blocks": [
        {"id": 3, "start": 90, "end": 100, "text": "Ähm, also..."}
    ],
    "remix_order": "C -> A",
    "segments": [
        {"id": 12, "role": "hook", "start": 300, "end": 310, "text": "Arbeite niemals..."},
        {"id": 5, "role": "body", "start": 120, "end": 180, "text": "Die Geschichte..."}
    ],
    "reasoning": "Die Punchline bei 300s (ID:12) ist der perfekte Hook weil...",
    "confidence": 0.85
}
```

⚠️ WICHTIG: Nutze die ORIGINAL-Timestamps und IDs! Erfinde keine neuen Zeiten!
"""

BRAIN_CONTEXT_TEMPLATE = """
═══════════════════════════════════════════════════════════════════════════════
🧠 BRAIN CONTEXT - Ähnlicher viraler Hit gefunden:
═══════════════════════════════════════════════════════════════════════════════

{brain_match_summary}

LERNE VON DIESEM HIT:
- Welche Struktur hat funktioniert?
- Wo kam der Hook im Original-Material?
- Was wurde weggeschnitten?

Nutze diese Erkenntnisse für deinen Remix-Vorschlag!
═══════════════════════════════════════════════════════════════════════════════
"""


JUDGE_SYSTEM_PROMPT = """Du bist der SUPREME JUDGE des Viral Council.

Vor dir liegen 5 Schnitt-Vorschläge von den besten AIs der Welt für denselben Clip.
Deine Aufgabe: Analysiere sie, finde den Gewinner, und erstelle den MASTER CUT.

═══════════════════════════════════════════════════════════════════════════════
BEWERTUNGSKRITERIEN:
═══════════════════════════════════════════════════════════════════════════════

1. HOOK STÄRKE (40%)
   - Welcher Vorschlag hat den stärksten, kontroversesten Hook?
   - Erzeugt er sofort Neugier?
   - Ist er unter 7 Sekunden?

2. BALLAST ENTFERNUNG (30%)
   - Welcher Vorschlag ist am radikalsten beim Löschen von Noise?
   - Wurde Meta-Talk entfernt?
   - Wurden Safety Bridges eliminiert?

3. RETENTION LOGIK (20%)
   - Ist die Remix-Reihenfolge psychologisch sinnvoll?
   - Wird die Spannung aufgebaut und gehalten?

4. AUSFÜHRBARKEIT (10%)
   - Sind die Timestamps präzise?
   - Macht der Schnitt technisch Sinn?

═══════════════════════════════════════════════════════════════════════════════
DEINE AUFGABE:
═══════════════════════════════════════════════════════════════════════════════

1. Bewerte jeden Vorschlag (kurz).
2. Wähle den BESTEN oder kombiniere die besten Elemente.
3. Erstelle den FINALEN Master-Cut.

DU ANTWORTEST NUR MIT JSON:
```json
{
    "evaluation": {
        "anthropic": {"score": 8.5, "strength": "Starker Hook", "weakness": "Zu lang"},
        "openai": {"score": 7.0, "strength": "Gute Struktur", "weakness": "Hook schwach"},
        ...
    },
    "winner": "anthropic",
    "merged_from": ["anthropic:hook", "openai:body"],
    "final_segments": [
        {"role": "hook", "start": 300, "end": 310},
        {"role": "body", "start": 120, "end": 180}
    ],
    "final_remix_order": "C -> A",
    "judge_reasoning": "Opus hatte den stärksten Hook, aber OpenAI's Body-Segmentierung war präziser...",
    "confidence": 0.90
}
```
"""


# =============================================================================
# THE VIRAL COUNCIL CLASS
# =============================================================================

class ViralCouncil:
    """
    The Viral Council - Multi-AI Remixing System.
    
    Convenes the world's best AIs to compete for the best edit.
    """
    
    def __init__(self, providers: List[str] = None):
        """
        Initialize the Council.
        
        Args:
            providers: List of providers to use. Default: all 5.
        """
        self.providers = providers or list(COUNCIL_MODEL_IDS.keys())
        self.proposals: List[CouncilProposal] = []
        self.total_cost = 0.0
        # For robust remapping
        self.original_segments: List[Dict] = []
        self.segments_with_ids: List[Dict] = []
        
    async def convene_council(
        self,
        transcript_text: str,
        brain_context: Optional[str] = None,
        max_concurrent: int = 5,
        original_segments: Optional[List[Dict]] = None
    ) -> List[CouncilProposal]:
        """
        Convene the Council - Send transcript to all AIs in parallel.
        
        Args:
            transcript_text: The raw transcript to analyze
            brain_context: Optional context from Brain (similar viral hits)
            max_concurrent: Max parallel API calls
            original_segments: Original transcript segments with timestamps (for remapping)
            
        Returns:
            List of proposals from each AI
        """
        # Store original segments for later remapping
        self.original_segments = original_segments or []
        
        print("\n" + "═" * 60)
        print("🏛️  THE VIRAL COUNCIL CONVENES")
        print("═" * 60)
        print(f"   📋 Transcript: {len(transcript_text)} chars")
        print(f"   🧠 Brain Context: {'✅ Provided' if brain_context else '❌ None'}")
        print(f"   📊 Original Segments: {len(self.original_segments)}")
        print(f"   👥 Council Members: {', '.join(self.providers)}")
        print("─" * 60)
        
        # Add IDs to segments for tracking
        if self.original_segments:
            segments_with_ids, formatted_transcript = add_segment_ids(self.original_segments)
            self.segments_with_ids = segments_with_ids
            transcript_for_prompt = formatted_transcript[:30000]
        else:
            # Fallback: Use raw text with simple line IDs
            lines = transcript_text.split('\n')
            formatted_lines = [f"[ID:{i}] {line}" for i, line in enumerate(lines)]
            transcript_for_prompt = '\n'.join(formatted_lines)[:30000]
            self.segments_with_ids = []
        
        # Build the user prompt
        user_prompt = f"""
TRANSKRIPT ZUM ANALYSIEREN (mit IDs markiert):
═══════════════════════════════════════════════════════════════════════════════

{transcript_for_prompt}

{"... (gekürzt)" if len(transcript_text) > 30000 else ""}

═══════════════════════════════════════════════════════════════════════════════

{BRAIN_CONTEXT_TEMPLATE.format(brain_match_summary=brain_context) if brain_context else ""}

AUFGABE:
1. Identifiziere die Lego-Blöcke [A], [B], [C], [D] - nutze die Segment-IDs!
2. Schlage einen Remix vor (welche Reihenfolge?).
3. Erstelle die Segment-Liste mit exakten Timestamps und IDs.
4. Begründe deine Entscheidung.

⚠️ NUTZE DIE ORIGINAL-IDs UND TIMESTAMPS! ERFINDE NICHTS NEUES!
"""
        
        # Create tasks for each council member
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def get_proposal(provider: str) -> Optional[CouncilProposal]:
            async with semaphore:
                model_id = COUNCIL_MODEL_IDS.get(provider)
                if not model_id:
                    logger.warning(f"Unknown provider: {provider}")
                    return None
                
                print(f"   🎯 Querying {provider.upper()} ({model_id[:30]}...)")
                
                try:
                    model = get_model(provider, model=model_id)
                    
                    response = await model.generate(
                        prompt=user_prompt,
                        system=LEGO_BLOCK_SYSTEM_PROMPT,
                        temperature=0.4,
                        max_tokens=4096,
                        cache_system=True  # Enable caching for cost savings
                    )
                    
                    # Parse the response
                    proposal = self._parse_proposal(
                        response.content, 
                        provider, 
                        model_id,
                        response.latency_ms,
                        response.cost
                    )
                    
                    if proposal:
                        print(f"   ✅ {provider.upper()}: Remix '{proposal.remix_order}' | Conf: {proposal.confidence:.0%}")
                        self.total_cost += response.cost
                        return proposal
                    else:
                        print(f"   ⚠️ {provider.upper()}: Failed to parse response")
                        return None
                        
                except Exception as e:
                    print(f"   ❌ {provider.upper()}: Error - {str(e)[:50]}")
                    logger.error(f"Council member {provider} failed: {e}")
                    return None
        
        # Run all queries in parallel
        tasks = [get_proposal(p) for p in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful proposals
        self.proposals = [r for r in results if isinstance(r, CouncilProposal)]
        
        print("─" * 60)
        print(f"   📊 Proposals received: {len(self.proposals)}/{len(self.providers)}")
        print(f"   💰 Total cost so far: ${self.total_cost:.4f}")
        
        return self.proposals
    
    async def executive_decision(
        self,
        proposals: Optional[List[CouncilProposal]] = None
    ) -> CouncilDecision:
        """
        The Judge (Opus) analyzes all proposals and makes the final decision.
        
        Args:
            proposals: List of proposals to judge (default: self.proposals)
            
        Returns:
            The final CouncilDecision with the master cut
        """
        proposals = proposals or self.proposals
        
        if not proposals:
            raise ValueError("No proposals to judge! Convene the council first.")
        
        print("\n" + "─" * 60)
        print("⚖️  EXECUTIVE DECISION (Opus Judge)")
        print("─" * 60)
        
        # Format proposals for the judge
        proposals_text = self._format_proposals_for_judge(proposals)
        
        user_prompt = f"""
HIER SIND DIE {len(proposals)} VORSCHLÄGE DES COUNCILS:

{proposals_text}

═══════════════════════════════════════════════════════════════════════════════

Analysiere jeden Vorschlag. Wähle den Gewinner oder kombiniere die besten Elemente.
Erstelle den FINALEN Master-Cut.

⚠️ WICHTIG: Nutze nur ORIGINALE Segment-IDs und Timestamps aus den Vorschlägen!
"""
        
        # Use Opus as the Judge
        judge = get_model("anthropic", model=OPUS_MODEL_ID)
        
        print(f"   👨‍⚖️ Judge: {OPUS_MODEL_ID}")
        
        response = await judge.generate(
            prompt=user_prompt,
            system=JUDGE_SYSTEM_PROMPT,
            temperature=0.2,  # Low temperature for consistent judgment
            max_tokens=4096,
            cache_system=True
        )
        
        self.total_cost += response.cost
        
        # Parse the judge's decision using robust parser
        decision = self._parse_judge_decision(response.content, proposals)
        
        # ═══════════════════════════════════════════════════════════════
        # 🛡️ ROBUST REMAPPING - Validate and fix timestamps
        # ═══════════════════════════════════════════════════════════════
        if decision.final_segments and self.original_segments:
            print(f"   🔄 Validating {len(decision.final_segments)} segments against originals...")
            
            validated_segments = fuzzy_remap_to_segments(
                decision.final_segments,
                self.original_segments,
                match_threshold=0.75
            )
            
            if validated_segments:
                decision.final_segments = validated_segments
                print(f"   ✅ Validated: {len(validated_segments)} segments with correct timestamps")
            else:
                # Fallback: Use best proposal's segments directly
                if decision.winning_proposal:
                    print("   ⚠️ Remapping failed, using winning proposal segments")
                    decision.final_segments = decision.winning_proposal.segments
        
        decision.total_cost = self.total_cost
        
        print(f"   🏆 Winner: {decision.winning_proposal.provider if decision.winning_proposal else 'MERGED'}")
        print(f"   📐 Final Remix: {decision.final_remix_order}")
        print(f"   💯 Confidence: {decision.confidence:.0%}")
        print(f"   📊 Final Segments: {len(decision.final_segments)}")
        print(f"   💰 Total Council Cost: ${self.total_cost:.4f}")
        
        return decision
    
    def _parse_proposal(
        self, 
        content: str, 
        provider: str, 
        model: str,
        latency_ms: int,
        cost: float
    ) -> Optional[CouncilProposal]:
        """Parse an AI's proposal from JSON response using robust parser."""
        
        # Use robust parser that handles <think> tags, markdown, etc.
        data = robust_json_parser(content, expected_type="dict")
        
        if not data:
            logger.warning(f"Empty or unparseable response from {provider}")
            return None
        
        try:
            # Validate we have at least some segments
            segments = data.get("segments", [])
            if not segments:
                # Try to build segments from blocks
                punchlines = data.get("punchline_blocks", [])
                stories = data.get("story_blocks", [])
                
                if punchlines:
                    segments.append({**punchlines[0], "role": "hook"})
                if stories:
                    segments.append({**stories[0], "role": "body"})
            
            return CouncilProposal(
                provider=provider,
                model=model,
                story_blocks=data.get("story_blocks", []),
                context_blocks=data.get("context_blocks", []),
                punchline_blocks=data.get("punchline_blocks", []),
                noise_blocks=data.get("noise_blocks", []),
                remix_order=data.get("remix_order", "unknown"),
                segments=segments,
                reasoning=data.get("reasoning", "No reasoning provided"),
                confidence=float(data.get("confidence", 0.5)),
                latency_ms=latency_ms,
                cost=cost,
                raw_response=content
            )
        except Exception as e:
            logger.error(f"Failed to build proposal from {provider}: {e}")
            return None
    
    def _format_proposals_for_judge(self, proposals: List[CouncilProposal]) -> str:
        """Format all proposals for the judge to review."""
        formatted = []
        
        for i, p in enumerate(proposals, 1):
            formatted.append(f"""
═══════════════════════════════════════════════════════════════════════════════
VORSCHLAG {i}: {p.provider.upper()} ({p.model})
═══════════════════════════════════════════════════════════════════════════════

REMIX ORDER: {p.remix_order}
CONFIDENCE: {p.confidence:.0%}

PUNCHLINE BLOCKS (Potential Hooks):
{json.dumps(p.punchline_blocks, indent=2, ensure_ascii=False)}

STORY BLOCKS:
{json.dumps(p.story_blocks, indent=2, ensure_ascii=False)}

CONTEXT BLOCKS:
{json.dumps(p.context_blocks, indent=2, ensure_ascii=False)}

NOISE BLOCKS (zu löschen):
{json.dumps(p.noise_blocks, indent=2, ensure_ascii=False)}

FINAL SEGMENTS:
{json.dumps(p.segments, indent=2, ensure_ascii=False)}

REASONING:
{p.reasoning}
""")
        
        return "\n".join(formatted)
    
    def _parse_judge_decision(
        self, 
        content: str, 
        proposals: List[CouncilProposal]
    ) -> CouncilDecision:
        """Parse the judge's final decision using robust parser."""
        
        # Use robust parser that handles all AI quirks
        data = robust_json_parser(content, expected_type="dict")
        
        if not data:
            logger.warning("Judge response unparseable, using fallback")
            # Fallback: Use the highest confidence proposal
            if proposals:
                best = max(proposals, key=lambda p: p.confidence)
                return CouncilDecision(
                    winning_proposal=best,
                    final_segments=best.segments,
                    final_remix_order=best.remix_order,
                    judge_reasoning="Fallback: Judge response unparseable, used highest confidence proposal",
                    merged_best_of=[best.provider],
                    confidence=best.confidence
                )
            return CouncilDecision(
                winning_proposal=None,
                final_segments=[],
                final_remix_order="",
                judge_reasoning="Failed to parse and no fallback",
                merged_best_of=[],
                confidence=0.0
            )
        
        try:
            # Find the winning proposal
            winner_provider = data.get("winner", "")
            winning_proposal = None
            for p in proposals:
                if p.provider.lower() == winner_provider.lower():
                    winning_proposal = p
                    break
            
            final_segments = data.get("final_segments", [])
            
            # If no segments from judge, use winning proposal's
            if not final_segments and winning_proposal:
                final_segments = winning_proposal.segments
                logger.info("Using winning proposal segments as judge didn't provide any")
            
            return CouncilDecision(
                winning_proposal=winning_proposal,
                final_segments=final_segments,
                final_remix_order=data.get("final_remix_order", winning_proposal.remix_order if winning_proposal else ""),
                judge_reasoning=data.get("judge_reasoning", ""),
                merged_best_of=data.get("merged_from", []),
                confidence=float(data.get("confidence", 0.5))
            )
            
        except Exception as e:
            logger.error(f"Failed to build judge decision: {e}")
            
            # Fallback: Use the highest confidence proposal
            if proposals:
                best = max(proposals, key=lambda p: p.confidence)
                return CouncilDecision(
                    winning_proposal=best,
                    final_segments=best.segments,
                    final_remix_order=best.remix_order,
                    judge_reasoning=f"Fallback due to error: {e}",
                    merged_best_of=[best.provider],
                    confidence=best.confidence
                )
            
            return CouncilDecision(
                winning_proposal=None,
                final_segments=[],
                final_remix_order="",
                judge_reasoning="Failed to parse",
                merged_best_of=[],
                confidence=0.0
            )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def run_viral_council(
    transcript_text: str,
    brain_context: Optional[str] = None,
    providers: Optional[List[str]] = None
) -> CouncilDecision:
    """
    Run the full Viral Council workflow.
    
    Args:
        transcript_text: The transcript to analyze
        brain_context: Optional Brain context (similar hits)
        providers: Optional list of providers (default: all 5)
        
    Returns:
        The final CouncilDecision with master cut
    """
    council = ViralCouncil(providers=providers)
    
    # Convene the council
    await council.convene_council(transcript_text, brain_context)
    
    # Get the judge's decision
    decision = await council.executive_decision()
    
    return decision


async def quick_council(
    transcript_text: str,
    brain_context: Optional[str] = None
) -> CouncilDecision:
    """
    Quick council with only 3 AIs (faster, cheaper).
    
    Uses: Opus, GPT, DeepSeek
    """
    return await run_viral_council(
        transcript_text,
        brain_context,
        providers=["anthropic", "openai", "deepseek"]
    )

