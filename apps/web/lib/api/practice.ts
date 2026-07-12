import { getApiBaseUrl } from "@/lib/api/config";
import type { SelfCheckResult } from "@/lib/types/question";

export async function submitSelfCheck(
  questionId: number,
  answer: string,
): Promise<SelfCheckResult> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/self-check`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ answer }),
  });

  if (!response.ok) {
    throw new Error(`Self-check request failed with status ${response.status}`);
  }

  return response.json() as Promise<SelfCheckResult>;
}
