type DailyPlanItem = {
  title: string;
  description: string;
  duration: string;
};

const PLACEHOLDER_PLAN: DailyPlanItem[] = [
  {
    title: "Conditional Probability",
    description: "Prerequisite repair before Bayes questions",
    duration: "20 min",
  },
  {
    title: "Bayes",
    description: "8 interview-style questions with base rates",
    duration: "28 min",
  },
  {
    title: "Mental Math",
    description: "10 drills across logs, powers, fractions, estimates",
    duration: "12 min",
  },
  {
    title: "Coding Patterns",
    description: "3 binary search and 2 prefix sum prompts",
    duration: "20 min",
  },
  {
    title: "Finance",
    description: "Greeks intuition and one market-making scenario",
    duration: "10 min",
  },
];

export function DailyPlanPlaceholder() {
  return (
    <section
      aria-label="Daily study plan"
      className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Study planner</p>
          <h2 className="text-xl font-semibold text-[#15201c]">Today&apos;s queue</h2>
        </div>
        <span className="rounded-full border border-[#dfe6e1] px-2.5 py-1 text-xs font-semibold text-[#66736e]">
          Placeholder
        </span>
      </div>

      <p className="mb-4 text-sm leading-relaxed text-[#66736e]">
        Deterministic daily planning arrives in Phase 3B. This queue mirrors the approved dashboard
        wireframe until attempt data drives scheduling.
      </p>

      <ol className="grid gap-3">
        {PLACEHOLDER_PLAN.map((item) => (
          <li
            key={item.title}
            className="flex items-start justify-between gap-4 rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-4 py-3"
          >
            <div>
              <strong className="block text-sm text-[#15201c]">{item.title}</strong>
              <span className="mt-1 block text-sm text-[#66736e]">{item.description}</span>
            </div>
            <span className="shrink-0 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              {item.duration}
            </span>
          </li>
        ))}
      </ol>
    </section>
  );
}

export const dailyPlanSummary = "90 min plan";

export const dailyPlanDetail = "15 probability, 10 mental math, 5 finance, 2 market games.";
