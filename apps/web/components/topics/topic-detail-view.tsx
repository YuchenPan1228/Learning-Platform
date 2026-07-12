import Link from "next/link";

import { formatMasteryScore } from "@/lib/mastery";
import { MasteryBar } from "@/components/ui/mastery-bar";
import type { ConceptSummary } from "@/lib/types/concept";
import type { TopicWithSubtopics } from "@/lib/types/topic";

type SubtopicGridProps = {
  subtopics: TopicWithSubtopics["subtopics"];
  conceptsBySlug: Record<string, ConceptSummary>;
};

export function SubtopicGrid({ subtopics, conceptsBySlug }: SubtopicGridProps) {
  return (
    <section aria-label="Subtopics" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {subtopics.map((subtopic) => {
        const concept = conceptsBySlug[subtopic.slug];

        return (
          <article
            key={subtopic.id}
            className="rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
          >
            <Link
              href={`/concepts/${subtopic.slug}`}
              className="text-base font-semibold text-[#15201c] hover:text-[#176b54] hover:underline"
            >
              {subtopic.name}
            </Link>
            {concept ? (
              <p className="mt-2 text-sm leading-relaxed text-[#66736e]">
                Study the <span className="font-medium text-[#31443d]">{concept.name}</span> concept
                in this section.
              </p>
            ) : (
              <p className="mt-2 text-sm text-[#66736e]">
                Open the linked concept to study this area.
              </p>
            )}
            <Link
              href={`/concepts/${subtopic.slug}`}
              className="mt-3 inline-block text-sm text-[#176b54] hover:underline"
            >
              Open concept
            </Link>
          </article>
        );
      })}
    </section>
  );
}

type TopicDetailViewProps = {
  topic: TopicWithSubtopics;
  masteryScore: number;
  conceptsBySlug: Record<string, ConceptSummary>;
};

export function TopicDetailView({ topic, masteryScore, conceptsBySlug }: TopicDetailViewProps) {
  return (
    <div className="grid gap-6">
      <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
              Topic section
            </p>
            <h2 className="text-2xl font-semibold text-[#15201c]">{topic.name}</h2>
          </div>
          <span className="text-sm font-semibold text-[#176b54]">
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
        <SubtopicGrid subtopics={topic.subtopics} conceptsBySlug={conceptsBySlug} />
      </div>
    </div>
  );
}
