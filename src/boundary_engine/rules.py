"""
Rule engine for deterministic safety checks.
"""

import re
from typing import List, Optional
from .types import Rule, RuleMatch, Decision, RiskTag, NormalizedQuery


# Default safety rules
DEFAULT_RULES = [
    Rule(
        name="illegal_weapons",
        keywords=[
            "bomb", "explosive", "pipe bomb", "molotov", "grenade",
            "c4", "tnt", "dynamite", "detonator", "blasting cap",
            "gunpowder", "ammonium nitrate", "fertilizer bomb"
        ],
        decision=Decision.REFUSE,
        severity=0.95,
        reason="Request involves illegal weapons or explosives",
        tags=[RiskTag.ILLEGAL, RiskTag.VIOLENCE]
    ),
    
    Rule(
        name="illegal_drugs",
        keywords=[
            "meth", "methamphetamine", "cocaine", "heroin", "fentanyl",
            "synthesize drugs", "cook meth", "drug lab", "precursor chemicals",
            "mdma synthesis", "lsd synthesis"
        ],
        decision=Decision.REFUSE,
        severity=0.93,
        reason="Request involves illegal drug production",
        tags=[RiskTag.ILLEGAL]
    ),
    
    Rule(
        name="hacking_malicious",
        keywords=[
            "hack into", "break into system", "bypass security", "exploit vulnerability",
            "ddos attack", "ransomware", "malware", "keylogger", "trojan",
            "sql injection", "xss attack", "brute force password"
        ],
        decision=Decision.REFUSE,
        severity=0.90,
        reason="Request involves malicious hacking or cybercrime",
        tags=[RiskTag.ILLEGAL]
    ),
    
    Rule(
        name="violence_harm",
        keywords=[
            "how to kill", "murder someone", "assassinate", "poison someone",
            "torture", "hurt someone", "cause pain", "attack", "assault"
        ],
        decision=Decision.REFUSE,
        severity=0.95,
        reason="Request involves violence or causing harm",
        tags=[RiskTag.VIOLENCE]
    ),
    
    Rule(
        name="self_harm",
        keywords=[
            "kill myself", "commit suicide", "end my life", "ways to die",
            "self harm", "cut myself", "overdose", "painless death"
        ],
        decision=Decision.REFUSE,
        severity=0.98,
        reason="Request involves self-harm or suicide - please seek help immediately",
        tags=[RiskTag.SELF_HARM]
    ),
    
    Rule(
        name="fraud_identity",
        keywords=[
            "fake id", "counterfeit", "forge document", "fake passport",
            "identity theft", "social security fraud", "phishing scam",
            "credit card fraud", "money laundering"
        ],
        decision=Decision.REFUSE,
        severity=0.92,
        reason="Request involves fraud or identity theft",
        tags=[RiskTag.ILLEGAL]
    ),
    
    Rule(
        name="medical_advice",
        keywords=[
            "diagnose", "diagnosis", "medical treatment", "cure for",
            "dosage", "prescription", "medication for", "should i take",
            "medical emergency", "symptoms mean"
        ],
        decision=Decision.CLARIFY,
        severity=0.75,
        reason="Medical advice requires professional consultation - can provide general information only",
        tags=[RiskTag.MEDICAL]
    ),
    
    Rule(
        name="legal_advice",
        keywords=[
            "legal advice", "sue", "lawsuit", "court case", "contract review",
            "am i liable", "legal rights", "lawyer", "attorney"
        ],
        decision=Decision.CLARIFY,
        severity=0.70,
        reason="Legal advice requires licensed professional - can provide general information only",
        tags=[RiskTag.LEGAL]
    ),
    
    Rule(
        name="personal_data_request",
        keywords=[
            "give me your", "what is your password", "api key", "secret key",
            "private key", "credit card number", "ssn", "social security"
        ],
        decision=Decision.REFUSE,
        severity=0.85,
        reason="Cannot provide personal or sensitive data",
        tags=[RiskTag.PERSONAL_DATA]
    ),
    
    Rule(
        name="child_safety",
        keywords=[
            "child abuse", "child exploitation", "inappropriate with child",
            "underage", "minor", "csam"
        ],
        decision=Decision.REFUSE,
        severity=1.0,
        reason="Content involves child safety violations",
        tags=[RiskTag.ILLEGAL, RiskTag.VIOLENCE]
    ),
]


class RuleEngine:
    """Rule-based safety checker."""
    
    def __init__(self, rules: Optional[List[Rule]] = None, sensitivity: str = "high"):
        """
        Initialize rule engine.
        
        Args:
            rules: Custom rules to use (defaults to DEFAULT_RULES)
            sensitivity: Rule sensitivity level (low, medium, high)
        """
        self.rules = rules if rules is not None else DEFAULT_RULES
        self.sensitivity = sensitivity
        
        # Adjust severity based on sensitivity
        self.severity_multiplier = {
            "low": 0.7,
            "medium": 0.85,
            "high": 1.0
        }.get(sensitivity, 1.0)
        
    def check(self, query: NormalizedQuery) -> List[RuleMatch]:
        """
        Check query against all rules.
        
        Args:
            query: Normalized query to check
            
        Returns:
            List of rule matches
        """
        matches = []
        text_lower = query.text.lower()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            matched_keywords = self._check_keywords(text_lower, rule.keywords)
            pattern_match = self._check_patterns(query.text, rule.patterns)
            
            if matched_keywords or pattern_match:
                adjusted_severity = rule.severity * self.severity_multiplier
                
                match = RuleMatch(
                    rule_name=rule.name,
                    decision=rule.decision,
                    confidence=adjusted_severity,
                    reason=rule.reason,
                    matched_keywords=matched_keywords
                )
                matches.append(match)
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches
    
    def _check_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Check if any keywords are present in text."""
        matched = []
        for keyword in keywords:
            # Use word boundaries for more accurate matching
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                matched.append(keyword)
        return matched
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if any regex patterns match."""
        for pattern in patterns:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            except re.error:
                # Skip invalid patterns
                continue
        return False
    
    def add_rule(self, rule: Rule) -> None:
        """Add a custom rule to the engine."""
        self.rules.append(rule)
    
    def disable_rule(self, rule_name: str) -> None:
        """Disable a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                break
    
    def enable_rule(self, rule_name: str) -> None:
        """Enable a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                break
