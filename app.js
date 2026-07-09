const topics = [
  {
    name: "Probability",
    mastery: 50,
    count: 126,
    subtopics: [
      "Counting",
      "Conditional Probability",
      "Bayes",
      "Random Variables",
      "Expectation",
      "Variance",
      "Independence",
      "Continuous Distributions",
      "Markov Chains",
      "Martingales"
    ]
  },
  {
    name: "Mathematics",
    mastery: 38,
    count: 74,
    subtopics: ["Linear Algebra", "Calculus", "Optimization", "Differential Equations"]
  },
  {
    name: "Statistics",
    mastery: 45,
    count: 82,
    subtopics: ["Estimation", "Hypothesis Testing", "Regression", "Maximum Likelihood", "Confidence Intervals"]
  },
  {
    name: "Finance",
    mastery: 28,
    count: 91,
    subtopics: ["Derivatives", "Black-Scholes", "Greeks", "Portfolio Theory", "CAPM", "Fixed Income", "Market Microstructure"]
  },
  {
    name: "Programming",
    mastery: 70,
    count: 144,
    subtopics: ["Python", "C++", "SQL", "Algorithms", "Data Structures", "Coding Patterns"]
  },
  {
    name: "Coding Patterns",
    mastery: 62,
    count: 88,
    subtopics: ["Sliding Window", "Binary Search", "Prefix Sum", "Union Find", "Sweep Line", "Greedy", "DP", "Graph Traversal"]
  },
  {
    name: "Mental Math",
    mastery: 74,
    count: 160,
    subtopics: ["Arithmetic", "Fractions", "Percentages", "Approximations", "Logarithms", "Roots", "Powers", "Expected Value"]
  },
  {
    name: "Quant Research",
    mastery: 19,
    count: 64,
    subtopics: ["Time Series", "Stochastic Processes", "Brownian Motion", "Monte Carlo", "Numerical Methods", "ML for Finance"]
  },
  {
    name: "Market Games",
    mastery: 34,
    count: 28,
    subtopics: ["Auctions", "Market Making", "Coin Games", "Secretary Problem", "Monty Hall", "Trading Games"]
  }
];

const paths = [
  {
    name: "Probability Foundations",
    level: "Beginner to interview-ready",
    steps: ["Counting", "Conditional Probability", "Bayes", "Expectation", "Variance", "Random Variables", "Markov Chains"]
  },
  {
    name: "Coding Patterns for Quant SWE",
    level: "SWE + quant screens",
    steps: ["Arrays", "Prefix Sum", "Binary Search", "Sliding Window", "Intervals", "Graphs", "Dynamic Programming"]
  },
  {
    name: "Options and Market Making",
    level: "Trading interviews",
    steps: ["Expected Value", "Derivatives", "Black-Scholes", "Greeks", "Order Books", "Market Making Games"]
  },
  {
    name: "Quant Research Track",
    level: "Advanced",
    steps: ["Regression", "Time Series", "Stochastic Processes", "Brownian Motion", "Monte Carlo", "Optimization"]
  }
];

const plan = [
  ["Conditional Probability", "Prerequisite repair before Bayes questions", "20 min"],
  ["Bayes", "8 interview-style questions with base rates", "28 min"],
  ["Mental Math", "10 drills across logs, powers, fractions, estimates", "12 min"],
  ["Coding Patterns", "3 binary search and 2 prefix sum prompts", "20 min"],
  ["Finance", "Greeks intuition and one market-making scenario", "10 min"]
];

const questions = [
  {
    title: "Exactly 7 Heads",
    body: "You flip 10 fair coins. What is the probability of exactly 7 heads?",
    answer: "C(10,7)/2^10 = 120/1024 = 15/128.",
    tag: "binomial",
    metadata: {
      topics: "Probability",
      subtopics: "Counting, Random Variables",
      difficulty: "Easy",
      time: "3 min",
      companies: "General quant",
      frequency: "High",
      prerequisites: "Combinations",
      mistakes: "Forgetting to choose which flips are heads",
      related: "At least 7 heads, biased coin variants"
    }
  },
  {
    title: "Two Heads Given One Head",
    body: "Two fair coins are flipped. Given that at least one coin is heads, what is the probability both are heads?",
    answer: "The possible outcomes are HH, HT, TH. Only HH works, so the probability is 1/3.",
    tag: "conditional",
    metadata: {
      topics: "Probability",
      subtopics: "Conditional Probability, Bayes",
      difficulty: "Medium",
      time: "4 min",
      companies: "Jane Street-style",
      frequency: "High",
      prerequisites: "Sample spaces",
      mistakes: "Answering 1/2 after changing the sample space",
      related: "At least one boy, Monty Hall"
    }
  },
  {
    title: "Expected Rolls",
    body: "What is the expected number of fair die rolls needed to see the first six?",
    answer: "This is geometric with p = 1/6, so the expected wait is 1/p = 6.",
    tag: "expected value",
    metadata: {
      topics: "Probability",
      subtopics: "Expectation, Random Variables",
      difficulty: "Medium",
      time: "5 min",
      companies: "General quant",
      frequency: "Medium",
      prerequisites: "Geometric distribution",
      mistakes: "Trying to enumerate many cases instead of using the distribution",
      related: "Coupon collector, first success problems"
    }
  }
];

