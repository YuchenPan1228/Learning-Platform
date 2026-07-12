import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_dashboard_returns_topic_mastery_and_weak_prerequisites(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == "local"
    assert len(payload["topic_mastery"]) == 9
    assert payload["topic_mastery"][0]["slug"] == "probability"
    assert payload["topic_mastery"][0]["mastery_score"] == 0.0
    assert payload["topic_mastery"][0]["attempts_count"] == 0

    weak_prerequisites = payload["weak_prerequisites"]
    assert len(weak_prerequisites) > 0
    assert (
        weak_prerequisites[0]["prerequisite_mastery_score"]
        <= weak_prerequisites[-1]["prerequisite_mastery_score"]
    )

    bayes_weakness = next(
        item
        for item in weak_prerequisites
        if item["concept_slug"] == "bayes"
        and item["prerequisite_slug"] == "conditional-probability"
    )
    assert bayes_weakness["prerequisite_mastery_score"] == 0.0
