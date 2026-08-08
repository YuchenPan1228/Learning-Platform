"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  buildDraftPayload,
  createDraftFormState,
  validateDraftFormState,
  type DraftFormState,
} from "@/lib/admin-review/draft-form";
import {
  fieldClassName,
  labelClassName,
  TopicTargetFields,
} from "@/components/admin/topic-target-fields";
import type { ReviewQueueEditInput } from "@/lib/types/admin-review";
import type { TopicWithSubtopics } from "@/lib/types/topic";

type DraftContentEditorProps = {
  initialState: DraftFormState;
  topics: TopicWithSubtopics[];
  canEdit: boolean;
  isBusy: boolean;
  onSave: (input: ReviewQueueEditInput) => Promise<void>;
};

export function DraftContentEditor({
  initialState,
  topics,
  canEdit,
  isBusy,
  onSave,
}: DraftContentEditorProps) {
  const [form, setForm] = useState(initialState);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSave() {
    setError(null);
    setIsSaving(true);
    try {
      validateDraftFormState(form);
      await onSave({
        objectType: "question",
        payloadJson: buildDraftPayload(form),
      });
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Save failed.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="border-t border-[#edf5f1] pt-4">
      <h3 className="text-sm font-semibold text-[#15201c]">Edit draft content</h3>
      <p className="mt-1 text-sm text-[#66736e]">
        Refine the interview question before approval and publish.
      </p>

      <div className="mt-4 grid gap-4">
        <TopicTargetFields
          topics={topics}
          objectType="question"
          topicSlug={form.topicSlug}
          subtopicSlug={form.subtopicSlug}
          disabled={!canEdit || isBusy || isSaving}
          onObjectTypeChange={() => undefined}
          onTopicSlugChange={(topicSlug) => setForm((current) => ({ ...current, topicSlug }))}
          onSubtopicSlugChange={(subtopicSlug) =>
            setForm((current) => ({ ...current, subtopicSlug }))
          }
        />

        <div className="grid gap-4">
          <label className={labelClassName}>
            Question title
            <input
              value={form.title}
              disabled={!canEdit || isBusy || isSaving}
              onChange={(event) =>
                setForm((current) => ({ ...current, title: event.target.value }))
              }
              className={fieldClassName}
            />
          </label>
          <label className={labelClassName}>
            Question body
            <textarea
              rows={6}
              value={form.body}
              disabled={!canEdit || isBusy || isSaving}
              onChange={(event) => setForm((current) => ({ ...current, body: event.target.value }))}
              className={fieldClassName}
            />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className={labelClassName}>
              Short answer (optional)
              <input
                value={form.shortAnswer}
                disabled={!canEdit || isBusy || isSaving}
                onChange={(event) =>
                  setForm((current) => ({ ...current, shortAnswer: event.target.value }))
                }
                className={fieldClassName}
              />
            </label>
            <label className={labelClassName}>
              Difficulty (optional)
              <select
                value={form.difficulty}
                disabled={!canEdit || isBusy || isSaving}
                onChange={(event) =>
                  setForm((current) => ({ ...current, difficulty: event.target.value }))
                }
                className={fieldClassName}
              >
                <option value="">Unspecified</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>
          </div>
        </div>

        {canEdit ? (
          <div>
            <Button type="button" disabled={isBusy || isSaving} onClick={handleSave}>
              {isSaving ? "Saving…" : "Save draft edits"}
            </Button>
          </div>
        ) : null}

        {error ? (
          <p className="text-sm text-[#9b2c2c]" role="alert">
            {error}
          </p>
        ) : null}
      </div>
    </section>
  );
}

export function createEditorStateFromItem(
  item: Parameters<typeof createDraftFormState>[0],
): DraftFormState {
  return createDraftFormState(item);
}
