"""
Pydantic Response Schemas for Structured AI Outputs

All AI responses must use these models for guaranteed schema compliance.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


# ============================================================================
# DISCOVER Stage Schemas
# ============================================================================

class Timestamp(BaseModel):
    """Timestamp range in a video."""
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")


class DiscoveredMoment(BaseModel):
    """A potential viral moment discovered in the transcript."""
    timestamps: Timestamp
    hook_text: str = Field(description="The exact text that could be the hook (first 3 seconds)")
    topic: str = Field(description="Main topic/theme of this moment")
    content_type: Literal["story", "insight", "tutorial", "emotional", "paradox", "beliefbreaker"] = Field(
        description="Type of content"
    )
    hook_strength: int = Field(ge=1, le=10, description="Hook quality score 1-10")
    viral_potential: int = Field(ge=1, le=10, description="Predicted viral potential 1-10")
    reasoning: str = Field(description="Why this moment has viral potential")
    pattern_match: Optional[str] = Field(
        default=None, 
        description="Matching pattern from PRINCIPLES (e.g., 'paradox_statement', 'authority_curiosity')"
    )


class DiscoverResponse(BaseModel):
    """Response from DISCOVER stage."""
    moments: List[DiscoveredMoment] = Field(max_length=30)
    total_duration_analyzed: float = Field(description="Total video duration in seconds")
    ai_provider: str = Field(description="Which AI generated this response")


# ============================================================================
# COMPOSE Stage Schemas
# ============================================================================

class SegmentEdit(BaseModel):
    """A segment edit instruction for the clip."""
    original_start: float = Field(description="Original start time in source video")
    original_end: float = Field(description="Original end time in source video")
    new_position: float = Field(description="New position in the composed clip timeline")
    text: str = Field(description="The text content of this segment")
    is_hook: bool = Field(default=False, description="Is this segment the hook?")


class ComposedClip(BaseModel):
    """A fully composed clip ready for validation."""
    clip_id: str = Field(description="Unique identifier for this clip")
    source_moment: Timestamp = Field(description="Original moment timestamps")
    
    # Structure
    structure_type: Literal["clean_extraction", "hook_extraction", "cross_moment"] = Field(
        description="How the clip was composed"
    )
    segments: List[SegmentEdit] = Field(description="Ordered list of segments")
    
    # Hook
    hook_text: str = Field(description="The hook text (first 3 seconds)")
    hook_origin: Literal["native", "extracted", "cross_moment"] = Field(
        description="Where the hook came from"
    )
    
    # Metadata
    total_duration: float = Field(ge=15, le=600, description="Total clip duration in seconds")
    caption_suggestion: str = Field(description="Suggested caption for the clip")
    reasoning: str = Field(description="Why this composition was chosen")


class ComposeResponse(BaseModel):
    """Response from COMPOSE stage."""
    clips: List[ComposedClip] = Field(max_length=20)
    debate_rounds: int = Field(description="Number of debate rounds completed")
    ai_consensus: float = Field(ge=0, le=1, description="Consensus level 0-1")


# ============================================================================
# VALIDATE Stage Schemas
# ============================================================================

class ScoreBreakdown(BaseModel):
    """Detailed score breakdown."""
    hook_quality: int = Field(ge=0, le=10, description="Hook quality score")
    content_engagement: int = Field(ge=0, le=10, description="Content engagement score")
    pacing: int = Field(ge=0, le=10, description="Pacing and flow score")
    emotional_impact: int = Field(ge=0, le=10, description="Emotional resonance score")
    shareability: int = Field(ge=0, le=10, description="Likelihood of sharing score")


class ValidationResult(BaseModel):
    """Validation result for a single clip."""
    clip_id: str
    overall_score: int = Field(ge=0, le=50, description="Total score (sum of breakdown)")
    breakdown: ScoreBreakdown
    verdict: Literal["approve", "refine", "reject"] = Field(
        description="Final verdict"
    )
    predicted_performance: Literal["viral", "good", "average", "weak"] = Field(
        description="Predicted performance level"
    )
    improvement_suggestions: List[str] = Field(
        max_length=5,
        description="Specific improvements if verdict is 'refine'"
    )
    assessment: str = Field(description="Detailed assessment explanation")


class ValidateResponse(BaseModel):
    """Response from VALIDATE stage."""
    results: List[ValidationResult]
    clips_approved: int
    clips_to_refine: int
    clips_rejected: int


# ============================================================================
# GODMODE Stage Schemas
# ============================================================================

class GodmodeVerdict(str, Enum):
    VIRAL = "viral"
    STRONG = "strong"
    GOOD = "good"
    WEAK = "weak"
    REJECT = "reject"


class GodmodeResult(BaseModel):
    """Godmode evaluation result."""
    clip_id: str
    verdict: GodmodeVerdict
    score: int = Field(ge=0, le=50, description="Final Godmode score")
    rank: int = Field(ge=1, description="Rank among all clips")
    reasoning: str = Field(description="Detailed Godmode reasoning")
    final_hook: str = Field(description="Confirmed or refined hook")
    export_ready: bool = Field(description="Ready for export without changes")


class GodmodeResponse(BaseModel):
    """Response from GODMODE evaluation."""
    results: List[GodmodeResult]
    total_clips: int
    export_ready_count: int
    top_performer: Optional[str] = Field(description="Clip ID of best performer")


# ============================================================================
# Consensus Building Schema
# ============================================================================

class AIVote(BaseModel):
    """A single AI's vote on a moment/clip."""
    provider: str
    supports: bool
    confidence: float = Field(ge=0, le=1)
    reasoning: str


class ConsensusResult(BaseModel):
    """Result of multi-AI consensus."""
    item_id: str
    votes: List[AIVote]
    consensus_reached: bool
    support_ratio: float = Field(ge=0, le=1, description="Ratio of AIs that support")
    final_decision: bool
    merged_reasoning: str


