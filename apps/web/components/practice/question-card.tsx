import Link from "next/link";

import type { QuestionSummary } from "@/lib/types/question";
import type { QuestionProgressStatus } from "@/lib/types/progress";
import { formatDifficulty } from "@/lib/questions/format";
import { cn } from "@/lib/utils";

const PROGRESS_LABELS: Record<QuestionProgressStatus, string> = {
  not_attempted: "Not started",
  attempted: "Attempted",
  solved: "Solved",
};

const PROGRESS_STYLES: Record<QuestionProgressStatus, string> = {
  not_attempted: "border-[#dfe6e1] bg-[#fbfcfa] text-[#66736e]",
  attempted: "border-[#f2d6a0] bg-[#fff8eb] text-[#9a6700]",
  solved: "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]",
};

export function QuestionCard({
  question,
  returnTo,
}: {
  question: QuestionSummary;
  returnTo?: string;
}) {
  const practiceHref = returnTo
    ? `/practice/${question.id}?returnTo=${encodeURIComponent(returnTo)}`
    : `/practice/${question.id}`;
  const progressStatus = question.progress_status ?? "not_attempted";

  return (
    <Link
      href={practiceHref}
      className="group block rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_12px_32px_rgba(21,32,28,0.06)] transition-colors hover:border-[#bdd3ca] hover:bg-[#fbfcfa]"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
            {question.topic_slug}
            {question.subtopic_slug ? ` · ${question.subtopic_slug}` : ""}
          </p>
          <h3 className="mt-1 line-clamp-2 text-base font-semibold text-[#15201c] group-hover:text-[#176b54]">
            {question.title}
          </h3>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          <span className="rounded-full border border-[#dfe6e1] bg-[#fbfcfa] px-2 py-0.5 text-[11px] font-semibold tracking-wide text-[#31443d] uppercase">
            {formatDifficulty(question.difficulty)}
          </span>
          <span className="text-[11px] font-medium text-[#66736e]">
            {question.company_hint ?? "General quant"}
          </span>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span
          className={cn(
            "rounded-full border px-2 py-0.5 text-[11px] font-semibold tracking-wide uppercase",
            PROGRESS_STYLES[progressStatus],
          )}
        >
          {PROGRESS_LABELS[progressStatus]}
        </span>
        {question.tags.slice(0, 3).map((tag) => (
          <span
            key={tag.id}
            className="rounded-full border border-[#edf5f1] bg-[#fbfcfa] px-2 py-0.5 text-[11px] font-medium text-[#66736e]"
          >
            {tag.name}
          </span>
        ))}
      </div>
    </Link>
  );
}
