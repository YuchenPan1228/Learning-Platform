from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.mastery import recalculate_user_topic_mastery


@dataclass(frozen=True, slots=True)
class LocalUserStateSummary:
    mastery_rows: int


def seed_local_user_state(session: Session) -> LocalUserStateSummary:
    rows = recalculate_user_topic_mastery(session)
    return LocalUserStateSummary(mastery_rows=len(rows))
