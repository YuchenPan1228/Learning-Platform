import { getApiBaseUrl } from "@/lib/api/config";
import type { ConceptSummary } from "@/lib/types/concept";
import type { SearchResponse } from "@/lib/types/search";

type SearchConceptsOptions = {
  query: string;
  topicSlug?: string;
  limit?: number;
};

export async function searchConcepts({
  query,
  topicSlug,
  limit = 20,
}: SearchConceptsOptions): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    types: "concepts",
    limit: String(limit),
  });

  if (topicSlug) {
    params.set("topic_slug", topicSlug);
  }

  const response = await fetch(`${getApiBaseUrl()}/search?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Search request failed with status ${response.status}`);
  }

  return response.json() as Promise<SearchResponse>;
}

export async function fetchConcepts(topicSlug?: string): Promise<ConceptSummary[]> {
  const url = topicSlug
    ? `${getApiBaseUrl()}/concepts?topic_slug=${encodeURIComponent(topicSlug)}`
    : `${getApiBaseUrl()}/concepts`;

  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Concepts request failed with status ${response.status}`);
  }

  return response.json() as Promise<ConceptSummary[]>;
}
