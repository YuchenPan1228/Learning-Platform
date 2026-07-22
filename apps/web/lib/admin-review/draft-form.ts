import type { ExtractedObjectType, ReviewQueueItem } from "@/lib/types/admin-review";
import type { TopicWithSubtopics } from "@/lib/types/topic";

export type ImportDraftTarget = Extract<ExtractedObjectType, "question" | "flashcard">;

export type DraftFormState = {
  objectType: ImportDraftTarget;
  topicSlug: string;
  subtopicSlug: string;
  title: string;
  body: string;
  shortAnswer: string;
  difficulty: string;
  front: string;
  back: string;
};

function readString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

export function createDraftFormState(item: ReviewQueueItem): DraftFormState {
  const payload = item.payload_json;
  const objectType: ImportDraftTarget = item.object_type === "flashcard" ? "flashcard" : "question";

  return {
    objectType,
    topicSlug: readString(payload.topic_slug),
    subtopicSlug: readString(payload.subtopic_slug),
    title: readString(payload.title),
    body: readString(payload.body) || readString(payload.extracted_text),
    shortAnswer: readString(payload.short_answer) || readString(payload.answer),
    difficulty: readString(payload.difficulty),
    front: readString(payload.front) || readString(payload.title),
    back: readString(payload.back) || readString(payload.body),
  };
}

export function buildDraftPayload(state: DraftFormState): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    topic_slug: state.topicSlug,
  };

  if (state.subtopicSlug.trim()) {
    payload.subtopic_slug = state.subtopicSlug.trim();
  }

  if (state.objectType === "flashcard") {
    payload.front = state.front.trim();
    payload.back = state.back.trim();
    payload.title = state.front.trim();
    payload.extracted_text = state.back.trim();
    return payload;
  }

  payload.title = state.title.trim();
  payload.body = state.body.trim();
  payload.extracted_text = state.body.trim();
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

  if (state.objectType === "flashcard") {
    if (!state.front.trim()) {
      throw new Error("Flashcard front is required.");
    }
    if (!state.back.trim()) {
      throw new Error("Flashcard back is required.");
    }
    return;
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
