import { FlashcardReview } from "@/components/flashcards/flashcard-review";
import { fetchFlashcards } from "@/lib/api/flashcards";

export default async function FlashcardsPage() {
  const dueFlashcards = await fetchFlashcards({ limit: 100, dueOnly: true });
  const flashcards =
    dueFlashcards.length > 0 ? dueFlashcards : await fetchFlashcards({ limit: 100 });

  return <FlashcardReview flashcards={flashcards} />;
}
