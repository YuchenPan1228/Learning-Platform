type PlaceholderPageProps = {
  title: string;
  description: string;
};

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <section className="rounded-lg border border-[#dfe6e1] bg-white p-5 shadow-[0_16px_42px_rgba(21,32,28,0.08)]">
      <h2 className="text-xl font-semibold text-[#15201c]">{title}</h2>
      <p className="mt-3 text-sm leading-relaxed text-[#40524b]">{description}</p>
    </section>
  );
}
