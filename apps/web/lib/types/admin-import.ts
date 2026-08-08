export type ResourceSourceType = "url" | "pdf" | "book_note" | "manual" | "generated";

export type ContentStatus = "draft" | "approved" | "rejected";

export type ImportedResource = {
  id: number;
  source_type: ResourceSourceType;
  url: string | null;
  title: string | null;
  author: string | null;
  publisher: string | null;
  license: string | null;
  attribution: string | null;
  summary: string | null;
  raw_text_hash: string | null;
  status: ContentStatus;
  extracted_object_id: number | null;
  extracted_object_ids: number[];
  draft_count: number;
  extraction_method: string | null;
  policy_decision: string | null;
  created_at: string;
  updated_at: string;
};
