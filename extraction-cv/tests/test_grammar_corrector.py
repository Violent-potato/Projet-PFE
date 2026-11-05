
import pytest

from correction.grammar_corrector import GrammarCorrector


class FakeMatch:
    offset = 4
    error_length = 5
    rule_id = "TEST_RULE"
    message = "Erreur de test."
    replacements = ["bonjour"]

    category = None


class FakeTool:
    def check(self, text):
        return [FakeMatch()]

    def close(self):
        pass


def test_check_text_returns_suggestions():
    corrector = GrammarCorrector.__new__(GrammarCorrector)
    corrector.tool = FakeTool()

    text = "Dite bonjor"

    result = corrector.check_text(text)

    assert len(result) == 1
    assert result[0]["original"] == " bonj"
    assert result[0]["suggestions"] == ["bonjour"]
    assert result[0]["offset"] == 4


def test_empty_text_returns_empty_list():
    corrector = GrammarCorrector.__new__(GrammarCorrector)
    corrector.tool = FakeTool()

    assert corrector.check_text("") == []
    assert corrector.check_text("   ") == []


def test_unsupported_language_raises_error():
    with pytest.raises(ValueError):
        GrammarCorrector("es")
