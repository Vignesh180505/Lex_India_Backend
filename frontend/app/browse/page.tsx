"use client";

/**
 * Browse page — browse all laws filtered by Act with text search and pagination.
 * Filter panel with one button per Act, text search, and 20 results per page.
 */

import { useEffect, useState, useCallback } from "react";
import { useLanguage } from "@/lib/TranslationContext";

import LanguageSwitcher from "@/components/LanguageSwitcher";
import LawCard from "@/components/LawCard";
import FilingModal from "@/components/FilingModal";
import { browseLaws, type LawListResponse } from "@/lib/api";

const ACTS = [
  { code: "IPC", label: "IPC", full: "Indian Penal Code 1860" },
  { code: "CrPC", label: "CrPC", full: "Code of Criminal Procedure 1973" },
  { code: "CPC", label: "CPC", full: "Code of Civil Procedure 1908" },
  { code: "ITA", label: "IT Act", full: "Information Technology Act 2000" },
  { code: "CPA", label: "Consumer", full: "Consumer Protection Act 2019" },
  { code: "PWDVA", label: "DV Act", full: "Domestic Violence Act 2005" },
  { code: "RTI", label: "RTI", full: "Right to Information Act 2005" },
  { code: "MVA", label: "MV Act", full: "Motor Vehicles Act 1988" },
  { code: "ICA", label: "Contract", full: "Indian Contract Act 1872" },
  { code: "NIA", label: "NI Act", full: "Negotiable Instruments Act 1881" },
];

export default function BrowsePage() {
  const { t, language } = useLanguage();
  const [selectedAct, setSelectedAct] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<LawListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedLawId, setExpandedLawId] = useState<string | null>(null);
  const [activeFilingActCode, setActiveFilingActCode] = useState<string | null>(null);

  const fetchLaws = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await browseLaws({
        act_code: selectedAct || undefined,
        search: search || undefined,
        page,
        per_page: 20,
        language,
      });
      setData(result);
    } catch (err) {
      console.error("Browse failed:", err);
      setError(t("error"));
    } finally {
      setIsLoading(false);
    }
  }, [selectedAct, search, page, t, language]);

  useEffect(() => {
    fetchLaws();
  }, [fetchLaws]);

  // Reset page and expanded state when filter changes
  useEffect(() => {
    setPage(1);
    setExpandedLawId(null);
  }, [selectedAct, search]);

  useEffect(() => {
    setExpandedLawId(null);
  }, [page]);

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Navigation ───────────────────────────────────────────────── */}
      <nav className="w-full px-6 py-4 flex items-center justify-between border-b border-surface-800/50 backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50">
        <a href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-saffron-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <span className="text-white font-bold text-sm">LI</span>
          </div>
          <span className="font-display font-bold text-xl text-surface-50">
            Lex<span className="gradient-text">India</span>
          </span>
        </a>
        <LanguageSwitcher />
      </nav>

      <main className="flex-1 px-6 py-8 max-w-6xl mx-auto w-full">
        {/* ── Page Title ─────────────────────────────────────────────── */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-display font-bold text-surface-50 mb-2">
            {t("browseLaws")}
          </h1>
          <p className="text-surface-400">
            {t("browseSubtitle")}
          </p>
        </div>

        {/* ── Filter Panel ───────────────────────────────────────────── */}
        <div className="mb-6 space-y-4 animate-fade-up" style={{ animationDelay: "100ms" }}>
          {/* Act Buttons */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedAct(null)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                !selectedAct
                  ? "bg-brand-600 text-white shadow-md shadow-brand-500/25"
                  : "bg-surface-800/50 text-surface-400 border border-surface-700/40 hover:text-surface-200 hover:bg-surface-700/50"
              }`}
              id="filter-all"
            >
              {t("allActs")}
            </button>
            {ACTS.map((act) => (
              <button
                key={act.code}
                onClick={() => setSelectedAct(act.code)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                  selectedAct === act.code
                    ? "bg-brand-600 text-white shadow-md shadow-brand-500/25"
                    : "bg-surface-800/50 text-surface-400 border border-surface-700/40 hover:text-surface-200 hover:bg-surface-700/50"
                }`}
                title={act.full}
                id={`filter-${act.code}`}
              >
                {act.label}
              </button>
            ))}
          </div>

          {/* Search Input */}
          <div className="relative max-w-lg">
            <svg
              className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("searchPlaceholder")}
              className="input-glass pl-11 py-2.5"
              id="browse-search"
            />
          </div>
        </div>

        {/* ── Loading ────────────────────────────────────────────────── */}
        {isLoading && (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="glass-card p-5">
                <div className="space-y-2">
                  <div className="h-4 bg-surface-700 rounded shimmer w-1/4" />
                  <div className="h-5 bg-surface-700 rounded shimmer w-1/2" />
                  <div className="h-4 bg-surface-700 rounded shimmer w-full" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Error ──────────────────────────────────────────────────── */}
        {error && (
          <div className="px-5 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* ── Results ────────────────────────────────────────────────── */}
        {!isLoading && data && (
          <>
            <div className="text-sm text-surface-500 mb-4">
              {data.total} {t("sectionsFound")} • {t("page")} {data.page} {t("of")} {data.total_pages}
            </div>

            <div className="space-y-4">
              {data.laws.map((law: any, i: number) => (
                <LawCard
                  key={law.section_id}
                  law={law}
                  index={i}
                  isExpanded={expandedLawId === law.section_id}
                  onToggleExpand={() =>
                    setExpandedLawId(expandedLawId === law.section_id ? null : law.section_id)
                  }
                  onFileCase={(actCode) => setActiveFilingActCode(actCode)}
                />
              ))}
            </div>

            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-8">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="btn-secondary text-sm disabled:opacity-30"
                  id="page-prev"
                >
                  {t("prevPage")}
                </button>
                <span className="text-sm text-surface-400">
                  {t("page")} {data.page} / {data.total_pages}
                </span>
                <button
                  onClick={() => setPage(Math.min(data.total_pages, page + 1))}
                  disabled={page === data.total_pages}
                  className="btn-secondary text-sm disabled:opacity-30"
                  id="page-next"
                >
                  {t("nextPage")}
                </button>
              </div>
            )}
          </>
        )}

        {/* No results */}
        {!isLoading && data && data.laws.length === 0 && (
          <div className="text-center py-16">
            <div className="text-5xl mb-4">📖</div>
            <p className="text-surface-400 text-lg">{t("noResults")}</p>
          </div>
        )}
      </main>

      <footer className="w-full px-6 py-6 text-center border-t border-surface-800/50">
        <p className="text-sm text-surface-500">
          {t("footerText")}
        </p>
      </footer>

      {/* Filing Modal */}
      <FilingModal
        actCode={activeFilingActCode || ""}
        isOpen={activeFilingActCode !== null}
        onClose={() => setActiveFilingActCode(null)}
      />
    </div>
  );
}
