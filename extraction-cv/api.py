
from contextlib import asynccontextmanager
from threading import RLock
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel, Field

from correction.grammar_corrector import GrammarCorrector
from correction.apply_corrections import apply_accepted_corrections
from correction.professional_rewriter import rewrite_text
from correction.mock_rewriter import MockRewriterProvider
from extractor import extract_cv, ExtractionError
from fastapi.middleware.cors import CORSMiddleware


# --------------------------------------------------
# Modèles des données échangées avec le frontend
# --------------------------------------------------

class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    language: Literal["fr", "en"] = "fr"


class CorrectionItem(BaseModel):
    id: str
    original: str
    suggestions: list[str]
    offset: int
    length: int


class ApplyCorrectionsRequest(BaseModel):
    original_text: str
    corrections: list[CorrectionItem]
    accepted_suggestions: dict[str, str]


# --------------------------------------------------
# Gestion du cycle de vie de l'API
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Les moteurs seront créés à la première utilisation.
    app.state.grammar_correctors = {}
    app.state.grammar_lock = RLock()

    yield

    # Fermeture propre des moteurs à l'arrêt de l'API.
    with app.state.grammar_lock:
        for corrector in app.state.grammar_correctors.values():
            corrector.close()

        app.state.grammar_correctors.clear()


app = FastAPI(
    title="CV Correction API",
    description="API de correction grammaticale et de reformulation professionnelle.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Endpoint de vérification
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "L'API fonctionne correctement."
    }


# --------------------------------------------------
# Correction grammaticale
# --------------------------------------------------

@app.post("/correction/grammar")
def grammar_correction(data: TextRequest, request: Request):
    try:
        with request.app.state.grammar_lock:
            correctors = request.app.state.grammar_correctors

            if data.language not in correctors:
                correctors[data.language] = GrammarCorrector(
                    data.language
                )

            corrector = correctors[data.language]

            corrections = corrector.check_text(data.text)

        return {
            "original_text": data.text,
            "language": data.language,
            "correction_count": len(corrections),
            "corrections": corrections,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la correction grammaticale : {error}"
        )


# --------------------------------------------------
# Application des corrections acceptées
# --------------------------------------------------

@app.post("/correction/apply")
def apply_corrections(data: ApplyCorrectionsRequest):

    corrections = [
        correction.model_dump()
        for correction in data.corrections
    ]

    try:
        corrected_text = apply_accepted_corrections(
            data.original_text,
            corrections,
            data.accepted_suggestions,
        )

        return {
            "original_text": data.original_text,
            "corrected_text": corrected_text,
        }

    except (ValueError, KeyError, TypeError) as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )


# --------------------------------------------------
# Reformulation professionnelle
# --------------------------------------------------

@app.post("/correction/rewrite")
def professional_rewriting(data: TextRequest):

    try:
        # Fournisseur fictif temporaire.
        # Il sera remplacé lorsque l'équipe aura choisi son IA.
        provider = MockRewriterProvider()

        suggestions = rewrite_text(
            data.text,
            data.language,
            provider,
        )

        return {
            "original_text": data.text,
            "language": data.language,
            "suggestions": suggestions,
        }

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )



# --------------------------------------------------
# Import et analyse complète d'un CV
# --------------------------------------------------

@app.post("/cv/analyze")
async def analyze_cv(
    request: Request,
    file: UploadFile = File(...),
    language: Literal["fr", "en"] = Form("fr"),
):
    try:
        # Lecture du fichier envoyé
        content = await file.read()

        # Extraction du texte
        extraction = extract_cv(
            file.filename or "cv",
            content
        )

        text = extraction["text"]

        # Si aucun texte n'est extrait (PDF scanné par exemple)
        if not text.strip():
            return {
                **extraction,
                "language": language,
                "correction_count": 0,
                "corrections": [],
            }

        # Correction grammaticale
        with request.app.state.grammar_lock:
            correctors = request.app.state.grammar_correctors

            if language not in correctors:
                correctors[language] = GrammarCorrector(language)

            corrector = correctors[language]
            corrections = corrector.check_text(text)

        return {
            **extraction,
            "language": language,
            "correction_count": len(corrections),
            "corrections": corrections,
        }

    except ExtractionError as error:
        raise HTTPException(
            status_code=400,
            detail={
                "code": error.code,
                "message": error.message,
            }
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du CV : {error}"
        )
