"""
Type definitions for AI Boundary Engine.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Decision(str, Enum):
    """Decision types for query analysis."""
    ANSWER = "ANSWER"
    REFUSE = "REFUSE"
    CLARIFY = "CLARIFY"


class RiskTag(str, Enum):
    """Risk categories for queries."""
    ILLEGAL = "illegal"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    MEDICAL = "medical"
    LEGAL = "legal"
    PERSONAL_DATA = "personal_data"
    AMBIGUOUS = "ambiguous"
    SAFE = "safe"


class NormalizedQuery(BaseModel):
    """Normalized query representation."""
    text: str = Field(description="Normalized query text")
    original: str = Field(description="Original query text")
    length: int = Field(description="Character length")
    tokens: int = Field(description="Token count (word-based)")


class RuleMatch(BaseModel):
    """Result of rule matching."""
    rule_name: str = Field(description="Name of matched rule")
    decision: Decision = Field(description="Suggested decision")
    confidence: float = Field(ge=0.0, le=1.0, description="Match confidence")
    reason: str = Field(description="Human-readable reason")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords that matched")


class IntentScore(BaseModel):
    """Intent similarity score."""
    intent: str = Field(description="Intent category name")
    similarity: float = Field(description="Cosine similarity score (typically 0.0-1.0)")
    description: str = Field(description="Intent description")


class AmbiguityResult(BaseModel):
    """Ambiguity analysis result."""
    is_ambiguous: bool = Field(description="Whether query is ambiguous")
    score: float = Field(ge=0.0, le=1.0, description="Ambiguity score")
    reasons: List[str] = Field(default_factory=list, description="Reasons for ambiguity")


class DecisionResult(BaseModel):
    """Final decision result from boundary engine."""
    decision: Decision = Field(description="Final decision")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence")
    reasons: List[str] = Field(description="List of reasons for decision")
    risk_tags: List[RiskTag] = Field(default_factory=list, description="Applicable risk tags")
    
    # Detailed breakdowns (optional)
    rule_matches: List[RuleMatch] = Field(default_factory=list, description="Matched rules")
    intent_scores: List[IntentScore] = Field(default_factory=list, description="Intent scores")
    ambiguity: Optional[AmbiguityResult] = Field(None, description="Ambiguity analysis")
    
    query: str = Field(description="Original query analyzed")

    class Config:
        use_enum_values = True


class Rule(BaseModel):
    """Safety rule definition."""
    name: str = Field(description="Unique rule name")
    keywords: List[str] = Field(description="Keywords to match")
    patterns: List[str] = Field(default_factory=list, description="Regex patterns to match")
    decision: Decision = Field(description="Decision if rule matches")
    severity: float = Field(ge=0.0, le=1.0, description="Rule severity/confidence")
    reason: str = Field(description="Human-readable reason for decision")
    tags: List[RiskTag] = Field(default_factory=list, description="Associated risk tags")
    enabled: bool = Field(default=True, description="Whether rule is active")


class EngineConfig(BaseModel):
    """Configuration for boundary engine."""
    
    # Rule engine settings
    rules_enabled: bool = Field(default=True, description="Enable rule engine")
    rule_sensitivity: str = Field(default="high", description="Rule sensitivity: low, medium, high")
    
    # Embedding settings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")
    similarity_threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Intent similarity threshold")
    
    # Ambiguity settings
    min_query_length: int = Field(default=5, description="Minimum query length for analysis")
    vague_verb_penalty: float = Field(default=0.2, ge=0.0, le=1.0, description="Penalty for vague verbs")
    
    # Decision settings
    refuse_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence threshold for REFUSE")
    clarify_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Confidence threshold for CLARIFY")
