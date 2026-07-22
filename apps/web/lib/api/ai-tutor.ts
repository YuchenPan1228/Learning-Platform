import { getApiBaseUrl } from "@/lib/api/config";
import type {
  AIExplanationResult,
  AIHintsResult,
  SimilarQuestionResult,
} from "@/lib/types/ai-tutor";

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
    throw new Error(await readApiError(response, "Explanation request failed"));
  }

  return response.json() as Promise<AIExplanationResult>;
}

export async function requestHints(
  questionId: number,
  answer: string = "",
): Promise<AIHintsResult> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/hints`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ answer }),
  });

  if (!response.ok) {
    throw new Error(await readApiError(response, "Hints request failed"));
  }

  return response.json() as Promise<AIHintsResult>;
}

export async function requestSimilarQuestion(questionId: number): Promise<SimilarQuestionResult> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/similar`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(await readApiError(response, "Similar question request failed"));
  }

  return response.json() as Promise<SimilarQuestionResult>;
}

async function readApiError(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string" && payload.detail.trim()) {
      return payload.detail;
    }
  } catch {
    // Ignore non-JSON error bodies.
  }
  return `${fallback} with status ${response.status}`;
}
