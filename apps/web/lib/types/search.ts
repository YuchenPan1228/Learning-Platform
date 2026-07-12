import type { ConceptSummary } from "@/lib/types/concept";
import type { QuestionSummary } from "@/lib/types/question";

export type SearchResponse = {
  query: string;
  questions: QuestionSummary[];
  concepts: ConceptSummary[];
  total: number;
};
