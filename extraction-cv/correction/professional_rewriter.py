
from typing import Protocol, Any


class RewriterProvider(Protocol):
    """
    Contrat que devra respecter chaque fournisseur d'IA.
    """

    def rewrite(
        self,
        text: str,
        language: str
    ) -> list[dict[str, Any]]:
        ...


def rewrite_text(
    text: str,
    language: str,
    provider: RewriterProvider
) -> list[dict[str, Any]]:
    """
    Demande des propositions de reformulation au fournisseur d'IA.
    Ne modifie jamais le texte original.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Le texte à reformuler ne peut pas être vide.")

    if language not in ("fr", "en"):
        raise ValueError("Langue non prise en charge.")

    suggestions = provider.rewrite(text, language)

    if not isinstance(suggestions, list):
        raise TypeError("Le fournisseur doit retourner une liste.")

    for suggestion in suggestions:
        required_fields = {
            "original",
            "rewritten",
            "explanation"
        }

        if not isinstance(suggestion, dict):
            raise TypeError("Chaque proposition doit être un dictionnaire.")

        if not required_fields.issubset(suggestion):
            raise ValueError(
                "Une proposition doit contenir : "
                "original, rewritten et explanation."
            )

        if suggestion["original"] != text:
            raise ValueError(
                "Le texte original de la proposition ne correspond pas."
            )

        if not suggestion["rewritten"].strip():
            raise ValueError("La reformulation ne peut pas être vide.")

    return suggestions
