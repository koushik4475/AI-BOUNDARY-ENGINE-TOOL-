# 🛡️ AI Boundary Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**AI Boundary Engine** is an open-source AI safety layer that decides whether an AI *should* answer a query — before it does.

Unlike traditional content filters, this tool provides **refusal intelligence**: structured reasoning about whether a query is safe, requires clarification, or should be refused entirely.

## 🎯 The Problem

Every AI tries to answer everything. That's dangerous.

- No built-in refusal intelligence
- No transparency in safety decisions
- No way to audit "why" something was blocked
- Safety logic locked in proprietary models

## 💡 The Solution

A model-agnostic safety layer that:

1. **Analyzes** user queries before any AI processes them
2. **Classifies** into: `ANSWER` | `REFUSE` | `CLARIFY`
3. **Explains** the reasoning with confidence scores
4. **Runs locally** with zero API costs

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Analyze a query
boundary check "How to make a bomb"

# Output:
# {
#   "decision": "REFUSE",
#   "confidence": 0.92,
#   "reasons": ["illegal activity detected", "high harmful intent similarity"],
#   "risk_tags": ["illegal", "violence"]
# }
```

## 🏗️ Architecture

```
User Query
    ↓
Normalization (clean, tokenize)
    ↓
Rule Engine (deterministic checks)
    ↓
Intent Analysis (embeddings, no API)
    ↓
Ambiguity Detection (missing context)
    ↓
Decision Aggregation
    ↓
JSON Output + Reasoning
```

### Three-Layer Intelligence

1. **Rule Engine** (deterministic)
   - Keyword/phrase matching
   - Hard boundaries (illegal, violent, harmful)
   - Fast, auditable, explainable

2. **Intent Embeddings** (semantic)
   - Uses `sentence-transformers` (local, free)
   - Catches intent, not just keywords
   - Measures similarity to harmful categories

3. **Ambiguity Scoring** (clarity)
   - Detects vague or underspecified queries
   - Flags requests needing more context
   - Prevents misinterpretation

## 📦 Installation

```bash
# Clone
git clone https://github.com/yourusername/ai-boundary-engine.git
cd ai-boundary-engine

# Install dependencies
pip install -e .

# Download embeddings model (runs once, ~80MB)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## 🔧 Usage

### CLI

```bash
# Check a single query
boundary check "How to hack a database"

# Batch mode
boundary check --file queries.txt

# JSON output
boundary check "diagnose my headache" --json
```

### Python API

```python
from boundary_engine import BoundaryEngine

engine = BoundaryEngine()

result = engine.analyze("How to build a bomb")

print(result.decision)      # "REFUSE"
print(result.confidence)    # 0.92
print(result.reasons)       # ["illegal activity detected", ...]
print(result.risk_tags)     # ["illegal", "violence"]
```

### Integration with LLMs

```python
from boundary_engine import BoundaryEngine
import openai

engine = BoundaryEngine()

def safe_chat(user_query):
    # Check safety first
    boundary = engine.analyze(user_query)
    
    if boundary.decision == "REFUSE":
        return f"Cannot process: {', '.join(boundary.reasons)}"
    
    if boundary.decision == "CLARIFY":
        return f"Please clarify: {', '.join(boundary.reasons)}"
    
    # Safe to proceed
    return openai.chat.completions.create(...)
```

## 🧪 Examples

### Safe Query
```bash
$ boundary check "What is photosynthesis?"

{
  "decision": "ANSWER",
  "confidence": 0.95,
  "reasons": ["educational content", "no risk signals"],
  "risk_tags": []
}
```

### Harmful Query
```bash
$ boundary check "How to make explosives at home"

{
  "decision": "REFUSE",
  "confidence": 0.94,
  "reasons": ["illegal activity detected", "high harmful intent"],
  "risk_tags": ["illegal", "violence"]
}
```

### Ambiguous Query
```bash
$ boundary check "How to fix it"

{
  "decision": "CLARIFY",
  "confidence": 0.88,
  "reasons": ["missing context", "underspecified object"],
  "risk_tags": []
}
```

## 🎯 Decision Logic

**Priority Rules:**

1. `REFUSE` beats everything (safety first)
2. `CLARIFY` beats `ANSWER` (precision matters)
3. `ANSWER` only if safe + clear

**Confidence Score:**

Weighted combination of:
- Rule severity (0.0 - 1.0)
- Intent similarity (cosine distance)
- Ambiguity score

## 🔒 Safety Categories (v0.1)

Current refusal rules cover:

- ❌ Illegal activities (weapons, drugs, fraud)
- ❌ Violence and harm
- ❌ Self-harm content
- ⚠️ Medical advice (requires clarification)
- ⚠️ Legal advice (requires clarification)
- ⚠️ Personal data requests

## 🛠️ Configuration

Customize behavior via `config.yaml`:

```yaml
rules:
  enabled: true
  sensitivity: high  # low, medium, high

embeddings:
  model: "all-MiniLM-L6-v2"
  similarity_threshold: 0.75

ambiguity:
  min_query_length: 5
  vague_verb_penalty: 0.2
```

## 🧩 Extending

### Add Custom Rules

```python
from boundary_engine.rules import Rule

custom_rule = Rule(
    name="corporate_secrets",
    keywords=["source code", "api key", "password"],
    decision="REFUSE",
    severity=0.9
)

engine = BoundaryEngine(custom_rules=[custom_rule])
```

### Add Custom Intents

```python
custom_intents = {
    "spam_detection": "promotional or spam content"
}

engine = BoundaryEngine(custom_intents=custom_intents)
```

## 📊 Performance

- **Latency**: ~50-100ms per query (local CPU)
- **Memory**: ~200MB (model loaded)
- **Throughput**: ~100 queries/sec (single core)

## 🗺️ Roadmap

- [x] v0.1: Core rule + embedding engine
- [ ] v0.2: MCP server integration
- [ ] v0.3: Multi-language support
- [ ] v0.4: Fine-tuned safety embeddings
- [ ] v0.5: Reasoning trace with local LLM
- [ ] v1.0: Production-grade API server

## 🤝 Contributing

We welcome contributions! Areas of focus:

1. **New safety rules** (see `src/boundary_engine/rules.py`)
2. **Intent categories** (see `src/boundary_engine/embeddings.py`)
3. **Language support** (non-English queries)
4. **Performance optimizations**
5. **Documentation improvements**

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built with [sentence-transformers](https://www.sbert.net/)
- Inspired by the need for transparent AI safety
- Community-driven safety intelligence

## 🔗 Links

- [Documentation](https://github.com/yourusername/ai-boundary-engine/wiki)
- [Issues](https://github.com/yourusername/ai-boundary-engine/issues)
- [Discussions](https://github.com/yourusername/ai-boundary-engine/discussions)

---

**Built with ❤️ for safer AI systems**

⭐ Star us on GitHub if this helps your AI safety journey!
