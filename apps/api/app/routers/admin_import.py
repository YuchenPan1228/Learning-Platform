from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.dependencies import AIProviderDep, SessionDep
from app.models.enums import ExtractedObjectType
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfImportCreate,
    QuestionImportCreate,
    ResourceImportRead,
    UrlImportCreate,
)
from app.services import admin_import as admin_import_service
from app.services.admin_import import ImportExtractionError, ImportPolicyError
from app.services.import_topic_validation import ImportTopicError
from app.services.pdf_upload import PdfUploadError

router = APIRouter(prefix="/admin/import", tags=["admin-import"])


@router.post("/url")
def import_url(
    payload: UrlImportCreate,
    session: SessionDep,
    provider: AIProviderDep,
) -> ResourceImportRead:
    try:
        return admin_import_service.import_url_resource(session, payload, provider=provider)
    except ImportTopicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportPolicyError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ImportExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/note")
def import_note(
    payload: NoteImportCreate,
    session: SessionDep,
    provider: AIProviderDep,
) -> ResourceImportRead:
    try:
        return admin_import_service.import_note_resource(session, payload, provider=provider)
    except ImportTopicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportPolicyError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ImportExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/question")
def import_question(payload: QuestionImportCreate, session: SessionDep) -> ResourceImportRead:
    try:
        return admin_import_service.import_question_resource(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportTopicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/pdf")
async def import_pdf(
    session: SessionDep,
    provider: AIProviderDep,
    file: Annotated[UploadFile, File()],
    topic_slug: Annotated[str, Form()],
    object_type: Annotated[ExtractedObjectType, Form()] = ExtractedObjectType.QUESTION,
    title: Annotated[str | None, Form()] = None,
    subtopic_slug: Annotated[str | None, Form()] = None,
    summary: Annotated[str | None, Form()] = None,
) -> ResourceImportRead:
    try:
        payload = PdfImportCreate(
            title=title,
            summary=summary,
            topic_slug=topic_slug,
            subtopic_slug=subtopic_slug,
            object_type=object_type,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    content = await file.read()
    try:
        return admin_import_service.import_pdf_resource(
            session,
            payload,
            provider=provider,
            filename=file.filename,
            content_type=file.content_type,
            content=content,
        )
    except ImportTopicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportPolicyError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ImportExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PdfUploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
