import { getApiBaseUrl } from "@/lib/api/config";
import type { Tag } from "@/lib/types/question";

export async function fetchTags(): Promise<Tag[]> {
  const response = await fetch(`${getApiBaseUrl()}/tags`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Tags request failed with status ${response.status}`);
  }

  return response.json() as Promise<Tag[]>;
}
