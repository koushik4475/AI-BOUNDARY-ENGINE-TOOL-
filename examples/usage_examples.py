"""
Example usage of AI Boundary Engine.
"""

from boundary_engine import BoundaryEngine, Decision, Rule, RiskTag


def basic_usage():
    """Basic usage example."""
    print("=" * 60)
    print("BASIC USAGE EXAMPLE")
    print("=" * 60)
    
    engine = BoundaryEngine()
    
    # Test queries
    queries = [
        "What is photosynthesis?",
        "How to make a bomb",
        "Explain quantum computing",
        "How to hack a database",
        "What medication for headache?",
        "How to fix it",
    ]
    
    for query in queries:
        result = engine.analyze(query)
        print(f"\nQuery: {query}")
        print(f"Decision: {result.decision}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Reasons: {', '.join(result.reasons[:2])}")
        print("-" * 60)


def custom_rules_example():
    """Example with custom rules."""
    print("\n" + "=" * 60)
    print("CUSTOM RULES EXAMPLE")
    print("=" * 60)
    
    # Define custom rule
    custom_rule = Rule(
        name="company_secrets",
        keywords=["internal", "proprietary", "confidential", "trade secret"],
        decision=Decision.REFUSE,
        severity=0.9,
        reason="Request involves company confidential information",
        tags=[RiskTag.PERSONAL_DATA]
    )
    
    engine = BoundaryEngine(custom_rules=[custom_rule])
    
    queries = [
        "What are our company's internal processes?",
        "Explain machine learning basics",
    ]
    
    for query in queries:
        result = engine.analyze(query)
        print(f"\nQuery: {query}")
        print(f"Decision: {result.decision}")
        print(f"Matched Rules: {[m.rule_name for m in result.rule_matches]}")
        print("-" * 60)


def custom_intents_example():
    """Example with custom intents."""
    print("\n" + "=" * 60)
    print("CUSTOM INTENTS EXAMPLE")
    print("=" * 60)
    
    # Define custom intents
    custom_intents = {
        "spam_detection": "promotional content, advertising, or spam messages",
        "off_topic": "content unrelated to the main purpose or topic"
    }
    
    engine = BoundaryEngine(custom_intents=custom_intents)
    
    queries = [
        "Buy our amazing product now! 50% off!",
        "What is the capital of France?",
    ]
    
    for query in queries:
        result = engine.analyze(query)
        print(f"\nQuery: {query}")
        print(f"Decision: {result.decision}")
        print(f"Top Intent: {result.intent_scores[0].intent if result.intent_scores else 'N/A'}")
        print("-" * 60)


def llm_integration_example():
    """Example of integrating with LLM."""
    print("\n" + "=" * 60)
    print("LLM INTEGRATION EXAMPLE")
    print("=" * 60)
    
    engine = BoundaryEngine()
    
    def safe_llm_call(user_query: str) -> str:
        """Safely call LLM with boundary check."""
        # Check query first
        boundary = engine.analyze(user_query)
        
        if boundary.decision == Decision.REFUSE:
            return f"❌ Cannot process request: {', '.join(boundary.reasons)}"
        
        if boundary.decision == Decision.CLARIFY:
            return f"⚠️  Please clarify: {', '.join(boundary.reasons)}"
        
        # Safe to proceed - simulate LLM call
        return f"✅ [LLM would process: '{user_query}']"
    
    # Test queries
    test_queries = [
        "How to make a bomb",
        "Explain machine learning",
        "How to fix it",
    ]
    
    for query in test_queries:
        response = safe_llm_call(query)
        print(f"\nUser: {query}")
        print(f"System: {response}")
        print("-" * 60)


def batch_processing_example():
    """Example of batch processing."""
    print("\n" + "=" * 60)
    print("BATCH PROCESSING EXAMPLE")
    print("=" * 60)
    
    engine = BoundaryEngine()
    
    queries = [
        "What is AI?",
        "How to hack systems",
        "Explain photosynthesis",
        "Ways to harm someone",
        "What is Python?",
    ]
    
    results = engine.batch_analyze(queries)
    
    # Summary
    print(f"\nProcessed {len(results)} queries:")
    print(f"  ANSWER: {sum(1 for r in results if r.decision == Decision.ANSWER)}")
    print(f"  REFUSE: {sum(1 for r in results if r.decision == Decision.REFUSE)}")
    print(f"  CLARIFY: {sum(1 for r in results if r.decision == Decision.CLARIFY)}")
    
    # Details
    print("\nDetails:")
    for result in results:
        symbol = {
            Decision.ANSWER: "✅",
            Decision.REFUSE: "❌",
            Decision.CLARIFY: "⚠️ "
        }.get(result.decision, "?")
        
        print(f"{symbol} {result.query[:50]:50s} -> {result.decision}")


def verbose_analysis_example():
    """Example with detailed analysis."""
    print("\n" + "=" * 60)
    print("VERBOSE ANALYSIS EXAMPLE")
    print("=" * 60)
    
    engine = BoundaryEngine()
    query = "How to make explosives"
    
    result = engine.analyze(query)
    
    print(f"\nQuery: {query}")
    print(f"\nDecision: {result.decision}")
    print(f"Confidence: {result.confidence:.3f}")
    
    print("\nReasons:")
    for i, reason in enumerate(result.reasons, 1):
        print(f"  {i}. {reason}")
    
    print("\nRisk Tags:")
    print(f"  {', '.join(str(tag) for tag in result.risk_tags)}")
    
    if result.rule_matches:
        print("\nMatched Rules:")
        for match in result.rule_matches:
            print(f"  - {match.rule_name}: {match.confidence:.2f}")
            print(f"    Reason: {match.reason}")
            if match.matched_keywords:
                print(f"    Keywords: {', '.join(match.matched_keywords)}")
    
    if result.intent_scores:
        print("\nTop Intent Scores:")
        for score in result.intent_scores[:5]:
            print(f"  - {score.intent}: {score.similarity:.3f}")
    
    if result.ambiguity:
        print("\nAmbiguity Analysis:")
        print(f"  Is Ambiguous: {result.ambiguity.is_ambiguous}")
        print(f"  Score: {result.ambiguity.score:.3f}")
        if result.ambiguity.reasons:
            print(f"  Reasons: {', '.join(result.ambiguity.reasons)}")


if __name__ == "__main__":
    basic_usage()
    custom_rules_example()
    custom_intents_example()
    llm_integration_example()
    batch_processing_example()
    verbose_analysis_example()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
