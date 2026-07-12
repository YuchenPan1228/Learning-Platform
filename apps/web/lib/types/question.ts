export type TagCategory = "concept" | "company" | "format" | "skill" | "formula";

export type Tag = {
  id: number;
  slug: string;
  name: string;
  category: TagCategory;
};

export type Difficulty = "easy" | "medium" | "hard" | "expert";

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
};
