import Link from "next/link";

import { TopicBadge } from "@/components/ui/topic-badge";
import type { TopicMastery } from "@/lib/types/dashboard";
import { formatMasteryScore } from "@/lib/mastery";
import { MasteryBar } from "@/components/ui/mastery-bar";
import { getTopicPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

function MasteryCard({ topic }: { topic: TopicMastery }) {
  const palette = getTopicPalette(topic.slug);

  return (
    <Link
      href={`/topics/${topic.slug}`}
      className={cn(
        "block rounded-lg border border-l-4 bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)] transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-[#0f766e]/20",
        palette.border,
        palette.accent,
        palette.hoverSurface,
      )}
    >
      <article>
        <TopicBadge slug={topic.slug} label={topic.name} />
        <strong className="mt-3 block text-2xl text-[#15201c]">
          {formatMasteryScore(topic.mastery_score)}
        </strong>
        <MasteryBar score={topic.mastery_score} className="mt-3" />
        <p className="mt-3 text-sm text-[#66736e]">
          {topic.solved_count} of {topic.total_questions} solved
        </p>
      </article>
    </Link>
  );
}

export function MasteryCards({ topics }: { topics: TopicMastery[] }) {
  return (
    <section aria-label="Topic mastery">
      <div className="mb-4">
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Progress</p>
        <h2 className="text-xl font-semibold text-[#15201c]">Mastery by topic</h2>
        <p className="mt-1 text-sm text-[#66736e]">
          Scores update from your solved practice questions.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {topics.map((topic) => (
          <MasteryCard key={topic.topic_id} topic={topic} />
        ))}
      </div>
    </section>
  );
}
