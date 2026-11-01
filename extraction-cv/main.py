import sys
from pathlib import Path

from extractor import extract_cv, ExtractionError


def main():
    if len(sys.argv) != 2:
        print("Utilisation : python main.py chemin/vers/cv.pdf")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print(f"Fichier introuvable : {file_path}")
        sys.exit(1)

    try:
        result = extract_cv(
            file_path.name,
            file_path.read_bytes()
        )

        print(f"Fichier : {result['filename']}")
        print(f"Format : {result['format']}")
        print(f"Nombre de pages : {result['page_count']}")
        print(f"Nombre de caractères : {result['character_count']}")

        for warning in result["warnings"]:
            print(f"Avertissement : {warning}")

        print("\n--- TEXTE EXTRAIT ---\n")
        print(result["text"])

    except ExtractionError as error:
        print(f"Erreur [{error.code}] : {error.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()