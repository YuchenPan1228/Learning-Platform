"use client";

import { useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import {
  deleteAdminFlashcard,
  fetchAdminFlashcard,
  fetchAdminFlashcards,
  updateAdminFlashcard,
} from "@/lib/api/admin-flashcards";
import type { Flashcard } from "@/lib/types/flashcard";
import type { Difficulty } from "@/lib/types/question";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type AdminFlashcardsViewProps = {
  topics: TopicWithSubtopics[];
  initialFlashcards: Flashcard[];
};

const panelClassName =
  "rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]";

const fieldClassName =
  "mt-1.5 w-full rounded-lg border border-[#dfe6e1] bg-white px-3 py-2 text-sm text-[#15201c] outline-none focus-visible:border-[#176b54] focus-visible:ring-2 focus-visible:ring-[#176b54]/25";

const labelClassName = "block text-sm font-medium text-[#40524b]";

const DIFFICULTIES: Array<Difficulty | ""> = ["", "easy", "medium", "hard", "expert"];

type EditorFields = {
  front: string;
  back: string;
  topicSlug: string;
  difficulty: Difficulty | "";
};

function toEditorFields(flashcard: Flashcard): EditorFields {
  return {
    front: flashcard.front,
    back: flashcard.back,
    topicSlug: flashcard.topic_slug,
    difficulty: flashcard.difficulty ?? "",
  };
}

function previewText(value: string, maxLength = 72): string {
  const compact = value.replace(/\s+/g, " ").trim();
  if (compact.length <= maxLength) {
    return compact;
  }
  return `${compact.slice(0, maxLength - 1)}…`;
}

export function AdminFlashcardsView({ topics, initialFlashcards }: AdminFlashcardsViewProps) {
  const [topicSlug, setTopicSlug] = useState("");
  const [flashcards, setFlashcards] = useState(initialFlashcards);
  const [selectedId, setSelectedId] = useState<number | null>(initialFlashcards[0]?.id ?? null);
  const [selected, setSelected] = useState<Flashcard | null>(null);
  const [fields, setFields] = useState<EditorFields | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const topicOptions = topics.flatMap((topic) => [
    { slug: topic.slug, name: topic.name },
    ...topic.subtopics.map((subtopic) => ({
      slug: subtopic.slug,
      name: `${topic.name} / ${subtopic.name}`,
    })),
  ]);

  useEffect(() => {
    let cancelled = false;

    async function loadList() {
      setError(null);
      try {
        const items = await fetchAdminFlashcards({
          topicSlug: topicSlug || undefined,
        });
        if (cancelled) {
          return;
        }
        setFlashcards(items);
        setSelectedId((current) => {
          if (current !== null && items.some((item) => item.id === current)) {
            return current;
          }
          return items[0]?.id ?? null;
        });
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load flashcards.");
        }
      }
    }

    void loadList();
    return () => {
      cancelled = true;
    };
  }, [topicSlug]);

  useEffect(() => {
    if (selectedId === null) {
      return;
    }

    let cancelled = false;
    const flashcardId = selectedId;

    async function loadDetail() {
      setIsLoadingDetail(true);
      setError(null);
      setStatusMessage(null);
      try {
        const detail = await fetchAdminFlashcard(flashcardId);
        if (cancelled) {
          return;
        }
        setSelected(detail);
        setFields(toEditorFields(detail));
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load flashcard.");
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
      const updated = await updateAdminFlashcard(selectedId, {
        front: activeFields.front.trim(),
        back: activeFields.back.trim(),
        topicSlug: activeFields.topicSlug,
        difficulty: activeFields.difficulty || null,
      });
      setSelected(updated);
      setFields(toEditorFields(updated));
      setFlashcards((current) =>
        current.map((item) =>
          item.id === selectedId
            ? {
                ...item,
                front: updated.front,
                back: updated.back,
                topic_slug: updated.topic_slug,
                difficulty: updated.difficulty,
              }
            : item,
        ),
      );
      setStatusMessage("Flashcard saved.");
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
      `Delete flashcard #${activeSelected.id}? This cannot be undone.`,
    );
    if (!confirmed) {
      return;
    }

    setIsDeleting(true);
    setError(null);
    setStatusMessage(null);
    try {
      await deleteAdminFlashcard(selectedId);
      const remaining = flashcards.filter((item) => item.id !== selectedId);
      setFlashcards(remaining);
      setSelectedId(remaining[0]?.id ?? null);
      setSelected(null);
      setFields(null);
      setStatusMessage(`Deleted flashcard #${selectedId}.`);
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
        <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Flashcards</h2>
        <p className="mt-1 text-sm text-[#66736e]">Edit or delete published flashcards.</p>

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

        {flashcards.length === 0 ? (
          <p className="mt-4 text-sm text-[#66736e]">No flashcards for this filter.</p>
        ) : (
          <ul className="mt-4 grid max-h-[70vh] gap-2 overflow-y-auto">
            {flashcards.map((flashcard) => {
              const isSelected = flashcard.id === selectedId;
              return (
                <li key={flashcard.id}>
                  <button
                    type="button"
                    className={cn(
                      "w-full rounded-lg border px-3 py-2 text-left transition-colors",
                      isSelected
                        ? "border-[#176b54] bg-[#f3faf7]"
                        : "border-[#edf5f1] bg-[#fafcfb] hover:border-[#176b54]/40",
                    )}
                    onClick={() => setSelectedId(flashcard.id)}
                  >
                    <p className="text-sm font-semibold text-[#15201c]">
                      {previewText(flashcard.front)}
                    </p>
                    <p className="mt-1 text-xs text-[#66736e]">
                      #{flashcard.id} · {flashcard.topic_slug}
                      {flashcard.difficulty ? ` · ${flashcard.difficulty}` : ""}
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

        {selectedId === null ? (
          <section className={panelClassName}>
            <p className="text-sm text-[#66736e]">Select a flashcard to edit.</p>
          </section>
        ) : isLoadingDetail || activeFields === null ? (
          <section className={panelClassName}>
            <p className="text-sm text-[#66736e]">Loading flashcard…</p>
          </section>
        ) : (
          <form className={panelClassName} onSubmit={handleSubmit}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Editor</p>
                <h2 className="mt-1 text-xl font-semibold text-[#15201c]">
                  Flashcard #{selectedId}
                </h2>
              </div>
              <Button
                type="button"
                variant="outline"
                onClick={() => void handleDelete()}
                disabled={isDeleting || isSaving}
              >
                {isDeleting ? "Deleting…" : "Delete"}
              </Button>
            </div>

            <label className={`${labelClassName} mt-4`}>
              Front
              <textarea
                required
                rows={4}
                value={activeFields.front}
                onChange={(event) =>
                  setFields((current) =>
                    current ? { ...current, front: event.target.value } : current,
                  )
                }
                className={fieldClassName}
              />
            </label>

            <label className={`${labelClassName} mt-3`}>
              Back
              <textarea
                required
                rows={5}
                value={activeFields.back}
                onChange={(event) =>
                  setFields((current) =>
                    current ? { ...current, back: event.target.value } : current,
                  )
                }
                className={fieldClassName}
              />
            </label>

            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className={labelClassName}>
                Topic
                <select
                  required
                  value={activeFields.topicSlug}
                  onChange={(event) =>
                    setFields((current) =>
                      current ? { ...current, topicSlug: event.target.value } : current,
                    )
                  }
                  className={fieldClassName}
                >
                  {topicOptions.map((option) => (
                    <option key={option.slug} value={option.slug}>
                      {option.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className={labelClassName}>
                Difficulty
                <select
                  value={activeFields.difficulty}
                  onChange={(event) =>
                    setFields((current) =>
                      current
                        ? {
                            ...current,
                            difficulty: event.target.value as Difficulty | "",
                          }
                        : current,
                    )
                  }
                  className={fieldClassName}
                >
                  {DIFFICULTIES.map((difficulty) => (
                    <option key={difficulty || "none"} value={difficulty}>
                      {difficulty || "None"}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="mt-5">
              <Button type="submit" disabled={isSaving || isDeleting}>
                {isSaving ? "Saving…" : "Save flashcard"}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
