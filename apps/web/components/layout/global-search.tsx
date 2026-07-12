"use client";

import { Search } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";

import { Input } from "@/components/ui/input";
import { searchContent } from "@/lib/api/search";
import type { SearchResponse } from "@/lib/api/search";
import { cn } from "@/lib/utils";

const MIN_QUERY_LENGTH = 2;
const DEBOUNCE_MS = 250;

export function GlobalSearch() {
  const listboxId = useId();
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < MIN_QUERY_LENGTH) {
      setResults(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    const timeout = window.setTimeout(() => {
      void searchContent(trimmed)
        .then((payload) => {
          setResults(payload);
          setIsOpen(true);
        })
        .catch(() => {
          setError("Search is unavailable.");
          setResults(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }, DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [query]);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (containerRef.current?.contains(event.target as Node)) {
        return;
      }
      setIsOpen(false);
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, []);

  function handleQuestionSelect(questionId: number) {
    setIsOpen(false);
    setQuery("");
    router.push(`/practice/${questionId}`);
  }

  const hasResults =
    results !== null && (results.concepts.length > 0 || results.questions.length > 0);
  const showPanel = isOpen && query.trim().length >= MIN_QUERY_LENGTH;

  return (
    <div ref={containerRef} className="relative w-full max-w-[420px]">
      <div className="flex h-11 items-center gap-2 rounded-lg border border-[#dfe6e1] bg-white px-3">
        <Search className="size-4 text-[#66736e]" aria-hidden="true" />
        <Input
          type="search"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setIsOpen(true);
          }}
          onFocus={() => {
            if (query.trim().length >= MIN_QUERY_LENGTH) {
              setIsOpen(true);
            }
          }}
          placeholder="Search questions and concepts..."
          className="h-9 border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
          aria-label="Search questions and concepts"
          aria-controls={listboxId}
          aria-expanded={showPanel}
          aria-autocomplete="list"
          role="combobox"
        />
      </div>

      {showPanel ? (
        <div
          id={listboxId}
          role="listbox"
          className="absolute top-[calc(100%+0.5rem)] right-0 left-0 z-20 max-h-[420px] overflow-y-auto rounded-lg border border-[#dfe6e1] bg-white p-2 shadow-[0_16px_42px_rgba(21,32,28,0.12)]"
        >
          {isLoading ? <p className="px-3 py-2 text-sm text-[#66736e]">Searching…</p> : null}
          {error ? <p className="px-3 py-2 text-sm text-[#b42318]">{error}</p> : null}
          {!isLoading && !error && !hasResults ? (
            <p className="px-3 py-2 text-sm text-[#66736e]">No matches for &ldquo;{query}&rdquo;.</p>
          ) : null}

          {results && results.concepts.length > 0 ? (
            <section className="px-1 py-1">
              <p className="px-2 py-1 text-xs font-bold tracking-wide text-[#66736e] uppercase">
                Concepts
              </p>
              <ul>
                {results.concepts.map((concept) => (
                  <li key={concept.id}>
                    <Link
                      href={`/concepts/${concept.slug}`}
                      onClick={() => {
                        setIsOpen(false);
                        setQuery("");
                      }}
                      className="block rounded-md px-2 py-2 text-sm text-[#15201c] hover:bg-[#edf5f1]"
                    >
                      <span className="font-medium">{concept.name}</span>
                      <span className="mt-0.5 block text-xs text-[#66736e]">
                        {concept.topic_slug}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          {results && results.questions.length > 0 ? (
            <section className="px-1 py-1">
              <p className="px-2 py-1 text-xs font-bold tracking-wide text-[#66736e] uppercase">
                Questions
              </p>
              <ul>
                {results.questions.map((question) => (
                  <li key={question.id}>
                    <button
                      type="button"
                      onClick={() => handleQuestionSelect(question.id)}
                      className={cn(
                        "block w-full rounded-md px-2 py-2 text-left text-sm text-[#15201c] hover:bg-[#edf5f1]",
                      )}
                    >
                      <span className="font-medium">{question.title}</span>
                      <span className="mt-0.5 block text-xs text-[#66736e]">
                        {question.topic_slug}
                        {question.subtopic_slug ? ` · ${question.subtopic_slug}` : ""}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
