import { notFound } from "next/navigation";

import { ConceptDetailView } from "@/components/concepts/concept-detail-view";
import { fetchConcept } from "@/lib/api/concepts";
import { fetchQuestions } from "@/lib/api/questions";
import { fetchTopics } from "@/lib/api/topics";

type ConceptPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ConceptPage({ params }: ConceptPageProps) {
  const { slug } = await params;
  const [concept, practiceQuestions, topics] = await Promise.all([
    fetchConcept(slug),
    fetchQuestions({ conceptSlug: slug, includeProgress: true, limit: 100 }),
    fetchTopics(),
  ]);

  if (concept === null) {
    notFound();
  }

  const rootTopic = topics.find((topic) =>
    topic.subtopics.some((subtopic) => subtopic.slug === concept.topic_slug),
  );
  const practiceHref = rootTopic
    ? `/practice?topic=${rootTopic.slug}&concept=${concept.slug}`
    : `/practice?concept=${concept.slug}`;

  return (
    <ConceptDetailView
      concept={concept}
      practiceQuestionCount={practiceQuestions.length}
      practiceHref={practiceHref}
    />
  );
}
