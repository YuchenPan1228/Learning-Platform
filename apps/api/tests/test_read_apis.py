import pytest
from app.config import get_settings
from app.db import get_session_factory, reset_db_state
from app.seeds.knowledge_graph import seed_knowledge_graph
from app.seeds.mvp_content import seed_mvp_content
from fastapi.testclient import TestClient


@pytest.fixture
def seeded_database(
    database_url: str,
    migrated_database: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    reset_db_state()

    session = get_session_factory()()
    try:
        seed_knowledge_graph(session)
        seed_mvp_content(session)
    finally:
        session.close()


@pytest.mark.integration
def test_list_topics_returns_root_sections_with_subtopics(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/topics")

    assert response.status_code == 200
    topics = response.json()
    assert len(topics) == 9
    assert topics[0]["slug"] == "probability"
    assert len(topics[0]["subtopics"]) == 10


@pytest.mark.integration
def test_get_topic_by_slug(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/topics/probability")

    assert response.status_code == 200
    topic = response.json()
    assert topic["name"] == "Probability"
    assert any(subtopic["slug"] == "bayes" for subtopic in topic["subtopics"])


@pytest.mark.integration
def test_get_topic_returns_404_for_missing_slug(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/topics/does-not-exist")

    assert response.status_code == 404


@pytest.mark.integration
def test_list_concepts_and_get_detail_with_neighbors(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    list_response = client.get("/concepts")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 64

    filtered_response = client.get("/concepts", params={"topic_slug": "probability"})
    assert filtered_response.status_code == 200
    assert len(filtered_response.json()) == 10

    detail_response = client.get("/concepts/bayes")
    assert detail_response.status_code == 200
    concept = detail_response.json()
    assert concept["formula"] is not None
    assert any(neighbor["slug"] == "conditional-probability" for neighbor in concept["neighbors"])


@pytest.mark.integration
def test_list_questions_with_filters_and_get_detail(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    list_response = client.get("/questions")
    assert list_response.status_code == 200
    questions = list_response.json()
    assert len(questions) == 50
    assert "body" not in questions[0]

    all_response = client.get("/questions", params={"limit": 100})
    assert len(all_response.json()) == 65

    filtered_response = client.get("/questions", params={"topic_slug": "probability", "limit": 100})
    assert len(filtered_response.json()) == 20

    detail_response = client.get(f"/questions/{questions[0]['id']}")
    assert detail_response.status_code == 200
    question = detail_response.json()
    assert question["body"]
    assert question["topic_slug"]


@pytest.mark.integration
def test_get_question_returns_404_for_missing_id(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/questions/999999")

    assert response.status_code == 404


@pytest.mark.integration
def test_flashcards_and_learning_paths_endpoints(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    flashcards_response = client.get("/flashcards")
    assert flashcards_response.status_code == 200
    assert flashcards_response.json() == []

    learning_paths_response = client.get("/learning-paths")
    assert learning_paths_response.status_code == 200
    assert learning_paths_response.json() == []

    missing_path_response = client.get("/learning-paths/missing-path")
    assert missing_path_response.status_code == 404
