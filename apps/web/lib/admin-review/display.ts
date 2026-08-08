import type { ReviewQueueItem, SourceQualityStatus } from "@/lib/types/admin-review";

function readString(value: unknown): string | null {
  return typeof value === "string" && value.trim() !== "" ? value.trim() : null;
}

function readObjectArray(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter(
    (item): item is Record<string, unknown> => typeof item === "object" && item !== null,
  );
}

export function formatReviewTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "—";
  }
  return value.toFixed(2);
}

export function formatMatchType(value: string): string {
  return value.replaceAll("_", " ");
}

export function getSourceLabel(item: ReviewQueueItem): string {
  const resource = item.resource;
  if (resource?.title) {
    return resource.title;
  }
  if (resource?.url) {
    return resource.url;
  }
  if (resource?.source_type) {
    return resource.source_type;
  }
  return "Unknown source";
}

export function getExtractedText(item: ReviewQueueItem): string | null {
  const payload = item.payload_json;
  return (
    readString(payload.extracted_text) ??
    readString(payload.text) ??
    readString(payload.body) ??
    readString(payload.note_text) ??
    readString(payload.front)
  );
}

export function getSummary(item: ReviewQueueItem): string | null {
  return readString(item.payload_json.summary) ?? readString(item.resource?.summary);
}

export function getFormulas(item: ReviewQueueItem): Record<string, unknown>[] {
  const payloadFormulas = readObjectArray(item.payload_json.formulas);
  if (payloadFormulas.length > 0) {
    return payloadFormulas;
  }

  if (item.object_type === "formula") {
    const formula = readString(item.payload_json.formula) ?? readString(item.payload_json.latex);
    if (formula) {
      return [{ latex: formula }];
    }
  }

  const conceptFormula = readString(item.payload_json.formula);
  if (conceptFormula) {
    return [{ latex: conceptFormula, concept: readString(item.payload_json.name) }];
  }

  return [];
}

export function getCandidateQuestions(item: ReviewQueueItem): Record<string, unknown>[] {
  const payloadQuestions = readObjectArray(item.payload_json.candidate_questions);
  if (payloadQuestions.length > 0) {
    return payloadQuestions;
  }

  if (item.object_type === "question") {
    const title = readString(item.payload_json.title);
    const body = readString(item.payload_json.body);
    if (title || body) {
      return [
        {
          title,
          body,
          difficulty: item.payload_json.difficulty,
        },
      ];
    }
  }

  return [];
}

export function getLicenseStatus(item: ReviewQueueItem): string {
  if (item.policy?.license_status) {
    return item.policy.license_status;
  }
  return readString(item.resource?.license) ?? "Unknown";
}

export function getQualityScore(item: ReviewQueueItem): number | null {
  return (
    item.quality?.overall_score ??
    item.quality_score ??
    item.resource?.quality_score ??
    null
  );
}

export function getQualityComponentRows(
  quality: SourceQualityStatus | null | undefined,
): { label: string; value: string }[] {
  if (!quality) {
    return [];
  }
  const rows: { label: string; value: string }[] = [];
  const push = (label: string, score: number | null | undefined) => {
    if (score === null || score === undefined) {
      return;
    }
    rows.push({ label, value: formatScore(score) });
  };
  push("Domain reputation", quality.domain_reputation_score);
  push("Content length", quality.content_length_score);
  push("Formula density", quality.formula_density_score);
  push("Code examples", quality.code_example_score);
  push("Educational structure", quality.educational_structure_score);
  push("Human review", quality.human_review_score);
  return rows;
}

export function getProvenanceRows(item: ReviewQueueItem): { label: string; value: string }[] {
  const resource = item.resource;
  const payloadProvenance =
    typeof item.payload_json.provenance === "object" && item.payload_json.provenance !== null
      ? (item.payload_json.provenance as Record<string, unknown>)
      : null;
  const rows: { label: string; value: string }[] = [];

  if (resource?.source_type) {
    rows.push({ label: "Source type", value: resource.source_type });
  }
  if (resource?.url) {
    rows.push({ label: "Source URL/path", value: resource.url });
  }
  if (resource?.title) {
    rows.push({ label: "Source title", value: resource.title });
  }
  if (resource?.author) {
    rows.push({ label: "Author", value: resource.author });
  }
  if (resource?.publisher) {
    rows.push({ label: "Publisher", value: resource.publisher });
  }
  if (resource?.license) {
    rows.push({ label: "License", value: resource.license });
  }
  if (resource?.attribution) {
    rows.push({ label: "Attribution", value: resource.attribution });
  }
  if (item.resource_id !== null) {
    rows.push({ label: "Resource ID", value: String(item.resource_id) });
  }
  if (item.topic_job_id !== null) {
    rows.push({ label: "Topic job ID", value: String(item.topic_job_id) });
  }
  if (item.duplicate_cluster_id !== null) {
    rows.push({ label: "Duplicate cluster", value: String(item.duplicate_cluster_id) });
  }
  if (item.extraction_method) {
    rows.push({ label: "Extraction method", value: item.extraction_method });
  }
  if (item.model_version) {
    rows.push({ label: "Model version", value: item.model_version });
  }
  if (payloadProvenance) {
    for (const [key, value] of Object.entries(payloadProvenance)) {
      if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
        rows.push({ label: `Payload · ${key}`, value: String(value) });
      }
    }
  }
  rows.push({ label: "Created", value: formatReviewTimestamp(item.created_at) });
  rows.push({ label: "Updated", value: formatReviewTimestamp(item.updated_at) });

  return rows;
}

export function getReviewItemTitle(item: ReviewQueueItem): string {
  const payload = item.payload_json;
  return (
    readString(payload.title) ??
    readString(payload.name) ??
    readString(payload.front) ??
    `${item.object_type} draft #${item.id}`
  );
}

export function isPublishedReviewItem(item: ReviewQueueItem): boolean {
  const published = item.payload_json.published;
  return typeof published === "object" && published !== null && "id" in published;
}
