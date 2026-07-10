from app.db import get_session_factory
from app.seeds.knowledge_graph import seed_knowledge_graph


def main() -> None:
    session = get_session_factory()()
    try:
        summary = seed_knowledge_graph(session)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        "Seeded knowledge graph:",
        f"{summary.topics} topics,",
        f"{summary.concepts} concepts,",
        f"{summary.concept_edges} concept edges.",
    )


if __name__ == "__main__":
    main()
