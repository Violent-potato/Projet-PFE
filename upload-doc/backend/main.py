
import sys
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware


EXTRACTION_PATH = Path(__file__).resolve().parents[2] / "extraction-cv"
sys.path.insert(0, str(EXTRACTION_PATH))

from extractor import ExtractionError, extract_cv

app = FastAPI(title="CV Analysis API")

# Autoriser le frontend React en développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/cv/upload")
async def upload_cv(file: UploadFile = File(...)):
    filename = file.filename or ""
    content = await file.read()

    try:
        result = extract_cv(filename, content)
    except ExtractionError as error:
        status_code = 413 if error.code == "FILE_TOO_LARGE" else 400
        raise HTTPException(status_code=status_code, detail=error.message) from error

    if not result["text"]:
        raise HTTPException(
            status_code=422,
            detail=result["warnings"][0],
        )

    return result
