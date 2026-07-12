type ConceptSectionProps = {
  title: string;
  content: string;
};

export function ConceptSection({ title, content }: ConceptSectionProps) {
  return (
    <section>
      <h3 className="text-sm font-semibold text-[#15201c]">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-[#66736e]">{content}</p>
    </section>
  );
}
