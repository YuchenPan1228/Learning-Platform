"use client";

import { useMemo, useState } from "react";

import { CategoryFilter, buildCategoryCounts } from "@/components/mental-math/category-filter";
import { buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { recordAttempt } from "@/lib/api/attempts";
import type { QuestionDetail } from "@/lib/types/question";
import type { TopicRead } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type MentalMathDrillProps = {
  categories: TopicRead[];
  questions: QuestionDetail[];
};

export function MentalMathDrill({ categories, questions }: MentalMathDrillProps) {
  const [promptStartedAt, setPromptStartedAt] = useState(() => Date.now());
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [queueIndex, setQueueIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [checkError, setCheckError] = useState<string | null>(null);

  const categoryCounts = useMemo(() => buildCategoryCounts(questions), [questions]);

  const filteredQuestions = useMemo(() => {
    if (selectedCategory === "all") {
      return questions;
    }
    return questions.filter((question) => question.subtopic_slug === selectedCategory);
  }, [questions, selectedCategory]);

  const currentQuestion =
    filteredQuestions.length > 0 ? filteredQuestions[queueIndex % filteredQuestions.length] : null;

  function resetPromptState() {
    setAnswer("");
    setFeedback(null);
    setIsCorrect(null);
    setCheckError(null);
    setPromptStartedAt(Date.now());
  }

  function handleCategorySelect(slug: string) {
    setSelectedCategory(slug);
    setQueueIndex(0);
    resetPromptState();
  }

  async function handleCheck() {
    if (currentQuestion === null) {
      return;
    }

    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer) {
      setCheckError("Type an answer before checking.");
      return;
    }

    setIsChecking(true);
    setCheckError(null);

    try {
      const timeSpentSeconds = Math.max(1, Math.round((Date.now() - promptStartedAt) / 1000));
      const result = await recordAttempt({
        questionId: currentQuestion.id,
        answer: trimmedAnswer,
        timeSpentSeconds,
      });
      setFeedback(result.feedback ?? "Attempt recorded.");
      setIsCorrect(result.is_correct);
    } catch {
      setCheckError("Check is unavailable. Verify the API is running.");
      setFeedback(null);
      setIsCorrect(null);
    } finally {
      setIsChecking(false);
    }
  }

  function handleNextPrompt() {
    if (filteredQuestions.length === 0) {
      return;
    }
    setQueueIndex((index) => (index + 1) % filteredQuestions.length);
    resetPromptState();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(280px,0.8fr)]">
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Practice drill</p>
          <h2 className="text-2xl font-semibold text-[#15201c]">Mental math prompt</h2>
          {currentQuestion ? (
            <p className="mt-1 text-sm text-[#66736e]">
              Prompt {(queueIndex % filteredQuestions.length) + 1} of {filteredQuestions.length}
              {currentQuestion.subtopic_slug ? ` · ${currentQuestion.subtopic_slug}` : ""}
            </p>
          ) : null}
        </div>

        {currentQuestion ? (
          <>
            <p className="text-xl font-medium text-[#15201c]">{currentQuestion.body}</p>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <Input
                type="text"
                inputMode="decimal"
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="Answer"
                aria-label="Mental math answer"
                className="h-11"
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    if (feedback) {
                      handleNextPrompt();
                    } else {
                      void handleCheck();
                    }
                  }
                }}
              />
              <button
                type="button"
                onClick={handleCheck}
                disabled={isChecking}
                className={cn(
                  buttonVariants(),
                  "h-11 shrink-0 disabled:cursor-not-allowed disabled:opacity-50",
                )}
              >
                {isChecking ? "Checking…" : "Check"}
              </button>
            </div>

            {checkError ? <p className="mt-3 text-sm text-[#b42318]">{checkError}</p> : null}

            {feedback ? (
              <p
                className={cn(
                  "mt-3 text-sm leading-relaxed",
                  isCorrect ? "text-[#176b54]" : "text-[#66736e]",
                )}
              >
                {feedback}
              </p>
            ) : (
              <p className="mt-3 text-sm text-[#66736e]">Type an answer and check instantly.</p>
            )}

            {feedback ? (
              <button
                type="button"
                onClick={handleNextPrompt}
                className={cn(buttonVariants({ variant: "outline" }), "mt-4")}
              >
                Next prompt
              </button>
            ) : null}
          </>
        ) : (
          <p className="text-sm text-[#66736e]">
            No prompts match this category. Choose another filter to continue drilling.
          </p>
        )}
      </section>

      <CategoryFilter
        categories={categories}
        selectedSlug={selectedCategory}
        questionCounts={categoryCounts}
        onSelect={handleCategorySelect}
      />
    </div>
  );
}
