"""
Intent analysis using sentence embeddings.
"""

import os
from typing import Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from .types import IntentScore, NormalizedQuery


# Default intent categories
DEFAULT_INTENTS = {
    "harmful_instruction": "instructions to cause physical harm, violence, or damage to people or property",
    "illegal_activity": "activities that are illegal such as fraud, theft, hacking, or producing illegal substances",
    "personal_data_breach": "requests for private information, passwords, API keys, or personal identifiable information",
    "self_harm_content": "content related to self-harm, suicide, or dangerous behaviors to oneself",
    "manipulation_deception": "attempts to deceive, manipulate, or scam others",
    "medical_diagnosis": "requests for medical diagnosis, treatment, or dosage without proper context",
    "legal_judgment": "requests for legal advice, judgments, or contract interpretation",
    "ambiguous_request": "vague or underspecified questions that lack necessary context or details",
    "safe_educational": "legitimate educational, informational, or creative requests",
    "safe_general": "general conversation, questions about facts, or harmless requests",
}


class EmbeddingAnalyzer:
    """Semantic intent analysis using embeddings."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        intents: Optional[Dict[str, str]] = None,
        similarity_threshold: float = 0.75,
        device: str = "cpu"
    ):
        """
        Initialize embedding analyzer.
        
        Args:
            model_name: SentenceTransformer model name
            intents: Custom intent categories (defaults to DEFAULT_INTENTS)
            similarity_threshold: Minimum similarity to flag an intent
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.intents = intents if intents is not None else DEFAULT_INTENTS
        self.similarity_threshold = similarity_threshold
        self.device = device
        
        # Suppress tokenizer warnings
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Load model
        self.model = SentenceTransformer(model_name, device=device)
        
        # Precompute intent embeddings
        self._intent_embeddings = self._compute_intent_embeddings()
    
    def _compute_intent_embeddings(self) -> Dict[str, np.ndarray]:
        """Precompute and cache embeddings for all intents."""
        intent_texts = list(self.intents.values())
        embeddings = self.model.encode(intent_texts, convert_to_numpy=True)
        
        return {
            intent_name: embeddings[i]
            for i, intent_name in enumerate(self.intents.keys())
        }
    
    def analyze(self, query: NormalizedQuery) -> List[IntentScore]:
        """
        Analyze query intent using semantic similarity.
        
        Args:
            query: Normalized query to analyze
            
        Returns:
            List of intent scores sorted by similarity
        """
        # Encode query
        query_embedding = self.model.encode(query.text, convert_to_numpy=True)
        
        # Calculate similarities
        scores = []
        for intent_name, intent_embedding in self._intent_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, intent_embedding)
            # Clamp to [0, 1] to handle floating point precision
            similarity = max(0.0, min(1.0, float(similarity)))
            
            scores.append(IntentScore(
                intent=intent_name,
                similarity=similarity,
                description=self.intents[intent_name]
            ))
        
        # Sort by similarity (highest first)
        scores.sort(key=lambda x: x.similarity, reverse=True)
        
        # Filter by threshold
        filtered_scores = [s for s in scores if s.similarity >= self.similarity_threshold]
        
        return filtered_scores if filtered_scores else scores[:3]  # Return top 3 if none above threshold
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def add_intent(self, name: str, description: str) -> None:
        """
        Add a custom intent category.
        
        Args:
            name: Intent name
            description: Intent description
        """
        self.intents[name] = description
        # Recompute embeddings
        embedding = self.model.encode(description, convert_to_numpy=True)
        self._intent_embeddings[name] = embedding
    
    def get_top_intent(self, query: NormalizedQuery) -> Optional[IntentScore]:
        """Get the highest scoring intent for a query."""
        scores = self.analyze(query)
        return scores[0] if scores else None