const mental = [
  { category: "Arithmetic", prompt: "13 x 27", answer: "351" },
  { category: "Powers", prompt: "25^2", answer: "625" },
  { category: "Roots", prompt: "sqrt(81)", answer: "9" },
  { category: "Fractions", prompt: "5! / 8!", answer: "1/336" },
  { category: "Logarithms", prompt: "ln(2)", answer: "0.693" },
  { category: "Approximations", prompt: "0.998^10", answer: "0.98" },
  { category: "Expected Value", prompt: "EV of fair die", answer: "3.5" },
  { category: "Percentages", prompt: "15% of 240", answer: "36" }
];

const conceptGraph = [
  ["Counting", "Prerequisite"],
  ["Conditional Probability", "Prerequisite"],
  ["Bayes", "Current"],
  ["Random Variables", "Unlocks"],
  ["Expectation", "Unlocks"],
  ["Markov Chains", "Advanced"]
];

const reviews = [
  {
    source: "quantguide.io/questions",
    title: "Candidate question cluster",
    status: "Review",
    quality: "82%",
    similarity: "0.91",
    object: "Question",
    provenance: "source_url, extractor-v1.0"
  },
  {
    source: "tradinginterview.com",
    title: "Market making formula and example",
    status: "Approve",
    quality: "88%",
    similarity: "0.34",
    object: "Formula",
    provenance: "source_url, policy-check"
  },
  {
    source: "Green Book notes",
    title: "Bayes flashcards from manual notes",
    status: "Edit",
    quality: "76%",
    similarity: "0.52",
    object: "Flashcards",
    provenance: "book_note, generated_from"
  }
];

const pipelineSteps = [
  ["Topic job", "Conditional Probability"],
  ["Source scoring", "20-50 candidates ranked"],
  ["Structured extraction", "Concepts, formulas, questions"],
  ["Semantic dedupe", "pgvector duplicate clusters"],
  ["Human review", "Approve, edit, reject"],
  ["Publish", "Knowledge graph objects"]
];

let currentQuestion = 0;
let currentMental = 0;

const pageTitle = document.querySelector("#page-title");
const navItems = document.querySelectorAll(".nav-item");
const views = document.querySelectorAll(".view");

function showView(viewName) {
  views.forEach((view) => view.classList.toggle("active-view", view.id === viewName));
  navItems.forEach((item) => item.classList.toggle("active", item.dataset.view === viewName));
  pageTitle.textContent = navItemsByView(viewName);
}

function navItemsByView(viewName) {
  const labels = {
    dashboard: "Dashboard",
    topics: "Topics",
    paths: "Learning Paths",
    concept: "Concept Page",
    practice: "Practice",
    mental: "Mental Math",
    crawler: "Ingestion"
  };
  return labels[viewName] || "Dashboard";
}

navItems.forEach((item) => item.addEventListener("click", () => showView(item.dataset.view)));

document.querySelectorAll("[data-view-target]").forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.viewTarget));
});

function renderPlan() {
  document.querySelector("#study-plan").innerHTML = plan
    .map(
      ([title, detail, time]) => `
        <div class="queue-item">
          <div>
            <strong>${title}</strong>
            <span>${detail}</span>
          </div>
          <span class="pill">${time}</span>
        </div>
      `
    )
    .join("");
}

