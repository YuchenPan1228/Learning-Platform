import type { Difficulty } from "@/lib/types/question";

export type FlashcardReviewRating = "again" | "good" | "easy";

export type Flashcard = {
  id: number;
  front: string;
  back: string;
  topic_id: number;
  topic_slug: string;
  difficulty: Difficulty | null;
  next_review_at?: string | null;
  interval_days?: number | null;
  ease_factor?: number | null;
  repetitions?: number | null;
  last_reviewed_at?: string | null;
  last_rating?: FlashcardReviewRating | null;
  is_due?: boolean;
};

export type FlashcardReviewResult = {
  flashcard: Flashcard;
  rating: FlashcardReviewRating;
  next_review_at: string;
  interval_days: number;
  ease_factor: number;
  repetitions: number;
};

export type FlashcardReviewEvent = {
  flashcard_id: number;
  rating: FlashcardReviewRating;
  reviewed_at: string;
};
