import { AdminReviewView } from "@/components/admin/admin-review-view";
import { fetchReviewQueue } from "@/lib/api/admin-review";

export default async function AdminReviewPage() {
  let initialItems: Awaited<ReturnType<typeof fetchReviewQueue>>["items"] = [];
  try {
    const queue = await fetchReviewQueue("draft");
    initialItems = queue.items;
  } catch {
    initialItems = [];
  }

  return <AdminReviewView initialItems={initialItems} />;
}
