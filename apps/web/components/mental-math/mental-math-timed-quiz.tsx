"use client";

import { useEffect, useMemo, useState } from "react";

import { buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { recordAttempt } from "@/lib/api/attempts";
import type { QuestionDetail } from "@/lib/types/question";
import type { TopicRead } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type MentalMathTimedQuizProps = {
  categories: TopicRead[];
  questions: QuestionDetail[];
  categoryCounts: Record<string, number>;
};

type QuizPhase = "setup" | "running" | "results";

type CategoryStat = {
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

const TIME_OPTIONS = [
  { label: "1 min", seconds: 60 },
  { label: "2 min", seconds: 120 },
  { label: "5 min", seconds: 300 },
];

function shuffleQuestions(questions: QuestionDetail[]): QuestionDetail[] {
  const copy = [...questions];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
  }
  return copy;
}

function formatSeconds(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export function MentalMathTimedQuiz({
  categories,
  questions,
  categoryCounts,
}: MentalMathTimedQuizProps) {
  const [phase, setPhase] = useState<QuizPhase>("setup");
  const [selectedCategories, setSelectedCategories] = useState<string[]>(["all"]);
  const [timeLimitSeconds, setTimeLimitSeconds] = useState(120);
  const [remainingSeconds, setRemainingSeconds] = useState(120);
  const [queue, setQueue] = useState<QuestionDetail[]>([]);
  const [queueIndex, setQueueIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [attempts, setAttempts] = useState<QuizAttempt[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [promptStartedAt, setPromptStartedAt] = useState(() => Date.now());

  const categoryNameBySlug = useMemo(
    () => Object.fromEntries(categories.map((category) => [category.slug, category.name])),
    [categories],
  );

  const filteredQuestions = useMemo(() => {
    if (selectedCategories.includes("all")) {
      return questions;
    }
    return questions.filter(
      (question) =>
        question.subtopic_slug !== null && selectedCategories.includes(question.subtopic_slug),
    );
  }, [questions, selectedCategories]);

  const currentQuestion = queue.length > 0 ? queue[queueIndex % queue.length] : null;

  useEffect(() => {
    if (phase !== "running") {
      return;
    }

    if (remainingSeconds <= 0) {
      setPhase("results");
      return;
    }

    const timeout = window.setTimeout(() => {
      setRemainingSeconds((seconds) => seconds - 1);
    }, 1000);

    return () => window.clearTimeout(timeout);
  }, [phase, remainingSeconds]);

  function toggleCategory(slug: string) {
    if (slug === "all") {
      setSelectedCategories(["all"]);
      return;
    }

    setSelectedCategories((current) => {
      const withoutAll = current.filter((item) => item !== "all");
      if (withoutAll.includes(slug)) {
        const next = withoutAll.filter((item) => item !== slug);
        return next.length === 0 ? ["all"] : next;
      }
      return [...withoutAll, slug];
    });
  }

  function startQuiz() {
    if (filteredQuestions.length === 0) {
      setError("Select at least one category with available prompts.");
      return;
    }

    setError(null);
    setQueue(shuffleQuestions(filteredQuestions));
    setQueueIndex(0);
    setAnswer("");
    setAttempts([]);
    setRemainingSeconds(timeLimitSeconds);
    setPromptStartedAt(Date.now());
    setPhase("running");
  }

  async function submitAnswer() {
    if (currentQuestion === null || phase !== "running") {
      return;
    }

    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer) {
      setError("Type an answer before submitting.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const timeSpentSeconds = Math.max(1, Math.round((Date.now() - promptStartedAt) / 1000));
      const result = await recordAttempt({
        questionId: currentQuestion.id,
        answer: trimmedAnswer,
        timeSpentSeconds,
      });

      setAttempts((current) => [
        ...current,
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
      setError("Submit is unavailable. Verify the API is running.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleEnter() {
    if (phase !== "running") {
      return;
    }
    void submitAnswer();
  }

  const categoryStats = useMemo(() => {
    const stats = new Map<string, CategoryStat>();

    for (const attempt of attempts) {
      const slug = attempt.categorySlug ?? "uncategorized";
      const name =
        attempt.categorySlug === null
          ? "Uncategorized"
          : (categoryNameBySlug[attempt.categorySlug] ?? attempt.categorySlug);
      const current = stats.get(slug) ?? { slug, name, attempts: 0, correct: 0 };
      current.attempts += 1;
      if (attempt.isCorrect) {
        current.correct += 1;
      }
      stats.set(slug, current);
    }

    return [...stats.values()].sort((left, right) => right.attempts - left.attempts);
  }, [attempts, categoryNameBySlug]);

  const totalAttempts = attempts.length;
  const totalCorrect = attempts.filter((attempt) => attempt.isCorrect).length;
  const overallAccuracy = totalAttempts === 0 ? 0 : Math.round((totalCorrect / totalAttempts) * 100);

  if (phase === "results") {
    return (
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Timed quiz</p>
          <h2 className="text-2xl font-semibold text-[#15201c]">Results</h2>
          <p className="mt-1 text-sm text-[#66736e]">
            {totalAttempts} question{totalAttempts === 1 ? "" : "s"} attempted · {overallAccuracy}%
            accuracy
          </p>
        </div>

        {categoryStats.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[#edf5f1] text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                  <th className="px-3 py-2">Category</th>
                  <th className="px-3 py-2">Attempted</th>
                  <th className="px-3 py-2">Correct</th>
                  <th className="px-3 py-2">Accuracy</th>
                </tr>
              </thead>
              <tbody>
                {categoryStats.map((stat) => (
                  <tr key={stat.slug} className="border-b border-[#f6f7f4]">
                    <td className="px-3 py-2 font-medium text-[#15201c]">{stat.name}</td>
                    <td className="px-3 py-2 text-[#66736e]">{stat.attempts}</td>
                    <td className="px-3 py-2 text-[#66736e]">{stat.correct}</td>
                    <td className="px-3 py-2 text-[#66736e]">
                      {stat.attempts === 0 ? "—" : `${Math.round((stat.correct / stat.attempts) * 100)}%`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-[#66736e]">No answers were submitted before time ran out.</p>
        )}

        <button
          type="button"
          onClick={() => setPhase("setup")}
          className={cn(buttonVariants(), "mt-5")}
        >
          Start another quiz
        </button>
      </section>
    );
  }

  if (phase === "running") {
    return (
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Timed quiz</p>
            <h2 className="text-2xl font-semibold text-[#15201c]">Answer as many as you can</h2>
            {currentQuestion ? (
              <p className="mt-1 text-sm text-[#66736e]">
                Prompt {attempts.length + 1}
                {currentQuestion.subtopic_slug ? ` · ${currentQuestion.subtopic_slug}` : ""}
              </p>
            ) : null}
          </div>
          <div className="rounded-lg border border-[#bdd3ca] bg-[#edf5f1] px-4 py-2 text-center">
            <p className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">Time left</p>
            <p className="text-2xl font-semibold text-[#15201c]">{formatSeconds(remainingSeconds)}</p>
          </div>
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
                aria-label="Timed quiz answer"
                className="h-11"
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    handleEnter();
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
            {error ? <p className="mt-3 text-sm text-[#b42318]">{error}</p> : null}
            <p className="mt-3 text-sm text-[#66736e]">
              {totalAttempts} submitted · press Enter to submit and move on
            </p>
          </>
        ) : (
          <p className="text-sm text-[#66736e]">No prompts available for this quiz.</p>
        )}
      </section>
    );
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(280px,0.8fr)]">
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Timed quiz</p>
          <h2 className="text-2xl font-semibold text-[#15201c]">Configure your session</h2>
        </div>

        <div className="grid gap-5">
          <div>
            <p className="mb-2 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Time limit
            </p>
            <div className="flex flex-wrap gap-2">
              {TIME_OPTIONS.map((option) => (
                <button
                  key={option.seconds}
                  type="button"
                  onClick={() => setTimeLimitSeconds(option.seconds)}
                  className={cn(
                    "rounded-lg border px-3 py-2 text-sm font-medium transition-colors",
                    timeLimitSeconds === option.seconds
                      ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
                      : "border-[#dfe6e1] bg-[#fbfcfa] text-[#31443d]",
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Categories
            </p>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => toggleCategory("all")}
                className={cn(
                  "rounded-lg border px-3 py-2 text-sm font-medium transition-colors",
                  selectedCategories.includes("all")
                    ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
                    : "border-[#dfe6e1] bg-[#fbfcfa] text-[#31443d]",
                )}
              >
                All ({questions.length})
              </button>
              {categories.map((category) => (
                <button
                  key={category.id}
                  type="button"
                  onClick={() => toggleCategory(category.slug)}
                  className={cn(
                    "rounded-lg border px-3 py-2 text-sm font-medium transition-colors",
                    selectedCategories.includes(category.slug)
                      ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
                      : "border-[#dfe6e1] bg-[#fbfcfa] text-[#31443d]",
                  )}
                >
                  {category.name} ({categoryCounts[category.slug] ?? 0})
                </button>
              ))}
            </div>
          </div>
        </div>

        {error ? <p className="mt-4 text-sm text-[#b42318]">{error}</p> : null}

        <button type="button" onClick={startQuiz} className={cn(buttonVariants(), "mt-5")}>
          Start timed quiz
        </button>
      </section>

      <aside className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <p className="text-sm leading-relaxed text-[#66736e]">
          Answer as many prompts as possible before the timer ends. Results break down attempts and
          accuracy by category.
        </p>
        <p className="mt-3 text-sm text-[#66736e]">
          Selected pool: {filteredQuestions.length} prompt
          {filteredQuestions.length === 1 ? "" : "s"}
        </p>
      </aside>
    </div>
  );
}
