import { getApiBaseUrl } from "@/lib/api/config";
import type {
  Flashcard,
  FlashcardReviewRating,
  FlashcardReviewResult,
} from "@/lib/types/flashcard";

type FetchFlashcardsOptions = {
  topicSlug?: string;
  dueOnly?: boolean;
  limit?: number;
  offset?: number;
};

export async function fetchFlashcards(options: FetchFlashcardsOptions = {}): Promise<Flashcard[]> {
  const params = new URLSearchParams();
  params.set("limit", String(options.limit ?? 100));
  if (options.offset !== undefined) {
    params.set("offset", String(options.offset));
  }
  if (options.topicSlug) {
    params.set("topic_slug", options.topicSlug);
  }
  if (options.dueOnly) {
    params.set("due_only", "true");
  }

  const response = await fetch(`${getApiBaseUrl()}/flashcards?${params.toString()}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Flashcards request failed with status ${response.status}`);
  }

  return response.json() as Promise<Flashcard[]>;
}

export async function reviewFlashcard(
  flashcardId: number,
  rating: FlashcardReviewRating,
): Promise<FlashcardReviewResult> {
  const response = await fetch(`${getApiBaseUrl()}/flashcards/${flashcardId}/review`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ rating }),
  });

  if (!response.ok) {
    throw new Error(`Flashcard review failed with status ${response.status}`);
  }

  return response.json() as Promise<FlashcardReviewResult>;
}
