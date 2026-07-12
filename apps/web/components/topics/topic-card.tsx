import Link from "next/link";

import { formatMasteryScore } from "@/lib/mastery";
import { MasteryBar } from "@/components/ui/mastery-bar";
import type { TopicWithSubtopics } from "@/lib/types/topic";

type TopicCardProps = {
  topic: TopicWithSubtopics;
  masteryScore: number;
};

export function TopicCard({ topic, masteryScore }: TopicCardProps) {
  return (
    <article className="flex h-full flex-col rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <Link
            href={`/topics/${topic.slug}`}
            className="text-lg font-semibold text-[#15201c] hover:text-[#176b54] hover:underline"
          >
            {topic.name}
          </Link>
          <p className="mt-1 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
            {topic.subtopics.length} subtopics
          </p>
        </div>
        <span className="shrink-0 text-sm font-semibold text-[#176b54]">
          {formatMasteryScore(masteryScore)}
        </span>
      </div>

      {topic.description ? (
        <p className="mt-3 line-clamp-3 text-sm leading-relaxed text-[#66736e]">
          {topic.description}
        </p>
      ) : null}

      <MasteryBar score={masteryScore} className="mt-4" />

      <div className="mt-4 flex flex-wrap gap-2">
        {topic.subtopics.map((subtopic) => (
          <Link
            key={subtopic.id}
            href={`/concepts/${subtopic.slug}`}
            className="rounded-full border border-[#dfe6e1] bg-[#fbfcfa] px-2.5 py-1 text-xs font-medium text-[#31443d] transition-colors hover:border-[#bdd3ca] hover:bg-[#edf5f1] hover:text-[#176b54]"
          >
            {subtopic.name}
          </Link>
        ))}
      </div>

      <Link
        href={`/topics/${topic.slug}`}
        className="mt-auto pt-4 text-sm text-[#176b54] hover:underline"
      >
        Browse subtopics
      </Link>
    </article>
  );
}
