"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { AiTutorPanel } from "@/components/practice/ai-tutor-panel";
import { QuestionMetadata } from "@/components/practice/question-metadata";
import { buttonVariants } from "@/components/ui/button";
import { recordAttempt } from "@/lib/api/attempts";
import type { QuestionProgress } from "@/lib/api/questions";
import { setQuestionProgress } from "@/lib/api/questions";
import { formatDifficulty } from "@/lib/questions/format";
import { findRelatedConcept, resolvePrerequisiteLinks } from "@/lib/practice/prerequisite-links";
import {
  formatQuestionProgressLabel,
  isQuestionSolved,
  PROGRESS_BADGE_STYLES,
} from "@/lib/practice/progress-display";
import type { AttemptResult } from "@/lib/types/attempt";
import type { ConceptSummary } from "@/lib/types/concept";
import type { QuestionDetail, QuestionProgressStatus } from "@/lib/types/question";
import { cn } from "@/lib/utils";

type PracticeSessionProps = {
  question: QuestionDetail;
  returnTo: string;
  questionIds: number[];
  concepts: ConceptSummary[];
  initialProgress: QuestionProgress | null;
};

function buildSessionHref(questionId: number, returnTo: string, questionIds: number[]): string {
  const params = new URLSearchParams();
  params.set("returnTo", returnTo);
  if (questionIds.length > 0) {
    params.set("ids", questionIds.join(","));
  }
  return `/practice/${questionId}?${params.toString()}`;
}

