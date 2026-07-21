import { DailyPlan } from "@/components/dashboard/daily-plan";
import { MasteryCards } from "@/components/dashboard/mastery-cards";
import { WeakPrerequisitePanel } from "@/components/dashboard/weak-prerequisite-panel";
import type { DashboardData } from "@/lib/types/dashboard";

export function DashboardView({ dashboard }: { dashboard: DashboardData }) {
  return (
    <div className="grid gap-6">
      <MasteryCards topics={dashboard.topic_mastery} />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
        <DailyPlan plan={dashboard.daily_plan} />
        <WeakPrerequisitePanel weakPrerequisites={dashboard.weak_prerequisites} />
      </div>
    </div>
  );
}
