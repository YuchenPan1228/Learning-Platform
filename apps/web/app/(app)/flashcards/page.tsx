import { FlashcardReview } from "@/components/flashcards/flashcard-review";
import { fetchFlashcards } from "@/lib/api/flashcards";
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

  const [dueFlashcards, topics, topic] = await Promise.all([
    fetchFlashcards({ limit: 100, dueOnly: true, topicSlug }),
    fetchTopics(),
    topicSlug ? fetchTopic(topicSlug) : Promise.resolve(null),
  ]);

  const flashcards =
    dueFlashcards.length > 0
      ? dueFlashcards
      : await fetchFlashcards({ limit: 100, topicSlug });

  const topicTitle = resolveTopicTitle(
    topics,
    topicSlug,
    topic?.name,
    flashcards[0]?.topic_slug,
  );

  const usedDueFallback = dueFlashcards.length === 0 && flashcards.length > 0;

  return (
    <FlashcardReview
      key={topicSlug ?? "all"}
      flashcards={flashcards}
      topics={topics}
      topicSlug={topicSlug}
      topicTitle={topicTitle}
      usedDueFallback={usedDueFallback}
    />
  );
}
