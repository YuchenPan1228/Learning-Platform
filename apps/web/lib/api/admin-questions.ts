import { getApiBaseUrl } from "@/lib/api/config";
import type { Difficulty, QuestionDetail, QuestionSummary } from "@/lib/types/question";

type QuestionListResponse = {
  items: QuestionSummary[];
};

export type QuestionUpdateInput = {
  title?: string;
  body?: string;
  canonicalSolution?: string | null;
  shortAnswer?: string | null;
  difficulty?: Difficulty;
  estimatedTimeSeconds?: number | null;
  topicSlug?: string;
  subtopicSlug?: string | null;
  companyHint?: string | null;
  expectedSolutionPattern?: string | null;
  commonMistakes?: string[] | null;
  prerequisites?: string[] | null;
  sourceAttribution?: string | null;
  status?: "draft" | "approved" | "rejected";
};

async function parseError(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Keep fallback when body is not JSON.
  }
  return fallback;
}

export async function fetchAdminQuestions(options?: {
  topicSlug?: string;
  status?: "draft" | "approved" | "rejected";
}): Promise<QuestionSummary[]> {
  const params = new URLSearchParams();
  if (options?.topicSlug) {
    params.set("topic_slug", options.topicSlug);
  }
  if (options?.status) {
    params.set("status", options.status);
  }
  const query = params.toString();
  const response = await fetch(`${getApiBaseUrl()}/admin/questions${query ? `?${query}` : ""}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Admin questions request failed with status ${response.status}`),
    );
  }

  const payload = (await response.json()) as QuestionListResponse;
  return payload.items;
}

export async function fetchAdminQuestion(questionId: number): Promise<QuestionDetail> {
  const response = await fetch(`${getApiBaseUrl()}/admin/questions/${questionId}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Admin question request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<QuestionDetail>;
}

export async function updateAdminQuestion(
  questionId: number,
  input: QuestionUpdateInput,
): Promise<QuestionDetail> {
  const response = await fetch(`${getApiBaseUrl()}/admin/questions/${questionId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title: input.title,
      body: input.body,
      canonical_solution: input.canonicalSolution,
      short_answer: input.shortAnswer,
      difficulty: input.difficulty,
      estimated_time_seconds: input.estimatedTimeSeconds,
      topic_slug: input.topicSlug,
      subtopic_slug: input.subtopicSlug,
      company_hint: input.companyHint,
      expected_solution_pattern: input.expectedSolutionPattern,
      common_mistakes: input.commonMistakes,
      prerequisites: input.prerequisites,
      source_attribution: input.sourceAttribution,
      status: input.status,
    }),
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Question update failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<QuestionDetail>;
}

export async function deleteAdminQuestion(questionId: number): Promise<{ deleted_id: number }> {
  const response = await fetch(`${getApiBaseUrl()}/admin/questions/${questionId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Question delete failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<{ deleted_id: number }>;
}
