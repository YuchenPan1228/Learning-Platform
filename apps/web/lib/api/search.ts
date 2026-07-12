import { getApiBaseUrl } from "@/lib/api/config";
import type { ConceptSummary } from "@/lib/types/concept";
import type { QuestionSummary } from "@/lib/types/question";

export type SearchResponse = {
  query: string;
  questions: QuestionSummary[];
  concepts: ConceptSummary[];
  total: number;
};

export async function searchContent(query: string, limit = 12): Promise<SearchResponse> {
  const url = new URL(`${getApiBaseUrl()}/search`);
  url.searchParams.set("q", query);
  url.searchParams.append("types", "questions");
  url.searchParams.append("types", "concepts");
  url.searchParams.set("limit", String(limit));

  const response = await fetch(url.toString(), { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Search request failed with status ${response.status}`);
  }

  return response.json() as Promise<SearchResponse>;
}
