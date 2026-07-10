from dataclasses import dataclass

from app.models.enums import ConceptEdgeRelationshipType


@dataclass(frozen=True, slots=True)
class ConceptSeed:
    slug: str
    name: str
    topic_slug: str
    definition: str | None = None
    formula: str | None = None
    intuition: str | None = None
    common_mistakes: str | None = None
    interview_tips: str | None = None
    prerequisites: str | None = None


@dataclass(frozen=True, slots=True)
class ConceptEdgeSeed:
    source_slug: str
    target_slug: str
    relationship_type: ConceptEdgeRelationshipType
    weight: float = 1.0


def default_concept_definition(name: str, parent_name: str) -> str:
    return f"Core interview concept for {name} within {parent_name}."


CONCEPT_DETAILS: dict[str, ConceptSeed] = {
    "counting": ConceptSeed(
        slug="counting",
        name="Counting",
        topic_slug="counting",
        definition="Methods for counting outcomes, arrangements, and combinations in finite sample spaces.",
        intuition="Fix the sample space before counting; combinations and permutations answer different questions.",
        interview_tips="State whether order matters and whether repetition is allowed before writing a formula.",
    ),
    "conditional-probability": ConceptSeed(
        slug="conditional-probability",
        name="Conditional Probability",
        topic_slug="conditional-probability",
        definition="The probability of an event given that another event has occurred.",
        formula="P(A | B) = P(A ∩ B) / P(B)",
        intuition="Conditioning restricts the sample space to the information you already observed.",
        common_mistakes="Treating P(A | B) and P(B | A) as interchangeable.",
        interview_tips="Define events clearly and check whether the sample space changed after observing evidence.",
        prerequisites="Counting, sample spaces",
    ),
    "bayes": ConceptSeed(
        slug="bayes",
        name="Bayes' Rule",
        topic_slug="bayes",
        definition="Updates the probability of a hypothesis after observing new evidence.",
        formula="P(A | B) = P(B | A)P(A) / P(B)",
        intuition="Posterior odds combine prior belief with the strength of the observed evidence.",
        common_mistakes="Confusing P(A | B) with P(B | A), ignoring base rates, or failing to redefine the sample space.",
        interview_tips="Name the events, write the formula, compute the denominator with total probability, then sanity-check.",
        prerequisites="Conditional Probability, Independence",
    ),
    "random-variables": ConceptSeed(
        slug="random-variables",
        name="Random Variables",
        topic_slug="random-variables",
        definition="Numeric summaries of random outcomes that support expectation, variance, and distribution work.",
        intuition="A random variable turns uncertain outcomes into numbers you can analyze systematically.",
    ),
    "expectation": ConceptSeed(
        slug="expectation",
        name="Expectation",
        topic_slug="expectation",
        definition="The long-run average value of a random variable, weighted by probability.",
        formula="E[X] = Σ x P(X = x) for discrete X",
        intuition="Expectation is a weighted average over the entire distribution.",
    ),
    "variance": ConceptSeed(
        slug="variance",
        name="Variance",
        topic_slug="variance",
        definition="Measures how spread out a random variable is around its expectation.",
        formula="Var(X) = E[(X - E[X])²]",
        intuition="Variance captures uncertainty beyond the average outcome.",
    ),
    "independence": ConceptSeed(
        slug="independence",
        name="Independence",
        topic_slug="independence",
        definition="Events or random variables that do not influence each other's probabilities.",
        formula="P(A ∩ B) = P(A)P(B)",
        intuition="Observing one independent event gives no information about the other.",
    ),
    "markov-chains": ConceptSeed(
        slug="markov-chains",
        name="Markov Chains",
        topic_slug="markov-chains",
        definition="Stochastic processes where the next state depends only on the current state.",
        intuition="The future is memoryless given the present state.",
    ),
}


CONCEPT_EDGES: tuple[ConceptEdgeSeed, ...] = (
    ConceptEdgeSeed("conditional-probability", "counting", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("bayes", "conditional-probability", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("bayes", "independence", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("expectation", "counting", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("expectation", "random-variables", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("variance", "expectation", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("random-variables", "expectation", ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed(
        "independence", "conditional-probability", ConceptEdgeRelationshipType.RELATED_TO
    ),
    ConceptEdgeSeed(
        "continuous-distributions", "random-variables", ConceptEdgeRelationshipType.REQUIRES
    ),
    ConceptEdgeSeed("markov-chains", "random-variables", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("martingales", "markov-chains", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("bayes", "counting", ConceptEdgeRelationshipType.USED_IN),
    ConceptEdgeSeed("hypothesis-testing", "estimation", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("regression", "hypothesis-testing", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("maximum-likelihood", "estimation", ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed("confidence-intervals", "estimation", ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed("black-scholes", "derivatives", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("greeks", "black-scholes", ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed("capm", "portfolio-theory", ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed(
        "stochastic-processes", "random-variables", ConceptEdgeRelationshipType.REQUIRES
    ),
    ConceptEdgeSeed(
        "brownian-motion", "stochastic-processes", ConceptEdgeRelationshipType.REQUIRES
    ),
    ConceptEdgeSeed("monte-carlo", "brownian-motion", ConceptEdgeRelationshipType.USED_IN),
    ConceptEdgeSeed("dynamic-programming", "graph-traversal", ConceptEdgeRelationshipType.REQUIRES),
)
