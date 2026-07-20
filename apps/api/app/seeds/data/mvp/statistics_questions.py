from app.models.enums import Difficulty
from app.seeds.data.question_seed import QuestionSeed

STATISTICS_QUESTIONS: tuple[QuestionSeed, ...] = (
    # --- Point Estimation ---
    QuestionSeed(
        seed_key="stats-001",
        title="MSE of the Sample Mean",
        body=(
            "IID $X_i$ with mean $\\mu$ and variance $\\sigma^2=4$. "
            "For $n=16$, what is $\\mathrm{MSE}(\\bar X)$ as an estimator of $\\mu$?"
        ),
        topic_slug="statistics",
        subtopic_slug="estimation",
        difficulty=Difficulty.EASY,
        short_answer="0.25",
        canonical_solution=(
            "$\\bar X$ is unbiased, so $\\mathrm{MSE}=\\mathrm{Var}(\\bar X)=\\sigma^2/n=4/16=1/4$."
        ),
        estimated_time_seconds=120,
        common_mistakes=("Using $\\sigma^2$ instead of $\\sigma^2/n$",),
        prerequisites=("Bias, variance, MSE",),
    ),
    QuestionSeed(
        seed_key="stats-002",
        title="Bias of a Scaled Estimator",
        body=("Let $E[\\hat\\theta]=\\theta+2$. What is $\\mathrm{Bias}(\\hat\\theta)$?"),
        topic_slug="statistics",
        subtopic_slug="estimation",
        difficulty=Difficulty.EASY,
        short_answer="2",
        canonical_solution="$\\mathrm{Bias}(\\hat\\theta)=E[\\hat\\theta]-\\theta=2$.",
        estimated_time_seconds=60,
        prerequisites=("Bias",),
    ),
    QuestionSeed(
        seed_key="stats-003",
        title="Single Observation vs Sample Mean",
        body=(
            "IID $X_i$ with variance $\\sigma^2$. "
            "What is $\\mathrm{MSE}(X_1)/\\mathrm{MSE}(\\bar X)$ for estimating $\\mu$ when $n=9$? "
            "(Both estimators are unbiased.)"
        ),
        topic_slug="statistics",
        subtopic_slug="estimation",
        difficulty=Difficulty.MEDIUM,
        short_answer="9",
        canonical_solution=(
            "$\\mathrm{MSE}(X_1)=\\sigma^2$ and $\\mathrm{MSE}(\\bar X)=\\sigma^2/9$, so the ratio is $9$."
        ),
        estimated_time_seconds=150,
        common_mistakes=("Comparing SEs instead of MSEs",),
        prerequisites=("MSE of sample mean",),
    ),
    # --- Confidence Intervals ---
    QuestionSeed(
        seed_key="stats-004",
        title="Z-Interval Half-Width",
        body=(
            "$n=100$, $\\sigma=2$ known, 95% CI for $\\mu$ using $z_{0.975}=1.96$. "
            "What is the half-width of the interval? (Numeric, 3 decimals.)"
        ),
        topic_slug="statistics",
        subtopic_slug="confidence-intervals",
        difficulty=Difficulty.EASY,
        short_answer="0.392",
        canonical_solution=("Half-width $= z\\,\\sigma/\\sqrt n = 1.96\\cdot 2/10 = 0.392$."),
        estimated_time_seconds=120,
        common_mistakes=("Using $\\sigma$ instead of $\\sigma/\\sqrt n$",),
        prerequisites=("Normal CI for mean",),
    ),
    QuestionSeed(
        seed_key="stats-005",
        title="CI Centered at Sample Mean",
        body=("$\\bar X=3$, half-width $0.5$. Enter the 95% CI as [a,b] with a<b."),
        topic_slug="statistics",
        subtopic_slug="confidence-intervals",
        difficulty=Difficulty.EASY,
        short_answer="[2.5,3.5]",
        canonical_solution="$\\bar X \\pm 0.5$ gives $[2.5, 3.5]$.",
        estimated_time_seconds=60,
        prerequisites=("CI construction",),
    ),
    QuestionSeed(
        seed_key="stats-006",
        title="What Is Random in a CI?",
        body=(
            "For a fixed unknown $\\mu$, which is random: the parameter $\\mu$, or the interval "
            "endpoints $L$ and $U$? Answer parameter or interval."
        ),
        topic_slug="statistics",
        subtopic_slug="confidence-intervals",
        difficulty=Difficulty.EASY,
        short_answer="interval",
        canonical_solution=(
            "In the frequentist CI, $\\mu$ is fixed; $L$ and $U$ are random (functions of the data)."
        ),
        estimated_time_seconds=90,
        common_mistakes=("Saying $\\mu$ is random with 95% probability inside the interval",),
        prerequisites=("CI interpretation",),
    ),
    # --- Hypothesis Testing ---
    QuestionSeed(
        seed_key="stats-007",
        title="Two-Sided Z-Test Statistic",
        body=(
            "Test $H_0:\\mu=0$ with $n=25$, $\\bar X=0.4$, $\\sigma=1$ known. "
            "What is the z-statistic $Z=\\sqrt n(\\bar X-\\mu_0)/\\sigma$?"
        ),
        topic_slug="statistics",
        subtopic_slug="hypothesis-testing",
        difficulty=Difficulty.EASY,
        short_answer="2",
        canonical_solution="$Z=5\\cdot 0.4/1=2$.",
        estimated_time_seconds=90,
        prerequisites=("Z-test for mean",),
    ),
    QuestionSeed(
        seed_key="stats-008",
        title="Reject at 5% with Critical Value",
        body=(
            "Two-sided level $\\alpha=0.05$ uses critical value $1.96$. "
            "If $|Z|=2.1$, do you reject $H_0$? Answer yes or no."
        ),
        topic_slug="statistics",
        subtopic_slug="hypothesis-testing",
        difficulty=Difficulty.EASY,
        short_answer="yes",
        canonical_solution="$|2.1|>1.96$, so reject $H_0$ at level 5%.",
        estimated_time_seconds=60,
        prerequisites=("Rejection region",),
    ),
    QuestionSeed(
        seed_key="stats-009",
        title="Type I Error Rate",
        body=(
            "A test is designed with significance level $\\alpha=0.05$. "
            "Under $H_0$, what is $P(\\text{reject }H_0)$? Enter as a decimal."
        ),
        topic_slug="statistics",
        subtopic_slug="hypothesis-testing",
        difficulty=Difficulty.EASY,
        short_answer="0.05",
        canonical_solution=(
            "By definition of level, $P(\\text{Type I error})=\\alpha=0.05$ when the null is true "
            "(for a correctly calibrated test)."
        ),
        estimated_time_seconds=60,
        common_mistakes=("Confusing with Type II error / power",),
        prerequisites=("Type I error",),
    ),
    # --- Maximum Likelihood ---
    QuestionSeed(
        seed_key="stats-010",
        title="Bernoulli MLE",
        body=(
            "IID Bernoulli($p$) trials: 7 successes in 10 trials. What is $\\hat p_{\\mathrm{MLE}}$?"
        ),
        topic_slug="statistics",
        subtopic_slug="maximum-likelihood",
        difficulty=Difficulty.EASY,
        short_answer="0.7",
        canonical_solution="$\\hat p_{\\mathrm{MLE}}=\\bar X=k/n=7/10=0.7$.",
        estimated_time_seconds=60,
        prerequisites=("Bernoulli MLE",),
    ),
    QuestionSeed(
        seed_key="stats-011",
        title="Normal Mean MLE",
        body=("IID $N(\\mu,1)$ data with $\\bar X=2.5$. What is $\\hat\\mu_{\\mathrm{MLE}}$?"),
        topic_slug="statistics",
        subtopic_slug="maximum-likelihood",
        difficulty=Difficulty.EASY,
        short_answer="2.5",
        canonical_solution="For Normal mean with known variance, $\\hat\\mu_{\\mathrm{MLE}}=\\bar X=2.5$.",
        estimated_time_seconds=60,
        prerequisites=("Normal MLE",),
    ),
    QuestionSeed(
        seed_key="stats-012",
        title="Log-Likelihood Score Equation",
        body=(
            "For IID Bernoulli($p$), $\\ell(p)=k\\log p+(n-k)\\log(1-p)$. "
            "Setting $\\ell'(p)=0$ yields $\\hat p=$ what in terms of $k$ and $n$? "
            "Enter as k/n."
        ),
        topic_slug="statistics",
        subtopic_slug="maximum-likelihood",
        difficulty=Difficulty.MEDIUM,
        short_answer="k/n",
        canonical_solution=(
            "$\\ell'=k/p-(n-k)/(1-p)=0$ ⇒ $k(1-p)=(n-k)p$ ⇒ $k=np$ ⇒ $\\hat p=k/n$."
        ),
        estimated_time_seconds=240,
        prerequisites=("Log-likelihood",),
    ),
    # --- Linear Regression ---
    QuestionSeed(
        seed_key="stats-013",
        title="OLS Intercept from Means",
        body=(
            "In simple OLS, $\\hat\\beta_1=2$, $\\bar x=1$, $\\bar y=5$. What is $\\hat\\beta_0$?"
        ),
        topic_slug="statistics",
        subtopic_slug="regression",
        difficulty=Difficulty.EASY,
        short_answer="3",
        canonical_solution="$\\hat\\beta_0=\\bar y-\\hat\\beta_1\\bar x=5-2\\cdot 1=3$.",
        estimated_time_seconds=60,
        prerequisites=("OLS intercept",),
    ),
    QuestionSeed(
        seed_key="stats-014",
        title="OLS Slope from Sums",
        body=(
            "Given $\\sum(x_i-\\bar x)(y_i-\\bar y)=10$ and $\\sum(x_i-\\bar x)^2=5$, "
            "what is $\\hat\\beta_1$?"
        ),
        topic_slug="statistics",
        subtopic_slug="regression",
        difficulty=Difficulty.EASY,
        short_answer="2",
        canonical_solution="$\\hat\\beta_1=10/5=2$.",
        estimated_time_seconds=60,
        prerequisites=("OLS slope",),
    ),
    QuestionSeed(
        seed_key="stats-015",
        title="Residual Orthogonality Check",
        body=(
            "In OLS with an intercept column, what must $\\sum_i e_i$ equal? "
            "(Residuals $e_i=y_i-\\hat y_i$.)"
        ),
        topic_slug="statistics",
        subtopic_slug="regression",
        difficulty=Difficulty.MEDIUM,
        short_answer="0",
        canonical_solution=(
            "Residuals are orthogonal to the columns of $X$; with an intercept column, "
            "$\\sum e_i=0$."
        ),
        estimated_time_seconds=120,
        prerequisites=("Normal equations / orthogonality",),
    ),
    # --- Bias–Variance ---
    QuestionSeed(
        seed_key="stats-016",
        title="MSE Decomposition",
        body=(
            "If $\\mathrm{Bias}(\\hat\\theta)=1$ and $\\mathrm{Var}(\\hat\\theta)=3$, "
            "what is $\\mathrm{MSE}(\\hat\\theta)$?"
        ),
        topic_slug="statistics",
        subtopic_slug="bias-variance",
        difficulty=Difficulty.EASY,
        short_answer="4",
        canonical_solution="$\\mathrm{MSE}=\\mathrm{Var}+\\mathrm{Bias}^2=3+1=4$.",
        estimated_time_seconds=60,
        common_mistakes=("Adding bias instead of bias squared",),
        prerequisites=("MSE = Var + Bias²",),
    ),
    QuestionSeed(
        seed_key="stats-017",
        title="Overfit in Bias–Variance Terms",
        body=(
            "A model that interpolates noisy training data but jumps around across repeated samples "
            "typically has: low bias and high variance, or high bias and low variance? "
            "Answer low-bias-high-variance or high-bias-low-variance."
        ),
        topic_slug="statistics",
        subtopic_slug="bias-variance",
        difficulty=Difficulty.EASY,
        short_answer="low-bias-high-variance",
        canonical_solution=(
            "Overfitting: flexible fit (low bias) that is unstable across samples (high variance)."
        ),
        estimated_time_seconds=90,
        prerequisites=("Bias–variance tradeoff",),
    ),
    QuestionSeed(
        seed_key="stats-018",
        title="Averaging Reduces Variance",
        body=(
            "Estimating a constant mean with IID noise: how does $\\mathrm{Var}(\\bar X)$ scale with $n$? "
            "Enter the factor as 1/n, 1/sqrt(n), or n."
        ),
        topic_slug="statistics",
        subtopic_slug="bias-variance",
        difficulty=Difficulty.EASY,
        short_answer="1/n",
        canonical_solution=(
            "$\\mathrm{Var}(\\bar X)=\\sigma^2/n$ scales as $1/n$ (SE scales as $1/\\sqrt n$)."
        ),
        estimated_time_seconds=90,
        common_mistakes=("Confusing variance scaling with SE scaling",),
        prerequisites=("Variance of the mean",),
    ),
)
