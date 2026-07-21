import { AnalyticsView } from "@/components/analytics/analytics-view";
import { fetchAnalytics } from "@/lib/api/analytics";

export default async function AnalyticsPage() {
  const analytics = await fetchAnalytics();
  return <AnalyticsView analytics={analytics} />;
}
