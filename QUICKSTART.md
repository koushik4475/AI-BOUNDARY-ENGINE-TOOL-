# 🚀 Quick Start Guide

Get up and running with AI Boundary Engine in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip package manager
- ~300MB free disk space (for model)

## Installation

### Option 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-boundary-engine.git
cd ai-boundary-engine

# Install the package
pip install -e .

# Verify installation
python verify_setup.py
```

### Option 2: Install from PyPI (Coming Soon)

```bash
pip install ai-boundary-engine
```

## First Steps

### 1. Test the CLI

```bash
# Check a safe query
boundary check "What is photosynthesis?"

# Output:
# Decision: ANSWER
# Confidence: 0.95
# Reasons:
#   • Query appears safe and clear
```

### 2. Test a harmful query

```bash
boundary check "How to make a bomb"

# Output:
# Decision: REFUSE
# Confidence: 0.92
# Reasons:
#   • Request involves illegal weapons or explosives
#   • High similarity to harmful instruction
```

### 3. Test ambiguity detection

```bash
boundary check "How to fix it"

# Output:
# Decision: CLARIFY
# Confidence: 0.88
# Reasons:
#   • missing specific object or subject
#   • contains vague verbs: fix
```

## Python API

### Basic Usage

```python
from boundary_engine import BoundaryEngine

# Create engine
engine = BoundaryEngine()

# Analyze a query
result = engine.analyze("What is machine learning?")

print(result.decision)      # ANSWER
print(result.confidence)    # 0.95
print(result.reasons)       # ['Query appears safe and clear']
```

### Integrate with Your LLM

```python
from boundary_engine import BoundaryEngine, Decision

engine = BoundaryEngine()

def safe_llm_call(user_query):
    # Check safety first
    boundary = engine.analyze(user_query)
    
    if boundary.decision == Decision.REFUSE:
        return f"Cannot process: {', '.join(boundary.reasons)}"
    
    if boundary.decision == Decision.CLARIFY:
        return f"Please clarify: {', '.join(boundary.reasons)}"
    
    # Safe to proceed with LLM
    return your_llm.complete(user_query)
```

## Run Examples

### View All Examples

```bash
python examples/usage_examples.py
```

### Interactive Demo

```bash
python examples/demo.py
```

This runs an interactive demo showing:
- Basic safety checks
- Ambiguity detection
- Intent analysis
- Custom rules
- Batch processing
- LLM integration

## Common Use Cases

### 1. Content Moderation

```python
from boundary_engine import BoundaryEngine, Decision

engine = BoundaryEngine()

def moderate_content(text):
    result = engine.analyze(text)
    return result.decision != Decision.REFUSE
```

### 2. Query Validation

```python
def validate_query(query):
    result = engine.analyze(query)
    
    if result.decision == Decision.ANSWER:
        return {"valid": True}
    else:
        return {
            "valid": False,
            "reason": result.reasons[0],
            "confidence": result.confidence
        }
```

### 3. Safety Layer for ChatBot

```python
class SafeChatBot:
    def __init__(self):
        self.engine = BoundaryEngine()
        self.llm = YourLLM()
    
    def chat(self, user_message):
        # Safety check
        boundary = self.engine.analyze(user_message)
        
        if boundary.decision == Decision.REFUSE:
            return "I can't help with that request."
        
        if boundary.decision == Decision.CLARIFY:
            return f"Could you clarify: {boundary.reasons[0]}"
        
        # Safe to use LLM
        return self.llm.generate(user_message)
```

## Customization

### Add Custom Rules

```python
from boundary_engine import BoundaryEngine, Rule, Decision, RiskTag

custom_rule = Rule(
    name="no_spoilers",
    keywords=["spoiler", "ending", "plot twist"],
    decision=Decision.REFUSE,
    severity=0.8,
    reason="Contains spoilers",
    tags=[RiskTag.SAFE]  # Custom categorization
)

engine = BoundaryEngine(custom_rules=[custom_rule])
```

### Add Custom Intents

```python
custom_intents = {
    "marketing_spam": "promotional or advertising content",
    "trolling": "provocative or inflammatory content"
}

engine = BoundaryEngine(custom_intents=custom_intents)
```

### Adjust Sensitivity

```python
from boundary_engine import EngineConfig

# More permissive
config = EngineConfig(
    refuse_threshold=0.85,     # Higher = fewer refusals
    clarify_threshold=0.75,
    rule_sensitivity="low"
)

engine = BoundaryEngine(config=config)
```

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=boundary_engine --cov-report=html

# View coverage
open htmlcov/index.html
```

### Add Your Own Tests

```python
# tests/test_my_cases.py
from boundary_engine import BoundaryEngine, Decision

def test_my_specific_case():
    engine = BoundaryEngine()
    result = engine.analyze("your test query")
    assert result.decision == Decision.ANSWER
```

## Troubleshooting

### Model Download Issues

If the embedding model fails to download:

```python
# Manual download
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Import Errors

If you get import errors:

```bash
# Reinstall in editable mode
pip install -e .
```

### Slow Performance

First query is slower due to model loading. Subsequent queries are fast:

```python
# Warm up the model
engine = BoundaryEngine()
engine.analyze("test")  # First call loads model

# Now fast
engine.analyze("real query")  # ~50ms
```

## Next Steps

1. **Read the docs**:
   - [README.md](README.md) - Full documentation
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Detailed guide

2. **Customize for your use case**:
   - Add domain-specific rules
   - Tune thresholds
   - Add custom intents

3. **Integrate**:
   - Add to your LLM pipeline
   - Deploy as API server
   - Use in production

4. **Contribute**:
   - Report issues
   - Add safety rules
   - Improve documentation

## Help & Support

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions, share use cases
- **Documentation**: Check the docs folder
- **Email**: Contact maintainers

## What's Next?

Check out:
- `examples/usage_examples.py` - Comprehensive examples
- `examples/demo.py` - Interactive demo
- `tests/` - Test suite for reference
- `CONTRIBUTING.md` - How to contribute

---

**Ready to build safer AI systems? Let's go! 🚀**
