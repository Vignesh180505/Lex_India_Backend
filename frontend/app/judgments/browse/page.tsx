"use client";

/**
 * Judgments Browse page — search and filter court judgments
 * by query, court type, and legal category.
 *
 * Displays paginated judgment cards (10 per page) with links
 * to full judgments on Indian Kanoon.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/TranslationContext";

import LanguageSwitcher from "@/components/LanguageSwitcher";
import ModeToggle from "@/components/ModeToggle";
import { useMode } from "@/lib/useMode";
import { searchJudgments, type JudgmentCard } from "@/lib/api";

export default function JudgmentsBrowsePage() {
  const { t, language, langCode } = useLanguage();
  const router = useRouter();
  const mode = useMode();

  const [query, setQuery] = useState("");
  const [court, setCourt] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(0);
  const [judgments, setJudgments] = useState<JudgmentCard[]>([]);
  const [totalFound, setTotalFound] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Court options with translations
  const COURTS = [
    { value: "", label: t("allCourts") },
    { value: "Supreme Court", label: t("supremeCourt") },
    { value: "High Court", label: t("highCourt") },
    { value: "District Court", label: t("districtCourt") },
  ];

  const CATEGORIES = [
    { value: "", label: t("allCategories") },
    { value: "Criminal", label: t("criminal") },
    { value: "Civil", label: t("civil") },
    { value: "Family", label: t("family") },
    { value: "Property", label: t("property") },
    { value: "Labour", label: t("labour") },
    { value: "Consumer", label: t("consumer") },
  ];

  const handleSearch = async (searchPage: number = 0, queryOverride?: string) => {
    const searchQuery = queryOverride ?? query;
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);
    setPage(searchPage);

    try {
      const data = await searchJudgments({
        query: searchQuery.trim(),
        language: langCode,
        mode,
        court: court || undefined,
        category: category || undefined,
        page: searchPage,
      });
      setJudgments(data.judgments || []);
      setTotalFound(data.total_found || 0);
      setHasSearched(true);
    } catch (err: unknown) {
      console.error("Judgment search failed:", err);
      setError(t("error"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch(0);
    }
  };

  const totalPages = Math.ceil(totalFound / 10);

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Navigation ───────────────────────────────────────────────── */}
      <nav
        className={`w-full px-6 py-4 flex items-center justify-between border-b backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50 ${
          mode === "lawyer"
            ? "border-amber-500/50 border-b-2"
            : "border-surface-800/50"
        }`}
      >
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
          <ModeToggle />
          <a
            href="/browse"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors hidden sm:block"
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
          <LanguageSwitcher />
        </div>
      </nav>

      {/* ── Main Content ─────────────────────────────────────────────── */}
      <main className="flex-1 px-6 py-10 max-w-5xl mx-auto w-full">
        {/* Header */}
        <div className="text-center mb-10 animate-fade-up">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-saffron-500/10 border border-saffron-500/20 mb-4">
            <span className="text-lg">⚖️</span>
            <span className="text-sm text-saffron-300 font-medium">
              {t("courtJudgmentsDatabase")}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-bold text-surface-50 mb-3">
            {t("judgmentsBrowseTitle").replace("Judgments", "")}{" "}
            <span className="gradient-text">{t("navJudgments")}</span>
          </h1>
          <p className="text-surface-400 max-w-xl mx-auto">
            {t("judgmentsBrowseSubtitle")}
          </p>
        </div>

        {/* ── Search + Filters ──────────────────────────────────────── */}
        <div className="glass-card p-6 mb-8 animate-fade-up" style={{ animationDelay: "100ms" }}>
          {/* Search Input */}
          <div className="mb-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t("searchJudgmentsPlaceholder")}
              className="input-glass text-base"
              id="judgment-search-input"
            />
          </div>

          {/* Filters Row */}
          <div className="flex flex-wrap gap-3 mb-4">
            {/* Court Dropdown */}
            <div className="flex-1 min-w-[180px]">
              <label className="text-xs text-surface-500 uppercase tracking-wider mb-1 block">
                {t("court")}
              </label>
              <select
                value={court}
                onChange={(e) => setCourt(e.target.value)}
                className="w-full rounded-xl border border-surface-600/60 bg-surface-800/40 px-4 py-2.5 text-surface-100 focus:outline-none focus:border-brand-500/60 focus:ring-2 focus:ring-brand-500/20 backdrop-blur-sm transition-all duration-200 appearance-none cursor-pointer"
                id="court-filter"
              >
                {COURTS.map((c) => (
                  <option key={c.value} value={c.value} className="bg-surface-800">
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Category Dropdown */}
            <div className="flex-1 min-w-[180px]">
              <label className="text-xs text-surface-500 uppercase tracking-wider mb-1 block">
                {t("category")}
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full rounded-xl border border-surface-600/60 bg-surface-800/40 px-4 py-2.5 text-surface-100 focus:outline-none focus:border-brand-500/60 focus:ring-2 focus:ring-brand-500/20 backdrop-blur-sm transition-all duration-200 appearance-none cursor-pointer"
                id="category-filter"
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value} className="bg-surface-800">
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Search Button */}
          <button
            onClick={() => handleSearch(0)}
            disabled={isLoading || !query.trim()}
            className="btn-primary w-full sm:w-auto flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            id="judgment-search-btn"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                {t("searching")}
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                </svg>
                {t("searchJudgments")}
              </>
            )}
          </button>
        </div>

        {/* ── Error Message ────────────────────────────────────────── */}
        {error && (
          <div className="mb-6 px-5 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-fade-in">
            {error}
          </div>
        )}

        {/* ── Loading Skeletons ────────────────────────────────────── */}
        {isLoading && (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="glass-card p-5">
                <div className="space-y-3">
                  <div className="h-5 bg-surface-700 rounded-lg shimmer w-3/4" />
                  <div className="flex gap-3">
                    <div className="h-3 bg-surface-700 rounded-lg shimmer w-24" />
                    <div className="h-3 bg-surface-700 rounded-lg shimmer w-20" />
                  </div>
                  <div className="h-3 bg-surface-700 rounded-lg shimmer w-full" />
                  <div className="h-3 bg-surface-700 rounded-lg shimmer w-4/5" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Results ──────────────────────────────────────────────── */}
        {!isLoading && hasSearched && (
          <>
            {/* Results Count */}
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-surface-500">
                {totalFound > 0
                  ? `${t("showing")} ${page * 10 + 1}–${Math.min((page + 1) * 10, totalFound)} ${t("of")} ${totalFound} ${t("judgments")}`
                  : t("noJudgmentsFound")}
              </span>
              {(court || category) ? (
                <div className="flex items-center gap-2">
                  {court && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20">
                      {court}
                    </span>
                  )}
                  {category && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-saffron-500/10 text-saffron-400 border border-saffron-500/20">
                      {category}
                    </span>
                  )}
                </div>
              ) : null}
            </div>

            {/* Judgment Cards */}
            {judgments.length > 0 ? (
              <div className="space-y-4">
                {judgments.map((judgment, index) => (
                  <div
                    key={judgment.doc_id}
                    className="glass-card p-5 animate-fade-up"
                    style={{ animationDelay: `${index * 60}ms` }}
                    id={`judgment-card-${judgment.doc_id}`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-base font-display font-semibold text-surface-50 mb-1.5 leading-snug">
                          {judgment.title}
                        </h3>
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                          <span className="text-xs text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded-md">
                            {judgment.court}
                          </span>
                          {judgment.date && (
                            <span className="text-xs text-surface-500">
                              📅 {judgment.date}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-surface-300 leading-relaxed line-clamp-3">
                          {judgment.snippet}
                        </p>
                      </div>
                      <a
                        href={judgment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="shrink-0 btn-secondary text-xs flex items-center gap-1.5 whitespace-nowrap"
                        id={`read-judgment-${judgment.doc_id}`}
                      >
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                        </svg>
                        {t("readFullJudgment")}
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16 animate-fade-in">
                <div className="text-5xl mb-4">📄</div>
                <p className="text-surface-400 text-lg">
                  {t("noJudgmentsFound")}
                </p>
                <p className="text-surface-500 text-sm mt-2">
                  {t("tryDifferentKeywords")}
                </p>
              </div>
            )}

            {/* ── Pagination ───────────────────────────────────────── */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-8">
                <button
                  onClick={() => handleSearch(page - 1)}
                  disabled={page === 0}
                  className="btn-secondary text-sm disabled:opacity-30 disabled:cursor-not-allowed"
                  id="prev-page"
                >
                  {t("prevPage")}
                </button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    const pageNum =
                      totalPages <= 5
                        ? i
                        : page < 3
                        ? i
                        : page > totalPages - 3
                        ? totalPages - 5 + i
                        : page - 2 + i;
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handleSearch(pageNum)}
                        className={`w-9 h-9 rounded-lg text-sm font-medium transition-all duration-200 ${
                          pageNum === page
                            ? "bg-brand-500 text-white shadow-lg shadow-brand-500/25"
                            : "text-surface-400 hover:bg-surface-700/50 hover:text-surface-200"
                        }`}
                        id={`page-${pageNum}`}
                      >
                        {pageNum + 1}
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={() => handleSearch(page + 1)}
                  disabled={page >= totalPages - 1}
                  className="btn-secondary text-sm disabled:opacity-30 disabled:cursor-not-allowed"
                  id="next-page"
                >
                  {t("nextPage")}
                </button>
              </div>
            )}
          </>
        )}

        {/* ── Empty State (before search) ──────────────────────────── */}
        {!isLoading && !hasSearched && (
          <div className="text-center py-20 animate-fade-in">
            <div className="text-6xl mb-6">⚖️</div>
            <h2 className="text-xl font-display font-semibold text-surface-200 mb-2">
              {t("searchCourtJudgments")}
            </h2>
            <p className="text-surface-500 max-w-md mx-auto">
              {t("searchCourtJudgmentsSubtitle")}
            </p>

            {/* Quick Search Suggestions */}
            <div className="flex flex-wrap justify-center gap-2 mt-8">
              {[
                "property dispute",
                "tenant eviction",
                "consumer complaint",
                "wrongful termination",
                "dowry harassment",
                "cheque bounce",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setQuery(suggestion);
                    handleSearch(0, suggestion);
                  }}
                  className="px-4 py-2 rounded-xl text-sm bg-surface-800/60 border border-surface-700/40 text-surface-300 hover:bg-surface-700/60 hover:text-surface-100 hover:border-surface-600/60 transition-all duration-200"
                  id={`suggestion-${suggestion.replace(/\s+/g, "-")}`}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
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
