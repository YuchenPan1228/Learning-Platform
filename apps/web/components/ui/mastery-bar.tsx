import { masteryTone, masteryWidth } from "@/lib/mastery";
import { cn } from "@/lib/utils";

export function MasteryBar({ score, className }: { score: number; className?: string }) {
  return (
    <div className={cn("h-2 overflow-hidden rounded-full bg-[#edf5f1]", className)}>
      <div
        className={cn("h-full rounded-full transition-all", masteryTone(score))}
        style={{ width: masteryWidth(score) }}
      />
    </div>
  );
}
