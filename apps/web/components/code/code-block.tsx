import { highlightCode } from "@/lib/shiki";

type CodeBlockProps = {
  code: string;
  lang?: string;
};

export async function CodeBlock({ code, lang = "python" }: CodeBlockProps) {
  const html = await highlightCode(code, lang);

  return (
    <div
      className="code-block overflow-hidden rounded-lg border border-[#e2e8f0] text-[13px] leading-[1.55] [&_pre]:m-0 [&_pre]:overflow-x-auto [&_pre]:p-3.5 [&_code]:font-mono"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
