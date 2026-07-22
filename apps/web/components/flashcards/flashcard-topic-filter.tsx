"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import type { TopicWithSubtopics } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type FlashcardTopicFilterProps = {
  topics: TopicWithSubtopics[];
  selectedSlug?: string;
  className?: string;
};

export function FlashcardTopicFilter({
  topics,
  selectedSlug,
  className,
}: FlashcardTopicFilterProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function handleChange(value: string) {
    startTransition(() => {
      router.push(
        value === "all" ? "/flashcards" : `/flashcards?topic=${encodeURIComponent(value)}`,
      );
    });
  }

  return (
    <label className={cn("grid min-w-[220px] gap-1 text-sm", className)}>
      <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">Topic</span>
      <select
        value={selectedSlug ?? "all"}
        disabled={isPending}
        aria-label="Filter flashcards by topic"
        onChange={(event) => handleChange(event.target.value)}
        className="h-9 w-full rounded-lg border border-[#dfe6e1] bg-white px-3 text-sm text-[#15201c] outline-none focus-visible:border-[#0f766e] focus-visible:ring-3 focus-visible:ring-[#0f766e]/20 disabled:opacity-60"
      >
        <option value="all">All topics</option>
        {topics.map((topic) => (
          <optgroup key={topic.id} label={topic.name}>
            <option value={topic.slug}>All {topic.name}</option>
            {topic.subtopics.map((subtopic) => (
              <option key={subtopic.id} value={subtopic.slug}>
                {subtopic.name}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </label>
  );
}
