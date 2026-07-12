import type { QuestionDetail } from "@/lib/types/question";
import type { TopicRead } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type CategoryFilterProps = {
  categories: TopicRead[];
  selectedSlug: string;
  questionCounts: Record<string, number>;
  onSelect: (slug: string) => void;
};

export function CategoryFilter({
  categories,
  selectedSlug,
  questionCounts,
  onSelect,
}: CategoryFilterProps) {
  const totalCount = Object.values(questionCounts).reduce((sum, count) => sum + count, 0);

  return (
    <section
      aria-label="Mental math categories"
      className="rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <div className="mb-4">
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Categories</p>
        <h2 className="text-lg font-semibold text-[#15201c]">Filter prompts</h2>
      </div>

      <ul className="grid gap-2">
        <li>
          <button
            type="button"
            onClick={() => onSelect("all")}
            className={cn(
              "flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition-colors",
              selectedSlug === "all"
                ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
                : "border-[#edf5f1] bg-[#fbfcfa] text-[#31443d] hover:border-[#bdd3ca] hover:bg-[#edf5f1]",
            )}
          >
            <span className="font-medium">All categories</span>
            <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
              {totalCount}
            </span>
          </button>
        </li>
        {categories.map((category) => (
          <li key={category.id}>
            <button
              type="button"
              onClick={() => onSelect(category.slug)}
              className={cn(
                "flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition-colors",
                selectedSlug === category.slug
                  ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
                  : "border-[#edf5f1] bg-[#fbfcfa] text-[#31443d] hover:border-[#bdd3ca] hover:bg-[#edf5f1]",
              )}
            >
              <span className="font-medium">{category.name}</span>
              <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                {questionCounts[category.slug] ?? 0}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function buildCategoryCounts(questions: QuestionDetail[]): Record<string, number> {
  return questions.reduce<Record<string, number>>((counts, question) => {
    if (question.subtopic_slug === null) {
      return counts;
    }
    counts[question.subtopic_slug] = (counts[question.subtopic_slug] ?? 0) + 1;
    return counts;
  }, {});
}
