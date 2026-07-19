import type { Difficulty } from "@/lib/types/question";

export type AIHintsResult = {
  question_id: number;
  cache_hit: boolean;
  hints: string[];
};

export type AIExplanationResult = {
  question_id: number;
  cache_hit: boolean;
  explanation: string;
};

export type SimilarQuestionResult = {
  source_question_id: number;
  draft_question_id: number;
  generated_from_id: number;
  cache_hit: boolean;
  title: string;
  body: string;
  short_answer: string | null;
  canonical_solution: string | null;
  difficulty: Difficulty;
  common_mistakes: string[] | null;
  expected_solution_pattern: string | null;
  estimated_time_seconds: number | null;
  status: string;
  topic_id: number;
  subtopic_id: number | null;
};
