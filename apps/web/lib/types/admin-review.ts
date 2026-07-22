import type { ContentStatus, ResourceSourceType } from "@/lib/types/admin-import";

export type ExtractedObjectType = "concept" | "formula" | "example" | "question" | "flashcard";

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
  status: ContentStatus;
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
};

export type ReviewQueueResponse = {
  items: ReviewQueueItem[];
};

export type ReviewQueueEditInput = {
  payloadJson?: Record<string, unknown>;
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
