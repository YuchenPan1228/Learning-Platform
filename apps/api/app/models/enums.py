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


class LearningSignalType(StrEnum):
    SEARCH_MISS = "search_miss"
    CONFUSING_QUESTION_FLAG = "confusing_question_flag"
    HIGH_COMPLETION_RATE = "high_completion_rate"
    WEAK_TOPIC = "weak_topic"


class SearchResourceType(StrEnum):
    QUESTIONS = "questions"
    CONCEPTS = "concepts"


class DuplicateMatchType(StrEnum):
    EXACT_RAW = "exact_raw"
    EXACT_NORMALIZED = "exact_normalized"
    NEAR_NORMALIZED = "near_normalized"


class QuestionProgressStatus(StrEnum):
    NOT_ATTEMPTED = "not_attempted"
    ATTEMPTED = "attempted"
    SOLVED = "solved"


class ManualQuestionProgressStatus(StrEnum):
    SOLVED = "solved"
    NOT_ATTEMPTED = "not_attempted"


class FlashcardReviewRating(StrEnum):
    AGAIN = "again"
    GOOD = "good"
    EASY = "easy"


class AICacheResultKind(StrEnum):
    EXPLANATION = "explanation"
    HINT = "hint"
    SUMMARY = "summary"
    GENERATED_QUESTION = "generated_question"


class TopicJobStatus(StrEnum):
    QUEUED = "queued"
    COLLECTING = "collecting"
    EXTRACTING = "extracting"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


class TopicJobCreatedBy(StrEnum):
    USER = "user"
    ADMIN = "admin"
    ACTIVE_LEARNING = "active_learning"


class ResourceSourceType(StrEnum):
    URL = "url"
    PDF = "pdf"
    BOOK_NOTE = "book_note"
    MANUAL = "manual"
    GENERATED = "generated"


class ExtractedObjectType(StrEnum):
    CONCEPT = "concept"
    FORMULA = "formula"
    EXAMPLE = "example"
    QUESTION = "question"
    FLASHCARD = "flashcard"


class JobExecutionStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobExecutionStage(StrEnum):
    COLLECTING = "collecting"
    POLICY_CHECK = "policy_check"
    QUALITY_SCORING = "quality_scoring"
    EXTRACTING = "extracting"
    AI_EXTRACTION = "ai_extraction"
    DEDUPLICATION = "deduplication"
    REVIEWING = "reviewing"
    PUBLISHING = "publishing"


class SourcePolicyDecision(StrEnum):
    ALLOW = "allow"
    REVIEW = "review"
    DENY = "deny"


class ExtractionMethod(StrEnum):
    URL_TRAFILATURA = "url_trafilatura"
    URL_BEAUTIFULSOUP = "url_beautifulsoup"
    URL_PLAYWRIGHT = "url_playwright"
    PDF_PYMUPDF = "pdf_pymupdf"
    PASTED_TEXT = "pasted_text"


class AllowlistStatus(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    NOT_CONFIGURED = "not_configured"
    NOT_APPLICABLE = "not_applicable"


class RobotsStatus(StrEnum):
    ALLOWED = "allowed"
    DISALLOWED = "disallowed"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class LicenseStatus(StrEnum):
    PERMISSIVE = "permissive"
    RESTRICTIVE = "restrictive"
    UNKNOWN = "unknown"
    MISSING = "missing"