export function PracticeSession({
  question,
  returnTo,
  questionIds,
  concepts,
  initialProgress,
}: PracticeSessionProps) {
  const [startedAt] = useState(() => Date.now());
  const [answer, setAnswer] = useState("");
  const [checkResult, setCheckResult] = useState<AttemptResult | null>(null);
  const [solutionRevealed, setSolutionRevealed] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [checkError, setCheckError] = useState<string | null>(null);
  const [progressStatus, setProgressStatus] = useState<QuestionProgressStatus>(
    initialProgress?.status ?? question.progress_status ?? "not_attempted",
  );
  const [isUpdatingProgress, setIsUpdatingProgress] = useState(false);
  const [progressError, setProgressError] = useState<string | null>(null);

  const supportsSelfCheck = question.short_answer !== null && question.short_answer.trim() !== "";

  const currentIndex = questionIds.indexOf(question.id);
  const hasNavigation = questionIds.length > 1 && currentIndex >= 0;
  const previousQuestionId = hasNavigation
    ? questionIds[(currentIndex - 1 + questionIds.length) % questionIds.length]
    : null;
  const nextQuestionId = hasNavigation
    ? questionIds[(currentIndex + 1) % questionIds.length]
    : null;

  const relatedConcept = useMemo(
    () => findRelatedConcept(question.subtopic_slug, concepts),
    [concepts, question.subtopic_slug],
  );
  const prerequisiteLinks = useMemo(
    () => resolvePrerequisiteLinks(question.prerequisites, concepts),
    [concepts, question.prerequisites],
  );
  const progressLabel = formatQuestionProgressLabel(progressStatus);
  const progressStyle = isQuestionSolved(progressStatus)
    ? PROGRESS_BADGE_STYLES.solved
    : PROGRESS_BADGE_STYLES.unsolved;

  async function handleSelfCheck() {
    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer) {
      setCheckError("Write an answer before checking.");
      return;
    }

    setIsChecking(true);
    setCheckError(null);

    try {
      const timeSpentSeconds = Math.max(1, Math.round((Date.now() - startedAt) / 1000));
      const result = await recordAttempt({
        questionId: question.id,
        answer: trimmedAnswer,
        timeSpentSeconds,
      });
      setCheckResult(result);
      if (result.is_correct) {
        setProgressStatus("solved");
      } else {
        setProgressStatus("attempted");
      }
    } catch {
      setCheckError("Self-check is unavailable. Check that the API is running.");
    } finally {
      setIsChecking(false);
    }
  }

  async function handleMarkProgress(status: "solved" | "not_attempted") {
    setIsUpdatingProgress(true);
    setProgressError(null);
    try {
      const updated = await setQuestionProgress(question.id, status);
      setProgressStatus(updated.status);
    } catch {
      setProgressError("Could not update progress. Check that the API is running.");
    } finally {
      setIsUpdatingProgress(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(280px,0.8fr)]">
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
              {question.topic_slug}
              {question.subtopic_slug ? ` · ${question.subtopic_slug}` : ""} ·{" "}
              {formatDifficulty(question.difficulty)}
            </p>
            <h2 className="mt-1 text-2xl font-semibold text-[#15201c]">{question.title}</h2>
            {hasNavigation ? (
              <p className="mt-1 text-sm text-[#66736e]">
                Question {currentIndex + 1} of {questionIds.length}
              </p>
            ) : null}
          </div>
          <div className="flex shrink-0 flex-wrap gap-2">
            {hasNavigation ? (
              <>
                {previousQuestionId !== null ? (
                  <Link
                    href={buildSessionHref(previousQuestionId, returnTo, questionIds)}
                    className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
                  >
                    Previous
                  </Link>
                ) : null}
                {nextQuestionId !== null ? (
                  <Link
                    href={buildSessionHref(nextQuestionId, returnTo, questionIds)}
                    className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
                  >
                    Next
                  </Link>
                ) : null}
              </>
            ) : null}
            <Link
              href={returnTo}
              className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
            >
              Back to browser
            </Link>
          </div>
        </div>

        <p className="text-sm leading-relaxed text-[#31443d]">{question.body}</p>

        <label className="mt-5 grid gap-2">
          <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
            Your answer
          </span>
          <textarea
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            placeholder="Write your reasoning or final answer..."
            rows={6}
            className="min-h-[144px] w-full rounded-lg border border-[#dfe6e1] bg-[#fbfcfa] px-3 py-2 text-sm text-[#15201c] outline-none focus-visible:border-[#0f766e] focus-visible:ring-3 focus-visible:ring-[#0f766e]/20"
          />
        </label>

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={handleSelfCheck}
            disabled={isChecking || !supportsSelfCheck}
            className={cn(buttonVariants(), "disabled:cursor-not-allowed disabled:opacity-50")}
          >
            {isChecking ? "Checking…" : "Check answer"}
          </button>
          <button
            type="button"
            onClick={() => setSolutionRevealed(true)}
            className={buttonVariants({ variant: "outline" })}
          >
            Reveal solution
          </button>
        </div>

        {!supportsSelfCheck ? (
          <p className="mt-3 text-sm text-[#66736e]">
            Deterministic self-check is not available for this question. Use solution reveal to
            compare your work.
          </p>
        ) : null}

        {checkError ? <p className="mt-3 text-sm text-[#b42318]">{checkError}</p> : null}

        {solutionRevealed ? (
          <section className="mt-6 rounded-lg border border-[#bdd3ca] bg-[#edf5f1] p-4">
            <h3 className="text-sm font-semibold text-[#15201c]">Solution</h3>
            {question.canonical_solution ? (
              <p className="mt-2 text-sm leading-relaxed text-[#31443d]">
                {question.canonical_solution}
              </p>
            ) : (
              <p className="mt-2 text-sm text-[#66736e]">No canonical solution is stored yet.</p>
            )}
            {question.short_answer ? (
              <p className="mt-3 text-sm text-[#66736e]">
                Expected answer:{" "}
                <span className="font-medium text-[#15201c]">{question.short_answer}</span>
              </p>
            ) : null}
          </section>
        ) : null}

        <div className="mt-6 border-t border-[#edf5f1] pt-5">
          <h3 className="mb-3 text-sm font-semibold text-[#15201c]">Question metadata</h3>
          <QuestionMetadata question={question} />
        </div>
      </section>

      <aside className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Progress</p>
          <div className="mt-2 flex items-center gap-2">
            <span className="text-sm font-medium text-[#15201c]">Status:</span>
            <span
              className={cn(
                "rounded-full border px-2.5 py-1 text-xs font-semibold tracking-wide uppercase",
                progressStyle,
              )}
            >
              {progressLabel}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => handleMarkProgress("solved")}
            disabled={isUpdatingProgress || isQuestionSolved(progressStatus)}
            className={cn(
              buttonVariants({ variant: "outline", size: "sm" }),
              "disabled:cursor-not-allowed disabled:opacity-50",
            )}
          >
            Mark solved
          </button>
          <button
            type="button"
            onClick={() => handleMarkProgress("not_attempted")}
            disabled={isUpdatingProgress || !isQuestionSolved(progressStatus)}
            className={cn(
              buttonVariants({ variant: "outline", size: "sm" }),
              "disabled:cursor-not-allowed disabled:opacity-50",
            )}
          >
            Mark unsolved
          </button>
        </div>
        {progressError ? <p className="mt-2 text-sm text-[#b42318]">{progressError}</p> : null}

        {relatedConcept ? (
          <div className="mt-5 border-t border-[#edf5f1] pt-4">
            <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
              Related concept
            </p>
            <Link
              href={`/concepts/${relatedConcept.slug}`}
              className="mt-2 inline-flex text-sm font-medium text-[#176b54] hover:underline"
            >
              {relatedConcept.name}
            </Link>
          </div>
        ) : null}

        {prerequisiteLinks.length > 0 ? (
          <div className="mt-5 border-t border-[#edf5f1] pt-4">
            <p className="mb-2 text-xs font-bold tracking-wide text-[#66736e] uppercase">
              Prerequisites
            </p>
            <div className="flex flex-wrap gap-2">
              {prerequisiteLinks.map((prerequisite) =>
                prerequisite.href ? (
                  <Link
                    key={prerequisite.label}
                    href={prerequisite.href}
                    className="rounded-full border border-[#bdd3ca] bg-[#edf5f1] px-2.5 py-1 text-xs font-medium text-[#176b54] hover:bg-[#dff0e8]"
                  >
                    {prerequisite.label}
                  </Link>
                ) : (
                  <span
                    key={prerequisite.label}
                    className="rounded-full border border-[#dfe6e1] bg-[#fbfcfa] px-2.5 py-1 text-xs font-medium text-[#66736e]"
                  >
                    {prerequisite.label}
                  </span>
                ),
              )}
            </div>
          </div>
        ) : null}

        <div className="mt-5 border-t border-[#edf5f1] pt-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Feedback</p>
          <h3 className="mt-1 text-sm font-semibold text-[#15201c]">Self-check</h3>
          {checkResult ? (
            <div className="mt-2 grid gap-3">
              <p
                className={cn(
                  "text-sm leading-relaxed",
                  checkResult.is_correct ? "text-[#176b54]" : "text-[#66736e]",
                )}
              >
                {checkResult.feedback ?? "Attempt recorded."}
              </p>
              {checkResult.supported && checkResult.is_correct === false ? (
                <p className="text-sm text-[#66736e]">
                  Reveal the solution to review the full reasoning and common mistakes.
                </p>
              ) : null}
            </div>
          ) : (
            <p className="mt-2 text-sm leading-relaxed text-[#66736e]">
              Submit an answer to run deterministic self-check.
            </p>
          )}
        </div>

        <AiTutorPanel questionId={question.id} answer={answer} returnTo={returnTo} />

        {question.tags.length > 0 ? (
          <div className="mt-5 flex flex-wrap gap-2 border-t border-[#edf5f1] pt-4">
            {question.tags.map((tag) => (
              <span
                key={tag.id}
                className="rounded-full border border-[#bdd3ca] bg-[#edf5f1] px-2.5 py-1 text-xs font-medium text-[#176b54]"
              >
                {tag.name}
              </span>
            ))}
          </div>
        ) : null}
      </aside>
    </div>
  );
}
