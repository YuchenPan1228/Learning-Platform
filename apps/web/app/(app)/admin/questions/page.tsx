import { AdminQuestionsView } from "@/components/admin/admin-questions-view";
import { fetchAdminQuestions } from "@/lib/api/admin-questions";
import { fetchTopics } from "@/lib/api/topics";

export default async function AdminQuestionsPage() {
  let topics: Awaited<ReturnType<typeof fetchTopics>> = [];
  let initialQuestions: Awaited<ReturnType<typeof fetchAdminQuestions>> = [];

  try {
    topics = await fetchTopics();
  } catch {
    topics = [];
  }

  try {
    initialQuestions = await fetchAdminQuestions({ status: "approved" });
  } catch {
    initialQuestions = [];
  }

  return <AdminQuestionsView topics={topics} initialQuestions={initialQuestions} />;
}
