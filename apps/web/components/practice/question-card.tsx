import type { QuestionSummary } from "@/lib/types/question";
import { formatDifficulty, formatEstimatedTime } from "@/lib/questions/format";

export function QuestionCard({ question }: { question: QuestionSummary }) {
  return (
    <article className="flex h-full flex-col rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
            {question.topic_slug}
            {question.subtopic_slug ? ` · ${question.subtopic_slug}` : ""}
          </p>
          <h3 className="mt-1 text-lg font-semibold text-[#15201c]">{question.title}</h3>
        </div>
        <span className="rounded-full border border-[#dfe6e1] bg-[#fbfcfa] px-2.5 py-1 text-xs font-semibold tracking-wide text-[#31443d] uppercase">
          {formatDifficulty(question.difficulty)}
        </span>
      </div>

      <dl className="mt-4 grid gap-2 text-sm text-[#66736e] sm:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold tracking-wide uppercase">Estimated time</dt>
          <dd className="mt-1 font-medium text-[#15201c]">
            {formatEstimatedTime(question.estimated_time_seconds)}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold tracking-wide uppercase">Company hint</dt>
          <dd className="mt-1 font-medium text-[#15201c]">
            {question.company_hint ?? "General quant"}
          </dd>
        </div>
      </dl>

      {question.tags.length > 0 ? (
        <div className="mt-4 flex flex-wrap gap-2">
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

      <p className="mt-auto pt-4 text-sm text-[#66736e]">Practice session opens in QP-018.</p>
    </article>
  );
}
