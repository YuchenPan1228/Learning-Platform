import { getApiBaseUrl } from "@/lib/api/config";
import type { ConceptDetail, ConceptSummary } from "@/lib/types/concept";

type ConceptListResponse = {
  items: ConceptSummary[];
};

export type ConceptUpdateInput = {
  name?: string;
  slug?: string;
  definition?: string | null;
  formula?: string | null;
  intuition?: string | null;
  workedExample?: string | null;
  commonMistakes?: string | null;
  interviewTips?: string | null;
  prerequisites?: string | null;
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

export async function fetchAdminConcepts(topicSlug?: string): Promise<ConceptSummary[]> {
  const params = new URLSearchParams();
  if (topicSlug) {
    params.set("topic_slug", topicSlug);
  }
  const query = params.toString();
  const response = await fetch(`${getApiBaseUrl()}/admin/concepts${query ? `?${query}` : ""}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Admin concepts request failed with status ${response.status}`),
    );
  }

  const payload = (await response.json()) as ConceptListResponse;
  return payload.items;
}

export async function fetchAdminConcept(slug: string): Promise<ConceptDetail> {
  const response = await fetch(`${getApiBaseUrl()}/admin/concepts/${encodeURIComponent(slug)}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Admin concept request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<ConceptDetail>;
}

export async function updateAdminConcept(
  slug: string,
  input: ConceptUpdateInput,
): Promise<ConceptDetail> {
  const response = await fetch(`${getApiBaseUrl()}/admin/concepts/${encodeURIComponent(slug)}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: input.name,
      slug: input.slug,
      definition: input.definition,
      formula: input.formula,
      intuition: input.intuition,
      worked_example: input.workedExample,
      common_mistakes: input.commonMistakes,
      interview_tips: input.interviewTips,
      prerequisites: input.prerequisites,
    }),
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Concept update failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<ConceptDetail>;
}
