import { getApiBaseUrl } from "@/lib/api/config";
import type { ImportedResource } from "@/lib/types/admin-import";
import type { ImportDraftTarget } from "@/lib/admin-review/draft-form";

type SharedImportDraftInput = {
  objectType?: ImportDraftTarget;
  topicSlug: string;
  subtopicSlug?: string;
};

export type UrlImportInput = SharedImportDraftInput & {
  url: string;
  title?: string;
};

export type NoteImportInput = SharedImportDraftInput & {
  noteText: string;
  title?: string;
};

export type QuestionImportInput = {
  title: string;
  body: string;
  shortAnswer?: string;
  topicSlug: string;
  subtopicSlug?: string;
  objectType: "question";
};

export type PdfImportInput = SharedImportDraftInput & {
  file: File;
  title?: string;
  summary?: string;
};

async function parseImportError(response: Response): Promise<string> {
  let detail = `Import failed with status ${response.status}`;
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      detail = payload.detail;
    }
  } catch {
    // Keep the status-based message when the body is not JSON.
  }
  return detail;
}

async function postImport(path: string, body: Record<string, unknown>): Promise<ImportedResource> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(await parseImportError(response));
  }

  return response.json() as Promise<ImportedResource>;
}

function draftFields(input: SharedImportDraftInput): Record<string, unknown> {
  return {
    object_type: input.objectType ?? "question",
    topic_slug: input.topicSlug,
    subtopic_slug: input.subtopicSlug,
  };
}

export function importUrlResource(input: UrlImportInput): Promise<ImportedResource> {
  return postImport("/admin/import/url", {
    url: input.url,
    title: input.title,
    ...draftFields(input),
  });
}

export function importNoteResource(input: NoteImportInput): Promise<ImportedResource> {
  return postImport("/admin/import/note", {
    note_text: input.noteText,
    title: input.title,
    source_type: "manual",
    ...draftFields(input),
  });
}

export function importQuestionResource(input: QuestionImportInput): Promise<ImportedResource> {
  return postImport("/admin/import/question", {
    title: input.title,
    body: input.body,
    short_answer: input.shortAnswer,
    topic_slug: input.topicSlug,
    subtopic_slug: input.subtopicSlug,
    object_type: input.objectType,
  });
}

export async function importPdfResource(input: PdfImportInput): Promise<ImportedResource> {
  const body = new FormData();
  body.append("file", input.file);
  body.append("topic_slug", input.topicSlug);
  body.append("object_type", input.objectType ?? "question");
  if (input.subtopicSlug) {
    body.append("subtopic_slug", input.subtopicSlug);
  }
  if (input.title?.trim()) {
    body.append("title", input.title.trim());
  }
  if (input.summary?.trim()) {
    body.append("summary", input.summary.trim());
  }

  const response = await fetch(`${getApiBaseUrl()}/admin/import/pdf`, {
    method: "POST",
    body,
  });

  if (!response.ok) {
    throw new Error(await parseImportError(response));
  }

  return response.json() as Promise<ImportedResource>;
}
