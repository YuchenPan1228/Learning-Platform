from app.models.enums import Difficulty
from app.seeds.data.question_seed import QuestionSeed

CODING_QUESTIONS: tuple[QuestionSeed, ...] = (
    QuestionSeed(
        seed_key="code-001",
        title="Binary Search Invariant",
        body="What invariant should you maintain in binary search on a sorted array?",
        topic_slug="coding-patterns",
        subtopic_slug="binary-search",
        difficulty=Difficulty.MEDIUM,
        canonical_solution=(
            "The target, if it exists, always remains inside the current search interval "
            "defined by low and high pointers."
        ),
        estimated_time_seconds=240,
        expected_solution_pattern="Maintain shrinking interval containing the answer.",
    ),
    QuestionSeed(
        seed_key="code-002",
        title="Two Pointers on Sorted Array",
        body="When is a two-pointer scan on a sorted array preferable to a hash map?",
        topic_slug="coding-patterns",
        subtopic_slug="two-pointers",
        difficulty=Difficulty.MEDIUM,
        canonical_solution=(
            "When the input is sorted and you need pair sums, deduplication, or merging "
            "with O(1) extra space."
        ),
        estimated_time_seconds=240,
    ),
    QuestionSeed(
        seed_key="code-003",
        title="Hash Map Tradeoff",
        body="What time and space tradeoff does a hash map provide for lookup problems?",
        topic_slug="programming",
        subtopic_slug="algorithms",
        difficulty=Difficulty.EASY,
        canonical_solution="Average O(1) lookup and insertion at the cost of O(n) extra space.",
        estimated_time_seconds=180,
    ),
    QuestionSeed(
        seed_key="code-004",
        title="Dynamic Programming Overlap",
        body="What property makes dynamic programming appropriate for a problem?",
        topic_slug="coding-patterns",
        subtopic_slug="dynamic-programming",
        difficulty=Difficulty.MEDIUM,
        canonical_solution="Optimal substructure and overlapping subproblems.",
        estimated_time_seconds=240,
    ),
    QuestionSeed(
        seed_key="code-005",
        title="BFS vs DFS Choice",
        body="When should you prefer BFS over DFS on a graph?",
        topic_slug="coding-patterns",
        subtopic_slug="graph-traversal",
        difficulty=Difficulty.MEDIUM,
        canonical_solution="Use BFS for shortest path in unweighted graphs or level-order processing.",
        estimated_time_seconds=240,
    ),
    QuestionSeed(
        seed_key="code-006",
        title="Sliding Window Trigger",
        body="What signal suggests a sliding window approach on an array?",
        topic_slug="coding-patterns",
        subtopic_slug="sliding-window",
        difficulty=Difficulty.MEDIUM,
        canonical_solution=(
            "You need the best subarray/substring under a contiguous constraint such as "
            "fixed length or sum threshold."
        ),
        estimated_time_seconds=240,
    ),
    QuestionSeed(
        seed_key="code-007",
        title="Prefix Sum Use Case",
        body="How does a prefix sum array help answer range sum queries?",
        topic_slug="coding-patterns",
        subtopic_slug="prefix-sum",
        difficulty=Difficulty.EASY,
        canonical_solution="Range sum [l,r] equals prefix[r+1] - prefix[l] after O(n) preprocessing.",
        estimated_time_seconds=180,
    ),
    QuestionSeed(
        seed_key="code-008",
        title="Connected Components",
        body="How do you find connected components in an undirected graph?",
        topic_slug="coding-patterns",
        subtopic_slug="graph-traversal",
        difficulty=Difficulty.MEDIUM,
        canonical_solution=(
            "Run BFS or DFS from unvisited nodes; each traversal marks one component. "
            "$O(V+E)$ total."
        ),
        estimated_time_seconds=240,
    ),
    QuestionSeed(
        seed_key="code-009",
        title="Nested Loop Complexity",
        body="What is the worst-case time complexity of two nested loops over n items?",
        topic_slug="programming",
        subtopic_slug="algorithms",
        difficulty=Difficulty.EASY,
        canonical_solution="O(n^2) if each loop runs up to n.",
        estimated_time_seconds=120,
    ),
    QuestionSeed(
        seed_key="code-010",
        title="Stack for Parentheses",
        body="Why does a stack solve valid parentheses checking?",
        topic_slug="coding-patterns",
        subtopic_slug="two-pointers",
        difficulty=Difficulty.MEDIUM,
        canonical_solution=(
            "Opening brackets push; closing brackets must match the most recent unmatched "
            "opener (LIFO). Related linear scan — not interval merge."
        ),
        estimated_time_seconds=240,
    ),
)
