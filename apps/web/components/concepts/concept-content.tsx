import Link from "next/link";

import { ConceptSection } from "@/components/concepts/concept-section";
import type { ConceptDetail } from "@/lib/types/concept";

export function ConceptContent({ concept }: { concept: ConceptDetail }) {
  return (
    <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
      <div className="mb-5">
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Concept page</p>
        <h2 className="mt-1 text-2xl font-semibold text-[#15201c] sm:text-3xl">{concept.name}</h2>
        <Link
          href={`/topics/${concept.topic_slug}`}
          className="mt-2 inline-block text-sm text-[#176b54] hover:underline"
        >
          View in topic library
        </Link>
      </div>

      {concept.formula ? (
        <div className="mb-6 rounded-lg border border-[#bdd3ca] bg-[#edf5f1] px-4 py-3 font-mono text-sm text-[#15201c]">
          {concept.formula}
        </div>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2">
        <div className="grid gap-6">
          {concept.definition ? (
            <ConceptSection title="Definition" content={concept.definition} />
          ) : null}
          {concept.intuition ? (
            <ConceptSection title="Intuition" content={concept.intuition} />
          ) : null}
          {concept.common_mistakes ? (
            <ConceptSection title="Common mistakes" content={concept.common_mistakes} />
          ) : null}
        </div>

        <div className="grid gap-6">
          {concept.interview_tips ? (
            <ConceptSection title="Interview tips" content={concept.interview_tips} />
          ) : null}
          {concept.prerequisites ? (
            <ConceptSection title="Prerequisites" content={concept.prerequisites} />
          ) : null}
        </div>
      </div>
    </section>
  );
}
