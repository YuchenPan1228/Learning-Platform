"use client";

import { useMemo, useState } from "react";

import { FlipCard } from "@/components/flashcards/flip-card";
import { FlashcardTopicFilter } from "@/components/flashcards/flashcard-topic-filter";
import { buttonVariants } from "@/components/ui/button";
import { reviewFlashcard } from "@/lib/api/flashcards";
import type { Flashcard, FlashcardReviewRating } from "@/lib/types/flashcard";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type FlashcardReviewProps = {
  flashcards: Flashcard[];
  topics: TopicWithSubtopics[];
  topicSlug?: string;
  topicTitle?: string | null;
  usedDueFallback?: boolean;
};

const RATING_OPTIONS: Array<{
  rating: FlashcardReviewRating;
  label: string;
  hint: string;
}> = [
  { rating: "again", label: "Again", hint: "~10 min" },
  { rating: "good", label: "Good", hint: "~1–3 days" },
  { rating: "easy", label: "Easy", hint: "longer" },
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

export function FlashcardReview({
  flashcards,
  topics,
  topicSlug,
  topicTitle,
  usedDueFallback = false,
}: FlashcardReviewProps) {
  const [order, setOrder] = useState<number[]>(() => flashcards.map((card) => card.id));
  const [index, setIndex] = useState(0);
  const [cardsById, setCardsById] = useState<Record<number, Flashcard>>(() =>
    Object.fromEntries(flashcards.map((card) => [card.id, card])),
  );
  const [isFlipped, setIsFlipped] = useState(false);
  const [sessionCount, setSessionCount] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastNextReviewAt, setLastNextReviewAt] = useState<string | null>(null);

  const currentCard = order.length > 0 ? cardsById[order[index]] : undefined;
  const dueCount = useMemo(
    () => Object.values(cardsById).filter((card) => card.is_due !== false).length,
    [cardsById],
  );
  const canGoPrev = index > 0;
  const canGoNext = index < order.length - 1;
  const atEnd = order.length > 0 && index >= order.length - 1;

  function resetFlip() {
    setIsFlipped(false);
  }

  function handleFlip() {
    setIsFlipped((flipped) => !flipped);
  }

  function goPrev() {
    if (!canGoPrev) {
      return;
    }
    setIndex((value) => value - 1);
    resetFlip();
    setError(null);
  }

  function goNext() {
    if (!canGoNext) {
      return;
    }
    setIndex((value) => value + 1);
    resetFlip();
    setError(null);
  }

  function handleSkip() {
    if (order.length === 0) {
      return;
    }
    const currentId = order[index];
    if (currentId === undefined) {
      return;
    }
    const remaining = [...order.slice(0, index), ...order.slice(index + 1)];
    if (remaining.length === 0) {
      setOrder([currentId]);
      setIndex(0);
      resetFlip();
      return;
    }
    const nextOrder = [...remaining, currentId];
    setOrder(nextOrder);
    // Stay on the same index so the next card slides into place.
    if (index >= nextOrder.length) {
      setIndex(nextOrder.length - 1);
    }
    resetFlip();
    setError(null);
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

      if (rating === "again") {
        const remaining = [...order.slice(0, index), ...order.slice(index + 1)];
        const nextOrder = [...remaining, currentCard.id];
        setOrder(nextOrder);
        if (index >= nextOrder.length) {
          setIndex(Math.max(0, nextOrder.length - 1));
        }
      } else if (canGoNext) {
        setIndex((value) => value + 1);
      }
      resetFlip();
    } catch {
      setError("Could not save review schedule. Check that the API is running.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleRestart() {
    setOrder(flashcards.map((card) => card.id));
    setCardsById(Object.fromEntries(flashcards.map((card) => [card.id, card])));
    setIndex(0);
    setIsFlipped(false);
    setSessionCount(0);
    setLastNextReviewAt(null);
    setError(null);
  }

  return (
    <div className="grid gap-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
            {topicSlug ? "Topic review" : "Flashcards"}
          </p>
          <h1 className="text-2xl font-semibold text-[#15201c]">
            {topicTitle ? `${topicTitle} flashcards` : "Review queue"}
          </h1>
          <p className="mt-1 text-sm text-[#66736e]">
            {flashcards.length === 0
              ? topicTitle
                ? `No flashcards found for ${topicTitle}.`
                : "No flashcards are available for review."
              : usedDueFallback
                ? "Nothing due right now — browsing the full set for this filter."
                : "Use Previous / Next to browse. Rate a card to schedule the next review."}
          </p>
        </div>
        <FlashcardTopicFilter topics={topics} selectedSlug={topicSlug} />
      </header>

      {flashcards.length === 0 ? (
        <section className="rounded-lg border border-dashed border-[#dfe6e1] bg-white p-8 text-center">
          <p className="text-sm text-[#66736e]">Pick another topic from the menu, or choose All topics.</p>
        </section>
      ) : null}

      {flashcards.length > 0 ? (

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(260px,0.8fr)]">
        <section className="grid gap-4">
          {currentCard ? (
            <>
              <div className="flex items-center justify-between gap-3 text-sm text-[#66736e]">
                <span>
                  Card {index + 1} of {order.length}
                </span>
                <span className="font-medium text-[#15201c]">{currentCard.topic_slug}</span>
              </div>

              <FlipCard flashcard={currentCard} isFlipped={isFlipped} onFlip={handleFlip} />

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={goPrev}
                  disabled={!canGoPrev || isSubmitting}
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "disabled:cursor-not-allowed disabled:opacity-50",
                  )}
                >
                  Previous
                </button>
                <button
                  type="button"
                  onClick={goNext}
                  disabled={!canGoNext || isSubmitting}
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "disabled:cursor-not-allowed disabled:opacity-50",
                  )}
                >
                  Next
                </button>
                <button
                  type="button"
                  onClick={handleSkip}
                  disabled={order.length <= 1 || isSubmitting}
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "disabled:cursor-not-allowed disabled:opacity-50",
                  )}
                >
                  Skip
                </button>
              </div>

              {isFlipped ? (
                <div className="grid gap-2">
                  <p className="text-sm text-[#66736e]">
                    Optional — rate to schedule when this card comes back.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {RATING_OPTIONS.map((option) => (
                      <button
                        key={option.rating}
                        type="button"
                        onClick={() => handleRating(option.rating)}
                        disabled={isSubmitting}
                        title={option.hint}
                        className={cn(
                          buttonVariants({
                            variant: option.rating === "again" ? "outline" : "default",
                          }),
                          "disabled:cursor-not-allowed disabled:opacity-50",
                        )}
                      >
                        {isSubmitting ? "Saving…" : `${option.label} · ${option.hint}`}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-[#66736e]">
                  Reveal the answer to rate, or move on with Next / Skip.
                </p>
              )}

              {atEnd && !canGoNext ? (
                <p className="text-sm text-[#66736e]">
                  You&apos;re on the last card. Rate it, Skip to recycle it, or restart the queue.
                </p>
              ) : null}

              {error ? <p className="text-sm text-[#b42318]">{error}</p> : null}
            </>
          ) : (
            <section className="rounded-lg border border-[#dfe6e1] bg-white p-6 text-center shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
              <h2 className="text-xl font-semibold text-[#15201c]">Review queue complete</h2>
              <p className="mt-2 text-sm text-[#66736e]">
                You rated {sessionCount} card{sessionCount === 1 ? "" : "s"} this session.
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
                Cards in deck
              </dt>
              <dd className="mt-1 font-medium text-[#15201c]">{order.length}</dd>
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
            Ratings schedule the next review (Again · Good · Easy). Browsing with Previous / Next /
            Skip does not change the schedule.
          </p>

          <button
            type="button"
            onClick={handleRestart}
            className={cn(buttonVariants({ variant: "outline" }), "mt-4 w-full")}
          >
            Restart queue
          </button>
        </aside>
      </div>
      ) : null}
    </div>
  );
}
