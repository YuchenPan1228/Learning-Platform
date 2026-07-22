import { AdminReviewView } from "@/components/admin/admin-review-view";
import { fetchReviewQueue } from "@/lib/api/admin-review";
import { fetchTopics } from "@/lib/api/topics";

export default async function AdminReviewPage() {
  let initialItems: Awaited<ReturnType<typeof fetchReviewQueue>>["items"] = [];
  let topics: Awaited<ReturnType<typeof fetchTopics>> = [];

  try {
    const queue = await fetchReviewQueue("draft");
    initialItems = queue.items;
  } catch {
    initialItems = [];
  }

  try {
    topics = await fetchTopics();
  } catch {
    topics = [];
  }

  return <AdminReviewView initialItems={initialItems} topics={topics} />;
}
