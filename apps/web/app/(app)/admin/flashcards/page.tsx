import { redirect } from "next/navigation";

/** Admin flashcard editor is paused; keep route as a stable redirect. */
export default function AdminFlashcardsPage() {
  redirect("/admin/questions");
}
