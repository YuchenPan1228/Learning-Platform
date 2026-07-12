import { notFound } from "next/navigation";

import { PracticeSession } from "@/components/practice/practice-session";
import { fetchQuestion, fetchQuestions } from "@/lib/api/questions";
import { buildPracticeHref, parsePracticeReturnTo } from "@/lib/practice/navigation";
import type { Difficulty } from "@/lib/types/question";

type PracticeSessionPageProps = {
  params: Promise<{ questionId: string }>;
  searchParams: Promise<{ returnTo?: string }>;
};

const DIFFICULTIES = new Set<Difficulty>(["easy", "medium", "hard", "expert"]);

function parseDifficulty(value: string | undefined): Difficulty | undefined {
  if (value === undefined) {
    return undefined;
  }
  return DIFFICULTIES.has(value as Difficulty) ? (value as Difficulty) : undefined;
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
  const returnTo = query.returnTo && query.returnTo.startsWith("/") ? query.returnTo : "/practice";
  const filters = parsePracticeReturnTo(returnTo);

  const [question, questions] = await Promise.all([
    fetchQuestion(parsedId),
    fetchQuestions({
      topicSlug: filters.topicSlug,
      conceptSlug: filters.conceptSlug,
      tagSlug: filters.tagSlug,
      difficulty: parseDifficulty(filters.difficulty),
      includeProgress: true,
      limit: 100,
    }),
  ]);

  if (question === null) {
    notFound();
  }

  const currentIndex = questions.findIndex((item) => item.id === parsedId);
  const previousQuestionId =
    currentIndex > 0 ? questions[currentIndex - 1]?.id ?? null : null;
  const nextQuestionId =
    currentIndex >= 0 && currentIndex < questions.length - 1
      ? questions[currentIndex + 1]?.id ?? null
      : null;

  return (
    <PracticeSession
      question={question}
      returnTo={returnTo}
      previousHref={
        previousQuestionId === null ? null : buildPracticeHref(previousQuestionId, returnTo)
      }
      nextHref={nextQuestionId === null ? null : buildPracticeHref(nextQuestionId, returnTo)}
      positionLabel={
        currentIndex >= 0 ? `${currentIndex + 1} of ${questions.length}` : undefined
      }
    />
  );
}
