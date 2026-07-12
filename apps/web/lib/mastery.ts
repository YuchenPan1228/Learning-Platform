export function masteryTone(score: number): string {
  if (score < 35) {
    return "bg-[#b42318]";
  }
  if (score < 55) {
    return "bg-[#b7791f]";
  }
  return "bg-[#176b54]";
}

export function formatMasteryScore(score: number): string {
  return `${Math.round(score)}%`;
}

export function masteryWidth(score: number): string {
  return `${Math.min(Math.max(score, 0), 100)}%`;
}
