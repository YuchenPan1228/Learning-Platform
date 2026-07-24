import { AdminConceptsView } from "@/components/admin/admin-concepts-view";
import { fetchAdminConcepts } from "@/lib/api/admin-concepts";
import { fetchTopics } from "@/lib/api/topics";

export default async function AdminConceptsPage() {
  let topics: Awaited<ReturnType<typeof fetchTopics>> = [];
  let initialConcepts: Awaited<ReturnType<typeof fetchAdminConcepts>> = [];

  try {
    topics = await fetchTopics();
  } catch {
    topics = [];
  }

  try {
    initialConcepts = await fetchAdminConcepts();
  } catch {
    initialConcepts = [];
  }

  return <AdminConceptsView topics={topics} initialConcepts={initialConcepts} />;
}
