from enum import StrEnum


def enum_values(enum_cls: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_cls]


class ConceptEdgeRelationshipType(StrEnum):
    REQUIRES = "requires"
    RELATED_TO = "related_to"
    USED_IN = "used_in"


class ContentStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class TagCategory(StrEnum):
    CONCEPT = "concept"
    COMPANY = "company"
    FORMAT = "format"
    SKILL = "skill"
    FORMULA = "formula"
