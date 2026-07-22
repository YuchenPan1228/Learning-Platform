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
  importPdfMetadataResource,
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
    description: "Save a source URL and create a draft to fill in during review.",
  },
  {
    id: "note",
    label: "Note",
    description: "Paste freeform text for a question body or flashcard back.",
  },
  {
    id: "question",
    label: "Question",
    description: "Paste a structured interview question with title and body.",
  },
  {
    id: "pdf",
    label: "PDF metadata",
    description: "Record local PDF metadata. No file upload or parsing yet.",
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
  const [urlLicense, setUrlLicense] = useState("");
  const [urlAttribution, setUrlAttribution] = useState("");

  const [noteText, setNoteText] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteSourceType, setNoteSourceType] = useState<"manual" | "book_note">("manual");
  const [noteAttribution, setNoteAttribution] = useState("");

  const [questionTitle, setQuestionTitle] = useState("");
  const [questionBody, setQuestionBody] = useState("");
  const [questionShortAnswer, setQuestionShortAnswer] = useState("");

  const [pdfTitle, setPdfTitle] = useState("");
  const [pdfPath, setPdfPath] = useState("");
  const [pdfAuthor, setPdfAuthor] = useState("");
  const [pdfPublisher, setPdfPublisher] = useState("");
  const [pdfLicense, setPdfLicense] = useState("");
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
          license: urlLicense.trim() || undefined,
          attribution: urlAttribution.trim() || undefined,
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
          sourceType: noteSourceType,
          attribution: noteAttribution.trim() || undefined,
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

      const imported = await importPdfMetadataResource({
        title: pdfTitle.trim(),
        filePath: pdfPath.trim() || undefined,
        author: pdfAuthor.trim() || undefined,
        publisher: pdfPublisher.trim() || undefined,
        license: pdfLicense.trim() || undefined,
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
      <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Import resources</h2>
      <p className="mt-1 text-sm text-[#66736e]">
        Create review-queue drafts as questions or flashcards. AI extraction from URLs and PDFs
        comes in Phase 5; for now you import sources and edit the draft before publish.
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
              {objectType === "flashcard" ? "Flashcard back" : "Question body"}
              <textarea
                required
                value={noteText}
                onChange={(event) => setNoteText(event.target.value)}
                rows={6}
                className={fieldClassName}
              />
            </label>
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
              Summary / notes (optional)
              <textarea
                value={pdfSummary}
                onChange={(event) => setPdfSummary(event.target.value)}
                rows={4}
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
