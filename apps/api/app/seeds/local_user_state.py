from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class LocalUserStateSummary:
    mastery_rows: int


def seed_local_user_state(session: Session) -> LocalUserStateSummary:
    # UserTopicMastery stays empty until Phase 3B (QP-028).
    # Dashboard mastery is computed from attempts in the meantime.
    session.commit()
    return LocalUserStateSummary(mastery_rows=0)
