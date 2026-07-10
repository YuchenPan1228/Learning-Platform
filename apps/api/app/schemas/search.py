from pydantic import BaseModel

from app.schemas.concept import ConceptSummaryRead
from app.schemas.question import QuestionSummaryRead


class SearchResponse(BaseModel):
    query: str
    questions: list[QuestionSummaryRead]
    concepts: list[ConceptSummaryRead]
    total: int
