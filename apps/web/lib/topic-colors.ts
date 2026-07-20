export type TopicPalette = {
  slug: string;
  label: string;
  border: string;
  surface: string;
  hoverSurface: string;
  badge: string;
  badgeText: string;
  accent: string;
};

const ROOT_PALETTES: Record<string, TopicPalette> = {
  probability: {
    slug: "probability",
    label: "Probability",
    border: "border-[#c7d7f0]",
    surface: "bg-[#f5f8fe]",
    hoverSurface: "hover:bg-[#eef4fd]",
    badge: "bg-[#dbeafe]",
    badgeText: "text-[#1d4ed8]",
    accent: "border-l-[#3b82f6]",
  },
  mathematics: {
    slug: "mathematics",
    label: "Mathematics",
    border: "border-[#d8c7f0]",
    surface: "bg-[#f8f5fe]",
    hoverSurface: "hover:bg-[#f1ebfd]",
    badge: "bg-[#ede9fe]",
    badgeText: "text-[#6d28d9]",
    accent: "border-l-[#8b5cf6]",
  },
  statistics: {
    slug: "statistics",
    label: "Statistics",
    border: "border-[#c7e8f0]",
    surface: "bg-[#f2fbfe]",
    hoverSurface: "hover:bg-[#e8f7fd]",
    badge: "bg-[#cffafe]",
    badgeText: "text-[#0e7490]",
    accent: "border-l-[#06b6d4]",
  },
  finance: {
    slug: "finance",
    label: "Finance",
    border: "border-[#c7f0dd]",
    surface: "bg-[#f3fdf8]",
    hoverSurface: "hover:bg-[#eafaf2]",
    badge: "bg-[#d1fae5]",
    badgeText: "text-[#047857]",
    accent: "border-l-[#10b981]",
  },
  programming: {
    slug: "programming",
    label: "Programming",
    border: "border-[#f0d7c7]",
    surface: "bg-[#fff8f3]",
    hoverSurface: "hover:bg-[#fdf1e8]",
    badge: "bg-[#ffedd5]",
    badgeText: "text-[#c2410c]",
    accent: "border-l-[#f97316]",
  },
  "coding-patterns": {
    slug: "coding-patterns",
    label: "Coding Patterns",
    border: "border-[#f0c7d8]",
    surface: "bg-[#fff5f8]",
    hoverSurface: "hover:bg-[#fdeef3]",
    badge: "bg-[#fce7f3]",
    badgeText: "text-[#be185d]",
    accent: "border-l-[#ec4899]",
  },
  "mental-math": {
    slug: "mental-math",
    label: "Mental Math",
    border: "border-[#f0e3c7]",
    surface: "bg-[#fffdf5]",
    hoverSurface: "hover:bg-[#fdf8e8]",
    badge: "bg-[#fef3c7]",
    badgeText: "text-[#b45309]",
    accent: "border-l-[#f59e0b]",
  },
  "quant-research": {
    slug: "quant-research",
    label: "Quant Research",
    border: "border-[#d0d7e8]",
    surface: "bg-[#f6f8fc]",
    hoverSurface: "hover:bg-[#edf1f8]",
    badge: "bg-[#e2e8f0]",
    badgeText: "text-[#334155]",
    accent: "border-l-[#64748b]",
  },
  "other-sections": {
    slug: "other-sections",
    label: "Other Sections",
    border: "border-[#d9dfd6]",
    surface: "bg-[#f8faf7]",
    hoverSurface: "hover:bg-[#f1f5ef]",
    badge: "bg-[#ecf1ea]",
    badgeText: "text-[#3f5a46]",
    accent: "border-l-[#6b8f71]",
  },
};

const SUBTOPIC_ROOT_SLUG: Record<string, string> = {
  counting: "probability",
  independence: "probability",
  "conditional-probability": "probability",
  bayes: "probability",
  "random-variables": "probability",
  expectation: "probability",
  "conditional-expectation": "probability",
  variance: "probability",
  "continuous-distributions": "probability",
  "limit-theorems": "probability",
  "markov-chains": "probability",
  martingales: "probability",
  "vectors-matrices": "mathematics",
  "linear-systems": "mathematics",
  eigenvalues: "mathematics",
  orthogonality: "mathematics",
  "derivatives-gradients": "mathematics",
  "taylor-expansions": "mathematics",
  "math-optimization": "mathematics",
  "lagrange-multipliers": "mathematics",
  "differential-equations": "mathematics",
  estimation: "statistics",
  "confidence-intervals": "statistics",
  "hypothesis-testing": "statistics",
  "maximum-likelihood": "statistics",
  regression: "statistics",
  "bias-variance": "statistics",
  derivatives: "finance",
  "black-scholes": "finance",
  greeks: "finance",
  "portfolio-theory": "finance",
  capm: "finance",
  "fixed-income": "finance",
  "market-microstructure": "finance",
  python: "programming",
  cpp: "programming",
  sql: "programming",
  algorithms: "programming",
  "data-structures": "programming",
  "sliding-window": "coding-patterns",
  "binary-search": "coding-patterns",
  "prefix-sum": "coding-patterns",
  greedy: "coding-patterns",
  "dynamic-programming": "coding-patterns",
  "graph-traversal": "coding-patterns",
  intervals: "coding-patterns",
  "two-pointers": "coding-patterns",
  "quick-tricks": "mental-math",
  "addition-subtraction": "mental-math",
  "basic-multiplication": "mental-math",
  "intermediate-multiplication": "mental-math",
  "mental-division-fractions": "mental-math",
  guesstimation: "mental-math",
  "memorizing-numbers": "mental-math",
  "advanced-multiplication": "mental-math",
  "time-series": "quant-research",
  "stochastic-processes": "quant-research",
  "brownian-motion": "quant-research",
  "monte-carlo": "quant-research",
  "numerical-methods": "quant-research",
  "machine-learning-for-finance": "quant-research",
  "brain-teasers": "other-sections",
  "game-theory": "other-sections",
  "market-games": "other-sections",
  "behavioral-interview": "other-sections",
  "system-design": "other-sections",
};

const DEFAULT_PALETTE: TopicPalette = {
  slug: "general",
  label: "General",
  border: "border-[#dfe6e1]",
  surface: "bg-[#fbfcfa]",
  hoverSurface: "hover:bg-[#f6f8f5]",
  badge: "bg-[#edf5f1]",
  badgeText: "text-[#31443d]",
  accent: "border-l-[#94a3b8]",
};

export function formatTopicLabel(slug: string): string {
  return slug
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function resolveRootTopicSlug(slug: string): string {
  if (slug in ROOT_PALETTES) {
    return slug;
  }
  return SUBTOPIC_ROOT_SLUG[slug] ?? slug;
}

export function getTopicPalette(slug: string): TopicPalette {
  if (slug in ROOT_PALETTES) {
    return ROOT_PALETTES[slug];
  }

  const rootSlug = SUBTOPIC_ROOT_SLUG[slug];
  if (rootSlug && rootSlug in ROOT_PALETTES) {
    return ROOT_PALETTES[rootSlug];
  }

  return {
    ...DEFAULT_PALETTE,
    slug,
    label: formatTopicLabel(slug),
  };
}

export function getConceptPalette(conceptSlug: string, topicSlug: string): TopicPalette {
  return getTopicPalette(SUBTOPIC_ROOT_SLUG[conceptSlug] ?? topicSlug);
}
