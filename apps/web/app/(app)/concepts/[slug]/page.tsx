import { notFound } from "next/navigation";

import { ConceptDetailView } from "@/components/concepts/concept-detail-view";
import { fetchConcept } from "@/lib/api/concepts";

type ConceptPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ConceptPage({ params }: ConceptPageProps) {
  const { slug } = await params;
  const concept = await fetchConcept(slug);

  if (concept === null) {
    notFound();
  }

  return <ConceptDetailView concept={concept} />;
}
