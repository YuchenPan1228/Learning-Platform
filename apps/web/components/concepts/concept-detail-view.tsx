import { ConceptContent } from "@/components/concepts/concept-content";
import { ConceptGraphPanel } from "@/components/concepts/concept-graph-panel";
import type { ConceptDetail } from "@/lib/types/concept";

export function ConceptDetailView({
  concept,
  practiceQuestionCount,
  practiceHref,
}: {
  concept: ConceptDetail;
  practiceQuestionCount: number;
  practiceHref: string;
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(280px,0.8fr)]">
      <ConceptContent
        concept={concept}
        practiceQuestionCount={practiceQuestionCount}
        practiceHref={practiceHref}
      />
      <ConceptGraphPanel concept={concept} />
    </div>
  );
}
