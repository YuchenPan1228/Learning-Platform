"use client";

import { useMemo, useState, type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import {
  approveReviewItem,
  editReviewItem,
  fetchReviewQueue,
  publishReviewItem,
  rejectReviewItem,
} from "@/lib/api/admin-review";
import {
  formatScore,
  getCandidateQuestions,
  getExtractedText,
  getFormulas,
  getLicenseStatus,
  getProvenanceRows,
  getQualityScore,
  getReviewItemTitle,
  getSourceLabel,
  getSummary,
  isPublishedReviewItem,
} from "@/lib/admin-review/display";
import type {
  PublishReviewResult,
  ReviewQueueItem,
  ReviewQueueStatus,
} from "@/lib/types/admin-review";
import { cn } from "@/lib/utils";

type AdminReviewViewProps = {
  initialItems: ReviewQueueItem[];
  initialStatus?: ReviewQueueStatus;
};

const QUEUE_TABS: { id: ReviewQueueStatus; label: string; description: string }[] = [
  {
    id: "draft",
    label: "Drafts",
    description: "Extracted objects awaiting human review.",
  },
  {
    id: "approved",
    label: "Approved",
    description: "Approved drafts ready to publish into live content.",
  },
  {
    id: "rejected",
    label: "Rejected",
    description: "Rejected drafts kept for provenance.",
  },
];

const panelClassName =
  "rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]";

const sectionTitleClassName = "text-sm font-semibold text-[#15201c]";
const mutedTextClassName = "text-sm text-[#66736e]";

function queueStatusLabel(status: ReviewQueueStatus): string {
  if (status === "draft") {
    return "Draft review";
  }
  if (status === "approved") {
    return "Approved draft";
  }
  return "Rejected draft";
}

function filterQueueItems(items: ReviewQueueItem[], status: ReviewQueueStatus): ReviewQueueItem[] {
  if (status !== "approved") {
    return items;
  }
  return items.filter((item) => !isPublishedReviewItem(item));
}

function DetailSection({
  title,
  children,
  emptyMessage,
  isEmpty,
}: {
  title: string;
  children: ReactNode;
  emptyMessage?: string;
  isEmpty?: boolean;
}) {
  return (
    <section className="border-t border-[#edf5f1] pt-4 first:border-t-0 first:pt-0">
      <h3 className={sectionTitleClassName}>{title}</h3>
      {isEmpty ? (
        <p className={`mt-2 ${mutedTextClassName}`}>{emptyMessage ?? "None available."}</p>
      ) : (
        children
      )}
    </section>
  );
}

function ReviewDetailPanel({
  item,
  queueStatus,
  isBusy,
  publishMessage,
  onApprove,
  onReject,
  onPublish,
  onSaveEdit,
}: {
  item: ReviewQueueItem;
  queueStatus: ReviewQueueStatus;
  isBusy: boolean;
  publishMessage: string | null;
  onApprove: () => void;
  onReject: () => void;
  onPublish: () => void;
  onSaveEdit: (qualityScore: number | null) => Promise<void>;
}) {
  const extractedText = getExtractedText(item);
  const summary = getSummary(item);
  const formulas = getFormulas(item);
  const candidateQuestions = getCandidateQuestions(item);
  const licenseStatus = getLicenseStatus(item);
  const qualityScore = getQualityScore(item);
  const provenanceRows = getProvenanceRows(item);
  const [qualityInput, setQualityInput] = useState(
    item.quality_score !== null ? String(item.quality_score) : "",
  );
  const [editError, setEditError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSaveQuality() {
    setEditError(null);
    setIsSaving(true);
    try {
      const trimmed = qualityInput.trim();
      const parsed = trimmed === "" ? null : Number(trimmed);
      if (parsed !== null && (Number.isNaN(parsed) || parsed < 0 || parsed > 1)) {
        throw new Error("Quality score must be between 0 and 1.");
      }
      await onSaveEdit(parsed);
    } catch (error) {
      setEditError(error instanceof Error ? error.message : "Edit failed.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className={panelClassName}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
            {queueStatusLabel(queueStatus)}
          </p>
          <h2 className="mt-1 text-xl font-semibold text-[#15201c]">{getReviewItemTitle(item)}</h2>
          <p className="mt-1 text-sm text-[#66736e]">
            {item.object_type} · confidence {formatScore(item.confidence_score)} · draft quality{" "}
            {formatScore(item.quality_score)}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {queueStatus === "draft" ? (
            <>
              <Button type="button" disabled={isBusy} onClick={onApprove}>
                Approve
              </Button>
              <Button type="button" variant="destructive" disabled={isBusy} onClick={onReject}>
                Reject
              </Button>
            </>
          ) : null}
          {queueStatus === "approved" ? (
            <Button type="button" disabled={isBusy} onClick={onPublish}>
              Publish
            </Button>
          ) : null}
        </div>
      </div>

      {publishMessage ? (
        <p className="mt-4 rounded-lg border border-[#cfe5db] bg-[#f3faf7] px-3 py-2 text-sm text-[#176b54]">
          {publishMessage}
        </p>
      ) : null}

      <div className="mt-5 grid gap-4">
        <DetailSection
          title="Source"
          emptyMessage="No linked source resource."
          isEmpty={!item.resource}
        >
          {item.resource ? (
            <div className="mt-2 grid gap-1 text-sm text-[#40524b]">
              <p className="font-medium text-[#15201c]">{getSourceLabel(item)}</p>
              {item.resource.url ? (
                <p className="break-all text-[#66736e]">{item.resource.url}</p>
              ) : null}
              <p className="text-[#66736e]">Source type: {item.resource.source_type}</p>
            </div>
          ) : null}
        </DetailSection>

        <DetailSection
          title="Extracted text"
          emptyMessage="No extracted text in this draft payload."
          isEmpty={!extractedText}
        >
          {extractedText ? (
            <pre className="mt-2 overflow-x-auto rounded-lg bg-[#f6f7f4] p-3 text-sm whitespace-pre-wrap text-[#40524b]">
              {extractedText}
            </pre>
          ) : null}
        </DetailSection>

        <DetailSection title="Summary" emptyMessage="No summary available." isEmpty={!summary}>
          {summary ? (
            <p className="mt-2 text-sm leading-relaxed text-[#40524b]">{summary}</p>
          ) : null}
        </DetailSection>

        <DetailSection
          title="Formulas"
          emptyMessage="No formulas detected."
          isEmpty={formulas.length === 0}
        >
          {formulas.length > 0 ? (
            <ul className="mt-2 grid gap-2">
              {formulas.map((formula, index) => {
                const latex = typeof formula.latex === "string" ? formula.latex : null;
                const concept = typeof formula.concept === "string" ? formula.concept : null;
                return (
                  <li
                    key={`${item.id}-formula-${index}`}
                    className="rounded-lg border border-[#edf5f1] bg-[#f6f7f4] p-3 text-sm text-[#40524b]"
                  >
                    {concept ? <p className="font-medium text-[#15201c]">{concept}</p> : null}
                    <p className={concept ? "mt-1 font-mono" : "font-mono"}>{latex ?? "—"}</p>
                  </li>
                );
              })}
            </ul>
          ) : null}
        </DetailSection>

        <DetailSection
          title="Candidate questions"
          emptyMessage="No candidate questions in this draft."
          isEmpty={candidateQuestions.length === 0}
        >
          {candidateQuestions.length > 0 ? (
            <ul className="mt-2 grid gap-3">
              {candidateQuestions.map((question, index) => {
                const title = typeof question.title === "string" ? question.title : null;
                const body = typeof question.body === "string" ? question.body : null;
                const difficulty =
                  typeof question.difficulty === "string" ? question.difficulty : null;
                return (
                  <li
                    key={`${item.id}-question-${index}`}
                    className="rounded-lg border border-[#edf5f1] p-3 text-sm text-[#40524b]"
                  >
                    {title ? <p className="font-medium text-[#15201c]">{title}</p> : null}
                    {body ? <p className="mt-1 leading-relaxed">{body}</p> : null}
                    {difficulty ? (
                      <p className="mt-2 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                        {difficulty}
                      </p>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          ) : null}
        </DetailSection>

        <div className="grid gap-4 sm:grid-cols-2">
          <DetailSection title="License status">
            <p className="mt-2 text-sm font-medium text-[#15201c]">{licenseStatus}</p>
          </DetailSection>
          <DetailSection title="Quality score">
            <p className="mt-2 text-sm font-medium text-[#15201c]">{formatScore(qualityScore)}</p>
            {queueStatus === "draft" ? (
              <div className="mt-3 flex flex-wrap items-end gap-2">
                <label className="block text-xs font-medium text-[#66736e]">
                  Edit draft quality (0–1)
                  <input
                    type="number"
                    min={0}
                    max={1}
                    step={0.01}
                    value={qualityInput}
                    onChange={(event) => setQualityInput(event.target.value)}
                    className="mt-1 block w-28 rounded-lg border border-[#dfe6e1] px-2 py-1.5 text-sm text-[#15201c]"
                  />
                </label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={isBusy || isSaving}
                  onClick={handleSaveQuality}
                >
                  {isSaving ? "Saving…" : "Save edit"}
                </Button>
              </div>
            ) : null}
            {editError ? (
              <p className="mt-2 text-sm text-[#9b2c2c]" role="alert">
                {editError}
              </p>
            ) : null}
          </DetailSection>
        </div>

        <DetailSection title="Provenance metadata">
          <dl className="mt-2 grid gap-2 text-sm">
            {provenanceRows.map((row) => (
              <div
                key={`${item.id}-${row.label}`}
                className="grid gap-1 sm:grid-cols-[160px_minmax(0,1fr)]"
              >
                <dt className="font-medium text-[#66736e]">{row.label}</dt>
                <dd className="break-all text-[#40524b]">{row.value}</dd>
              </div>
            ))}
          </dl>
        </DetailSection>
      </div>
    </div>
  );
}

function formatPublishMessage(result: PublishReviewResult): string {
  const warnings =
    result.duplicate_warnings.length > 0
      ? ` ${result.duplicate_warnings.length} near-duplicate warning(s) recorded.`
      : "";
  return `Published as ${result.published.kind} #${result.published.id}.${warnings}`;
}

export function AdminReviewView({ initialItems, initialStatus = "draft" }: AdminReviewViewProps) {
  const [queueStatus, setQueueStatus] = useState<ReviewQueueStatus>(initialStatus);
  const [items, setItems] = useState(() => filterQueueItems(initialItems, initialStatus));
  const [selectedId, setSelectedId] = useState<number | null>(
    filterQueueItems(initialItems, initialStatus)[0]?.id ?? null,
  );
  const [error, setError] = useState<string | null>(null);
  const [publishMessage, setPublishMessage] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  const selectedItem = useMemo(
    () => items.find((item) => item.id === selectedId) ?? null,
    [items, selectedId],
  );

  const activeTab = QUEUE_TABS.find((tab) => tab.id === queueStatus) ?? QUEUE_TABS[0];

  async function refreshQueue(
    status: ReviewQueueStatus = queueStatus,
    nextSelectedId?: number | null,
  ) {
    const response = await fetchReviewQueue(status);
    const visibleItems = filterQueueItems(response.items, status);
    setItems(visibleItems);
    if (nextSelectedId !== undefined) {
      setSelectedId(nextSelectedId);
      return;
    }
    if (selectedId !== null && !visibleItems.some((item) => item.id === selectedId)) {
      setSelectedId(visibleItems[0]?.id ?? null);
    }
  }

  async function switchQueueStatus(nextStatus: ReviewQueueStatus) {
    setError(null);
    setPublishMessage(null);
    setQueueStatus(nextStatus);
    setIsBusy(true);
    try {
      const response = await fetchReviewQueue(nextStatus);
      const visibleItems = filterQueueItems(response.items, nextStatus);
      setItems(visibleItems);
      setSelectedId(visibleItems[0]?.id ?? null);
    } catch (switchError) {
      setError(switchError instanceof Error ? switchError.message : "Review queue request failed.");
      setItems([]);
      setSelectedId(null);
    } finally {
      setIsBusy(false);
    }
  }

  async function runAction(action: () => Promise<void>) {
    setError(null);
    setPublishMessage(null);
    setIsBusy(true);
    try {
      await action();
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : "Review action failed.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[320px_minmax(0,1fr)]">
      <section className={panelClassName}>
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Admin</p>
        <h2 className="mt-1 text-xl font-semibold text-[#15201c]">Review queue</h2>
        <p className="mt-1 text-sm text-[#66736e]">{activeTab.description}</p>

        <div className="mt-4 flex flex-wrap gap-2" role="tablist" aria-label="Review queue status">
          {QUEUE_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={queueStatus === tab.id}
              className={cn(
                "rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors",
                queueStatus === tab.id
                  ? "border-[#176b54] bg-[#176b54] text-white"
                  : "border-[#dfe6e1] bg-[#f6f7f4] text-[#40524b] hover:border-[#176b54]/50",
              )}
              disabled={isBusy}
              onClick={() => {
                if (tab.id !== queueStatus) {
                  void switchQueueStatus(tab.id);
                }
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {items.length === 0 ? (
          <p className="mt-4 text-sm text-[#66736e]">
            No {activeTab.label.toLowerCase()} in the queue.
          </p>
        ) : (
          <ul className="mt-4 grid gap-2">
            {items.map((item) => {
              const isSelected = item.id === selectedId;
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    className={cn(
                      "w-full rounded-lg border px-3 py-2 text-left transition-colors",
                      isSelected
                        ? "border-[#176b54] bg-[#f3faf7]"
                        : "border-[#edf5f1] bg-[#fafcfb] hover:border-[#176b54]/40",
                    )}
                    onClick={() => {
                      setPublishMessage(null);
                      setSelectedId(item.id);
                    }}
                  >
                    <p className="text-sm font-semibold text-[#15201c]">
                      {getReviewItemTitle(item)}
                    </p>
                    <p className="mt-1 text-xs text-[#66736e]">
                      {item.object_type} · {getSourceLabel(item)}
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

        {selectedItem ? (
          <ReviewDetailPanel
            key={selectedItem.id}
            item={selectedItem}
            queueStatus={queueStatus}
            isBusy={isBusy}
            publishMessage={publishMessage}
            onApprove={() =>
              runAction(async () => {
                await approveReviewItem(selectedItem.id);
                await refreshQueue(queueStatus, null);
              })
            }
            onReject={() =>
              runAction(async () => {
                await rejectReviewItem(selectedItem.id);
                await refreshQueue(queueStatus, null);
              })
            }
            onPublish={() =>
              runAction(async () => {
                const result = await publishReviewItem(selectedItem.id);
                setPublishMessage(formatPublishMessage(result));
                await refreshQueue(queueStatus, null);
              })
            }
            onSaveEdit={async (qualityScore) => {
              await editReviewItem(selectedItem.id, { qualityScore });
              await refreshQueue(queueStatus, selectedItem.id);
            }}
          />
        ) : (
          <section className={panelClassName}>
            <p className="text-sm text-[#66736e]">Select a queue item to review.</p>
          </section>
        )}
      </div>
    </div>
  );
}
