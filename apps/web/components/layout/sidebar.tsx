"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { adminNavItems, isNavItemActive, mainNavItems } from "@/lib/navigation";
import { cn } from "@/lib/utils";

function NavLink({ href, label }: { href: string; label: string }) {
  const pathname = usePathname();
  const active = isNavItemActive(pathname, href);

  return (
    <Link
      href={href}
      className={cn(
        "flex min-h-[42px] items-center rounded-lg border px-3 text-sm text-[#31443d] transition-colors",
        active
          ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
          : "border-transparent hover:border-[#bdd3ca] hover:bg-[#edf5f1] hover:text-[#176b54]",
      )}
    >
      {label}
    </Link>
  );
}

export function Sidebar() {
  return (
    <aside className="sticky top-0 flex h-screen flex-col gap-6 border-r border-[#dfe6e1] bg-[#fbfcfa] p-6">
      <div className="flex items-center gap-3">
        <div className="grid size-[42px] place-items-center rounded-lg border border-[#9fb7ac] bg-[#e7f1ed] text-sm font-extrabold text-[#176b54]">
          QP
        </div>
        <div>
          <strong className="block text-sm text-[#15201c]">Quant Prep AI</strong>
          <span className="block text-[13px] text-[#66736e]">Interview training</span>
        </div>
      </div>

      <nav className="grid gap-1.5" aria-label="Primary">
        {mainNavItems.map((item) => (
          <NavLink key={item.href} href={item.href} label={item.label} />
        ))}
      </nav>

      <nav className="grid gap-1.5" aria-label="Admin">
        <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
          Admin
        </span>
        {adminNavItems.map((item) => (
          <NavLink key={item.href} href={item.href} label={item.label} />
        ))}
      </nav>

      <div className="mt-auto rounded-lg border border-[#dfe6e1] bg-white p-4">
        <span className="text-xs font-semibold tracking-wide text-[#66736e] uppercase">
          Today
        </span>
        <strong className="mt-1 block text-sm text-[#15201c]">90 min plan</strong>
        <p className="mt-2 text-sm leading-relaxed text-[#66736e]">
          Study planner content arrives in Phase 2.
        </p>
      </div>
    </aside>
  );
}