function renderTopics(filter = "") {
  const normalized = filter.trim().toLowerCase();
  const filtered = topics.filter((topic) => {
    const haystack = `${topic.name} ${topic.subtopics.join(" ")}`.toLowerCase();
    return haystack.includes(normalized);
  });

  document.querySelector("#topic-grid").innerHTML = filtered
    .map(
      (topic) => `
        <article class="topic-card">
          <strong>${topic.name}</strong>
          <span>${topic.count} items · ${topic.mastery}% mastery</span>
          <div class="bar"><i style="width: ${topic.mastery}%"></i></div>
          <div class="topic-meta">
            ${topic.subtopics.map((tag) => `<span class="pill">${tag}</span>`).join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function renderPaths() {
  document.querySelector("#path-list").innerHTML = paths
    .map(
      (path) => `
        <article class="path-card">
          <div>
            <strong>${path.name}</strong>
            <span>${path.level}</span>
          </div>
          <div class="path-steps">
            ${path.steps.map((step) => `<span>${step}</span>`).join("<i></i>")}
          </div>
        </article>
      `
    )
    .join("");
}

function renderConceptGraph() {
  document.querySelector("#concept-graph").innerHTML = conceptGraph
    .map(
      ([name, relation], index) => `
        <div class="graph-node ${name === "Bayes" ? "current-node" : ""}">
          <strong>${name}</strong>
          <span>${relation}</span>
        </div>
        ${index < conceptGraph.length - 1 ? '<div class="graph-edge"></div>' : ""}
      `
    )
    .join("");
}

function renderQuestion() {
  const question = questions[currentQuestion];
  document.querySelector("#question-title").textContent = question.title;
  document.querySelector("#question-body").textContent = question.body;
  document.querySelector(".practice-card .pill").textContent = question.tag;
  document.querySelector("#answer").value = "";
  document.querySelector("#feedback").textContent =
    "Submit an answer to get a step-by-step explanation, a mistake diagnosis, and a follow-up variant.";
  document.querySelector("#question-metadata").innerHTML = Object.entries(question.metadata)
    .map(([label, value]) => `<div><span>${formatLabel(label)}</span><strong>${value}</strong></div>`)
    .join("");
}

function formatLabel(label) {
  return label.replace(/([A-Z])/g, " $1").replace(/^./, (char) => char.toUpperCase());
}

function gradeAnswer() {
  const userAnswer = document.querySelector("#answer").value.trim();
  const question = questions[currentQuestion];
  const feedback = userAnswer
    ? `Good start. The clean solution is: ${question.answer} The likely grading focus is ${question.metadata.mistakes.toLowerCase()}.`
    : `Try writing the setup first. Hint: ${question.metadata.prerequisites} is the prerequisite to use here.`;
  document.querySelector("#feedback").textContent = feedback;
}

function renderMental() {
  document.querySelector("#mental-prompt").textContent = mental[currentMental].prompt;
  document.querySelector("#mental-answer").value = "";
  document.querySelector("#mental-feedback").textContent = "Type an answer and check instantly.";
  document.querySelector("#mental-list").innerHTML = mental
    .map(
      (item, index) => `
        <div class="mini-row">
          <span>${item.category}</span>
          <strong>${index === currentMental ? "Now" : item.prompt}</strong>
        </div>
      `
    )
    .join("");
}

function checkMental() {
  const guess = document.querySelector("#mental-answer").value.trim();
  const correct = mental[currentMental].answer;
  const result = guess === correct ? "Correct. Nice and clean." : `Expected ${correct}. Try the next one.`;
  document.querySelector("#mental-feedback").textContent = result;
  currentMental = (currentMental + 1) % mental.length;
  setTimeout(renderMental, 800);
}

function renderReviews() {
  document.querySelector("#review-list").innerHTML = reviews
    .map(
      (item) => `
        <div class="review-item">
          <div>
            <strong>${item.title}</strong>
            <span>${item.object} · ${item.source} · provenance: ${item.provenance}</span>
            <div class="review-meta">
              <span>Quality ${item.quality}</span>
              <span>Similarity ${item.similarity}</span>
            </div>
          </div>
          <span class="pill">${item.status}</span>
        </div>
      `
    )
    .join("");
}

function renderPipelineSteps() {
  document.querySelector("#pipeline-steps").innerHTML = pipelineSteps
    .map(
      ([title, detail]) => `
        <div>
          <strong>${title}</strong>
          <span>${detail}</span>
        </div>
      `
    )
    .join("");
}

document.querySelector("#grade-answer").addEventListener("click", gradeAnswer);
document.querySelector("#next-question").addEventListener("click", () => {
  currentQuestion = (currentQuestion + 1) % questions.length;
  renderQuestion();
});
document.querySelector("#check-mental").addEventListener("click", checkMental);
document.querySelector("#mental-answer").addEventListener("keydown", (event) => {
  if (event.key === "Enter") checkMental();
});
document.querySelector("#search").addEventListener("input", (event) => {
  renderTopics(event.target.value);
  if (event.target.value.trim()) showView("topics");
});

renderPlan();
renderTopics();
renderPaths();
renderConceptGraph();
renderQuestion();
renderMental();
renderReviews();
renderPipelineSteps();
