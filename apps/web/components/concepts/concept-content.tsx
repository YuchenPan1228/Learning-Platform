import Link from "next/link";

import { ConceptSection } from "@/components/concepts/concept-section";
import { TopicBadge } from "@/components/ui/topic-badge";
import { buttonVariants } from "@/components/ui/button";
import type { ConceptDetail } from "@/lib/types/concept";
import { getConceptPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

export async function ConceptContent({
  concept,
  practiceQuestionCount,
  practiceHref,
}: {
  concept: ConceptDetail;
  practiceQuestionCount: number;
  practiceHref: string;
}) {
  const palette = getConceptPalette(concept.slug, concept.topic_slug);

  return (
    <div className="grid gap-3">
      <section
        className={cn(
          "rounded-lg border border-l-4 bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]",
          palette.border,
          palette.accent,
          palette.surface,
        )}
      >
        <div>
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Concept page</p>
          <TopicBadge slug={concept.slug} label={concept.name} className="mt-2" />
          <h2 className="mt-3 text-2xl font-semibold text-[#15201c] sm:text-3xl">{concept.name}</h2>
          <Link
            href={`/topics/${concept.topic_slug}`}
            className="mt-2 inline-block text-sm text-[#176b54] hover:underline"
          >
            View in topic library
          </Link>
        </div>

        <section className="mt-5 rounded-lg border border-[#edf5f1] bg-[#fbfcfa] px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Practice</p>
              <p className="mt-1 text-sm text-[#31443d]">
                {practiceQuestionCount > 0
                  ? `${practiceQuestionCount} question${practiceQuestionCount === 1 ? "" : "s"} available for this concept.`
                  : "No practice questions are linked to this concept yet."}
              </p>
            </div>
            {practiceQuestionCount > 0 ? (
              <Link href={practiceHref} className={cn(buttonVariants({ size: "sm" }))}>
                Practice questions
              </Link>
            ) : null}
          </div>
        </section>
      </section>

      {concept.formula ? (
        <ConceptSection title="Formula" content={concept.formula} tone="formula" monospace />
      ) : null}
      {concept.definition ? (
        <ConceptSection title="Definition" content={concept.definition} tone="definition" />
      ) : null}
      {concept.intuition ? (
        <ConceptSection title="Key insight" content={concept.intuition} tone="insight" />
      ) : null}
      {concept.worked_example ? (
        <ConceptSection title="Worked example" content={concept.worked_example} tone="example" />
      ) : null}
      {concept.interview_tips ? (
        <ConceptSection title="Interview tips" content={concept.interview_tips} tone="tips" />
      ) : null}
      {concept.common_mistakes ? (
        <ConceptSection title="Common mistakes" content={concept.common_mistakes} tone="mistakes" />
      ) : null}
      {concept.prerequisites ? (
        <ConceptSection
          title="Prerequisites"
          content={concept.prerequisites}
          tone="prerequisites"
        />
      ) : null}
    </div>
  );
}
