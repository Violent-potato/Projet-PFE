from io import BytesIO
from pathlib import Path

import pymupdf
from docx import Document


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mo

 
class ExtractionError(Exception):
    """Erreur contrôlée lors de l'extraction d'un CV."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def extract_pdf(content: bytes) -> tuple[str, int]:
    try:
        with pymupdf.open(stream=content, filetype="pdf") as pdf:
            if pdf.needs_pass:
                raise ExtractionError(
                    "PDF_PASSWORD_PROTECTED",
                    "Ce PDF est protégé par un mot de passe."
                )

            if pdf.page_count == 0:
                raise ExtractionError(
                    "EMPTY_DOCUMENT",
                    "Le PDF ne contient aucune page."
                )

            pages = [
                page.get_text("text", sort=True)
                for page in pdf
            ]

            return "\n\n".join(pages), pdf.page_count

    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(
            "PDF_UNREADABLE",
            "Impossible de lire ce PDF. Vérifiez son intégrité."
        ) from exc


def extract_docx(content: bytes) -> tuple[str, None]:
    try:
        document = Document(BytesIO(content))
        elements = []

        # Paragraphes
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if text:
                elements.append(text)

        # Tableaux
        for table in document.tables:
            for row in table.rows:
                cells = [
                    cell.text.strip().replace("\n", " ")
                    for cell in row.cells
                ]

                if any(cells):
                    elements.append(" | ".join(cells))

        return "\n".join(elements), None

    except Exception as exc:
        raise ExtractionError(
            "DOCX_UNREADABLE",
            "Impossible de lire ce document Word."
        ) from exc


def extract_cv(filename: str, content: bytes) -> dict:
    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        raise ExtractionError(
            "UNSUPPORTED_FORMAT",
            "Format non pris en charge. Importez un PDF ou un DOCX."
        )

    if not content:
        raise ExtractionError(
            "EMPTY_FILE",
            "Le fichier est vide."
        )

    if len(content) > MAX_FILE_SIZE:
        raise ExtractionError(
            "FILE_TOO_LARGE",
            "Le fichier dépasse la taille maximale de 10 Mo."
        )

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ExtractionError(
                "INVALID_PDF",
                "Le contenu du fichier n'est pas un PDF valide."
            )

        text, page_count = extract_pdf(content)

    else:
        if not content.startswith(b"PK"):
            raise ExtractionError(
                "INVALID_DOCX",
                "Le contenu du fichier n'est pas un DOCX valide."
            )

        text, page_count = extract_docx(content)

    # Nettoyage du texte extrait
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)

    warnings = []

    if not text:
        warnings.append(
            "Aucun texte extractible. Le document est peut-être scanné."
        )

    return {
        "status": "success",
        "filename": Path(filename).name,
        "format": extension[1:].upper(),
        "page_count": page_count,
        "text": text,
        "character_count": len(text),
        "warnings": warnings,
    }