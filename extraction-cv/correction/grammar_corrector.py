
from typing import Any

import language_tool_python


SUPPORTED_LANGUAGES = {
    "fr": "fr",
    "en": "en-US",
}


class GrammarCorrector:
    """Détecte les erreurs grammaticales et propose des corrections."""

    def __init__(self, language: str = "fr"):
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Langue non prise en charge : {language}. "
                f"Langues disponibles : {', '.join(SUPPORTED_LANGUAGES)}"
            )

        self.language = SUPPORTED_LANGUAGES[language]
        self.tool = language_tool_python.LanguageTool(self.language)

    def check_text(self, text: str) -> list[dict[str, Any]]:
        """
        Analyse un texte et retourne les erreurs détectées.
        Le texte original n'est jamais modifié.
        """
        if not isinstance(text, str):
            raise TypeError("Le texte doit être une chaîne de caractères.")

        if not text.strip():
            return []

        matches = self.tool.check(text)
        corrections = []

        for index, match in enumerate(matches, start=1):
            offset = match.offset
            length = match.error_length

            category = getattr(match, "category", None)
            category_name = getattr(category, "name", None)

            original = text[offset:offset + length]

            corrections.append({
                "id": f"grammar-{index}",
                "type": "grammar",
                "category": category_name or "Autre",
                "rule_id": match.rule_id,
                "message": match.message,
                "original": original,
                "suggestions": list(match.replacements),
                "offset": offset,
                "length": length,
            })

        return corrections

    def close(self) -> None:
        """Ferme le moteur LanguageTool."""
        self.tool.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
