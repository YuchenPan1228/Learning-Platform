import type { ImportDraftTarget } from "@/lib/admin-review/draft-form";
import { getSubtopicsForTopic } from "@/lib/admin-review/draft-form";
import type { TopicWithSubtopics } from "@/lib/types/topic";

const fieldClassName =
  "mt-1.5 w-full rounded-lg border border-[#dfe6e1] bg-white px-3 py-2 text-sm text-[#15201c] outline-none focus-visible:border-[#176b54] focus-visible:ring-2 focus-visible:ring-[#176b54]/25";

const labelClassName = "block text-sm font-medium text-[#40524b]";

type TopicTargetFieldsProps = {
  topics: TopicWithSubtopics[];
  objectType: ImportDraftTarget;
  topicSlug: string;
  subtopicSlug: string;
  onObjectTypeChange: (value: ImportDraftTarget) => void;
  onTopicSlugChange: (value: string) => void;
  onSubtopicSlugChange: (value: string) => void;
  disabled?: boolean;
  showObjectType?: boolean;
};

export function TopicTargetFields({
  topics,
  topicSlug,
  subtopicSlug,
  onTopicSlugChange,
  onSubtopicSlugChange,
  disabled = false,
  showObjectType = false,
}: TopicTargetFieldsProps) {
  const subtopics = getSubtopicsForTopic(topics, topicSlug);
  void showObjectType;

  return (
    <div className="grid gap-4 rounded-lg border border-[#edf5f1] bg-[#fafcfb] p-4">
      <p className="text-sm font-semibold text-[#15201c]">Draft target</p>
      <div className="grid gap-4">
        <label className={labelClassName}>
          Topic
          <select
            required
            value={topicSlug}
            disabled={disabled}
            onChange={(event) => {
              onTopicSlugChange(event.target.value);
              onSubtopicSlugChange("");
            }}
            className={fieldClassName}
          >
            <option value="">Select a topic</option>
            {topics.map((topic) => (
              <option key={topic.id} value={topic.slug}>
                {topic.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className={labelClassName}>
        Subtopic (optional)
        <select
          value={subtopicSlug}
          disabled={disabled || !topicSlug || subtopics.length === 0}
          onChange={(event) => onSubtopicSlugChange(event.target.value)}
          className={fieldClassName}
        >
          <option value="">No subtopic</option>
          {subtopics.map((subtopic) => (
            <option key={subtopic.id} value={subtopic.slug}>
              {subtopic.name}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

export { fieldClassName, labelClassName };
