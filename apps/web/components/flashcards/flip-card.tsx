import type { Flashcard } from "@/lib/types/flashcard";
import { cn } from "@/lib/utils";

type FlipCardProps = {
  flashcard: Flashcard;
  isFlipped: boolean;
  onFlip: () => void;
};

export function FlipCard({ flashcard, isFlipped, onFlip }: FlipCardProps) {
  return (
    <button
      type="button"
      onClick={onFlip}
      className={cn(
        "min-h-[280px] w-full rounded-lg border border-[#dfe6e1] bg-white p-6 text-left shadow-[0_16px_42px_rgba(21,32,28,0.08)] transition-colors",
        "hover:border-[#bdd3ca] focus-visible:border-[#0f766e] focus-visible:ring-3 focus-visible:ring-[#0f766e]/20",
      )}
      aria-pressed={isFlipped}
    >
      <p className="text-xs font-bold tracking-wide text-[#66736e] uppercase">
        {isFlipped ? "Answer" : "Prompt"} · {flashcard.topic_slug}
      </p>
      <p className="mt-4 text-xl leading-relaxed font-medium text-[#15201c]">
        {isFlipped ? flashcard.back : flashcard.front}
      </p>
      <p className="mt-6 text-sm text-[#66736e]">
        {isFlipped ? "Tap the card to hide the answer." : "Tap the card to reveal the answer."}
      </p>
    </button>
  );
}
