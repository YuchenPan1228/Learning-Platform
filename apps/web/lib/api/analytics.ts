import { getApiBaseUrl } from "@/lib/api/config";
import type { LearningAnalytics } from "@/lib/types/analytics";

export async function fetchAnalytics(): Promise<LearningAnalytics> {
  const response = await fetch(`${getApiBaseUrl()}/analytics`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Analytics request failed with status ${response.status}`);
  }

  return response.json() as Promise<LearningAnalytics>;
}
