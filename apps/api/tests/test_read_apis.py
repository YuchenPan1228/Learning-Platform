import pytest
from fastapi.testclient import TestClient


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
    assert "tags" in questions[0]

    all_response = client.get("/questions", params={"limit": 100})
    assert len(all_response.json()) == 65

    filtered_response = client.get("/questions", params={"topic_slug": "probability", "limit": 100})
    assert len(filtered_response.json()) == 20

    concept_response = client.get("/questions", params={"concept_slug": "bayes", "limit": 100})
    assert concept_response.status_code == 200
    concept_questions = concept_response.json()
    assert len(concept_questions) >= 1
    assert all(item["subtopic_slug"] == "bayes" for item in concept_questions)

    tagged = next(item for item in questions if item["tags"])
    tag_slug = tagged["tags"][0]["slug"]
    tag_response = client.get("/questions", params={"tag_slug": tag_slug, "limit": 100})
    assert tag_response.status_code == 200
    assert len(tag_response.json()) >= 1
    assert all(any(tag["slug"] == tag_slug for tag in item["tags"]) for item in tag_response.json())

    difficulty_response = client.get(
        "/questions",
        params={"difficulty": "easy", "limit": 100},
    )
    assert difficulty_response.status_code == 200
    assert len(difficulty_response.json()) >= 1
    difficulties = {item["difficulty"] for item in difficulty_response.json()}
    assert difficulties == {"easy"}

    detail_response = client.get(f"/questions/{questions[0]['id']}")
    assert detail_response.status_code == 200
    question = detail_response.json()
    assert question["body"]
    assert question["topic_slug"]
    assert "tags" in question


@pytest.mark.integration
def test_list_tags_endpoint(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/tags")
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) >= 1
    assert {"id", "slug", "name", "category"} <= set(tags[0].keys())


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
    flashcards = flashcards_response.json()
    assert len(flashcards) == 15
    assert flashcards[0]["front"]
    assert flashcards[0]["topic_slug"]

    filtered_flashcards_response = client.get("/flashcards", params={"topic_slug": "bayes"})
    assert filtered_flashcards_response.status_code == 200
    assert len(filtered_flashcards_response.json()) == 1
    assert filtered_flashcards_response.json()[0]["front"] == "State Bayes' rule."

    flashcard_detail_response = client.get(f"/flashcards/{flashcards[0]['id']}")
    assert flashcard_detail_response.status_code == 200
    assert flashcard_detail_response.json()["back"]

    learning_paths_response = client.get("/learning-paths")
    assert learning_paths_response.status_code == 200
    assert learning_paths_response.json() == []

    missing_path_response = client.get("/learning-paths/missing-path")
    assert missing_path_response.status_code == 404
