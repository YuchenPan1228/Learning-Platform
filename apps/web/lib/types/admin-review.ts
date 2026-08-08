import type { ContentStatus, ResourceSourceType } from "@/lib/types/admin-import";

export type ExtractedObjectType = "concept" | "formula" | "example" | "question" | "flashcard";

export type DuplicateMatchType = "exact_raw" | "exact_normalized" | "near_normalized";

export type SourcePolicyDecision = "allow" | "review" | "deny";
export type AllowlistStatus = "allowed" | "denied" | "not_configured" | "not_applicable";
export type RobotsStatus = "allowed" | "disallowed" | "unknown" | "not_applicable";
export type LicenseStatus = "permissive" | "restrictive" | "unknown" | "missing";

export type ResourceProvenance = {
  id: number;
  source_type: ResourceSourceType;
  url: string | null;
  title: string | null;
  author: string | null;
  publisher: string | null;
  license: string | null;
  attribution: string | null;
  summary: string | null;
  quality_score: number | null;
  domain_reputation_score?: number | null;
  content_length_score?: number | null;
  formula_density_score?: number | null;
  code_example_score?: number | null;
  educational_structure_score?: number | null;
  human_review_score?: number | null;
  status: ContentStatus;
};

export type SourcePolicyStatus = {
  decision: SourcePolicyDecision;
  allowlist_status: AllowlistStatus;
  robots_status: RobotsStatus;
  license_status: LicenseStatus;
  attribution_required: boolean;
  attribution_present: boolean;
  reasons: string[];
  host: string | null;
};

export type SourceQualityStatus = {
  draft_quality_score: number | null;
  resource_quality_score: number | null;
  overall_score: number | null;
  domain_reputation_score: number | null;
  content_length_score: number | null;
  formula_density_score: number | null;
  code_example_score: number | null;
  educational_structure_score: number | null;
  human_review_score: number | null;
};

export type ExtractedDuplicateMatch = {
  source: string;
  object_id: number;
  title: string;
  match_type: DuplicateMatchType;
  similarity_score: number | null;
  status: ContentStatus | null;
  confidence_score: number | null;
};

export type CanonicalSuggestion = {
  kind: string;
  object_id: number;
  title: string;
  reason: string;
};

export type ExtractedDedupeResult = {
  extracted_object_id: number;
  object_type: ExtractedObjectType;
  raw_text_hash: string;
  normalized_text_hash: string;
  normalized_text: string;
  matches: ExtractedDuplicateMatch[];
  suggested_canonical: CanonicalSuggestion;
};

export type ReviewQueueItem = {
  id: number;
  resource_id: number | null;
  topic_job_id: number | null;
  object_type: ExtractedObjectType;
  payload_json: Record<string, unknown>;
  confidence_score: number | null;
  quality_score: number | null;
  duplicate_cluster_id: number | null;
  status: ContentStatus;
  extraction_method: string | null;
  model_version: string | null;
  created_at: string;
  updated_at: string;
  resource: ResourceProvenance | null;
  policy?: SourcePolicyStatus | null;
  quality?: SourceQualityStatus | null;
  duplicates?: ExtractedDedupeResult | null;
};

export type ReviewQueueResponse = {
  items: ReviewQueueItem[];
};

export type ReviewQueueEditInput = {
  payloadJson?: Record<string, unknown>;
  objectType?: Extract<ExtractedObjectType, "question" | "flashcard">;
  qualityScore?: number | null;
  confidenceScore?: number | null;
};

export type ReviewQueueStatus = "draft" | "approved" | "rejected";

export type PublishedObjectRef = {
  kind: "concept" | "question" | "flashcard";
  id: number;
};

export type PublishDuplicateMatch = {
  question_id: number;
  title: string;
  match_type: string;
  similarity_score: number | null;
};

export type PublishReviewResult = {
  extracted_object_id: number;
  object_type: ExtractedObjectType;
  published: PublishedObjectRef;
  duplicate_warnings: PublishDuplicateMatch[];
};
