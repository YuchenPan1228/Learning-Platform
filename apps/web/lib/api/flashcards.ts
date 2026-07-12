import { getApiBaseUrl } from "@/lib/api/config";
import type { Flashcard } from "@/lib/types/flashcard";

type FetchFlashcardsOptions = {
  topicSlug?: string;
  limit?: number;
};

export async function fetchFlashcards(options: FetchFlashcardsOptions = {}): Promise<Flashcard[]> {
  const params = new URLSearchParams();
  params.set("limit", String(options.limit ?? 100));
  if (options.topicSlug) {
    params.set("topic_slug", options.topicSlug);
  }

  const response = await fetch(`${getApiBaseUrl()}/flashcards?${params.toString()}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Flashcards request failed with status ${response.status}`);
  }

  return response.json() as Promise<Flashcard[]>;
}
