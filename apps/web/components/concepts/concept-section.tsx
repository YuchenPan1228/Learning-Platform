import type { CSSProperties, ReactNode } from "react";

import { CodeBlock } from "@/components/code/code-block";
import { MathText } from "@/components/math/math-text";
import { splitConceptContent } from "@/lib/concept-content-segments";

export type ConceptSectionTone =
  "definition" | "insight" | "formula" | "example" | "tips" | "mistakes" | "prerequisites";

type SectionToneStyles = {
  accent: string;
  label: string;
};

const SECTION_TONES: Record<ConceptSectionTone, SectionToneStyles> = {
  definition: { accent: "#3b82f6", label: "#1d4ed8" },
  insight: { accent: "#0f766e", label: "#0f766e" },
  formula: { accent: "#4f46e5", label: "#4338ca" },
  example: { accent: "#d97706", label: "#b45309" },
  tips: { accent: "#2563eb", label: "#1e40af" },
  mistakes: { accent: "#e11d48", label: "#be123c" },
  prerequisites: { accent: "#64748b", label: "#475569" },
};

const BODY_TEXT: CSSProperties = {
  margin: 0,
  fontSize: 14,
  lineHeight: 1.55,
  color: "#334155",
};

function renderTextBody(content: string, monospace = false): ReactNode {
  const blocks = content
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean);

  if (blocks.length === 0) {
    return null;
  }

  return (
    <div style={{ display: "grid", gap: 10 }}>
      {blocks.map((block, blockIndex) => {
        const lines = block
          .split("\n")
          .map((line) => line.trim())
          .filter(Boolean);
        const isNumberedList = lines.length > 1 && lines.every((line) => /^\d+\.\s+/.test(line));
        const isBulletList = lines.length > 1 && lines.every((line) => /^[-•]\s+/.test(line));

        if (isNumberedList) {
          return (
            <ol
              key={`block-${blockIndex}`}
              style={{ ...BODY_TEXT, paddingLeft: 18, display: "grid", gap: 5 }}
            >
              {lines.map((line, lineIndex) => (
                <li key={`line-${lineIndex}`}>
                  <MathText text={line.replace(/^\d+\.\s+/, "")} />
                </li>
              ))}
            </ol>
          );
        }

        if (isBulletList) {
          return (
            <ul
              key={`block-${blockIndex}`}
              style={{ ...BODY_TEXT, paddingLeft: 18, display: "grid", gap: 5 }}
            >
              {lines.map((line, lineIndex) => (
                <li key={`line-${lineIndex}`}>
                  <MathText text={line.replace(/^[-•]\s+/, "")} />
                </li>
              ))}
            </ul>
          );
        }

        if (monospace || lines.length > 1) {
          return (
            <div
              key={`block-${blockIndex}`}
              style={{
                overflow: "hidden",
                borderRadius: 8,
                border: "1px solid #e2e8f0",
                backgroundColor: "#f8fafc",
              }}
            >
              {lines.map((line, lineIndex) => (
                <div
                  key={`line-${lineIndex}`}
                  style={{
                    ...BODY_TEXT,
                    padding: "7px 12px",
                    borderTop: lineIndex > 0 ? "1px solid #e2e8f0" : undefined,
                    overflowX: "auto",
                  }}
                >
                  <MathText text={line} />
                </div>
              ))}
            </div>
          );
        }

        return (
          <p key={`block-${blockIndex}`} style={BODY_TEXT}>
            <MathText text={block} />
          </p>
        );
      })}
    </div>
  );
}

async function renderBody(content: string, monospace = false): Promise<ReactNode> {
  // Formula cards stay on the monospace card layout (not Shiki).
  if (monospace) {
    return renderTextBody(content, true);
  }

  const segments = splitConceptContent(content);
  const hasCode = segments.some((segment) => segment.type === "code");
  if (!hasCode) {
    return renderTextBody(content, false);
  }

  const nodes: ReactNode[] = [];
  for (const [index, segment] of segments.entries()) {
    if (segment.type === "text") {
      const textNode = renderTextBody(segment.value, false);
      if (textNode) {
        nodes.push(<div key={`text-${index}`}>{textNode}</div>);
      }
      continue;
    }
    nodes.push(<CodeBlock key={`code-${index}`} code={segment.value} lang={segment.lang} />);
  }

  return <div style={{ display: "grid", gap: 10 }}>{nodes}</div>;
}

type ConceptSectionProps = {
  title: string;
  content: string;
  tone: ConceptSectionTone;
  monospace?: boolean;
};

export async function ConceptSection({
  title,
  content,
  tone,
  monospace = false,
}: ConceptSectionProps) {
  const styles = SECTION_TONES[tone];
  const body = await renderBody(content, monospace);

  return (
    <section
      className="concept-section-card"
      style={{
        backgroundColor: "#ffffff",
        borderStyle: "solid",
        borderWidth: "1px 1px 1px 4px",
        borderColor: `#e5e7eb #e5e7eb #e5e7eb ${styles.accent}`,
        borderRadius: 12,
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
        padding: "14px 16px",
      }}
    >
      <h3
        style={{
          margin: 0,
          fontSize: 13,
          fontWeight: 600,
          letterSpacing: "0.02em",
          lineHeight: 1.3,
          color: styles.label,
        }}
      >
        {title}
      </h3>
      <div
        style={{
          marginTop: 8,
          marginBottom: 10,
          height: 1,
          width: "100%",
          backgroundColor: "#e5e7eb",
        }}
      />
      {body}
    </section>
  );
}
