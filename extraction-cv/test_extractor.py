import pymupdf
import pytest
from docx import Document
from io import BytesIO

from extractor import extract_cv, ExtractionError


def create_pdf(text="CV de test"):
    buffer = BytesIO()

    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((50, 50), text)
        pdf.save(buffer)

    return buffer.getvalue()


def create_docx(text="CV de test"):
    buffer = BytesIO()
    document = Document()
    document.add_paragraph(text)
    document.save(buffer)
    return buffer.getvalue()


def test_extract_pdf():
    result = extract_cv("cv.pdf", create_pdf())

    assert result["format"] == "PDF"
    assert "CV de test" in result["text"]
    assert result["page_count"] == 1


def test_extract_docx():
    result = extract_cv("cv.docx", create_docx())

    assert result["format"] == "DOCX"
    assert "CV de test" in result["text"]


def test_unsupported_format():
    with pytest.raises(ExtractionError) as error:
        extract_cv("cv.txt", b"test")

    assert error.value.code == "UNSUPPORTED_FORMAT"


def test_empty_file():
    with pytest.raises(ExtractionError) as error:
        extract_cv("cv.pdf", b"")

    assert error.value.code == "EMPTY_FILE"


def test_invalid_pdf():
    with pytest.raises(ExtractionError) as error:
        extract_cv("cv.pdf", b"ceci n'est pas un PDF")

    assert error.value.code == "INVALID_PDF"


def test_file_too_large():
    content = b"a" * (10 * 1024 * 1024 + 1)

    with pytest.raises(ExtractionError) as error:
        extract_cv("cv.pdf", content)

    assert error.value.code == "FILE_TOO_LARGE"