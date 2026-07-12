import Link from "next/link";

import type { ConceptSummary } from "@/lib/types/concept";

type ConceptSearchResultsProps = {
  query: string;
  concepts: ConceptSummary[];
  isLoading: boolean;
  error: string | null;
};

export function ConceptSearchResults({
  query,
  concepts,
  isLoading,
  error,
}: ConceptSearchResultsProps) {
  if (!query.trim()) {
    return null;
  }

  return (
    <section
      aria-label="Concept search results"
      className="rounded-lg border border-[#dfe6e1] bg-white p-4 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <div className="mb-3">
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Concept matches</p>
        <h2 className="text-base font-semibold text-[#15201c]">
          Results for &ldquo;{query.trim()}&rdquo;
        </h2>
      </div>

      {isLoading ? <p className="text-sm text-[#66736e]">Searching concepts...</p> : null}

      {error ? <p className="text-sm text-[#b42318]">{error}</p> : null}

      {!isLoading && !error && concepts.length === 0 ? (
        <p className="text-sm text-[#66736e]">No concepts matched this search.</p>
      ) : null}

      {!isLoading && !error && concepts.length > 0 ? (
        <ul className="grid gap-2">
          {concepts.map((concept) => (
            <li key={concept.id}>
              <Link
                href={`/concepts/${concept.slug}`}
                className="flex items-center justify-between gap-3 rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-3 py-2 transition-colors hover:border-[#bdd3ca] hover:bg-[#edf5f1]"
              >
                <span className="text-sm font-medium text-[#15201c]">{concept.name}</span>
                <span className="shrink-0 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                  {concept.topic_slug}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
