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

export type DashboardData = {
  user_id: string;
  topic_mastery: TopicMastery[];
  subtopic_mastery: TopicMastery[];
  weak_prerequisites: WeakPrerequisite[];
};
