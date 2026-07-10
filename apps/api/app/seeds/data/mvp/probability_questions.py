from app.models.enums import Difficulty
from app.seeds.data.question_seed import QuestionSeed

PROBABILITY_QUESTIONS: tuple[QuestionSeed, ...] = (
    QuestionSeed(
        seed_key="prob-001",
        title="Exactly 7 Heads",
        body="You flip 10 fair coins. What is the probability of exactly 7 heads?",
        topic_slug="probability",
        subtopic_slug="counting",
        difficulty=Difficulty.EASY,
        short_answer="15/128",
        canonical_solution="Choose 7 of 10 flips: C(10,7)/2^10 = 120/1024 = 15/128.",
        estimated_time_seconds=180,
        common_mistakes=("Forgetting to choose which flips are heads",),
        prerequisites=("Combinations",),
    ),
    QuestionSeed(
        seed_key="prob-002",
        title="Two Heads Given One Head",
        body=(
            "Two fair coins are flipped. Given that at least one coin shows heads, "
            "what is the probability both coins are heads?"
        ),
        topic_slug="probability",
        subtopic_slug="conditional-probability",
        difficulty=Difficulty.MEDIUM,
        short_answer="1/3",
        canonical_solution="Condition on {HH, HT, TH}. Only HH works, so the probability is 1/3.",
        estimated_time_seconds=240,
        common_mistakes=("Answering 1/2 without updating the sample space",),
        prerequisites=("Conditional probability",),
    ),
    QuestionSeed(
        seed_key="prob-003",
        title="Expected Rolls Until Six",
        body="What is the expected number of fair die rolls needed to obtain the first six?",
        topic_slug="probability",
        subtopic_slug="expectation",
        difficulty=Difficulty.MEDIUM,
        short_answer="6",
        canonical_solution="This is geometric with p = 1/6, so E[N] = 1/p = 6.",
        estimated_time_seconds=300,
        common_mistakes=(
            "Trying to enumerate many finite cases instead of using geometric distribution",
        ),
        prerequisites=("Geometric distribution",),
    ),
    QuestionSeed(
        seed_key="prob-004",
        title="Shared Birthday in a Room",
        body=(
            "Assuming birthdays are uniformly distributed across 365 days and independent, "
            "is a shared birthday more likely than not in a room of 23 people?"
        ),
        topic_slug="probability",
        subtopic_slug="counting",
        difficulty=Difficulty.MEDIUM,
        short_answer="yes",
        canonical_solution=(
            "P(all distinct) = 365/365 * 364/365 * ... * 343/365 < 1/2, "
            "so a shared birthday is more likely than not."
        ),
        estimated_time_seconds=300,
    ),
    QuestionSeed(
        seed_key="prob-005",
        title="Medical Test Base Rates",
        body=(
            "A disease affects 1% of people. A test is 95% sensitive and 95% specific. "
            "If a patient tests positive, what is the approximate probability they have the disease?"
        ),
        topic_slug="probability",
        subtopic_slug="bayes",
        difficulty=Difficulty.MEDIUM,
        short_answer="about 16%",
        canonical_solution=(
            "Use Bayes: P(D|+) = P(+|D)P(D) / P(+). "
            "With these numbers the posterior is about 16%, not 95%."
        ),
        estimated_time_seconds=300,
        common_mistakes=("Ignoring the base rate and answering 95%",),
    ),
    QuestionSeed(
        seed_key="prob-006",
        title="Sum of Two Dice Is 7",
        body="Two fair six-sided dice are rolled. What is the probability the sum is 7?",
        topic_slug="probability",
        subtopic_slug="counting",
        difficulty=Difficulty.EASY,
        short_answer="1/6",
        canonical_solution="There are 6 favorable ordered outcomes out of 36, so 6/36 = 1/6.",
        estimated_time_seconds=120,
    ),
    QuestionSeed(
        seed_key="prob-007",
        title="Heart Given Red Card",
        body=(
            "One card is drawn uniformly from a standard 52-card deck. "
            "Given that the card is red, what is the probability it is a heart?"
        ),
        topic_slug="probability",
        subtopic_slug="conditional-probability",
        difficulty=Difficulty.EASY,
        short_answer="1/2",
        canonical_solution="Among 26 red cards, 13 are hearts, so the probability is 13/26 = 1/2.",
        estimated_time_seconds=120,
    ),
    QuestionSeed(
        seed_key="prob-008",
        title="Three Independent All Heads",
        body="Three fair coins are flipped independently. What is the probability all three are heads?",
        topic_slug="probability",
        subtopic_slug="independence",
        difficulty=Difficulty.EASY,
        short_answer="1/8",
        canonical_solution="By independence, (1/2)^3 = 1/8.",
        estimated_time_seconds=90,
    ),
    QuestionSeed(
        seed_key="prob-009",
        title="Variance of Binomial",
        body="If X ~ Binomial(n, p), what is Var(X)?",
        topic_slug="probability",
        subtopic_slug="variance",
        difficulty=Difficulty.MEDIUM,
        short_answer="np(1-p)",
        canonical_solution="A binomial count has variance np(1-p).",
        estimated_time_seconds=180,
    ),
    QuestionSeed(
        seed_key="prob-010",
        title="Two-State Markov Limit",
        body=(
            "A Markov chain on two states has transition matrix "
            "[[0.8, 0.2], [0.3, 0.7]]. What is its long-run probability of state 1?"
        ),
        topic_slug="probability",
        subtopic_slug="markov-chains",
        difficulty=Difficulty.HARD,
        short_answer="3/5",
        canonical_solution=(
            "Solve pi P = pi with pi1 + pi2 = 1. The stationary probability of state 1 is 3/5."
        ),
        estimated_time_seconds=420,
    ),
    QuestionSeed(
        seed_key="prob-011",
        title="At Least One Ace in Five Cards",
        body="Five cards are drawn without replacement from a standard deck. What is P(at least one ace)?",
        topic_slug="probability",
        subtopic_slug="counting",
        difficulty=Difficulty.MEDIUM,
        short_answer="about 0.342",
        canonical_solution="Use complement: 1 - C(48,5)/C(52,5).",
        estimated_time_seconds=300,
    ),
    QuestionSeed(
        seed_key="prob-012",
        title="Geometric Expectation Fair Coin",
        body="What is the expected number of flips until the first heads with a fair coin?",
        topic_slug="probability",
        subtopic_slug="expectation",
        difficulty=Difficulty.EASY,
        short_answer="2",
        canonical_solution="Geometric with p = 1/2 gives expected wait 1/p = 2.",
        estimated_time_seconds=120,
    ),
    QuestionSeed(
        seed_key="prob-013",
        title="Die Roll Given Even",
        body="A fair die is rolled. Given the outcome is even, what is the probability it is a six?",
        topic_slug="probability",
        subtopic_slug="conditional-probability",
        difficulty=Difficulty.EASY,
        short_answer="1/3",
        canonical_solution="Condition on {2,4,6}. Only one outcome is six, so 1/3.",
        estimated_time_seconds=120,
    ),
    QuestionSeed(
        seed_key="prob-014",
        title="Random Coin By Factory",
        body=(
            "Coin A is fair and coin B has P(H)=0.6. You pick a coin uniformly at random and flip it once, "
            "observing heads. What is the probability you picked coin B?"
        ),
        topic_slug="probability",
        subtopic_slug="bayes",
        difficulty=Difficulty.MEDIUM,
        short_answer="3/4",
        canonical_solution="Apply Bayes with prior 1/2 on each coin and likelihoods 1/2 and 0.6.",
        estimated_time_seconds=300,
    ),
    QuestionSeed(
        seed_key="prob-015",
        title="Uniform Above 0.7",
        body="If X is uniform on [0, 1], what is P(X > 0.7)?",
        topic_slug="probability",
        subtopic_slug="continuous-distributions",
        difficulty=Difficulty.EASY,
        short_answer="0.3",
        canonical_solution="The favorable interval has length 0.3.",
        estimated_time_seconds=120,
    ),
    QuestionSeed(
        seed_key="prob-016",
        title="Compare Two Variances",
        body="Which has higher variance: one fair die roll or the sum of two fair die rolls?",
        topic_slug="probability",
        subtopic_slug="variance",
        difficulty=Difficulty.MEDIUM,
        short_answer="sum of two dice",
        canonical_solution="Var(X+Y)=Var(X)+Var(Y) for independent rolls, so the sum has larger variance.",
        estimated_time_seconds=180,
    ),
    QuestionSeed(
        seed_key="prob-017",
        title="Poisson Approximation Setup",
        body=(
            "In 1000 trials with success probability 0.002, why can a Poisson model be reasonable "
            "for the total number of successes?"
        ),
        topic_slug="probability",
        subtopic_slug="random-variables",
        difficulty=Difficulty.HARD,
        short_answer="rare events with fixed rate",
        canonical_solution=(
            "There are many trials, small p, and np stays moderate, so Poisson(2) approximates well."
        ),
        estimated_time_seconds=360,
    ),
    QuestionSeed(
        seed_key="prob-018",
        title="Fair Game Martingale",
        body=(
            "In a fair random walk with +1/-1 steps, why is your net position a martingale "
            "with respect to the natural filtration?"
        ),
        topic_slug="probability",
        subtopic_slug="martingales",
        difficulty=Difficulty.HARD,
        short_answer="zero conditional increment",
        canonical_solution="Each step has conditional expectation 0, so E[S_{n+1} | F_n] = S_n.",
        estimated_time_seconds=420,
    ),
    QuestionSeed(
        seed_key="prob-019",
        title="Coupon Collector Expectation",
        body="How many fair die rolls do you expect to need to see all six faces at least once?",
        topic_slug="probability",
        subtopic_slug="expectation",
        difficulty=Difficulty.HARD,
        short_answer="14.7",
        canonical_solution="Coupon collector on 6 types gives 6 * (1 + 1/2 + ... + 1/6) ≈ 14.7.",
        estimated_time_seconds=420,
    ),
    QuestionSeed(
        seed_key="prob-020",
        title="Conditional Rate Confusion",
        body=(
            "Treatment A has a higher success rate than treatment B in every hospital, "
            "but B has a higher overall success rate. What paradox is this?"
        ),
        topic_slug="probability",
        subtopic_slug="conditional-probability",
        difficulty=Difficulty.EXPERT,
        short_answer="Simpson's paradox",
        canonical_solution="Aggregating groups can reverse conditional comparisons when base rates differ.",
        estimated_time_seconds=300,
    ),
)
