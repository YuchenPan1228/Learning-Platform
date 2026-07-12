import type { ConceptNeighbor } from "@/lib/types/concept";

export type NeighborGroup = {
  title: string;
  neighbors: ConceptNeighbor[];
};

export function groupConceptNeighbors(neighbors: ConceptNeighbor[]): NeighborGroup[] {
  const prerequisites = neighbors.filter(
    (neighbor) => neighbor.relationship_type === "requires" && neighbor.direction === "outgoing",
  );
  const requiredBy = neighbors.filter(
    (neighbor) => neighbor.relationship_type === "requires" && neighbor.direction === "incoming",
  );
  const related = neighbors.filter((neighbor) => neighbor.relationship_type === "related_to");
  const usedIn = neighbors.filter(
    (neighbor) => neighbor.relationship_type === "used_in" && neighbor.direction === "outgoing",
  );
  const uses = neighbors.filter(
    (neighbor) => neighbor.relationship_type === "used_in" && neighbor.direction === "incoming",
  );

  return [
    { title: "Prerequisites", neighbors: prerequisites },
    { title: "Required by", neighbors: requiredBy },
    { title: "Related concepts", neighbors: related },
    { title: "Used in", neighbors: usedIn },
    { title: "Uses", neighbors: uses },
  ].filter((group) => group.neighbors.length > 0);
}

export function neighborRelationLabel(neighbor: ConceptNeighbor): string {
  if (neighbor.relationship_type === "requires") {
    return neighbor.direction === "outgoing" ? "Prerequisite" : "Dependent";
  }
  if (neighbor.relationship_type === "related_to") {
    return "Related";
  }
  return neighbor.direction === "outgoing" ? "Application" : "Uses";
}
