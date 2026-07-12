import { getApiBaseUrl } from "@/lib/api/config";
import type { Difficulty, QuestionDetail, QuestionSummary } from "@/lib/types/question";

export type QuestionListFilters = {
  topicSlug?: string;
  conceptSlug?: string;
  tagSlug?: string;
  difficulty?: Difficulty;
  limit?: number;
  offset?: number;
};

export async function fetchQuestions(
  filters: QuestionListFilters = {},
): Promise<QuestionSummary[]> {
  const params = new URLSearchParams();

  if (filters.topicSlug) {
    params.set("topic_slug", filters.topicSlug);
  }
  if (filters.conceptSlug) {
    params.set("concept_slug", filters.conceptSlug);
  }
  if (filters.tagSlug) {
    params.set("tag_slug", filters.tagSlug);
  }
  if (filters.difficulty) {
    params.set("difficulty", filters.difficulty);
  }
  params.set("limit", String(filters.limit ?? 100));
  if (filters.offset !== undefined) {
    params.set("offset", String(filters.offset));
  }

  const response = await fetch(`${getApiBaseUrl()}/questions?${params.toString()}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Questions request failed with status ${response.status}`);
  }

  return response.json() as Promise<QuestionSummary[]>;
}

export async function fetchQuestion(questionId: number): Promise<QuestionDetail | null> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}`, {
    cache: "no-store",
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Question request failed with status ${response.status}`);
  }

  return response.json() as Promise<QuestionDetail>;
}
