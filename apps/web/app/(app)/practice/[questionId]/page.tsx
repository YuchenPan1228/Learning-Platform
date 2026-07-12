import { notFound } from "next/navigation";

import { PracticeSession } from "@/components/practice/practice-session";
import { fetchConcepts } from "@/lib/api/concepts";
import { fetchQuestion, fetchQuestionProgress, fetchQuestions } from "@/lib/api/questions";
import {
  buildPracticeNavigationIds,
  filterQuestionsByProgress,
  parsePracticeBrowserFilters,
} from "@/lib/practice/navigation";

type PracticeSessionPageProps = {
  params: Promise<{ questionId: string }>;
  searchParams: Promise<{ returnTo?: string; ids?: string }>;
};

function parseQuestionIds(value: string | undefined): number[] {
  if (!value) {
    return [];
  }
  return value
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((id) => Number.isInteger(id) && id > 0);
}

export default async function PracticeSessionPage({
  params,
  searchParams,
}: PracticeSessionPageProps) {
  const { questionId } = await params;
  const parsedId = Number(questionId);
  if (!Number.isInteger(parsedId) || parsedId <= 0) {
    notFound();
  }

  const query = await searchParams;
  const [question, concepts, progress] = await Promise.all([
    fetchQuestion(parsedId),
    fetchConcepts(),
    fetchQuestionProgress(parsedId).catch(() => null),
  ]);
  if (question === null) {
    notFound();
  }

  const returnTo = query.returnTo && query.returnTo.startsWith("/") ? query.returnTo : "/practice";
  const explicitIds = parseQuestionIds(query.ids);

  let navigationIds =
    explicitIds.length > 0 && explicitIds.includes(parsedId) ? explicitIds : [];

  if (navigationIds.length === 0) {
    const browserFilters = parsePracticeBrowserFilters(returnTo);
    const filteredQuestions = await fetchQuestions({
      topicSlug: browserFilters.topicSlug,
      conceptSlug: browserFilters.conceptSlug,
      tagSlug: browserFilters.tagSlug,
      difficulty: browserFilters.difficulty,
      includeProgress: true,
      limit: 100,
    });
    const visibleQuestions = filterQuestionsByProgress(
      filteredQuestions,
      browserFilters.progress,
    );
    navigationIds = buildPracticeNavigationIds(visibleQuestions, parsedId);
  }

  return (
    <PracticeSession
      question={question}
      returnTo={returnTo}
      questionIds={navigationIds}
      concepts={concepts}
      initialProgress={progress}
    />
  );
}
