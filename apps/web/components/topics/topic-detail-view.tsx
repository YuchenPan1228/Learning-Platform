import Link from "next/link";

import { TopicBadge } from "@/components/ui/topic-badge";
import { formatMasteryScore } from "@/lib/mastery";
import { MasteryBar } from "@/components/ui/mastery-bar";
import type { ConceptSummary } from "@/lib/types/concept";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { getConceptPalette, getTopicPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

type SubtopicGridProps = {
  subtopics: TopicWithSubtopics["subtopics"];
  conceptsBySlug: Record<string, ConceptSummary>;
  masteryBySlug: Record<string, number>;
};

export function SubtopicGrid({ subtopics, conceptsBySlug, masteryBySlug }: SubtopicGridProps) {
  return (
    <section aria-label="Subtopics" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {subtopics.map((subtopic) => {
        const concept = conceptsBySlug[subtopic.slug];
        const palette = getConceptPalette(subtopic.slug, subtopic.slug);
        const masteryScore = masteryBySlug[subtopic.slug] ?? 0;

        return (
          <Link
            key={subtopic.id}
            href={`/concepts/${subtopic.slug}`}
            className={cn(
              "block rounded-lg border border-l-4 bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)] transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-[#0f766e]/20",
              palette.border,
              palette.accent,
              palette.hoverSurface,
            )}
          >
            <article>
              <div className="flex items-start justify-between gap-3">
                <TopicBadge slug={subtopic.slug} label={subtopic.name} />
                <span className={cn("shrink-0 text-sm font-semibold", palette.badgeText)}>
                  {formatMasteryScore(masteryScore)}
                </span>
              </div>
              <h4 className="mt-3 text-base font-semibold text-[#15201c]">
                {concept?.name ?? subtopic.name}
              </h4>
              <MasteryBar score={masteryScore} className="mt-3" />
            </article>
          </Link>
        );
      })}
    </section>
  );
}

type TopicDetailViewProps = {
  topic: TopicWithSubtopics;
  masteryScore: number;
  conceptsBySlug: Record<string, ConceptSummary>;
  subtopicMasteryBySlug: Record<string, number>;
};

export function TopicDetailView({
  topic,
  masteryScore,
  conceptsBySlug,
  subtopicMasteryBySlug,
}: TopicDetailViewProps) {
  const palette = getTopicPalette(topic.slug);

  return (
    <div className="grid gap-6">
      <section
        className={cn(
          "rounded-lg border border-l-4 bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]",
          palette.border,
          palette.accent,
          palette.surface,
        )}
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
              Topic section
            </p>
            <TopicBadge slug={topic.slug} label={topic.name} className="mt-2" />
            <h2 className="mt-3 text-2xl font-semibold text-[#15201c]">{topic.name}</h2>
          </div>
          <span className={cn("text-sm font-semibold", palette.badgeText)}>
            {formatMasteryScore(masteryScore)} mastery
          </span>
        </div>

        {topic.description ? (
          <p className="mt-3 max-w-3xl text-sm leading-relaxed text-[#66736e]">
            {topic.description}
          </p>
        ) : null}

        <MasteryBar score={masteryScore} className="mt-4 max-w-md" />

        <p className="mt-4 text-sm text-[#66736e]">
          {topic.subtopics.length} subtopic{topic.subtopics.length === 1 ? "" : "s"} in this section
        </p>
      </section>

      <div>
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Curriculum</p>
          <h3 className="text-xl font-semibold text-[#15201c]">Subtopics</h3>
        </div>
        <SubtopicGrid
          subtopics={topic.subtopics}
          conceptsBySlug={conceptsBySlug}
          masteryBySlug={subtopicMasteryBySlug}
        />
      </div>
    </div>
  );
}
