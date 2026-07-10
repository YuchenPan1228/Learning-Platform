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
            _subtopic("Counting"),
            _subtopic("Conditional Probability"),
            _subtopic("Bayes"),
            _subtopic("Random Variables"),
            _subtopic("Expectation"),
            _subtopic("Variance"),
            _subtopic("Independence"),
            _subtopic("Continuous Distributions"),
            _subtopic("Markov Chains"),
            _subtopic("Martingales"),
        ),
    ),
    TopicSeed(
        name="Mathematics",
        slug="mathematics",
        description="Mathematical foundations used across quant roles.",
        subtopics=(
            _subtopic("Linear Algebra"),
            _subtopic("Calculus"),
            _subtopic("Optimization", slug="math-optimization"),
            _subtopic("Differential Equations"),
        ),
    ),
    TopicSeed(
        name="Statistics",
        slug="statistics",
        description="Inference, estimation, and modeling fundamentals.",
        subtopics=(
            _subtopic("Estimation"),
            _subtopic("Hypothesis Testing"),
            _subtopic("Regression"),
            _subtopic("Maximum Likelihood"),
            _subtopic("Confidence Intervals"),
        ),
    ),
    TopicSeed(
        name="Finance",
        slug="finance",
        description="Markets, derivatives, and portfolio concepts.",
        subtopics=(
            _subtopic("Derivatives"),
            _subtopic("Black-Scholes"),
            _subtopic("Greeks"),
            _subtopic("Portfolio Theory"),
            _subtopic("CAPM"),
            _subtopic("Fixed Income"),
            _subtopic("Market Microstructure"),
        ),
    ),
    TopicSeed(
        name="Programming",
        slug="programming",
        description="Languages and implementation skills for quant SWE screens.",
        subtopics=(
            _subtopic("Python"),
            _subtopic("C++", slug="cpp"),
            _subtopic("SQL"),
            _subtopic("Algorithms"),
            _subtopic("Data Structures"),
            _subtopic("Coding Patterns", slug="programming-coding-patterns"),
        ),
    ),
    TopicSeed(
        name="Coding Patterns",
        slug="coding-patterns",
        description="Reusable algorithmic patterns for timed coding interviews.",
        subtopics=(
            _subtopic("Sliding Window"),
            _subtopic("Binary Search"),
            _subtopic("Prefix Sum"),
            _subtopic("Union Find"),
            _subtopic("Sweep Line"),
            _subtopic("Greedy"),
            _subtopic("Dynamic Programming"),
            _subtopic("Graph Traversal"),
            _subtopic("Intervals"),
            _subtopic("Two Pointers"),
        ),
    ),
    TopicSeed(
        name="Mental Math",
        slug="mental-math",
        description="Fast arithmetic and estimation drills for trading interviews.",
        subtopics=(
            _subtopic("Arithmetic"),
            _subtopic("Fractions"),
            _subtopic("Percentages"),
            _subtopic("Approximations"),
            _subtopic("Logarithms"),
            _subtopic("Roots"),
            _subtopic("Powers"),
            _subtopic("Expected Value"),
            _subtopic("Fast Estimation"),
        ),
    ),
    TopicSeed(
        name="Quant Research",
        slug="quant-research",
        description="Research-oriented stochastic and numerical methods.",
        subtopics=(
            _subtopic("Time Series"),
            _subtopic("Stochastic Processes"),
            _subtopic("Brownian Motion"),
            _subtopic("Monte Carlo"),
            _subtopic("Optimization", slug="quant-research-optimization"),
            _subtopic("Numerical Methods"),
            _subtopic("Machine Learning for Finance"),
        ),
    ),
    TopicSeed(
        name="Other Sections",
        slug="other-sections",
        description="Brain teasers, games, behavioral, and system design topics.",
        subtopics=(
            _subtopic("Brain Teasers"),
            _subtopic("Game Theory"),
            _subtopic("Market Games"),
            _subtopic("Behavioral"),
            _subtopic("System Design"),
            _subtopic("Behavior Questions"),
        ),
    ),
)
