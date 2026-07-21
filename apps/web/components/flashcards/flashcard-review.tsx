"use client";

import { useMemo, useState } from "react";

import { FlipCard } from "@/components/flashcards/flip-card";
import { buttonVariants } from "@/components/ui/button";
import { reviewFlashcard } from "@/lib/api/flashcards";
import type { Flashcard, FlashcardReviewRating } from "@/lib/types/flashcard";
import { cn } from "@/lib/utils";

type FlashcardReviewProps = {
  flashcards: Flashcard[];
};

const RATING_OPTIONS: Array<{ rating: FlashcardReviewRating; label: string }> = [
  { rating: "again", label: "Again" },
  { rating: "good", label: "Good" },
  { rating: "easy", label: "Easy" },
];

function formatNextReview(value: string | null | undefined): string {
  if (!value) {
    return "Not scheduled";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Not scheduled";
  }
  return date.toLocaleString();
}

export function FlashcardReview({ flashcards }: FlashcardReviewProps) {
  const [queue, setQueue] = useState<number[]>(() => flashcards.map((card) => card.id));
  const [cardsById, setCardsById] = useState<Record<number, Flashcard>>(() =>
    Object.fromEntries(flashcards.map((card) => [card.id, card])),
  );
  const [isFlipped, setIsFlipped] = useState(false);
  const [sessionCount, setSessionCount] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastNextReviewAt, setLastNextReviewAt] = useState<string | null>(null);

  const currentCard = queue.length > 0 ? cardsById[queue[0]] : undefined;
  const dueCount = useMemo(
    () => Object.values(cardsById).filter((card) => card.is_due !== false).length,
    [cardsById],
  );

  function handleFlip() {
    setIsFlipped((flipped) => !flipped);
  }

  async function handleRating(rating: FlashcardReviewRating) {
    if (currentCard === undefined || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const result = await reviewFlashcard(currentCard.id, rating);
      setCardsById((existing) => ({
        ...existing,
        [currentCard.id]: result.flashcard,
      }));
      setLastNextReviewAt(result.next_review_at);
      setSessionCount((count) => count + 1);

      const remaining = queue.slice(1);
      const nextQueue = rating === "again" ? [...remaining, currentCard.id] : remaining;
      setQueue(nextQueue);
      setIsFlipped(false);
    } catch {
      setError("Could not save review schedule. Check that the API is running.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleRestart() {
    setQueue(flashcards.map((card) => card.id));
    setCardsById(Object.fromEntries(flashcards.map((card) => [card.id, card])));
    setIsFlipped(false);
    setSessionCount(0);
    setLastNextReviewAt(null);
    setError(null);
  }

  if (flashcards.length === 0) {
    return (
      <section className="rounded-lg border border-dashed border-[#dfe6e1] bg-white p-8 text-center">
        <p className="text-sm text-[#66736e]">No flashcards are due for review.</p>
      </section>
    );
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(260px,0.8fr)]">
      <section className="grid gap-4">
        {currentCard ? (
          <>
            <FlipCard flashcard={currentCard} isFlipped={isFlipped} onFlip={handleFlip} />

            {isFlipped ? (
              <div className="flex flex-wrap gap-2">
                {RATING_OPTIONS.map((option) => (
                  <button
                    key={option.rating}
                    type="button"
                    onClick={() => handleRating(option.rating)}
                    disabled={isSubmitting}
                    className={cn(
                      buttonVariants({
                        variant: option.rating === "again" ? "outline" : "default",
                      }),
                      "disabled:cursor-not-allowed disabled:opacity-50",
                    )}
                  >
                    {isSubmitting ? "Saving…" : option.label}
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[#66736e]">Reveal the answer before rating the card.</p>
            )}
            {error ? <p className="text-sm text-[#b42318]">{error}</p> : null}
          </>
        ) : (
          <section className="rounded-lg border border-[#dfe6e1] bg-white p-6 text-center shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
            <h2 className="text-xl font-semibold text-[#15201c]">Review queue complete</h2>
            <p className="mt-2 text-sm text-[#66736e]">
              You reviewed {sessionCount} card{sessionCount === 1 ? "" : "s"} this session.
            </p>
            <button type="button" onClick={handleRestart} className={cn(buttonVariants(), "mt-4")}>
              Restart queue
            </button>
          </section>
        )}
      </section>

      <aside className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Review</p>
          <h2 className="text-lg font-semibold text-[#15201c]">Spaced repetition</h2>
        </div>

        <dl className="grid gap-3 text-sm">
          <div>
            <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Cards in queue
            </dt>
            <dd className="mt-1 font-medium text-[#15201c]">{queue.length}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Due in loaded set
            </dt>
            <dd className="mt-1 font-medium text-[#15201c]">{dueCount}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Rated this session
            </dt>
            <dd className="mt-1 font-medium text-[#15201c]">{sessionCount}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Last next review
            </dt>
            <dd className="mt-1 font-medium text-[#15201c]">
              {formatNextReview(lastNextReviewAt)}
            </dd>
          </div>
        </dl>

        <p className="mt-4 text-sm leading-relaxed text-[#66736e]">
          Ratings update deterministic next-review dates on the server using again / good / easy
          intervals.
        </p>
      </aside>
    </div>
  );
}
