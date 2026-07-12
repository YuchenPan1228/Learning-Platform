import type { ConceptSummary } from "@/lib/types/concept";

export type SearchResponse = {
  query: string;
  questions: unknown[];
  concepts: ConceptSummary[];
  total: number;
};
