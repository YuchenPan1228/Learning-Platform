export type NavItem = {
  href: string;
  label: string;
};

export const mainNavItems: NavItem[] = [
  { href: "/", label: "Dashboard" },
  { href: "/topics", label: "Topics" },
  { href: "/practice", label: "Practice" },
  { href: "/mental-math", label: "Mental Math" },
  { href: "/flashcards", label: "Flashcards" },
];

export const adminNavItems: NavItem[] = [
  { href: "/admin/import", label: "Import" },
  { href: "/admin/review", label: "Review" },
];

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/topics": "Topics",
  "/practice": "Practice",
  "/mental-math": "Mental Math",
  "/flashcards": "Flashcards",
  "/admin/import": "Admin Import",
  "/admin/review": "Admin Review",
};

export function isNavItemActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

export function getPageTitle(pathname: string): string {
  if (pageTitles[pathname]) {
    return pageTitles[pathname];
  }

  if (pathname.startsWith("/topics/")) {
    return "Topic";
  }

  if (pathname.startsWith("/concepts/")) {
    return "Concept";
  }

  if (pathname.startsWith("/admin/")) {
    return "Admin";
  }

  return "Quant Prep AI";
}
