
import logging

from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile, BadZipFile
from io import BytesIO

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Request,
    HTTPException
)

from fastapi.responses import StreamingResponse

from backend.app.services.document_service import (
    DocumentService
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_EXTRACTED_SIZE = 100 * 1024 * 1024


@router.post("/translate")
def translate_document(
    request: Request,
    file: UploadFile = File(...),
    beam_size: int = Form(4)
):

    filename = file.filename or "document.docx"

    if not filename.lower().endswith(".docx"):

        raise HTTPException(
            status_code=400,
            detail="Only .docx files are supported."
        )

    if not 1 <= beam_size <= 8:

        raise HTTPException(
            status_code=400,
            detail="Beam size must be between 1 and 8."
        )

    try:

        content = file.file.read(MAX_FILE_SIZE + 1)

    finally:

        file.file.close()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="File is empty."
        )

    if len(content) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 20 MB."
        )

    try:

        with ZipFile(BytesIO(content)) as archive:

            extracted_size = sum(
                item.file_size
                for item in archive.infolist()
            )

            if extracted_size > MAX_EXTRACTED_SIZE:

                raise HTTPException(
                    status_code=413,
                    detail="Extracted document is too large."
                )

            if "word/document.xml" not in archive.namelist():

                raise HTTPException(
                    status_code=400,
                    detail="Invalid Word document."
                )

    except BadZipFile:

        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted DOCX file."
        )

    try:

        service = DocumentService(
            request.app.state.translation_service
        )

        output = service.translate_document(
            file_bytes=content,
            beam_size=beam_size
        )

        output_filename = (
            Path(filename).stem + "_VI.docx"
        )

        return StreamingResponse(
            output,
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            headers={
                "Content-Disposition":
                    "attachment; filename*=UTF-8''"
                    + quote(output_filename, safe="")
            }
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        logger.exception("Document translation failed")

        raise HTTPException(
            status_code=500,
            detail="Document translation failed."
        )
