import { getApiBaseUrl } from "@/lib/api/config";
import type { SearchResponse } from "@/lib/types/search";

export async function searchContent(
  query: string,
  limit = 12,
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  });

  const response = await fetch(`${getApiBaseUrl()}/search?${params.toString()}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Search request failed with status ${response.status}`);
  }

  return response.json() as Promise<SearchResponse>;
}
