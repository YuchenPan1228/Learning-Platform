import type { ExtractedObjectType, ReviewQueueItem } from "@/lib/types/admin-review";
import type { TopicWithSubtopics } from "@/lib/types/topic";

export type ImportDraftTarget = Extract<ExtractedObjectType, "question">;

export type DraftFormState = {
  objectType: ImportDraftTarget;
  topicSlug: string;
  subtopicSlug: string;
  title: string;
  body: string;
  shortAnswer: string;
  difficulty: string;
};

function readString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

export function createDraftFormState(item: ReviewQueueItem): DraftFormState {
  const payload = item.payload_json;

  return {
    objectType: "question",
    topicSlug: readString(payload.topic_slug),
    subtopicSlug: readString(payload.subtopic_slug),
    title: readString(payload.title) || readString(payload.front),
    body:
      readString(payload.body) ||
      readString(payload.extracted_text) ||
      readString(payload.back),
    shortAnswer: readString(payload.short_answer) || readString(payload.answer),
    difficulty: readString(payload.difficulty),
  };
}

export function buildDraftPayload(state: DraftFormState): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    topic_slug: state.topicSlug,
    title: state.title.trim(),
    body: state.body.trim(),
    extracted_text: state.body.trim(),
  };

  if (state.subtopicSlug.trim()) {
    payload.subtopic_slug = state.subtopicSlug.trim();
  }
  if (state.shortAnswer.trim()) {
    payload.short_answer = state.shortAnswer.trim();
  }
  if (state.difficulty.trim()) {
    payload.difficulty = state.difficulty.trim();
  }
  return payload;
}

export function validateDraftFormState(state: DraftFormState): void {
  if (!state.topicSlug.trim()) {
    throw new Error("Topic is required.");
  }
  if (!state.title.trim()) {
    throw new Error("Question title is required.");
  }
  if (!state.body.trim()) {
    throw new Error("Question body is required.");
  }
}

export function getSubtopicsForTopic(
  topics: TopicWithSubtopics[],
  topicSlug: string,
): TopicWithSubtopics["subtopics"] {
  return topics.find((topic) => topic.slug === topicSlug)?.subtopics ?? [];
}
