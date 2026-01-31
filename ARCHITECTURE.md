# Architecture Documentation

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                   BoundaryEngine                        │
│                  (Main Orchestrator)                    │
└──────────────┬──────────────────────────────────────────┘
               │
               ├──► Normalization Layer
               │    └─► Clean & standardize input
               │
               ├──► Analysis Layer (Parallel)
               │    ├─► RuleEngine
               │    │   └─► Keyword/pattern matching
               │    ├─► EmbeddingAnalyzer
               │    │   └─► Semantic intent analysis
               │    └─► AmbiguityDetector
               │        └─► Context completeness check
               │
               └──► Decision Layer
                    └─► DecisionAggregator
                        └─► Combine signals → Final decision
```

---

## 📦 Component Details

### 1. BoundaryEngine (Orchestrator)

**File**: `src/boundary_engine/engine.py`

**Responsibility**: Main entry point that coordinates all analysis

**Key Methods**:
- `analyze(query: str) -> DecisionResult`
- `batch_analyze(queries: List[str]) -> List[DecisionResult]`
- `add_rule(rule: Rule)` - Add custom safety rules
- `add_intent(name: str, description: str)` - Add custom intents

**Data Flow**:
```python
User Query → normalize() → [Rules, Embeddings, Ambiguity] → aggregate() → Result
```

---

### 2. RuleEngine (Deterministic Safety)

**File**: `src/boundary_engine/rules.py`

**Responsibility**: Fast, explainable safety checks via keyword/pattern matching

**Why It Exists**:
- **Speed**: Instant checks (< 1ms)
- **Transparency**: Easy to audit
- **Determinism**: Same input = same output
- **Explainability**: Clear reasons for decisions

**Algorithm**:
```python
for each rule:
    if keywords match OR patterns match:
        return RuleMatch(
            rule_name=rule.name,
            decision=rule.decision,
            confidence=rule.severity,
            matched_keywords=[...]
        )
```

**Default Rules** (v0.1):
1. `illegal_weapons` - Explosives, bombs, weapons
2. `illegal_drugs` - Drug synthesis, precursors
3. `hacking_malicious` - System intrusion, exploits
4. `violence_harm` - Physical harm instructions
5. `self_harm` - Suicide, self-injury
6. `fraud_identity` - Fake IDs, scams
7. `medical_advice` - Diagnosis, treatment (CLARIFY)
8. `legal_advice` - Legal judgments (CLARIFY)
9. `personal_data_request` - Passwords, keys
10. `child_safety` - CSAM, child exploitation

**Performance**: O(n * m) where n=queries, m=rules (very fast)

---

### 3. EmbeddingAnalyzer (Semantic Understanding)

**File**: `src/boundary_engine/embeddings.py`

**Responsibility**: Understand query intent via semantic similarity

**Why It Exists**:
Rules catch keywords, embeddings catch **meaning**

Example:
- Rule might miss: "How to create an incendiary device"
- Embedding catches it: High similarity to "harmful_instruction"

**Technology**:
- **Model**: `all-MiniLM-L6-v2` (sentence-transformers)
- **Size**: ~80MB
- **Speed**: ~50ms per query
- **Runs**: 100% locally, no API

**Algorithm**:
```python
1. Precompute embeddings for all intent categories (done once)
2. For each query:
   a. Embed query → vector
   b. Compute cosine similarity to each intent
   c. Return top matches above threshold
```

**Intent Categories** (v0.1):
- `harmful_instruction` - Physical harm
- `illegal_activity` - Crimes, fraud
- `personal_data_breach` - Privacy violations
- `self_harm_content` - Self-injury
- `manipulation_deception` - Scams
- `medical_diagnosis` - Medical advice
- `legal_judgment` - Legal advice
- `ambiguous_request` - Vague queries
- `safe_educational` - Learning content
- `safe_general` - Normal conversation

**Performance**: O(d) where d=embedding dimensions (384)

---

### 4. AmbiguityDetector (Clarity Check)

**File**: `src/boundary_engine/ambiguity.py`

**Responsibility**: Detect queries needing clarification

**Why It Exists**:
- Prevent misinterpretation
- Force users to be specific
- Avoid hallucinated answers

**Signals**:
1. **Length**: Too short (< 5 chars)
2. **Vague verbs**: "explain", "fix", "help", "do"
3. **Unclear pronouns**: "it", "this", "that"
4. **Missing object**: "How to fix" (fix what?)
5. **Context-dependent**: "my file", "this code"
6. **Multiple interpretations**: "or" questions

**Algorithm**:
```python
score = 0.0

if len(query) < min_length:
    score += 0.3

vague_verbs = count_vague_verbs(query)
score += vague_verbs * vague_verb_penalty

unclear_pronouns = count_unclear_pronouns(query)
score += unclear_pronouns * pronoun_penalty

if score > 0.4:
    is_ambiguous = True
```

**Performance**: O(n) where n=query length

---

### 5. DecisionAggregator (Final Decision)

**File**: `src/boundary_engine/decision.py`

**Responsibility**: Combine all signals into final decision

**Decision Priority** (Critical!):
```
1. REFUSE beats everything (safety first)
2. CLARIFY beats ANSWER (precision matters)
3. ANSWER only if safe + clear
```

**Confidence Calculation**:
```python
refuse_confidence = (
    rule_weight * max_rule_severity +
    intent_weight * max_harmful_intent_similarity
)

