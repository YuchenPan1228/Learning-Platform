import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { fetchStudyPlan } from "@/lib/api/study-plan";
import type { DailyStudyPlan } from "@/lib/types/dashboard";

export async function AppShell({ children }: { children: React.ReactNode }) {
  let dailyPlan: DailyStudyPlan | null = null;
  try {
    dailyPlan = await fetchStudyPlan();
  } catch {
    dailyPlan = null;
  }

  return (
    <div className="grid min-h-screen bg-[#f6f7f4] lg:grid-cols-[280px_minmax(0,1fr)]">
      <Sidebar dailyPlan={dailyPlan} />
      <main className="min-w-0 p-5 sm:p-7">
        <Topbar />
        {children}
      </main>
    </div>
  );
}
