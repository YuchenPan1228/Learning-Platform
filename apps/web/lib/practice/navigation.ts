import type { Difficulty, QuestionSummary } from "@/lib/types/question";
import {
  matchesPracticeProgressFilter,
  parsePracticeProgressFilter,
  type PracticeProgressFilter,
} from "@/lib/practice/progress-display";

const DIFFICULTIES = new Set<Difficulty>(["easy", "medium", "hard", "expert"]);

export type PracticeBrowserFilters = {
  topicSlug?: string;
  conceptSlug?: string;
  tagSlug?: string;
  difficulty?: Difficulty;
  progress?: PracticeProgressFilter;
};

export function parsePracticeBrowserFilters(returnTo: string): PracticeBrowserFilters {
  try {
    const url = new URL(returnTo, "http://localhost");
    if (url.pathname !== "/practice") {
      return {};
    }

    const topic = url.searchParams.get("topic");
    const concept = url.searchParams.get("concept");
    const tag = url.searchParams.get("tag");
    const difficulty = url.searchParams.get("difficulty");
    const progress = url.searchParams.get("progress");

    const filters: PracticeBrowserFilters = {};

    if (topic && topic !== "all") {
      filters.topicSlug = topic;
    }
    if (concept && concept !== "all") {
      filters.conceptSlug = concept;
    }
    if (tag && tag !== "all") {
      filters.tagSlug = tag;
    }
    if (difficulty && DIFFICULTIES.has(difficulty as Difficulty)) {
      filters.difficulty = difficulty as Difficulty;
    }
    if (progress) {
      filters.progress = parsePracticeProgressFilter(progress);
    }

    return filters;
  } catch {
    return {};
  }
}

export function filterQuestionsByProgress(
  questions: QuestionSummary[],
  progress: PracticeProgressFilter | undefined,
): QuestionSummary[] {
  if (!progress || progress === "all") {
    return questions;
  }
  return questions.filter((question) =>
    matchesPracticeProgressFilter(question.progress_status, progress),
  );
}

export function buildPracticeNavigationIds(
  questions: QuestionSummary[],
  currentQuestionId: number,
): number[] {
  const ids = questions.map((question) => question.id);
  if (ids.length === 0) {
    return [currentQuestionId];
  }
  if (ids.includes(currentQuestionId)) {
    return ids;
  }
  return [...ids, currentQuestionId];
}
