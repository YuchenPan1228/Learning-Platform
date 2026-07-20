export type ConceptTextSegment = {
  type: "text";
  value: string;
};

export type ConceptCodeSegment = {
  type: "code";
  lang: string;
  value: string;
};

export type ConceptContentSegment = ConceptTextSegment | ConceptCodeSegment;

const FENCE_RE = /```([\w+-]*)\r?\n([\s\S]*?)```/g;

const CODE_START_RE =
  /^(def |class |async def |from |import |@{1,2}|#include\b|using |namespace |template\b|std::|SELECT |WITH |CREATE |INSERT |UPDATE |DELETE |int main\b)/;

function isCodeContinuation(line: string): boolean {
  if (!line.trim()) {
    return true;
  }
  if (/^\s/.test(line)) {
    return true;
  }
  return (
    /^(return |if |elif |else:|for |while |try:|except |finally:|with |pass\b|break\b|continue\b|yield |raise |assert |global |nonlocal |lambda |print\(|#)/.test(
      line,
    ) || CODE_START_RE.test(line)
  );
}

/** Split fenced ```lang blocks from prose; also lift unfenced Python-like code after a title line. */
export function splitConceptContent(content: string): ConceptContentSegment[] {
  const fenced = splitFenced(content);
  return fenced.flatMap((segment) => {
    if (segment.type === "code") {
      return [segment];
    }
    return liftUnfencedCode(segment.value);
  });
}

function splitFenced(content: string): ConceptContentSegment[] {
  const segments: ConceptContentSegment[] = [];
  let lastIndex = 0;

  for (const match of content.matchAll(FENCE_RE)) {
    const index = match.index ?? 0;
    if (index > lastIndex) {
      segments.push({ type: "text", value: content.slice(lastIndex, index) });
    }
    segments.push({
      type: "code",
      lang: match[1] || "text",
      value: match[2].replace(/\n$/, ""),
    });
    lastIndex = index + match[0].length;
  }

  if (lastIndex < content.length) {
    segments.push({ type: "text", value: content.slice(lastIndex) });
  }

  return segments.length > 0 ? segments : [{ type: "text", value: content }];
}

function liftUnfencedCode(text: string): ConceptContentSegment[] {
  const blocks = text
    .split(/\n{2,}/)
    .map((block) => block.trimEnd())
    .filter((block) => block.trim().length > 0);

  const segments: ConceptContentSegment[] = [];

  for (const block of blocks) {
    const lines = block.split("\n");
    const codeStart = lines.findIndex((line) => CODE_START_RE.test(line));

    if (codeStart < 0) {
      segments.push({ type: "text", value: block });
      continue;
    }

    const proseLines = lines.slice(0, codeStart);
    const codeLines = lines.slice(codeStart);

    // Require the rest of the block to look like code (avoid false positives).
    const restLooksLikeCode =
      codeLines.length >= 2 &&
      codeLines.slice(1).every((line) => isCodeContinuation(line) || CODE_START_RE.test(line));

    if (!restLooksLikeCode) {
      segments.push({ type: "text", value: block });
      continue;
    }

    if (proseLines.some((line) => line.trim())) {
      segments.push({ type: "text", value: proseLines.join("\n").trimEnd() });
    }
    segments.push({
      type: "code",
      lang: inferLang(codeLines[0] ?? ""),
      value: codeLines.join("\n").replace(/\n$/, ""),
    });
  }

  return segments;
}

function inferLang(firstLine: string): string {
  if (/^(SELECT |WITH |CREATE |INSERT |UPDATE |DELETE )/i.test(firstLine)) {
    return "sql";
  }
  if (/^(#include|using |namespace |std::|int main|template\b)/.test(firstLine)) {
    return "cpp";
  }
  return "python";
}
