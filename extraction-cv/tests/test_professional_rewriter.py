
import pytest

from correction.professional_rewriter import rewrite_text
from correction.mock_rewriter import MockRewriterProvider


def test_rewrite_returns_suggestion():
    text = "J'ai travaillé sur un projet Python."

    provider = MockRewriterProvider()

    result = rewrite_text(text, "fr", provider)

    assert len(result) == 1
    assert result[0]["original"] == text
    assert result[0]["rewritten"]
    assert result[0]["explanation"]


def test_original_text_is_not_modified():
    text = "J'ai travaillé sur un projet Python."

    provider = MockRewriterProvider()

    rewrite_text(text, "fr", provider)

    assert text == "J'ai travaillé sur un projet Python."


def test_empty_text_raises_error():
    provider = MockRewriterProvider()

    with pytest.raises(ValueError):
        rewrite_text("", "fr", provider)


def test_unsupported_language_raises_error():
    provider = MockRewriterProvider()

    with pytest.raises(ValueError):
        rewrite_text("Some text", "es", provider)
