"use client";

import { useRouter } from "next/navigation";

import { TopicBadge } from "@/components/ui/topic-badge";
import type { QuestionProgressStatus, QuestionSummary } from "@/lib/types/question";
import { formatDifficulty } from "@/lib/questions/format";
import { getTopicPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

const PROGRESS_LABELS: Record<QuestionProgressStatus, string> = {
  not_attempted: "New",
  attempted: "Attempted",
  solved: "Solved",
};

const PROGRESS_STYLES: Record<QuestionProgressStatus, string> = {
  not_attempted: "border-[#dfe6e1] bg-[#fbfcfa] text-[#66736e]",
  attempted: "border-[#f4d9a6] bg-[#fff8eb] text-[#8a5b00]",
  solved: "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]",
};

export function QuestionCard({
  question,
  returnTo,
  questionIds,
}: {
  question: QuestionSummary;
  returnTo?: string;
  questionIds?: number[];
}) {
  const router = useRouter();
  const progressStatus = question.progress_status ?? "not_attempted";
  const palette = getTopicPalette(question.topic_slug);

  const params = new URLSearchParams();
  if (returnTo) {
    params.set("returnTo", returnTo);
  }
  if (questionIds && questionIds.length > 0) {
    params.set("ids", questionIds.join(","));
  }
  const query = params.toString();
  const practiceHref = query
    ? `/practice/${question.id}?${query}`
    : `/practice/${question.id}`;

  return (
    <article
      role="link"
      tabIndex={0}
      onClick={() => router.push(practiceHref)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          router.push(practiceHref);
        }
      }}
      className={cn(
        "cursor-pointer rounded-lg border border-l-4 bg-white p-4 shadow-[0_8px_24px_rgba(21,32,28,0.06)] transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-[#0f766e]/20",
        palette.border,
        palette.accent,
        palette.hoverSurface,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <TopicBadge slug={question.topic_slug} />
          <h3 className="mt-2 line-clamp-2 text-base font-semibold text-[#15201c]">
            {question.title}
          </h3>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          <span className="rounded-full border border-[#dfe6e1] bg-[#fbfcfa] px-2 py-0.5 text-[11px] font-semibold tracking-wide text-[#31443d] uppercase">
            {formatDifficulty(question.difficulty)}
          </span>
          <span className="text-[11px] text-[#66736e]">
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
    </article>
  );
}
