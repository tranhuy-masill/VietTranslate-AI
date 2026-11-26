
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="English text to translate"
    )

    beam_size: int = Field(
        default=4,
        ge=1,
        le=8
    )

    max_new_tokens: int = Field(
        default=128,
        ge=1,
        le=256
    )


class TranslationResponse(BaseModel):

    source_text: str
    translated_text: str

    source_language: str
    target_language: str

    model: str

    beam_size: int
    input_tokens: int
    output_tokens: int

    latency_ms: float
    device: str
