import type { QuestionProgressStatus } from "@/lib/types/question";

export type PracticeProgressFilter = "all" | "solved" | "unsolved";

export function isQuestionSolved(status: QuestionProgressStatus | null | undefined): boolean {
  return status === "solved";
}

export function formatQuestionProgressLabel(
  status: QuestionProgressStatus | null | undefined,
): "Solved" | "Unsolved" {
  return isQuestionSolved(status) ? "Solved" : "Unsolved";
}

export function parsePracticeProgressFilter(value: string | undefined): PracticeProgressFilter {
  if (value === "solved") {
    return "solved";
  }
  if (value === "unsolved" || value === "not_attempted" || value === "attempted") {
    return "unsolved";
  }
  return "all";
}

export function matchesPracticeProgressFilter(
  status: QuestionProgressStatus | null | undefined,
  filter: PracticeProgressFilter,
): boolean {
  if (filter === "all") {
    return true;
  }
  if (filter === "solved") {
    return isQuestionSolved(status);
  }
  return !isQuestionSolved(status);
}

export const PROGRESS_BADGE_STYLES = {
  solved: "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]",
  unsolved: "border-[#dfe6e1] bg-[#fbfcfa] text-[#66736e]",
} as const;
