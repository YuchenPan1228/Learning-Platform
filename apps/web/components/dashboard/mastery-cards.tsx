import Link from "next/link";

import type { TopicMastery } from "@/lib/types/dashboard";
import { cn } from "@/lib/utils";

function masteryTone(score: number): string {
  if (score < 35) {
    return "bg-[#b42318]";
  }
  if (score < 55) {
    return "bg-[#b7791f]";
  }
  return "bg-[#176b54]";
}

function MasteryCard({ topic }: { topic: TopicMastery }) {
  const roundedScore = Math.round(topic.mastery_score);

  return (
    <article className="rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
      <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
        {topic.name}
      </span>
      <strong className="mt-2 block text-2xl text-[#15201c]">{roundedScore}%</strong>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-[#edf5f1]">
        <div
          className={cn("h-full rounded-full transition-all", masteryTone(topic.mastery_score))}
          style={{ width: `${Math.min(Math.max(topic.mastery_score, 0), 100)}%` }}
        />
      </div>
      <Link
        href={`/topics/${topic.slug}`}
        className="mt-3 inline-block text-sm text-[#176b54] hover:underline"
      >
        Open topic
      </Link>
    </article>
  );
}

export function MasteryCards({ topics }: { topics: TopicMastery[] }) {
  return (
    <section aria-label="Topic mastery">
      <div className="mb-4">
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Progress</p>
        <h2 className="text-xl font-semibold text-[#15201c]">Mastery by topic</h2>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {topics.map((topic) => (
          <MasteryCard key={topic.topic_id} topic={topic} />
        ))}
      </div>
    </section>
  );
}
