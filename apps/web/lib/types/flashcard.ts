import type { Difficulty } from "@/lib/types/question";

export type Flashcard = {
  id: number;
  front: string;
  back: string;
  topic_id: number;
  topic_slug: string;
  difficulty: Difficulty | null;
};

export type FlashcardReviewRating = "again" | "good" | "easy";

export type FlashcardReviewEvent = {
  flashcard_id: number;
  rating: FlashcardReviewRating;
  reviewed_at: string;
};
