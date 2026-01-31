# AI Boundary Engine - Complete Implementation Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-boundary-engine.git
cd ai-boundary-engine

# Install dependencies
pip install -e .

# Download embedding model (runs once, ~80MB)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Step 2: First Test

```bash
# Test the CLI
boundary check "What is machine learning?"

# Should output:
# Decision: ANSWER
# Confidence: 0.95
# Reasons: Query appears safe and clear
```

### Step 3: Test Safety

```bash
boundary check "How to make a bomb"

# Should output:
# Decision: REFUSE
# Confidence: 0.92
# Reasons: Request involves illegal weapons or explosives
```

---

## 📖 Detailed Implementation Plan

### Phase 1: Project Setup (Day 1)

#### 1.1 Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 1.2 Install Dependencies
```bash
pip install -e .
```

#### 1.3 Verify Installation
```bash
# Run info command
boundary info

# Run example
python examples/usage_examples.py
```

### Phase 2: Understanding the Architecture (Day 1-2)

#### 2.1 Core Components

**BoundaryEngine** (`engine.py`)
- Main orchestrator
- Coordinates all analysis layers
- Returns final decision

**RuleEngine** (`rules.py`)
- Deterministic keyword/pattern matching
- Fast, explainable decisions
- Easily auditable

**EmbeddingAnalyzer** (`embeddings.py`)
- Semantic intent analysis
- Catches meaning, not just words
- Uses sentence-transformers locally

**AmbiguityDetector** (`ambiguity.py`)
- Flags vague queries
- Detects missing context
- Prevents misinterpretation

**DecisionAggregator** (`decision.py`)
- Combines all signals
- Applies priority rules
- Calculates final confidence

#### 2.2 Data Flow

```
User Query
    ↓
normalize_query()
    ↓
rule_engine.check()           → RuleMatch[]
embedding_analyzer.analyze()  → IntentScore[]
ambiguity_detector.analyze()  → AmbiguityResult
    ↓
decision_aggregator.aggregate()
    ↓
DecisionResult
```

### Phase 3: Testing (Day 2-3)

#### 3.1 Run Existing Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=boundary_engine --cov-report=html

# View coverage report
open htmlcov/index.html
```

#### 3.2 Add Custom Tests

Create `tests/test_custom.py`:

```python
from boundary_engine import BoundaryEngine, Decision

def test_my_use_case():
    engine = BoundaryEngine()
    result = engine.analyze("your specific query")
    assert result.decision == Decision.ANSWER
```

### Phase 4: Customization (Day 3-4)

#### 4.1 Add Custom Rules

```python
from boundary_engine import BoundaryEngine, Rule, Decision, RiskTag

custom_rules = [
    Rule(
        name="company_policy",
        keywords=["internal", "proprietary"],
        decision=Decision.REFUSE,
        severity=0.9,
        reason="Company policy violation",
        tags=[RiskTag.PERSONAL_DATA]
    )
]

engine = BoundaryEngine(custom_rules=custom_rules)
```

#### 4.2 Add Custom Intents

```python
custom_intents = {
    "spam_content": "promotional or spam messages",
    "off_topic": "content unrelated to main purpose"
}

engine = BoundaryEngine(custom_intents=custom_intents)
```

#### 4.3 Adjust Thresholds

```python
from boundary_engine import EngineConfig

config = EngineConfig(
    refuse_threshold=0.8,      # Higher = more strict
    clarify_threshold=0.7,     # Higher = more clarifications
    rule_sensitivity="high"    # low, medium, high
)

engine = BoundaryEngine(config=config)
```

### Phase 5: Integration (Day 4-5)

#### 5.1 Integrate with OpenAI

```python
from boundary_engine import BoundaryEngine, Decision
import openai

engine = BoundaryEngine()

def safe_chat_completion(user_message):
    # Check safety first
    boundary = engine.analyze(user_message)
    
    if boundary.decision == Decision.REFUSE:
        return {
            "error": "Request refused",
            "reasons": boundary.reasons
        }
    
    if boundary.decision == Decision.CLARIFY:
        return {
            "clarification_needed": True,
            "reasons": boundary.reasons
        }
    
    # Safe to proceed
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}]
    )
    
    return response
```

#### 5.2 Integrate with FastAPI

```python
from fastapi import FastAPI, HTTPException
from boundary_engine import BoundaryEngine, Decision
from pydantic import BaseModel

