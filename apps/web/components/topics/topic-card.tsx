import Link from "next/link";

import { TopicBadge } from "@/components/ui/topic-badge";
import { formatMasteryScore } from "@/lib/mastery";
import { MasteryBar } from "@/components/ui/mastery-bar";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { getConceptPalette, getTopicPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

type TopicCardProps = {
  topic: TopicWithSubtopics;
  masteryScore: number;
};

export function TopicCard({ topic, masteryScore }: TopicCardProps) {
  const palette = getTopicPalette(topic.slug);

  return (
    <Link
      href={`/topics/${topic.slug}`}
      className={cn(
        "flex h-full flex-col rounded-lg border border-l-4 bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)] transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-[#0f766e]/20",
        palette.border,
        palette.accent,
        palette.hoverSurface,
      )}
    >
      <article className="flex h-full flex-col">
        <div className="flex items-start justify-between gap-3">
          <div>
            <TopicBadge slug={topic.slug} label={topic.name} />
            <h3 className="mt-3 text-lg font-semibold text-[#15201c]">{topic.name}</h3>
            <p className="mt-1 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              {topic.subtopics.length} subtopics
            </p>
          </div>
          <span className={cn("shrink-0 text-sm font-semibold", palette.badgeText)}>
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
          {topic.subtopics.map((subtopic) => {
            const subtopicPalette = getConceptPalette(subtopic.slug, topic.slug);
            return (
              <span
                key={subtopic.id}
                className={cn(
                  "rounded-full border px-2.5 py-1 text-xs font-medium",
                  subtopicPalette.border,
                  subtopicPalette.badge,
                  subtopicPalette.badgeText,
                )}
              >
                {subtopic.name}
              </span>
            );
          })}
        </div>
      </article>
    </Link>
  );
}
