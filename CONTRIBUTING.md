# Contributing to AI Boundary Engine

Thank you for your interest in contributing! This project aims to build transparent, community-driven AI safety intelligence.

## 🎯 Areas for Contribution

### 1. Safety Rules
Add new safety rules in `src/boundary_engine/rules.py`:

```python
Rule(
    name="your_rule_name",
    keywords=["keyword1", "keyword2"],
    decision=Decision.REFUSE,  # or CLARIFY
    severity=0.9,
    reason="Human-readable reason",
    tags=[RiskTag.ILLEGAL]
)
```

### 2. Intent Categories
Add new intent categories in `src/boundary_engine/embeddings.py`:

```python
"your_intent_name": "description of the harmful or problematic intent"
```

### 3. Language Support
Help extend the engine to support non-English queries.

### 4. Performance Optimizations
- Improve embedding model selection
- Optimize batch processing
- Add caching layers

### 5. Documentation
- Improve examples
- Add tutorials
- Write integration guides

## 🔧 Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-boundary-engine.git
cd ai-boundary-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
black src/ tests/
ruff check src/ tests/
```

## 📝 Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/amazing-feature`
3. **Make your changes** with clear commit messages
4. **Add tests** for new functionality
5. **Run tests** to ensure everything passes
6. **Update documentation** if needed
7. **Submit a PR** with a clear description

## ✅ Code Standards

- Use **type hints** for all function signatures
- Follow **PEP 8** style guide
- Write **docstrings** for all public functions
- Add **tests** for new features
- Keep functions **focused and small**

## 🧪 Testing Guidelines

All new features should include tests:

```python
def test_new_feature():
    """Test description."""
    engine = BoundaryEngine()
    result = engine.analyze("test query")
    assert result.decision == Decision.ANSWER
```

Run tests with:
```bash
pytest tests/ -v --cov=boundary_engine
```

## 🤝 Code Review

All contributions will be reviewed for:
- **Correctness**: Does it work as intended?
- **Safety**: Does it improve safety without false positives?
- **Performance**: Is it efficient?
- **Documentation**: Is it well-documented?

## 🐛 Bug Reports

Use GitHub Issues with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- System information

## 💡 Feature Requests

Open an issue with:
- Use case description
- Proposed solution
- Alternatives considered

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

All contributors will be acknowledged in the README and release notes.

---

**Questions?** Open a discussion on GitHub or reach out to the maintainers.
