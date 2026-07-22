import Link from "next/link";

import type { DailyStudyPlan } from "@/lib/types/dashboard";

type SidebarDailyPlanProps = {
  dailyPlan: DailyStudyPlan | null;
};

export function SidebarDailyPlan({ dailyPlan }: SidebarDailyPlanProps) {
  const summary = dailyPlan?.summary ?? "Plan unavailable";
  const detail = dailyPlan?.detail ?? "Start the API to load today's deterministic study plan.";
  const firstItem = dailyPlan?.items[0];

  return (
    <Link
      href="/"
      aria-label="Open today's study queue"
      className="mt-auto block rounded-lg border border-[#dfe6e1] bg-white p-4 transition-colors hover:border-[#bdd3ca] hover:bg-[#edf5f1] focus-visible:border-[#0f766e] focus-visible:ring-3 focus-visible:ring-[#0f766e]/20"
    >
      <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">Today</span>
      <strong className="mt-1 block text-sm text-[#15201c]">{summary}</strong>
      <p className="mt-2 text-sm leading-relaxed text-[#66736e]">{detail}</p>
      {firstItem ? (
        <p className="mt-3 text-sm font-semibold text-[#176b54]">
          Next: {firstItem.title}
          <span className="mt-0.5 block font-normal text-[#66736e]">Open today&apos;s queue →</span>
        </p>
      ) : (
        <p className="mt-3 text-sm font-semibold text-[#176b54]">Open today&apos;s queue →</p>
      )}
    </Link>
  );
}
