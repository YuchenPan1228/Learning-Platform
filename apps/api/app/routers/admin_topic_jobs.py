from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import SessionDep
from app.models.enums import TopicJobStatus
from app.schemas.topic_job import (
    TopicJobCreate,
    TopicJobDetailRead,
    TopicJobListResponse,
    TopicJobStatusUpdate,
)
from app.services.topic_job import (
    TopicJobCreateInput,
    TopicJobError,
    create_topic_job,
    get_topic_job,
    list_topic_jobs,
    transition_topic_job,
)

router = APIRouter(prefix="/admin/ingestion/jobs", tags=["admin-ingestion-jobs"])

StatusQuery = Annotated[TopicJobStatus | None, Query()]
TopicIdQuery = Annotated[int | None, Query()]
LimitQuery = Annotated[int, Query(ge=1, le=200)]


@router.post("")
def create_ingestion_job(
    payload: TopicJobCreate,
    session: SessionDep,
) -> TopicJobDetailRead:
    try:
        return create_topic_job(
            session,
            TopicJobCreateInput(
                query=payload.query,
                topic_id=payload.topic_id,
                topic_slug=payload.topic_slug,
                concept_id=payload.concept_id,
                target_source_count=payload.target_source_count,
                priority=payload.priority,
                created_by=payload.created_by,
            ),
        )
    except TopicJobError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def list_ingestion_jobs(
    session: SessionDep,
    status: StatusQuery = None,
    topic_id: TopicIdQuery = None,
    limit: LimitQuery = 50,
) -> TopicJobListResponse:
    try:
        return list_topic_jobs(
            session,
            status=status,
            topic_id=topic_id,
            limit=limit,
        )
    except TopicJobError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{job_id}")
def get_ingestion_job(job_id: int, session: SessionDep) -> TopicJobDetailRead:
    try:
        return get_topic_job(session, job_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{job_id}/status")
def update_ingestion_job_status(
    job_id: int,
    payload: TopicJobStatusUpdate,
    session: SessionDep,
) -> TopicJobDetailRead:
    try:
        return transition_topic_job(session, job_id, payload.status)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TopicJobError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
