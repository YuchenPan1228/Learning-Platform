import Link from "next/link";

import type { DailyStudyPlan } from "@/lib/types/dashboard";

type DailyPlanProps = {
  plan: DailyStudyPlan;
};

export function DailyPlan({ plan }: DailyPlanProps) {
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
          {plan.summary}
        </span>
      </div>

      <p className="mb-4 text-sm leading-relaxed text-[#66736e]">{plan.detail}</p>

      {plan.items.length === 0 ? (
        <p className="rounded-lg border border-dashed border-[#dfe6e1] bg-[#fbfcfa] px-4 py-6 text-sm text-[#66736e]">
          No study items scheduled yet. Attempt questions or review flashcards to build a plan.
        </p>
      ) : (
        <ol className="grid gap-3">
          {plan.items.map((item) => (
            <li
              key={`${item.kind}-${item.title}-${item.href ?? item.topic_slug ?? item.concept_slug}`}
              className="flex items-start justify-between gap-4 rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-4 py-3"
            >
              <div>
                {item.href ? (
                  <Link
                    href={item.href}
                    className="block text-sm font-semibold text-[#176b54] hover:underline"
                  >
                    {item.title}
                  </Link>
                ) : (
                  <strong className="block text-sm text-[#15201c]">{item.title}</strong>
                )}
                <span className="mt-1 block text-sm text-[#66736e]">{item.description}</span>
              </div>
              <span className="shrink-0 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                {item.duration_minutes} min
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
