import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen bg-[#f6f7f4] lg:grid-cols-[280px_minmax(0,1fr)]">
      <Sidebar />
      <main className="min-w-0 p-5 sm:p-7">
        <Topbar />
        {children}
      </main>
    </div>
  );
}
