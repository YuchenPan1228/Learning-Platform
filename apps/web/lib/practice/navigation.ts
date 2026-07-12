export type PracticeListFilters = {
  topicSlug?: string;
  conceptSlug?: string;
  tagSlug?: string;
  difficulty?: string;
};

export function parsePracticeReturnTo(returnTo: string): PracticeListFilters {
  try {
    const url = new URL(returnTo, "http://localhost");
    if (!url.pathname.startsWith("/practice")) {
      return {};
    }

    const topic = url.searchParams.get("topic");
    const concept = url.searchParams.get("concept");
    const tag = url.searchParams.get("tag");
    const difficulty = url.searchParams.get("difficulty");

    return {
      topicSlug: topic && topic !== "all" ? topic : undefined,
      conceptSlug: concept && concept !== "all" ? concept : undefined,
      tagSlug: tag && tag !== "all" ? tag : undefined,
      difficulty: difficulty && difficulty !== "all" ? difficulty : undefined,
    };
  } catch {
    return {};
  }
}

export function buildPracticeHref(questionId: number, returnTo: string): string {
  return `/practice/${questionId}?returnTo=${encodeURIComponent(returnTo)}`;
}
