"use client";

import { useEffect, useState } from "react";

import { ConceptSearchResults } from "@/components/topics/concept-search-results";
import { searchConcepts } from "@/lib/api/concepts";
import type { ConceptSummary } from "@/lib/types/concept";

type ConceptSearchPanelProps = {
  query: string;
  topicSlug?: string;
};

export function ConceptSearchPanel({ query, topicSlug }: ConceptSearchPanelProps) {
  const [concepts, setConcepts] = useState<ConceptSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const timeoutId = window.setTimeout(async () => {
      try {
        const response = await searchConcepts({ query, topicSlug });
        if (!cancelled) {
          setConcepts(response.concepts);
          setError(null);
        }
      } catch {
        if (!cancelled) {
          setConcepts([]);
          setError("Concept search is unavailable. Check that the API is running.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }, 300);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [query, topicSlug]);

  return (
    <ConceptSearchResults query={query} concepts={concepts} isLoading={isLoading} error={error} />
  );
}
