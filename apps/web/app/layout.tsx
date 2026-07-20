import type { Metadata } from "next";
import { Inter } from "next/font/google";

import "katex/dist/katex.min.css";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "Quant Prep AI",
  description: "AI-assisted quant interview prep for local MVP development.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full bg-[#f6f7f4] text-[#15201c]">{children}</body>
    </html>
  );
}
