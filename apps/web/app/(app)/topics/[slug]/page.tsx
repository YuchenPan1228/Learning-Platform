import { PlaceholderPage } from "@/components/placeholder-page";

type TopicDetailPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function TopicDetailPage({ params }: TopicDetailPageProps) {
  const { slug } = await params;

  return (
    <PlaceholderPage
      title={`Topic: ${slug}`}
      description="Topic detail content will be added in Phase 2 after topic APIs and seeds land."
    />
  );
}
