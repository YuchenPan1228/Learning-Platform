"use client";

import { useMemo, useState } from "react";

import { ConceptSearchPanel } from "@/components/topics/concept-search-panel";
import { TopicCard } from "@/components/topics/topic-card";
import { Input } from "@/components/ui/input";
import type { TopicWithSubtopics } from "@/lib/types/topic";

type TopicLibraryProps = {
  topics: TopicWithSubtopics[];
  masteryBySlug: Record<string, number>;
};

function matchesTopicQuery(topic: TopicWithSubtopics, query: string): boolean {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return true;
  }

  const haystack = [
    topic.name,
    topic.slug,
    topic.description ?? "",
    ...topic.subtopics.map((subtopic) => subtopic.name),
    ...topic.subtopics.map((subtopic) => subtopic.slug),
  ]
    .join(" ")
    .toLowerCase();

  return haystack.includes(normalized);
}

export function TopicLibrary({ topics, masteryBySlug }: TopicLibraryProps) {
  const [query, setQuery] = useState("");
  const [selectedTopicSlug, setSelectedTopicSlug] = useState<string>("all");

  const trimmedQuery = query.trim();
  const shouldSearchConcepts = trimmedQuery.length >= 2;

  const filteredTopics = useMemo(() => {
    return topics.filter((topic) => {
      if (selectedTopicSlug !== "all" && topic.slug !== selectedTopicSlug) {
        return false;
      }
      return matchesTopicQuery(topic, query);
    });
  }, [query, selectedTopicSlug, topics]);

  const conceptSearchTopicSlug = selectedTopicSlug === "all" ? undefined : selectedTopicSlug;

  return (
    <div className="grid gap-6">
      <section
        aria-label="Topic library filters"
        className="rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
      >
        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_220px]">
          <Input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search topics and subtopics..."
            aria-label="Search topics and subtopics"
          />

          <label className="grid gap-1 text-sm">
            <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              Filter by topic
            </span>
            <select
              value={selectedTopicSlug}
              onChange={(event) => setSelectedTopicSlug(event.target.value)}
              className="h-9 rounded-lg border border-[#dfe6e1] bg-white px-3 text-sm text-[#15201c] outline-none focus-visible:border-[#0f766e] focus-visible:ring-3 focus-visible:ring-[#0f766e]/20"
            >
              <option value="all">All topics</option>
              {topics.map((topic) => (
                <option key={topic.id} value={topic.slug}>
                  {topic.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <p className="mt-3 text-sm text-[#66736e]">
          {filteredTopics.length} topic{filteredTopics.length === 1 ? "" : "s"} shown
          {shouldSearchConcepts ? " · concept search active" : ""}
        </p>
      </section>

      {shouldSearchConcepts ? (
        <ConceptSearchPanel
          key={`${trimmedQuery}:${conceptSearchTopicSlug ?? "all"}`}
          query={trimmedQuery}
          topicSlug={conceptSearchTopicSlug}
        />
      ) : null}

      {filteredTopics.length === 0 ? (
        <section className="rounded-lg border border-dashed border-[#dfe6e1] bg-white p-8 text-center">
          <p className="text-sm text-[#66736e]">
            No topics matched your filters. Try clearing the topic filter or broadening your search.
          </p>
        </section>
      ) : (
        <section aria-label="Topic cards" className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredTopics.map((topic) => (
            <TopicCard key={topic.id} topic={topic} masteryScore={masteryBySlug[topic.slug] ?? 0} />
          ))}
        </section>
      )}
    </div>
  );
}
