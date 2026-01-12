"""
VIRAL BRAIN PROMPT GENERATOR - Fusion Engine

Combines two learning sources into one actionable AI instruction:
- Source A (Strategy): data/learned_patterns.json (967+ viral clips analysis)
- Source B (Tactics): data/editing_patterns.json (Longform → Clip deep-dive)

The generated prompt teaches the AI both WHAT to aim for (archetypes)
and HOW to execute (micro-editing rules).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# Paths
# =============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
LEARNED_PATTERNS_FILE = DATA_DIR / "learned_patterns.json"
EDITING_PATTERNS_FILE = DATA_DIR / "editing_patterns.json"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ArchetypeInfo:
    """Extracted archetype information."""
    name: str
    description: str
    structure: List[str]
    hook_location: str


@dataclass
class EditingRule:
    """A micro-editing rule from pair analysis."""
    rule: str
    occurrences: int


@dataclass
class FewShotExample:
    """A before/after example for few-shot learning."""
    pair_id: str
    pattern_type: str
    source_excerpt: str
    result_excerpt: str
    reasoning: str
    rules_applied: List[str]


# =============================================================================
# Viral Brain Prompt Generator
# =============================================================================

class ViralBrainPrompt:
    """
    Fusion Engine: Combines strategic insights (900+ clips) with
    tactical execution rules (pair deep-dives) into one prompt.
    """
    
    def __init__(self):
        self.learned_patterns: Dict = {}
        self.editing_patterns: Dict = {}
        self.archetypes: List[ArchetypeInfo] = []
        self.top_rules: List[EditingRule] = []
        self.examples: List[FewShotExample] = []
        
        self._load_sources()
    
    def _load_sources(self):
        """Load both JSON sources with graceful error handling."""
        
        # Source A: Strategic Patterns (967+ clips)
        if LEARNED_PATTERNS_FILE.exists():
            try:
                with open(LEARNED_PATTERNS_FILE, 'r', encoding='utf-8') as f:
                    self.learned_patterns = json.load(f)
                self._extract_archetypes()
                logger.info(f"✅ Loaded learned_patterns.json: {len(self.archetypes)} archetypes")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load learned_patterns.json: {e}")
        else:
            logger.warning(f"⚠️ learned_patterns.json not found at {LEARNED_PATTERNS_FILE}")
        
        # Source B: Tactical Editing Rules (pairs)
        if EDITING_PATTERNS_FILE.exists():
            try:
                with open(EDITING_PATTERNS_FILE, 'r', encoding='utf-8') as f:
                    self.editing_patterns = json.load(f)
                self._extract_rules()
                self._extract_examples()
                logger.info(f"✅ Loaded editing_patterns.json: {len(self.top_rules)} rules, {len(self.examples)} examples")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load editing_patterns.json: {e}")
        else:
            logger.warning(f"⚠️ editing_patterns.json not found at {EDITING_PATTERNS_FILE}")
    
    def _extract_archetypes(self):
        """Extract archetype definitions from learned_patterns.json."""
        archetypes_data = self.learned_patterns.get("archetype_definitions", {})
        
        for key, data in archetypes_data.items():
            if isinstance(data, dict):
                self.archetypes.append(ArchetypeInfo(
                    name=data.get("name", key),
                    description=data.get("description", ""),
                    structure=data.get("structure", []),
                    hook_location=data.get("hook_location", "start")
                ))
    
    def _extract_rules(self):
        """Extract top editing rules from editing_patterns.json."""
        rules_data = self.editing_patterns.get("top_rules", [])
        
        for rule_entry in rules_data[:10]:  # Top 10
            if isinstance(rule_entry, dict):
                self.top_rules.append(EditingRule(
                    rule=rule_entry.get("rule", ""),
                    occurrences=rule_entry.get("occurrences", 1)
                ))
            elif isinstance(rule_entry, str):
                self.top_rules.append(EditingRule(rule=rule_entry, occurrences=1))
    
    def _extract_examples(self):
        """Extract few-shot examples from editing_patterns.json."""
        patterns_data = self.editing_patterns.get("patterns", [])
        
        for pattern in patterns_data:
            if isinstance(pattern, dict):
                self.examples.append(FewShotExample(
                    pair_id=pattern.get("pair_id", "unknown"),
                    pattern_type=pattern.get("pattern_type", "unknown"),
                    source_excerpt=pattern.get("source_text", "")[:500],
                    result_excerpt=pattern.get("result_text", "")[:500],
                    reasoning=pattern.get("ai_reasoning", ""),
                    rules_applied=pattern.get("editing_rules", [])
                ))
    
    def _select_diverse_examples(self, n: int = 3) -> List[FewShotExample]:
        """
        Select diverse examples covering different pattern types.
        Prioritizes variety in editing techniques.
        """
        if not self.examples:
            return []
        
        selected = []
        seen_types = set()
        
        # First pass: one of each pattern type
        for example in self.examples:
            if example.pattern_type not in seen_types:
                selected.append(example)
                seen_types.add(example.pattern_type)
                if len(selected) >= n:
                    break
        
        # Second pass: fill remaining slots
        if len(selected) < n:
            for example in self.examples:
                if example not in selected:
                    selected.append(example)
                    if len(selected) >= n:
                        break
        
        return selected[:n]
    
    def build(self, raw_transcript: str, num_examples: int = 3) -> str:
        """
        Generate the fusion prompt combining strategy + tactics.
        
        Args:
            raw_transcript: The raw transcript to be edited
            num_examples: Number of few-shot examples to include
            
        Returns:
            Complete prompt string for the AI
        """
        sections = []
        
        # =================================================================
        # SECTION 1: Identity & Strategy
        # =================================================================
        strategy_section = self._build_strategy_section()
        sections.append(strategy_section)
        
        # =================================================================
        # SECTION 2: Tactical Execution Rules
        # =================================================================
        tactics_section = self._build_tactics_section()
        sections.append(tactics_section)
        
        # =================================================================
        # SECTION 3: Few-Shot Examples
        # =================================================================
        examples_section = self._build_examples_section(num_examples)
        sections.append(examples_section)
        
        # =================================================================
        # SECTION 4: The Task
        # =================================================================
        task_section = self._build_task_section(raw_transcript)
        sections.append(task_section)
        
        return "\n\n".join(sections)
    
    def _build_strategy_section(self) -> str:
        """Build Section 1: Identity & Strategy."""
        lines = [
            "═" * 70,
            "🧠 IDENTITY & STRATEGY",
            "═" * 70,
            "",
            "You are an ELITE VIRAL EDITOR. Your strategy is based on analyzing",
            f"967+ viral clips that collectively generated billions of views.",
            "",
        ]
        
        if self.archetypes:
            lines.append("TARGET ARCHETYPES (aim for one of these styles):")
            lines.append("")
            
            for i, arch in enumerate(self.archetypes[:5], 1):
                lines.append(f"  {i}. **{arch.name}**")
                lines.append(f"     {arch.description}")
                if arch.structure:
                    lines.append(f"     Structure: {' → '.join(arch.structure)}")
                lines.append("")
        else:
            lines.append("(No archetype data available - using general viral patterns)")
        
        # Add statistics if available
        stats = self.learned_patterns.get("statistics", {})
        if stats:
            lines.append("LEARNED STATISTICS:")
            for key, value in list(stats.items())[:3]:
                lines.append(f"  • {key}: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_tactics_section(self) -> str:
        """Build Section 2: Tactical Execution Rules."""
        lines = [
            "═" * 70,
            "⚡ TACTICAL EXECUTION RULES",
            "═" * 70,
            "",
            "To achieve viral potential, STRICTLY follow these editing rules",
            "derived from analyzing high-performing Longform → Clip transformations:",
            "",
        ]
        
        if self.top_rules:
            for i, rule in enumerate(self.top_rules[:7], 1):
                occurrence_text = f" (seen {rule.occurrences}x)" if rule.occurrences > 1 else ""
                lines.append(f"  {i}. {rule.rule}{occurrence_text}")
            lines.append("")
        else:
            lines.append("  (No tactical rules available - use best judgment)")
            lines.append("")
        
        # Add actionable insights if available
        insights = self.editing_patterns.get("actionable_insights", [])
        if insights:
            lines.append("CRITICAL INSIGHTS:")
            for insight in insights[:2]:
                if isinstance(insight, dict):
                    lines.append(f"  ⚠️ {insight.get('insight', '')}")
                    lines.append(f"     Action: {insight.get('action', '')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_examples_section(self, num_examples: int = 3) -> str:
        """Build Section 3: Few-Shot Examples."""
        lines = [
            "═" * 70,
            "📚 LEARNING FROM EXAMPLES (Few-Shot)",
            "═" * 70,
            "",
            "Here is how raw transcripts are transformed into viral clips:",
            "",
        ]
        
        examples = self._select_diverse_examples(num_examples)
        
        if examples:
            for i, ex in enumerate(examples, 1):
                lines.append(f"─── EXAMPLE {i}: {ex.pattern_type.upper()} ───")
                lines.append("")
                lines.append("RAW (Before):")
                lines.append(f'  "{ex.source_excerpt[:300]}..."')
                lines.append("")
                lines.append("VIRAL OUTPUT (After):")
                lines.append(f'  "{ex.result_excerpt[:300]}..."')
                lines.append("")
                if ex.reasoning:
                    lines.append(f"REASONING: {ex.reasoning[:200]}")
                if ex.rules_applied:
                    lines.append(f"RULES APPLIED: {', '.join(ex.rules_applied[:3])}")
                lines.append("")
        else:
            lines.append("(No examples available - apply general viral editing principles)")
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_task_section(self, raw_transcript: str) -> str:
        """Build Section 4: The Task."""
        # Truncate very long transcripts
        max_transcript_length = 8000
        if len(raw_transcript) > max_transcript_length:
            transcript_display = raw_transcript[:max_transcript_length] + "\n\n[... TRANSCRIPT TRUNCATED ...]"
        else:
            transcript_display = raw_transcript
        
        lines = [
            "═" * 70,
            "🎯 YOUR TASK",
            "═" * 70,
            "",
            "EDIT THE FOLLOWING TRANSCRIPT TO MATCH THE PATTERNS ABOVE.",
            "",
            "BE AGGRESSIVE:",
            "  • Cut all preambles and filler",
            "  • Move the punchline/conclusion to the START if it creates a better hook",
            "  • Compress ruthlessly - keep only the viral core",
            "  • Match one of the target archetypes",
            "",
            "─── RAW TRANSCRIPT ───",
            "",
            transcript_display,
            "",
            "─── END TRANSCRIPT ───",
            "",
            "OUTPUT FORMAT:",
            "```json",
            "{",
            '  "archetype": "paradox_story | contrarian_rant | listicle | insight",',
            '  "hook_text": "The first 1-2 sentences of your edit",',
            '  "edited_transcript": "The complete edited viral version",',
            '  "cuts_made": ["List of specific cuts/changes you made"],',
            '  "reasoning": "Why this edit creates viral potential"',
            "}",
            "```",
        ]
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        """Return statistics about loaded data."""
        return {
            "archetypes_loaded": len(self.archetypes),
            "rules_loaded": len(self.top_rules),
            "examples_loaded": len(self.examples),
            "learned_patterns_available": bool(self.learned_patterns),
            "editing_patterns_available": bool(self.editing_patterns),
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def build_viral_prompt(transcript: str) -> str:
    """Quick function to generate a viral editing prompt."""
    generator = ViralBrainPrompt()
    return generator.build(transcript)


def get_prompt_generator() -> ViralBrainPrompt:
    """Get a reusable prompt generator instance."""
    return ViralBrainPrompt()

