"""
Ambiguity detection for queries requiring clarification.
"""

import re
from typing import List
from .types import AmbiguityResult, NormalizedQuery


# Vague verbs that often indicate ambiguity
VAGUE_VERBS = {
    "explain", "tell", "show", "describe", "help",
    "fix", "solve", "handle", "deal", "work",
    "do", "make", "get", "find", "see"
}

# Pronouns without clear referents
UNCLEAR_PRONOUNS = {
    "it", "this", "that", "these", "those",
    "them", "they", "something", "anything"
}


class AmbiguityDetector:
    """Detector for ambiguous or underspecified queries."""
    
    def __init__(
        self,
        min_query_length: int = 5,
        vague_verb_penalty: float = 0.2,
        pronoun_penalty: float = 0.15
    ):
        """
        Initialize ambiguity detector.
        
        Args:
            min_query_length: Minimum acceptable query length
            vague_verb_penalty: Penalty score for vague verbs
            pronoun_penalty: Penalty score for unclear pronouns
        """
        self.min_query_length = min_query_length
        self.vague_verb_penalty = vague_verb_penalty
        self.pronoun_penalty = pronoun_penalty
    
    def analyze(self, query: NormalizedQuery) -> AmbiguityResult:
        """
        Analyze query for ambiguity.
        
        Args:
            query: Normalized query to analyze
            
        Returns:
            Ambiguity analysis result
        """
        reasons = []
        score = 0.0
        
        # Check query length
        if query.length < self.min_query_length:
            reasons.append("query is too short")
            score += 0.3
        
        # Check for vague verbs
        vague_verbs_found = self._find_vague_verbs(query.text)
        if vague_verbs_found:
            reasons.append(f"contains vague verbs: {', '.join(vague_verbs_found[:3])}")
            score += self.vague_verb_penalty * len(vague_verbs_found)
        
        # Check for unclear pronouns
        unclear_pronouns = self._find_unclear_pronouns(query.text)
        if unclear_pronouns:
            reasons.append(f"contains unclear pronouns: {', '.join(unclear_pronouns[:3])}")
            score += self.pronoun_penalty * len(unclear_pronouns)
        
        # Check for missing object/subject
        if self._missing_object(query.text):
            reasons.append("missing specific object or subject")
            score += 0.25
        
        # Check for multiple possible interpretations
        if self._multiple_interpretations(query.text):
            reasons.append("multiple possible interpretations")
            score += 0.2
        
        # Check for context-dependent questions
        if self._context_dependent(query.text):
            reasons.append("requires additional context")
            score += 0.2
        
        # Cap score at 1.0
        score = min(score, 1.0)
        
        # Consider ambiguous if score > 0.4
        is_ambiguous = score > 0.4
        
        return AmbiguityResult(
            is_ambiguous=is_ambiguous,
            score=score,
            reasons=reasons
        )
    
    def _find_vague_verbs(self, text: str) -> List[str]:
        """Find vague verbs in text."""
        words = text.lower().split()
        return [w for w in words if w in VAGUE_VERBS]
    
    def _find_unclear_pronouns(self, text: str) -> List[str]:
        """Find unclear pronouns in text."""
        words = text.lower().split()
        
        # Only flag pronouns at the beginning or without clear antecedents
        found = []
        for i, word in enumerate(words):
            if word in UNCLEAR_PRONOUNS:
                # Check if at the beginning or early in sentence
                if i < 3:
                    found.append(word)
        
        return found
    
    def _missing_object(self, text: str) -> bool:
        """Check if query is missing a specific object."""
        # Very short queries with vague verbs likely missing object
        words = text.lower().split()
        
        if len(words) <= 3:
            # Check if has vague verb but no clear object
            has_vague = any(w in VAGUE_VERBS for w in words)
            has_object = any(len(w) > 4 for w in words if w not in VAGUE_VERBS)
            
            return has_vague and not has_object
        
        return False
    
    def _multiple_interpretations(self, text: str) -> bool:
        """Check if query could have multiple interpretations."""
        # Detect ambiguous phrasing patterns
        ambiguous_patterns = [
            r'\bor\b',  # "A or B" questions
            r'\bmultiple\b',
            r'\bdifferent ways\b',
            r'\bvarious\b',
        ]
        
        for pattern in ambiguous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _context_dependent(self, text: str) -> bool:
        """Check if query requires external context."""
        context_patterns = [
            r'\bmy\b',  # "my file", "my code"
            r'\bthis\s+\w+',  # "this code", "this file"
            r'\bthe\s+(above|below|previous|following)\b',
            r'\bcurrent\b',
            r'\beach\s+\w+',  # "each item" without defining items
        ]
        
        for pattern in context_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
