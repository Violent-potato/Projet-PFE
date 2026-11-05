
from typing import Any


class MockRewriterProvider:
    """
    Fournisseur fictif utilisé uniquement pour les tests.
    Il simule les réponses d'un moteur de reformulation IA.
    """

    def rewrite(
        self,
        text: str,
        language: str
    ) -> list[dict[str, Any]]:

        if language == "fr":
            rewritten = (
                "Réalisation d'un projet en Python "
                "portant sur l'analyse de données."
            )
            explanation = (
                "Formulation plus concise et professionnelle, "
                "adaptée à un CV."
            )
        else:
            rewritten = (
                "Developed a Python project focused on data analysis."
            )
            explanation = (
                "A more concise and professional formulation "
                "for a CV."
            )

        return [
            {
                "original": text,
                "rewritten": rewritten,
                "explanation": explanation
            }
        ]
