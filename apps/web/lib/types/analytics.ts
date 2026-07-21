export type WeakConcept = {
  concept_id: number;
  slug: string;
  name: string;
  topic_id: number;
  topic_slug: string;
  mastery_score: number;
  attempts_count: number;
};

export type AttemptHistoryItem = {
  id: number;
  question_id: number;
  question_title: string;
  topic_id: number;
  topic_slug: string;
  is_correct: boolean | null;
  score: number | null;
  time_spent_seconds: number;
  created_at: string;
};

export type SearchMiss = {
  id: number;
  query: string;
  topic_slug: string | null;
  types: string[];
  created_at: string;
};

export type LearningAnalytics = {
  user_id: string;
  weak_concepts: WeakConcept[];
  attempt_history: AttemptHistoryItem[];
  review_due_count: number;
  search_misses: SearchMiss[];
};
