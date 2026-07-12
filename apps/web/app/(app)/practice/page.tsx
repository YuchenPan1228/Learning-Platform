import { Suspense } from "react";

import { QuestionBrowser } from "@/components/practice/question-browser";
import { fetchConcepts } from "@/lib/api/concepts";
import { fetchQuestions } from "@/lib/api/questions";
import { fetchTags } from "@/lib/api/tags";
import { fetchTopics } from "@/lib/api/topics";
import type { Difficulty } from "@/lib/types/question";

type PracticePageProps = {
  searchParams: Promise<{
    topic?: string;
    concept?: string;
    tag?: string;
    difficulty?: string;
    progress?: string;
  }>;
};

const DIFFICULTIES = new Set<Difficulty>(["easy", "medium", "hard", "expert"]);
const PROGRESS_STATUSES = new Set(["not_attempted", "attempted", "solved"]);

function parseDifficulty(value: string | undefined): Difficulty | undefined {
  if (value === undefined) {
    return undefined;
  }
  return DIFFICULTIES.has(value as Difficulty) ? (value as Difficulty) : undefined;
}

export default async function PracticePage({ searchParams }: PracticePageProps) {
  const params = await searchParams;
  const topicSlug = params.topic && params.topic !== "all" ? params.topic : undefined;
  const conceptSlug = params.concept && params.concept !== "all" ? params.concept : undefined;
  const tagSlug = params.tag && params.tag !== "all" ? params.tag : undefined;
  const difficulty = parseDifficulty(params.difficulty);
  const progress =
    params.progress && PROGRESS_STATUSES.has(params.progress) ? params.progress : "all";

  const [topics, concepts, tags, questions] = await Promise.all([
    fetchTopics(),
    fetchConcepts(topicSlug),
    fetchTags(),
    fetchQuestions({
      topicSlug,
      conceptSlug,
      tagSlug,
      difficulty,
      limit: 100,
    }),
  ]);

  return (
    <Suspense fallback={<p className="text-sm text-[#66736e]">Loading question browser…</p>}>
      <QuestionBrowser
        topics={topics}
        concepts={concepts}
        tags={tags}
        questions={questions}
        filters={{
          topicSlug: topicSlug ?? "all",
          conceptSlug: conceptSlug ?? "all",
          tagSlug: tagSlug ?? "all",
          difficulty: difficulty ?? "all",
          progress,
        }}
      />
    </Suspense>
  );
}
