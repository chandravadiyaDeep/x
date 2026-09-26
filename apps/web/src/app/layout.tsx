import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "NUMPA — Clean data, measured readiness",
  description: "Smart Data Cleaning and ML Readiness Assessment in one workflow.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-full flex flex-col">
        <nav
          className="sticky top-0 z-20 border-b"
          style={{ borderColor: "var(--line)", background: "rgba(8,13,23,0.85)", backdropFilter: "blur(10px)" }}
        >
          <div className="max-w-6xl mx-auto px-7 py-4 flex items-center justify-between gap-5">
            <Link href="/" className="flex items-center gap-2 font-bold text-lg">
              <span
                className="inline-block w-2.5 h-2.5 rounded-[3px]"
                style={{ background: "linear-gradient(135deg, var(--blue), var(--cyan))" }}
              />
              NUMPA
            </Link>
            <div className="flex items-center gap-4 text-sm" style={{ color: "var(--muted)" }}>
              <Link href="/">Dashboard</Link>
              <Link href="/upload">Upload</Link>
            </div>
          </div>
        </nav>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
