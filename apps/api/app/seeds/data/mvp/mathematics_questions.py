from app.models.enums import Difficulty
from app.seeds.data.question_seed import QuestionSeed

MATHEMATICS_QUESTIONS: tuple[QuestionSeed, ...] = (
    # --- Vectors & Matrices ---
    QuestionSeed(
        seed_key="math-001",
        title="Matrix Times Standard Basis",
        body=(
            "Let A = [[1, 2], [3, 4]]. What is A[1, 0]^T? "
            "Enter the result as (a,b)."
        ),
        topic_slug="mathematics",
        subtopic_slug="vectors-matrices",
        difficulty=Difficulty.EASY,
        short_answer="(1,3)",
        canonical_solution=(
            "A e₁ equals the first column of A, so A[1,0]^T = [1,3]^T."
        ),
        estimated_time_seconds=120,
        common_mistakes=("Returning the first row (1,2) instead of the first column",),
        prerequisites=("Matrix–vector product",),
    ),
    QuestionSeed(
        seed_key="math-002",
        title="Outer Product Matrix",
        body=(
            "Let u = [1, 2]^T and v = [3, 4]^T. What is the (2,1) entry of uv^T?"
        ),
        topic_slug="mathematics",
        subtopic_slug="vectors-matrices",
        difficulty=Difficulty.EASY,
        short_answer="6",
        canonical_solution=(
            "uv^T = [[3,4],[6,8]]. The (2,1) entry is u₂ v₁ = 2·3 = 6."
        ),
        estimated_time_seconds=150,
        common_mistakes=("Computing u^T v = 11 instead of an entry of uv^T",),
        prerequisites=("Outer product",),
    ),
    QuestionSeed(
        seed_key="math-003",
        title="Cross Product of Basis Vectors",
        body=(
            "In R^3, what is [1,0,0]^T × [0,1,0]^T? Enter as (a,b,c)."
        ),
        topic_slug="mathematics",
        subtopic_slug="vectors-matrices",
        difficulty=Difficulty.EASY,
        short_answer="(0,0,1)",
        canonical_solution=(
            "i × j = k, so [1,0,0]^T × [0,1,0]^T = [0,0,1]^T."
        ),
        estimated_time_seconds=120,
        prerequisites=("Cross product",),
    ),
    # --- Linear Systems & Rank ---
    QuestionSeed(
        seed_key="math-004",
        title="Rank of a Repeated-Row Matrix",
        body=(
            "What is rank([[1, 2], [2, 4]])?"
        ),
        topic_slug="mathematics",
        subtopic_slug="linear-systems",
        difficulty=Difficulty.EASY,
        short_answer="1",
        canonical_solution=(
            "The second row is twice the first, so there is only one independent row. Rank = 1."
        ),
        estimated_time_seconds=90,
        prerequisites=("Rank",),
    ),
    QuestionSeed(
        seed_key="math-005",
        title="Nullity of a 3x5 Matrix",
        body=(
            "A is a 3×5 matrix with rank 2. What is dim N(A)?"
        ),
        topic_slug="mathematics",
        subtopic_slug="linear-systems",
        difficulty=Difficulty.MEDIUM,
        short_answer="3",
        canonical_solution="Rank–nullity: dim N(A) = n − rank(A) = 5 − 2 = 3.",
        estimated_time_seconds=120,
        common_mistakes=("Using m − rank instead of n − rank",),
        prerequisites=("Rank–nullity",),
    ),
    # --- Eigenvalues & Eigenvectors ---
    QuestionSeed(
        seed_key="math-006",
        title="Eigenvalues of a Diagonal Matrix",
        body=(
            "What are the eigenvalues of diag(2, 5)? Enter them in increasing order as a,b."
        ),
        topic_slug="mathematics",
        subtopic_slug="eigenvalues",
        difficulty=Difficulty.EASY,
        short_answer="2,5",
        canonical_solution="For a diagonal matrix, the eigenvalues are the diagonal entries: 2 and 5.",
        estimated_time_seconds=60,
        prerequisites=("Eigenvalues",),
    ),
    QuestionSeed(
        seed_key="math-007",
        title="Eigenvalues of a Symmetric 2x2",
        body=(
            "Find the eigenvalues of A = [[2, 1], [1, 2]]. "
            "Enter them in increasing order as a,b."
        ),
        topic_slug="mathematics",
        subtopic_slug="eigenvalues",
        difficulty=Difficulty.MEDIUM,
        short_answer="1,3",
        canonical_solution=(
            "det(A−λI) = (2−λ)^2 − 1 = λ^2 − 4λ + 3 = (λ−1)(λ−3). Eigenvalues are 1 and 3."
        ),
        estimated_time_seconds=300,
        prerequisites=("Characteristic polynomial",),
    ),
    QuestionSeed(
        seed_key="math-008",
        title="Positive Definite Check",
        body=(
            "Is A = [[2, 1], [1, 2]] symmetric positive definite? Answer yes or no."
        ),
        topic_slug="mathematics",
        subtopic_slug="eigenvalues",
        difficulty=Difficulty.MEDIUM,
        short_answer="yes",
        canonical_solution=(
            "A is symmetric and eigenvalues are 1 and 3, both positive, so A is SPD."
        ),
        estimated_time_seconds=180,
        prerequisites=("SPD / eigenvalues",),
    ),
    # --- Orthogonality & Projections ---
    QuestionSeed(
        seed_key="math-009",
        title="Project Onto the x-Axis",
        body=(
            "Project b = [2, 2]^T onto span{[1, 0]^T}. Enter the projection as (a,b)."
        ),
        topic_slug="mathematics",
        subtopic_slug="orthogonality",
        difficulty=Difficulty.EASY,
        short_answer="(2,0)",
        canonical_solution=(
            "Onto unit vector u=[1,0]^T: proj = (u^T b)u = 2[1,0]^T = [2,0]^T."
        ),
        estimated_time_seconds=120,
        prerequisites=("Orthogonal projection",),
    ),
    QuestionSeed(
        seed_key="math-010",
        title="Are These Vectors Orthogonal?",
        body=(
            "Are u = [3, 4]^T and v = [−4, 3]^T orthogonal? Answer yes or no."
        ),
        topic_slug="mathematics",
        subtopic_slug="orthogonality",
        difficulty=Difficulty.EASY,
        short_answer="yes",
        canonical_solution="u^T v = −12 + 12 = 0, so they are orthogonal.",
        estimated_time_seconds=90,
        prerequisites=("Dot product",),
    ),
    # --- Derivatives & Gradients ---
    QuestionSeed(
        seed_key="math-011",
        title="Gradient of a Simple Function",
        body=(
            "Let f(x,y) = x^2 y + e^y. What is ∇f at (1, 0)? Enter as (a,b)."
        ),
        topic_slug="mathematics",
        subtopic_slug="derivatives-gradients",
        difficulty=Difficulty.MEDIUM,
        short_answer="(0,2)",
        canonical_solution=(
            "∇f = (2xy, x^2 + e^y). At (1,0): (0, 1+1) = (0,2)."
        ),
        estimated_time_seconds=180,
        prerequisites=("Gradient",),
    ),
    QuestionSeed(
        seed_key="math-012",
        title="Product Rule at a Point",
        body=(
            "If f(x) = x^2 sin x, what is f'(π/2)? Enter an exact value in terms of pi "
            "as a bare number times pi if needed (e.g. if the answer is π, enter pi)."
        ),
        topic_slug="mathematics",
        subtopic_slug="derivatives-gradients",
        difficulty=Difficulty.MEDIUM,
        short_answer="pi",
        canonical_solution=(
            "f' = 2x sin x + x^2 cos x. At x=π/2: 2·(π/2)·1 + (π/2)^2·0 = π."
        ),
        estimated_time_seconds=240,
        common_mistakes=("Forgetting the product rule",),
        prerequisites=("Product rule",),
    ),
    QuestionSeed(
        seed_key="math-013",
        title="Critical Point of x^2 + y^2",
        body=(
            "Where is the critical point of f(x,y) = x^2 + y^2? Enter as (a,b)."
        ),
        topic_slug="mathematics",
        subtopic_slug="derivatives-gradients",
        difficulty=Difficulty.EASY,
        short_answer="(0,0)",
        canonical_solution="∇f = (2x, 2y) = 0 ⇒ (x,y) = (0,0).",
        estimated_time_seconds=90,
        prerequisites=("Critical points",),
    ),
    # --- Taylor Expansions ---
    QuestionSeed(
        seed_key="math-014",
        title="Second-Order Exp Approximation",
        body=(
            "Using e^h ≈ 1 + h + (1/2)h^2, approximate e^{0.1}. "
            "Enter a decimal."
        ),
        topic_slug="mathematics",
        subtopic_slug="taylor-expansions",
        difficulty=Difficulty.EASY,
        short_answer="1.105",
        canonical_solution="1 + 0.1 + 0.5·0.01 = 1.105.",
        estimated_time_seconds=120,
        prerequisites=("Taylor series for exp",),
    ),
    QuestionSeed(
        seed_key="math-015",
        title="Log Return Second Order",
        body=(
            "Using log(1+r) ≈ r − (1/2)r^2, approximate log(1.01). "
            "Enter a decimal."
        ),
        topic_slug="mathematics",
        subtopic_slug="taylor-expansions",
        difficulty=Difficulty.MEDIUM,
        short_answer="0.00995",
        canonical_solution="0.01 − 0.5·(0.01)^2 = 0.01 − 0.00005 = 0.00995.",
        estimated_time_seconds=150,
        prerequisites=("Taylor series for log",),
    ),
    # --- Convexity & Unconstrained Optimization ---
    QuestionSeed(
        seed_key="math-016",
        title="Minimize a 1D Quadratic",
        body=(
            "Minimize f(x) = x^2 − 4x + 1 over the reals. What is the minimizer x*?"
        ),
        topic_slug="mathematics",
        subtopic_slug="math-optimization",
        difficulty=Difficulty.EASY,
        short_answer="2",
        canonical_solution="f' = 2x − 4 = 0 ⇒ x = 2. f'' = 2 > 0, so it is a minimum.",
        estimated_time_seconds=120,
        prerequisites=("First-order conditions",),
    ),
    QuestionSeed(
        seed_key="math-017",
        title="SPD Quadratic Minimizer",
        body=(
            "Minimize f(x) = (1/2) x^T Q x − b^T x with Q = [[2, 0], [0, 4]] and "
            "b = [2, 4]^T. What is the first coordinate of x*?"
        ),
        topic_slug="mathematics",
        subtopic_slug="math-optimization",
        difficulty=Difficulty.MEDIUM,
        short_answer="1",
        canonical_solution=(
            "FOC: Qx = b ⇒ [2x₁, 4x₂]^T = [2, 4]^T ⇒ x₁ = 1, x₂ = 1. First coordinate is 1."
        ),
        estimated_time_seconds=240,
        prerequisites=("Quadratic optimization",),
    ),
    # --- Lagrange Multipliers ---
    QuestionSeed(
        seed_key="math-018",
        title="Maximize xy on a Line",
        body=(
            "Maximize f(x,y) = xy subject to x + y = 1. What is the maximum value?"
        ),
        topic_slug="mathematics",
        subtopic_slug="lagrange-multipliers",
        difficulty=Difficulty.MEDIUM,
        short_answer="1/4",
        canonical_solution=(
            "∇f = λ∇g with g=x+y−1: (y,x)=λ(1,1) and x+y=1 ⇒ x=y=1/2 ⇒ f=1/4."
        ),
        estimated_time_seconds=300,
        prerequisites=("Lagrange multipliers",),
    ),
    QuestionSeed(
        seed_key="math-019",
        title="Closest Point on a Line",
        body=(
            "Minimize x^2 + y^2 subject to x + 2y = 1. What is x* at the minimum?"
        ),
        topic_slug="mathematics",
        subtopic_slug="lagrange-multipliers",
        difficulty=Difficulty.MEDIUM,
        short_answer="1/5",
        canonical_solution=(
            "∇f=(2x,2y)=λ(1,2) ⇒ 2x=λ, 2y=2λ ⇒ y=λ, x=λ/2. "
            "Constraint: λ/2 + 2λ = 1 ⇒ (5/2)λ=1 ⇒ λ=2/5 ⇒ x=1/5."
        ),
        estimated_time_seconds=360,
        prerequisites=("Lagrange multipliers", "projections"),
    ),
    # --- Differential Equations ---
    QuestionSeed(
        seed_key="math-020",
        title="Exponential Decay ODE",
        body=(
            "Solve y' = −3y with y(0) = 5. The solution is y(t) = C e^{-3t}. What is C?"
        ),
        topic_slug="mathematics",
        subtopic_slug="differential-equations",
        difficulty=Difficulty.EASY,
        short_answer="5",
        canonical_solution="y = y₀ e^{kt} with k=−3 and y₀=5 ⇒ C = 5.",
        estimated_time_seconds=120,
        prerequisites=("Exponential ODE",),
    ),
)
