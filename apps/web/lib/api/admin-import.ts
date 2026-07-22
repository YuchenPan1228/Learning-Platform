import { getApiBaseUrl } from "@/lib/api/config";
import type { ImportedResource, ResourceSourceType } from "@/lib/types/admin-import";

export type UrlImportInput = {
  url: string;
  title?: string;
  author?: string;
  license?: string;
  attribution?: string;
  summary?: string;
};

export type NoteImportInput = {
  noteText: string;
  title?: string;
  author?: string;
  license?: string;
  attribution?: string;
  sourceType?: Extract<ResourceSourceType, "manual" | "book_note">;
};

export type PdfMetadataImportInput = {
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

export function importUrlResource(input: UrlImportInput): Promise<ImportedResource> {
  return postImport("/admin/import/url", {
    url: input.url,
    title: input.title,
    author: input.author,
    license: input.license,
    attribution: input.attribution,
    summary: input.summary,
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
  });
}
