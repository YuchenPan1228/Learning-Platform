from app.models.enums import Difficulty
from app.seeds.data.question_seed import QuestionSeed

FINANCE_QUESTIONS: tuple[QuestionSeed, ...] = (
    # --- Derivatives Payoffs & Parity ---
    QuestionSeed(
        seed_key="fin-001",
        title="Put–Call Parity with Zero Rates",
        body=(
            "European options, $S_0=100$, $K=100$, $r=0$, no dividends. "
            "If $C=10$, what must $P$ be under put–call parity?"
        ),
        topic_slug="finance",
        subtopic_slug="derivatives",
        difficulty=Difficulty.EASY,
        short_answer="10",
        canonical_solution=("$r=0$ ⇒ $C-P=S_0-K=0$ ⇒ $P=C=10$."),
        estimated_time_seconds=120,
        common_mistakes=("Using $C-P=S-K e^{-rT}$ without setting $r=0$",),
        prerequisites=("Put–call parity",),
    ),
    QuestionSeed(
        seed_key="fin-002",
        title="Forward Price No Dividends",
        body=("$S_0=100$, continuous $r=0$, $T=1$. What is the no-dividend forward price $F$?"),
        topic_slug="finance",
        subtopic_slug="derivatives",
        difficulty=Difficulty.EASY,
        short_answer="100",
        canonical_solution="$F=S_0 e^{rT}=100\\cdot e^{0}=100$.",
        estimated_time_seconds=60,
        prerequisites=("Forward pricing",),
    ),
    QuestionSeed(
        seed_key="fin-003",
        title="Call Payoff at Expiry",
        body=("A European call with $K=50$ expires with $S_T=60$. What is the payoff?"),
        topic_slug="finance",
        subtopic_slug="derivatives",
        difficulty=Difficulty.EASY,
        short_answer="10",
        canonical_solution="Payoff $=(S_T-K)^+=(60-50)^+=10$.",
        estimated_time_seconds=45,
        prerequisites=("Call payoff",),
    ),
    # --- Black–Scholes ---
    QuestionSeed(
        seed_key="fin-004",
        title="Zero-Vol Call Limit",
        body=(
            "In Black–Scholes with $r=q=0$ and $S_0>K$, as $\\sigma\\to 0$ with $T>0$ fixed, "
            "the European call price approaches what? Enter $S_0-K$ or $0$."
        ),
        topic_slug="finance",
        subtopic_slug="black-scholes",
        difficulty=Difficulty.MEDIUM,
        short_answer="S_0-K",
        canonical_solution=(
            "With $r=q=0$ and $F=S_0>K$, zero vol ⇒ call → $S_0-K$ (discounted intrinsic / forward claim)."
        ),
        estimated_time_seconds=180,
        common_mistakes=('Answering 0 because "no uncertainty"',),
        prerequisites=("Black–Scholes limits",),
    ),
    QuestionSeed(
        seed_key="fin-005",
        title="d2 vs d1 Gap",
        body=(
            "In Black–Scholes, $d_2=d_1 - \\sigma\\sqrt{T}$. If $\\sigma=0.2$ and $T=1$, "
            "what is $d_1-d_2$?"
        ),
        topic_slug="finance",
        subtopic_slug="black-scholes",
        difficulty=Difficulty.EASY,
        short_answer="0.2",
        canonical_solution="$d_1-d_2=\\sigma\\sqrt{T}=0.2\\cdot 1=0.2$.",
        estimated_time_seconds=60,
        prerequisites=("Black–Scholes $d_1,d_2$",),
    ),
    QuestionSeed(
        seed_key="fin-006",
        title="Put–Call Check After BS",
        body=(
            "No dividends, $r=0$, $S_0=K=100$. A BS call is quoted at $8$. "
            "What must the BS put be (parity)?"
        ),
        topic_slug="finance",
        subtopic_slug="black-scholes",
        difficulty=Difficulty.EASY,
        short_answer="8",
        canonical_solution="$C-P=S_0-K=0$ ⇒ $P=C=8$.",
        estimated_time_seconds=90,
        prerequisites=(
            "Put–call parity",
            "Black–Scholes",
        ),
    ),
    # --- Greeks ---
    QuestionSeed(
        seed_key="fin-007",
        title="ATM Call Delta Rough",
        body=(
            "Approximately what delta does an at-the-money call have (no yield, rough interview answer)? "
            "Enter 0.5 or 1."
        ),
        topic_slug="finance",
        subtopic_slug="greeks",
        difficulty=Difficulty.EASY,
        short_answer="0.5",
        canonical_solution="ATM call delta is roughly $1/2$ (50Δ) before dividends / skew nuances.",
        estimated_time_seconds=60,
        prerequisites=("Delta",),
    ),
    QuestionSeed(
        seed_key="fin-008",
        title="Where Gamma Peaks",
        body=(
            "For a vanilla option, where is gamma typically largest: deep ITM, deep OTM, or near ATM? "
            "Answer ITM, OTM, or ATM."
        ),
        topic_slug="finance",
        subtopic_slug="greeks",
        difficulty=Difficulty.EASY,
        short_answer="ATM",
        canonical_solution="Gamma (and usually vega) peak near at-the-money, especially for short-dated options.",
        estimated_time_seconds=60,
        prerequisites=("Gamma",),
    ),
    QuestionSeed(
        seed_key="fin-009",
        title="Short Gamma After a Jump",
        body=(
            "You are short an ATM call and delta-hedged. Spot jumps up sharply. "
            "On gamma, are you happy or unhappy? Answer happy or unhappy."
        ),
        topic_slug="finance",
        subtopic_slug="greeks",
        difficulty=Difficulty.MEDIUM,
        short_answer="unhappy",
        canonical_solution=(
            "Short call ⇒ short gamma. A large move forces rehedging against you (buy high / sell low)."
        ),
        estimated_time_seconds=120,
        prerequisites=("Gamma hedging",),
    ),
    # --- Mean–Variance Portfolios ---
    QuestionSeed(
        seed_key="fin-010",
        title="Equal-Weight Zero Correlation Vol",
        body=(
            "Two assets with $\\sigma_1=\\sigma_2=\\sigma$ and $\\rho=0$, equal weight $w=1/2$. "
            "What is $\\sigma_p$ in terms of $\\sigma$? Enter like sigma/sqrt(2)."
        ),
        topic_slug="finance",
        subtopic_slug="portfolio-theory",
        difficulty=Difficulty.MEDIUM,
        short_answer="sigma/sqrt(2)",
        canonical_solution=(
            "$\\sigma_p^2=2\\cdot(1/4)\\sigma^2=\\sigma^2/2$ ⇒ $\\sigma_p=\\sigma/\\sqrt{2}$."
        ),
        estimated_time_seconds=180,
        prerequisites=("Portfolio variance",),
    ),
    QuestionSeed(
        seed_key="fin-011",
        title="Sharpe Ratio Value",
        body=(
            "$\\mu_p=10\\%$, $r_f=2\\%$, $\\sigma_p=16\\%$. What is the Sharpe ratio? "
            "Enter as a decimal (e.g. 0.5)."
        ),
        topic_slug="finance",
        subtopic_slug="portfolio-theory",
        difficulty=Difficulty.EASY,
        short_answer="0.5",
        canonical_solution="Sharpe $=(\\mu_p-r_f)/\\sigma_p=(0.10-0.02)/0.16=0.5$.",
        estimated_time_seconds=90,
        prerequisites=("Sharpe ratio",),
    ),
    QuestionSeed(
        seed_key="fin-012",
        title="Perfect Correlation Diversification",
        body=(
            "If $\\rho=1$ and $\\sigma_1=\\sigma_2=\\sigma$, equal weight, what is $\\sigma_p$? "
            "Enter sigma or sigma/sqrt(2)."
        ),
        topic_slug="finance",
        subtopic_slug="portfolio-theory",
        difficulty=Difficulty.EASY,
        short_answer="sigma",
        canonical_solution=(
            "With $\\rho=1$, the portfolio is like a single risk factor: $\\sigma_p=\\sigma$. "
            "No diversification benefit."
        ),
        estimated_time_seconds=120,
        prerequisites=("Diversification",),
    ),
    # --- CAPM & Beta ---
    QuestionSeed(
        seed_key="fin-013",
        title="CAPM Expected Return",
        body=(
            "$r_f=2\\%$, $E[R_m]=8\\%$, $\\beta=1.5$. What is CAPM $E[R_i]$ in percent? "
            "Enter the number only (e.g. 11)."
        ),
        topic_slug="finance",
        subtopic_slug="capm",
        difficulty=Difficulty.EASY,
        short_answer="11",
        canonical_solution="$E[R_i]=2+1.5\\cdot(8-2)=2+9=11$.",
        estimated_time_seconds=90,
        prerequisites=("CAPM SML",),
    ),
    QuestionSeed(
        seed_key="fin-014",
        title="Beta Definition Pieces",
        body=("$\\mathrm{Cov}(R_i,R_m)=0.03$ and $\\mathrm{Var}(R_m)=0.02$. What is $\\beta_i$?"),
        topic_slug="finance",
        subtopic_slug="capm",
        difficulty=Difficulty.EASY,
        short_answer="1.5",
        canonical_solution="$\\beta=\\mathrm{Cov}/\\mathrm{Var}=0.03/0.02=1.5$.",
        estimated_time_seconds=60,
        prerequisites=("Beta",),
    ),
    QuestionSeed(
        seed_key="fin-015",
        title="Market Beta",
        body=("In CAPM, what is the beta of the market portfolio itself?"),
        topic_slug="finance",
        subtopic_slug="capm",
        difficulty=Difficulty.EASY,
        short_answer="1",
        canonical_solution="$\\beta_m=\\mathrm{Cov}(R_m,R_m)/\\mathrm{Var}(R_m)=1$.",
        estimated_time_seconds=45,
        prerequisites=("Beta",),
    ),
    # --- Fixed Income Basics ---
    QuestionSeed(
        seed_key="fin-016",
        title="Bond Price vs Yield Direction",
        body=(
            "If yields rise, existing fixed-rate bond prices generally: rise or fall? "
            "Answer rise or fall."
        ),
        topic_slug="finance",
        subtopic_slug="fixed-income",
        difficulty=Difficulty.EASY,
        short_answer="fall",
        canonical_solution="Prices move inversely to yields (discounting cashflows at higher rates).",
        estimated_time_seconds=45,
        prerequisites=("Price–yield",),
    ),
    QuestionSeed(
        seed_key="fin-017",
        title="One-Year Zero Price",
        body=("Face 100, continuous yield $y=0$ for one year. What is the zero's price?"),
        topic_slug="finance",
        subtopic_slug="fixed-income",
        difficulty=Difficulty.EASY,
        short_answer="100",
        canonical_solution="$P=100 e^{-yT}=100$ when $y=0$.",
        estimated_time_seconds=45,
        prerequisites=("Zero bond",),
    ),
    QuestionSeed(
        seed_key="fin-018",
        title="DV01 Meaning",
        body=(
            "DV01 is the approximate dollar change in price for a move of how many basis points? "
            "Enter 1 or 100."
        ),
        topic_slug="finance",
        subtopic_slug="fixed-income",
        difficulty=Difficulty.EASY,
        short_answer="1",
        canonical_solution="DV01 ≈ dollar value of a 1bp yield move.",
        estimated_time_seconds=60,
        prerequisites=("DV01",),
    ),
    # --- Market Microstructure ---
    QuestionSeed(
        seed_key="fin-019",
        title="Quoted Spread Width",
        body=("Bid $99.90$, ask $100.10$. What is the quoted spread?"),
        topic_slug="finance",
        subtopic_slug="market-microstructure",
        difficulty=Difficulty.EASY,
        short_answer="0.2",
        canonical_solution="Spread $=\\mathrm{ask}-\\mathrm{bid}=100.10-99.90=0.20$.",
        estimated_time_seconds=45,
        prerequisites=("Bid–ask spread",),
    ),
    QuestionSeed(
        seed_key="fin-020",
        title="Mid Price",
        body=("Bid $99.90$, ask $100.10$. What is the mid?"),
        topic_slug="finance",
        subtopic_slug="market-microstructure",
        difficulty=Difficulty.EASY,
        short_answer="100",
        canonical_solution="Mid $=(\\mathrm{bid}+\\mathrm{ask})/2=100$.",
        estimated_time_seconds=45,
        prerequisites=("Mid",),
    ),
    QuestionSeed(
        seed_key="fin-021",
        title="Adverse Selection Markout",
        body=(
            "You buy at the ask $100.1$. One minute later the mid is $99.8$. "
            "Was your markout positive or negative? Answer positive or negative."
        ),
        topic_slug="finance",
        subtopic_slug="market-microstructure",
        difficulty=Difficulty.MEDIUM,
        short_answer="negative",
        canonical_solution=(
            "Paid $100.1$; mid fell to $99.8$ ⇒ negative markout, consistent with adverse selection / toxic flow."
        ),
        estimated_time_seconds=90,
        prerequisites=("Adverse selection",),
    ),
)
