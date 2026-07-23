from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import SessionDep
from app.schemas.admin_concepts import ConceptListResponse, ConceptUpdate
from app.schemas.concept import ConceptDetailRead
from app.services.admin_concepts import (
    ConceptEditorError,
    get_concept_for_editor,
    list_concepts_for_editor,
    update_concept,
)

router = APIRouter(prefix="/admin/concepts", tags=["admin-concepts"])

TopicSlugQuery = Annotated[str | None, Query()]


@router.get("")
def list_admin_concepts(
    session: SessionDep,
    topic_slug: TopicSlugQuery = None,
) -> ConceptListResponse:
    items = list_concepts_for_editor(session, topic_slug=topic_slug)
    return ConceptListResponse(items=items)


@router.get("/{slug}")
def get_admin_concept(slug: str, session: SessionDep) -> ConceptDetailRead:
    try:
        return get_concept_for_editor(session, slug)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{slug}")
def patch_admin_concept(
    slug: str,
    payload: ConceptUpdate,
    session: SessionDep,
) -> ConceptDetailRead:
    try:
        return update_concept(session, slug, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConceptEditorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
