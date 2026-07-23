"use client";

import { useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import {
  fetchAdminConcept,
  fetchAdminConcepts,
  updateAdminConcept,
} from "@/lib/api/admin-concepts";
import type { ConceptDetail, ConceptSummary } from "@/lib/types/concept";
import type { TopicWithSubtopics } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type AdminConceptsViewProps = {
  topics: TopicWithSubtopics[];
  initialConcepts: ConceptSummary[];
};

const panelClassName =
  "rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]";

const fieldClassName =
  "mt-1.5 w-full rounded-lg border border-[#dfe6e1] bg-white px-3 py-2 text-sm text-[#15201c] outline-none focus-visible:border-[#176b54] focus-visible:ring-2 focus-visible:ring-[#176b54]/25";

const labelClassName = "block text-sm font-medium text-[#40524b]";

type EditorFields = {
  name: string;
  definition: string;
  formula: string;
  intuition: string;
  workedExample: string;
  commonMistakes: string;
  interviewTips: string;
  prerequisites: string;
};

function toEditorFields(concept: ConceptDetail): EditorFields {
  return {
    name: concept.name,
    definition: concept.definition ?? "",
    formula: concept.formula ?? "",
    intuition: concept.intuition ?? "",
    workedExample: concept.worked_example ?? "",
    commonMistakes: concept.common_mistakes ?? "",
    interviewTips: concept.interview_tips ?? "",
    prerequisites: concept.prerequisites ?? "",
  };
}

export function AdminConceptsView({ topics, initialConcepts }: AdminConceptsViewProps) {
  const [topicSlug, setTopicSlug] = useState("");
  const [concepts, setConcepts] = useState(initialConcepts);
  const [selectedSlug, setSelectedSlug] = useState<string | null>(initialConcepts[0]?.slug ?? null);
  const [selected, setSelected] = useState<ConceptDetail | null>(null);
  const [fields, setFields] = useState<EditorFields | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadList() {
      setError(null);
      try {
        const items = await fetchAdminConcepts(topicSlug || undefined);
        if (cancelled) {
          return;
        }
        setConcepts(items);
        setSelectedSlug((current) => {
          if (current !== null && items.some((item) => item.slug === current)) {
            return current;
          }
          return items[0]?.slug ?? null;
        });
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load concepts.");
        }
      }
    }

    void loadList();
    return () => {
      cancelled = true;
    };
  }, [topicSlug]);

  useEffect(() => {
    if (selectedSlug === null) {
      return;
    }

    let cancelled = false;
    const slug = selectedSlug;

    async function loadDetail() {
      setIsLoadingDetail(true);
      setError(null);
      setStatusMessage(null);
      try {
        const detail = await fetchAdminConcept(slug);
        if (cancelled) {
          return;
        }
        setSelected(detail);
        setFields(toEditorFields(detail));
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load concept.");
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
  }, [selectedSlug]);

  const activeSelected = selectedSlug !== null && selected?.slug === selectedSlug ? selected : null;
  const activeFields =
    selectedSlug !== null && selected?.slug === selectedSlug && fields !== null ? fields : null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selectedSlug === null || activeFields === null) {
      return;
    }

    setIsSaving(true);
    setError(null);
    setStatusMessage(null);
    try {
      const updated = await updateAdminConcept(selectedSlug, {
        name: activeFields.name.trim(),
        definition: activeFields.definition,
        formula: activeFields.formula,
        intuition: activeFields.intuition,
        workedExample: activeFields.workedExample,
        commonMistakes: activeFields.commonMistakes,
        interviewTips: activeFields.interviewTips,
        prerequisites: activeFields.prerequisites,
      });
      setSelected(updated);
      setFields(toEditorFields(updated));
      setConcepts((current) =>
        current.map((item) =>
          item.slug === selectedSlug
            ? {
                ...item,
                name: updated.name,
                slug: updated.slug,
              }
            : item,
        ),
      );
      if (updated.slug !== selectedSlug) {
        setSelectedSlug(updated.slug);
      }
      setStatusMessage("Concept saved. Slug and graph edges were preserved.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Save failed.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[320px_minmax(0,1fr)]">
      <section className={panelClassName}>
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Admin</p>
        <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Concept editor</h2>
        <p className="mt-1 text-sm text-[#66736e]">
          Edit existing concepts. Creation stays outside the import → review loop.
        </p>

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

        {concepts.length === 0 ? (
          <p className="mt-4 text-sm text-[#66736e]">No concepts for this filter.</p>
        ) : (
          <ul className="mt-4 grid gap-2">
            {concepts.map((concept) => {
              const isSelected = concept.slug === selectedSlug;
              return (
                <li key={concept.id}>
                  <button
                    type="button"
                    className={cn(
                      "w-full rounded-lg border px-3 py-2 text-left transition-colors",
                      isSelected
                        ? "border-[#176b54] bg-[#f3faf7]"
                        : "border-[#edf5f1] bg-[#fafcfb] hover:border-[#176b54]/40",
                    )}
                    onClick={() => setSelectedSlug(concept.slug)}
                  >
                    <p className="text-sm font-semibold text-[#15201c]">{concept.name}</p>
                    <p className="mt-1 text-xs text-[#66736e]">
                      {concept.topic_slug} · {concept.slug}
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
            <p className="text-sm text-[#66736e]">Loading concept…</p>
          </section>
        ) : null}

        {!isLoadingDetail && activeSelected && activeFields ? (
          <section className={panelClassName}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
                  Editing concept
                </p>
                <h2 className="mt-1 text-xl font-semibold text-[#15201c]">{activeSelected.name}</h2>
                <p className="mt-1 text-sm text-[#66736e]">
                  Slug <span className="font-mono">{activeSelected.slug}</span> · topic{" "}
                  {activeSelected.topic_slug}
                </p>
              </div>
            </div>

            <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
              <label className={labelClassName}>
                Name
                <input
                  required
                  value={activeFields.name}
                  onChange={(event) => setFields({ ...activeFields, name: event.target.value })}
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Definition
                <textarea
                  rows={4}
                  value={activeFields.definition}
                  onChange={(event) =>
                    setFields({ ...activeFields, definition: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Formula
                <textarea
                  rows={2}
                  value={activeFields.formula}
                  onChange={(event) => setFields({ ...activeFields, formula: event.target.value })}
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Intuition
                <textarea
                  rows={3}
                  value={activeFields.intuition}
                  onChange={(event) =>
                    setFields({ ...activeFields, intuition: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Worked example
                <textarea
                  rows={4}
                  value={activeFields.workedExample}
                  onChange={(event) =>
                    setFields({ ...activeFields, workedExample: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Common mistakes
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
                Interview tips
                <textarea
                  rows={3}
                  value={activeFields.interviewTips}
                  onChange={(event) =>
                    setFields({ ...activeFields, interviewTips: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>
              <label className={labelClassName}>
                Prerequisites (text)
                <textarea
                  rows={2}
                  value={activeFields.prerequisites}
                  onChange={(event) =>
                    setFields({ ...activeFields, prerequisites: event.target.value })
                  }
                  className={fieldClassName}
                />
              </label>

              <div>
                <Button type="submit" disabled={isSaving}>
                  {isSaving ? "Saving…" : "Save concept"}
                </Button>
              </div>
            </form>

            <section className="mt-6 border-t border-[#edf5f1] pt-4">
              <h3 className="text-sm font-semibold text-[#15201c]">Graph edges (read-only)</h3>
              <p className="mt-1 text-sm text-[#66736e]">
                Edges are preserved by this editor. Graph curation stays a separate workflow.
              </p>
              {activeSelected.neighbors.length === 0 ? (
                <p className="mt-3 text-sm text-[#66736e]">No neighbors linked.</p>
              ) : (
                <ul className="mt-3 grid gap-2 text-sm text-[#40524b]">
                  {activeSelected.neighbors.map((neighbor) => (
                    <li
                      key={`${neighbor.direction}-${neighbor.relationship_type}-${neighbor.slug}`}
                    >
                      <span className="font-medium">{neighbor.name}</span>
                      <span className="text-[#66736e]">
                        {" "}
                        · {neighbor.direction} {neighbor.relationship_type}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </section>
        ) : null}

        {!isLoadingDetail && !activeSelected ? (
          <section className={panelClassName}>
            <p className="text-sm text-[#66736e]">Select a concept to edit.</p>
          </section>
        ) : null}
      </div>
    </div>
  );
}
