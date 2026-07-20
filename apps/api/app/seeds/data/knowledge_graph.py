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
    worked_example: str | None = None
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
        slug='counting',
        name='Counting & Sample Spaces',
        topic_slug='counting',
        definition='A finite probability problem starts by fixing the sample space $\\Omega$ — the set of equally likely outcomes you treat as atomic — then counting the favorable outcomes. Permutations count ordered arrangements; combinations count unordered selections. Almost every classic interview probability question is $|\\mathrm{favorable}| / |\\Omega|$ once $\\Omega$ is chosen correctly.',
        formula='$P(A) = |A| / |\\Omega|$\n$P(n,k) = n! / (n-k)!$\n$C(n,k) = n! / (k!(n-k)!)$\nWith repetition / independent trials: often $|\\Omega| = n^k$',
        intuition="Before writing a formula, ask: what are the atoms I'm counting? If outcomes are not equally likely, either reweight them or rebuild $\\Omega$ so they are. Order matters only when the experiment distinguishes sequences (dealing in order, sequences of flips). If the problem only cares about the set of items, use combinations.",
        worked_example='Q: Two fair six-sided dice are rolled. Probability the sum is 7?\n\nSolve: Take $\\Omega$ = all ordered pairs $(i,j)$ with $i,j \\in \\{1,\\ldots,6\\}$ → $|\\Omega| = 36$. Favorable: $(1,6)$, $(2,5)$, $(3,4)$, $(4,3)$, $(5,2)$, $(6,1)$ → 6 outcomes. $P = 6/36 = 1/6$.\n\nOrdered pairs are safer in interviews than unordered pairs with ad-hoc weights.',
        interview_tips='1. Say out loud: "I\'ll take $\\Omega$ to be …" and whether outcomes are equally likely.\n2. State whether order/repetition matter before picking $P$, $C$, or $n^k$.\n3. Prefer complement for "at least one" / birthday-style problems.\n4. Sanity-check: probability in $[0,1]$, and small cases ($n=2$) you can enumerate by hand.',
        prerequisites='None — first concept on the Probability path.',
    ),
    "independence": ConceptSeed(
        slug='independence',
        name='Independence',
        topic_slug='independence',
        definition="Two events are independent if learning that one occurred does not change the probability of the other: $P(A \\mid B) = P(A)$ (when $P(B) > 0$). Equivalently, $P(A \\cap B) = P(A)P(B)$. For random variables, independence means the joint distribution factors into the product of the margins — knowing one variable's value gives no information about the other.",
        formula='Events: $P(A \\cap B) = P(A)P(B) \\iff P(A \\mid B) = P(A)$\nFinite collection: $P(A_1 \\cap \\cdots \\cap A_n) = P(A_1)\\cdots P(A_n)$ (mutual; pairwise is weaker)\nDiscrete RVs: $P(X = x, Y = y) = P(X = x)P(Y = y)$\nContinuous RVs: $f_{X,Y}(x,y) = f_X(x)f_Y(y)$',
        intuition='Independence is a modeling assumption about information, not about "looking unrelated." Disjoint events with positive probability are dependent (if $A$ happened, $B$ cannot have). Coin flips and dice rolls are independent when the physical process does not couple them. In interviews, independence is what lets you multiply probabilities and what fails when sampling without replacement or conditioning on a shared constraint.',
        worked_example="Q: Three fair coins are flipped independently. Probability all three are heads?\n\nSolve: Independence ⇒ $P(HHH) = P(H)P(H)P(H) = (1/2)^3 = 1/8$.\n\nContrast (dependence): Draw two cards without replacement from a 52-card deck. $P(\\text{both aces}) \\neq (4/52)^2$ — use $P = (4/52)\\cdot(3/51)$ because the second draw's odds change after the first ace.",
        interview_tips='1. Say explicitly whether trials are independent before multiplying.\n2. Check the experiment: with replacement / separate coins → usually independent; without replacement / shared totals → usually not.\n3. Pairwise independence $\\neq$ mutual independence — if the problem needs $P(\\text{all})$, verify the full product (or enumerate a small $\\Omega$).\n4. After conditioning, previously independent events can become dependent (and vice versa) — re-check on the new sample space.',
        prerequisites='Counting & Sample Spaces',
    ),
    "conditional-probability": ConceptSeed(
        slug='conditional-probability',
        name='Conditional Probability',
        topic_slug='conditional-probability',
        definition='$P(A \\mid B)$ is the probability of $A$ given that $B$ occurred: restrict attention to outcomes in $B$ and renormalize. Formally $P(A \\mid B) = P(A \\cap B) / P(B)$ when $P(B) > 0$. Conditioning updates the sample space; it does not change the underlying experiment after the fact — it changes what you treat as possible.',
        formula='$P(A \\mid B) = P(A \\cap B) / P(B)$\n$P(A \\cap B) = P(A \\mid B)P(B)$  (chain rule)\nFor partitions: often easier via tables or enumeration than raw formula',
        intuition='Think "of the worlds consistent with $B$, what fraction also have $A$?" The classic trap is treating "given at least one heads" as if a specific coin were heads. Always rebuild $\\Omega$ under the condition before counting.',
        worked_example='Q: Two fair coins. Given at least one heads, $P(\\text{both heads})$?\n\nSolve: Unconditional $\\Omega = \\{HH, HT, TH, TT\\}$. Condition on $\\{HH, HT, TH\\}$. Only $HH$ works → $1/3$, not $1/2$.',
        interview_tips='1. Name $A$ and $B$ in words before writing symbols.\n2. Prefer listing the conditional sample space when $|\\Omega|$ is small.\n3. Never swap $P(A\\mid B)$ and $P(B\\mid A)$.\n4. Ask whether the information is "at least one" vs "a specific one."',
        prerequisites='Counting & Sample Spaces',
    ),
    "bayes": ConceptSeed(
        slug='bayes',
        name="Bayes' Rule",
        topic_slug='bayes',
        definition="Bayes' rule converts a likelihood $P(\\text{evidence} \\mid \\text{hypothesis})$ and a prior $P(\\text{hypothesis})$ into a posterior $P(\\text{hypothesis} \\mid \\text{evidence})$. The denominator is the law of total probability — sum (or integrate) over all ways the evidence could arise.",
        formula='$P(H \\mid E) = P(E \\mid H)P(H) / P(E)$\n$P(E) = \\sum_i P(E \\mid H_i)P(H_i)$  (discrete partition)\nOdds form: posterior odds = likelihood ratio $\\times$ prior odds',
        intuition='Rare diseases + accurate tests still yield modest posteriors when the base rate is tiny. Interviewers care that you respect the prior and expand $P(\\text{evidence})$ over competing hypotheses — not that you memorize a slogan.',
        worked_example='Q: Disease rate 1%. Test 95% sensitive and 95% specific. Given positive, $P(\\text{disease})$?\n\nSolve: Among 10,000 people: 100 diseased → 95 true +, 9,900 healthy → $\\sim$495 false +. Posterior $\\approx 95 / (95+495) \\approx 16\\%$, not $95\\%$.',
        interview_tips='1. Write prior, likelihood, then expand the denominator.\n2. Use counts (10,000 people) when percentages confuse.\n3. Sanity-check: posterior moves toward hypotheses that explain the data better.\n4. State independence assumptions when multiplying observations.',
        prerequisites='Conditional Probability, Independence',
    ),
    "random-variables": ConceptSeed(
        slug='random-variables',
        name='Random Variables',
        topic_slug='random-variables',
        definition='A random variable is a numerical function of the outcome: $X: \\Omega \\to \\mathbb{R}$. Discrete RVs take countable values with a PMF $p(x) = P(X=x)$. Continuous RVs have a density $f$ with $P(X \\in A) = \\int_A f$. The CDF $F(x) = P(X \\leq x)$ always exists and is the common language between discrete and continuous.',
        formula="PMF: $P(X = x)$ · CDF: $F(x) = P(X \\le x)$\nContinuous: $P(a < X \\le b) = \\int_a^b f(x)\\,dx$, $f = F'$ when $F$ is absolutely continuous\nIndicator: $1_A(\\omega) = 1$ if $\\omega\\in A$ else $0$ — the bridge to expectation tricks",
        intuition='Outcomes can be messy (cards, paths); RVs extract the number you care about (profit, waiting time, count of successes). Once $X$ is defined, stop narrating the story and work with its distribution.',
        worked_example='Q: Flip a fair coin twice. Let $X$ = number of heads.\n\nSolve: $X \\in \\{0,1,2\\}$ with PMF $1/4$, $1/2$, $1/4$. CDF jumps at $0,1,2$. Same experiment, different RV: $Y = 1$ if first flip heads else $0$ — Bernoulli$(1/2)$.',
        interview_tips='1. Define $X$ in one sentence before computing anything.\n2. Discrete vs continuous changes tools (sums vs integrals), not the story.\n3. Indicators turn events into RVs — often the cleanest setup.\n4. For "distribution of $X$," give PMF/PDF or CDF, not just $E[X]$.',
        prerequisites='Counting & Sample Spaces',
    ),
    "expectation": ConceptSeed(
        slug='expectation',
        name='Expectation',
        topic_slug='expectation',
        definition='Expectation is the probability-weighted average of a random variable: for discrete $X$, $E[X] = \\sum x\\, P(X=x)$. It is linear always: $E[aX+bY] = aE[X]+bE[Y]$ with no independence required. Indicator and linearity tricks solve many interview problems without expanding the full distribution.',
        formula='Discrete: $E[X] = \\sum x\\, p(x)$ · Continuous: $E[X] = \\int x f(x)\\,dx$\n$E[g(X)] = \\sum g(x)p(x)$  (LOTUS)\n$E[1_A] = P(A)$ · Linearity always · If independent: $E[XY]=E[X]E[Y]$\nGeometric (trials until first success, success prob $p$): $E[N] = 1/p$',
        intuition='$E[X]$ is the long-run average per trial, not the "most likely" value and not something that must be a possible outcome. Geometric waiting times and coupon collector are expectation problems first, distribution problems second.',
        worked_example='Q: Expected fair die rolls until first six?\n\nSolve: Geometric with $p=1/6$ → $E[N]=6$.\nCoupon flavor: $n$ coupons, $E[\\text{time to collect all}] = n(1 + 1/2 + \\cdots + 1/n) \\approx n \\log n$.',
        interview_tips='1. Reach for linearity + indicators before enumerating $\\Omega$.\n2. State whether geometric counts trials-until-success or failures-before-success.\n3. Linearity does not need independence — say that out loud when useful.\n4. $E[X]$ need not be in the support (e.g. die mean $3.5$).',
        prerequisites='Random Variables, Counting & Sample Spaces',
    ),
    "conditional-expectation": ConceptSeed(
        slug='conditional-expectation',
        name='Conditional Expectation',
        topic_slug='conditional-expectation',
        definition='$E[X \\mid Y=y]$ is the expectation of $X$ under the conditional law of $X$ given $Y=y$. As a random variable, $E[X \\mid Y]$ is a function of $Y$. Tower property: $E[E[X \\mid Y]] = E[X]$. Known information can be pulled out: if $Z$ is $Y$-measurable, $E[ZX \\mid Y] = Z\\, E[X \\mid Y]$.',
        formula='Discrete: $E[X \\mid Y=y] = \\sum x\\, P(X=x \\mid Y=y)$\nTower: $E[E[X \\mid \\mathcal{G}]] = E[X]$\nTake out what’s known: $E[g(Y)X \\mid Y] = g(Y)E[X \\mid Y]$\nIf $X \\perp Y$: $E[X \\mid Y] = E[X]$',
        intuition='Conditioning replaces $X$ with its best mean-square predictor given what you know. In trading/interview language: update your fair value when news arrives; take out of the conditional expectation anything already determined by that news.',
        worked_example='Q: Fair die $X$. Let $Y = 1$ if $X$ even, else $0$. Find $E[X \\mid Y]$.\n\nSolve: Given $Y=1$ (even): uniform on $\\{2,4,6\\}$ → mean $4$. Given $Y=0$ (odd): uniform on $\\{1,3,5\\}$ → mean $3$. So $E[X \\mid Y] = 4Y + 3(1-Y)$. Check tower: $E[E[X\\mid Y]] = 4\\cdot(1/2)+3\\cdot(1/2)=3.5=E[X]$.',
        interview_tips='1. First compute $E[X \\mid Y=y]$ as a number, then assemble the RV.\n2. Use tower to reduce hard expectations to iterated ones.\n3. "Take out what\'s known" is the main algebraic move.\n4. Independence ⇒ conditional expectation collapses to the unconditional mean.',
        prerequisites='Expectation, Conditional Probability',
    ),
    "variance": ConceptSeed(
        slug='variance',
        name='Variance & Covariance',
        topic_slug='variance',
        definition='$\\mathrm{Var}(X) = E[(X-E[X])^2] = E[X^2]-(E[X])^2$ measures spread. Covariance $\\mathrm{Cov}(X,Y)=E[(X-E[X])(Y-E[Y])]$ measures co-movement; $\\mathrm{Corr} = \\mathrm{Cov}/(\\sigma_X \\sigma_Y)$. Variance of sums expands with covariances; independence (or uncorrelatedness) kills cross terms.',
        formula='$\\mathrm{Var}(aX+b) = a^2\\mathrm{Var}(X)$\n$\\mathrm{Var}(X+Y) = \\mathrm{Var}(X)+\\mathrm{Var}(Y)+2\\mathrm{Cov}(X,Y)$\nIndependent $\\Rightarrow$ $\\mathrm{Var}(X+Y)=\\mathrm{Var}(X)+\\mathrm{Var}(Y)$\n$\\mathrm{Cov}(X,Y)=E[XY]-E[X]E[Y]$\nChebyshev: $P(|X-\\mu| \\ge k\\sigma) \\le 1/k^2$\nMarkov: $P(X \\ge a) \\le E[X]/a$ for $X\\ge 0$, $a>0$',
        intuition='Mean alone does not capture risk. Uncorrelated $\\neq$ independent, but independent ⇒ uncorrelated. Markov/Chebyshev bound probabilities using only mean/variance when the full distribution is unknown.',
        worked_example='Q: $X \\sim \\mathrm{Binomial}(n,p)$. $\\mathrm{Var}(X)$?\n\nSolve: $X$ = sum of $n$ independent Bernoullis ⇒ $\\mathrm{Var}(X)=np(1-p)$.\nCompare: For fixed mean, Bernoulli variance is maximized at $p=1/2$.',
        interview_tips='1. Expand $\\mathrm{Var}(\\mathrm{sum})$ and ask which covariances are zero.\n2. Compute $E[X^2]$ carefully — most algebra mistakes live there.\n3. Use Chebyshev only when you lack a full distribution; it is often loose.\n4. Correlation is scale-free; covariance is not.',
        prerequisites='Expectation',
    ),
    "continuous-distributions": ConceptSeed(
        slug='continuous-distributions',
        name='Common Distributions',
        topic_slug='continuous-distributions',
        definition='Interview distribution fluency means recognizing the named family, knowing mean/variance, and knowing which story generates it. Core discrete: Bernoulli, Binomial, Geometric, Poisson. Core continuous: Uniform, Exponential, Normal. Everything else is usually a transformation or approximation of these.',
        formula='$\\mathrm{Bern}(p)$: $E=p$, $\\mathrm{Var}=p(1-p)$\n$\\mathrm{Bin}(n,p)$: $E=np$, $\\mathrm{Var}=np(1-p)$\n$\\mathrm{Geo}(p)$ trials-until-success: $E=1/p$, $\\mathrm{Var}=(1-p)/p^2$\n$\\mathrm{Poisson}(\\lambda)$: $E=\\mathrm{Var}=\\lambda$\n$\\mathrm{Unif}[a,b]$: $E=(a+b)/2$, $\\mathrm{Var}=(b-a)^2/12$\n$\\mathrm{Exp}(\\lambda)$: $E=1/\\lambda$, memoryless\n$N(\\mu,\\sigma^2)$: sums of independents stay normal; standardize $(X-\\mu)/\\sigma$',
        intuition='Match the story first: fixed trials with success/fail → Binomial; waiting for first success → Geometric; rare events in continuum → Poisson; memoryless waits → Exponential; noise / CLT limits → Normal.',
        worked_example='Q: $P(U > 0.7)$ for $U \\sim \\mathrm{Unif}[0,1]$?\n\nSolve: Length of favorable interval → $0.3$.\nPoisson setup: $n$ large, $p$ small, $np=\\lambda$ → Binomial $\\approx$ Poisson$(\\lambda)$.',
        interview_tips="1. Name the distribution and parameters before computing.\n2. Confirm geometric/exponential convention (trials vs failures; rate vs scale).\n3. Use Poisson/Normal approximations only when asymptotics are plausible — say the regime.\n4. Memoryless ⇒ past wait doesn't help; that's Exponential/Geometric.",
        prerequisites='Random Variables, Expectation, Variance & Covariance',
    ),
    "limit-theorems": ConceptSeed(
        slug='limit-theorems',
        name='Limit Theorems (LLN & CLT)',
        topic_slug='limit-theorems',
        definition='LLN: sample averages converge to the mean (law of large numbers) — intuition for long-run frequency. CLT: properly scaled averages become approximately Normal — the reason $\\sqrt{n}$ rates and $z$-scores appear everywhere. Interviews want correct statements and when approximations apply, not measure-theoretic proofs.',
        formula='IID $X_i$ with $E[X_i]=\\mu$, $\\mathrm{Var}=\\sigma^2\\in(0,\\infty)$:\n$\\bar{X}_n \\to \\mu$  (LLN)\n$\\sqrt{n}(\\bar{X}_n - \\mu)/\\sigma \\xrightarrow{d} N(0,1)$  (CLT)\nBinomial/Poisson Normal approximations are CLT special cases',
        intuition='More independent noise averages out (LLN). Fluctuations around the mean are typically Gaussian on the $1/\\sqrt{n}$ scale (CLT). Dependence, heavy tails, or tiny $n$ break the slogan — say so.',
        worked_example='Q: 100 fair coin flips. Approx $P(\\text{more than 60 heads})$?\n\nSolve: $X\\sim\\mathrm{Bin}(100,1/2)$, mean $50$, sd $5$. $P(X>60) \\approx P\\big(Z > (60.5-50)/5\\big) \\approx P(Z>2.1) \\approx 1.8\\%$ (continuity correction optional but impressive if stated).',
        interview_tips="1. State IID + finite variance assumptions.\n2. Continuity correction for discrete→Normal when $n$ is moderate.\n3. LLN is about averages converging; CLT is about $\\sqrt{n}$ fluctuations.\n4. Don't invoke CLT for $n=2$ unless joking — and don't.",
        prerequisites='Expectation, Variance & Covariance',
    ),
    "markov-chains": ConceptSeed(
        slug='markov-chains',
        name='Markov Chains',
        topic_slug='markov-chains',
        definition='A Markov chain is a process where the next state depends only on the present: $P(X_{n+1}\\mid X_n,\\ldots,X_0)=P(X_{n+1}\\mid X_n)$. Finite-state chains are described by a transition matrix $P$. Stationary distributions $\\pi$ satisfy $\\pi^{\\top}P = \\pi^{\\top}$ (row-vector convention varies — pick one and stick to it).',
        formula='$P_{ij} = P(\\text{go to } j \\mid \\text{at } i)$\nn-step: $P^{(n)} = P^n$\nStationary: $\\pi = \\pi P$, $\\sum_i \\pi_i = 1$\nFirst-step: condition on the first transition to get hitting-time expectations',
        intuition='Memoryless given the present state. Long-run fraction of time in a state is the stationary mass (when the chain is irreducible + aperiodic on a finite space). Interviews love two-state chains and first-step equations.',
        worked_example='Q: States $\\{0,1\\}$, $P(0\\to 1)=p$, $P(1\\to 0)=q$. Stationary?\n\nSolve: $\\pi_0 p = \\pi_1 q$ and $\\pi_0+\\pi_1=1$ ⇒ $\\pi_0 = q/(p+q)$, $\\pi_1 = p/(p+q)$.',
        interview_tips='1. Draw the state diagram before algebra.\n2. Write balance equations + normalize.\n3. First-step analysis for expected hitting times.\n4. Say irreducible/aperiodic when claiming a unique long-run limit.',
        prerequisites='Random Variables, Conditional Probability',
    ),
    "martingales": ConceptSeed(
        slug='martingales',
        name='Martingales',
        topic_slug='martingales',
        definition='A process $M_n$ is a martingale if it is integrable and $E[M_{n+1} \\mid \\text{past}] = M_n$ — fair game: conditional on what you know, tomorrow\'s expectation equals today\'s value. Optional stopping theorems need conditions; naive "stopped martingale stays fair" is a common interview trap (e.g. betting until you win).',
        formula='$E[M_{n+1} \\mid \\mathcal{F}_n] = M_n$\n$\\Rightarrow E[M_n] = E[M_0]$ for all $n$\nDoob: $M_n = E[X \\mid \\mathcal{F}_n]$ is a martingale\nStopped process: need bounded time / bounded increments / UI hypotheses for $E[M_\\tau]=E[M_0]$',
        intuition='Martingales formalize "no free lunch given current information." Random walks with mean-zero steps are the basic example. Stopping rules can break fairness if the stopping time is unbounded or increments are uncontrolled.',
        worked_example='Q: Fair coin: win $+1$ or $-1$ each bet. Fortune after $n$ bets is $S_n$. Martingale?\n\nSolve: $E[S_{n+1}\\mid S_n] = S_n + E[\\text{next}]=S_n$, so yes.\nTrap: Stop at first time you are ahead by $1$ — stopping time may be unbounded; you must check optional-stopping conditions before claiming $E[S_\\tau]=E[S_0]$.',
        interview_tips='1. Verify the conditional-expectation definition, don\'t just say "fair."\n2. Construct examples from conditional expectations: $M_n = E[X \\mid \\mathcal{F}_n]$.\n3. Before optional stopping, check bounded time / bounded increments / UI.\n4. Related to Markov: functions of Markov chains can be martingales under the right setup.',
        prerequisites='Conditional Expectation, Markov Chains',
    ),
    "vectors-matrices": ConceptSeed(
        slug='vectors-matrices',
        name='Vectors & Matrices',
        topic_slug='vectors-matrices',
        definition='A vector is an ordered tuple of numbers — both a point and a direction in $\\mathbb{R}^n$. A matrix is a rectangular array encoding a linear map: $x \\mapsto Ax$. Interview work is mostly about (1) shapes and legal multiplications, (2) reading $Ax$ as a mix of columns, (3) using transpose to move between row/column views and write dot products, (4) special structure (symmetric, diagonal, outer products), and (5) the cross product in $\\mathbb{R}^3$ for geometry / perpendicular-to-both questions.',
        formula='Dot: $u \\cdot v = u^{\\top}v = \\sum_i u_i v_i$\nMatrix–vector: $(Ax)_i = \\sum_j A_{ij} x_j$ · $A$ is $m\\times n$, $x$ is $n\\times 1 \\to m\\times 1$\nMatrix–matrix: $(AB)_{ij} = \\sum_k A_{ik} B_{kj}$ · need inner dim match\nOuter product: $uv^{\\top}$ (rank $\\le 1$)\nTranspose: $(A^{\\top})_{ij} = A_{ji}$ · $(AB)^{\\top} = B^{\\top}A^{\\top}$ · $(A^{\\top})^{\\top} = A$\nSymmetric: $A = A^{\\top}$ · Skew: $A^{\\top} = -A$ · Inverse: $AA^{-1} = A^{-1}A = I$ when it exists\nCross ($\\mathbb{R}^3$): $u \\times v = (u_2v_3-u_3v_2,\\, u_3v_1-u_1v_3,\\, u_1v_2-u_2v_1)$\n$\\|u \\times v\\| = \\|u\\|\\|v\\|\\lvert\\sin\\theta\\rvert$ · $u \\times v = 0 \\iff$ parallel',
        intuition='$Ax$ is a linear combination of the columns of $A$ with weights from $x$; the $i$-th entry is the $i$-th row of $A$ dotted with $x$. Transpose swaps rows and columns and turns row actions into column actions — if $A$ maps $\\mathbb{R}^n \\to \\mathbb{R}^m$, then $A^{\\top}$ maps $\\mathbb{R}^m \\to \\mathbb{R}^n$. Symmetric matrices ($A=A^{\\top}$) are the ones quadratic forms $x^{\\top}Ax$ "see" (replace $A$ by $(A+A^{\\top})/2$ if needed). Cross product $u \\times v$ in $\\mathbb{R}^3$ is orthogonal to both, with length $\\|u\\|\\|v\\|\\sin\\theta$ and right-hand orientation; it vanishes iff the vectors are parallel.',
        worked_example='Example 1 — columns of $A$:\n$A = \\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}$, $v = \\begin{bmatrix}1\\\\0\\end{bmatrix}$ → $Av = \\begin{bmatrix}1\\\\3\\end{bmatrix}$ (first column). $w = \\begin{bmatrix}0\\\\1\\end{bmatrix}$ → $Aw = \\begin{bmatrix}2\\\\4\\end{bmatrix}$ (second column). Knowing $A$ on the standard basis is knowing its columns.\n\nExample 2 — transpose, symmetry, quadratic form:\n$B = \\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}$ ⇒ $B^{\\top} = \\begin{bmatrix}1&3\\\\2&4\\end{bmatrix} \\neq B$ (not symmetric). $S = (B+B^{\\top})/2 = \\begin{bmatrix}1&2.5\\\\2.5&4\\end{bmatrix}$. For $x = \\begin{bmatrix}1\\\\1\\end{bmatrix}$, $x^{\\top}Bx = x^{\\top}Sx = 10$ — same quadratic form. Transpose swaps orientation; symmetry is what quadratic forms see.\n\nExample 3 — outer product:\n$u = \\begin{bmatrix}1\\\\2\\end{bmatrix}$, $v = \\begin{bmatrix}3\\\\4\\end{bmatrix}$ ⇒ $uv^{\\top} = \\begin{bmatrix}3&4\\\\6&8\\end{bmatrix}$. Every column is a multiple of $u$; rank $\\leq 1$.\n\nExample 4 — cross product:\n$u = \\begin{bmatrix}1\\\\0\\\\0\\end{bmatrix}$, $v = \\begin{bmatrix}0\\\\1\\\\0\\end{bmatrix}$ ⇒ $u \\times v = \\begin{bmatrix}0\\\\0\\\\1\\end{bmatrix}$. If $v = \\begin{bmatrix}2\\\\0\\\\0\\end{bmatrix}$ (parallel) ⇒ $u \\times v = 0$.',
        interview_tips='1. Announce shapes before any product ($m \\times n$ times $n \\times p$).\n2. Say "$Ax$ = combination of columns" early in matrix questions.\n3. Use $u^{\\top}v$ for dots; use $uv^{\\top}$ when you need a matrix — don\'t mix them up.\n4. If you see $x^{\\top}Ax$, assume $A$ symmetric / replace by $(A+A^{\\top})/2$.\n5. Cross product only in $\\mathbb{R}^3$ — don\'t invent one in other dimensions.\n6. Left-multiply $PA$ vs right-multiply $AP$ do different things (row vs column ops).',
        prerequisites='None — first concept on the Mathematics path.',
    ),
    "linear-systems": ConceptSeed(
        slug='linear-systems',
        name='Linear Systems & Rank',
        topic_slug='linear-systems',
        definition='A linear system $Ax = b$ asks whether $b$ lies in the column space of $A$. The rank of $A$ is the dimension of that column space (equivalently row space). Full column rank means unique solutions when they exist; full row rank means solutions exist for every $b$. Interview fluency: classify consistent vs inconsistent, unique vs infinite solutions, and read rank from pivots / independent columns — not endless row reduction theater.',
        formula='$Ax = b$ · $A$ is $m\\times n$, $x \\in \\mathbb{R}^n$, $b \\in \\mathbb{R}^m$\n$\\mathrm{rank}(A) = \\dim(\\mathrm{col}(A)) = \\dim(\\mathrm{row}(A)) \\le \\min(m,n)$\nConsistent $\\iff b \\in \\mathrm{col}(A) \\iff \\mathrm{rank}([A|b]) = \\mathrm{rank}(A)$\nUnique solution $\\iff$ consistent and $\\mathrm{rank}(A) = n$ (full column rank)\nNullspace: $N(A) = \\{x : Ax = 0\\}$ · $\\dim N(A) = n - \\mathrm{rank}(A)$ (rank–nullity)\nIf $A$ is square and full rank: unique solution $x = A^{-1}b$',
        intuition='Each equation is a hyperplane; intersections may be a point, a line/plane of solutions, or empty. Columns are the "ingredients" you can mix to make $b$. Free variables parametrize the nullspace — add any nullspace vector to a particular solution. Rank counts how many independent constraints / directions you truly have after removing redundancy.',
        worked_example='Example 1 — unique solution:\n$\\begin{bmatrix}1&0\\\\0&1\\end{bmatrix}\\begin{bmatrix}x\\\\y\\end{bmatrix} = \\begin{bmatrix}3\\\\4\\end{bmatrix}$ ⇒ $(x,y)=(3,4)$. Rank $2 = n$.\n\nExample 2 — infinite solutions:\n$\\begin{bmatrix}1&2\\\\2&4\\end{bmatrix}\\begin{bmatrix}x\\\\y\\end{bmatrix} = \\begin{bmatrix}3\\\\6\\end{bmatrix}$. Second equation is double the first. Rank $1 < n=2$. Particular: $(3,0)$. Nullspace: $t(-2,1)$. General: $(3,0)+t(-2,1)$.\n\nExample 3 — inconsistent:\nSame $A$ but $b = \\begin{bmatrix}3\\\\5\\end{bmatrix}$. $\\mathrm{rank}(A)=1$ but $\\mathrm{rank}([A|b])=2$ ⇒ no solution.\n\nExample 4 — rank–nullity check:\n$A$ is $3 \\times 5$ with rank $2$ ⇒ $\\dim N(A) = 5-2 = 3$ free parameters in the homogeneous solution.',
        interview_tips="1. State the three cases: none / unique / infinitely many.\n2. Compare $\\mathrm{rank}(A)$ to $\\mathrm{rank}([A|b])$ for consistency; compare $\\mathrm{rank}(A)$ to $n$ for uniqueness.\n3. Write general solution as $x_{\\mathrm{particular}}$ + nullspace.\n4. Square invertible is the special case $\\mathrm{rank} = n = m$ — don't assume it.\n5. Underdetermined ($n>m$) often has free variables when consistent.",
        prerequisites='Vectors & Matrices',
    ),
    "eigenvalues": ConceptSeed(
        slug='eigenvalues',
        name='Eigenvalues & Eigenvectors',
        topic_slug='eigenvalues',
        definition="For a square matrix $A$, a nonzero vector $v$ is an eigenvector with eigenvalue $\\lambda$ if $Av = \\lambda v$ — $A$ stretches/flips $v$ without rotating it out of its line. The characteristic equation $\\det(A-\\lambda I)=0$ finds the $\\lambda$'s. Real symmetric matrices are special: real eigenvalues and an orthonormal eigenbasis (spectral theorem). Quadratic forms and covariance matrices live here; positive definite means all eigenvalues $> 0$.",
        formula='$Av = \\lambda v$, $v \\neq 0 \\iff (A-\\lambda I)v = 0 \\iff \\det(A-\\lambda I)=0$\n$\\mathrm{tr}(A) = \\sum \\lambda_i$ · $\\det(A) = \\prod \\lambda_i$ (over algebraic multiplicities / complex)\nDiagonalizable: $A = PDP^{-1}$ with $D=\\mathrm{diag}(\\lambda_i)$\nReal symmetric: $A = Q\\Lambda Q^{\\top}$ with $Q$ orthogonal ($Q^{\\top}Q=I$)\nQuadratic form: $x^{\\top}Ax = \\sum \\lambda_i (q_i^{\\top}x)^2$ in an eigenbasis\nSPD (symmetric positive definite): $x^{\\top}Ax > 0$ for all $x\\neq 0 \\iff$ all $\\lambda_i > 0$',
        intuition='Eigenvectors are the "natural axes" of a linear map. On those axes the map acts by simple scaling. Symmetric maps have orthogonal natural axes — like principal axes of an ellipse. Powers $A^{k}$ become trivial in an eigenbasis: scale by $\\lambda^{k}$. Stability, PCA, and many quant models reduce to reading the spectrum.',
        worked_example='Example 1 — $2 \\times 2$ diagonal:\n$A = \\mathrm{diag}(2,5)$ has $\\lambda=2,5$ with $e_1,e_2$. $A\\begin{bmatrix}1\\\\0\\end{bmatrix} = 2\\begin{bmatrix}1\\\\0\\end{bmatrix}$.\n\nExample 2 — compute spectrum:\n$A = \\begin{bmatrix}2&1\\\\1&2\\end{bmatrix}$. Char poly $(2-\\lambda)^2-1 = \\lambda^2-4\\lambda+3 = (\\lambda-1)(\\lambda-3)$. $\\lambda=1$ with $v\\propto\\begin{bmatrix}1\\\\-1\\end{bmatrix}$; $\\lambda=3$ with $v\\propto\\begin{bmatrix}1\\\\1\\end{bmatrix}$. Symmetric ⇒ eigenvectors orthogonal.\n\nExample 3 — quadratic form / PD:\n$x^{\\top}Ax = 2x_1^2 + 2x_1 x_2 + 2x_2^2$. Eigenvalues $1$ and $3$, both $>0$ ⇒ SPD. Minimum of $x^{\\top}Ax$ on $\\|x\\|=1$ is $\\lambda_{\\min}=1$.\n\nExample 4 — powers:\nIf $Av=\\lambda v$ then $A^{k}v = \\lambda^{k}v$. For $|\\lambda|<1$, $A^{k}v\\to 0$ along that mode.',
        interview_tips='1. Write $Av=\\lambda v$ and $(A-\\lambda I)v=0$ before computing anything.\n2. Use trace/det as sanity checks for the characteristic polynomial.\n3. If $A$ is symmetric/covariance-like, say "real $\\lambda$, orthonormal basis" early.\n4. PD/PSD is about the sign of eigenvalues (or $x^{\\top}Ax$ tests).\n5. Not every matrix is diagonalizable — Jordan issues exist, but interviews usually stick to symmetric or explicitly nice matrices.',
        prerequisites='Vectors & Matrices, Linear Systems & Rank',
    ),
    "orthogonality": ConceptSeed(
        slug='orthogonality',
        name='Orthogonality & Projections',
        topic_slug='orthogonality',
        definition='Vectors $u,v$ are orthogonal if $u^{\\top}v = 0$. An orthogonal set is linearly independent (if nonzero); an orthonormal set has unit lengths too. An orthogonal matrix $Q$ satisfies $Q^{\\top}Q = I$ (columns orthonormal) and preserves lengths: $\\|Qx\\|=\\|x\\|$. The orthogonal projection of $b$ onto $\\mathrm{col}(A)$ is the closest point in that subspace — the heart of least squares.',
        formula='Orthogonal: $u^{\\top}v = 0$ · Orthonormal: $u_i^{\\top}u_j = 0$ ($i\\neq j$) and $\\|u_i\\|=1$\nOrthogonal matrix: $Q^{\\top}Q = I = QQ^{\\top}$ (square) · $Q^{-1} = Q^{\\top}$\nProj onto unit $u$: $(u^{\\top}b)\\, u$\nProj onto orthonormal columns of $Q$: $QQ^{\\top} b$\nLeast squares: $\\min \\|Ax-b\\| \\Rightarrow A^{\\top}A\\hat{x} = A^{\\top}b$ (normal equations)\nIf $A$ has thin QR, $A=QR \\Rightarrow \\hat{x} = R^{-1} Q^{\\top}b$',
        intuition='Orthogonal directions don\'t interfere — coefficients decouple. Projection is "drop a perpendicular" onto a subspace: error $b-\\mathrm{proj}$ is orthogonal to every vector in the subspace (normal equations). Least squares finds the mix of columns of $A$ closest to $b$ when $b$ isn\'t in the column space.',
        worked_example='Example 1 — orthonormal check:\n$u=\\begin{bmatrix}3/5\\\\4/5\\end{bmatrix}$, $v=\\begin{bmatrix}-4/5\\\\3/5\\end{bmatrix}$. $u^{\\top}v=0$ and both unit ⇒ orthonormal basis of $\\mathbb{R}^2$.\n\nExample 2 — project onto a line:\n$b=\\begin{bmatrix}2\\\\2\\end{bmatrix}$ onto $\\mathrm{span}\\{\\begin{bmatrix}1\\\\0\\end{bmatrix}\\}$: $\\mathrm{proj} = 2\\begin{bmatrix}1\\\\0\\end{bmatrix} = \\begin{bmatrix}2\\\\0\\end{bmatrix}$. Error $\\begin{bmatrix}0\\\\2\\end{bmatrix} \\perp \\begin{bmatrix}1\\\\0\\end{bmatrix}$.\n\nExample 3 — least squares for an overdetermined system:\n$A$ has rows $(1,0)$, $(1,1)$, $(1,2)$ and $b=\\begin{bmatrix}1\\\\2\\\\2\\end{bmatrix}$. Normal equations $A^{\\top}A \\hat{x} = A^{\\top}b$ with $A^{\\top}A=\\begin{bmatrix}3&3\\\\3&5\\end{bmatrix}$, $A^{\\top}b=\\begin{bmatrix}5\\\\6\\end{bmatrix}$. Solve: $3x+3y=5$ and $3x+5y=6$ ⇒ $2y=1$ ⇒ $y=1/2$, then $3x=5-3/2=7/2$ ⇒ $x=7/6$. So $\\hat{x}=\\begin{bmatrix}7/6\\\\1/2\\end{bmatrix}$.\n\nExample 4 — $QQ^{\\top}$ projection:\n$Q$ with columns $u,v$ from Example 1: $QQ^{\\top} = I$ in $\\mathbb{R}^2$ (full basis) so proj of any $b$ is $b$. If only first column, $QQ^{\\top} = uu^{\\top}$ projects onto that axis.',
        interview_tips='1. Orthogonal ⇒ independent (for nonzero vectors) — useful for quick arguments.\n2. Write the geometric condition $(b-Ax) \\perp \\mathrm{col}(A)$ to derive $A^{\\top}(b-Ax)=0$.\n3. Prefer QR intuition over memorizing normal equations alone.\n4. Orthogonal matrices preserve norms and angles — mention when discussing stability / rotations.\n5. SVD (light): $A = U\\Sigma V^{\\top}$ rotates, scales axes, rotates again — defer deep SVD proofs unless asked.',
        prerequisites='Vectors & Matrices',
    ),
    "derivatives-gradients": ConceptSeed(
        slug='derivatives-gradients',
        name='Derivatives & Gradients',
        topic_slug='derivatives-gradients',
        definition="The derivative $f'(x)$ is the best linear approximation to how $f$ changes near $x$. In several variables, the gradient $\\nabla f$ is the vector of partial derivatives — direction of steepest ascent, and $\\nabla f \\cdot v$ is the directional derivative. The Hessian $H = D^2 f$ is the matrix of second partials. Chain rule is the interview workhorse for compositions and matrix calculus lite.",
        formula="1D: $f(x+h) \\approx f(x) + f'(x)h$\nGradient: $\\nabla f = (\\partial f/\\partial x_1, \\ldots, \\partial f/\\partial x_n)$\nDirectional derivative: $D_v f = \\nabla f \\cdot v$\nChain rule: $\\frac{d}{dt} f(g(t)) = \\nabla f(g(t)) \\cdot g'(t)$\nHessian: $H_{ij} = \\partial^2 f/(\\partial x_i \\partial x_j)$ · symmetric when mixed partials equal\nQuadratic: $f(x)=\\tfrac{1}{2}x^{\\top}Ax+b^{\\top}x \\Rightarrow \\nabla f = \\tfrac{1}{2}(A+A^{\\top})x+b$ ($A$ if $A$ symmetric)",
        intuition='Derivative = local linear map. Gradient points uphill and is orthogonal to level sets $\\{f=c\\}$. Hessian describes curvature — positive definite Hessian means locally bowl-shaped (local minimum). Most optimization first-order conditions are "gradient equals zero" plus a Hessian test.',
        worked_example="Example 1 — 1D product/chain:\n$f(x)=x^2 \\sin x$ ⇒ $f' = 2x \\sin x + x^2 \\cos x$.\n\nExample 2 — gradient:\n$f(x,y)=x^2 y + e^{y}$ ⇒ $\\nabla f = (2xy,\\, x^2 + e^{y})$. At $(1,0)$: $\\nabla f=(0,2)$.\n\nExample 3 — directional derivative:\nSame $f$ at $(1,0)$, unit direction $v=(1/\\sqrt{2},1/\\sqrt{2})$: $D_v f = \\nabla f\\cdot v = 2/\\sqrt{2} = \\sqrt{2}$.\n\nExample 4 — Hessian / critical point:\n$f(x,y)=x^2+y^2$ ⇒ $\\nabla f=(2x,2y)=0$ at origin, $H=\\mathrm{diag}(2,2)$ SPD ⇒ local (global) min.\n\nExample 5 — chain rule path:\n$f(x,y)=x^2+y^2$, $(x,y)=(t,t^2)$ ⇒ $g(t)=t^2+t^4$, $g'=2t+4t^3 = \\nabla f\\cdot(1,2t)$.",
        interview_tips='1. State what is scalar vs vector vs matrix before differentiating.\n2. For $\\nabla(x^{\\top}Ax)$, symmetrize $A$ first.\n3. Level set $\\Leftrightarrow$ gradient perpendicular — useful geometry check.\n4. Critical points: $\\nabla f=0$, then use Hessian eigenvalues / PD test.\n5. Write chain rule as "outer gradient times inner Jacobian" for compositions.',
        prerequisites='Vectors & Matrices (helpful for multivariable)',
    ),
    "taylor-expansions": ConceptSeed(
        slug='taylor-expansions',
        name='Taylor Expansions',
        topic_slug='taylor-expansions',
        definition='Taylor expansion approximates a smooth function locally by a polynomial built from its derivatives at a point. First order is the tangent linearization; second order adds Hessian curvature. In interviews this is how you approximate returns, option payoffs, logs, exponentials, and objective functions near a known point.',
        formula="1D: $f(x+h) = f(x) + f'(x)h + \\tfrac{1}{2}f''(x)h^2 + \\cdots + R$\nMultivariable: $f(x+h) \\approx f(x) + \\nabla f(x)^{\\top}h + \\tfrac{1}{2} h^{\\top} H(x) h$\nCommon: $e^h \\approx 1+h+\\tfrac{1}{2}h^2$ · $\\log(1+h) \\approx h-\\tfrac{1}{2}h^2$ · $(1+h)^a \\approx 1+ah$\n$\\sin h \\approx h-h^3/6$ · $\\cos h \\approx 1-\\tfrac{1}{2}h^2$ · $1/(1-h) \\approx 1+h+h^2$ ($|h|<1$)",
        intuition="Near a point, smooth functions look like their best polynomial fit. First-order ignores curvature; second-order is the workhorse for local min/max and risk approximations. Always track the order of the remainder — interviews care whether you're $O(h)$ or $O(h^2)$.",
        worked_example='Example 1 — log return approx:\n$\\log(1+r) \\approx r - \\tfrac{1}{2}r^2$. For $r=0.01$: $\\log(1.01)\\approx 0.00995$ vs $0.01 - 0.00005 = 0.00995$.\n\nExample 2 — exp:\n$e^{0.1} \\approx 1 + 0.1 + 0.005 = 1.105$ (true $\\approx 1.10517$).\n\nExample 3 — multivariable second order:\n$f(x,y)=e^{x}\\cos y$ at $(0,0)$: $f=1$, $\\nabla f=(1,0)$, $H=\\begin{bmatrix}1&0\\\\0&-1\\end{bmatrix}$. $f(h,k)\\approx 1 + h + \\tfrac{1}{2}(h^2 - k^2)$.\n\nExample 4 — binomial / power:\n$\\sqrt{1+h} \\approx 1 + \\tfrac{1}{2}h - \\tfrac{1}{8}h^2$. For $h=0.21$: approx $1.105$ vs $\\sqrt{1.21}=1.1$ (first order $1.105$ already close; second order $1.105-0.0055=1.0995$).',
        interview_tips="1. Say the expansion point and the order you keep.\n2. Memorize $e$, $\\log$, $(1+h)^a$, $\\sin/\\cos$ to second order — they appear constantly.\n3. For multivariate, write gradient term + Hessian quadratic form explicitly.\n4. Check a numeric plug-in for small $h$ when time allows.\n5. Don't use small-$h$ expansions for $h=O(1)$ without commenting on error.",
        prerequisites='Derivatives & Gradients',
    ),
    "math-optimization": ConceptSeed(
        slug='math-optimization',
        name='Convexity & Unconstrained Optimization',
        topic_slug='math-optimization',
        definition="Unconstrained optimization seeks min/max of $f$ over all of $\\mathbb{R}^n$. First-order necessary condition: $\\nabla f(x^*)=0$. Second-order: Hessian PD ⇒ local min. Convexity upgrades local to global: a convex function's any local minimum is global, and $\\nabla f=0$ is enough. Interview focus: recognize convex structure, write FOCs, and test Hessians — not run heavy solvers.",
        formula='FOC: $\\nabla f(x^*) = 0$ · SOC min: $H(x^*) \\succ 0$ (PD) · max: $H \\prec 0$\nConvex set: segment between points stays in set\nConvex $f$: $f(tx+(1-t)y) \\le t f(x)+(1-t)f(y)$\nFor smooth $f$: convex $\\iff H \\succeq 0$ (PSD) everywhere\nGradient descent intuition: $x \\leftarrow x - \\eta \\nabla f(x)$',
        intuition="Convex bowls have one valley — any critical point is a global min. Nonconvex landscapes can have many traps; FOC alone isn't enough. Level sets of convex functions are convex. In quant interviews, mean-variance style objectives and least squares are the usual convex examples.",
        worked_example="Example 1 — 1D:\n$f(x)=x^2-4x+1$ ⇒ $f'=2x-4=0$ ⇒ $x=2$, $f''=2>0$ ⇒ global min (convex).\n\nExample 2 — quadratic:\n$f(x)=\\tfrac{1}{2}x^{\\top}Qx - b^{\\top}x$ with $Q$ SPD. $\\nabla f=Qx-b=0$ ⇒ $x^*=Q^{-1}b$. $H=Q\\succ 0$ ⇒ unique global min.\n\nExample 3 — least squares is convex:\n$f(x)=\\|Ax-b\\|^2 = x^{\\top}(A^{\\top}A)x - 2(A^{\\top}b)^{\\top}x + \\|b\\|^2$. $A^{\\top}A$ is PSD ⇒ $f$ convex. FOC recovers normal equations $A^{\\top}A x = A^{\\top}b$.\n\nExample 4 — nonconvex trap:\n$f(x)=x^3/3 - x$ ⇒ $f'=x^2-1=0$ at $\\pm 1$. $f''(1)=2>0$ local min; $f''(-1)=-2<0$ local max. No global min ($f\\to-\\infty$ as $x\\to-\\infty$).",
        interview_tips='1. Always state FOC then SOC / convexity argument for global claims.\n2. "Quadratic with SPD Hessian" ⇒ unique global min — say it.\n3. Convexity is preserved by nonnegative cones of convex functions and by affine composition $f(Ax+b)$.\n4. Distinguish convex set vs convex function if the interviewer mixes terms.\n5. Gradient descent: small enough step, convex smooth ⇒ converges to the min.',
        prerequisites='Derivatives & Gradients',
    ),
    "lagrange-multipliers": ConceptSeed(
        slug='lagrange-multipliers',
        name='Lagrange Multipliers',
        topic_slug='lagrange-multipliers',
        definition='Lagrange multipliers solve equality-constrained optimization: $\\min f(x)$ subject to $g(x)=0$ (or several equalities). At an optimum, $\\nabla f$ is normal to the constraint surface — parallel to $\\nabla g$ — so $\\nabla f = \\lambda \\nabla g$. The multiplier $\\lambda$ measures sensitivity of the optimal value to relaxing the constraint. MVP interviews: equalities only (full KKT / inequalities later if needed).',
        formula='Problem: $\\min f(x)$ s.t. $g(x)=0$\n$L(x,\\lambda) = f(x) - \\lambda g(x)$  (sign convention varies)\nStationarity: $\\nabla_x L = \\nabla f - \\lambda \\nabla g = 0$ · primal feasibility: $g(x)=0$\nSeveral constraints $g_i=0$: $\\nabla f = \\sum_i \\lambda_i \\nabla g_i$\nEnvelope: $d/dc$ of optimal value with $g(x)=c$ relates to $\\lambda$',
        intuition='On the constraint surface you can only move tangent to it. For $f$ to be stationary there, its gradient can\'t have a tangential component — so $\\nabla f$ must align with the constraint gradients. $\\lambda$ is the "price" of the constraint.',
        worked_example='Example 1 — classic:\n$\\max f=xy$ s.t. $x+y=1$. $\\nabla f=(y,x)$, $\\nabla g=(1,1)$ ⇒ $(y,x)=\\lambda(1,1)$ and $x+y=1$. So $x=y=\\lambda$ ⇒ $x=y=1/2$, $f=1/4$.\n\nExample 2 — quadratic on a line:\n$\\min x^2+y^2$ s.t. $x+2y=1$. $\\nabla f=(2x,2y)=\\lambda(1,2)$ ⇒ $2x=\\lambda$, $2y=2\\lambda$ ⇒ $y=\\lambda$, $x=\\lambda/2$. Constraint: $\\lambda/2+2\\lambda=1$ ⇒ $(5/2)\\lambda=1$ ⇒ $\\lambda=2/5$, $x=1/5$, $y=2/5$ (geometry: projection of the origin onto the line).\n\nExample 3 — two variables one constraint check FOC count:\n$n=2$, one equality ⇒ system has 3 equations (2 stationarity + 1 constraint) for $(x,y,\\lambda)$.',
        interview_tips='1. Write $\\mathcal{L}$, then $\\nabla_x \\mathcal{L}=0$ and constraints — don\'t skip feasibility.\n2. Count equations vs unknowns to sanity-check.\n3. Interpret $\\lambda$ as shadow price if asked "what if the budget relaxes."\n4. For inequalities you\'d need KKT; say so if the constraint is $\\geq$.\n5. Geometry line: $\\nabla f \\parallel \\nabla g$ at the contact point of level set and constraint.',
        prerequisites='Convexity & Unconstrained Optimization, Derivatives & Gradients',
    ),
    "differential-equations": ConceptSeed(
        slug='differential-equations',
        name='Differential Equations',
        topic_slug='differential-equations',
        definition='An ordinary differential equation (ODE) relates a function to its derivatives. Interview focus: recognize separable and linear first-order ODEs, solve constant-coefficient linear ODEs, and read growth/decay / oscillation from the characteristic root. PDEs and stochastic DEs belong later (Quant Research / Finance) — keep this page ODE-first.',
        formula="Separable: $dy/dx = g(x)h(y) \\Rightarrow \\int dy/h(y) = \\int g(x)\\,dx$\nLinear 1st order: $y' + p(x)y = q(x)$ · integrating factor $\\mu=\\exp(\\int p\\,dx)$\nConst coeff: $y''+ay'+by=0$ · try $e^{rt} \\Rightarrow r^2+ar+b=0$\nExponential growth: $y' = ky \\Rightarrow y = y_0 e^{kt}$\nSystem form: $x' = Ax$ · solutions mix $e^{\\lambda t}$ along eigenvectors of $A$",
        intuition='ODEs describe how a state evolves given a local rule. Linear constant-coefficient equations are solved by exponentials because the derivative of $e^{rt}$ is a multiple of itself — same eigen-idea as $Av=\\lambda v$. Stability: $\\mathrm{Re}(r)<0$ ⇒ decay.',
        worked_example="Example 1 — growth/decay:\n$y' = -3y$, $y(0)=5$ ⇒ $y=5e^{-3t}$.\n\nExample 2 — separable:\n$dy/dx = xy$, $y(0)=2$ ⇒ $\\int dy/y = \\int x\\, dx$ ⇒ $\\log|y| = \\tfrac{1}{2}x^2+C$ ⇒ $y=2e^{x^2/2}$.\n\nExample 3 — second order:\n$y''-y'-2y=0$ ⇒ $(r-2)(r+1)=0$ ⇒ $r=2,-1$. General: $y=Ae^{2t}+Be^{-t}$.\n\nExample 4 — linear system link:\n$x' = \\begin{bmatrix}0&1\\\\-2&-3\\end{bmatrix}x$ has characteristic poly of the matrix; modes $e^{\\lambda t}v$ with $Av=\\lambda v$ — same eigenvalues as the matrix $A$.",
        interview_tips="1. Identify type: separable, linear first-order, const-coeff, or system.\n2. For const-coeff, write the characteristic polynomial immediately.\n3. Apply initial conditions only after the general solution.\n4. Stability $\\Leftrightarrow$ negative real parts of roots / eigenvalues.\n5. If they ask heat/Black-Scholes PDE, say that's a different toolbox — don't force ODE slogans.",
        prerequisites='Derivatives & Gradients',
    ),
    "estimation": ConceptSeed(
        slug="estimation",
        name="Point Estimation",
        topic_slug="estimation",
        definition=(
            "A point estimator $\\hat{\\theta}=\\hat{\\theta}(X_1,\\ldots,X_n)$ is a function of the data "
            "that returns a single guess for an unknown parameter $\\theta$. Interview fluency is about "
            "properties of $\\hat{\\theta}$ — bias, variance, MSE — and constructing simple estimators "
            "(sample mean, method of moments), not naming every classical recipe."
        ),
        formula=(
            "$\\mathrm{Bias}(\\hat{\\theta}) = E[\\hat{\\theta}] - \\theta$\n"
            "$\\mathrm{Var}(\\hat{\\theta}) = E[(\\hat{\\theta}-E[\\hat{\\theta}])^2]$\n"
            "$\\mathrm{MSE}(\\hat{\\theta}) = E[(\\hat{\\theta}-\\theta)^2] = \\mathrm{Var}(\\hat{\\theta}) + \\mathrm{Bias}(\\hat{\\theta})^2$\n"
            "$\\bar{X} = n^{-1}\\sum_i X_i$ (unbiased for $\\mu$ under IID)\n"
            "MoM (light): equate sample moments to population moments and solve for $\\theta$"
        ),
        intuition=(
            "Bias and variance trade: an unbiased estimator can still be noisy; a slightly biased one "
            "can win on MSE. Consistency is the large-$n$ promise that $\\hat{\\theta}$ settles near "
            "$\\theta$. Always state what you are estimating before writing a formula."
        ),
        worked_example=(
            "Q: IID $X_i$ with mean $\\mu$, variance $\\sigma^2$. Is $\\bar{X}$ unbiased for $\\mu$? "
            "What is its MSE?\n\n"
            "Solve: $E[\\bar{X}]=\\mu$ ⇒ bias $0$. $\\mathrm{Var}(\\bar{X})=\\sigma^2/n$. "
            "So $\\mathrm{MSE}=\\sigma^2/n$.\n\n"
            "Contrast: $\\hat{\\mu}=X_1$ is also unbiased but $\\mathrm{MSE}=\\sigma^2$ — much worse "
            "for $n>1$. Unbiased $\\neq$ good."
        ),
        interview_tips=(
            "1. Name the target parameter before the estimator.\n"
            "2. Compute bias and variance separately, then MSE.\n"
            "3. Sample mean / sample variance are the default sanity estimators — know "
            "$E[S^2]=\\sigma^2$ for the unbiased version with $n-1$.\n"
            "4. Consistency $\\neq$ unbiasedness for finite $n$; say which claim you are making.\n"
            "5. MoM is often faster than MLE in a screen when the moments are obvious."
        ),
        prerequisites="Expectation, Variance & Covariance",
    ),
    "confidence-intervals": ConceptSeed(
        slug="confidence-intervals",
        name="Confidence Intervals",
        topic_slug="confidence-intervals",
        definition=(
            "A confidence interval is a data-dependent range $[L,U]$ designed so that, under repeated "
            "sampling, it covers the true parameter $\\theta$ with nominal rate $1-\\alpha$ "
            "(e.g. 95%). The random object is the interval, not $\\theta$. Interviews punish "
            "\"$\\theta$ is random in $[L,U]$ with probability 95%\" — $\\theta$ is fixed; coverage "
            "is about the procedure."
        ),
        formula=(
            "IID $X_i\\sim N(\\mu,\\sigma^2)$, $\\sigma$ known: "
            "$\\bar{X} \\pm z_{1-\\alpha/2}\\,\\sigma/\\sqrt{n}$\n"
            "$\\sigma$ unknown: $\\bar{X} \\pm t_{n-1,1-\\alpha/2}\\, S/\\sqrt{n}$\n"
            "Wald (approx): $\\hat{\\theta} \\pm z_{1-\\alpha/2}\\,\\widehat{\\mathrm{SE}}$\n"
            "Duality: $\\theta_0$ in a $(1-\\alpha)$ CI $\\Leftrightarrow$ fail to reject $H_0:\\theta=\\theta_0$ "
            "at level $\\alpha$ (for standard two-sided tests)"
        ),
        intuition=(
            "Wider intervals buy more coverage; more data / smaller SE shrinks the interval. "
            "A 95% CI means: if you repeated the experiment many times, about 95% of such intervals "
            "would contain $\\theta$. It does not mean there is a 95% posterior probability that "
            "$\\theta$ lies inside this particular interval (that needs a Bayesian model)."
        ),
        worked_example=(
            "Q: $n=100$, $\\bar{X}=2.0$, $\\sigma=1$ known. 95% CI for $\\mu$?\n\n"
            "Solve: $z_{0.975}\\approx 1.96$, SE $=1/10=0.1$. "
            "Interval $2.0 \\pm 1.96\\cdot 0.1 = [1.804, 2.196]$.\n\n"
            "Interpretation: the method covers $\\mu$ about 95% of the time in repeated samples — "
            "not \"$\\mu$ is random.\""
        ),
        interview_tips=(
            "1. Say what is random (the interval) vs fixed ($\\theta$).\n"
            "2. State known vs unknown variance ($z$ vs $t$).\n"
            "3. Quote the SE and critical value explicitly.\n"
            "4. Use CI ↔ test duality when asked whether $\\theta_0$ is plausible.\n"
            "5. Do not confuse confidence with posterior probability unless the interviewer "
            "explicitly wants Bayes."
        ),
        prerequisites="Point Estimation, Limit Theorems (helpful for large-sample CIs)",
    ),
    "hypothesis-testing": ConceptSeed(
        slug="hypothesis-testing",
        name="Hypothesis Testing",
        topic_slug="hypothesis-testing",
        definition=(
            "Hypothesis testing decides between a null $H_0$ and alternative $H_1$ using a "
            "test statistic and a rejection rule with controlled Type I error "
            "$\\alpha = P(\\text{reject } H_0 \\mid H_0\\text{ true})$. The $p$-value is the "
            "probability, under $H_0$, of a result at least as extreme as observed. Power is "
            "$P(\\text{reject } H_0 \\mid H_1)$ — interviews want the definitions clean, not "
            "every named test catalog."
        ),
        formula=(
            "Type I: reject $H_0$ when true · Type II: fail to reject when $H_1$ true\n"
            "$\\alpha = P(\\text{Type I})$ · $\\beta = P(\\text{Type II})$ · $\\mathrm{power}=1-\\beta$\n"
            "z-test for mean ($\\sigma$ known): $Z = \\sqrt{n}(\\bar{X}-\\mu_0)/\\sigma$; reject if "
            "$|Z|>z_{1-\\alpha/2}$ (two-sided)\n"
            "$p$-value (two-sided normal): $2\\bigl(1-\\Phi(|Z_{\\mathrm{obs}}|)\\bigr)$\n"
            "Reject at level $\\alpha$ $\\Leftrightarrow$ $p \\le \\alpha$ (for standard tests)"
        ),
        intuition=(
            "You design a gate that rarely opens under $H_0$ (level $\\alpha$). Seeing a small "
            "$p$-value means the data are unusual under $H_0$ — not that $H_1$ is \"true with "
            "probability $1-p$.\" Power rises with $n$, effect size, and $\\alpha$. Failing to "
            "reject is not the same as proving $H_0$."
        ),
        worked_example=(
            "Q: Test $H_0:\\mu=0$ vs $H_1:\\mu\\neq 0$ with $n=25$, $\\bar{X}=0.4$, $\\sigma=1$, "
            "$\\alpha=0.05$.\n\n"
            "Solve: $Z = 5\\cdot 0.4 / 1 = 2$. Two-sided $p = 2(1-\\Phi(2))\\approx 0.0455 < 0.05$ ⇒ "
            "reject $H_0$. Equivalently $|2|>1.96$.\n\n"
            "If $\\bar{X}=0.2$, then $Z=1$, $p\\approx 0.32$ ⇒ do not reject."
        ),
        interview_tips=(
            "1. Write $H_0$, $H_1$, and whether the test is one- or two-sided before computing.\n"
            "2. Define Type I / II in one sentence each if asked.\n"
            "3. \"$p=0.03$\" means evidence against $H_0$, not \"$H_0$ has 3% probability.\"\n"
            "4. Mention power when discussing sample size or weak alternatives.\n"
            "5. Link to CIs: values outside a 95% CI are rejected by the dual level-5% test."
        ),
        prerequisites="Point Estimation, Confidence Intervals",
    ),
    "maximum-likelihood": ConceptSeed(
        slug="maximum-likelihood",
        name="Maximum Likelihood",
        topic_slug="maximum-likelihood",
        definition=(
            "Given a parametric model with density/PMF $f(x\\mid\\theta)$, the likelihood of IID "
            "data is $L(\\theta)=\\prod_i f(X_i\\mid\\theta)$. The maximum likelihood estimator (MLE) "
            "maximizes $L$ (usually via the log-likelihood $\\ell=\\log L$). MLE is the workhorse "
            "\"fit the model that makes the data most probable\" — interviews want setup, score "
            "equation, and common closed forms (Bernoulli, Normal mean)."
        ),
        formula=(
            "$L(\\theta)=\\prod_i f(X_i\\mid\\theta)$ · $\\ell(\\theta)=\\sum_i \\log f(X_i\\mid\\theta)$\n"
            "Score: $\\ell'(\\hat{\\theta}_{\\mathrm{MLE}})=0$ (interior max; check boundary)\n"
            "Bernoulli($p$): $\\hat{p}_{\\mathrm{MLE}}=\\bar{X}$\n"
            "Normal mean ($\\sigma$ known): $\\hat{\\mu}_{\\mathrm{MLE}}=\\bar{X}$\n"
            "Invariance: $\\widehat{g(\\theta)}=g(\\hat{\\theta}_{\\mathrm{MLE}})$ for suitable $g$"
        ),
        intuition=(
            "Likelihood asks: which parameter makes what we saw least surprising? Log turns "
            "products into sums and is monotone, so argmax is unchanged. Large-sample MLE is "
            "approximately Normal with SE from Fisher information — mention if asked about "
            "asymptotics; do not force it on a quick screen."
        ),
        worked_example=(
            "Q: IID Bernoulli($p$), observe $k$ ones in $n$ trials. Find $\\hat{p}_{\\mathrm{MLE}}$.\n\n"
            "Solve: $L(p)=p^k(1-p)^{n-k}$. $\\ell = k\\log p+(n-k)\\log(1-p)$. "
            "$\\ell' = k/p - (n-k)/(1-p)=0$ ⇒ $\\hat{p}=k/n=\\bar{X}$.\n\n"
            "Check: $p=0$ or $1$ only if $k=0$ or $n$ — otherwise critical point is the max."
        ),
        interview_tips=(
            "1. Write the likelihood from the joint density/PMF before differentiating.\n"
            "2. Maximize $\\ell$, not $L$, and say why (monotone + sums).\n"
            "3. Check endpoints when the parameter lives in a closed interval.\n"
            "4. Know Bernoulli / Poisson / Normal mean MLEs cold.\n"
            "5. Invariance saves work: estimate $\\theta$, then transform."
        ),
        prerequisites="Point Estimation, Common Distributions",
    ),
    "regression": ConceptSeed(
        slug="regression",
        name="Linear Regression (OLS)",
        topic_slug="regression",
        definition=(
            "Ordinary least squares (OLS) fits $Y \\approx \\beta_0 + \\beta_1 X$ (or a linear "
            "combination of features) by minimizing residual sum of squares. The fitted "
            "coefficients are the projection of $Y$ onto the column space of the design matrix — "
            "same geometry as least squares in linear algebra. Interviews care about "
            "interpretation of $\\hat{\\beta}$, residuals, $R^2$, and the standard assumptions "
            "(linearity, noise mean zero, roughly constant variance, weak dependence)."
        ),
        formula=(
            "Simple: $\\hat{\\beta}_1 = \\dfrac{\\sum (x_i-\\bar{x})(y_i-\\bar{y})}{\\sum (x_i-\\bar{x})^2}$, "
            "$\\hat{\\beta}_0 = \\bar{y}-\\hat{\\beta}_1\\bar{x}$\n"
            "Matrix: $\\hat{\\beta}=(X^{\\top}X)^{-1}X^{\\top}y$ (full column rank)\n"
            "Residuals: $e = y - X\\hat{\\beta}$ · $X^{\\top}e = 0$\n"
            "$R^2 = 1 - \\dfrac{\\|e\\|^2}{\\|y-\\bar{y}\\mathbf{1}\\|^2}$\n"
            "Noise model (classical): $y = X\\beta + \\varepsilon$, $E[\\varepsilon\\mid X]=0$"
        ),
        intuition=(
            "OLS draws the line (hyperplane) that makes vertical errors as small as possible in "
            "$L^2$. Coefficients answer \"holding other features fixed, how does $Y$ change with "
            "this $X$?\" — causal language needs extra assumptions. $R^2$ is in-sample fit, not "
            "proof of a good model."
        ),
        worked_example=(
            "Q: Points $(x,y)$: $(0,1)$, $(1,3)$, $(2,3)$. Fit OLS line.\n\n"
            "Solve: $\\bar{x}=1$, $\\bar{y}=7/3$. "
            "$\\sum (x-\\bar{x})(y-\\bar{y}) = (-1)(-4/3)+(0)(2/3)+(1)(2/3)=2$. "
            "$\\sum (x-\\bar{x})^2 = 1+0+1=2$. So $\\hat{\\beta}_1=1$, "
            "$\\hat{\\beta}_0=7/3-1=4/3$. Line $y=\\tfrac{4}{3}+x$.\n\n"
            "Fitted values $4/3$, $7/3$, $10/3$; residuals sum to $0$."
        ),
        interview_tips=(
            "1. Say \"minimize $\\|y-X\\beta\\|^2$\" / normal equations before formulas.\n"
            "2. Interpret $\\hat{\\beta}_1$ as a slope / partial effect, not automatically causal.\n"
            "3. Mention residual ⊥ columns ($X^{\\top}e=0$) as a geometry check.\n"
            "4. $R^2$ high $\\neq$ model is true; $R^2$ low $\\neq$ useless for prediction.\n"
            "5. Link to orthogonality / projections if the interviewer is math-heavy."
        ),
        prerequisites="Point Estimation, Orthogonality & Projections (helpful), Hypothesis Testing",
    ),
    "bias-variance": ConceptSeed(
        slug="bias-variance",
        name="Bias–Variance Tradeoff",
        topic_slug="bias-variance",
        definition=(
            "For predicting a target with squared error, expected loss decomposes into bias², "
            "variance, and irreducible noise. Flexible models can drive bias down but inflate "
            "variance (overfit); rigid models do the opposite (underfit). Interview focus: use "
            "the decomposition to explain overfit/underfit and regularization intuition — not "
            "derive every learning-theory bound."
        ),
        formula=(
            "At a point $x$: "
            "$E[(Y-\\hat{f}(x))^2] = \\mathrm{Bias}(\\hat{f}(x))^2 + \\mathrm{Var}(\\hat{f}(x)) + \\sigma^2$\n"
            "$\\mathrm{Bias}(\\hat{f}(x)) = E[\\hat{f}(x)] - f(x)$ "
            "(here $f(x)=E[Y\\mid x]$)\n"
            "Estimator view (same idea): "
            "$\\mathrm{MSE}(\\hat{\\theta})=\\mathrm{Var}(\\hat{\\theta})+\\mathrm{Bias}(\\hat{\\theta})^2$\n"
            "Regularization intuition: shrink flexibility ⇒ often ↑bias, ↓variance"
        ),
        intuition=(
            "Think of fitting with limited data: a wild interpolating curve hits training points "
            "(low bias in-sample) but jumps around across samples (high variance). A flat line "
            "is stable (low variance) but systematically wrong if the truth is curved (high bias). "
            "Cross-validation / held-out error estimates the total, not each term separately."
        ),
        worked_example=(
            "Q: Estimating a constant mean $\\mu$ with $n$ IID observations. Compare "
            "$\\hat{\\mu}_1=X_1$ vs $\\hat{\\mu}_n=\\bar{X}$.\n\n"
            "Solve: Both unbiased (bias $0$). $\\mathrm{Var}(X_1)=\\sigma^2$, "
            "$\\mathrm{Var}(\\bar{X})=\\sigma^2/n$. MSE falls like $1/n$ when you average — "
            "classic variance reduction at no bias cost.\n\n"
            "Overfit cartoon: degree-$(n-1)$ polynomial through $n$ noisy points has tiny "
            "training error but huge variance on a new draw of noise."
        ),
        interview_tips=(
            "1. Write the three-term decomposition when asked \"why overfit hurts.\"\n"
            "2. Connect to estimation: MSE = variance + bias² is the same story.\n"
            "3. Regularization / fewer features / more data → usually lower variance.\n"
            "4. Training error alone cannot diagnose the tradeoff — mention held-out error.\n"
            "5. Do not claim high $R^2$ on train means low bias and low variance out of sample."
        ),
        prerequisites="Point Estimation, Linear Regression (OLS)",
    ),

    "derivatives": ConceptSeed(
        slug="derivatives",
        name="Derivatives Payoffs & Parity",
        topic_slug="derivatives",
        definition=(
            "A derivative's value is defined by a contractual payoff on an underlying. Interview core: "
            "linear contracts (forwards/futures), vanilla calls and puts, and put–call parity as a "
            "no-arbitrage identity — not exotic product catalogs."
        ),
        formula=(
            "Forward (no dividends): $F = S_0 e^{rT}$ · long forward struck at $K$: payoff $S_T - K$\n"
            "European call / put: $(S_T-K)^+$ · $(K-S_T)^+$\n"
            "Put–call parity (European, no dividends): $C - P = S_0 - K e^{-rT} = e^{-rT}(F-K)$\n"
            "With continuous yield $q$: $C - P = S_0 e^{-qT} - K e^{-rT}$"
        ),
        intuition=(
            "Price by replication / no-arbitrage first; models (Black–Scholes) come after. Parity says "
            "a European call and put with the same strike and expiry differ by a forward on the stock — "
            "if parity fails, a static arb is available."
        ),
        worked_example=(
            "Q: $S_0=100$, $K=100$, $r=0$, $T=1$, European. If $C=10$, what must $P$ be?\n\n"
            "Solve: $r=0$ ⇒ $C-P = S_0-K = 0$ ⇒ $P=C=10$.\n\n"
            "If the market quotes $P=8$ with $C=10$, call is rich vs put: sell call, buy put "
            "(and hedge the synthetic using parity) to lock the mispricing."
        ),
        interview_tips=(
            "1. Draw terminal payoffs before writing formulas.\n"
            "2. State European vs American (classical parity is European).\n"
            "3. Write $C-P$ as prepaid forward on stock minus cash strike.\n"
            "4. Dividends / borrow: adjust the stock leg ($e^{-qT}$ or PV of dividends).\n"
            "5. Treat futures ≈ forwards unless asked about margin / mark-to-market."
        ),
        prerequisites="None — first concept on the Finance path (discounting helpful)",
    ),
    "black-scholes": ConceptSeed(
        slug="black-scholes",
        name="Black–Scholes",
        topic_slug="black-scholes",
        definition=(
            "Black–Scholes prices European options by assuming geometric Brownian motion for the "
            "underlying and no arbitrage (complete market). The call price is a risk-neutral "
            "expectation of the discounted payoff — equivalently, a delta-hedged portfolio that "
            "replicates the option. Interviews want the setup, the call/put formulas, and what "
            "$d_1,d_2$ mean — not a PDE derivation from scratch."
        ),
        formula=(
            "Call: $C = S_0 e^{-qT}\\Phi(d_1) - K e^{-rT}\\Phi(d_2)$\n"
            "Put: $P = K e^{-rT}\\Phi(-d_2) - S_0 e^{-qT}\\Phi(-d_1)$\n"
            "$d_1 = \\dfrac{\\log(S_0/K)+(r-q+\\tfrac{1}{2}\\sigma^2)T}{\\sigma\\sqrt{T}}$, "
            "$d_2 = d_1 - \\sigma\\sqrt{T}$\n"
            "Risk-neutral: $C = e^{-rT}E[(S_T-K)^+]$ under the GBM measure with drift $r-q$"
        ),
        intuition=(
            "$\\Phi(d_2)$ is (roughly) risk-neutral prob ITM; $e^{-qT}\\Phi(d_1)$ is the stock-measure "
            "delta weight. Higher $\\sigma$ or $T$ raises option value (for vanillas). BS is a "
            "benchmark — real markets show smiles; still the interview default model."
        ),
        worked_example=(
            "Q: As $\\sigma \\to 0$ with $F=S_0 e^{(r-q)T}>K$, what happens to the European call?\n\n"
            "Solve: Paths concentrate near the forward. Call → $e^{-rT}(F-K)$ (forward value of "
            "intrinsic in the forward measure). If $F<K$, call → $0$.\n\n"
            "Sanity: zero vol ⇒ option becomes a discounted forward claim or worthless."
        ),
        interview_tips=(
            "1. State GBM + no arb / complete market before writing $C$.\n"
            "2. Interpret $d_1$ (delta / stock-numeraire) vs $d_2$ (RN prob ITM) in one line each.\n"
            "3. Check put–call parity after any BS quote.\n"
            "4. Know limiting cases: $\\sigma\\to 0$, $T\\to 0$, deep ITM/OTM.\n"
            "5. If asked for a derivation, sketch replication / RN expectation — skip Ito theater "
            "unless they push."
        ),
        prerequisites="Derivatives Payoffs & Parity, Common Distributions / lognormals helpful",
    ),
    "greeks": ConceptSeed(
        slug="greeks",
        name="Greeks",
        topic_slug="greeks",
        definition=(
            "Greeks are sensitivities of an option (or book) to market inputs: delta to spot, "
            "gamma to delta, vega to volatility, theta to calendar time, rho to rates. Trading "
            "interviews care about signs, ATM intuition, and hedging stories — especially "
            "delta-hedging and why short gamma hurts in big moves."
        ),
        formula=(
            "Delta $\\Delta = \\partial V/\\partial S$ · Gamma $\\Gamma = \\partial^2 V/\\partial S^2$\n"
            "Vega $\\nu = \\partial V/\\partial \\sigma$ · Theta $\\Theta = \\partial V/\\partial t$\n"
            "BS call (yield $q$): $\\Delta = e^{-qT}\\Phi(d_1)$ · $\\Gamma = e^{-qT}\\phi(d_1)/(S\\sigma\\sqrt{T})$\n"
            "ATM call delta (no yield, rough): $\\approx 1/2$ · Gamma / vega peak near ATM"
        ),
        intuition=(
            "Delta is the hedge ratio in shares. Gamma measures how fast that hedge changes — "
            "long gamma benefits from realized moves if you rehedge; short gamma pays for calm "
            "markets via theta. Vega is the vol bet; most vanillas are long vega."
        ),
        worked_example=(
            "Q: You are short an ATM call and delta-hedged. Spot jumps up 5% with no vol change. "
            "Are you roughly happy or unhappy on gamma?\n\n"
            "Solve: Short call ⇒ short gamma. A large move makes the option's delta rise against "
            "you; rehedging buys high / sells low. Unhappy on gamma (theta was your compensation "
            "if nothing moved)."
        ),
        interview_tips=(
            "1. Quote sign: long vanilla call ⇒ $\\Delta>0$, $\\Gamma>0$, $\\nu>0$, $\\Theta$ usually $<0$.\n"
            "2. ATM ≈ 50Δ for calls (adjust for $q$, $r$, skew).\n"
            "3. Tie gamma ↔ theta: long gamma pays theta.\n"
            "4. Vega is not a Greek letter historically — still say $\\partial V/\\partial\\sigma$.\n"
            "5. Book level: aggregate Greeks; one-name vs index matters for trading talk."
        ),
        prerequisites="Black–Scholes, Derivatives Payoffs & Parity",
    ),
    "portfolio-theory": ConceptSeed(
        slug="portfolio-theory",
        name="Mean–Variance Portfolios",
        topic_slug="portfolio-theory",
        definition=(
            "Mean–variance theory chooses portfolio weights to trade off expected return against "
            "variance. Diversification works when assets are imperfectly correlated: portfolio "
            "variance includes covariance terms that shrink the risk of the mix. Sharpe ratio "
            "summarizes excess return per unit of volatility."
        ),
        formula=(
            "Two assets: $\\sigma_p^2 = w^2\\sigma_1^2+(1-w)^2\\sigma_2^2+2w(1-w)\\rho\\sigma_1\\sigma_2$\n"
            "Vector: $\\sigma_p^2 = w^{\\top}\\Sigma w$ · $\\mu_p = w^{\\top}\\mu$\n"
            "Sharpe: $(\\mu_p - r_f)/\\sigma_p$\n"
            "Min-variance weight on asset 1 (two-asset, equal constraint): "
            "depends on $\\sigma_i$ and $\\rho$ — know the $\\rho=1$ vs $\\rho<1$ cartoons"
        ),
        intuition=(
            "Risk is not additive; covariances are the story. Perfect correlation ⇒ no "
            "diversification benefit. Low correlation is why a book of weak edges can still "
            "look good in variance terms."
        ),
        worked_example=(
            "Q: Two assets, $\\sigma_1=\\sigma_2=\\sigma$, $\\rho=0$, equal weight $w=1/2$. "
            "What is $\\sigma_p$?\n\n"
            "Solve: $\\sigma_p^2 = 2\\cdot(1/4)\\sigma^2 = \\sigma^2/2$ ⇒ $\\sigma_p = \\sigma/\\sqrt{2}$.\n\n"
            "If $\\rho=1$, equal weight gives $\\sigma_p=\\sigma$ — no variance reduction."
        ),
        interview_tips=(
            "1. Expand $\\mathrm{Var}(w\\cdot X)$ and point at the covariance term.\n"
            "2. Say when diversification helps ($|\\rho|<1$) vs fails ($\\rho=\\pm 1$ extremes).\n"
            "3. Sharpe needs a risk-free baseline — state $r_f$.\n"
            "4. Mean–variance ≠ utility theory for all investors — quadratic / Normal backdrop.\n"
            "5. Link to CAPM as the equilibrium story built on this math."
        ),
        prerequisites="Variance & Covariance",
    ),
    "capm": ConceptSeed(
        slug="capm",
        name="CAPM & Beta",
        topic_slug="capm",
        definition=(
            "CAPM prices expected returns from exposure to the market portfolio: only systematic "
            "risk (beta) is compensated. Idiosyncratic risk is diversified away in the model. "
            "Interviews want $\\beta$, the SML equation, and when CAPM fails as a description of "
            "real markets."
        ),
        formula=(
            "$\\beta_i = \\mathrm{Cov}(R_i,R_m)/\\mathrm{Var}(R_m)$\n"
            "SML: $E[R_i] = r_f + \\beta_i\\bigl(E[R_m]-r_f\\bigr)$\n"
            "Alpha (regression): $R_i - r_f = \\alpha + \\beta(R_m-r_f)+\\varepsilon$\n"
            "CAPM ⇒ $E[\\alpha]=0$ if the market portfolio is mean–variance efficient"
        ),
        intuition=(
            "You get paid for risk you cannot diversify. High beta ⇒ higher required return in "
            "the model. Empirical critiques (size, value, momentum) matter in interviews as "
            "\"where CAPM is incomplete,\" not as a reason to forget the formula."
        ),
        worked_example=(
            "Q: $r_f=2\\%$, $E[R_m]=8\\%$, $\\beta=1.5$. What is CAPM $E[R_i]$?\n\n"
            "Solve: $E[R_i]=2\\% + 1.5\\cdot(8\\%-2\\%)=2\\%+9\\%=11\\%$.\n\n"
            "If realized average return is $14\\%$, sample alpha vs CAPM is $+3\\%$ (not proof of skill)."
        ),
        interview_tips=(
            "1. Write $\\beta=\\mathrm{Cov}/\\mathrm{Var}$ before SML.\n"
            "2. Distinguish systematic vs idiosyncratic risk in one sentence.\n"
            "3. Alpha is a residual vs a benchmark — state the benchmark.\n"
            "4. Know one limitation: market portfolio unobservable / anomalies.\n"
            "5. Trading desks may care more about realized beta hedges than equilibrium CAPM."
        ),
        prerequisites="Mean–Variance Portfolios",
    ),
    "fixed-income": ConceptSeed(
        slug="fixed-income",
        name="Fixed Income Basics",
        topic_slug="fixed-income",
        definition=(
            "Fixed income maps yields to prices for bonds and rates instruments. Core interview "
            "facts: prices move inversely to yields; duration / DV01 measure interest-rate "
            "sensitivity; discounting is the pricing engine. Keep to vanilla bonds and first-order "
            "risk — not full curve construction."
        ),
        formula=(
            "Zero bond: $P(T)=e^{-yT}$ (continuous) or $1/(1+y)^T$ (annual)\n"
            "Coupon bond: sum of discounted cashflows\n"
            "Macaulay duration $D$ · modified duration $\\approx -\\dfrac{1}{P}\\dfrac{dP}{dy}$\n"
            "DV01 ≈ dollar value of 1bp: first-order $\\Delta P \\approx -\\mathrm{DV01}\\cdot(\\Delta y\\text{ in bp})$"
        ),
        intuition=(
            "A bond is a package of cashflows; higher discount rates cut present value. Longer "
            "cashflows ⇒ more sensitivity (higher duration). Traders think in DV01: how many "
            "dollars per basis point."
        ),
        worked_example=(
            "Q: One-year zero, face 100, continuous yield $y=5\\%$. Price? If $y$ rises to $6\\%$, "
            "new price?\n\n"
            "Solve: $P=100 e^{-0.05}=95.12$ (approx). At $6\\%$: $100 e^{-0.06}=94.18$. "
            "Price fell when yield rose.\n\n"
            "Rough duration for a one-year zero is about $1$ year — large relative move for a 100bp shock."
        ),
        interview_tips=(
            "1. Always say price ↑ when yield ↓ (other things equal).\n"
            "2. State compounding convention if you write a formula.\n"
            "3. Duration / DV01 for risk; convexity only if they ask for second order.\n"
            "4. Distinguish yield-to-maturity from a spot/zero rate if the question is careful.\n"
            "5. For trading interviews, prefer DV01 intuition over Macaulay memorization."
        ),
        prerequisites="None (discounting from Math/Derivatives helpful)",
    ),
    "market-microstructure": ConceptSeed(
        slug="market-microstructure",
        name="Market Microstructure",
        topic_slug="market-microstructure",
        definition=(
            "Microstructure is how trades actually happen: spreads, limit vs market orders, "
            "inventory risk, and adverse selection. Interview focus: why the bid–ask spread "
            "exists, maker vs taker, and how informed flow hurts liquidity providers — not "
            "full LOB simulators."
        ),
        formula=(
            "Quoted spread: ask $-$ bid · Mid $= (\\mathrm{bid}+\\mathrm{ask})/2$\n"
            "Rough: spread compensates inventory risk + adverse selection + costs\n"
            "Adverse selection: after you buy, price tends to drift against you if flow is informed\n"
            "Markout / PnL after trade: compare entry mid to later mid"
        ),
        intuition=(
            "Liquidity providers earn spread when flow is uninformed noise, and lose when "
            "counterparties know more. Inventory: after buying a lot, you lower quotes to shed "
            "risk. Optimal quoting balances earn-the-spread vs getting run over."
        ),
        worked_example=(
            "Q: Bid $99.9$, ask $100.1$. You buy at the ask. One minute later mid is $99.8$. "
            "Were you likely hit by adverse selection on this trade?\n\n"
            "Solve: You paid $100.1$; mid fell to $99.8$ — markout negative. That pattern is "
            "consistent with buying into informed selling / toxic flow (one anecdote, not proof)."
        ),
        interview_tips=(
            "1. Define bid/ask/mid and who is maker vs taker.\n"
            "2. Name two spread components: inventory and adverse selection.\n"
            "3. \"Toxic flow\" = flow that predicts future mid moves against the LP.\n"
            "4. Separate latency / queue priority talk from economics unless asked.\n"
            "5. Tie back to derivatives only if discussing hedging in the underlying market."
        ),
        prerequisites="Derivatives Payoffs & Parity (markets context)",
    ),

    "python": ConceptSeed(
        slug="python",
        name="Python for Quant",
        topic_slug="python",
        definition=(
            "Python is the default research and scripting language in quant interviews: clear code "
            "under time pressure, correct use of built-ins, and knowing the cost of common operations. "
            "Focus on language mechanics interviewers probe (mutability, iteration, dict/set, sorting "
            "with keys) plus a light NumPy/pandas layer — not a full data-science course."
        ),
        formula=(
            "$\\texttt{dict}$/$\\texttt{set}$ lookup, insert: amortized $O(1)$\n"
            "$\\texttt{list}$ index / append: $O(1)$ amortized append · $x$ in list: $O(n)$\n"
            "Timsort $\\texttt{sorted}$: $O(n\\log n)$ · $\\texttt{bisect}$ on sorted list: $O(\\log n)$\n"
            "Comprehension ≈ loop (clarity first) · NumPy ufuncs ≈ $O(n)$ vectorized work"
        ),
        intuition=(
            "Write the obvious correct solution first; then talk complexity. Most Python screens are "
            "really: can you manipulate collections safely, avoid quadratic traps (list membership in "
            "a loop), and use the standard library ($\\texttt{bisect}$, $\\texttt{heapq}$, "
            "$\\texttt{collections}$) instead of reinventing them."
        ),
        worked_example=(
            "Q: Count frequencies of tokens in a list $\\texttt{xs}$. Idiomatic approach and complexity?\n\n"
            "Solve: $\\texttt{Counter(xs)}$ or a $\\texttt{dict}$ loop — $O(n)$ time, $O(k)$ space for "
            "$k$ distinct keys. Sorting then scanning is $O(n\\log n)$ and usually worse for pure counts.\n\n"
            "Second: sorted list, find insertion point for $x$ → $\\texttt{bisect\\_left}$ — $O(\\log n)$, "
            "not a linear scan."
        ),
        interview_tips=(
            "1. State time/space before coding when the problem is algorithmic.\n"
            "2. Prefer $\\texttt{dict}$/$\\texttt{set}$ over $\\texttt{list}$ for membership.\n"
            "3. Know $\\texttt{defaultdict}$, $\\texttt{Counter}$, $\\texttt{deque}$, $\\texttt{heapq}$, "
            "$\\texttt{bisect}$ by name.\n"
            "4. Mutability: default-arg $\\texttt{[]}$ trap; copy vs alias ($\\texttt{b = a}$ vs "
            "$\\texttt{a.copy()}$).\n"
            "5. NumPy: vectorize hot loops; don't claim pandas expertise you don't have."
        ),
        prerequisites="None — first concept on the Programming path",
    ),
    "cpp": ConceptSeed(
        slug="cpp",
        name="C++ for Quant",
        topic_slug="cpp",
        definition=(
            "C++ shows up in low-latency and production quant SWE screens: value semantics, references, "
            "RAII, and avoiding undefined behavior. Interview focus is correct, predictable code and "
            "complexity of standard containers — not template metaprogramming contests."
        ),
        formula=(
            "$\\texttt{vector}$ random access $O(1)$ · push\\_back amortized $O(1)$ · insert mid $O(n)$\n"
            "$\\texttt{unordered\\_map}$ average $O(1)$ · worst $O(n)$ · $\\texttt{map}$ $O(\\log n)$\n"
            "Pass by $\\texttt{const T\\&}$ to avoid copies · move when transferring ownership\n"
            "RAII: resource lifetime tied to object lifetime (destructors free handles)"
        ),
        intuition=(
            "C++ makes costs visible: copies, allocations, and aliasing. Prefer clear ownership "
            "(RAII, smart pointers when needed) over raw $\\texttt{new}$/$\\texttt{delete}$. Know when "
            "$\\texttt{vector}$ invalidates iterators (reallocation) — a classic interview footgun."
        ),
        worked_example=(
            "Q: Why is $\\texttt{for (auto x : vec)}$ different from $\\texttt{for (auto\\& x : vec)}$ "
            "for a $\\texttt{vector<Big>}$?\n\n"
            "Solve: $\\texttt{auto x}$ copies each element; $\\texttt{auto\\& x}$ binds a reference "
            "(no copy). Use $\\texttt{const auto\\&}$ when you only read.\n\n"
            "Second: after $\\texttt{vec.push\\_back}$ may reallocate, old iterators/pointers into "
            "$\\texttt{vec}$ can be invalidated — don't hold them across growth."
        ),
        interview_tips=(
            "1. Say const-ref vs copy explicitly when passing large objects.\n"
            "2. Prefer $\\texttt{vector}$ / $\\texttt{unordered\\_map}$ defaults; justify $\\texttt{map}$ "
            "when you need order.\n"
            "3. Name one UB example (dangling ref, out-of-bounds) if asked about bugs.\n"
            "4. RAII in one sentence: acquire in ctor, release in dtor.\n"
            "5. Don't volunteer template wizardry unless the interviewer goes there."
        ),
        prerequisites="Core Data Structures (helpful)",
    ),
    "data-structures": ConceptSeed(
        slug="data-structures",
        name="Core Data Structures",
        topic_slug="data-structures",
        definition=(
            "Core data structures are the tools behind almost every coding screen: arrays/vectors, "
            "hash maps/sets, stacks/queues, heaps, and trees. Interview fluency is choosing the "
            "structure that matches access patterns (lookup, ordered stats, FIFO) and stating the "
            "resulting complexity."
        ),
        formula=(
            "Array / vector: index $O(1)$ · search unsorted $O(n)$ · sorted search $O(\\log n)$\n"
            "Hash map / set: average $O(1)$ lookup · heap: insert / pop $O(\\log n)$ · peek $O(1)$\n"
            "Stack / queue: push/pop $O(1)$ · BST / ordered map: $O(\\log n)$ ops when balanced\n"
            "Match need → structure: membership ⇒ hash; top-$k$ ⇒ heap; monotonic stack ⇒ stack"
        ),
        intuition=(
            "Pick the structure from the question's verbs: 'frequent lookups', 'next greater', "
            "'running median', 'BFS layers'. Wrong structure turns an $O(n)$ idea into $O(n^2)$."
        ),
        worked_example=(
            "Q: Return the $k$ largest elements of an unsorted array. Which structure, and complexity?\n\n"
            "Solve: size-$k$ min-heap (or Quickselect). Heap approach: $O(n\\log k)$ time, $O(k)$ space.\n\n"
            "Contrast: sorting all then taking $k$ is $O(n\\log n)$ — fine if $k\\sim n$, worse if $k\\ll n$."
        ),
        interview_tips=(
            "1. Name the structure and the op costs before coding.\n"
            "2. Hash maps need a clear key; watch collisions / mutability of keys in theory talk.\n"
            "3. Heaps for top-$k$ and Dijkstra-style priorities.\n"
            "4. Stacks for matching / next-greater; queues for BFS.\n"
            "5. Trees: know BST vs heap vs trie at the cartoon level."
        ),
        prerequisites="Python for Quant or C++ for Quant (either language is fine)",
    ),
    "algorithms": ConceptSeed(
        slug="algorithms",
        name="Complexity & Core Algorithms",
        topic_slug="algorithms",
        definition=(
            "Algorithm screens test whether you can state Big-O honestly, pick a standard approach "
            "(scan, sort + scan, binary search, DFS/BFS, greedy when optimal), and avoid hidden "
            "quadratic loops. Deep pattern catalogs live under Coding Patterns — here keep the "
            "foundations."
        ),
        formula=(
            "Big-O: worst-case growth · $\\Theta$ when tight · ignore constants in first pass\n"
            "Sorting lower bound (comparison): $\\Omega(n\\log n)$ · binary search: $O(\\log n)$\n"
            "Two nested loops over $n$: often $O(n^2)$ · hashmap one-pass: often $O(n)$\n"
            "Master idea: reduce search space, reuse work (prefix / DP), or exploit order"
        ),
        intuition=(
            "Complexity is a communication tool: agree on $n$, count dominant ops, watch "
            "library costs ($\\texttt{in}$ on a list). Correctness first; then tighten."
        ),
        worked_example=(
            "Q: Check if any two values in an array sum to $T$. Naive vs better?\n\n"
            "Solve: Naive double loop $O(n^2)$. Better: one pass with a hash set of seen values — "
            "for each $x$ query $T-x$ in $O(1)$ average ⇒ $O(n)$ time, $O(n)$ space.\n\n"
            "If sorted, two pointers also $O(n)$ after $O(n\\log n)$ sort."
        ),
        interview_tips=(
            "1. Define $n$ (and $m$ for graphs) out loud.\n"
            "2. Give worst-case unless average-case is the point (hashing).\n"
            "3. Binary search needs a monotonic predicate — say it.\n"
            "4. Recursion: state the recurrence / depth before diving.\n"
            "5. Point to Coding Patterns for window / DP / graph templates."
        ),
        prerequisites="Core Data Structures",
    ),
    "sql": ConceptSeed(
        slug="sql",
        name="SQL for Quant",
        topic_slug="sql",
        definition=(
            "SQL appears in data / QR / trading ops screens: joining tables correctly, aggregating, "
            "and using window functions for running metrics. Interview focus is readable queries and "
            "NULL / duplicate pitfalls — not vendor-specific admin trivia."
        ),
        formula=(
            "Filter: $\\texttt{WHERE}$ · aggregate: $\\texttt{GROUP BY}$ + $\\texttt{HAVING}$\n"
            "Joins: $\\texttt{INNER}$ / $\\texttt{LEFT}$ — row multiplication on key fanout\n"
            "Window: $\\texttt{AVG(x) OVER (PARTITION BY k ORDER BY t)}$\n"
            "NULL: $\\texttt{NULL} \\neq \\texttt{NULL}$; use $\\texttt{IS NULL}$ · aggregates ignore NULL "
            "(usually)"
        ),
        intuition=(
            "Think in tables and keys: what is the grain of a row after the join? Window functions "
            "compute across related rows without collapsing them like $\\texttt{GROUP BY}$."
        ),
        worked_example=(
            "Q: For each trader\\_id, return the latest trade timestamp. Sketch the idea.\n\n"
            "Solve: $\\texttt{GROUP BY trader\\_id}$ with $\\texttt{MAX(ts)}$, or a window "
            "$\\texttt{ROW\\_NUMBER() OVER (PARTITION BY trader\\_id ORDER BY ts DESC)}$ filtered to "
            "$\\texttt{rn = 1}$ when you need full rows.\n\n"
            "Trap: joining before aggregating can duplicate rows and inflate sums."
        ),
        interview_tips=(
            "1. State the grain (one row per what?) before joining.\n"
            "2. Prefer explicit $\\texttt{JOIN ... ON}$ over ambiguous commas.\n"
            "3. Know $\\texttt{LEFT JOIN}$ keeps left rows when right is missing.\n"
            "4. Window vs group: windows keep detail rows.\n"
            "5. Call out NULL behavior if comparisons or counts look weird."
        ),
        prerequisites="None (set thinking helps)",
    ),

    "two-pointers": ConceptSeed(
        slug='two-pointers',
        name='Two Pointers',
        topic_slug='two-pointers',
        definition='Two pointers maintain indices that move through a sequence under an invariant — often on a sorted array, a string, or after sorting. Classic uses: pair sums, in-place filters, partitioning, and merging sorted lists. Interview skill: state the invariant and show why each move is safe.',
        formula='Opposite ends (sorted pair-sum): $O(n)$ after sort, $O(1)$ extra space\nSlow/fast same direction: in-place filter, cycle detection\nUnsorted membership → prefer hash set, not two pointers',
        intuition='If the space is ordered, each pointer move is forced by a comparison — you avoid nested $O(n^2)$. Sliding window is the contiguous special case of two pointers.',
        worked_example='Pair sum on a sorted array:\n```python\ndef two_sum_sorted(a: list[int], t: int) -> tuple[int, int] | None:\n    i, j = 0, len(a) - 1\n    while i < j:\n        s = a[i] + a[j]\n        if s == t:\n            return (a[i], a[j])\n        if s < t:\n            i += 1\n        else:\n            j -= 1\n    return None\n# [1,2,4,7,11], t=9 → (2, 7)\n```\n\nIn-place keep evens (slow/fast):\n```python\ndef keep_evens(a: list[int]) -> int:\n    slow = 0\n    for fast in range(len(a)):\n        if a[fast] % 2 == 0:\n            a[slow] = a[fast]\n            slow += 1\n    return slow  # new length\n```',
        interview_tips='1. Sorted vs unsorted → two pointers vs hash.\n2. Say the invariant out loud before coding.\n3. Dedup: skip equal neighbors when uniqueness matters.\n4. Off-by-one: i < j vs i <= j.\n5. Sliding window = two pointers + a contiguous feasibility constraint.',
        prerequisites='Core Data Structures (arrays); sorting/complexity helpful',
    ),
    "sliding-window": ConceptSeed(
        slug='sliding-window',
        name='Sliding Window',
        topic_slug='sliding-window',
        definition='A sliding window maintains a contiguous subarray/substring $[L,R]$ while expanding and shrinking to satisfy a constraint (sum, distinct count, character budget). Amortized $O(n)$ when each index enters/leaves at most once.',
        formula='Fixed length $k$: one pass, maintain running sum — $O(n)$\nVariable length: expand $R$, shrink $L$ while invalid — amortized $O(n)$\nNeed best contiguous segment under a constraint ⇒ think window',
        intuition='The window is a two-pointer pair locked to contiguity. Grow to include candidates; shrink from the left when the constraint breaks.',
        worked_example="Longest substring with at most k distinct characters:\n```python\nfrom collections import defaultdict\n\ndef longest_at_most_k(s: str, k: int) -> int:\n    count: dict[str, int] = defaultdict(int)\n    left = best = 0\n    for right, ch in enumerate(s):\n        count[ch] += 1\n        while len(count) > k:\n            count[s[left]] -= 1\n            if count[s[left]] == 0:\n                del count[s[left]]\n            left += 1\n        best = max(best, right - left + 1)\n    return best\n# s='araaci', k=2 → 4 ('raac')\n```",
        interview_tips="1. Name the constraint that makes a window valid/invalid.\n2. Argue each index moves at most once ⇒ $O(n)$.\n3. Fixed $k$ vs variable length — pick the right variant.\n4. Hash map / counter for frequencies inside the window.\n5. Related: prefix sums when the metric is range-sum, not 'shrink when invalid'.",
        prerequisites='Two Pointers',
    ),
    "prefix-sum": ConceptSeed(
        slug='prefix-sum',
        name='Prefix Sum',
        topic_slug='prefix-sum',
        definition='A prefix sum array precomputes running totals so any contiguous range sum is $O(1)$ after $O(n)$ setup. Variants: prefix XOR, 2D prefixes, and difference arrays for range updates.',
        formula='$\\mathrm{pref}[0]=0$, $\\mathrm{pref}[i]=a_0+\\cdots+a_{i-1}$\nSum $a[L..R] = \\mathrm{pref}[R+1]-\\mathrm{pref}[L]$\nSubarray sum $=k$: hashmap of prefix frequencies — $O(n)$',
        intuition="Turning range queries into two prefix lookups is the whole trick. For 'count subarrays with sum $k$', store how often each prefix appeared.",
        worked_example='Range sum after build:\n```python\ndef build_pref(a: list[int]) -> list[int]:\n    pref = [0] * (len(a) + 1)\n    for i, x in enumerate(a):\n        pref[i + 1] = pref[i] + x\n    return pref\n\ndef range_sum(pref: list[int], L: int, R: int) -> int:\n    return pref[R + 1] - pref[L]\n# a=[2,3,1,4], sum[1..2] = pref[3]-pref[1] = 6-2 = 4\n```\n\nCount subarrays with sum k:\n```python\nfrom collections import defaultdict\n\ndef count_sum_k(a: list[int], k: int) -> int:\n    seen: dict[int, int] = defaultdict(int)\n    seen[0] = 1\n    pref = ans = 0\n    for x in a:\n        pref += x\n        ans += seen[pref - k]\n        seen[pref] += 1\n    return ans\n```',
        interview_tips="1. Draw pref with a leading 0 to simplify indices.\n2. Off-by-one: inclusive $[L,R]$ ↔ pref[R+1]-pref[L].\n3. Hashmap of prefixes for subarray-sum counts.\n4. Difference array for many range increments.\n5. Don't use a window if you only need arbitrary range sums.",
        prerequisites='Two Pointers / arrays; Complexity & Core Algorithms helpful',
    ),
    "binary-search": ConceptSeed(
        slug='binary-search',
        name='Binary Search',
        topic_slug='binary-search',
        definition='Binary search finds a boundary in a monotonic search space: sorted arrays, or a yes/no predicate that flips from false to true (minimize feasible capacity, first true index, etc.). Interview skill: define the predicate and the invariant on $[lo, hi)$.',
        formula='Sorted array lookup: $O(\\log n)$\nAnswer-space search: lo/hi on the answer; check(mid) feasible?\nInvariant: answer lies in the active interval; shrink half each step',
        intuition="You're not always 'finding a value in an array' — often you're binary-searching the answer while a linear check validates mid.",
        worked_example='Lower bound (first index with a[i] >= x):\n```python\ndef lower_bound(a: list[int], x: int) -> int:\n    lo, hi = 0, len(a)  # [lo, hi)\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if a[mid] >= x:\n            hi = mid\n        else:\n            lo = mid + 1\n    return lo\n# a=[1,3,3,7], x=3 → 1\n```\n\nMinimize capacity: ship packages in D days (sketch):\n```python\ndef can_ship(a, cap, D) -> bool:\n    days = cur = 1\n    for w in a:\n        if cur + w > cap:\n            days += 1\n            cur = 0\n        cur += w\n    return days <= D\n# binary search cap in [max(a), sum(a)]\n```',
        interview_tips='1. Write the monotonic predicate in one sentence.\n2. Prefer half-open $[lo, hi)$ to reduce off-by-ones.\n3. mid = lo + (hi-lo)//2 if overflow worries you (C++ int).\n4. Duplicate values: specify first / last occurrence.\n5. If not monotonic, binary search is wrong — say so.',
        prerequisites='Complexity & Core Algorithms',
    ),
    "intervals": ConceptSeed(
        slug='intervals',
        name='Intervals',
        topic_slug='intervals',
        definition='Interval problems sort by start (or end) then scan once: merge overlaps, insert an interval, or find minimum rooms / arrows. Stack matching for parentheses is a related linear scan — keep merge logic as the core pattern here.',
        formula='Sort by start: $O(n\\log n)$ then $O(n)$ merge\nOverlap if $next.start \\le cur.end$ (careful with inclusive ends)\nMin meeting rooms: sort starts/ends or use a heap of end times',
        intuition='Sorting creates order so a single sweep decides merges. When a new interval starts before the current end, they overlap.',
        worked_example="Merge overlapping intervals:\n```python\ndef merge(intervals: list[list[int]]) -> list[list[int]]:\n    intervals.sort(key=lambda x: x[0])\n    out: list[list[int]] = []\n    for s, e in intervals:\n        if not out or s > out[-1][1]:\n            out.append([s, e])\n        else:\n            out[-1][1] = max(out[-1][1], e)\n    return out\n# [[1,3],[2,6],[8,10]] → [[1,6],[8,10]]\n```\n\nParentheses (stack — related linear scan):\n```python\ndef valid(s: str) -> bool:\n    pairs = {')':'(', ']':'[', '}':'{'}\n    st: list[str] = []\n    for ch in s:\n        if ch in '([{':\n            st.append(ch)\n        elif not st or st.pop() != pairs[ch]:\n            return False\n    return not st\n```",
        interview_tips="1. Sort key: by start for merge; sometimes by end for greedy picks.\n2. Clarify half-open vs closed intervals.\n3. Heap of end times for 'how many overlap now'.\n4. Don't force merge logic onto parentheses — use a stack.\n5. After sort, argue one linear pass is enough.",
        prerequisites='Two Pointers; sorting',
    ),
    "graph-traversal": ConceptSeed(
        slug='graph-traversal',
        name='Graph Traversal',
        topic_slug='graph-traversal',
        definition='Graph traversal explores nodes via BFS or DFS: grids, adjacency lists, and implicit graphs. BFS gives unweighted shortest paths and level order; DFS fits connectivity, cycle checks, and backtracking. Interview skill: pick BFS vs DFS and track visited.',
        formula='BFS: queue + visited — unweighted shortest path $O(V+E)$\nDFS: stack/recursion + visited — components, topo (with care)\nGrid: 4- or 8-neighbor edges; mark visited to avoid revisits',
        intuition="BFS expands by distance; DFS dives deep. On a grid, 'graph' is just cells with neighbor edges.",
        worked_example='BFS shortest path in an unweighted grid (4-dir):\n```python\nfrom collections import deque\n\ndef shortest(grid: list[list[int]]) -> int:\n    # 0 free, 1 blocked; start (0,0) to (n-1,m-1)\n    n, m = len(grid), len(grid[0])\n    if grid[0][0] or grid[n-1][m-1]:\n        return -1\n    q = deque([(0, 0, 1)])  # r, c, dist\n    seen = {(0, 0)}\n    while q:\n        r, c, d = q.popleft()\n        if (r, c) == (n - 1, m - 1):\n            return d\n        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n            nr, nc = r + dr, c + dc\n            if 0 <= nr < n and 0 <= nc < m and not grid[nr][nc] and (nr, nc) not in seen:\n                seen.add((nr, nc))\n                q.append((nr, nc, d + 1))\n    return -1\n```',
        interview_tips="1. BFS for shortest unweighted; DFS for components / search trees.\n2. Always mark visited when enqueue/push (not when pop) to avoid dup work.\n3. State $V$ and $E$ for complexity.\n4. Implicit graphs: don't build adj if a neighbor function suffices.\n5. Directed vs undirected changes cycle/topo rules — clarify.",
        prerequisites='Core Data Structures (queue/stack)',
    ),
    "dynamic-programming": ConceptSeed(
        slug='dynamic-programming',
        name='Dynamic Programming',
        topic_slug='dynamic-programming',
        definition='DP solves problems with optimal substructure and overlapping subproblems by storing subanswers. Interview focus: define state, transition, base cases, and iteration order (or memoized recursion) — 1D/2D classics, not exotic DP theory.',
        formula='Need: optimal substructure + overlapping subproblems\nState → transition → base → order\nTime ≈ (#states)×(work per state); space often reducible',
        intuition='If recursion recomputes the same subproblems, cache them. If you can order states so prerequisites come first, use a table bottom-up.',
        worked_example='Climb stairs (1 or 2 steps): ways to reach n:\n```python\ndef climb(n: int) -> int:\n    if n <= 2:\n        return n\n    a, b = 1, 2\n    for _ in range(3, n + 1):\n        a, b = b, a + b\n    return b\n```\n\n0/1 knapsack (count max value):\n```python\ndef knapsack(w: list[int], v: list[int], W: int) -> int:\n    dp = [0] * (W + 1)\n    for wi, vi in zip(w, v):\n        for cap in range(W, wi - 1, -1):  # backward = 0/1\n            dp[cap] = max(dp[cap], dp[cap - wi] + vi)\n    return dp[W]\n```',
        interview_tips='1. Speak state meaning in words before code.\n2. Write transition + base cases explicitly.\n3. 0/1 vs unbounded: loop direction on capacity.\n4. Start from recursion + memo if stuck on order.\n5. Complexity: count states × transitions.',
        prerequisites='Complexity & Core Algorithms; Graph Traversal helpful for DAG DP',
    ),
    "greedy": ConceptSeed(
        slug='greedy',
        name='Greedy',
        topic_slug='greedy',
        definition='A greedy algorithm builds a solution by local choices that never reconsider the past. It works when an exchange argument / greedy choice property holds. Interviews want the choice rule, a correctness sketch, and a counterexample when greedy fails.',
        formula='Pattern: sort by key → scan once taking feasible picks\nClassic: interval scheduling by end time; Huffman; activity selection\nIf greedy fails, fall back to DP / search',
        intuition="Sort so the locally best next option is globally safe. If you can't prove it, stress-test with a tiny counterexample before coding.",
        worked_example="Max non-overlapping intervals (schedule by earliest end):\n```python\ndef max_non_overlap(intervals: list[list[int]]) -> int:\n    intervals.sort(key=lambda x: x[1])\n    count = 0\n    end = float('-inf')\n    for s, e in intervals:\n        if s >= end:\n            count += 1\n            end = e\n    return count\n# pick earliest-finishing feasible interval each time\n```\n\nCounterexample intuition: choosing longest interval first can block two short ones.",
        interview_tips="1. State the greedy choice in one sentence.\n2. Sort key matters — justify it.\n3. Give a 30-second exchange / 'stays feasible' argument.\n4. Keep a counterexample ready if the interviewer challenges you.\n5. Greedy ≠ always optimal; know when to switch to DP.",
        prerequisites='Intervals; Complexity & Core Algorithms',
    ),
    "quick-tricks": ConceptSeed(
        slug="quick-tricks",
        name="Quick Tricks",
        topic_slug="quick-tricks",
        definition=(
            "Chapter 0 tricks from Benjamin's method: high-impact patterns you can deploy "
            "immediately — multiply by 11, the 'same first digit / second digits sum to 10' "
            "rule, and squaring numbers ending in 5. These buy time and confidence before "
            "deeper methods."
        ),
        formula=(
            "×11 (two digits): split digits; middle = sum (carry if $\\ge 10$)\n"
            "Same tens, units sum to 10: $ab \\times ac = a(a+1)$ followed by $b(10-b)$\n"
            "Square $n5$: $n(n+1)$ followed by 25"
        ),
        intuition=(
            "The tricks work because they turn multiplication into addition on digits you "
            "already see. Learn 2–3 cold; reach for them when the problem shape matches."
        ),
        worked_example=(
            "×11: $57 \\times 11$. Split: 5 _ 7. Middle digit $5+7=12$ → carry 1: "
            "$5+1=6$ in hundreds, write 2 in tens → **627**.\n\n"
            "Same-tens product: $43 \\times 47$. Tens digit 4; units $3+7=10$. "
            "$4 \\times 5 = 20$, append $3 \\times 7 = 21$ → **2021**.\n\n"
            "Square ending in 5: $65^2$. $6 \\times 7 = 42$, append 25 → **4225**."
        ),
        interview_tips=(
            "1. Name the pattern before computing ('this is an ×11').\n"
            "2. For ×11, say carries out loud — one mistake cascades.\n"
            "3. Same-tens rule needs units summing to exactly 10.\n"
            "4. $n5^2$ only works when the number ends in 5.\n"
            "5. If no pattern fits, switch to left-to-right methods (next concepts)."
        ),
        prerequisites="None — start here on the Mental Math path",
    ),
    "addition-subtraction": ConceptSeed(
        slug="addition-subtraction",
        name="Addition & Subtraction",
        topic_slug="addition-subtraction",
        definition=(
            "Left-to-right mental addition and subtraction: process high digits first so "
            "partial sums stay meaningful. Subtraction uses complements (how far a number "
            "is from a round target) to avoid painful borrowing."
        ),
        formula=(
            "Add left to right, carrying mentally\n"
            "Subtract via complement: $a - b = a - \\text{round} + \\text{complement}(b)$\n"
            "Three-digit sub: subtract round hundreds, add back complement of remainder"
        ),
        intuition=(
            "Humans read numbers left to right; your brain wants the big magnitude first. "
            "Complements turn ugly subtractions into easy additions."
        ),
        worked_example=(
            "Add: $728 + 346$. $700+300=1000$, $28+46=74$ → **1074**.\n\n"
            "Subtract with complement: $725 - 468$. Round 468 → 500 (complement 32). "
            "$725 - 500 = 225$, then $225 + 32 =$ **257**.\n\n"
            "Four-digit: $1246 - 579$. $1246 - 600 = 646$, complement of 79 is 21, "
            "$646 + 21 =$ **667**."
        ),
        interview_tips=(
            "1. Announce the round number you subtract (500, 600, …).\n"
            "2. Complement = how much you overshot when rounding up.\n"
            "3. Left-to-right addition: pause after hundreds if carrying.\n"
            "4. For trading P&L, sign errors hurt — restate the operation.\n"
            "5. Practice until complements feel automatic."
        ),
        prerequisites="Quick Tricks",
    ),
    "basic-multiplication": ConceptSeed(
        slug="basic-multiplication",
        name="Basic Multiplication",
        topic_slug="basic-multiplication",
        definition=(
            "Two-by-one and friendly two-by-two multiplication: break numbers apart, round "
            "up then adjust, and exploit numbers that start with 5 or end in 0. Foundation "
            "for all harder products in the book."
        ),
        formula=(
            "Distribute: $a(b+c) = ab + ac$\n"
            "Round up: $a \\times 98 = a \\times 100 - 2a$\n"
            "×25: divide by 4, append 00 (or ×100 then ÷4)\n"
            "×5: half the number, then ×10"
        ),
        intuition=(
            "Never multiply the hard way if a nearby round number plus a small correction "
            "is easier. Most 'basic' problems are disguised distribution."
        ),
        worked_example=(
            "$13 \\times 27$: $13 \\times 20 = 260$, $13 \\times 7 = 91$ → **351**.\n\n"
            "$48 \\times 25$: $48/4 = 12$, append 00 → **1200**.\n\n"
            "$78 \\times 98$: $78 \\times 100 = 7800$, minus $2 \\times 78 = 156$ → **7644**."
        ),
        interview_tips=(
            "1. Factor one side when possible ($27 = 20 + 7$).\n"
            "2. ×25 = ÷4 ×100; ×125 = ÷8 ×1000.\n"
            "3. Numbers near 100: multiply by 100 minus correction.\n"
            "4. Starting with 5: $52 \\times 11 = 520 + 52$ style splits help.\n"
            "5. State intermediate partial products — catches errors early."
        ),
        prerequisites="Addition & Subtraction",
    ),
    "intermediate-multiplication": ConceptSeed(
        slug="intermediate-multiplication",
        name="Intermediate Multiplication",
        topic_slug="intermediate-multiplication",
        definition=(
            "Two-digit × two-digit products, squaring two- and three-digit numbers, and "
            "cubing two-digit numbers. Methods: addition (split one factor), subtraction "
            "(round one factor up), and factoring when digits cooperate."
        ),
        formula=(
            "Square near $100$: $(100 \\pm d)^2 = 10000 \\pm 200d + d^2$\n"
            "2×2 split: $ab \\times cd = ab \\times c \\text{ tens} + ab \\times d$\n"
            "Factor when visible: $144 \\times 56 = 144 \\times 7 \\times 8$"
        ),
        intuition=(
            "Squaring is a special case of multiplication — pick the split that leaves the "
            "easiest final addition. Near-100 squares are interview favorites."
        ),
        worked_example=(
            "Square: $99^2 = (100-1)^2 = 10000 - 200 + 1 =$ **9801**.\n\n"
            "2×2: $42 \\times 46$. Split 42 → $40 \\times 46 = 1840$, $2 \\times 46 = 92$ "
            "→ **1932**.\n\n"
            "Power of 2: $2^{10} = 1024$ (memorize the ladder: 2,4,8,16,…,1024)."
        ),
        interview_tips=(
            "1. For squares, check if near 50, 100, or ends in 5 first.\n"
            "2. Choose the split that minimizes the last addition.\n"
            "3. Know $2^{10}=1024$ and $2^{16}=65536$ for compounding back-of-envelope.\n"
            "4. Three-digit squares: work from $(100a+b)^2$ expansion.\n"
            "5. If stuck, fall back to addition-method 2×2 — always works."
        ),
        prerequisites="Basic Multiplication",
    ),
    "mental-division-fractions": ConceptSeed(
        slug="mental-division-fractions",
        name="Mental Division & Fractions",
        topic_slug="mental-division-fractions",
        definition=(
            "Left-to-right division by peeling off chunks of the divisor, plus fast fraction "
            "arithmetic: simplify, common denominators, and factorial ratios. Critical for "
            "probability-style counting and P&L splits."
        ),
        formula=(
            "Divide: estimate quotient digit by digit from the left\n"
            "Same denominator: add/subtract numerators\n"
            "Factorial ratio: $n!/(n-k)! = n(n-1)\\cdots(n-k+1)$\n"
            "Decimal ↔ fraction: memorize $1/8=0.125$, $1/6 \\approx 0.167$"
        ),
        intuition=(
            "Division is repeated subtraction of convenient multiples. Fractions cancel "
            "before you multiply — never expand factorials fully."
        ),
        worked_example=(
            "Divide: $675 \\div 8$. $8 \\times 80 = 640$, remainder 35; $8 \\times 4 = 32$ "
            "→ **84** r3.\n\n"
            "Fraction: $1/7 + 1/7 =$ **2/7**.\n\n"
            "Factorial ratio: $5!/8! = 1/(8 \\cdot 7 \\cdot 6) =$ **1/336**.\n\n"
            "Decimal: $3/8 = 3 \\times 0.125 =$ **0.375**."
        ),
        interview_tips=(
            "1. Say each quotient digit before refining the remainder.\n"
            "2. Cancel factorials top and bottom before multiplying.\n"
            "3. Know common decimals: eighths, sixths, thirds.\n"
            "4. $720/6$: recognize 72/6 = 12, scale → 120.\n"
            "5. For $\\div 25$, multiply by 4 and shift decimal."
        ),
        prerequisites="Basic Multiplication",
    ),
    "guesstimation": ConceptSeed(
        slug="guesstimation",
        name="Guesstimation",
        topic_slug="guesstimation",
        definition=(
            "Order-of-magnitude estimates when exact arithmetic is unnecessary: approximate "
            "square roots, percentages, compound growth, and small-$x$ expansions. Includes "
            "Benjamin's Rule of 70 for doubling time."
        ),
        formula=(
            "√ near perfect square: $\\sqrt{n} \\approx a + (n-a^2)/(2a)$\n"
            "Percent: $x\\%$ of $N$ = $N \\times x/100$; chain percents multiply\n"
            "$(1 \\pm x)^n \\approx 1 \\pm nx$ for small $x$\n"
            "Rule of 70: doubling time $\\approx 70 / r\\%$"
        ),
        intuition=(
            "Guesstimation is knowing which approximation is good enough. Trading screens "
            "want speed with sane error bars — say your approximation aloud."
        ),
        worked_example=(
            "Percent: 15% of 240 = $240 \\times 0.15 = 240 \\times 3/20 =$ **36**.\n\n"
            "√ estimate: $\\sqrt{50} \\approx 7.07$ because $7^2=49$.\n\n"
            "Small power: $0.998^{10} \\approx 1 - 10(0.002) =$ **0.98**.\n\n"
            "Rule of 70: at 5% interest, doubling $\\approx 70/5 =$ **14 years**.\n\n"
            "Combinatorics: $C(8,3) = 8 \\cdot 7 \\cdot 6 / 6 =$ **56**."
        ),
        interview_tips=(
            "1. Prefix with 'approximately' when using linearization.\n"
            "2. $\\ln(2) \\approx 0.69$ — useful for continuous compounding sketches.\n"
            "3. Nested percents multiply: 10% of 10% of 1000 = 10.\n"
            "4. For √, bracket between consecutive squares first.\n"
            "5. Rule of 110 for tripling money (rough)."
        ),
        prerequisites="Mental Division & Fractions; Addition & Subtraction",
    ),
    "memorizing-numbers": ConceptSeed(
        slug="memorizing-numbers",
        name="Memorizing Numbers",
        topic_slug="memorizing-numbers",
        definition=(
            "Benjamin's phonetic code maps digits to consonant sounds so numbers become "
            "memorable words. Used to store intermediate results during hard multiplications "
            "and to recall constants under pressure."
        ),
        formula=(
            "Phonetic code: 1=t/d, 2=n, 3=m, 4=r, 5=l, 6=j/sh/ch, 7=k/g, 8=f/v, 9=p/b, 0=s/z\n"
            "Encode digits → consonants → add vowels freely → word picture\n"
            "Link words in a vivid mini-story"
        ),
        intuition=(
            "Your brain remembers scenes, not digits. Convert a partial product into a "
            "word, picture it, retrieve it when adding later steps."
        ),
        worked_example=(
            "Encode 142857: 1→t, 4→r, 2→n, 8→f, 5→l, 7→k → 'turn file' / 'drum full' "
            "(vowel-free skeleton). Add vowels: **turNFiLe**.\n\n"
            "During $76^2$: compute $70^2=4900$, store '4900' as word, then add "
            "$2(70)(6)=840$ and $6^2=36$ from memory of the partial.\n\n"
            "Practice: encode your phone's last four digits as one word tonight."
        ),
        interview_tips=(
            "1. You don't need full mastery — even 2-digit mnemonics help mid-problem.\n"
            "2. Vowels don't encode; any vowel between consonants is fine.\n"
            "3. Make images absurd — memory sticks to weird scenes.\n"
            "4. For interviews, plain notes-on-fingers may beat untrained mnemonics.\n"
            "5. Rehearse phonetic code once; it's a long-term skill, not cram-night."
        ),
        prerequisites="Intermediate Multiplication",
    ),
    "advanced-multiplication": ConceptSeed(
        slug="advanced-multiplication",
        name="Advanced Multiplication",
        topic_slug="advanced-multiplication",
        definition=(
            "Large products: four- and five-digit squares, three-by-two and three-by-three "
            "multiplication via factoring, close-together method, and the when-all-else-fails "
            "fallback. Peak difficulty in Benjamin's curriculum."
        ),
        formula=(
            "Close-together: if $a \\approx b$, use $(a+c)(b-c) = ab - c^2$ (adjust)\n"
            "Factor: $773 \\times 42 = 773 \\times 7 \\times 6$\n"
            "4-digit square: $(1000a+b)^2$ via $a^2$, $2ab$, $b^2$ blocks\n"
            "3×3: factor both sides when digits share factors"
        ),
        intuition=(
            "Advanced means choosing the method: factoring beats brute force when digits "
            "factor nicely; close-together wins when numbers cluster."
        ),
        worked_example=(
            "Factor: $773 \\times 42 = 773 \\times 7 \\times 6 = 5411 \\times 6 =$ **32,466**.\n\n"
            "Close together: $97 \\times 93 = (95+2)(95-2) = 95^2 - 4 = 9025 - 4 =$ **9021**.\n\n"
            "4-digit square sketch: $1234^2$ — split $1200|34$, combine blocks "
            "(use mnemonics for partials if needed)."
        ),
        interview_tips=(
            "1. Scan for factorizations before any method.\n"
            "2. Close-together needs numbers near a common midpoint.\n"
            "3. On timed screens, advanced 3×3 is rare — know 2×2 cold instead.\n"
            "4. Five-digit squares are showmanship; 2×2 speed matters more.\n"
            "5. Fall back to distributive split — slow but reliable."
        ),
        prerequisites="Intermediate Multiplication",
    ),
    "time-series": ConceptSeed(
        slug="time-series",
        name="Time Series Basics",
        topic_slug="time-series",
        definition=(
            "A time series $\\{X_t\\}$ is data indexed by time. Interview focus: stationarity "
            "(distribution of $(X_t,\\ldots,X_{t+k})$ does not depend on $t$), autocorrelation, "
            "random-walk / unit-root intuition, and AR(1) as the workhorse model — not full "
            "econometrics notation."
        ),
        formula=(
            "Stationary: $E[X_t]=\\mu$, $\\mathrm{Cov}(X_t,X_{t+k})$ depends only on lag $k$\n"
            "AR(1): $X_t = \\phi X_{t-1} + \\varepsilon_t$, $|\\phi|<1$ ⇒ stationary\n"
            "Random walk: $X_t = X_{t-1} + \\varepsilon_t$ (not stationary — variance grows)\n"
            "ACF at lag $k$: correlation of $X_t$ with $X_{t-k}$"
        ),
        intuition=(
            "Stationarity means the world tomorrow looks like the world today in distribution. "
            "A random walk has no mean reversion — differences are the stationary object "
            "($\\Delta X_t = \\varepsilon_t$). Volatility clustering (GARCH) is 'variance has "
            "memory' even when returns look uncorrelated."
        ),
        worked_example=(
            "Q: AR(1) with $\\phi=0.8$, $\\varepsilon_t \\sim$ iid mean 0, var $1$. What is "
            "$\\mathrm{Var}(X_t)$ at stationarity?\n\n"
            "Solve: $\\mathrm{Var}(X_t) = 0.64\\,\\mathrm{Var}(X_t) + 1$ ⇒ "
            "$0.36\\,\\mathrm{Var}(X_t)=1$ ⇒ $\\mathrm{Var}(X_t)=1/0.36 \\approx 2.78$.\n\n"
            "Contrast: random walk ($\\phi=1$) has $\\mathrm{Var}(X_t)=t\\,\\mathrm{Var}(\\varepsilon)$ "
            "— grows with $t$."
        ),
        interview_tips=(
            "1. State stationary vs unit root before fitting anything.\n"
            "2. AR(1) mean is 0 if $\\varepsilon$ mean 0; long-run variance formula uses $1-\\phi^2$.\n"
            "3. ACF of AR(1) decays as $\\phi^k$ — geometric memory.\n"
            "4. For returns, test whether you model levels or differences.\n"
            "5. GARCH: name it as 'conditional variance depends on past shocks' if asked."
        ),
        prerequisites="Linear Regression (OLS); Limit Theorems helpful",
    ),
    "stochastic-processes": ConceptSeed(
        slug="stochastic-processes",
        name="Stochastic Processes",
        topic_slug="stochastic-processes",
        definition=(
            "A stochastic process is a collection of random variables $\\{X_t\\}_{t\\in T}$ indexed "
            "by time (or space). Interview focus: Markov property, Poisson and compound Poisson "
            "jump models, filtrations at a cartoon level — link to counting without re-teaching "
            "Markov chains from Probability."
        ),
        formula=(
            "Markov: $P(X_{t+1}\\mid X_t,X_{t-1},\\ldots)=P(X_{t+1}\\mid X_t)$\n"
            "Poisson$(\\lambda)$: $P(N_t=k)=e^{-\\lambda t}(\\lambda t)^k/k!$\n"
            "Compound Poisson: jumps $Y_i$ iid, $X_t=\\sum_{i=1}^{N_t} Y_i$\n"
            "Adapted: $X_t$ is known given information up to time $t$"
        ),
        intuition=(
            "A process is a rule for random evolution. Markov means only the present matters "
            "for the future. Poisson counts rare events in continuous time; compound Poisson "
            "adds random jump sizes — common in credit / operational risk sketches."
        ),
        worked_example=(
            "Q: $N_t$ is Poisson with rate $\\lambda=3$ per hour. Find $P(N_1=0)$ and "
            "$E[N_1]$.\n\n"
            "Solve: $E[N_1]=\\lambda t = 3$. $P(N_1=0)=e^{-3} \\approx 0.050$.\n\n"
            "Compound sketch: if each event costs iid $Y_i$ with $E[Y]=100$, then "
            "$E[X_1]=E[N_1]E[Y]=300$ by Wald / double expectation."
        ),
        interview_tips=(
            "1. Say Markov in words: conditional future depends only on current state.\n"
            "2. Poisson inter-arrival times are Exponential$(\\lambda)$ — link to Probability.\n"
            "3. Compound Poisson: separate counting from jump-size distribution.\n"
            "4. Don't confuse process stationarity with Markov property.\n"
            "5. For filtrations: 'what you know at time $t$' — informal is fine."
        ),
        prerequisites="Random Variables; Markov Chains (related)",
    ),
    "brownian-motion": ConceptSeed(
        slug="brownian-motion",
        name="Brownian Motion & GBM",
        topic_slug="brownian-motion",
        definition=(
            "Standard Brownian motion $W_t$ has independent Gaussian increments, $W_0=0$, and "
            "continuous paths. Geometric Brownian motion (GBM) models asset prices as "
            "$dS_t = \\mu S_t\\,dt + \\sigma S_t\\,dW_t$, giving lognormal $S_T$. Interview "
            "focus: BM facts + GBM intuition — full Black–Scholes derivation lives under Finance."
        ),
        formula=(
            "$W_t - W_s \\sim N(0, t-s)$ for $t>s$; $W_0=0$\n"
            "Quadratic variation: $[W]_t = t$\n"
            "GBM solution: $S_t = S_0 \\exp\\big((\\mu-\\tfrac{1}{2}\\sigma^2)t + \\sigma W_t\\big)$\n"
            "$\\log S_t$ is normal ⇒ $S_t$ is lognormal"
        ),
        intuition=(
            "BM is the continuous-time limit of a symmetric random walk — Gaussian shocks, "
            "nowhere differentiable paths. GBM forces positivity and multiplicative noise; "
            "the $-\\tfrac{1}{2}\\sigma^2$ term is Itô correction so $\\log S$ has the right drift."
        ),
        worked_example=(
            "Q: $W_t$ standard BM. What is $E[W_t]$, $\\mathrm{Var}(W_t)$, and $E[W_t^2]$?\n\n"
            "Solve: $E[W_t]=0$, $\\mathrm{Var}(W_t)=t$, so $E[W_t^2]=t$.\n\n"
            "GBM: if $S_0=100$, $\\mu=0.05$, $\\sigma=0.2$, one year, then "
            "$E[S_1]=100 e^{0.05} \\approx 105.13$ (not $100(1+0.05)$ — Jensen)."
        ),
        interview_tips=(
            "1. Increments independent and Gaussian — state both.\n"
            "2. $W_t^2$ has mean $t$; don't claim $W_t^2$ has mean $t^2$.\n"
            "3. GBM ⇒ log returns normal, not price levels.\n"
            "4. Point to Black–Scholes concept for option pricing on GBM.\n"
            "5. Quadratic variation matters in Itô calculus — mention if SDEs come up."
        ),
        prerequisites="Stochastic Processes; Common Distributions",
    ),
    "monte-carlo": ConceptSeed(
        slug="monte-carlo",
        name="Monte Carlo Methods",
        topic_slug="monte-carlo",
        definition=(
            "Monte Carlo estimates expectations by simulation: draw paths, average payoffs. "
            "Interview focus: law of large numbers for MC, standard error scaling $1/\\sqrt{N}$, "
            "pricing path-dependent options, and naming variance reduction (antithetic, control "
            "variates) without implementing full schemes."
        ),
        formula=(
            "$\\hat{\\mu}_N = N^{-1}\\sum_{i=1}^N g(X^{(i)}) \\approx E[g(X)]$\n"
            "MC SE $\\approx \\widehat{\\mathrm{SD}}(g)/\\sqrt{N}$\n"
            "To halve error ⇒ 4× samples\n"
            "European call: average $e^{-rT}(S_T-K)^+$ over simulated GBM paths"
        ),
        intuition=(
            "Simulation trades compute for generality — path-dependent and high-dimensional "
            "payoffs where closed forms fail. Error shrinks slowly with $N$; variance reduction "
            "is about getting the same SE with fewer paths."
        ),
        worked_example=(
            "Q: You estimate an option price with $N=10{,}000$ paths and sample SD of discounted "
            "payoffs is $2.50. Rough 95% CI width?\n\n"
            "Solve: SE $\\approx 2.50/\\sqrt{10000}=0.025$. 95% CI $\\approx \\hat{\\mu} \\pm "
            "1.96(0.025) \\approx \\hat{\\mu} \\pm 0.05$.\n\n"
            "If you need SE $0.01$, need $N \\approx (2.50/0.01)^2 = 62{,}500$ paths."
        ),
        interview_tips=(
            "1. Always report MC error bars — SE scales $1/\\sqrt{N}$.\n"
            "2. Antithetic: pair $Z$ and $-Z$ for symmetric problems.\n"
            "3. Control variate: use correlated quantity with known mean to reduce variance.\n"
            "4. Seed RNG for reproducibility in research code.\n"
            "5. MC is unbiased if you simulate the correct law — bias comes from discretization."
        ),
        prerequisites="Expectation; Brownian Motion & GBM",
    ),
    "numerical-methods": ConceptSeed(
        slug="numerical-methods",
        name="Numerical Methods",
        topic_slug="numerical-methods",
        definition=(
            "Numerical methods approximate continuous models on a grid or via iteration: "
            "Euler–Maruyama for SDEs, finite differences for PDEs (sketch), Newton/bisection "
            "for implied vol. Interview focus: stability vs accuracy and what discretization "
            "bias does to MC/PDE prices."
        ),
        formula=(
            "Euler–Maruyama: $X_{n+1}=X_n + \\mu\\Delta t + \\sigma\\sqrt{\\Delta t}\\,Z_n$\n"
            "Implied vol: solve $\\sigma$ s.t. $C_{\\mathrm{BS}}(\\sigma)=C_{\\mathrm{mkt}}$\n"
            "FDM sketch: replace $\\partial_x$ with $(f_{i+1}-f_i)/\\Delta x$\n"
            "Newton: $x_{n+1}=x_n - f(x_n)/f'(x_n)$"
        ),
        intuition=(
            "Discretization introduces error — smaller steps help but cost compute. For SDEs, "
            "Euler is first-order; too large $\\Delta t$ biases path-dependent option estimates. "
            "Root-finding inverts the pricing map (implied vol)."
        ),
        worked_example=(
            "Q: Simulate GBM with $S_0=100$, $\\mu=0$, $\\sigma=0.3$, one step $\\Delta t=1$. "
            "One draw $Z=1$. Euler–Maruyama value?\n\n"
            "Solve: $S_1 \\approx S_0 + \\sigma S_0 \\sqrt{\\Delta t}\\,Z = 100 + 30 = 130$ "
            "(drift-zero Euler on levels; log-Euler is also common — state which you use).\n\n"
            "Implied vol: if BS price is 10 and Newton gives $\\sigma=0.22$, verify by "
            "re-pricing — one iteration is rarely enough."
        ),
        interview_tips=(
            "1. Name the error source: discretization vs sampling vs root tolerance.\n"
            "2. Euler–Maruyama is the baseline SDE scheme — know it cold.\n"
            "3. Implied vol is a root-finding problem; bracket with bisection if Newton unstable.\n"
            "4. FDM: mention CFL / stability if they push PDEs.\n"
            "5. Convex optimization theory is under Mathematics — here you implement solvers."
        ),
        prerequisites="Differential Equations; Monte Carlo Methods",
    ),
    "machine-learning-for-finance": ConceptSeed(
        slug="machine-learning-for-finance",
        name="Statistical Learning for Alpha",
        topic_slug="machine-learning-for-finance",
        definition=(
            "Using ML-style models to forecast returns or build signals — interview focus is "
            "research hygiene: overfitting, train/test splits, purged cross-validation for "
            "overlapping labels, regularization, and data leakage — not a sklearn API quiz."
        ),
        formula=(
            "Train error vs test error: gap ⇒ overfitting\n"
            "Ridge: minimize $\\|y-X\\beta\\|^2 + \\lambda\\|\\beta\\|^2$\n"
            "Purged CV: remove training samples whose labels overlap test window in time\n"
            "Sharpe of strategy $\\approx$ mean return / std (know limitations)"
        ),
        intuition=(
            "Markets are low signal-to-noise — flexible models memorize noise. Time ordering "
            "matters: random CV on financial panels leaks future into past. A 'great' backtest "
            "with leakage is worse than useless."
        ),
        worked_example=(
            "Q: You fit a 500-feature model on 5 years of daily data and get 80% in-sample "
            "directional accuracy but 51% out-of-sample. Diagnose.\n\n"
            "Solve: classic overfitting / multiple testing. Too many degrees of freedom vs "
            "effective sample size; in-sample metric is optimistically biased. Next: reduce "
            "features, regularize, purged walk-forward CV, report OOS Sharpe with costs.\n\n"
            "Leakage example: using tomorrow's open to predict today's close in features — "
            "inflates performance."
        ),
        interview_tips=(
            "1. Lead with overfitting and leakage before model architecture.\n"
            "2. Purged / embargo CV for overlapping return horizons.\n"
            "3. Ridge/Lasso as variance reduction on coefficients — link to bias–variance.\n"
            "4. Report economic significance (after costs), not just accuracy.\n"
            "5. OLS is a baseline — beat it with justification, not complexity alone."
        ),
        prerequisites="Bias–Variance Tradeoff; Linear Regression (OLS)",
    ),
    "brain-teasers": ConceptSeed(
        slug="brain-teasers",
        name="Brain Teasers",
        topic_slug="brain-teasers",
        definition=(
            "Brain teasers test structured reasoning under ambiguity: logic puzzles, invariants, "
            "Fermi estimates, and lateral 'aha' problems. Interviewers care less about the exact "
            "answer than a clear decomposition, sanity checks, and stated assumptions."
        ),
        formula=(
            "Fermi: $\\text{estimate} \\approx \\prod (\\text{reasonable factors})$\n"
            "Invariant: quantity unchanged under allowed operations\n"
            "Pigeonhole: $n+1$ objects in $n$ bins ⇒ a collision\n"
            "Weighing coins: $k$ weighings distinguish $3^k$ outcomes"
        ),
        intuition=(
            "Resist guessing — narrate a model. For logic puzzles, track what must be true after "
            "each step. For Fermi, bracket high/low then multiply independent estimates."
        ),
        worked_example=(
            "Q: How many piano tuners in Chicago? (Fermi sketch)\n\n"
            "Solve: Population $\\approx 3$M. Households $\\approx 1$M. Pianos per 50 households "
            "⇒ $\\sim 20{,}000$ pianos. Tune once/year, tuner does $\\sim 4$/day, 250 days "
            "⇒ 1000 tunings/year each. Need $\\sim 20{,}000/1000 = 20$ tuners (order of magnitude).\n\n"
            "Logic: 12 coins, one fake (lighter). Minimum weighings on a balance scale? "
            "Three outcomes per weighing ⇒ $3^2=9<12\\le 27=3^3$ ⇒ **3 weighings** suffice with "
            "the right grouping."
        ),
        interview_tips=(
            "1. Say assumptions out loud before arithmetic.\n"
            "2. Round aggressively — Fermi is order-of-magnitude.\n"
            "3. For invariants (color parity, sum mod 3), name the preserved quantity.\n"
            "4. If stuck, try a tiny version of the puzzle ($n=2,3$).\n"
            "5. Don't claim precision you don't have — give a range."
        ),
        prerequisites="None — start here on the Other Sections path",
    ),
    "game-theory": ConceptSeed(
        slug="game-theory",
        name="Game Theory",
        topic_slug="game-theory",
        definition=(
            "Game theory models strategic interaction: players, actions, payoffs, and equilibrium "
            "concepts. Interview focus: dominant strategies, Nash equilibrium, mixed strategies "
            "(light), and classic 2×2 games — not full mechanism-design proofs."
        ),
        formula=(
            "Dominant strategy: best regardless of opponent's move\n"
            "Nash: no player gains by unilateral deviation\n"
            "Mixed NE (2×2): indifference $E[\\pi_1 \\mid p] = E[\\pi_1 \\mid q]$\n"
            "Prisoner's dilemma: (Temptation, Reward, Punish, Sucker) with $T>R>P>S$"
        ),
        intuition=(
            "Predict behavior by asking 'given what others do, would I switch?' If everyone is "
            "best-responding, you're at Nash. Dominant-strategy games are easy; coordination "
            "games need beliefs or focal points."
        ),
        worked_example=(
            "Q: Two firms choose High or Low output. Payoffs (row, col): (H,H)=(2,2), (H,L)=(4,0), "
            "(L,H)=(0,4), (L,L)=(3,3). Find Nash equilibria.\n\n"
            "Solve: If col plays H, row prefers H (2 vs 0). If col plays L, row prefers H (4 vs 3). "
            "H is dominant for row; symmetric for col. Unique NE: **(H,H)**.\n\n"
            "Prisoner's dilemma: mutual cooperate beats mutual defect, but Temptation makes "
            "defect dominant ⇒ NE is mutual defect despite (R,R) being better."
        ),
        interview_tips=(
            "1. Write the payoff matrix before talking.\n"
            "2. Check dominant strategies first — saves time.\n"
            "3. For mixed strategies, set expected payoffs equal across opponent mixes.\n"
            "4. Distinguish Nash from Pareto optimal — they need not coincide.\n"
            "5. Auctions: second-price ⇒ truthful bidding is weakly dominant (Vickrey)."
        ),
        prerequisites="Expectation helpful; Probability counting for mixed strategies",
    ),
    "market-games": ConceptSeed(
        slug="market-games",
        name="Market Games",
        topic_slug="market-games",
        definition=(
            "Trading-desk interview games: guess 2/3 of the average, Monty Hall, market-making "
            "spreads, penny auctions, optimal stopping. Tests iterative reasoning, probability "
            "under rules, and tradeoffs between spread width and adverse selection — interactive "
            "UI is Phase 8; concepts + practice prompts come first."
        ),
        formula=(
            "2/3-of-average: iterate 'everyone rational' ⇒ bids collapse toward 0\n"
            "Monty Hall (switch): $P(\\text{win}\\mid\\text{switch}) = 2/3$\n"
            "Secretary problem: reject first $n/e$, then pick next best\n"
            "Market making: tighter spread ⇒ more flow + more adverse selection"
        ),
        intuition=(
            "These games blend game theory and probability with trading instincts. Level-$k$ "
            "thinking ('what do others think I think…') matters for 2/3 games. Monty Hall is "
            "a conditional probability trap — switching doubles win rate under standard rules."
        ),
        worked_example=(
            "Q: Monty Hall — you pick door 1, host opens goat on door 3, offers switch to door 2. "
            "Switch or stay?\n\n"
            "Solve: Car equally likely behind 1,2,3 initially. Your pick wins with prob $1/3$. "
            "Host opens a goat. Switching wins iff car was not behind your door ⇒ **switch wins "
            "with $2/3$**.\n\n"
            "2/3-of-average on [0,100]: if all pick randomly (avg 50), target 33; iterate ⇒ "
            "experienced players bid lower. Jane Street-style: model opponent depth."
        ),
        interview_tips=(
            "1. State game rules precisely before analyzing.\n"
            "2. Monty Hall: host knowledge matters — not generic 'switch always'.\n"
            "3. Market making: name adverse selection when tightening.\n"
            "4. Penny auctions: bid fees mean EV can be deeply negative.\n"
            "5. Link to Game Theory concept for equilibrium language."
        ),
        prerequisites="Game Theory",
    ),
    "behavioral-interview": ConceptSeed(
        slug="behavioral-interview",
        name="Behavioral Interview",
        topic_slug="behavioral-interview",
        definition=(
            "Two lanes in one: cognitive biases that distort trading and research decisions, "
            "and structured behavioral questions (STAR stories, motivation, failure, teamwork). "
            "Interviewers want self-awareness plus concrete examples — not generic platitudes."
        ),
        formula=(
            "STAR: Situation → Task → Action → Result\n"
            "Base-rate neglect: ignore prior, overweight vivid evidence\n"
            "Loss aversion: losses loom larger than equal gains\n"
            "Overconfidence: narrow confidence intervals, excessive trading"
        ),
        intuition=(
            "Biases explain why smart people trade badly; STAR stories prove you can collaborate "
            "and learn. Quant shops ask both — connect bias awareness to risk management and "
            "humility in research."
        ),
        worked_example=(
            "Bias example: After three winning days, you size up because you 'feel hot' — "
            "overconfidence + recency. Fix: pre-commit rules, track hit rate vs baseline, "
            "use base rates.\n\n"
            "STAR sketch — 'Tell me about a mistake':\n"
            "S: Backtest looked great on in-sample data.\n"
            "T: Validate before proposing to the team.\n"
            "A: Ran purged walk-forward CV, found leakage from future data in features.\n"
            "R: Fixed pipeline; presented honest OOS results; team trusted the process."
        ),
        interview_tips=(
            "1. Have 3–5 polished stories (conflict, failure, leadership, tight deadline).\n"
            "2. Quantify results when possible ('Sharpe dropped from X to Y').\n"
            "3. Name the bias if asked about bad trading decisions.\n"
            "4. 'Why quant?' — tie curiosity + puzzles + markets, not only money.\n"
            "5. Link to Bayes for base-rate / base-rate neglect answers."
        ),
        prerequisites="None (Bayes concept helpful for bias framing)",
    ),
    "system-design": ConceptSeed(
        slug="system-design",
        name="System Design for Quant",
        topic_slug="system-design",
        definition=(
            "Architecture for quant systems: market-data ingestion, backtesting/research "
            "pipelines, execution, and low-latency paths. Interview focus is tradeoffs "
            "(correctness vs speed, batch vs stream), not drawing a generic microservices "
            "diagram from big-tech SWE interviews."
        ),
        formula=(
            "Backtest loop: data → signals → simulator → PnL / metrics\n"
            "Latency budget: feed + strategy + risk + gateway\n"
            "Idempotent replay: same inputs ⇒ same outputs (research reproducibility)\n"
            "CAP sketch: pick consistency vs availability under partition"
        ),
        intuition=(
            "Research wants reproducibility and fast iteration; production wants reliability "
            "and bounded tail latency. Separate research sandbox from live trading stack; "
            "never let a backtest shortcut become a silent live bug."
        ),
        worked_example=(
            "Q: Design a daily equity backtester for a small team.\n\n"
            "Sketch: (1) **Data layer** — point-in-time corporate actions, split-adjusted "
            "bars in Parquet/S3. (2) **Signal layer** — Python research notebooks → versioned "
            "signal code. (3) **Simulator** — event-driven or vectorized; apply slippage/fees "
            "model. (4) **Metrics** — Sharpe, drawdown, turnover; store run configs for "
            "reproducibility. (5) **Guardrails** — no lookahead joins; audit feature timestamps.\n\n"
            "Live extension: add streaming feed handler + order gateway + kill switch — "
            "different SLA, shared instrument master."
        ),
        interview_tips=(
            "1. Clarify scale: bars vs ticks, assets, latency target.\n"
            "2. Mention point-in-time data — #1 backtest bug.\n"
            "3. Separate hot path (C++) from research (Python) if relevant.\n"
            "4. Monitoring: PnL breaks, stale quotes, position limits.\n"
            "5. Don't over-engineer Kubernetes on a first pass — show sensible MVP."
        ),
        prerequisites="Python for Quant; Core Data Structures helpful",
    ),
}


