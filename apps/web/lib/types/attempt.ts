export type AttemptResult = {
  id: number;
  question_id: number;
  topic_id: number;
  answer: string;
  supported: boolean;
  is_correct: boolean | null;
  score: number | null;
  feedback: string | null;
  time_spent_seconds: number;
  created_at: string;
};
