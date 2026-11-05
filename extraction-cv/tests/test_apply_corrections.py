
import pytest

from correction.apply_corrections import apply_accepted_corrections


def test_apply_accepted_correction():
    text = "Je suis étudiant."

    corrections = [
        {
            "id": "grammar-1",
            "original": "étudiant",
            "suggestions": ["développeur"],
            "offset": 8,
            "length": 8,
        }
    ]

    result = apply_accepted_corrections(
        text,
        corrections,
        {"grammar-1": "développeur"}
    )

    assert result == "Je suis développeur."
    assert text == "Je suis étudiant."


def test_rejected_correction_is_not_applied():
    text = "Je suis un étudiant."

    corrections = [
        {
            "id": "grammar-1",
            "original": "étudiant",
            "suggestions": ["étudiante"],
            "offset": 11,
            "length": 8,
        }
    ]

    result = apply_accepted_corrections(
        text,
        corrections,
        {}
    )

    assert result == text


def test_invalid_suggestion_raises_error():
    text = "Je suis un étudiant."

    corrections = [
        {
            "id": "grammar-1",
            "original": "étudiant",
            "suggestions": ["étudiante"],
            "offset": 11,
            "length": 8,
        }
    ]

    with pytest.raises(ValueError):
        apply_accepted_corrections(
            text,
            corrections,
            {"grammar-1": "développeur"}
        )


def test_modified_original_text_raises_error():
    text = "Je suis une étudiante."

    corrections = [
        {
            "id": "grammar-1",
            "original": "étudiant",
            "suggestions": ["étudiante"],
            "offset": 11,
            "length": 8,
        }
    ]

    with pytest.raises(ValueError):
        apply_accepted_corrections(
            text,
            corrections,
            {"grammar-1": "étudiante"}
        )
