import { createHighlighter, type BundledLanguage, type Highlighter } from "shiki";

const THEME = "github-light";
const LANGS = ["python", "cpp", "c", "sql", "typescript", "javascript", "bash", "text"] as const;

type SupportedLang = (typeof LANGS)[number];

let highlighterPromise: Promise<Highlighter> | null = null;

function getHighlighter(): Promise<Highlighter> {
  if (!highlighterPromise) {
    highlighterPromise = createHighlighter({
      themes: [THEME],
      langs: [...LANGS],
    });
  }
  return highlighterPromise;
}

export function normalizeCodeLang(lang: string | undefined): BundledLanguage {
  const raw = (lang ?? "text").trim().toLowerCase();
  const aliases: Record<string, SupportedLang> = {
    py: "python",
    python3: "python",
    "c++": "cpp",
    cxx: "cpp",
    js: "javascript",
    ts: "typescript",
    sh: "bash",
    shell: "bash",
    plaintext: "text",
    txt: "text",
  };
  const resolved = aliases[raw] ?? (LANGS.includes(raw as SupportedLang) ? (raw as SupportedLang) : "text");
  return resolved as BundledLanguage;
}

export async function highlightCode(code: string, lang?: string): Promise<string> {
  const highlighter = await getHighlighter();
  const language = normalizeCodeLang(lang);
  return highlighter.codeToHtml(code.replace(/\n$/, ""), {
    lang: language,
    theme: THEME,
  });
}
