from io import BytesIO

import pymupdf
import pytest
from docx import Document
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def create_pdf(text: str = "CV de test") -> bytes:
    buffer = BytesIO()
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((50, 50), text)
        pdf.save(buffer)
    return buffer.getvalue()


def create_docx(text: str = "CV de test") -> bytes:
    buffer = BytesIO()
    document = Document()
    document.add_paragraph(text)
    document.save(buffer)
    return buffer.getvalue()


@pytest.mark.parametrize(
    ("filename", "content", "expected_format"),
    [
        ("cv.pdf", create_pdf(), "PDF"),
        ("cv.docx", create_docx(), "DOCX"),
    ],
)
def test_upload_returns_extractor_result(filename, content, expected_format):
    response = client.post(
        "/cv/upload",
        files={"file": (filename, content)},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["format"] == expected_format
    assert "CV de test" in result["text"]
    assert result["character_count"] == len(result["text"])
    assert result["warnings"] == []


@pytest.mark.parametrize(
    ("filename", "content", "expected_status"),
    [
        ("cv.txt", b"texte", 400),
        ("cv.pdf", b"not a pdf", 400),
        ("cv.pdf", b"", 400),
        ("cv.pdf", b"x" * (10 * 1024 * 1024 + 1), 413),
    ],
)
def test_upload_returns_extraction_errors(filename, content, expected_status):
    response = client.post(
        "/cv/upload",
        files={"file": (filename, content)},
    )

    assert response.status_code == expected_status
    assert response.json()["detail"]


def test_upload_rejects_document_without_extractable_text():
    response = client.post(
        "/cv/upload",
        files={"file": ("cv.pdf", create_pdf(""))},
    )

    assert response.status_code == 422
    assert "Aucun texte" in response.json()["detail"]
