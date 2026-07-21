import { getApiBaseUrl } from "@/lib/api/config";
import type { DailyStudyPlan } from "@/lib/types/dashboard";

export async function fetchStudyPlan(): Promise<DailyStudyPlan> {
  const response = await fetch(`${getApiBaseUrl()}/study-plan`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Study plan request failed with status ${response.status}`);
  }

  return response.json() as Promise<DailyStudyPlan>;
}
