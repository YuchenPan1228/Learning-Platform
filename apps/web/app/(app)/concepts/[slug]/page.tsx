import { notFound } from "next/navigation";

import { ConceptDetailView } from "@/components/concepts/concept-detail-view";
import { fetchConcept } from "@/lib/api/concepts";
import { fetchQuestions } from "@/lib/api/questions";

type ConceptPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ConceptPage({ params }: ConceptPageProps) {
  const { slug } = await params;
  const [concept, practiceQuestions] = await Promise.all([
    fetchConcept(slug),
    fetchQuestions({ conceptSlug: slug, includeProgress: true, limit: 100 }),
  ]);

  if (concept === null) {
    notFound();
  }

  return (
    <ConceptDetailView concept={concept} practiceQuestionCount={practiceQuestions.length} />
  );
}
