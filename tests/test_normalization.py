import pytest

from boundary_engine.engine import BoundaryEngine


def make_engine_without_loading_models():
    # Query normalization is a pure transformation and does not need model setup.
    return object.__new__(BoundaryEngine)


def test_normalization_preserves_non_ascii_query_content():
    engine = make_engine_without_loading_models()
    original = "  你好，世界！  "

    normalized = engine._normalize_query(original)

    assert normalized.text == "你好，世界！"
    assert normalized.original == original
    assert normalized.length == len("你好，世界！")


def test_normalization_applies_nfkc_without_dropping_unicode():
    engine = make_engine_without_loading_models()

    normalized = engine._normalize_query("  Ｈｅｌｌｏ　世界  ")

    assert normalized.text == "Hello 世界"


def test_normalization_rejects_empty_queries():
    engine = make_engine_without_loading_models()

    with pytest.raises(ValueError, match="cannot be empty"):
        engine._normalize_query(" \t\n ")


@pytest.mark.parametrize("query", [None, 123, b"hello"])
def test_normalization_rejects_non_string_queries(query):
    engine = make_engine_without_loading_models()

    with pytest.raises(TypeError, match="must be a string"):
        engine._normalize_query(query)
