"""
Main boundary engine orchestrator.
"""

import re
import unicodedata
from typing import Optional, List, Dict
from .types import (
    NormalizedQuery, DecisionResult, EngineConfig, Rule
)
from .rules import RuleEngine, DEFAULT_RULES
from .embeddings import EmbeddingAnalyzer, DEFAULT_INTENTS
from .ambiguity import AmbiguityDetector
from .decision import DecisionAggregator


class BoundaryEngine:
    """
    Main AI Boundary Engine.
    
    Analyzes queries to determine if they should be answered,
    refused, or require clarification.
    """
    
    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        custom_rules: Optional[List[Rule]] = None,
        custom_intents: Optional[Dict[str, str]] = None
    ):
        """
        Initialize boundary engine.
        
        Args:
            config: Engine configuration (uses defaults if None)
            custom_rules: Additional custom rules
            custom_intents: Additional custom intents
        """
        # Load config
        self.config = config if config is not None else EngineConfig()
        
        # Initialize components
        self._init_rule_engine(custom_rules)
        self._init_embedding_analyzer(custom_intents)
        self._init_ambiguity_detector()
        self._init_decision_aggregator()
    
    def _init_rule_engine(self, custom_rules: Optional[List[Rule]]):
        """Initialize rule engine."""
        rules = DEFAULT_RULES.copy()
        if custom_rules:
            rules.extend(custom_rules)
        
        self.rule_engine = RuleEngine(
            rules=rules,
            sensitivity=self.config.rule_sensitivity
        )
    
    def _init_embedding_analyzer(self, custom_intents: Optional[Dict[str, str]]):
        """Initialize embedding analyzer."""
        intents = DEFAULT_INTENTS.copy()
        if custom_intents:
            intents.update(custom_intents)
        
        self.embedding_analyzer = EmbeddingAnalyzer(
            model_name=self.config.embedding_model,
            intents=intents,
            similarity_threshold=self.config.similarity_threshold
        )
    
    def _init_ambiguity_detector(self):
        """Initialize ambiguity detector."""
        self.ambiguity_detector = AmbiguityDetector(
            min_query_length=self.config.min_query_length,
            vague_verb_penalty=self.config.vague_verb_penalty
        )
    
    def _init_decision_aggregator(self):
        """Initialize decision aggregator."""
        self.decision_aggregator = DecisionAggregator(
            refuse_threshold=self.config.refuse_threshold,
            clarify_threshold=self.config.clarify_threshold
        )
    
    def analyze(self, query: str) -> DecisionResult:
        """
        Analyze a query and return decision.
        
        Args:
            query: User query text
            
        Returns:
            Decision result with reasoning
        """
        # Normalize query
        normalized = self._normalize_query(query)
        
        # Run analysis layers
        rule_matches = self.rule_engine.check(normalized)
        intent_scores = self.embedding_analyzer.analyze(normalized)
        ambiguity = self.ambiguity_detector.analyze(normalized)
        
        # Aggregate decision
        result = self.decision_aggregator.aggregate(
            query=normalized,
            rule_matches=rule_matches,
            intent_scores=intent_scores,
            ambiguity=ambiguity
        )
        
        return result
    
    def _normalize_query(self, query: str) -> NormalizedQuery:
        """
        Normalize query text.
        
        Args:
            query: Raw query text
            
        Returns:
            Normalized query
        """
        if not isinstance(query, str):
            raise TypeError("Query must be a string")

        # Normalize Unicode canonically without discarding non-ASCII characters. Removing
        # them can erase non-English requests before the safety checks run.
        text = unicodedata.normalize("NFC", query).strip()
        if not text:
            raise ValueError("Query cannot be empty")

        # Normalize whitespace while preserving the original input separately.
        text = re.sub(r'\s+', ' ', text)
        
        # Calculate metrics
        length = len(text)
        tokens = len(text.split())
        
        return NormalizedQuery(
            text=text,
            original=query,
            length=length,
            tokens=tokens
        )
    
    def add_rule(self, rule: Rule) -> None:
        """Add a custom rule."""
        self.rule_engine.add_rule(rule)
    
    def add_intent(self, name: str, description: str) -> None:
        """Add a custom intent category."""
        self.embedding_analyzer.add_intent(name, description)
    
    def batch_analyze(self, queries: List[str]) -> List[DecisionResult]:
        """
        Analyze multiple queries.
        
        Args:
            queries: List of query texts
            
        Returns:
            List of decision results
        """
        return [self.analyze(q) for q in queries]
