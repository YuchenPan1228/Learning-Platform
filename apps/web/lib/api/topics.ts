import { getApiBaseUrl } from "@/lib/api/config";
import type { TopicWithSubtopics } from "@/lib/types/topic";

export async function fetchTopics(): Promise<TopicWithSubtopics[]> {
  const response = await fetch(`${getApiBaseUrl()}/topics`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Topics request failed with status ${response.status}`);
  }

  return response.json() as Promise<TopicWithSubtopics[]>;
}

export async function fetchTopic(slug: string): Promise<TopicWithSubtopics | null> {
  const response = await fetch(`${getApiBaseUrl()}/topics/${slug}`, {
    cache: "no-store",
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Topic request failed with status ${response.status}`);
  }

  return response.json() as Promise<TopicWithSubtopics>;
}