clarify_confidence = (
    signal_count * 0.3 +
    ambiguity_score * 0.4
)

if refuse_confidence >= refuse_threshold:
    decision = REFUSE
elif clarify_confidence >= clarify_threshold:
    decision = CLARIFY
else:
    decision = ANSWER
```

**Weights** (tunable):
- `rule_weight`: 0.6 (high trust in rules)
- `intent_weight`: 0.4 (supplement with semantics)

**Thresholds** (tunable):
- `refuse_threshold`: 0.7 (conservative)
- `clarify_threshold`: 0.6 (ask when unsure)

---

## 🔄 Complete Request Flow

### Example: "How to make a bomb"

```
1. Input: "How to make a bomb"

2. Normalization:
   ├─► Lowercase: "how to make a bomb"
   ├─► Strip: No extra whitespace
   └─► Output: NormalizedQuery(text="how to make a bomb", length=18, tokens=5)

3. Rule Engine:
   ├─► Check: "illegal_weapons" rule
   ├─► Match: "bomb" keyword found
   └─► Output: RuleMatch(
           rule_name="illegal_weapons",
           decision=REFUSE,
           confidence=0.95,
           matched_keywords=["bomb"]
       )

4. Embedding Analyzer:
   ├─► Embed query: [0.12, -0.45, ..., 0.78]  (384 dims)
   ├─► Compare to intents
   ├─► Top match: "harmful_instruction" (similarity=0.89)
   └─► Output: IntentScore(
           intent="harmful_instruction",
           similarity=0.89
       )

5. Ambiguity Detector:
   ├─► Length: 18 chars ✓ (not too short)
   ├─► Vague verbs: "make" found (penalty=0.2)
   ├─► Context: Clear enough
   └─► Output: AmbiguityResult(
           is_ambiguous=False,
           score=0.2
       )

6. Decision Aggregator:
   ├─► Refuse signals: ["rule:illegal_weapons", "intent:harmful_instruction"]
   ├─► Calculate: refuse_confidence = 0.6*0.95 + 0.4*0.89 = 0.926
   ├─► Check: 0.926 > refuse_threshold (0.7) ✓
   └─► Output: DecisionResult(
           decision=REFUSE,
           confidence=0.92,
           reasons=["Request involves illegal weapons or explosives",
                    "High similarity to harmful instruction"],
           risk_tags=[ILLEGAL, VIOLENCE]
       )

7. Return to user
```

---

## ⚙️ Configuration & Tuning

### Sensitivity Levels

**Low** (permissive):
- `refuse_threshold`: 0.85
- `clarify_threshold`: 0.75
- `rule_severity_multiplier`: 0.7

**Medium** (balanced):
- `refuse_threshold`: 0.75
- `clarify_threshold`: 0.65
- `rule_severity_multiplier`: 0.85

**High** (strict):
- `refuse_threshold`: 0.65
- `clarify_threshold`: 0.55
- `rule_severity_multiplier`: 1.0

### Custom Configuration

```python
from boundary_engine import EngineConfig

config = EngineConfig(
    # Rules
    rules_enabled=True,
    rule_sensitivity="high",
    
    # Embeddings
    embedding_model="all-MiniLM-L6-v2",
    similarity_threshold=0.75,
    
    # Ambiguity
    min_query_length=5,
    vague_verb_penalty=0.2,
    
    # Decisions
    refuse_threshold=0.7,
    clarify_threshold=0.6
)
```

---

## 🎯 Design Principles

### 1. **Safety First**
- REFUSE beats all other decisions
- Conservative thresholds by default
- Multiple layers of defense

### 2. **Transparency**
- Every decision is explainable
- Reasoning provided with confidence
- Audit trail via rule matches

### 3. **No External Dependencies**
- Runs 100% locally
- No API calls required
- No data leaves the system

### 4. **Extensibility**
- Easy to add custom rules
- Easy to add custom intents
- Pluggable components

### 5. **Performance**
- Fast enough for real-time (<100ms)
- Batch processing supported
- Cacheable results

---

## 📊 Performance Characteristics

### Latency (Single Query)

| Component | Time | % of Total |
|-----------|------|------------|
| Normalization | <1ms | 1% |
| Rule Engine | 1-2ms | 2% |
| Embedding | 40-60ms | 60% |
| Ambiguity | 1-2ms | 2% |
| Aggregation | <1ms | 1% |
| **Total** | **50-70ms** | **100%** |

### Memory Usage

| Component | Memory |
|-----------|--------|
| Model (all-MiniLM-L6-v2) | ~200MB |
| Intent embeddings | <1MB |
| Rules | <100KB |
| **Total** | **~200MB** |

### Throughput

- **Single core**: ~15 queries/sec
- **Batch (10)**: ~50 queries/sec
- **Multi-core**: Scales linearly

---

## 🔮 Future Architecture

### v0.2 Features
- MCP server integration
- Streaming API
- Result caching

### v0.3 Features
- Multi-language support
- Custom embedding training
- Confidence calibration

### v1.0 Features
- Distributed deployment
- Advanced reasoning traces
- Enterprise audit logs

---

## 🤝 Extension Points

### 1. Custom Rules
Add domain-specific safety rules

### 2. Custom Intents
Add industry-specific intents

### 3. Custom Aggregation
Override decision logic

### 4. Custom Embeddings
Use different models

### 5. Middleware
Add pre/post processing hooks

---

## 📚 Related Documentation

- [README.md](README.md) - Getting started
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Detailed setup
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
