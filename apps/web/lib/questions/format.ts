import type { Difficulty } from "@/lib/types/question";

export function formatEstimatedTime(seconds: number | null): string {
  if (seconds === null || seconds <= 0) {
    return "Time n/a";
  }

  if (seconds < 60) {
    return `${seconds} sec`;
  }

  const minutes = Math.round(seconds / 60);
  return `${minutes} min`;
}

export function formatDifficulty(difficulty: Difficulty): string {
  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
}
