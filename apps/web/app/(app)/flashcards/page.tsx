import { FlashcardReview } from "@/components/flashcards/flashcard-review";
import { fetchFlashcards } from "@/lib/api/flashcards";

export default async function FlashcardsPage() {
  const flashcards = await fetchFlashcards({ limit: 100 });

  return <FlashcardReview flashcards={flashcards} />;
}
