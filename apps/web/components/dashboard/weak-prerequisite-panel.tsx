import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import type { WeakPrerequisite } from "@/lib/types/dashboard";
import { cn } from "@/lib/utils";

function formatDiagnosis(item: WeakPrerequisite): string {
  return `You are working on ${item.concept_name}, but ${item.prerequisite_name} mastery is only ${Math.round(item.prerequisite_mastery_score)}%. Strengthen the prerequisite before pushing harder on dependent concepts.`;
}

export function WeakPrerequisitePanel({
  weakPrerequisites,
}: {
  weakPrerequisites: WeakPrerequisite[];
}) {
  const focus = weakPrerequisites[0];

  if (focus === undefined) {
    return (
      <section
        aria-label="Weak prerequisites"
        className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
      >
        <div className="mb-4">
          <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Diagnosis</p>
          <h2 className="text-xl font-semibold text-[#15201c]">Focus area</h2>
        </div>
        <p className="text-sm leading-relaxed text-[#66736e]">
          No weak prerequisite gaps detected at the current mastery threshold.
        </p>
      </section>
    );
  }

  return (
    <section
      aria-label="Weak prerequisites"
      className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]"
    >
      <div className="mb-4">
        <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">Diagnosis</p>
        <h2 className="text-xl font-semibold text-[#15201c]">Focus area</h2>
      </div>

      <p className="text-sm leading-relaxed text-[#66736e]">{formatDiagnosis(focus)}</p>

      <div
        className="mt-4 flex flex-wrap items-center gap-2 text-xs font-semibold text-[#31443d]"
        aria-label="Knowledge graph preview"
      >
        <span className="rounded-full border border-[#bdd3ca] bg-[#edf5f1] px-3 py-1">
          {focus.prerequisite_name}
        </span>
        <span className="text-[#66736e]" aria-hidden="true">
          →
        </span>
        <span className="rounded-full border border-[#bdd3ca] bg-[#edf5f1] px-3 py-1">
          {focus.concept_name}
        </span>
      </div>

      {weakPrerequisites.length > 1 ? (
        <ul className="mt-5 grid gap-2 border-t border-[#edf5f1] pt-4">
          {weakPrerequisites.slice(1, 4).map((item) => (
            <li
              key={`${item.concept_slug}-${item.prerequisite_slug}`}
              className="flex items-center justify-between gap-3 text-sm"
            >
              <span className="text-[#31443d]">
                {item.concept_name}{" "}
                <span className="text-[#66736e]">needs {item.prerequisite_name}</span>
              </span>
              <span className="shrink-0 font-semibold text-[#b7791f]">
                {Math.round(item.prerequisite_mastery_score)}%
              </span>
            </li>
          ))}
        </ul>
      ) : null}

      <Link
        href={`/concepts/${focus.prerequisite_slug}`}
        className={cn(buttonVariants(), "mt-5 inline-flex w-full justify-center")}
      >
        Review {focus.prerequisite_name}
      </Link>
    </section>
  );
}
