import { dailyPlanDetail, dailyPlanSummary } from "@/components/dashboard/daily-plan-placeholder";

export function SidebarDailyPlan() {
  return (
    <div className="mt-auto rounded-lg border border-[#dfe6e1] bg-white p-4">
      <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">Today</span>
      <strong className="mt-1 block text-sm text-[#15201c]">{dailyPlanSummary}</strong>
      <p className="mt-2 text-sm leading-relaxed text-[#66736e]">{dailyPlanDetail}</p>
    </div>
  );
}
