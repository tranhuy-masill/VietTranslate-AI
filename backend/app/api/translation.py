
import logging

from fastapi import APIRouter, HTTPException, Request

from backend.app.schemas.translation import (
    TranslationRequest,
    TranslationResponse
)


router = APIRouter(prefix="/api")

logger = logging.getLogger(__name__)


@router.get("/health", tags=["System"])
def health_check(request: Request):

    return {
        "status": "healthy",
        "service": "VietTranslate AI",
        "model_loaded": hasattr(
            request.app.state,
            "translation_service"
        )
    }


@router.get("/model", tags=["Model"])
def model_info(request: Request):

    service = request.app.state.translation_service

    return service.get_model_info()


@router.post(
    "/translate",
    response_model=TranslationResponse,
    tags=["Translation"]
)
def translate(
    payload: TranslationRequest,
    request: Request
):

    service = request.app.state.translation_service

    try:

        return service.translate(
            text=payload.text,
            beam_size=payload.beam_size,
            max_new_tokens=payload.max_new_tokens
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        logger.exception("Translation failed")

        raise HTTPException(
            status_code=500,
            detail="Internal translation error."
        )
