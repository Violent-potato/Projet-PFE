
from typing import Any


def apply_accepted_corrections(
    original_text: str,
    corrections: list[dict[str, Any]],
    accepted_suggestions: dict[str, str],
) -> str:
    """
    Applique uniquement les corrections acceptées par l'utilisateur.

    accepted_suggestions :
        dictionnaire associant l'identifiant d'une correction
        à la suggestion choisie.

    Exemple :
        {
            "grammar-1": "des opportunités",
            "grammar-2": "intéressantes."
        }
    """

    if not isinstance(original_text, str):
        raise TypeError("Le texte original doit être une chaîne de caractères.")

    selected_changes = []

    for correction in corrections:
        correction_id = correction["id"]

        # Cette correction n'a pas été acceptée.
        if correction_id not in accepted_suggestions:
            continue

        replacement = accepted_suggestions[correction_id]

        # Vérifier que la suggestion choisie a bien été proposée.
        if replacement not in correction["suggestions"]:
            raise ValueError(
                f"La suggestion choisie pour {correction_id} "
                "n'est pas valide."
            )

        offset = correction["offset"]
        length = correction["length"]
        original_fragment = correction["original"]

        # Vérifier que les positions correspondent toujours au texte.
        if original_text[offset:offset + length] != original_fragment:
            raise ValueError(
                f"Le texte a changé à la position de {correction_id}. "
                "Il faut relancer l'analyse."
            )

        selected_changes.append({
            "id": correction_id,
            "offset": offset,
            "length": length,
            "replacement": replacement,
        })

    # Vérifier que les corrections ne se chevauchent pas.
    selected_changes.sort(key=lambda item: item["offset"])

    for previous, current in zip(
        selected_changes, selected_changes[1:]
    ):
        previous_end = previous["offset"] + previous["length"]

        if current["offset"] < previous_end:
            raise ValueError(
                "Certaines corrections acceptées se chevauchent."
            )

    # Appliquer les modifications de droite à gauche
    # pour conserver les positions initiales.
    corrected_text = original_text

    for change in reversed(selected_changes):
        start = change["offset"]
        end = start + change["length"]

        corrected_text = (
            corrected_text[:start]
            + change["replacement"]
            + corrected_text[end:]
        )

    return corrected_text
