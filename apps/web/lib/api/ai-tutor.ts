import { getApiBaseUrl } from "@/lib/api/config";
import type {
  AIExplanationResult,
  AIHintsResult,
  SimilarQuestionResult,
} from "@/lib/types/ai-tutor";

export async function requestHints(questionId: number, answer: string): Promise<AIHintsResult> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/hints`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ answer }),
  });

  if (!response.ok) {
    throw new Error(`Hints request failed with status ${response.status}`);
  }

  return response.json() as Promise<AIHintsResult>;
}

export async function requestExplanation(
  questionId: number,
  answer: string,
): Promise<AIExplanationResult> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/explanation`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ answer }),
  });

  if (!response.ok) {
    throw new Error(`Explanation request failed with status ${response.status}`);
  }

  return response.json() as Promise<AIExplanationResult>;
}

export async function requestSimilarQuestion(questionId: number): Promise<SimilarQuestionResult> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/similar`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`Similar question request failed with status ${response.status}`);
  }

  return response.json() as Promise<SimilarQuestionResult>;
}
