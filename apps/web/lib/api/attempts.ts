import { getApiBaseUrl } from "@/lib/api/config";
import type { AttemptResult } from "@/lib/types/attempt";

type RecordAttemptInput = {
  questionId: number;
  answer: string;
  timeSpentSeconds: number;
};

export async function recordAttempt(input: RecordAttemptInput): Promise<AttemptResult> {
  const response = await fetch(`${getApiBaseUrl()}/attempts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question_id: input.questionId,
      answer: input.answer,
      time_spent_seconds: input.timeSpentSeconds,
    }),
  });

  if (!response.ok) {
    throw new Error(`Attempt request failed with status ${response.status}`);
  }

  return response.json() as Promise<AttemptResult>;
}
