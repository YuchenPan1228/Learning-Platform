import Link from "next/link";

import { TopicBadge } from "@/components/ui/topic-badge";
import { groupConceptNeighbors, neighborRelationLabel } from "@/lib/concepts/neighbors";
import type { ConceptDetail } from "@/lib/types/concept";
import { getConceptPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

export function ConceptGraphPanel({ concept }: { concept: ConceptDetail }) {
  const groups = groupConceptNeighbors(concept.neighbors);
  const currentPalette = getConceptPalette(concept.slug, concept.topic_slug);

  return (
    <aside
      aria-label="Knowledge graph neighbors"
      className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <div className="mb-4">
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Knowledge graph</p>
        <h2 className="text-lg font-semibold text-[#15201c]">Related neighbors</h2>
      </div>

      <div
        className={cn(
          "mb-4 rounded-lg border border-l-4 px-3 py-2",
          currentPalette.border,
          currentPalette.accent,
          currentPalette.surface,
        )}
      >
        <TopicBadge slug={concept.slug} label={concept.name} />
        <span className="mt-2 block text-xs font-semibold tracking-wide text-[#66736e] uppercase">
          Current
        </span>
      </div>

      {groups.length === 0 ? (
        <p className="text-sm text-[#66736e]">No graph neighbors are linked to this concept yet.</p>
      ) : (
        <div className="grid gap-5">
          {groups.map((group) => (
            <section key={group.title}>
              <h3 className="mb-2 text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                {group.title}
              </h3>
              <ul className="grid gap-2">
                {group.neighbors.map((neighbor) => {
                  const palette = getConceptPalette(neighbor.slug, concept.topic_slug);
                  return (
                    <li key={`${group.title}-${neighbor.slug}-${neighbor.direction}`}>
                      <Link
                        href={`/concepts/${neighbor.slug}`}
                        className={cn(
                          "block rounded-lg border border-l-4 px-3 py-2 transition-colors",
                          palette.border,
                          palette.accent,
                          palette.surface,
                          palette.hoverSurface,
                        )}
                      >
                        <strong className="block text-sm text-[#15201c]">{neighbor.name}</strong>
                        <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
                          {neighborRelationLabel(neighbor)}
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </section>
          ))}
        </div>
      )}
    </aside>
  );
}
