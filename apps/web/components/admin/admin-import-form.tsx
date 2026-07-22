"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import {
  importNoteResource,
  importPdfMetadataResource,
  importUrlResource,
} from "@/lib/api/admin-import";
import type { ImportedResource } from "@/lib/types/admin-import";
import { cn } from "@/lib/utils";

type ImportMode = "url" | "note" | "pdf";

const MODES: { id: ImportMode; label: string; description: string }[] = [
  {
    id: "url",
    label: "URL",
    description: "Save a source URL as a draft resource. No crawling.",
  },
  {
    id: "note",
    label: "Note",
    description: "Paste a manual or book note. Stored as draft text only.",
  },
  {
    id: "pdf",
    label: "PDF metadata",
    description: "Record local PDF metadata. No file upload or parsing.",
  },
];

const fieldClassName =
  "mt-1.5 w-full rounded-lg border border-[#dfe6e1] bg-white px-3 py-2 text-sm text-[#15201c] outline-none focus-visible:border-[#176b54] focus-visible:ring-2 focus-visible:ring-[#176b54]/25";

const labelClassName = "block text-sm font-medium text-[#40524b]";

export function AdminImportForm() {
  const [mode, setMode] = useState<ImportMode>("url");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ImportedResource | null>(null);

  const [url, setUrl] = useState("");
  const [urlTitle, setUrlTitle] = useState("");
  const [urlLicense, setUrlLicense] = useState("");
  const [urlAttribution, setUrlAttribution] = useState("");

  const [noteText, setNoteText] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteSourceType, setNoteSourceType] = useState<"manual" | "book_note">("manual");
  const [noteAttribution, setNoteAttribution] = useState("");

  const [pdfTitle, setPdfTitle] = useState("");
  const [pdfPath, setPdfPath] = useState("");
  const [pdfAuthor, setPdfAuthor] = useState("");
  const [pdfPublisher, setPdfPublisher] = useState("");
  const [pdfLicense, setPdfLicense] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setIsSubmitting(true);

    try {
      if (mode === "url") {
        const imported = await importUrlResource({
          url: url.trim(),
          title: urlTitle.trim() || undefined,
          license: urlLicense.trim() || undefined,
          attribution: urlAttribution.trim() || undefined,
        });
        setResult(imported);
        return;
      }

      if (mode === "note") {
        const imported = await importNoteResource({
          noteText: noteText.trim(),
          title: noteTitle.trim() || undefined,
          sourceType: noteSourceType,
          attribution: noteAttribution.trim() || undefined,
        });
        setResult(imported);
        return;
      }

      const imported = await importPdfMetadataResource({
        title: pdfTitle.trim(),
        filePath: pdfPath.trim() || undefined,
        author: pdfAuthor.trim() || undefined,
        publisher: pdfPublisher.trim() || undefined,
        license: pdfLicense.trim() || undefined,
      });
      setResult(imported);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Import failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
      <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Admin</p>
      <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Import resources</h2>
      <p className="mt-1 text-sm text-[#66736e]">
        Create draft resources for later review. Crawling and PDF extraction stay deferred.
      </p>

      <div className="mt-5 flex flex-wrap gap-2" role="tablist" aria-label="Import type">
        {MODES.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={mode === item.id}
            className={cn(
              "rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors",
              mode === item.id
                ? "border-[#176b54] bg-[#176b54] text-white"
                : "border-[#dfe6e1] bg-[#f6f7f4] text-[#40524b] hover:border-[#176b54]/50",
            )}
            onClick={() => {
              setMode(item.id);
              setError(null);
              setResult(null);
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
      <p className="mt-2 text-sm text-[#66736e]">{MODES.find((item) => item.id === mode)?.description}</p>

      <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
        {mode === "url" ? (
          <>
            <label className={labelClassName}>
              URL
              <input
                required
                type="url"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="https://..."
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Title
              <input
                value={urlTitle}
                onChange={(event) => setUrlTitle(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              License
              <input
                value={urlLicense}
                onChange={(event) => setUrlLicense(event.target.value)}
                placeholder="CC-BY-4.0"
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Attribution
              <input
                value={urlAttribution}
                onChange={(event) => setUrlAttribution(event.target.value)}
                className={fieldClassName}
              />
            </label>
          </>
        ) : null}

        {mode === "note" ? (
          <>
            <label className={labelClassName}>
              Note text
              <textarea
                required
                value={noteText}
                onChange={(event) => setNoteText(event.target.value)}
                rows={6}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Title
              <input
                value={noteTitle}
                onChange={(event) => setNoteTitle(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Note kind
              <select
                value={noteSourceType}
                onChange={(event) =>
                  setNoteSourceType(event.target.value as "manual" | "book_note")
                }
                className={fieldClassName}
              >
                <option value="manual">Manual note</option>
                <option value="book_note">Book note</option>
              </select>
            </label>
            <label className={labelClassName}>
              Attribution
              <input
                value={noteAttribution}
                onChange={(event) => setNoteAttribution(event.target.value)}
                className={fieldClassName}
              />
            </label>
          </>
        ) : null}

        {mode === "pdf" ? (
          <>
            <label className={labelClassName}>
              Title
              <input
                required
                value={pdfTitle}
                onChange={(event) => setPdfTitle(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Local file path
              <input
                value={pdfPath}
                onChange={(event) => setPdfPath(event.target.value)}
                placeholder="/path/to/notes.pdf"
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Author
              <input
                value={pdfAuthor}
                onChange={(event) => setPdfAuthor(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Publisher
              <input
                value={pdfPublisher}
                onChange={(event) => setPdfPublisher(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              License
              <input
                value={pdfLicense}
                onChange={(event) => setPdfLicense(event.target.value)}
                className={fieldClassName}
              />
            </label>
          </>
        ) : null}

        <div>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving draft…" : "Save draft resource"}
          </Button>
        </div>
      </form>

      {error ? (
        <p className="mt-4 text-sm text-[#9b2c2c]" role="alert">
          {error}
        </p>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-lg border border-[#cfe5db] bg-[#f3faf7] p-3 text-sm text-[#40524b]">
          <p className="font-semibold text-[#15201c]">Draft resource saved</p>
          <p className="mt-1">
            ID {result.id} · {result.source_type} · {result.status}
          </p>
          {result.title ? <p className="mt-1">Title: {result.title}</p> : null}
          {result.url ? <p className="mt-1 break-all">Path/URL: {result.url}</p> : null}
        </div>
      ) : null}
    </section>
  );
}
