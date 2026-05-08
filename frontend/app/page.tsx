"use client";

/**
 * Home page — main query input for legal issue search.
 * Features: animated hero, full-width search textarea, example prompts, category shortcuts.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/TranslationContext";

import LanguageSwitcher from "@/components/LanguageSwitcher";
import ModeToggle from "@/components/ModeToggle";
import QueryInput from "@/components/QueryInput";
import { queryLaws, type QueryResponse } from "@/lib/api";
import { useMode } from "@/lib/useMode";

const CATEGORIES = [
  { id: "criminal", icon: "⚖️", color: "from-red-500/20 to-red-600/10 border-red-500/20 hover:border-red-500/40" },
  { id: "civil", icon: "📋", color: "from-blue-500/20 to-blue-600/10 border-blue-500/20 hover:border-blue-500/40" },
  { id: "consumer", icon: "🛡️", color: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/20 hover:border-emerald-500/40" },
];

export default function HomePage() {
  const { t, langCode } = useLanguage();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mode = useMode();

  const handleQuery = async (query: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const result: QueryResponse = await queryLaws(query, langCode, mode);

      // Store result in sessionStorage for the results page
      sessionStorage.setItem("lexindia-results", JSON.stringify(result));
      sessionStorage.setItem("lexindia-query", query);
      router.push("/results");
    } catch (err: unknown) {
      console.error("Query failed:", err);
      setError(t("error"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCategoryClick = (category: string) => {
    const categoryQueries: Record<string, string> = {
      criminal: "Someone has been threatening me and I want to file a criminal complaint",
      civil: "I have a property dispute with my neighbor about land boundaries",
      consumer: "I bought a defective product online and the seller refuses to refund my money",
    };
    handleQuery(categoryQueries[category] || "");
  };

  const getCategoryLabel = (id: string): string => {
    const map: Record<string, "categoryCriminal" | "categoryCivil" | "categoryConsumer"> = {
      criminal: "categoryCriminal",
      civil: "categoryCivil",
      consumer: "categoryConsumer",
    };
    return t(map[id] || "categoryCriminal");
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Navigation ───────────────────────────────────────────────── */}
      <nav className={`w-full px-6 py-4 flex items-center justify-between border-b backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50 ${mode === "lawyer" ? "border-amber-500/50 border-b-2" : "border-surface-800/50"}`}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-saffron-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <span className="text-white font-bold text-sm">LI</span>
          </div>
          <span className="font-display font-bold text-xl text-surface-50">
            Lex<span className="gradient-text">India</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <ModeToggle />
          <a
            href="/browse"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors hidden sm:block"
            id="nav-browse"
          >
            {t("browseLaws")}
          </a>
          <a
            href="/drafting"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors hidden sm:block"
            id="nav-drafting"
          >
            📝 {t("navDraft")}
          </a>
          <a
            href="/judgments/browse"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors hidden sm:block"
            id="nav-judgments"
          >
            ⚖️ {t("navJudgments")}
          </a>
          <LanguageSwitcher />
        </div>
      </nav>

      {/* ── Hero Section ─────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-16 sm:py-24">
        {/* Decorative gradient orbs */}
        <div className="absolute top-32 left-1/4 w-72 h-72 bg-brand-500/8 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-32 right-1/4 w-64 h-64 bg-saffron-500/6 rounded-full blur-3xl pointer-events-none" />

        <div className="relative text-center mb-12 animate-fade-up">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/20 mb-6">
            <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse-soft" />
            <span className="text-sm text-brand-300 font-medium">
              {t("aiPoweredLegalAccess")}
            </span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-display font-bold text-surface-50 mb-5 text-balance leading-[1.1]">
            {t("knowYourRights")}{" "}
            <span className="gradient-text">&nbsp;</span>
            <br />
            {t("underIndianLaw")}
          </h1>

          <p className="text-lg sm:text-xl text-surface-400 max-w-2xl mx-auto text-balance leading-relaxed">
            {t("tagline")}
          </p>
        </div>

        {/* ── Query Input ──────────────────────────────────────────── */}
        <div className="w-full max-w-3xl animate-fade-up" style={{ animationDelay: "150ms" }}>
          <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
        </div>

        {/* ── Error Message ────────────────────────────────────────── */}
        {error && (
          <div className="mt-6 px-5 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-fade-in max-w-lg">
            {error}
          </div>
        )}

        {/* ── Loading Skeleton ─────────────────────────────────────── */}
        {isLoading && (
          <div className="mt-10 w-full max-w-3xl space-y-4 animate-fade-in">
            <p className="text-center text-surface-400 text-sm mb-4 animate-pulse-soft">
              {t("loading")}
            </p>
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="glass-card p-6"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="flex gap-4">
                  <div className="flex-1 space-y-3">
                    <div className="h-4 bg-surface-700 rounded-lg shimmer w-1/3" />
                    <div className="h-5 bg-surface-700 rounded-lg shimmer w-2/3" />
                    <div className="h-4 bg-surface-700 rounded-lg shimmer w-full" />
                    <div className="h-4 bg-surface-700 rounded-lg shimmer w-4/5" />
                  </div>
                  <div className="h-12 w-16 bg-surface-700 rounded-lg shimmer" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Category Shortcuts ───────────────────────────────────── */}
        <div
          className="mt-14 flex flex-wrap gap-4 justify-center animate-fade-up"
          style={{ animationDelay: "300ms" }}
        >
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategoryClick(cat.id)}
              className={`
                flex items-center gap-3 px-6 py-4 rounded-2xl
                bg-gradient-to-br ${cat.color} border
                backdrop-blur-sm
                hover:scale-[1.02] active:scale-[0.98]
                transition-all duration-200
              `}
              id={`category-${cat.id}`}
            >
              <span className="text-2xl">{cat.icon}</span>
              <span className="font-medium text-surface-200">
                {getCategoryLabel(cat.id)}
              </span>
            </button>
          ))}
        </div>
      </main>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer className="w-full px-6 py-6 text-center border-t border-surface-800/50">
        <p className="text-sm text-surface-500">
          {t("footerText")}
        </p>
      </footer>
    </div>
  );
}
