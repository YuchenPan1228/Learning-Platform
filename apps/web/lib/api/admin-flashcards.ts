import { getApiBaseUrl } from "@/lib/api/config";
import type { Difficulty } from "@/lib/types/question";
import type { Flashcard } from "@/lib/types/flashcard";

type FlashcardListResponse = {
  items: Flashcard[];
};

export type FlashcardUpdateInput = {
  front?: string;
  back?: string;
  topicSlug?: string;
  difficulty?: Difficulty | null;
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

export async function fetchAdminFlashcards(options?: { topicSlug?: string }): Promise<Flashcard[]> {
  const params = new URLSearchParams();
  if (options?.topicSlug) {
    params.set("topic_slug", options.topicSlug);
  }
  const query = params.toString();
  const response = await fetch(`${getApiBaseUrl()}/admin/flashcards${query ? `?${query}` : ""}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Admin flashcards request failed with status ${response.status}`),
    );
  }

  const payload = (await response.json()) as FlashcardListResponse;
  return payload.items;
}

export async function fetchAdminFlashcard(flashcardId: number): Promise<Flashcard> {
  const response = await fetch(`${getApiBaseUrl()}/admin/flashcards/${flashcardId}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Admin flashcard request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<Flashcard>;
}

export async function updateAdminFlashcard(
  flashcardId: number,
  input: FlashcardUpdateInput,
): Promise<Flashcard> {
  const response = await fetch(`${getApiBaseUrl()}/admin/flashcards/${flashcardId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      front: input.front,
      back: input.back,
      topic_slug: input.topicSlug,
      difficulty: input.difficulty,
    }),
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Flashcard update failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<Flashcard>;
}

export async function deleteAdminFlashcard(flashcardId: number): Promise<{ deleted_id: number }> {
  const response = await fetch(`${getApiBaseUrl()}/admin/flashcards/${flashcardId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Flashcard delete failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<{ deleted_id: number }>;
}
