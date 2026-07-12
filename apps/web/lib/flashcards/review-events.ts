import type { FlashcardReviewEvent } from "@/lib/types/flashcard";

const STORAGE_KEY = "quant-prep:flashcard-review-events";
const REVIEW_EVENTS_CHANGED = "quant-prep:flashcard-review-events-changed";

type StoredReviewEvents = {
  events: FlashcardReviewEvent[];
};

function readStorage(): StoredReviewEvents {
  if (typeof window === "undefined") {
    return { events: [] };
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { events: [] };
  }

  try {
    const parsed = JSON.parse(raw) as StoredReviewEvents;
    if (!Array.isArray(parsed.events)) {
      return { events: [] };
    }
    return parsed;
  } catch {
    return { events: [] };
  }
}

function writeStorage(data: StoredReviewEvents): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  window.dispatchEvent(new Event(REVIEW_EVENTS_CHANGED));
}

export function subscribeToFlashcardReviewEvents(onStoreChange: () => void): () => void {
  window.addEventListener(REVIEW_EVENTS_CHANGED, onStoreChange);
  return () => window.removeEventListener(REVIEW_EVENTS_CHANGED, onStoreChange);
}

export function getFlashcardReviewEventCount(): number {
  return readStorage().events.length;
}

export function loadFlashcardReviewEvents(): FlashcardReviewEvent[] {
  return readStorage().events;
}

export function appendFlashcardReviewEvent(event: FlashcardReviewEvent): FlashcardReviewEvent[] {
  const data = readStorage();
  const events = [...data.events, event];
  writeStorage({ events });
  return events;
}

export function clearFlashcardReviewEvents(): void {
  window.localStorage.removeItem(STORAGE_KEY);
}
