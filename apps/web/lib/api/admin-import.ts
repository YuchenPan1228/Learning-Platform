import { getApiBaseUrl } from "@/lib/api/config";
import type { ImportedResource, ResourceSourceType } from "@/lib/types/admin-import";
import type { ImportDraftTarget } from "@/lib/admin-review/draft-form";

type SharedImportDraftInput = {
  objectType?: ImportDraftTarget;
  topicSlug: string;
  subtopicSlug?: string;
};

export type UrlImportInput = SharedImportDraftInput & {
  url: string;
  title?: string;
  author?: string;
  license?: string;
  attribution?: string;
  summary?: string;
};

export type NoteImportInput = SharedImportDraftInput & {
  noteText: string;
  title?: string;
  author?: string;
  license?: string;
  attribution?: string;
  sourceType?: Extract<ResourceSourceType, "manual" | "book_note">;
};

export type QuestionImportInput = {
  title: string;
  body: string;
  shortAnswer?: string;
  difficulty?: "easy" | "medium" | "hard";
  topicSlug: string;
  subtopicSlug?: string;
  objectType: "question";
};

export type PdfMetadataImportInput = SharedImportDraftInput & {
  title: string;
  filePath?: string;
  author?: string;
  publisher?: string;
  license?: string;
  attribution?: string;
  summary?: string;
};

async function postImport(path: string, body: Record<string, unknown>): Promise<ImportedResource> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let detail = `Import failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: unknown };
      if (typeof payload.detail === "string") {
        detail = payload.detail;
      }
    } catch {
      // Keep the status-based message when the body is not JSON.
    }
    throw new Error(detail);
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
    author: input.author,
    license: input.license,
    attribution: input.attribution,
    summary: input.summary,
    ...draftFields(input),
  });
}

export function importNoteResource(input: NoteImportInput): Promise<ImportedResource> {
  return postImport("/admin/import/note", {
    note_text: input.noteText,
    title: input.title,
    author: input.author,
    license: input.license,
    attribution: input.attribution,
    source_type: input.sourceType ?? "manual",
    ...draftFields(input),
  });
}

export function importQuestionResource(input: QuestionImportInput): Promise<ImportedResource> {
  return postImport("/admin/import/question", {
    title: input.title,
    body: input.body,
    short_answer: input.shortAnswer,
    difficulty: input.difficulty,
    topic_slug: input.topicSlug,
    subtopic_slug: input.subtopicSlug,
    object_type: input.objectType,
  });
}

export function importPdfMetadataResource(
  input: PdfMetadataImportInput,
): Promise<ImportedResource> {
  return postImport("/admin/import/pdf", {
    title: input.title,
    file_path: input.filePath,
    author: input.author,
    publisher: input.publisher,
    license: input.license,
    attribution: input.attribution,
    summary: input.summary,
    ...draftFields(input),
  });
}
