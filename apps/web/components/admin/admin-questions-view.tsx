"use client";

import { useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import {
  deleteAdminQuestion,
  fetchAdminQuestion,
  fetchAdminQuestions,
  updateAdminQuestion,
} from "@/lib/api/admin-questions";
import type { Difficulty, QuestionDetail, QuestionSummary } from "@/lib/types/question";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type AdminQuestionsViewProps = {
  topics: TopicWithSubtopics[];
  initialQuestions: QuestionSummary[];
};

const panelClassName =
  "rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]";

const fieldClassName =
  "mt-1.5 w-full rounded-lg border border-[#dfe6e1] bg-white px-3 py-2 text-sm text-[#15201c] outline-none focus-visible:border-[#176b54] focus-visible:ring-2 focus-visible:ring-[#176b54]/25";

const labelClassName = "block text-sm font-medium text-[#40524b]";

type EditorFields = {
  title: string;
  body: string;
  shortAnswer: string;
  canonicalSolution: string;
  difficulty: Difficulty;
  status: "draft" | "approved" | "rejected";
  topicSlug: string;
  subtopicSlug: string;
  companyHint: string;
  expectedSolutionPattern: string;
  commonMistakes: string;
  prerequisites: string;
  sourceAttribution: string;
};

function toEditorFields(question: QuestionDetail): EditorFields {
  return {
    title: question.title,
    body: question.body,
    shortAnswer: question.short_answer ?? "",
    canonicalSolution: question.canonical_solution ?? "",
    difficulty: question.difficulty,
    status: question.status as EditorFields["status"],
    topicSlug: question.topic_slug,
    subtopicSlug: question.subtopic_slug ?? "",
    companyHint: question.company_hint ?? "",
    expectedSolutionPattern: question.expected_solution_pattern ?? "",
    commonMistakes: (question.common_mistakes ?? []).join("\n"),
    prerequisites: (question.prerequisites ?? []).join("\n"),
    sourceAttribution: question.source_attribution ?? "",
  };
}

function splitLines(value: string): string[] | null {
  const items = value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  return items.length > 0 ? items : null;
}

export function AdminQuestionsView({ topics, initialQuestions }: AdminQuestionsViewProps) {
  const [topicSlug, setTopicSlug] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "draft" | "approved" | "rejected">(
    "approved",
  );
  const [questions, setQuestions] = useState(initialQuestions);
  const [selectedId, setSelectedId] = useState<number | null>(initialQuestions[0]?.id ?? null);
  const [selected, setSelected] = useState<QuestionDetail | null>(null);
  const [fields, setFields] = useState<EditorFields | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const subtopics =
    topics.find((topic) => topic.slug === (fields?.topicSlug || topicSlug))?.subtopics ?? [];

  useEffect(() => {
    let cancelled = false;

    async function loadList() {
      setError(null);
      try {
        const items = await fetchAdminQuestions({
          topicSlug: topicSlug || undefined,
          status: statusFilter === "all" ? undefined : statusFilter,
        });
        if (cancelled) {
          return;
        }
        setQuestions(items);
        setSelectedId((current) => {
          if (current !== null && items.some((item) => item.id === current)) {
            return current;
          }
          return items[0]?.id ?? null;
        });
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load questions.");
        }
      }
    }

    void loadList();
    return () => {
      cancelled = true;
    };
  }, [topicSlug, statusFilter]);

  useEffect(() => {
    if (selectedId === null) {
      return;
    }

    let cancelled = false;
    const questionId = selectedId;

    async function loadDetail() {
      setIsLoadingDetail(true);
      setError(null);
      setStatusMessage(null);
      try {
        const detail = await fetchAdminQuestion(questionId);
        if (cancelled) {
          return;
        }
        setSelected(detail);
        setFields(toEditorFields(detail));
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load question.");
          setSelected(null);
          setFields(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoadingDetail(false);
        }
      }
    }

    void loadDetail();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const activeSelected = selectedId !== null && selected?.id === selectedId ? selected : null;
  const activeFields =
    selectedId !== null && selected?.id === selectedId && fields !== null ? fields : null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selectedId === null || activeFields === null) {
      return;
    }

    setIsSaving(true);
    setError(null);
    setStatusMessage(null);
    try {
      const updated = await updateAdminQuestion(selectedId, {
        title: activeFields.title.trim(),
        body: activeFields.body.trim(),
        shortAnswer: activeFields.shortAnswer,
        canonicalSolution: activeFields.canonicalSolution,
        difficulty: activeFields.difficulty,
        status: activeFields.status,
        topicSlug: activeFields.topicSlug,
        subtopicSlug: activeFields.subtopicSlug.trim() || null,
        companyHint: activeFields.companyHint,
        expectedSolutionPattern: activeFields.expectedSolutionPattern,
        commonMistakes: splitLines(activeFields.commonMistakes),
        prerequisites: splitLines(activeFields.prerequisites),
        sourceAttribution: activeFields.sourceAttribution,
      });
      setSelected(updated);
      setFields(toEditorFields(updated));
      setQuestions((current) =>
        current.map((item) =>
          item.id === selectedId
            ? {
                ...item,
                title: updated.title,
                difficulty: updated.difficulty,
                status: updated.status,
                topic_slug: updated.topic_slug,
                subtopic_slug: updated.subtopic_slug,
              }
            : item,
        ),
      );
      setStatusMessage("Question saved.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Save failed.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete() {
    if (selectedId === null || activeSelected === null) {
      return;
    }
    const confirmed = window.confirm(
      `Delete question #${activeSelected.id} "${activeSelected.title}"? This cannot be undone.`,
    );
    if (!confirmed) {
      return;
    }

    setIsDeleting(true);
    setError(null);
    setStatusMessage(null);
    try {
      await deleteAdminQuestion(selectedId);
      const remaining = questions.filter((item) => item.id !== selectedId);
      setQuestions(remaining);
      setSelectedId(remaining[0]?.id ?? null);
      setSelected(null);
      setFields(null);
      setStatusMessage(`Deleted question #${selectedId}.`);
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Delete failed.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[320px_minmax(0,1fr)]">
      <section className={panelClassName}>
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Admin</p>
        <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Practice questions</h2>
        <p className="mt-1 text-sm text-[#66736e]">Edit or delete published practice questions.</p>

        <label className={`${labelClassName} mt-4`}>
          Topic filter
          <select
            value={topicSlug}
            onChange={(event) => setTopicSlug(event.target.value)}
            className={fieldClassName}
          >
            <option value="">All topics</option>
            {topics.map((topic) => (
              <option key={topic.id} value={topic.slug}>
                {topic.name}
              </option>
            ))}
          </select>
        </label>

        <label className={`${labelClassName} mt-3`}>
          Status
          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value as "all" | "draft" | "approved" | "rejected")
            }
            className={fieldClassName}
          >
            <option value="all">All</option>
            <option value="approved">Approved</option>
            <option value="draft">Draft</option>
            <option value="rejected">Rejected</option>
          </select>
        </label>

        {questions.length === 0 ? (
          <p className="mt-4 text-sm text-[#66736e]">No questions for this filter.</p>
        ) : (
          <ul className="mt-4 grid max-h-[70vh] gap-2 overflow-y-auto">
            {questions.map((question) => {
              const isSelected = question.id === selectedId;
              return (
                <li key={question.id}>
                  <button
                    type="button"
                    className={cn(
                      "w-full rounded-lg border px-3 py-2 text-left transition-colors",
                      isSelected
                        ? "border-[#176b54] bg-[#f3faf7]"
                        : "border-[#edf5f1] bg-[#fafcfb] hover:border-[#176b54]/40",
                    )}
                    onClick={() => setSelectedId(question.id)}
                  >
                    <p className="text-sm font-semibold text-[#15201c]">{question.title}</p>
                    <p className="mt-1 text-xs text-[#66736e]">
                      #{question.id} · {question.difficulty} · {question.status}
                    </p>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <div className="min-w-0">
        {error ? (
          <p className="mb-4 text-sm text-[#9b2c2c]" role="alert">
            {error}
          </p>
        ) : null}
        {statusMessage ? (
          <p className="mb-4 text-sm text-[#176b54]" role="status">
            {statusMessage}
          </p>
        ) : null}

        {isLoadingDetail ? (
          <section className={panelClassName}>
            <p className="text-sm text-[#66736e]">Loading question…</p>
          </section>
        ) : null}

        {!isLoadingDetail && activeSelected && activeFields ? (
          <section className={panelClassName}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
                  Editing question
                </p>
                <h2 className="mt-1 text-xl font-semibold text-[#15201c]">
                  #{activeSelected.id} {activeSelected.title}
                </h2>
              </div>
              <Button
                type="button"
                variant="destructive"
                disabled={isSaving || isDeleting}
                onClick={handleDelete}
              >
                {isDeleting ? "Deleting…" : "Delete"}
              </Button>
            </div>

            <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
              <label className={labelClassName}>
                Title
                <input
                  required
                  value={activeFields.title}
                  onChange={(event) => setFields({ ...activeFields, title: event.target.value })}
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Body
                <textarea
                  required
                  rows={5}
                  value={activeFields.body}
                  onChange={(event) => setFields({ ...activeFields, body: event.target.value })}
                  className={fieldClassName}
                />
              </label>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className={labelClassName}>
                  Difficulty
                  <select
                    value={activeFields.difficulty}
                    onChange={(event) =>
                      setFields({
                        ...activeFields,
                        difficulty: event.target.value as Difficulty,
                      })
                    }
                    className={fieldClassName}
                  >
                    <option value="easy">easy</option>
                    <option value="medium">medium</option>
                    <option value="hard">hard</option>
                    <option value="expert">expert</option>
                  </select>
                </label>
                <label className={labelClassName}>
                  Status
                  <select
                    value={activeFields.status}
                    onChange={(event) =>
                      setFields({
                        ...activeFields,
                        status: event.target.value as EditorFields["status"],
                      })
                    }
                    className={fieldClassName}
                  >
                    <option value="approved">approved</option>
                    <option value="draft">draft</option>
                    <option value="rejected">rejected</option>
                  </select>
                </label>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className={labelClassName}>
                  Topic
                  <select
                    required
                    value={activeFields.topicSlug}
                    onChange={(event) =>
                      setFields({
                        ...activeFields,
                        topicSlug: event.target.value,
                        subtopicSlug: "",
                      })
                    }
                    className={fieldClassName}
                  >
                    {topics.map((topic) => (
                      <option key={topic.id} value={topic.slug}>
                        {topic.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className={labelClassName}>
                  Subtopic
                  <select
                    value={activeFields.subtopicSlug}
                    onChange={(event) =>
                      setFields({ ...activeFields, subtopicSlug: event.target.value })
                    }
                    className={fieldClassName}
                  >
                    <option value="">None</option>
                    {subtopics.map((subtopic) => (
                      <option key={subtopic.id} value={subtopic.slug}>
                        {subtopic.name}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <label className={labelClassName}>
                Short answer
                <input
                  value={activeFields.shortAnswer}
                  onChange={(event) =>
                    setFields({ ...activeFields, shortAnswer: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Canonical solution
                <textarea
                  rows={4}
                  value={activeFields.canonicalSolution}
                  onChange={(event) =>
                    setFields({ ...activeFields, canonicalSolution: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Common mistakes (one per line)
                <textarea
                  rows={3}
                  value={activeFields.commonMistakes}
                  onChange={(event) =>
                    setFields({ ...activeFields, commonMistakes: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Prerequisites (one per line)
                <textarea
                  rows={2}
                  value={activeFields.prerequisites}
                  onChange={(event) =>
                    setFields({ ...activeFields, prerequisites: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Expected solution pattern
                <textarea
                  rows={2}
                  value={activeFields.expectedSolutionPattern}
                  onChange={(event) =>
                    setFields({ ...activeFields, expectedSolutionPattern: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Company hint
                <input
                  value={activeFields.companyHint}
                  onChange={(event) =>
                    setFields({ ...activeFields, companyHint: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Source attribution
                <textarea
                  rows={2}
                  value={activeFields.sourceAttribution}
                  onChange={(event) =>
                    setFields({ ...activeFields, sourceAttribution: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>

              <div>
                <Button type="submit" disabled={isSaving || isDeleting}>
                  {isSaving ? "Saving…" : "Save question"}
                </Button>
              </div>
            </form>
          </section>
        ) : null}

        {!isLoadingDetail && !activeSelected ? (
          <section className={panelClassName}>
            <p className="text-sm text-[#66736e]">Select a question to edit.</p>
          </section>
        ) : null}
      </div>
    </div>
  );
}
