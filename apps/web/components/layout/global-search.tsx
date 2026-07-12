"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";

import { Input } from "@/components/ui/input";
import { TopicBadge } from "@/components/ui/topic-badge";
import { searchContent } from "@/lib/api/search";
import type { SearchResponse } from "@/lib/types/search";
import { getConceptPalette, getTopicPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

const MIN_QUERY_LENGTH = 2;

export function GlobalSearch() {
  const router = useRouter();
  const listboxId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < MIN_QUERY_LENGTH) {
      return;
    }

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
    }, 250);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [query]);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (containerRef.current?.contains(event.target as Node)) {
        return;
      }
      setIsOpen(false);
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
    };
  }, []);

  function handleSelect(href: string) {
    setIsOpen(false);
    setQuery("");
    setResults(null);
    router.push(href);
  }

  const hasResults =
    results !== null && (results.concepts.length > 0 || results.questions.length > 0);

  return (
    <div ref={containerRef} className="relative w-full max-w-[420px]">
      <Input
        type="search"
        value={query}
        onChange={(event) => {
          const value = event.target.value;
          setQuery(value);
          setIsOpen(true);
          if (value.trim().length < MIN_QUERY_LENGTH) {
            setResults(null);
            setIsLoading(false);
            setError(null);
          } else {
            setIsLoading(true);
            setError(null);
          }
        }}
        onFocus={() => {
          if (results !== null) {
            setIsOpen(true);
          }
        }}
        placeholder="Search questions and concepts..."
        aria-label="Search questions and concepts"
        aria-expanded={isOpen}
        aria-controls={listboxId}
        className="h-11 rounded-lg border-[#dfe6e1] bg-white px-3 shadow-none focus-visible:ring-[#0f766e]/20"
      />

      {isOpen && query.trim().length >= MIN_QUERY_LENGTH ? (
        <div
          id={listboxId}
          role="listbox"
          className="absolute top-[calc(100%+0.5rem)] z-20 max-h-[360px] w-full overflow-y-auto rounded-lg border border-[#dfe6e1] bg-white p-2 shadow-[0_16px_42px_rgba(21,32,28,0.12)]"
        >
          {isLoading ? (
            <p className="px-3 py-2 text-sm text-[#66736e]">Searching…</p>
          ) : null}
          {error ? <p className="px-3 py-2 text-sm text-[#b42318]">{error}</p> : null}
          {!isLoading && !error && !hasResults ? (
            <p className="px-3 py-2 text-sm text-[#66736e]">No matches for &ldquo;{query}&rdquo;.</p>
          ) : null}

          {results && results.concepts.length > 0 ? (
            <section className="mb-2">
              <p className="px-3 py-1 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                Concepts
              </p>
              <ul>
                {results.concepts.map((concept) => {
                  const palette = getConceptPalette(concept.slug, concept.topic_slug);
                  return (
                    <li key={concept.id}>
                      <button
                        type="button"
                        role="option"
                        aria-selected={false}
                        onClick={() => handleSelect(`/concepts/${concept.slug}`)}
                        className={cn(
                          "flex w-full items-center justify-between gap-3 rounded-md border border-l-4 px-3 py-2 text-left",
                          palette.border,
                          palette.accent,
                          palette.surface,
                          palette.hoverSurface,
                        )}
                      >
                        <span className="text-sm font-medium text-[#15201c]">{concept.name}</span>
                        <TopicBadge slug={concept.slug} />
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          ) : null}

          {results && results.questions.length > 0 ? (
            <section>
              <p className="px-3 py-1 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                Questions
              </p>
              <ul>
                {results.questions.map((question) => {
                  const palette = getTopicPalette(question.topic_slug);
                  return (
                    <li key={question.id}>
                      <button
                        type="button"
                        role="option"
                        aria-selected={false}
                        onClick={() =>
                          handleSelect(
                            `/practice/${question.id}?returnTo=${encodeURIComponent("/practice")}`,
                          )
                        }
                        className={cn(
                          "flex w-full flex-col gap-2 rounded-md border border-l-4 px-3 py-2 text-left",
                          palette.border,
                          palette.accent,
                          palette.surface,
                          palette.hoverSurface,
                        )}
                      >
                        <span className="text-sm font-medium text-[#15201c]">{question.title}</span>
                        <TopicBadge slug={question.topic_slug} />
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          ) : null}

          {hasResults ? (
            <div className="border-t border-[#edf5f1] px-3 py-2">
              <Link
                href={`/practice?q=${encodeURIComponent(query.trim())}`}
                className="text-sm text-[#176b54] hover:underline"
                onClick={() => setIsOpen(false)}
              >
                Browse all practice questions
              </Link>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
