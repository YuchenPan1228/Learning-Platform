import { DashboardView } from "@/components/dashboard/dashboard-view";
import { fetchDashboard } from "@/lib/api/dashboard";

export default async function DashboardPage() {
  const dashboard = await fetchDashboard();

  return <DashboardView dashboard={dashboard} />;
}
