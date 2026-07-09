import { PlaceholderPage } from "@/components/placeholder-page";

type ConceptPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ConceptPage({ params }: ConceptPageProps) {
  const { slug } = await params;

  return (
    <PlaceholderPage
      title={`Concept: ${slug}`}
      description="Concept pages with definitions, formulas, and graph neighbors arrive in QP-016."
    />
  );
}
