import { getApiBaseUrl } from "@/lib/api/config";
import type {
  ReviewQueueEditInput,
  ReviewQueueItem,
  ReviewQueueResponse,
} from "@/lib/types/admin-review";

async function parseError(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Keep fallback when body is not JSON.
  }
  return fallback;
}

export async function fetchReviewQueue(status: "draft" | "approved" | "rejected" = "draft") {
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
