"use client";

import Link from "next/link";
import { useState } from "react";

import { buttonVariants } from "@/components/ui/button";
import { shouldShowAiCacheState } from "@/lib/ai/cache-state";
import {
  requestExplanation,
  requestHints,
  requestSimilarQuestion,
} from "@/lib/api/ai-tutor";
import type {
  AIExplanationResult,
  AIHintsResult,
  SimilarQuestionResult,
} from "@/lib/types/ai-tutor";
import { cn } from "@/lib/utils";

type AiTutorPanelProps = {
  questionId: number;
  answer: string;
  returnTo: string;
};

type PendingAction = "hint" | "explanation" | "similar" | null;

function CacheStateBadge({ cacheHit }: { cacheHit: boolean }) {
  return (
    <span className="rounded-full border border-[#dfe6e1] bg-[#fbfcfa] px-2 py-0.5 text-[10px] font-semibold tracking-wide text-[#66736e] uppercase">
      cache {cacheHit ? "hit" : "miss"}
    </span>
  );
}

export function AiTutorPanel({ questionId, answer, returnTo }: AiTutorPanelProps) {
  const showCacheState = shouldShowAiCacheState();
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [error, setError] = useState<string | null>(null);
  const [hints, setHints] = useState<AIHintsResult | null>(null);
  const [hintsAnswer, setHintsAnswer] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<AIExplanationResult | null>(null);
  const [explanationAnswer, setExplanationAnswer] = useState<string | null>(null);
  const [showHints, setShowHints] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [similar, setSimilar] = useState<SimilarQuestionResult | null>(null);

  function requireAnswer() {
    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer) {
      throw new Error("Write an answer before requesting AI help.");
    }
    return trimmedAnswer;
  }

  async function ensureHints() {
    const trimmedAnswer = requireAnswer();
    if (hints !== null && hintsAnswer === trimmedAnswer) {
      return hints;
    }
    const result = await requestHints(questionId, trimmedAnswer);
    setHints(result);
    setHintsAnswer(trimmedAnswer);
    return result;
  }

  async function ensureExplanation() {
    const trimmedAnswer = requireAnswer();
    if (explanation !== null && explanationAnswer === trimmedAnswer) {
      return explanation;
    }
    const result = await requestExplanation(questionId, trimmedAnswer);
    setExplanation(result);
    setExplanationAnswer(trimmedAnswer);
    return result;
  }

  async function handleHint() {
    setPendingAction("hint");
    setError(null);
    try {
      await ensureHints();
      setShowHints(true);
    } catch (caught) {
      setError(
        caught instanceof Error && caught.message.startsWith("Write an answer")
          ? caught.message
          : "AI hint is unavailable. Check that the API and Ollama are running.",
      );
    } finally {
      setPendingAction(null);
    }
  }

  async function handleExplanation() {
    setPendingAction("explanation");
    setError(null);
    try {
      await ensureExplanation();
      setShowExplanation(true);
    } catch (caught) {
      setError(
        caught instanceof Error && caught.message.startsWith("Write an answer")
          ? caught.message
          : "AI explanation is unavailable. Check that the API and Ollama are running.",
      );
    } finally {
      setPendingAction(null);
    }
  }

  async function handleSimilar() {
    setPendingAction("similar");
    setError(null);
    try {
      const result = await requestSimilarQuestion(questionId);
      setSimilar(result);
    } catch {
      setError(
        "Similar question generation is unavailable. Check that the API and Ollama are running.",
      );
    } finally {
      setPendingAction(null);
    }
  }

  return (
    <div className="mt-5 border-t border-[#edf5f1] pt-4">
      <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">AI tutor</p>
      <p className="mt-1 text-sm text-[#66736e]">
        Request a hint, full explanation, or an original practice variant.
      </p>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={handleHint}
          disabled={pendingAction !== null}
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "disabled:cursor-not-allowed disabled:opacity-50",
          )}
        >
          {pendingAction === "hint" ? "Requesting…" : "Get hint"}
        </button>
        <button
          type="button"
          onClick={handleExplanation}
          disabled={pendingAction !== null}
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "disabled:cursor-not-allowed disabled:opacity-50",
          )}
        >
          {pendingAction === "explanation" ? "Requesting…" : "Get explanation"}
        </button>
        <button
          type="button"
          onClick={handleSimilar}
          disabled={pendingAction !== null}
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "disabled:cursor-not-allowed disabled:opacity-50",
          )}
        >
          {pendingAction === "similar" ? "Generating…" : "Similar question"}
        </button>
      </div>

      {error ? <p className="mt-3 text-sm text-[#b42318]">{error}</p> : null}

      {hints && showHints ? (
        <div className="mt-4 rounded-lg border border-[#bdd3ca] bg-[#edf5f1] p-3">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-sm font-semibold text-[#15201c]">Hints</h4>
            {showCacheState ? <CacheStateBadge cacheHit={hints.cache_hit} /> : null}
          </div>
          <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-[#31443d]">
            {hints.hints.map((hint) => (
              <li key={hint}>{hint}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {explanation && showExplanation ? (
        <div className="mt-3 rounded-lg border border-[#bdd3ca] bg-[#edf5f1] p-3">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-sm font-semibold text-[#15201c]">Explanation</h4>
            {showCacheState ? <CacheStateBadge cacheHit={explanation.cache_hit} /> : null}
          </div>
          <p className="mt-2 text-sm leading-relaxed text-[#31443d]">{explanation.explanation}</p>
        </div>
      ) : null}

      {similar ? (
        <div className="mt-3 rounded-lg border border-[#bdd3ca] bg-[#edf5f1] p-3">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-sm font-semibold text-[#15201c]">Similar question draft</h4>
            {showCacheState ? <CacheStateBadge cacheHit={similar.cache_hit} /> : null}
          </div>
          <p className="mt-2 text-sm font-medium text-[#15201c]">{similar.title}</p>
          <p className="mt-1 text-sm leading-relaxed text-[#31443d]">{similar.body}</p>
          <p className="mt-2 text-xs text-[#66736e]">
            Saved as draft #{similar.draft_question_id} from question #{similar.generated_from_id}.
          </p>
          <Link
            href={`/practice/${similar.draft_question_id}?returnTo=${encodeURIComponent(returnTo)}`}
            className={cn(buttonVariants({ variant: "outline", size: "sm" }), "mt-3 inline-flex")}
          >
            Open draft
          </Link>
        </div>
      ) : null}
    </div>
  );
}
