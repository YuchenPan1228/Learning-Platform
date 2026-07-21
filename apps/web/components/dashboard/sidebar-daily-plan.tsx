import type { DailyStudyPlan } from "@/lib/types/dashboard";

type SidebarDailyPlanProps = {
  dailyPlan: DailyStudyPlan | null;
};

export function SidebarDailyPlan({ dailyPlan }: SidebarDailyPlanProps) {
  const summary = dailyPlan?.summary ?? "Plan unavailable";
  const detail = dailyPlan?.detail ?? "Start the API to load today's deterministic study plan.";

  return (
    <div className="mt-auto rounded-lg border border-[#dfe6e1] bg-white p-4">
      <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">Today</span>
      <strong className="mt-1 block text-sm text-[#15201c]">{summary}</strong>
      <p className="mt-2 text-sm leading-relaxed text-[#66736e]">{detail}</p>
    </div>
  );
}
