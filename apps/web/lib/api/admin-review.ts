import { getApiBaseUrl } from "@/lib/api/config";
import type {
  PublishReviewResult,
  ReviewQueueEditInput,
  ReviewQueueItem,
  ReviewQueueResponse,
  ReviewQueueStatus,
} from "@/lib/types/admin-review";

async function parseError(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
    if (
      typeof payload.detail === "object" &&
      payload.detail !== null &&
      "message" in payload.detail &&
      typeof payload.detail.message === "string"
    ) {
      const detail = payload.detail as {
        message: string;
        matches?: Array<{ title?: string; match_type?: string }>;
      };
      const matchSummary = (detail.matches ?? [])
        .map((match) => {
          const title = match.title ?? "untitled";
          const matchType = match.match_type ?? "unknown";
          return `${title} (${matchType})`;
        })
        .join("; ");
      return matchSummary ? `${detail.message} Matches: ${matchSummary}` : detail.message;
    }
  } catch {
    // Keep fallback when body is not JSON.
  }
  return fallback;
}

export async function fetchReviewQueue(status: ReviewQueueStatus = "draft") {
  const response = await fetch(`${getApiBaseUrl()}/admin/review?status=${status}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Review queue request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<ReviewQueueResponse>;
}

export async function approveReviewItem(extractedObjectId: number): Promise<ReviewQueueItem> {
  const response = await fetch(`${getApiBaseUrl()}/admin/review/${extractedObjectId}/approve`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Approve request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<ReviewQueueItem>;
}

export async function rejectReviewItem(extractedObjectId: number): Promise<ReviewQueueItem> {
  const response = await fetch(`${getApiBaseUrl()}/admin/review/${extractedObjectId}/reject`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Reject request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<ReviewQueueItem>;
}

export async function editReviewItem(
  extractedObjectId: number,
  input: ReviewQueueEditInput,
): Promise<ReviewQueueItem> {
  const response = await fetch(`${getApiBaseUrl()}/admin/review/${extractedObjectId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      payload_json: input.payloadJson,
      quality_score: input.qualityScore,
      confidence_score: input.confidenceScore,
    }),
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Edit request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<ReviewQueueItem>;
}

export async function publishReviewItem(extractedObjectId: number): Promise<PublishReviewResult> {
  const response = await fetch(`${getApiBaseUrl()}/admin/review/${extractedObjectId}/publish`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(
      await parseError(response, `Publish request failed with status ${response.status}`),
    );
  }

  return response.json() as Promise<PublishReviewResult>;
}
