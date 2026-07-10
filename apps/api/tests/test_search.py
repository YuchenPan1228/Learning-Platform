import pytest
from app.models.enums import LearningSignalType
from app.models.learning_signal import LearningSignal
from fastapi.testclient import TestClient
from sqlalchemy import func, select


@pytest.mark.integration
def test_search_finds_questions_and_concepts(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/search", params={"q": "bayes"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "bayes"
    assert payload["total"] > 0
    assert any(item["slug"] == "bayes" for item in payload["concepts"])


@pytest.mark.integration
def test_search_filters_by_resource_type(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get(
        "/search",
        params={"q": "bayes", "types": ["concepts"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["questions"] == []
    assert len(payload["concepts"]) >= 1


@pytest.mark.integration
def test_search_records_miss_for_empty_results(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory, reset_db_state

    miss_query = "zzzz-no-results-qp012"
    response = client.get("/search", params={"q": miss_query})

    assert response.status_code == 200
    assert response.json()["total"] == 0

    session = get_session_factory()()
    try:
        signal_count = session.scalar(
            select(func.count())
            .select_from(LearningSignal)
            .where(LearningSignal.signal_type == LearningSignalType.SEARCH_MISS)
        )
        signal = session.scalar(
            select(LearningSignal).where(
                LearningSignal.payload_json["query"].as_string() == miss_query
            )
        )
        assert signal_count == 1
        assert signal is not None
        assert signal.payload_json["result_count"] == 0
    finally:
        session.close()
        reset_db_state()


@pytest.mark.integration
def test_search_does_not_record_miss_when_results_exist(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory, reset_db_state

    client.get("/search", params={"q": "bayes"})
    client.get("/search", params={"q": "zzzz-no-results-qp012-unique"})

    session = get_session_factory()()
    try:
        signal_count = session.scalar(
            select(func.count())
            .select_from(LearningSignal)
            .where(LearningSignal.signal_type == LearningSignalType.SEARCH_MISS)
        )
        assert signal_count == 1
    finally:
        session.close()
        reset_db_state()


@pytest.mark.integration
def test_search_rejects_empty_query(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/search", params={"q": " "})

    assert response.status_code == 422
