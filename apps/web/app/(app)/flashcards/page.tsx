import { FlashcardReview } from "@/components/flashcards/flashcard-review";
import { fetchFlashcardsPage } from "@/lib/api/flashcards";
import { fetchTopic, fetchTopics } from "@/lib/api/topics";

type FlashcardsPageProps = {
  searchParams: Promise<{
    topic?: string;
  }>;
};

function resolveTopicTitle(
  topics: Awaited<ReturnType<typeof fetchTopics>>,
  topicSlug: string | undefined,
  fetchedName: string | null | undefined,
  fallbackSlug: string | null | undefined,
): string | null {
  if (fetchedName) {
    return fetchedName;
  }
  if (!topicSlug) {
    return null;
  }
  for (const topic of topics) {
    if (topic.slug === topicSlug) {
      return topic.name;
    }
    const subtopic = topic.subtopics.find((item) => item.slug === topicSlug);
    if (subtopic) {
      return subtopic.name;
    }
  }
  return fallbackSlug ?? topicSlug;
}

export default async function FlashcardsPage({ searchParams }: FlashcardsPageProps) {
  const params = await searchParams;
  const topicSlug = params.topic?.trim() || undefined;

  const [duePage, topics, topic] = await Promise.all([
    fetchFlashcardsPage({ limit: 100, dueOnly: true, topicSlug }),
    fetchTopics(),
    topicSlug ? fetchTopic(topicSlug) : Promise.resolve(null),
  ]);

  const usedDueFallback = duePage.total === 0;
  const page = duePage.total > 0 ? duePage : await fetchFlashcardsPage({ limit: 100, topicSlug });

  const topicTitle = resolveTopicTitle(topics, topicSlug, topic?.name, page.items[0]?.topic_slug);

  return (
    <FlashcardReview
      key={topicSlug ?? "all"}
      flashcards={page.items}
      total={page.total}
      topics={topics}
      topicSlug={topicSlug}
      topicTitle={topicTitle}
      usedDueFallback={usedDueFallback}
    />
  );
}
