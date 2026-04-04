"use client";

/**
 * Results page — displays AI summary and matching law cards.
 * Renders LawCard components sorted by relevance_score descending.
 * Reads query results from sessionStorage (set by the home page on submit).
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import "@/lib/i18n";

import LanguageSwitcher from "@/components/LanguageSwitcher";
import LawCard from "@/components/LawCard";
import type { QueryResponse } from "@/lib/api";

export default function ResultsPage() {
  const { t } = useTranslation();
  const router = useRouter();
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const stored = sessionStorage.getItem("lexindia-results");
    const storedQuery = sessionStorage.getItem("lexindia-query");

    if (stored) {
      try {
        setResults(JSON.parse(stored));
      } catch {
        router.push("/");
      }
    } else {
      router.push("/");
    }

    if (storedQuery) {
      setQuery(storedQuery);
    }
  }, [router]);

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Navigation ───────────────────────────────────────────────── */}
      <nav className="w-full px-6 py-4 flex items-center justify-between border-b border-surface-800/50 backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50">
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-3 hover:opacity-80 transition-opacity"
          id="nav-home"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-saffron-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <span className="text-white font-bold text-sm">LI</span>
          </div>
          <span className="font-display font-bold text-xl text-surface-50">
            Lex<span className="gradient-text">India</span>
          </span>
        </button>
        <div className="flex items-center gap-4">
          <a
            href="/browse"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors hidden sm:block"
          >
            {t("browseLaws")}
          </a>
          <LanguageSwitcher />
        </div>
      </nav>

      {/* ── Main Content ─────────────────────────────────────────────── */}
      <main className="flex-1 px-6 py-8 max-w-4xl mx-auto w-full">
        {/* Back + Query */}
        <div className="mb-8 animate-fade-in">
          <button
            onClick={() => router.push("/")}
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors mb-4 flex items-center gap-1"
            id="back-btn"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            New search
          </button>

          {query && (
            <div className="glass-card p-4">
              <p className="text-sm text-surface-500 mb-1">Your query:</p>
              <p className="text-surface-200">{query}</p>
            </div>
          )}
        </div>

        {/* Response Time */}
        <div className="flex items-center gap-3 mb-6 animate-fade-in" style={{ animationDelay: "100ms" }}>
          <span className="text-xs text-surface-500">
            {results.laws.length} {results.laws.length === 1 ? "result" : "results"} found in {results.response_ms}ms
          </span>
          {results.detected_language !== "en" && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20">
              Detected: {results.detected_language === "ta" ? "Tamil" : "Hindi"}
            </span>
          )}
        </div>

        {/* AI Summary */}
        {results.ai_summary && (
          <div className="mb-8 animate-fade-up" style={{ animationDelay: "150ms" }}>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-brand-400 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
              </svg>
              {t("aiSummaryTitle")}
            </h2>
            <div className="glass-card p-6 border-l-4 border-l-brand-500">
              <p className="text-surface-200 leading-relaxed text-[15px]">
                {results.ai_summary}
              </p>
            </div>
          </div>
        )}

        {/* Law Cards */}
        {results.laws.length > 0 ? (
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-surface-400 mb-4">
              {t("resultsTitle")} ({results.laws.length})
            </h2>
            <div className="space-y-4">
              {results.laws.map((law, index) => (
                <LawCard key={law.section_id} law={law} index={index} />
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-16 animate-fade-in">
            <div className="text-5xl mb-4">🔍</div>
            <p className="text-surface-400 text-lg">{t("noResults")}</p>
          </div>
        )}
      </main>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer className="w-full px-6 py-6 text-center border-t border-surface-800/50">
        <p className="text-sm text-surface-500">
          LexIndia — AI-powered legal access for every Indian citizen
        </p>
      </footer>
    </div>
  );
}
