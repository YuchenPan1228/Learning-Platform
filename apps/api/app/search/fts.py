from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement

from app.models.concept import Concept
from app.models.question import Question

FTS_CONFIG = "quant_prep_english"


def question_search_vector() -> ColumnElement[object]:
    return func.to_tsvector(
        FTS_CONFIG,
        func.concat(
            func.coalesce(Question.title, ""),
            " ",
            func.coalesce(Question.body, ""),
        ),
    )


def concept_search_vector() -> ColumnElement[object]:
    return func.to_tsvector(
        FTS_CONFIG,
        func.concat(
            func.coalesce(Concept.name, ""),
            " ",
            func.coalesce(Concept.definition, ""),
            " ",
            func.coalesce(Concept.formula, ""),
        ),
    )


def plainto_tsquery(query: str) -> ColumnElement[object]:
    return func.plainto_tsquery(FTS_CONFIG, query)
