from app.db import get_session_factory
from app.seeds.knowledge_graph import seed_knowledge_graph
from app.seeds.local_user_state import seed_local_user_state


def main() -> None:
    session = get_session_factory()()
    try:
        graph_summary = seed_knowledge_graph(session)
        user_summary = seed_local_user_state(session)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        "Seeded knowledge graph:",
        f"{graph_summary.topics} topics,",
        f"{graph_summary.concepts} concepts,",
        f"{graph_summary.concept_edges} concept edges.",
    )
    print(f"Seeded local user state: {user_summary.mastery_rows} mastery rows.")


if __name__ == "__main__":
    main()
