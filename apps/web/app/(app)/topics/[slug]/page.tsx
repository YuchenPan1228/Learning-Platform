import { notFound } from "next/navigation";

import { TopicDetailView } from "@/components/topics/topic-detail-view";
import { fetchConcepts } from "@/lib/api/concepts";
import { fetchDashboard } from "@/lib/api/dashboard";
import { fetchTopic } from "@/lib/api/topics";
import type { ConceptSummary } from "@/lib/types/concept";

type TopicDetailPageProps = {
  params: Promise<{ slug: string }>;
};

function conceptsBySlug(concepts: ConceptSummary[]): Record<string, ConceptSummary> {
  return Object.fromEntries(concepts.map((concept) => [concept.slug, concept]));
}

export default async function TopicDetailPage({ params }: TopicDetailPageProps) {
  const { slug } = await params;
  const [topic, dashboard, concepts] = await Promise.all([
    fetchTopic(slug),
    fetchDashboard(),
    fetchConcepts(slug),
  ]);

  if (topic === null) {
    notFound();
  }

  const masteryScore =
    dashboard.topic_mastery.find((entry) => entry.slug === slug)?.mastery_score ?? 0;

  return (
    <TopicDetailView
      topic={topic}
      masteryScore={masteryScore}
      conceptsBySlug={conceptsBySlug(concepts)}
    />
  );
}
