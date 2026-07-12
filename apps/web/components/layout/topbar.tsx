"use client";

import { usePathname } from "next/navigation";

import { GlobalSearch } from "@/components/layout/global-search";
import { getPageTitle } from "@/lib/navigation";

export function Topbar() {
  const pathname = usePathname();

  return (
    <header className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <p className="mb-1 text-xs font-bold tracking-wide text-[#66736e] uppercase">
          Adaptive quant interview prep
        </p>
        <h1 className="text-3xl leading-tight font-semibold text-[#15201c] sm:text-4xl">
          {getPageTitle(pathname)}
        </h1>
      </div>

      <GlobalSearch />
    </header>
  );
}
