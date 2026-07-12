import { notFound } from "next/navigation";

import { MentalMathModes } from "@/components/mental-math/mental-math-modes";
import { fetchQuestion, fetchQuestions } from "@/lib/api/questions";
import { fetchTopic } from "@/lib/api/topics";

export default async function MentalMathPage() {
  const [topic, summaries] = await Promise.all([
    fetchTopic("mental-math"),
    fetchQuestions({ topicSlug: "mental-math", limit: 100 }),
  ]);

  if (topic === null) {
    notFound();
  }

  const questions = (
    await Promise.all(summaries.map((summary) => fetchQuestion(summary.id)))
  ).filter((question) => question !== null);

  return <MentalMathModes categories={topic.subtopics} questions={questions} />;
}
