import { formatTopicLabel, getTopicPalette } from "@/lib/topic-colors";
import { cn } from "@/lib/utils";

export function TopicBadge({
  slug,
  label,
  className,
}: {
  slug: string;
  label?: string;
  className?: string;
}) {
  const palette = getTopicPalette(slug);

  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2.5 py-0.5 text-[11px] font-semibold tracking-wide uppercase",
        palette.border,
        palette.badge,
        palette.badgeText,
        className,
      )}
    >
      {label ?? palette.label ?? formatTopicLabel(slug)}
    </span>
  );
}
