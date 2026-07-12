import { getApiBaseUrl } from "@/lib/api/config";
import type { DashboardData } from "@/lib/types/dashboard";

export async function fetchDashboard(): Promise<DashboardData> {
  const response = await fetch(`${getApiBaseUrl()}/dashboard`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Dashboard request failed with status ${response.status}`);
  }

  return response.json() as Promise<DashboardData>;
}
