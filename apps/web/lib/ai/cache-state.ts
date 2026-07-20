export function shouldShowAiCacheState(): boolean {
  return (
    process.env.NODE_ENV === "development" || process.env.NEXT_PUBLIC_SHOW_AI_CACHE_STATE === "true"
  );
}
