from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import SessionDep
from app.models.enums import ContentStatus, ExtractedObjectType
from app.schemas.admin_review import (
    ExtractedObjectEdit,
    ExtractedObjectReviewRead,
    ReviewQueueResponse,
)
from app.services.admin_review import (
    ReviewQueueError,
    approve_review_item,
    edit_review_item,
    get_review_item,
    list_review_items,
    reject_review_item,
)

router = APIRouter(prefix="/admin/review", tags=["admin-review"])

StatusQuery = Annotated[ContentStatus, Query()]
ObjectTypeQuery = Annotated[ExtractedObjectType | None, Query()]


@router.get("")
def list_review_queue(
    session: SessionDep,
    status: StatusQuery = ContentStatus.DRAFT,
    object_type: ObjectTypeQuery = None,
) -> ReviewQueueResponse:
    items = list_review_items(session, status=status, object_type=object_type)
    return ReviewQueueResponse(items=items)


@router.get("/{extracted_object_id}")
def get_review_queue_item(
    extracted_object_id: int,
    session: SessionDep,
) -> ExtractedObjectReviewRead:
    try:
        return get_review_item(session, extracted_object_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{extracted_object_id}")
def edit_review_queue_item(
    extracted_object_id: int,
    payload: ExtractedObjectEdit,
    session: SessionDep,
) -> ExtractedObjectReviewRead:
    try:
        return edit_review_item(session, extracted_object_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReviewQueueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{extracted_object_id}/approve")
def approve_review_queue_item(
    extracted_object_id: int,
    session: SessionDep,
) -> ExtractedObjectReviewRead:
    try:
        return approve_review_item(session, extracted_object_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReviewQueueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{extracted_object_id}/reject")
def reject_review_queue_item(
    extracted_object_id: int,
    session: SessionDep,
) -> ExtractedObjectReviewRead:
    try:
        return reject_review_item(session, extracted_object_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReviewQueueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
