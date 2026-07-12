import { getApiBaseUrl } from "@/lib/api/config";
import type { QuestionProgressStatus } from "@/lib/types/progress";

export type QuestionProgressItem = {
  question_id: number;
  status: QuestionProgressStatus;
  attempt_count: number;
};

export async function fetchQuestionProgress(): Promise<QuestionProgressItem[]> {
  const response = await fetch(`${getApiBaseUrl()}/attempts/progress`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Progress request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as { items: QuestionProgressItem[] };
  return payload.items;
}
