import type { QuestionDetail } from "@/lib/types/question";
import { formatDifficulty, formatEstimatedTime } from "@/lib/questions/format";

type QuestionMetadataProps = {
  question: QuestionDetail;
};

function MetadataItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">{label}</dt>
      <dd className="mt-1 text-sm font-medium text-[#15201c]">{value}</dd>
    </div>
  );
}

export function QuestionMetadata({ question }: QuestionMetadataProps) {
  return (
    <dl className="grid gap-3 sm:grid-cols-2">
      <MetadataItem label="Topic" value={question.topic_slug} />
      {question.subtopic_slug ? (
        <MetadataItem label="Concept" value={question.subtopic_slug} />
      ) : null}
      <MetadataItem label="Difficulty" value={formatDifficulty(question.difficulty)} />
      <MetadataItem
        label="Estimated time"
        value={formatEstimatedTime(question.estimated_time_seconds)}
      />
      <MetadataItem label="Company hint" value={question.company_hint ?? "General quant"} />
      {question.expected_solution_pattern ? (
        <MetadataItem label="Pattern" value={question.expected_solution_pattern} />
      ) : null}
      {question.prerequisites && question.prerequisites.length > 0 ? (
        <MetadataItem label="Prerequisites" value={question.prerequisites.join(", ")} />
      ) : null}
      {question.common_mistakes && question.common_mistakes.length > 0 ? (
        <MetadataItem label="Common mistakes" value={question.common_mistakes.join("; ")} />
      ) : null}
    </dl>
  );
}
