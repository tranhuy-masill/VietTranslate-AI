
from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.app.api.document import router as document_router
from backend.app.api.translation import router
from backend.app.services.translation_service import (
    TranslationService
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting VietTranslate AI Backend...")

    app.state.translation_service = TranslationService()

    print("AI Model is ready!")

    yield

    print("Shutting down Backend...")


app = FastAPI(
    title="VietTranslate AI API",
    description=(
        "English-Vietnamese Neural Machine Translation "
        "using MarianMT SwitchOut p=0.02"
    ),
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(router)
app.include_router(document_router)

@app.get("/", tags=["System"])
def root():

    return {
        "platform": "VietTranslate AI",
        "version": "1.0.0",
        "status": "running",
        "model": "MarianMT SwitchOut p=0.02",
        "documentation": "/docs"
    }
