"use client";

import { useEffect, useMemo, useState } from "react";

import { buildCategoryCounts } from "@/components/mental-math/category-filter";
import { buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { recordAttempt } from "@/lib/api/attempts";
import type { QuestionDetail } from "@/lib/types/question";
import type { TopicRead } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type TimedMentalMathQuizProps = {
  categories: TopicRead[];
  questions: QuestionDetail[];
};

type CategoryResult = {
  slug: string;
  name: string;
  attempts: number;
  correct: number;
};

type QuizAttempt = {
  questionId: number;
  categorySlug: string | null;
  isCorrect: boolean;
};

const TIME_LIMIT_OPTIONS = [
  { label: "1 minute", seconds: 60 },
  { label: "2 minutes", seconds: 120 },
  { label: "5 minutes", seconds: 300 },
];

function shuffleQuestions(items: QuestionDetail[]): QuestionDetail[] {
  const copy = [...items];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
  }
  return copy;
}

function formatPercent(correct: number, attempts: number): string {
  if (attempts === 0) {
    return "0%";
  }
  return `${Math.round((correct / attempts) * 100)}%`;
}

export function TimedMentalMathQuiz({ categories, questions }: TimedMentalMathQuizProps) {
  const categoryCounts = useMemo(() => buildCategoryCounts(questions), [questions]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(() =>
    categories.map((category) => category.slug),
  );
  const [timeLimitSeconds, setTimeLimitSeconds] = useState(120);
  const [phase, setPhase] = useState<"setup" | "running" | "results">("setup");
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [queue, setQueue] = useState<QuestionDetail[]>([]);
  const [queueIndex, setQueueIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [promptStartedAt, setPromptStartedAt] = useState(() => Date.now());
  const [quizAttempts, setQuizAttempts] = useState<QuizAttempt[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const availableQuestions = useMemo(() => {
    if (selectedCategories.length === 0) {
      return [];
    }
    return questions.filter(
      (question) =>
        question.subtopic_slug !== null && selectedCategories.includes(question.subtopic_slug),
    );
  }, [questions, selectedCategories]);

  const currentQuestion =
    phase === "running" && queue.length > 0 ? queue[queueIndex % queue.length] : null;

  useEffect(() => {
    if (phase !== "running" || remainingSeconds <= 0) {
      return;
    }

    const timeout = window.setTimeout(() => {
      const next = remainingSeconds - 1;
      if (next <= 0) {
        setPhase("results");
        setRemainingSeconds(0);
      } else {
        setRemainingSeconds(next);
      }
    }, 1000);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [phase, remainingSeconds]);

  function toggleCategory(slug: string) {
    setSelectedCategories((current) =>
      current.includes(slug) ? current.filter((item) => item !== slug) : [...current, slug],
    );
  }

  function startQuiz() {
    if (availableQuestions.length === 0) {
      return;
    }
    setQueue(shuffleQuestions(availableQuestions));
    setQueueIndex(0);
    setQuizAttempts([]);
    setAnswer("");
    setPromptStartedAt(Date.now());
    setRemainingSeconds(timeLimitSeconds);
    setSubmitError(null);
    setPhase("running");
  }

  async function submitAnswer() {
    if (currentQuestion === null || phase !== "running") {
      return;
    }

    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer) {
      setSubmitError("Type an answer before submitting.");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const timeSpentSeconds = Math.max(1, Math.round((Date.now() - promptStartedAt) / 1000));
      const result = await recordAttempt({
        questionId: currentQuestion.id,
        answer: trimmedAnswer,
        timeSpentSeconds,
      });
      setQuizAttempts((attempts) => [
        ...attempts,
        {
          questionId: currentQuestion.id,
          categorySlug: currentQuestion.subtopic_slug,
          isCorrect: result.is_correct === true,
        },
      ]);
      setQueueIndex((index) => index + 1);
      setAnswer("");
      setPromptStartedAt(Date.now());
    } catch {
      setSubmitError("Could not record answer. Verify the API is running.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function endQuiz() {
    setPhase("results");
    setRemainingSeconds(0);
  }

  const categoryResults = useMemo(() => {
    const bySlug = new Map<string, CategoryResult>();
    for (const category of categories) {
      bySlug.set(category.slug, {
        slug: category.slug,
        name: category.name,
        attempts: 0,
        correct: 0,
      });
    }

    for (const attempt of quizAttempts) {
      if (attempt.categorySlug === null) {
        continue;
      }
      const existing = bySlug.get(attempt.categorySlug);
      if (existing === undefined) {
        continue;
      }
      existing.attempts += 1;
      if (attempt.isCorrect) {
        existing.correct += 1;
      }
    }

    return [...bySlug.values()].filter(
      (result) => selectedCategories.includes(result.slug) && result.attempts > 0,
    );
  }, [categories, quizAttempts, selectedCategories]);

  const totalAttempts = quizAttempts.length;
  const totalCorrect = quizAttempts.filter((attempt) => attempt.isCorrect).length;

  if (phase === "results") {
    return (
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Timed quiz</p>
          <h2 className="text-2xl font-semibold text-[#15201c]">Results</h2>
        </div>

        <dl className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-4 py-3">
            <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Questions attempted
            </dt>
            <dd className="mt-1 text-2xl font-semibold text-[#15201c]">{totalAttempts}</dd>
          </div>
          <div className="rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-4 py-3">
            <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Correct
            </dt>
            <dd className="mt-1 text-2xl font-semibold text-[#15201c]">{totalCorrect}</dd>
          </div>
          <div className="rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-4 py-3">
            <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Overall accuracy
            </dt>
            <dd className="mt-1 text-2xl font-semibold text-[#15201c]">
              {formatPercent(totalCorrect, totalAttempts)}
            </dd>
          </div>
        </dl>

        {categoryResults.length > 0 ? (
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-[#15201c]">By category</h3>
            <ul className="mt-3 grid gap-2">
              {categoryResults.map((result) => (
                <li
                  key={result.slug}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-4 py-3 text-sm"
                >
                  <span className="font-medium text-[#15201c]">{result.name}</span>
                  <span className="text-[#66736e]">
                    {result.attempts} attempted · {result.correct} correct ·{" "}
                    {formatPercent(result.correct, result.attempts)} accuracy
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="mt-4 text-sm text-[#66736e]">No answers were submitted during this quiz.</p>
        )}

        <button
          type="button"
          onClick={() => setPhase("setup")}
          className={cn(buttonVariants(), "mt-6")}
        >
          Start another quiz
        </button>
      </section>
    );
  }

  if (phase === "running" && currentQuestion) {
    return (
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Timed quiz</p>
            <h2 className="text-2xl font-semibold text-[#15201c]">Keep going</h2>
            <p className="mt-1 text-sm text-[#66736e]">
              {totalAttempts} attempted
              {currentQuestion.subtopic_slug ? ` · ${currentQuestion.subtopic_slug}` : ""}
            </p>
          </div>
          <div className="rounded-lg border border-[#bdd3ca] bg-[#edf5f1] px-4 py-2 text-center">
            <p className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Time left
            </p>
            <p className="text-2xl font-semibold text-[#176b54]">{remainingSeconds}s</p>
          </div>
        </div>

        <p className="text-xl font-medium text-[#15201c]">{currentQuestion.body}</p>

        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
          <Input
            type="text"
            inputMode="decimal"
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            placeholder="Answer"
            aria-label="Timed quiz answer"
            className="h-11"
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void submitAnswer();
              }
            }}
          />
          <button
            type="button"
            onClick={() => void submitAnswer()}
            disabled={isSubmitting}
            className={cn(
              buttonVariants(),
              "h-11 shrink-0 disabled:cursor-not-allowed disabled:opacity-50",
            )}
          >
            {isSubmitting ? "Submitting…" : "Submit"}
          </button>
        </div>

        {submitError ? <p className="mt-3 text-sm text-[#b42318]">{submitError}</p> : null}

        <button
          type="button"
          onClick={endQuiz}
          className={cn(buttonVariants({ variant: "outline" }), "mt-4")}
        >
          End quiz early
        </button>
      </section>
    );
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(280px,0.8fr)]">
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Timed quiz</p>
          <h2 className="text-2xl font-semibold text-[#15201c]">Configure quiz</h2>
          <p className="mt-1 text-sm text-[#66736e]">
            Select categories and a time limit. Submit answers quickly before time runs out.
          </p>
        </div>

        <label className="grid gap-2">
          <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
            Time limit
          </span>
          <select
            value={timeLimitSeconds}
            onChange={(event) => setTimeLimitSeconds(Number(event.target.value))}
            className="h-10 rounded-lg border border-[#dfe6e1] bg-white px-3 text-sm text-[#15201c] outline-none focus-visible:border-[#0f766e] focus-visible:ring-3 focus-visible:ring-[#0f766e]/20"
          >
            {TIME_LIMIT_OPTIONS.map((option) => (
              <option key={option.seconds} value={option.seconds}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          onClick={startQuiz}
          disabled={availableQuestions.length === 0}
          className={cn(buttonVariants(), "mt-5 disabled:cursor-not-allowed disabled:opacity-50")}
        >
          Start quiz
        </button>

        {availableQuestions.length === 0 ? (
          <p className="mt-3 text-sm text-[#66736e]">
            Select at least one category with available prompts.
          </p>
        ) : null}
      </section>

      <section className="rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Categories</p>
          <h2 className="text-lg font-semibold text-[#15201c]">Include in quiz</h2>
        </div>

        <ul className="grid gap-2">
          {categories.map((category) => (
            <li key={category.id}>
              <label className="flex cursor-pointer items-center justify-between rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-3 py-2 text-sm">
                <span className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedCategories.includes(category.slug)}
                    onChange={() => toggleCategory(category.slug)}
                    className="size-4 rounded border-[#dfe6e1]"
                  />
                  <span className="font-medium text-[#15201c]">{category.name}</span>
                </span>
                <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                  {categoryCounts[category.slug] ?? 0}
                </span>
              </label>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
