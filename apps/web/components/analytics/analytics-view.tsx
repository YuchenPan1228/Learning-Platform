import Link from "next/link";

import type {
  AttemptHistoryItem,
  LearningAnalytics,
  SearchMiss,
  WeakConcept,
} from "@/lib/types/analytics";
import { formatMasteryScore } from "@/lib/mastery";

function formatAttemptResult(item: AttemptHistoryItem): string {
  if (item.is_correct === true) {
    return "Correct";
  }
  if (item.is_correct === false) {
    return "Incorrect";
  }
  return "Ungraded";
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function ReviewDueCount({ count }: { count: number }) {
  return (
    <section
      aria-label="Review due count"
      className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Spaced repetition</p>
      <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Flashcards due</h2>
      <p className="mt-4 text-4xl font-semibold text-[#15201c]">{count}</p>
      <p className="mt-2 text-sm text-[#66736e]">
        Cards never reviewed or past their next review time.
      </p>
      <Link
        href="/flashcards"
        className="mt-4 inline-flex text-sm font-semibold text-[#176b54] hover:underline"
      >
        Open flashcards
      </Link>
    </section>
  );
}

function WeakConceptsPanel({ concepts }: { concepts: WeakConcept[] }) {
  return (
    <section
      aria-label="Weak concepts"
      className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Mastery</p>
      <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Weak concepts</h2>
      <p className="mt-1 text-sm text-[#66736e]">
        Concepts below 50% mastery, lowest scores first.
      </p>

      {concepts.length === 0 ? (
        <p className="mt-4 text-sm text-[#66736e]">No weak concepts under the current threshold.</p>
      ) : (
        <ul className="mt-4 grid gap-2">
          {concepts.map((concept) => (
            <li
              key={concept.concept_id}
              className="flex items-center justify-between gap-3 border-t border-[#edf5f1] pt-3 text-sm first:border-t-0 first:pt-0"
            >
              <div>
                <Link
                  href={`/concepts/${concept.slug}`}
                  className="font-semibold text-[#176b54] hover:underline"
                >
                  {concept.name}
                </Link>
                <span className="mt-1 block text-[#66736e]">{concept.topic_slug}</span>
              </div>
              <span className="shrink-0 font-semibold text-[#b7791f]">
                {formatMasteryScore(concept.mastery_score)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function AttemptHistoryPanel({ attempts }: { attempts: AttemptHistoryItem[] }) {
  return (
    <section
      aria-label="Attempt history"
      className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Practice</p>
      <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Attempt history</h2>
      <p className="mt-1 text-sm text-[#66736e]">Most recent graded and ungraded attempts.</p>

      {attempts.length === 0 ? (
        <p className="mt-4 text-sm text-[#66736e]">No attempts yet. Start a practice session.</p>
      ) : (
        <ul className="mt-4 grid gap-3">
          {attempts.map((attempt) => (
            <li
              key={attempt.id}
              className="flex items-start justify-between gap-3 border-t border-[#edf5f1] pt-3 text-sm first:border-t-0 first:pt-0"
            >
              <div>
                <Link
                  href={`/practice/${attempt.question_id}`}
                  className="font-semibold text-[#176b54] hover:underline"
                >
                  {attempt.question_title}
                </Link>
                <span className="mt-1 block text-[#66736e]">
                  {attempt.topic_slug} · {formatTimestamp(attempt.created_at)} ·{" "}
                  {attempt.time_spent_seconds}s
                </span>
              </div>
              <span
                className={
                  attempt.is_correct === true
                    ? "shrink-0 font-semibold text-[#176b54]"
                    : attempt.is_correct === false
                      ? "shrink-0 font-semibold text-[#b7791f]"
                      : "shrink-0 font-semibold text-[#66736e]"
                }
              >
                {formatAttemptResult(attempt)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function SearchMissesPanel({ misses }: { misses: SearchMiss[] }) {
  return (
    <section
      aria-label="Search misses"
      className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Active learning</p>
      <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Search misses</h2>
      <p className="mt-1 text-sm text-[#66736e]">
        Queries that returned no results — useful signals for later content gaps.
      </p>

      {misses.length === 0 ? (
        <p className="mt-4 text-sm text-[#66736e]">No search misses recorded yet.</p>
      ) : (
        <ul className="mt-4 grid gap-3">
          {misses.map((miss) => (
            <li
              key={miss.id}
              className="border-t border-[#edf5f1] pt-3 text-sm first:border-t-0 first:pt-0"
            >
              <strong className="block text-[#15201c]">&ldquo;{miss.query}&rdquo;</strong>
              <span className="mt-1 block text-[#66736e]">
                {formatTimestamp(miss.created_at)}
                {miss.topic_slug ? ` · ${miss.topic_slug}` : ""}
                {miss.types.length > 0 ? ` · ${miss.types.join(", ")}` : ""}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function AnalyticsView({ analytics }: { analytics: LearningAnalytics }) {
  return (
    <div className="grid gap-6">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <ReviewDueCount count={analytics.review_due_count} />
        <WeakConceptsPanel concepts={analytics.weak_concepts} />
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <AttemptHistoryPanel attempts={analytics.attempt_history} />
        <SearchMissesPanel misses={analytics.search_misses} />
      </div>
    </div>
  );
}
