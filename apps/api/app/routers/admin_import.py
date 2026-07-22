from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.dependencies import SessionDep
from app.models.enums import ExtractedObjectType
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfImportCreate,
    QuestionImportCreate,
    ResourceImportRead,
    UrlImportCreate,
)
from app.services import admin_import as admin_import_service
from app.services.import_topic_validation import ImportTopicError
from app.services.pdf_upload import PdfUploadError

router = APIRouter(prefix="/admin/import", tags=["admin-import"])


@router.post("/url")
def import_url(payload: UrlImportCreate, session: SessionDep) -> ResourceImportRead:
    try:
        return admin_import_service.import_url_resource(session, payload)
    except ImportTopicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/note")
def import_note(payload: NoteImportCreate, session: SessionDep) -> ResourceImportRead:
    try:
        return admin_import_service.import_note_resource(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportTopicError as exc:
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
            filename=file.filename,
            content_type=file.content_type,
            content=content,
        )
    except PdfUploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportTopicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
