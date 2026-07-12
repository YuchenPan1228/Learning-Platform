import type { ConceptSummary } from "@/lib/types/concept";

export type PrerequisiteLink = {
  label: string;
  href: string | null;
};

function normalizeLabel(value: string): string {
  return value.trim().toLowerCase().replace(/['’]/g, "");
}

function slugifyLabel(value: string): string {
  return normalizeLabel(value)
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function resolvePrerequisiteLinks(
  prerequisites: string[] | null | undefined,
  concepts: ConceptSummary[],
): PrerequisiteLink[] {
  if (!prerequisites || prerequisites.length === 0) {
    return [];
  }

  const conceptsBySlug = new Map(concepts.map((concept) => [concept.slug, concept]));
  const conceptsByName = new Map(
    concepts.map((concept) => [normalizeLabel(concept.name), concept]),
  );

  return prerequisites.map((rawLabel) => {
    const label = rawLabel.trim();
    const slugGuess = slugifyLabel(label);
    const matched =
      conceptsBySlug.get(slugGuess) ??
      conceptsByName.get(normalizeLabel(label)) ??
      concepts.find((concept) => slugifyLabel(concept.name) === slugGuess);

    return {
      label,
      href: matched ? `/concepts/${matched.slug}` : null,
    };
  });
}

export function findRelatedConcept(
  subtopicSlug: string | null | undefined,
  concepts: ConceptSummary[],
): ConceptSummary | null {
  if (!subtopicSlug) {
    return null;
  }
  return concepts.find((concept) => concept.slug === subtopicSlug) ?? null;
}
