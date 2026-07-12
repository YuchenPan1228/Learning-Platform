export type QuestionProgressStatus = "not_attempted" | "attempted" | "solved";

export type QuestionProgressItem = {
  question_id: number;
  status: QuestionProgressStatus;
  attempt_count: number;
};
