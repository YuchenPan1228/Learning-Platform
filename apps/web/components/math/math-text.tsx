import katex from "katex";

const MATH_SEGMENT_RE =
  /(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\))/g;

function stripDelimiters(segment: string): { math: string; displayMode: boolean } {
  if (segment.startsWith("$$") && segment.endsWith("$$")) {
    return { math: segment.slice(2, -2).trim(), displayMode: true };
  }
  if (segment.startsWith("\\[") && segment.endsWith("\\]")) {
    return { math: segment.slice(2, -2).trim(), displayMode: true };
  }
  if (segment.startsWith("$") && segment.endsWith("$")) {
    return { math: segment.slice(1, -1).trim(), displayMode: false };
  }
  if (segment.startsWith("\\(") && segment.endsWith("\\)")) {
    return { math: segment.slice(2, -2).trim(), displayMode: false };
  }
  return { math: segment, displayMode: false };
}

function renderMathHtml(math: string, displayMode: boolean): string {
  return katex.renderToString(math, {
    throwOnError: false,
    displayMode,
    strict: "ignore",
    trust: false,
  });
}

export function renderMathTextHtml(text: string): string {
  const parts = text.split(MATH_SEGMENT_RE);
  return parts
    .map((part) => {
      if (!part) {
        return "";
      }
      if (
        (part.startsWith("$$") && part.endsWith("$$")) ||
        (part.startsWith("$") && part.endsWith("$")) ||
        (part.startsWith("\\[") && part.endsWith("\\]")) ||
        (part.startsWith("\\(") && part.endsWith("\\)"))
      ) {
        const { math, displayMode } = stripDelimiters(part);
        return renderMathHtml(math, displayMode);
      }
      return escapeHtml(part);
    })
    .join("");
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

type MathTextProps = {
  text: string;
  className?: string;
  as?: "span" | "div" | "p";
};

export function MathText({ text, className, as = "span" }: MathTextProps) {
  const Tag = as;
  return (
    <Tag
      className={className}
      dangerouslySetInnerHTML={{ __html: renderMathTextHtml(text) }}
    />
  );
}
