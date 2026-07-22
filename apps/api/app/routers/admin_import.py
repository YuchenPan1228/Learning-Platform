from fastapi import APIRouter, HTTPException

from app.dependencies import SessionDep
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfMetadataImportCreate,
    QuestionImportCreate,
    ResourceImportRead,
    UrlImportCreate,
)
from app.services import admin_import as admin_import_service
from app.services.import_topic_validation import ImportTopicError

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
def import_pdf_metadata(
    payload: PdfMetadataImportCreate,
    session: SessionDep,
) -> ResourceImportRead:
    try:
        return admin_import_service.import_pdf_metadata_resource(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportTopicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