CONCEPT_EDGES: tuple[ConceptEdgeSeed, ...] = (
    ConceptEdgeSeed('independence', 'counting', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('conditional-probability', 'counting', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('independence', 'conditional-probability', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('bayes', 'conditional-probability', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('bayes', 'independence', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('bayes', 'counting', ConceptEdgeRelationshipType.USED_IN),
    ConceptEdgeSeed('bayes', 'continuous-distributions', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('random-variables', 'counting', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('expectation', 'random-variables', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('expectation', 'counting', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('random-variables', 'expectation', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('conditional-expectation', 'expectation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('conditional-expectation', 'conditional-probability', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('variance', 'expectation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('continuous-distributions', 'random-variables', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('continuous-distributions', 'expectation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('continuous-distributions', 'variance', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('limit-theorems', 'expectation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('limit-theorems', 'variance', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('limit-theorems', 'continuous-distributions', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('markov-chains', 'random-variables', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('markov-chains', 'conditional-probability', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('martingales', 'conditional-expectation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('martingales', 'markov-chains', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('linear-systems', 'vectors-matrices', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('eigenvalues', 'vectors-matrices', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('eigenvalues', 'linear-systems', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('orthogonality', 'vectors-matrices', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('orthogonality', 'eigenvalues', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('taylor-expansions', 'derivatives-gradients', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('math-optimization', 'derivatives-gradients', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('lagrange-multipliers', 'math-optimization', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('lagrange-multipliers', 'derivatives-gradients', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('differential-equations', 'derivatives-gradients', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('confidence-intervals', 'estimation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('hypothesis-testing', 'estimation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed(
        'hypothesis-testing', 'confidence-intervals', ConceptEdgeRelationshipType.REQUIRES
    ),
    ConceptEdgeSeed('maximum-likelihood', 'estimation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed(
        'maximum-likelihood',
        'continuous-distributions',
        ConceptEdgeRelationshipType.RELATED_TO,
    ),
    ConceptEdgeSeed('regression', 'estimation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('regression', 'hypothesis-testing', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('regression', 'orthogonality', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('bias-variance', 'estimation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('bias-variance', 'regression', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('black-scholes', 'derivatives', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('greeks', 'black-scholes', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('greeks', 'derivatives', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('portfolio-theory', 'variance', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('capm', 'portfolio-theory', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('fixed-income', 'derivatives', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed(
        'market-microstructure', 'derivatives', ConceptEdgeRelationshipType.RELATED_TO
    ),
    ConceptEdgeSeed('data-structures', 'python', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('cpp', 'data-structures', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('algorithms', 'data-structures', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('algorithms', 'python', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('sql', 'algorithms', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('stochastic-processes', 'random-variables', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('stochastic-processes', 'markov-chains', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('stochastic-processes', 'time-series', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('brownian-motion', 'stochastic-processes', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('brownian-motion', 'black-scholes', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('monte-carlo', 'brownian-motion', ConceptEdgeRelationshipType.USED_IN),
    ConceptEdgeSeed('monte-carlo', 'expectation', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('numerical-methods', 'monte-carlo', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('numerical-methods', 'differential-equations', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('numerical-methods', 'math-optimization', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('time-series', 'regression', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('time-series', 'limit-theorems', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('machine-learning-for-finance', 'bias-variance', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('machine-learning-for-finance', 'regression', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('sliding-window', 'two-pointers', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('prefix-sum', 'algorithms', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('binary-search', 'algorithms', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('intervals', 'two-pointers', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('graph-traversal', 'data-structures', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('dynamic-programming', 'algorithms', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed(
        'dynamic-programming', 'graph-traversal', ConceptEdgeRelationshipType.RELATED_TO
    ),
    ConceptEdgeSeed('greedy', 'intervals', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('two-pointers', 'data-structures', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('addition-subtraction', 'quick-tricks', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('basic-multiplication', 'addition-subtraction', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('intermediate-multiplication', 'basic-multiplication', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('mental-division-fractions', 'basic-multiplication', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('guesstimation', 'addition-subtraction', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed(
        'guesstimation', 'mental-division-fractions', ConceptEdgeRelationshipType.RELATED_TO
    ),
    ConceptEdgeSeed('memorizing-numbers', 'intermediate-multiplication', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('advanced-multiplication', 'intermediate-multiplication', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('advanced-multiplication', 'memorizing-numbers', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('game-theory', 'expectation', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('market-games', 'game-theory', ConceptEdgeRelationshipType.REQUIRES),
    ConceptEdgeSeed('market-games', 'market-microstructure', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('behavioral-interview', 'bayes', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('system-design', 'python', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('system-design', 'data-structures', ConceptEdgeRelationshipType.RELATED_TO),
    ConceptEdgeSeed('brain-teasers', 'counting', ConceptEdgeRelationshipType.RELATED_TO),
)
