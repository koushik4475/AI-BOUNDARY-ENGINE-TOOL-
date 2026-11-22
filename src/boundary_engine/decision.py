"""
Decision aggregation logic for combining multiple signals.
"""

from typing import List
from .types import (
    Decision, DecisionResult, RuleMatch, IntentScore,
    AmbiguityResult, RiskTag, NormalizedQuery
)


class DecisionAggregator:
    """Aggregates signals from rules, intents, and ambiguity into final decision."""
    
    def __init__(
        self,
        refuse_threshold: float = 0.7,
        clarify_threshold: float = 0.6
    ):
        """
        Initialize decision aggregator.
        
        Args:
            refuse_threshold: Confidence threshold for REFUSE decision
            clarify_threshold: Confidence threshold for CLARIFY decision
        """
        self.refuse_threshold = refuse_threshold
        self.clarify_threshold = clarify_threshold
    
    def aggregate(
        self,
        query: NormalizedQuery,
        rule_matches: List[RuleMatch],
        intent_scores: List[IntentScore],
        ambiguity: AmbiguityResult
    ) -> DecisionResult:
        """
        Aggregate all signals into a final decision.
        
        Priority order:
        1. REFUSE beats everything (safety first)
        2. CLARIFY beats ANSWER (precision matters)
        3. ANSWER only if safe + clear
        
        Args:
            query: Original normalized query
            rule_matches: Matched safety rules
            intent_scores: Intent similarity scores
            ambiguity: Ambiguity analysis
            
        Returns:
            Final decision with reasoning
        """
        # Collect signals
        refuse_signals = self._get_refuse_signals(rule_matches, intent_scores)
        clarify_signals = self._get_clarify_signals(rule_matches, ambiguity)
        
        # Calculate confidence scores
        refuse_confidence = self._calculate_refuse_confidence(refuse_signals, intent_scores, rule_matches)
        clarify_confidence = self._calculate_clarify_confidence(clarify_signals, ambiguity, rule_matches)
        
        # Make decision (priority order)
        if refuse_confidence >= self.refuse_threshold:
            decision = Decision.REFUSE
            confidence = refuse_confidence
            reasons = self._build_refuse_reasons(refuse_signals, intent_scores)
            risk_tags = self._extract_risk_tags(rule_matches, intent_scores)
        
        elif clarify_confidence >= self.clarify_threshold:
            decision = Decision.CLARIFY
            confidence = clarify_confidence
            reasons = self._build_clarify_reasons(clarify_signals, ambiguity)
            risk_tags = self._extract_risk_tags(rule_matches, intent_scores)
        
        else:
            decision = Decision.ANSWER
            confidence = 1.0 - max(refuse_confidence, clarify_confidence)
            reasons = ["Query appears safe and clear"]
            risk_tags = [RiskTag.SAFE]
        
        return DecisionResult(
            decision=decision,
            confidence=confidence,
            reasons=reasons,
            risk_tags=risk_tags,
            rule_matches=rule_matches,
            intent_scores=intent_scores[:5],  # Top 5 intents
            ambiguity=ambiguity,
            query=query.original
        )
    
    def _get_refuse_signals(
        self,
        rule_matches: List[RuleMatch],
        intent_scores: List[IntentScore]
    ) -> List[str]:
        """Get signals suggesting REFUSE decision."""
        signals = []
        
        # Rules suggesting refusal
        for match in rule_matches:
            if match.decision == Decision.REFUSE:
                signals.append(f"rule:{match.rule_name}")
        
        # High-risk intents
        harmful_intents = [
            "harmful_instruction", "illegal_activity",
            "personal_data_breach", "self_harm_content",
            "manipulation_deception"
        ]
        
        for score in intent_scores:
            if score.intent in harmful_intents and score.similarity > 0.75:
                signals.append(f"intent:{score.intent}")
        
        return signals
    
    def _get_clarify_signals(
        self,
        rule_matches: List[RuleMatch],
        ambiguity: AmbiguityResult
    ) -> List[str]:
        """Get signals suggesting CLARIFY decision."""
        signals = []
        
        # Rules suggesting clarification
        for match in rule_matches:
            if match.decision == Decision.CLARIFY:
                signals.append(f"rule:{match.rule_name}")
        
        # Ambiguity signals
        if ambiguity.is_ambiguous:
            signals.append("ambiguity")
        
        return signals
    
    def _calculate_refuse_confidence(
        self,
        refuse_signals: List[str],
        intent_scores: List[IntentScore],
        rule_matches: List[RuleMatch]
    ) -> float:
        """Calculate confidence for REFUSE decision."""
        if not refuse_signals:
            return 0.0
        
        # Preserve the confidence assigned by the matching safety rule.
        rule_score = max(
            (match.confidence for match in rule_matches if match.decision == Decision.REFUSE),
            default=0.0
        )
        
        # Get max intent similarity for harmful intents
        intent_score = 0.0
        if intent_scores:
            harmful_intents = [
                "harmful_instruction", "illegal_activity",
                "personal_data_breach", "self_harm_content"
            ]
            intent_score = max(
                (s.similarity for s in intent_scores if s.intent in harmful_intents),
                default=0.0
            )
        
        return max(rule_score, intent_score)
    
    def _calculate_clarify_confidence(
        self,
        clarify_signals: List[str],
        ambiguity: AmbiguityResult,
        rule_matches: List[RuleMatch]
    ) -> float:
        """Calculate confidence for CLARIFY decision."""
        if not clarify_signals:
            return 0.0
        
        # Base confidence from signal count
        signal_score = min(len(clarify_signals) * 0.3, 0.6)
        
        # Add ambiguity score
        ambiguity_score = ambiguity.score * 0.4
        
        rule_score = max(
            (match.confidence for match in rule_matches if match.decision == Decision.CLARIFY),
            default=0.0
        )
        return min(max(rule_score, signal_score + ambiguity_score), 1.0)
    
    def _build_refuse_reasons(
        self,
        refuse_signals: List[str],
        intent_scores: List[IntentScore]
    ) -> List[str]:
        """Build human-readable reasons for REFUSE decision."""
        reasons = []
        
        # Add high-level categorization
        if any("illegal" in s or "harmful" in s for s in refuse_signals):
            reasons.append("Request involves potentially illegal or harmful activity")
        
        if any("personal_data" in s for s in refuse_signals):
            reasons.append("Request asks for sensitive personal data")
        
        if any("self_harm" in s for s in refuse_signals):
            reasons.append("Content related to self-harm detected - please seek professional help")
        
        # Add top harmful intent if present
        harmful_intents = [
            s for s in intent_scores
            if s.intent in ["harmful_instruction", "illegal_activity", "self_harm_content"]
            and s.similarity > 0.75
        ]
        
        if harmful_intents:
            top_intent = harmful_intents[0]
            reasons.append(f"High similarity to {top_intent.intent.replace('_', ' ')}")
        
        # Fallback
        if not reasons:
            reasons = ["Safety concerns detected in request"]
        
        return reasons
    
    def _build_clarify_reasons(
        self,
        clarify_signals: List[str],
        ambiguity: AmbiguityResult
    ) -> List[str]:
        """Build human-readable reasons for CLARIFY decision."""
        reasons = []
        
        # Add ambiguity reasons
        if ambiguity.is_ambiguous:
            reasons.extend(ambiguity.reasons)
        
        # Add rule-based clarification needs
        if any("medical" in s for s in clarify_signals):
            reasons.append("Medical questions require professional consultation")
        
        if any("legal" in s for s in clarify_signals):
            reasons.append("Legal questions require licensed professional advice")
        
        # Fallback
        if not reasons:
            reasons = ["Additional context or clarification needed"]
        
        return reasons
    
    def _extract_risk_tags(
        self,
        rule_matches: List[RuleMatch],
        intent_scores: List[IntentScore]
    ) -> List[RiskTag]:
        """Extract risk tags from matches and intents."""
        tags = set()
        
        # From rule matches
        # Note: rule_matches don't directly have tags in RuleMatch type,
        # but we can infer from rule names
        for match in rule_matches:
            if "illegal" in match.rule_name:
                tags.add(RiskTag.ILLEGAL)
            if "violence" in match.rule_name or "harm" in match.rule_name:
                tags.add(RiskTag.VIOLENCE)
            if "self_harm" in match.rule_name:
                tags.add(RiskTag.SELF_HARM)
            if "medical" in match.rule_name:
                tags.add(RiskTag.MEDICAL)
            if "legal" in match.rule_name:
                tags.add(RiskTag.LEGAL)
            if "personal_data" in match.rule_name:
                tags.add(RiskTag.PERSONAL_DATA)
        
        # From intents
        intent_to_tag = {
            "harmful_instruction": RiskTag.VIOLENCE,
            "illegal_activity": RiskTag.ILLEGAL,
            "personal_data_breach": RiskTag.PERSONAL_DATA,
            "self_harm_content": RiskTag.SELF_HARM,
            "medical_diagnosis": RiskTag.MEDICAL,
            "legal_judgment": RiskTag.LEGAL,
            "ambiguous_request": RiskTag.AMBIGUOUS,
        }
        
        for score in intent_scores:
            if score.similarity > 0.7 and score.intent in intent_to_tag:
                tags.add(intent_to_tag[score.intent])
        
        return list(tags) if tags else [RiskTag.SAFE]
