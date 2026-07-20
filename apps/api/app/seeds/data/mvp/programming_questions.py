from app.models.enums import Difficulty
from app.seeds.data.question_seed import QuestionSeed

PROGRAMMING_QUESTIONS: tuple[QuestionSeed, ...] = (
    # --- Python for Quant ---
    QuestionSeed(
        seed_key="prog-001",
        title="Membership Cost: List vs Set",
        body=(
            "In Python, worst-case / typical cost of `x in lst` for a length-$n$ list vs "
            "`x in s` for a set? Enter like O(n) vs O(1)."
        ),
        topic_slug="programming",
        subtopic_slug="python",
        difficulty=Difficulty.EASY,
        short_answer="O(n) vs O(1)",
        canonical_solution=(
            "List membership scans: $O(n)$. Set/dict membership is average $O(1)$."
        ),
        estimated_time_seconds=60,
        prerequisites=("Python collections",),
    ),
    QuestionSeed(
        seed_key="prog-002",
        title="Bisect Complexity",
        body=(
            "Using `bisect_left` on a sorted Python list of length $n$, what is the time "
            "complexity of one search? Enter like O(log n)."
        ),
        topic_slug="programming",
        subtopic_slug="python",
        difficulty=Difficulty.EASY,
        short_answer="O(log n)",
        canonical_solution="`bisect` is binary search: $O(\\log n)$.",
        estimated_time_seconds=45,
        prerequisites=("bisect",),
    ),
    QuestionSeed(
        seed_key="prog-003",
        title="Counter Complexity",
        body=(
            "Building `Counter(xs)` for a list of length $n$ with $k$ distinct keys: "
            "time complexity? Enter like O(n)."
        ),
        topic_slug="programming",
        subtopic_slug="python",
        difficulty=Difficulty.EASY,
        short_answer="O(n)",
        canonical_solution="One pass over $n$ elements with hash updates: $O(n)$ time, $O(k)$ space.",
        estimated_time_seconds=60,
        prerequisites=("Counter",),
    ),
    # --- C++ for Quant ---
    QuestionSeed(
        seed_key="prog-004",
        title="Range-for Copy vs Reference",
        body=(
            "In C++, for `vector<Big> vec`, does `for (auto x : vec)` copy each element? "
            "Answer yes or no."
        ),
        topic_slug="programming",
        subtopic_slug="cpp",
        difficulty=Difficulty.EASY,
        short_answer="yes",
        canonical_solution=(
            "`auto x` copies; use `const auto& x` (or `auto&`) to avoid copies."
        ),
        estimated_time_seconds=60,
        prerequisites=("C++ references",),
    ),
    QuestionSeed(
        seed_key="prog-005",
        title="unordered_map Average Lookup",
        body=(
            "Average-case lookup complexity in `std::unordered_map`? Enter like O(1)."
        ),
        topic_slug="programming",
        subtopic_slug="cpp",
        difficulty=Difficulty.EASY,
        short_answer="O(1)",
        canonical_solution="Average $O(1)$; worst case $O(n)$ with pathological hashing.",
        estimated_time_seconds=45,
        prerequisites=("Hash maps",),
    ),
    QuestionSeed(
        seed_key="prog-006",
        title="vector Iterator Invalidation",
        body=(
            "After `vec.push_back` that triggers reallocation, are old iterators into `vec` "
            "still valid? Answer yes or no."
        ),
        topic_slug="programming",
        subtopic_slug="cpp",
        difficulty=Difficulty.MEDIUM,
        short_answer="no",
        canonical_solution="Reallocation invalidates pointers/iterators/references into the vector.",
        estimated_time_seconds=90,
        prerequisites=("std::vector",),
    ),
    # --- Core Data Structures ---
    QuestionSeed(
        seed_key="prog-007",
        title="Heap Pop Complexity",
        body=(
            "Binary heap: complexity of insert and of extract-min? Enter like O(log n), O(log n)."
        ),
        topic_slug="programming",
        subtopic_slug="data-structures",
        difficulty=Difficulty.EASY,
        short_answer="O(log n), O(log n)",
        canonical_solution="Both insert and extract-min are $O(\\log n)$; peek is $O(1)$.",
        estimated_time_seconds=60,
        prerequisites=("Heaps",),
    ),
    QuestionSeed(
        seed_key="prog-008",
        title="Structure for Membership",
        body=(
            "You need repeated membership tests on $n$ integers. Prefer array scan or hash set? "
            "Answer array or hash."
        ),
        topic_slug="programming",
        subtopic_slug="data-structures",
        difficulty=Difficulty.EASY,
        short_answer="hash",
        canonical_solution="Hash set gives average $O(1)$ membership vs $O(n)$ scans.",
        estimated_time_seconds=45,
        prerequisites=("Hash sets",),
    ),
    QuestionSeed(
        seed_key="prog-009",
        title="Top-k Structure",
        body=(
            "Return the $k$ largest of $n$ unsorted numbers with $k\\ll n$. "
            "Preferred structure: sort-all or size-$k$ heap? Answer sort or heap."
        ),
        topic_slug="programming",
        subtopic_slug="data-structures",
        difficulty=Difficulty.MEDIUM,
        short_answer="heap",
        canonical_solution="Size-$k$ heap is $O(n\\log k)$, better than $O(n\\log n)$ full sort when $k\\ll n$.",
        estimated_time_seconds=120,
        prerequisites=("Heaps", "top-k",),
    ),
    # --- Complexity & Core Algorithms ---
    QuestionSeed(
        seed_key="prog-010",
        title="Two-Sum Better Bound",
        body=(
            "Check whether any two array values sum to $T$. Hash-set one-pass time? "
            "Enter like O(n)."
        ),
        topic_slug="programming",
        subtopic_slug="algorithms",
        difficulty=Difficulty.EASY,
        short_answer="O(n)",
        canonical_solution="One pass with a seen-set: average $O(n)$ time, $O(n)$ space.",
        estimated_time_seconds=90,
        prerequisites=("Hashing",),
    ),
    QuestionSeed(
        seed_key="prog-011",
        title="Binary Search Need",
        body=(
            "Binary search requires what property of the search space? "
            "Answer sorted or monotonic."
        ),
        topic_slug="programming",
        subtopic_slug="algorithms",
        difficulty=Difficulty.EASY,
        short_answer="monotonic",
        canonical_solution=(
            "A monotonic predicate / sorted order so you can discard half each step."
        ),
        estimated_time_seconds=60,
        common_mistakes=("Saying only 'array' without monotonicity",),
        prerequisites=("Binary search",),
    ),
    QuestionSeed(
        seed_key="prog-012",
        title="Nested Loop Complexity",
        body=(
            "Two nested loops `for i in 0..n-1` and `for j in 0..n-1` with $O(1)$ body: "
            "time complexity? Enter like O(n^2)."
        ),
        topic_slug="programming",
        subtopic_slug="algorithms",
        difficulty=Difficulty.EASY,
        short_answer="O(n^2)",
        canonical_solution="$n\\times n$ iterations ⇒ $O(n^2)$.",
        estimated_time_seconds=45,
        prerequisites=("Big-O",),
    ),
    # --- SQL for Quant ---
    QuestionSeed(
        seed_key="prog-013",
        title="NULL Comparison",
        body=(
            "In SQL, does `WHERE x = NULL` match NULL rows? Answer yes or no."
        ),
        topic_slug="programming",
        subtopic_slug="sql",
        difficulty=Difficulty.EASY,
        short_answer="no",
        canonical_solution="Use `IS NULL` / `IS NOT NULL`; `=` with NULL yields unknown.",
        estimated_time_seconds=45,
        prerequisites=("SQL NULL",),
    ),
    QuestionSeed(
        seed_key="prog-014",
        title="LEFT JOIN Keeps Which Side",
        body=(
            "In a `LEFT JOIN`, rows from which table are always kept even without a match? "
            "Answer left or right."
        ),
        topic_slug="programming",
        subtopic_slug="sql",
        difficulty=Difficulty.EASY,
        short_answer="left",
        canonical_solution="`LEFT JOIN` keeps all left-table rows; missing right side is NULL-padded.",
        estimated_time_seconds=45,
        prerequisites=("SQL joins",),
    ),
    QuestionSeed(
        seed_key="prog-015",
        title="Window vs GROUP BY",
        body=(
            "Which keeps detail rows while computing a per-group aggregate: "
            "WINDOW or GROUP BY? Answer WINDOW or GROUP BY."
        ),
        topic_slug="programming",
        subtopic_slug="sql",
        difficulty=Difficulty.MEDIUM,
        short_answer="WINDOW",
        canonical_solution=(
            "Window functions compute across partitions but do not collapse rows; "
            "`GROUP BY` collapses to one row per group."
        ),
        estimated_time_seconds=90,
        prerequisites=("Window functions",),
    ),
)
