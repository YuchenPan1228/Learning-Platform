"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useTransition } from "react";

import { QuestionCard } from "@/components/practice/question-card";
import type { ConceptSummary } from "@/lib/types/concept";
import type { Difficulty, QuestionSummary, Tag } from "@/lib/types/question";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { matchesPracticeProgressFilter } from "@/lib/practice/progress-display";
import { cn } from "@/lib/utils";

type QuestionBrowserProps = {
  topics: TopicWithSubtopics[];
  concepts: ConceptSummary[];
  tags: Tag[];
  questions: QuestionSummary[];
  filters: {
    topicSlug: string;
    conceptSlug: string;
    tagSlug: string;
    difficulty: string;
    progress: string;
  };
};

const DIFFICULTIES: Difficulty[] = ["easy", "medium", "hard", "expert"];
const PROGRESS_FILTERS: Array<{ value: string; label: string }> = [
  { value: "all", label: "All progress" },
  { value: "unsolved", label: "Unsolved" },
  { value: "solved", label: "Solved" },
];

function FilterSelect({
  label,
  value,
  onChange,
  children,
  className,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <label className={cn("grid min-w-0 gap-1 text-sm", className)}>
      <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
        {label}
      </span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-9 w-full rounded-lg border border-[#dfe6e1] bg-white px-3 text-sm text-[#15201c] outline-none focus-visible:border-[#0f766e] focus-visible:ring-3 focus-visible:ring-[#0f766e]/20"
      >
        {children}
      </select>
    </label>
  );
}

export function QuestionBrowser({
  topics,
  concepts,
  tags,
  questions,
  filters,
}: QuestionBrowserProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  const returnTo = useMemo(() => {
    const query = searchParams.toString();
    return query ? `/practice?${query}` : "/practice";
  }, [searchParams]);

  const filteredQuestions = useMemo(() => {
    if (filters.progress === "all") {
      return questions;
    }
    return questions.filter((question) =>
      matchesPracticeProgressFilter(
        question.progress_status,
        filters.progress as "solved" | "unsolved",
      ),
    );
  }, [filters.progress, questions]);

  const questionIds = useMemo(
    () => filteredQuestions.map((question) => question.id),
    [filteredQuestions],
  );

  const conceptOptions = useMemo(() => {
    if (filters.topicSlug === "all") {
      return [];
    }
    const topic = topics.find((item) => item.slug === filters.topicSlug);
    if (topic === undefined) {
      return concepts;
    }
    const allowedSlugs = new Set(topic.subtopics.map((subtopic) => subtopic.slug));
    return concepts.filter((concept) => allowedSlugs.has(concept.slug));
  }, [concepts, filters.topicSlug, topics]);

  function updateFilter(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value === "all" || value === "") {
      params.delete(key);
    } else {
      params.set(key, value);
    }

    if (key === "topic") {
      params.delete("concept");
    }

    const query = params.toString();
    startTransition(() => {
      router.push(query ? `/practice?${query}` : "/practice");
    });
  }

  return (
    <div className="grid gap-6">
      <section
        aria-label="Question filters"
        className="rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
      >
        <div className="grid gap-3 [grid-template-columns:repeat(auto-fit,minmax(180px,1fr))]">
          <FilterSelect
            label="Topic"
            value={filters.topicSlug}
            onChange={(value) => updateFilter("topic", value)}
          >
            <option value="all">All topics</option>
            {topics.map((topic) => (
              <option key={topic.id} value={topic.slug}>
                {topic.name}
              </option>
            ))}
          </FilterSelect>

          <FilterSelect
            label="Concept"
            value={filters.topicSlug === "all" ? "all" : filters.conceptSlug}
            onChange={(value) => updateFilter("concept", value)}
          >
            {filters.topicSlug === "all" ? (
              <option value="all">Select a topic first</option>
            ) : (
              <>
                <option value="all">All concepts in topic</option>
                {conceptOptions.map((concept) => (
                  <option key={concept.id} value={concept.slug}>
                    {concept.name}
                  </option>
                ))}
              </>
            )}
          </FilterSelect>

          <FilterSelect
            label="Difficulty"
            value={filters.difficulty}
            onChange={(value) => updateFilter("difficulty", value)}
          >
            <option value="all">All difficulties</option>
            {DIFFICULTIES.map((difficulty) => (
              <option key={difficulty} value={difficulty}>
                {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
              </option>
            ))}
          </FilterSelect>

          <FilterSelect
            label="Tag"
            value={filters.tagSlug}
            onChange={(value) => updateFilter("tag", value)}
          >
            <option value="all">All tags</option>
            {tags.map((tag) => (
              <option key={tag.id} value={tag.slug}>
                {tag.name}
              </option>
            ))}
          </FilterSelect>

          <FilterSelect
            label="Progress"
            value={filters.progress}
            onChange={(value) => updateFilter("progress", value)}
          >
            {PROGRESS_FILTERS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </FilterSelect>
        </div>

        <p className="mt-3 text-sm text-[#66736e]">
          {filteredQuestions.length} question{filteredQuestions.length === 1 ? "" : "s"} shown
          {isPending ? " · updating…" : ""}
        </p>
      </section>

      {filteredQuestions.length === 0 ? (
        <section className="rounded-lg border border-dashed border-[#dfe6e1] bg-white p-8 text-center">
          <p className="text-sm text-[#66736e]">
            No questions matched these filters. Try clearing a filter or choosing a broader topic.
          </p>
        </section>
      ) : (
        <section aria-label="Question results" className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {filteredQuestions.map((question) => (
            <QuestionCard
              key={question.id}
              question={question}
              returnTo={returnTo}
              questionIds={questionIds}
            />
          ))}
        </section>
      )}
    </div>
  );
}
