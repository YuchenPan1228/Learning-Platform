from app.models.enums import Difficulty
from app.seeds.data.question_seed import QuestionSeed

BRAIN_TEASER_QUESTIONS: tuple[QuestionSeed, ...] = (
    # --- Fermi estimates ---
    QuestionSeed(
        seed_key="oth-001",
        title="Piano Tuners in New York City",
        body=(
            "Estimate the number of piano tuners in New York City. "
            "State key assumptions and give an order-of-magnitude answer."
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="about 100–300",
        canonical_solution=(
            "NYC $\\approx 8$M people, $\\sim 3$M households. "
            "Maybe 1 piano per 50 households ⇒ $\\sim 60{,}000$ pianos. "
            "Each tuned once/year; a tuner handles $\\sim 4$/day, 250 days "
            "⇒ 1000 pianos/year per tuner. "
            "Need $\\sim 60{,}000/1000 = 60$ tuners; generous assumptions push toward low hundreds."
        ),
        estimated_time_seconds=300,
        common_mistakes=(
            "Skipping assumptions and guessing a number",
            "Treating Fermi as needing a precise count",
        ),
        prerequisites=("Fermi decomposition",),
    ),
    QuestionSeed(
        seed_key="oth-002",
        title="Golf Balls in a School Bus",
        body=(
            "Roughly how many standard golf balls fit in an empty school bus? "
            "Give an order-of-magnitude estimate."
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="about $10^6$",
        canonical_solution=(
            "Bus interior $\\approx 2.5\\,\\text{m} \\times 2\\,\\text{m} \\times 10\\,\\text{m} "
            "⇒ $\\sim 50\\,\\text{m}^3$ usable volume. "
            "Ball diameter $\\approx 4\\,\\text{cm}$ ⇒ volume $\\sim 30\\,\\text{cm}^3$. "
            "Packing efficiency $\\sim 60\\%$ ⇒ "
            "$50\\times 10^6 / 30 \\times 0.6 \\approx 10^6$ balls."
        ),
        estimated_time_seconds=300,
        prerequisites=("Volume estimation",),
    ),
    QuestionSeed(
        seed_key="oth-003",
        title="US Gas Stations",
        body=(
            "Estimate how many gas stations operate in the United States. "
            "Order of magnitude is enough."
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="about $10^5$",
        canonical_solution=(
            "US $\\approx 330$M people, $\\sim 250$M licensed drivers. "
            "Each fills up roughly once/week ⇒ $\\sim 13$B fill-ups/year. "
            "A busy station might serve $\\sim 10^5$ customers/year "
            "⇒ $1.3\\times 10^{10}/10^5 \\approx 10^5$ stations nationally."
        ),
        estimated_time_seconds=360,
        common_mistakes=("Using population without translating to fill-up rate",),
        prerequisites=("Fermi decomposition",),
    ),
    QuestionSeed(
        seed_key="oth-004",
        title="Tennis Balls in a Room",
        body=(
            "A room is roughly $10\\,\\text{ft} \\times 10\\,\\text{ft} \\times 10\\,\\text{ft}$. "
            "About how many tennis balls fit inside (order of magnitude)?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.EASY,
        short_answer="about $10^4$",
        canonical_solution=(
            "Room volume $\\approx 1000\\,\\text{ft}^3 \\approx 30\\,\\text{m}^3$. "
            "Tennis ball $\\approx 6.5\\,\\text{cm}$ diameter ⇒ $\\sim 150\\,\\text{cm}^3$. "
            "Loose packing $\\sim 50\\%$ ⇒ $3\\times 10^7 / 150 \\times 0.5 \\approx 10^5$; "
            "tighter stacking often quoted $\\sim 10^4$–$10^5$ — either defensible with stated packing."
        ),
        estimated_time_seconds=240,
        prerequisites=("Unit conversion",),
    ),
    # --- Weighing puzzles ---
    QuestionSeed(
        seed_key="oth-005",
        title="12 Coins, One Lighter",
        body=(
            "You have 12 identical-looking coins; exactly one is counterfeit and lighter. "
            "Using a two-pan balance scale, what is the minimum number of weighings "
            "guaranteed to find the fake coin?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="3",
        canonical_solution=(
            "Each weighing has 3 outcomes (left heavy, right heavy, balance). "
            "$3^2=9<12\\le 27=3^3$, so 2 weighings are insufficient in the worst case; "
            "3 weighings suffice with a standard ternary split strategy."
        ),
        estimated_time_seconds=300,
        common_mistakes=(
            "Answering 4 by halving repeatedly (binary thinking)",
            "Forgetting the balance has three outcomes",
        ),
        prerequisites=("Ternary weighing logic",),
    ),
    QuestionSeed(
        seed_key="oth-006",
        title="9 Coins, One Heavier",
        body=(
            "Nine coins look identical; one is heavier than the rest. "
            "What is the minimum number of balance-scale weighings to identify the heavy coin?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.EASY,
        short_answer="2",
        canonical_solution=(
            "Weigh 3 vs 3. If unequal, heavy side has the coin; if equal, coin is in the remaining 3. "
            "Second weighing: 1 vs 1 on the suspect triple identifies the heavy coin."
        ),
        estimated_time_seconds=180,
        prerequisites=("Balance-scale grouping",),
    ),
    QuestionSeed(
        seed_key="oth-007",
        title="8 Balls, One Heavier",
        body=(
            "Eight balls; one is heavier. Can you always find it in exactly 2 weighings on a balance scale?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="yes",
        canonical_solution=(
            "Weigh 3 vs 3. If balanced, weigh 1 vs 1 among the remaining 2. "
            "If unbalanced, take the heavy 3 and weigh 1 vs 1; equal means the unweighed ball is heavy."
        ),
        estimated_time_seconds=240,
        prerequisites=("Weighing puzzle strategy",),
    ),
    # --- Logic puzzles ---
    QuestionSeed(
        seed_key="oth-008",
        title="Two Doors, Two Guards",
        body=(
            "Two doors: one leads to freedom, one to doom. "
            "One guard always lies, one always tells the truth; you don't know which is which. "
            "You may ask one guard one yes/no question. "
            "What question guarantees you pick the freedom door?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.HARD,
        short_answer="ask what the other guard would say",
        canonical_solution=(
            "Ask either guard: 'If I asked the other guard whether this door leads to freedom, "
            "would they say yes?' Both liar and truth-teller point you to the wrong door — choose the opposite."
        ),
        estimated_time_seconds=360,
        common_mistakes=("Asking a direct question to one guard without double negation",),
        prerequisites=("Logic / self-reference",),
    ),
    QuestionSeed(
        seed_key="oth-009",
        title="Three Switches, One Bulb",
        body=(
            "In another room are three light switches; in a second room is one bulb (initially off). "
            "You may flip switches, then enter the bulb room once. "
            "How do you determine which switch controls the bulb?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="heat from a lit bulb",
        canonical_solution=(
            "Turn switch 1 on for several minutes, then off. Turn switch 2 on and enter. "
            "On ⇒ switch 2; off but warm ⇒ switch 1; off and cold ⇒ switch 3."
        ),
        estimated_time_seconds=240,
        prerequisites=("Use all available state variables",),
    ),
    QuestionSeed(
        seed_key="oth-010",
        title="Mislabeled Fruit Boxes",
        body=(
            "Three boxes are labeled Apples, Oranges, and Apples+Oranges, but every label is wrong. "
            "You may draw one fruit from one box (without looking inside). "
            "Which box do you draw from to relabel all boxes correctly?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="Apples+Oranges box",
        canonical_solution=(
            "Draw from the box labeled Apples+Oranges — it contains only one fruit type. "
            "If apple, that box is Apples; the Oranges-labeled box must be mixed; "
            "the Apples-labeled box is Oranges."
        ),
        estimated_time_seconds=240,
        prerequisites=("Constraint propagation",),
    ),
    QuestionSeed(
        seed_key="oth-011",
        title="Heavier or Lighter Unknown",
        body=(
            "12 coins; one is counterfeit and either heavier or lighter (you don't know which). "
            "What is the minimum number of balance weighings guaranteed to find it and its type?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.HARD,
        short_answer="3",
        canonical_solution=(
            "First weighing 4 vs 4 narrows to 4 suspects with known heavy/light possibilities. "
            "Careful second and third weighings disambiguate — classic solution uses 3 weighings total."
        ),
        estimated_time_seconds=420,
        common_mistakes=("Assuming you know heavy vs light upfront",),
        prerequisites=("Advanced coin weighing",),
    ),
    # --- Pigeonhole & invariants ---
    QuestionSeed(
        seed_key="oth-012",
        title="Socks in a Dark Drawer",
        body=(
            "A drawer has 10 black socks and 10 white socks, mixed randomly. "
            "How many socks must you pull out (in the dark) to guarantee a matching pair?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.EASY,
        short_answer="3",
        canonical_solution=(
            "Worst case: first black, second white. Third sock must match one of them. "
            "By pigeonhole, 3 socks with 2 colors forces a pair."
        ),
        estimated_time_seconds=90,
        prerequisites=("Pigeonhole principle",),
    ),
    QuestionSeed(
        seed_key="oth-013",
        title="Birthday Months",
        body=(
            "In a group of 13 people, must at least two share a birth month? Answer yes or no."
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.EASY,
        short_answer="yes",
        canonical_solution=(
            "12 months, 13 people — pigeonhole principle guarantees a shared month."
        ),
        estimated_time_seconds=60,
        prerequisites=("Pigeonhole principle",),
    ),
    QuestionSeed(
        seed_key="oth-014",
        title="Checkerboard Corners Removed",
        body=(
            "An $8\\times 8$ checkerboard has two opposite corner squares removed. "
            "Can the remaining 62 squares be tiled exactly by 31 dominoes (each covers 2 adjacent squares)?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="no",
        canonical_solution=(
            "Opposite corners are the same color. Removing them leaves 32 of one color and 30 of the other. "
            "Each domino covers one black and one white square — parity invariant makes tiling impossible."
        ),
        estimated_time_seconds=240,
        common_mistakes=("Trying to construct a tiling instead of using parity",),
        prerequisites=("Color parity invariant",),
    ),
    # --- Classic lateral puzzles ---
    QuestionSeed(
        seed_key="oth-015",
        title="Measure 4 Liters",
        body=(
            "You have a 3-liter jug and a 5-liter jug (no other markings). "
            "How do you measure exactly 4 liters of water?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="fill 5, pour into 3, refill 5, top up 3",
        canonical_solution=(
            "Fill 5L, pour into 3L until full (leaves 2L in 5L). Empty 3L, pour the 2L in, "
            "refill 5L, pour 1L into 3L to fill it — 4L remains in the 5L jug."
        ),
        estimated_time_seconds=300,
        prerequisites=("State-space reasoning",),
    ),
    QuestionSeed(
        seed_key="oth-016",
        title="Wolf, Goat, and Cabbage",
        body=(
            "A farmer must ferry a wolf, a goat, and a cabbage across a river in a boat that holds "
            "the farmer plus one item. The wolf cannot be left alone with the goat; "
            "the goat cannot be left alone with the cabbage. Describe a valid sequence."
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.MEDIUM,
        short_answer="goat first, return alone, take wolf, bring goat back, take cabbage, return, take goat",
        canonical_solution=(
            "Take goat over; return alone; take wolf over; bring goat back; "
            "take cabbage over; return alone; take goat over. All constraints satisfied."
        ),
        estimated_time_seconds=300,
        prerequisites=("Constraint satisfaction",),
    ),
    QuestionSeed(
        seed_key="oth-017",
        title="Burning Ropes for 45 Minutes",
        body=(
            "Two identical ropes each burn completely in exactly 60 minutes, but non-uniformly "
            "(not at constant rate). How can you measure exactly 45 minutes using only these ropes "
            "and a lighter?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.HARD,
        short_answer="light both ends of one, one end of the other",
        canonical_solution=(
            "Light rope A at both ends and rope B at one end. "
            "When A finishes (30 min), light the other end of B. "
            "B had 30 min left at constant wall-clock time; burning both ends takes 15 min more ⇒ 45 total."
        ),
        estimated_time_seconds=360,
        common_mistakes=("Assuming uniform burn rate along the rope",),
        prerequisites=("Non-uniform timing trick",),
    ),
    QuestionSeed(
        seed_key="oth-018",
        title="Hourglasses for 15 Minutes",
        body=(
            "You have 7-minute and 11-minute hourglasses. "
            "How do you measure exactly 15 minutes?"
        ),
        topic_slug="other-sections",
        subtopic_slug="brain-teasers",
        difficulty=Difficulty.HARD,
        short_answer="start both; flip 7 when 11 empties",
        canonical_solution=(
            "Start both hourglasses. When the 11-minute glass empties (11 min elapsed), "
            "the 7-minute glass has 4 minutes left — flip it. "
            "When the 7-minute glass empties again, exactly 15 minutes have passed."
        ),
        estimated_time_seconds=360,
        prerequisites=("Parallel timers",),
    ),
)
