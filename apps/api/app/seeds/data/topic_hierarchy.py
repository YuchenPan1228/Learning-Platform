from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubtopicSeed:
    name: str
    slug: str | None = None


@dataclass(frozen=True, slots=True)
class TopicSeed:
    name: str
    slug: str
    subtopics: tuple[SubtopicSeed, ...]
    description: str | None = None


def _subtopic(name: str, slug: str | None = None) -> SubtopicSeed:
    return SubtopicSeed(name=name, slug=slug)


TOPIC_TREE: tuple[TopicSeed, ...] = (
    TopicSeed(
        name="Probability",
        slug="probability",
        description="Core probability theory for quant interviews.",
        subtopics=(
            _subtopic("Counting & Sample Spaces", slug="counting"),
            _subtopic("Independence"),
            _subtopic("Conditional Probability"),
            _subtopic("Bayes"),
            _subtopic("Random Variables"),
            _subtopic("Expectation"),
            _subtopic("Conditional Expectation", slug="conditional-expectation"),
            _subtopic("Variance & Covariance", slug="variance"),
            _subtopic("Common Distributions", slug="continuous-distributions"),
            _subtopic("Limit Theorems (LLN & CLT)", slug="limit-theorems"),
            _subtopic("Markov Chains"),
            _subtopic("Martingales"),
        ),
    ),
    TopicSeed(
        name="Mathematics",
        slug="mathematics",
        description="Interview-focused math foundations for quant trading and research screens.",
        subtopics=(
            _subtopic("Vectors & Matrices", slug="vectors-matrices"),
            _subtopic("Linear Systems & Rank", slug="linear-systems"),
            _subtopic("Eigenvalues & Eigenvectors", slug="eigenvalues"),
            _subtopic("Orthogonality & Projections", slug="orthogonality"),
            _subtopic("Derivatives & Gradients", slug="derivatives-gradients"),
            _subtopic("Taylor Expansions", slug="taylor-expansions"),
            _subtopic("Convexity & Unconstrained Optimization", slug="math-optimization"),
            _subtopic("Lagrange Multipliers", slug="lagrange-multipliers"),
            _subtopic("Differential Equations"),
        ),
    ),
    TopicSeed(
        name="Statistics",
        slug="statistics",
        description="Interview-focused inference: estimation, testing, likelihood, and regression.",
        subtopics=(
            _subtopic("Point Estimation", slug="estimation"),
            _subtopic("Confidence Intervals"),
            _subtopic("Hypothesis Testing"),
            _subtopic("Maximum Likelihood"),
            _subtopic("Linear Regression (OLS)", slug="regression"),
            _subtopic("Bias–Variance Tradeoff", slug="bias-variance"),
        ),
    ),
    TopicSeed(
        name="Finance",
        slug="finance",
        description="Interview-focused markets: derivatives, pricing intuition, portfolios, and trading microstructure.",
        subtopics=(
            _subtopic("Derivatives Payoffs & Parity", slug="derivatives"),
            _subtopic("Black–Scholes", slug="black-scholes"),
            _subtopic("Greeks"),
            _subtopic("Mean–Variance Portfolios", slug="portfolio-theory"),
            _subtopic("CAPM & Beta", slug="capm"),
            _subtopic("Fixed Income Basics", slug="fixed-income"),
            _subtopic("Market Microstructure"),
        ),
    ),
    TopicSeed(
        name="Programming",
        slug="programming",
        description="Languages and CS foundations for quant SWE and research coding screens.",
        subtopics=(
            _subtopic("Python for Quant", slug="python"),
            _subtopic("C++ for Quant", slug="cpp"),
            _subtopic("Core Data Structures", slug="data-structures"),
            _subtopic("Complexity & Core Algorithms", slug="algorithms"),
            _subtopic("SQL for Quant", slug="sql"),
        ),
    ),
    TopicSeed(
        name="Coding Patterns",
        slug="coding-patterns",
        description="Reusable algorithmic patterns for timed quant coding interviews.",
        subtopics=(
            _subtopic("Two Pointers"),
            _subtopic("Sliding Window"),
            _subtopic("Prefix Sum"),
            _subtopic("Binary Search"),
            _subtopic("Intervals"),
            _subtopic("Graph Traversal"),
            _subtopic("Dynamic Programming"),
            _subtopic("Greedy"),
        ),
    ),
    TopicSeed(
        name="Mental Math",
        slug="mental-math",
        description="Lightning calculation for trading interviews — based on Arthur Benjamin's Secrets of Mental Math.",
        subtopics=(
            _subtopic("Quick Tricks", slug="quick-tricks"),
            _subtopic("Addition & Subtraction", slug="addition-subtraction"),
            _subtopic("Basic Multiplication", slug="basic-multiplication"),
            _subtopic("Intermediate Multiplication", slug="intermediate-multiplication"),
            _subtopic("Mental Division & Fractions", slug="mental-division-fractions"),
            _subtopic("Guesstimation", slug="guesstimation"),
            _subtopic("Memorizing Numbers", slug="memorizing-numbers"),
            _subtopic("Advanced Multiplication", slug="advanced-multiplication"),
        ),
    ),
    TopicSeed(
        name="Quant Research",
        slug="quant-research",
        description="Research bridge: time series, stochastic models, simulation, and numerical methods.",
        subtopics=(
            _subtopic("Time Series Basics", slug="time-series"),
            _subtopic("Stochastic Processes", slug="stochastic-processes"),
            _subtopic("Brownian Motion & GBM", slug="brownian-motion"),
            _subtopic("Monte Carlo Methods", slug="monte-carlo"),
            _subtopic("Numerical Methods", slug="numerical-methods"),
            _subtopic("Statistical Learning for Alpha", slug="machine-learning-for-finance"),
        ),
    ),
    TopicSeed(
        name="Other Sections",
        slug="other-sections",
        description="Brain teasers, game theory, market games, behavioral interview, and quant system design.",
        subtopics=(
            _subtopic("Brain Teasers", slug="brain-teasers"),
            _subtopic("Game Theory", slug="game-theory"),
            _subtopic("Market Games", slug="market-games"),
            _subtopic("Behavioral Interview", slug="behavioral-interview"),
            _subtopic("System Design for Quant", slug="system-design"),
        ),
    ),
)
