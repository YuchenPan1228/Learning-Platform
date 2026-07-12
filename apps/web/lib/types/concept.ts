export type ConceptSummary = {
  id: number;
  slug: string;
  name: string;
  topic_id: number;
  topic_slug: string;
};

export type ConceptRelationshipType = "requires" | "related_to" | "used_in";

export type ConceptNeighbor = {
  slug: string;
  name: string;
  relationship_type: ConceptRelationshipType;
  direction: "incoming" | "outgoing";
};

export type ConceptDetail = ConceptSummary & {
  definition: string | null;
  formula: string | null;
  intuition: string | null;
  common_mistakes: string | null;
  interview_tips: string | null;
  prerequisites: string | null;
  neighbors: ConceptNeighbor[];
};
