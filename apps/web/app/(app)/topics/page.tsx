import { TopicLibrary } from "@/components/topics/topic-library";
import { fetchDashboard } from "@/lib/api/dashboard";
import { fetchTopics } from "@/lib/api/topics";

function buildMasteryMap(
  masteryEntries: Array<{ slug: string; mastery_score: number }>,
): Record<string, number> {
  return Object.fromEntries(masteryEntries.map((entry) => [entry.slug, entry.mastery_score]));
}

export default async function TopicsPage() {
  const [topics, dashboard] = await Promise.all([fetchTopics(), fetchDashboard()]);
  const masteryBySlug = buildMasteryMap(dashboard.topic_mastery);

  return <TopicLibrary topics={topics} masteryBySlug={masteryBySlug} />;
}
