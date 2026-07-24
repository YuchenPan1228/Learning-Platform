import { getApiBaseUrl } from "@/lib/api/config";
import type {
  Difficulty,
  QuestionDetail,
  QuestionProgressStatus,
  QuestionSummary,
} from "@/lib/types/question";

export type QuestionProgress = {
  question_id: number;
  status: QuestionProgressStatus;
  attempt_count: number;
  manually_marked: boolean;
};

export type QuestionListFilters = {
  topicSlug?: string;
  conceptSlug?: string;
  tagSlug?: string;
  difficulty?: Difficulty;
  includeProgress?: boolean;
  limit?: number;
  offset?: number;
};

export type QuestionListPage = {
  items: QuestionSummary[];
  total: number;
  limit: number;
  offset: number;
};

export async function fetchQuestionsPage(
  filters: QuestionListFilters = {},
): Promise<QuestionListPage> {
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
  if (filters.includeProgress) {
    params.set("include_progress", "true");
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

  return response.json() as Promise<QuestionListPage>;
}

export async function fetchQuestions(
  filters: QuestionListFilters = {},
): Promise<QuestionSummary[]> {
  const page = await fetchQuestionsPage(filters);
  return page.items;
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

export async function fetchQuestionProgress(questionId: number): Promise<QuestionProgress> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/progress`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Question progress request failed with status ${response.status}`);
  }

  return response.json() as Promise<QuestionProgress>;
}

export async function setQuestionProgress(
  questionId: number,
  status: "solved" | "not_attempted",
): Promise<QuestionProgress> {
  const response = await fetch(`${getApiBaseUrl()}/questions/${questionId}/progress`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });

  if (!response.ok) {
    throw new Error(`Set question progress failed with status ${response.status}`);
  }

  return response.json() as Promise<QuestionProgress>;
}
