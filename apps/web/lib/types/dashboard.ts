export type TopicMastery = {
  topic_id: number;
  slug: string;
  name: string;
  mastery_score: number;
  attempts_count: number;
  solved_count: number;
  total_questions: number;
};

export type WeakPrerequisite = {
  concept_slug: string;
  concept_name: string;
  prerequisite_slug: string;
  prerequisite_name: string;
  prerequisite_mastery_score: number;
};

export type StudyPlanItemKind =
  "flashcard_review" | "prerequisite_repair" | "learning_path" | "practice";

export type StudyPlanItem = {
  kind: StudyPlanItemKind;
  title: string;
  description: string;
  duration_minutes: number;
  href: string | null;
  topic_slug: string | null;
  concept_slug: string | null;
};

export type DailyStudyPlan = {
  user_id: string;
  generated_at: string;
  target_minutes: number;
  total_minutes: number;
  summary: string;
  detail: string;
  items: StudyPlanItem[];
};

export type DashboardData = {
  user_id: string;
  topic_mastery: TopicMastery[];
  subtopic_mastery: TopicMastery[];
  weak_prerequisites: WeakPrerequisite[];
  daily_plan: DailyStudyPlan;
};
