"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import {
  fieldClassName,
  labelClassName,
  TopicTargetFields,
} from "@/components/admin/topic-target-fields";
import { Button } from "@/components/ui/button";
import {
  importNoteResource,
  importPdfResource,
  importQuestionResource,
  importUrlResource,
} from "@/lib/api/admin-import";
import type { ImportDraftTarget } from "@/lib/admin-review/draft-form";
import type { ImportedResource } from "@/lib/types/admin-import";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type ImportMode = "url" | "note" | "question" | "pdf";

const MODES: { id: ImportMode; label: string; description: string }[] = [
  {
    id: "url",
    label: "URL",
    description: "Bookmark a source URL. Fill in the question or flashcard in review.",
  },
  {
    id: "note",
    label: "Note",
    description: "Paste freeform text for a question body or flashcard.",
  },
  {
    id: "question",
    label: "Question",
    description: "Paste a structured interview question with title and body.",
  },
  {
    id: "pdf",
    label: "PDF",
    description: "Upload a PDF and create a draft. Question extraction comes in Phase 5.",
  },
];

type AdminImportFormProps = {
  topics: TopicWithSubtopics[];
};

export function AdminImportForm({ topics }: AdminImportFormProps) {
  const [mode, setMode] = useState<ImportMode>("question");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ImportedResource | null>(null);

  const [objectType, setObjectType] = useState<ImportDraftTarget>("question");
  const [topicSlug, setTopicSlug] = useState(topics[0]?.slug ?? "");
  const [subtopicSlug, setSubtopicSlug] = useState("");

  const [url, setUrl] = useState("");
  const [urlTitle, setUrlTitle] = useState("");

  const [noteText, setNoteText] = useState("");
  const [noteTitle, setNoteTitle] = useState("");

  const [questionTitle, setQuestionTitle] = useState("");
  const [questionBody, setQuestionBody] = useState("");
  const [questionShortAnswer, setQuestionShortAnswer] = useState("");

  const [pdfTitle, setPdfTitle] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfSummary, setPdfSummary] = useState("");

  const sharedDraftOptions = {
    objectType: mode === "question" ? ("question" as const) : objectType,
    topicSlug,
    subtopicSlug: subtopicSlug || undefined,
  };

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);

    if (!topicSlug) {
      setError("Select a topic before importing.");
      return;
    }

    setIsSubmitting(true);

    try {
      if (mode === "url") {
        const imported = await importUrlResource({
          url: url.trim(),
          title: urlTitle.trim() || undefined,
          ...sharedDraftOptions,
        });
        setResult(imported);
        return;
      }

      if (mode === "note") {
        if (objectType === "flashcard" && !noteTitle.trim()) {
          throw new Error("Flashcard imports need a title for the card front.");
        }
        const imported = await importNoteResource({
          noteText: noteText.trim(),
          title: noteTitle.trim() || undefined,
          ...sharedDraftOptions,
        });
        setResult(imported);
        return;
      }

      if (mode === "question") {
        const imported = await importQuestionResource({
          title: questionTitle.trim(),
          body: questionBody.trim(),
          shortAnswer: questionShortAnswer.trim() || undefined,
          objectType: "question",
          topicSlug,
          subtopicSlug: subtopicSlug || undefined,
        });
        setResult(imported);
        return;
      }

      if (!pdfFile) {
        throw new Error("Choose a PDF file to upload.");
      }
      const imported = await importPdfResource({
        file: pdfFile,
        title: pdfTitle.trim() || undefined,
        summary: pdfSummary.trim() || undefined,
        ...sharedDraftOptions,
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
      <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Import drafts</h2>
      <p className="mt-1 text-sm text-[#66736e]">
        Create question or flashcard drafts for review. URL bookmarks and PDF uploads store the
        source now; AI extraction from those sources comes in Phase 5.
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
              setPdfFile(null);
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
      <p className="mt-2 text-sm text-[#66736e]">
        {MODES.find((item) => item.id === mode)?.description}
      </p>

      <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
        {mode === "question" ? (
          <TopicTargetFields
            topics={topics}
            objectType="question"
            topicSlug={topicSlug}
            subtopicSlug={subtopicSlug}
            showObjectType={false}
            onObjectTypeChange={() => undefined}
            onTopicSlugChange={setTopicSlug}
            onSubtopicSlugChange={setSubtopicSlug}
          />
        ) : (
          <TopicTargetFields
            topics={topics}
            objectType={objectType}
            topicSlug={topicSlug}
            subtopicSlug={subtopicSlug}
            onObjectTypeChange={setObjectType}
            onTopicSlugChange={setTopicSlug}
            onSubtopicSlugChange={setSubtopicSlug}
          />
        )}

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
              Title (optional)
              <input
                value={urlTitle}
                onChange={(event) => setUrlTitle(event.target.value)}
                className={fieldClassName}
              />
            </label>
          </>
        ) : null}

        {mode === "note" ? (
          <>
            <label className={labelClassName}>
              {objectType === "flashcard" ? "Flashcard front" : "Title (optional)"}
              <input
                required={objectType === "flashcard"}
                value={noteTitle}
                onChange={(event) => setNoteTitle(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              {objectType === "flashcard" ? "Flashcard back" : "Question body"}
              <textarea
                required
                value={noteText}
                onChange={(event) => setNoteText(event.target.value)}
                rows={6}
                className={fieldClassName}
              />
            </label>
          </>
        ) : null}

        {mode === "question" ? (
          <>
            <label className={labelClassName}>
              Question title
              <input
                required
                value={questionTitle}
                onChange={(event) => setQuestionTitle(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Question body
              <textarea
                required
                value={questionBody}
                onChange={(event) => setQuestionBody(event.target.value)}
                rows={6}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Short answer (optional)
              <input
                value={questionShortAnswer}
                onChange={(event) => setQuestionShortAnswer(event.target.value)}
                className={fieldClassName}
              />
            </label>
          </>
        ) : null}

        {mode === "pdf" ? (
          <>
            <label className={labelClassName}>
              PDF file
              <input
                required
                type="file"
                accept="application/pdf,.pdf"
                onChange={(event) => setPdfFile(event.target.files?.[0] ?? null)}
                className={fieldClassName}
              />
            </label>
            {pdfFile ? (
              <p className="text-sm text-[#66736e]">
                Selected: {pdfFile.name} ({Math.max(1, Math.round(pdfFile.size / 1024))} KB)
              </p>
            ) : null}
            <label className={labelClassName}>
              Title (optional — defaults to filename)
              <input
                value={pdfTitle}
                onChange={(event) => setPdfTitle(event.target.value)}
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Notes (optional)
              <textarea
                value={pdfSummary}
                onChange={(event) => setPdfSummary(event.target.value)}
                rows={4}
                className={fieldClassName}
              />
            </label>
          </>
        ) : null}

        <div>
          <Button type="submit" disabled={isSubmitting || topics.length === 0}>
            {isSubmitting ? "Saving draft…" : "Save draft"}
          </Button>
        </div>
      </form>

      {topics.length === 0 ? (
        <p className="mt-4 text-sm text-[#9b2c2c]">No topics available. Seed the database first.</p>
      ) : null}

      {error ? (
        <p className="mt-4 text-sm text-[#9b2c2c]" role="alert">
          {error}
        </p>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-lg border border-[#cfe5db] bg-[#f3faf7] p-3 text-sm text-[#40524b]">
          <p className="font-semibold text-[#15201c]">Draft saved to review queue</p>
          <p className="mt-1">
            Resource ID {result.id} · Review item ID {result.extracted_object_id ?? "—"} ·{" "}
            {result.source_type} · {result.status}
          </p>
          {result.title ? <p className="mt-1">Title: {result.title}</p> : null}
          {result.url ? <p className="mt-1 break-all">Path/URL: {result.url}</p> : null}
          {result.extracted_object_id ? (
            <Link
              href="/admin/review"
              className="mt-3 inline-flex text-sm font-medium text-[#176b54] underline-offset-2 hover:underline"
            >
              Open review queue
            </Link>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
