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
    assert len(topics[0]["subtopics"]) == 12


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
    assert len(list_response.json()) == 66

    filtered_response = client.get("/concepts", params={"topic_slug": "probability"})
    assert filtered_response.status_code == 200
    assert len(filtered_response.json()) == 12

    math_response = client.get("/concepts", params={"topic_slug": "mathematics"})
    assert math_response.status_code == 200
    assert len(math_response.json()) == 9
    assert any(item["slug"] == "vectors-matrices" for item in math_response.json())

    stats_response = client.get("/concepts", params={"topic_slug": "statistics"})
    assert stats_response.status_code == 200
    assert len(stats_response.json()) == 6
    assert any(item["slug"] == "bias-variance" for item in stats_response.json())
    assert any(item["name"] == "Point Estimation" for item in stats_response.json())

    finance_response = client.get("/concepts", params={"topic_slug": "finance"})
    assert finance_response.status_code == 200
    assert len(finance_response.json()) == 7
    assert any(item["slug"] == "greeks" for item in finance_response.json())
    assert any(item["name"] == "Derivatives Payoffs & Parity" for item in finance_response.json())

    programming_response = client.get("/concepts", params={"topic_slug": "programming"})
    assert programming_response.status_code == 200
    assert len(programming_response.json()) == 5
    assert any(item["slug"] == "python" for item in programming_response.json())
    assert any(item["name"] == "C++ for Quant" for item in programming_response.json())
    programming_concepts = programming_response.json()
    assert all(item["slug"] != "programming-coding-patterns" for item in programming_concepts)
    detail_response = client.get("/concepts/counting")
    assert detail_response.status_code == 200
    counting = detail_response.json()
    assert counting["name"] == "Counting & Sample Spaces"
    assert counting["worked_example"] is not None
    assert "common_mistakes" in counting

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
    all_page2 = client.get("/questions", params={"limit": 100, "offset": 100})
    assert len(all_response.json()) + len(all_page2.json()) == 183

    filtered_response = client.get("/questions", params={"topic_slug": "probability", "limit": 100})
    assert len(filtered_response.json()) == 20

    math_response = client.get("/questions", params={"topic_slug": "mathematics", "limit": 100})
    assert math_response.status_code == 200
    assert len(math_response.json()) == 20
    assert all(item["topic_slug"] == "mathematics" for item in math_response.json())

    stats_response = client.get("/questions", params={"topic_slug": "statistics", "limit": 100})
    assert stats_response.status_code == 200
    assert len(stats_response.json()) == 18
    assert all(item["topic_slug"] == "statistics" for item in stats_response.json())
    assert any(item["subtopic_slug"] == "estimation" for item in stats_response.json())

    finance_q_response = client.get("/questions", params={"topic_slug": "finance", "limit": 100})
    assert finance_q_response.status_code == 200
    assert len(finance_q_response.json()) == 21
    assert all(item["topic_slug"] == "finance" for item in finance_q_response.json())
    assert any(item["subtopic_slug"] == "greeks" for item in finance_q_response.json())

    programming_q_response = client.get(
        "/questions", params={"topic_slug": "programming", "limit": 100}
    )
    assert programming_q_response.status_code == 200
    assert len(programming_q_response.json()) == 17
    assert all(item["topic_slug"] == "programming" for item in programming_q_response.json())
    assert any(item["subtopic_slug"] == "python" for item in programming_q_response.json())

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
    flashcards_response = client.get("/flashcards", params={"limit": 100})
    flashcards_page2 = client.get("/flashcards", params={"limit": 100, "offset": 100})
    assert flashcards_response.status_code == 200
    assert flashcards_page2.status_code == 200
    flashcards = flashcards_response.json() + flashcards_page2.json()
    assert len(flashcards) == 165
    assert flashcards[0]["front"]
    assert flashcards[0]["topic_slug"]

    filtered_flashcards_response = client.get("/flashcards", params={"topic_slug": "bayes"})
    assert filtered_flashcards_response.status_code == 200
    bayes_cards = filtered_flashcards_response.json()
    assert len(bayes_cards) == 3
    assert any(card["front"] == "State Bayes' rule." for card in bayes_cards)

    flashcard_detail_response = client.get(f"/flashcards/{flashcards[0]['id']}")
    assert flashcard_detail_response.status_code == 200
    assert flashcard_detail_response.json()["back"]

    learning_paths_response = client.get("/learning-paths")
    assert learning_paths_response.status_code == 200
    assert learning_paths_response.json() == []

    missing_path_response = client.get("/learning-paths/missing-path")
    assert missing_path_response.status_code == 404
