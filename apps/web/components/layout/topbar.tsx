"use client";

import { Search } from "lucide-react";
import { usePathname } from "next/navigation";

import { Input } from "@/components/ui/input";
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

      <div className="flex h-11 w-full max-w-[420px] items-center gap-2 rounded-lg border border-[#dfe6e1] bg-white px-3">
        <Search className="size-4 text-[#66736e]" aria-hidden="true" />
        <Input
          type="search"
          placeholder="Search topics, tags, formulas..."
          className="h-9 border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
          disabled
          aria-label="Search"
        />
      </div>
    </header>
  );
}
