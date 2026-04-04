/**
 * Root layout for LexIndia — applies global styles, fonts, metadata, and i18n provider.
 */

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LexIndia — AI-Powered Indian Legal Access",
  description:
    "Describe your legal problem in plain language (English, Tamil, or Hindi) and get applicable Indian laws, simplified explanations, and court filing links.",
  keywords: [
    "Indian law",
    "legal help",
    "AI legal assistant",
    "Indian Penal Code",
    "consumer protection",
    "court filing",
  ],
  authors: [{ name: "LexIndia" }],
  openGraph: {
    title: "LexIndia — AI-Powered Indian Legal Access",
    description:
      "Find applicable Indian laws from plain-language queries. Supports English, Tamil, and Hindi.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body className="min-h-screen">
        {children}
      </body>
    </html>
  );
}
