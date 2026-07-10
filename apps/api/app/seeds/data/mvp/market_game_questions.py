from app.models.enums import ContentStatus, Difficulty
from app.seeds.data.question_seed import QuestionSeed

MARKET_GAME_QUESTIONS: tuple[QuestionSeed, ...] = (
    QuestionSeed(
        seed_key="game-001",
        title="Guess Two-Thirds of the Average",
        body=(
            "Placeholder market game: each player submits an integer from 0 to 100. "
            "The winner is closest to two-thirds of the average submission. "
            "Describe a reasonable first-move strategy."
        ),
        topic_slug="other-sections",
        subtopic_slug="market-games",
        difficulty=Difficulty.MEDIUM,
        status=ContentStatus.APPROVED,
        expected_solution_pattern="Iterated reasoning toward lower numbers; interactive UI deferred.",
        canonical_solution=(
            "If everyone picks randomly, the average is near 50 and the target is about 33. "
            "Iterating that logic pushes rational play lower."
        ),
        estimated_time_seconds=300,
    ),
    QuestionSeed(
        seed_key="game-002",
        title="Monty Hall Interactive Placeholder",
        body=(
            "Placeholder market game: three doors, one car, two goats. "
            "After you pick a door, the host opens a goat door and offers a switch. Should you switch?"
        ),
        topic_slug="other-sections",
        subtopic_slug="market-games",
        difficulty=Difficulty.EASY,
        short_answer="switch",
        canonical_solution="Switching wins with probability 2/3 under standard Monty Hall rules.",
        expected_solution_pattern="Interactive simulation deferred to Phase 8.",
        estimated_time_seconds=240,
    ),
    QuestionSeed(
        seed_key="game-003",
        title="Penny Auction Expected Value",
        body=(
            "Placeholder market game: each bid costs $0.75 and raises the price by $0.01. "
            "What qualitative EV issue makes these auctions risky?"
        ),
        topic_slug="other-sections",
        subtopic_slug="market-games",
        difficulty=Difficulty.HARD,
        canonical_solution=(
            "Players pay real bid fees while only one wins the item, so expected spend can exceed value."
        ),
        expected_solution_pattern="Deterministic scoring UI deferred.",
        estimated_time_seconds=360,
    ),
    QuestionSeed(
        seed_key="game-004",
        title="Market Making Spread Game",
        body=(
            "Placeholder market game: you quote a bid/ask around an unknown fair value. "
            "What tradeoff do you face when tightening the spread?"
        ),
        topic_slug="other-sections",
        subtopic_slug="market-games",
        difficulty=Difficulty.MEDIUM,
        canonical_solution=(
            "Tighter spreads attract more flow but increase adverse selection and inventory risk."
        ),
        expected_solution_pattern="Order book simulation deferred to Phase 8.",
        estimated_time_seconds=300,
    ),
    QuestionSeed(
        seed_key="game-005",
        title="Secretary Problem Strategy",
        body=(
            "Placeholder market game: candidates arrive one by one and must be accepted or rejected permanently. "
            "What classic strategy approximates the optimal stopping rule?"
        ),
        topic_slug="other-sections",
        subtopic_slug="market-games",
        difficulty=Difficulty.HARD,
        short_answer="reject first 37%",
        canonical_solution=(
            "Reject the first n/e candidates, then pick the next candidate better than all seen so far."
        ),
        expected_solution_pattern="Interactive stopping game deferred.",
        estimated_time_seconds=360,
    ),
)
