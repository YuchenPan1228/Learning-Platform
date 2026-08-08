import { redirect } from "next/navigation";

/** Flashcard learner surface is paused; keep route as a stable redirect. */
export default function FlashcardsPage() {
  redirect("/practice");
}
