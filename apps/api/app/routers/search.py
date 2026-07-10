from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import SessionDep
from app.models.enums import Difficulty, SearchResourceType
from app.routers.concepts import _concept_summary
from app.routers.questions import _question_summary
from app.schemas.search import SearchResponse
from app.services.search import record_search_miss, search_content

router = APIRouter(prefix="/search", tags=["search"])

QueryParam = Annotated[str, Query(min_length=1)]
TypesQuery = Annotated[list[SearchResourceType], Query()]
TopicSlugQuery = Annotated[str | None, Query()]
DifficultyQuery = Annotated[Difficulty | None, Query()]
LimitQuery = Annotated[int, Query(ge=1, le=50)]

DEFAULT_SEARCH_TYPES = [SearchResourceType.QUESTIONS, SearchResourceType.CONCEPTS]


@router.get("")
def search(
    session: SessionDep,
    q: QueryParam,
    types: TypesQuery = DEFAULT_SEARCH_TYPES,
    topic_slug: TopicSlugQuery = None,
    difficulty: DifficultyQuery = None,
    limit: LimitQuery = 20,
) -> SearchResponse:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Search query must not be empty")

    results = search_content(
        session,
        query,
        types=types,
        topic_slug=topic_slug,
        difficulty=difficulty,
        limit=limit,
    )
    questions = [_question_summary(question) for question in results.questions]
    concepts = [_concept_summary(concept) for concept in results.concepts]
    total = len(questions) + len(concepts)

    record_search_miss(
        session,
        query=query,
        types=types,
        topic_slug=topic_slug,
        result_count=total,
    )

    return SearchResponse(
        query=query,
        questions=questions,
        concepts=concepts,
        total=total,
    )
