import { AdminFlashcardsView } from "@/components/admin/admin-flashcards-view";
import { fetchAdminFlashcards } from "@/lib/api/admin-flashcards";
import { fetchTopics } from "@/lib/api/topics";

export default async function AdminFlashcardsPage() {
  let topics: Awaited<ReturnType<typeof fetchTopics>> = [];
  let initialFlashcards: Awaited<ReturnType<typeof fetchAdminFlashcards>> = [];

  try {
    topics = await fetchTopics();
  } catch {
    topics = [];
  }

  try {
    initialFlashcards = await fetchAdminFlashcards();
  } catch {
    initialFlashcards = [];
  }

  return <AdminFlashcardsView topics={topics} initialFlashcards={initialFlashcards} />;
}
