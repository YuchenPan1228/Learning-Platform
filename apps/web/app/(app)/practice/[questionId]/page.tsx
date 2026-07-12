import { notFound } from "next/navigation";

import { PracticeSession } from "@/components/practice/practice-session";
import { fetchQuestion } from "@/lib/api/questions";

type PracticeSessionPageProps = {
  params: Promise<{ questionId: string }>;
  searchParams: Promise<{ returnTo?: string }>;
};

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
  const question = await fetchQuestion(parsedId);
  if (question === null) {
    notFound();
  }

  const returnTo = query.returnTo && query.returnTo.startsWith("/") ? query.returnTo : "/practice";

  return <PracticeSession question={question} returnTo={returnTo} />;
}
