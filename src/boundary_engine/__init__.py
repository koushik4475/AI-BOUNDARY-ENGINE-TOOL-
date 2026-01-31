"""
AI Boundary Engine - AI safety layer for query analysis.
"""

__version__ = "0.1.0"

from .engine import BoundaryEngine
from .types import (
    Decision,
    DecisionResult,
    Rule,
    RiskTag,
    EngineConfig,
)

__all__ = [
    "BoundaryEngine",
    "Decision",
    "DecisionResult",
    "Rule",
    "RiskTag",
    "EngineConfig",
]
