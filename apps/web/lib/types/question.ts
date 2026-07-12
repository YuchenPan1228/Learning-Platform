export type TagCategory = "concept" | "company" | "format" | "skill" | "formula";

export type Tag = {
  id: number;
  slug: string;
  name: string;
  category: TagCategory;
};

export type Difficulty = "easy" | "medium" | "hard" | "expert";

export type QuestionProgressStatus = "not_attempted" | "attempted" | "solved";

export type QuestionSummary = {
  id: number;
  title: string;
  difficulty: Difficulty;
  topic_id: number;
  topic_slug: string;
  subtopic_id: number | null;
  subtopic_slug: string | null;
  estimated_time_seconds: number | null;
  company_hint: string | null;
  status: string;
  tags: Tag[];
  progress_status?: QuestionProgressStatus | null;
  attempt_count?: number | null;
};

export type QuestionDetail = QuestionSummary & {
  body: string;
  canonical_solution: string | null;
  short_answer: string | null;
  expected_solution_pattern: string | null;
  common_mistakes: string[] | null;
  prerequisites: string[] | null;
  source_attribution: string | null;
};
