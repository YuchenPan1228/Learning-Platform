import { AdminImportForm } from "@/components/admin/admin-import-form";
import { fetchTopics } from "@/lib/api/topics";

export default async function AdminImportPage() {
  let topics: Awaited<ReturnType<typeof fetchTopics>> = [];
  try {
    topics = await fetchTopics();
  } catch {
    topics = [];
  }

  return <AdminImportForm topics={topics} />;
}