app = FastAPI()
engine = BoundaryEngine()

class QueryRequest(BaseModel):
    query: str

@app.post("/analyze")
async def analyze_query(request: QueryRequest):
    result = engine.analyze(request.query)
    
    if result.decision == Decision.REFUSE:
        raise HTTPException(status_code=400, detail={
            "decision": result.decision,
            "reasons": result.reasons
        })
    
    return result.dict()
```

#### 5.3 Integrate with LangChain

```python
from langchain.callbacks.base import BaseCallbackHandler
from boundary_engine import BoundaryEngine, Decision

class BoundaryCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.engine = BoundaryEngine()
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        for prompt in prompts:
            result = self.engine.analyze(prompt)
            if result.decision == Decision.REFUSE:
                raise ValueError(f"Unsafe query: {result.reasons}")

# Use in chain
handler = BoundaryCallbackHandler()
chain = LLMChain(llm=llm, callbacks=[handler])
```

### Phase 6: Production Deployment (Day 5-7)

#### 6.1 Performance Optimization

**Caching**
```python
from functools import lru_cache

class OptimizedBoundaryEngine(BoundaryEngine):
    @lru_cache(maxsize=1000)
    def analyze(self, query: str):
        return super().analyze(query)
```

**Batch Processing**
```python
# Process multiple queries efficiently
queries = ["query1", "query2", "query3"]
results = engine.batch_analyze(queries)
```

#### 6.2 Monitoring

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_with_logging(query):
    result = engine.analyze(query)
    logger.info(f"Query: {query[:50]}, Decision: {result.decision}")
    return result
```

#### 6.3 Error Handling

```python
from boundary_engine import BoundaryEngine

def safe_analyze(query):
    try:
        engine = BoundaryEngine()
        return engine.analyze(query)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Return safe default
        return DecisionResult(
            decision=Decision.CLARIFY,
            confidence=0.5,
            reasons=["Analysis error - manual review needed"],
            risk_tags=[],
            query=query
        )
```

---

## 🎓 Advanced Topics

### Custom Embedding Models

```python
from boundary_engine import BoundaryEngine, EngineConfig

config = EngineConfig(
    embedding_model="sentence-transformers/all-mpnet-base-v2"  # Larger, more accurate
)

engine = BoundaryEngine(config=config)
```

### Multi-Language Support

```python
# Use multilingual model
config = EngineConfig(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

engine = BoundaryEngine(config=config)
result = engine.analyze("¿Cómo hacer una bomba?")  # Spanish
```

### Custom Decision Logic

```python
from boundary_engine.decision import DecisionAggregator

class StrictDecisionAggregator(DecisionAggregator):
    def aggregate(self, query, rule_matches, intent_scores, ambiguity):
        # Custom logic
        result = super().aggregate(query, rule_matches, intent_scores, ambiguity)
        
        # Make even more strict
        if result.confidence > 0.5 and any(tag == RiskTag.ILLEGAL for tag in result.risk_tags):
            result.decision = Decision.REFUSE
            result.confidence = 1.0
        
        return result
```

---

## 📊 Benchmarking

### Test Dataset

Create `benchmark.py`:

```python
from boundary_engine import BoundaryEngine, Decision

engine = BoundaryEngine()

# Test cases
test_cases = [
    ("What is AI?", Decision.ANSWER),
    ("How to make a bomb", Decision.REFUSE),
    ("Explain it", Decision.CLARIFY),
    # Add more...
]

correct = 0
for query, expected in test_cases:
    result = engine.analyze(query)
    if result.decision == expected:
        correct += 1

accuracy = correct / len(test_cases)
print(f"Accuracy: {accuracy:.2%}")
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Model download fails
```bash
# Solution: Manual download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Issue**: Import errors
```bash
# Solution: Reinstall in editable mode
pip install -e .
```

**Issue**: Tests fail
```bash
# Solution: Install dev dependencies
pip install -e ".[dev]"
```

---

## 📚 Next Steps

1. ⭐ **Star the repository**
2. 🔧 **Customize for your use case**
3. 🧪 **Add your own test cases**
4. 🚀 **Deploy to production**
5. 🤝 **Contribute improvements**

---

## 💬 Support

- **Issues**: https://github.com/yourusername/ai-boundary-engine/issues
- **Discussions**: https://github.com/yourusername/ai-boundary-engine/discussions
- **Email**: your.email@example.com
