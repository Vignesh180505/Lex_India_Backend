"use client";

/**
 * Results page — displays AI summary, matching law cards,
 * similar past court cases, and win/loss outcome analysis.
 *
 * Reads query results from sessionStorage (set by the home page on submit).
 * Fetches similar cases and outcome stats from the judgments API.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/TranslationContext";

import LanguageSwitcher from "@/components/LanguageSwitcher";
import ModeToggle from "@/components/ModeToggle";
import LawCard from "@/components/LawCard";
import FilingModal from "@/components/FilingModal";
import { useMode } from "@/lib/useMode";
import type { QueryResponse, JudgmentCard, OutcomeAnalysisResponse } from "@/lib/api";
import { getSimilarCases, getOutcomeAnalysis } from "@/lib/api";

export default function ResultsPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [query, setQuery] = useState("");
  const mode = useMode();

  // Similar cases state
  const [similarCases, setSimilarCases] = useState<JudgmentCard[]>([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [casesError, setCasesError] = useState<string | null>(null);

  // Outcome analysis state
  const [outcomeData, setOutcomeData] = useState<OutcomeAnalysisResponse | null>(null);
  const [outcomeLoading, setOutcomeLoading] = useState(false);

  // Law card expansion state
  const [expandedLawId, setExpandedLawId] = useState<string | null>(null);

  // Active filing portal act code state
  const [activeFilingActCode, setActiveFilingActCode] = useState<string | null>(null);

  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    // Try sessionStorage first (set on fresh query), then fall back to
    // localStorage (persists across soft/hard refreshes in the same browser).
    const stored =
      sessionStorage.getItem("lexindia-results") ||
      localStorage.getItem("lexindia-results");
    const storedQuery =
      sessionStorage.getItem("lexindia-query") ||
      localStorage.getItem("lexindia-query");

    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setResults(parsed);
        // Keep both stores in sync
        sessionStorage.setItem("lexindia-results", stored);
        localStorage.setItem("lexindia-results", stored);
      } catch {
        setNotFound(true);
      }
    } else {
      // No results available — show a helpful message rather than
      // redirecting immediately, giving the user a chance to click
      // "New Search" themselves.
      setNotFound(true);
    }

    if (storedQuery) {
      setQuery(storedQuery);
      sessionStorage.setItem("lexindia-query", storedQuery);
      localStorage.setItem("lexindia-query", storedQuery);
    }
  }, []);

  // Fetch similar cases and outcome analysis when query is loaded
  useEffect(() => {
    if (!query) return;

    // Fetch similar past cases
    const fetchSimilar = async () => {
      setCasesLoading(true);
      setCasesError(null);
      try {
        const data = await getSimilarCases(query, mode);
        setSimilarCases(data.cases || []);

        // Once we have cases, fetch outcome analysis with their doc_ids
        if (data.cases && data.cases.length > 0) {
          setOutcomeLoading(true);
          try {
            const docIds = data.cases.map((c) => c.doc_id).filter(Boolean);
            if (docIds.length > 0) {
              const outcome = await getOutcomeAnalysis(query, docIds);
              setOutcomeData(outcome);
            }
          } catch (err) {
            console.warn("Outcome analysis failed:", err);
          } finally {
            setOutcomeLoading(false);
          }
        }
      } catch (err: unknown) {
        console.warn("Similar cases fetch failed:", err);
        setCasesError(t("couldNotLoadCases"));
      } finally {
        setCasesLoading(false);
      }
    };

    fetchSimilar();
  }, [query, mode, t]);

  if (notFound) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-6 px-6">
        <div className="text-5xl">🔍</div>
        <div className="text-center">
          <h2 className="text-xl font-display font-semibold text-surface-100 mb-2">
            No results to display
          </h2>
          <p className="text-surface-400 text-sm max-w-sm">
            Your search results are no longer available. Please start a new search.
          </p>
        </div>
        <button
          onClick={() => router.push("/")}
          className="btn-primary"
          id="start-new-search"
        >
          Start New Search
        </button>
      </div>
    );
  }

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
      <nav className={`w-full px-6 py-4 flex items-center justify-between border-b backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50 ${mode === "lawyer" ? "border-amber-500/50 border-b-2" : "border-surface-800/50"}`}>
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
            href="/judgments/browse"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors hidden sm:block"
            id="nav-judgments"
          >
            ⚖️ {t("navJudgments")}
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
            {t("newSearch")}
          </button>

          {query && (
            <div className="glass-card p-4">
              <p className="text-sm text-surface-500 mb-1">{t("yourQuery")}</p>
              <p className="text-surface-200">{query}</p>
            </div>
          )}
        </div>

        {/* Response Time */}
        <div className="flex items-center gap-3 mb-6 animate-fade-in" style={{ animationDelay: "100ms" }}>
          <span className="text-xs text-surface-500">
            {results.laws.length} {results.laws.length === 1 ? t("resultFound") : t("resultsFound")} {results.response_ms}ms
          </span>
          {results.detected_language !== "en" && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20">
              {t("detected")}: {results.detected_language === "ta" ? t("tamilLang") : t("hindiLang")}
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

        {/* ── Outcome Analysis — "Who Does the Law Favour?" ────────── */}
        {(outcomeLoading || outcomeData) && (
          <div className="mb-8 animate-fade-up" style={{ animationDelay: "200ms" }}>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-saffron-400 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
              {t("whoDoesLawFavour")}
            </h2>

            {outcomeLoading ? (
              <div className="glass-card p-6">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 border-2 border-saffron-500 border-t-transparent rounded-full animate-spin" />
                  <span className="text-surface-400 text-sm">{t("analysingOutcomes")}</span>
                </div>
              </div>
            ) : outcomeData && (outcomeData.petitioner_wins > 0 || outcomeData.respondent_wins > 0 || outcomeData.partial > 0) ? (
              <div className="glass-card p-6 border-l-4 border-l-saffron-500">
                {/* Favour Label */}
                <p className="text-lg font-display font-semibold text-surface-50 mb-4">
                  {outcomeData.favour_label}
                </p>

                {/* Visual Stat Bar */}
                <div className="mb-4">
                  <div className="flex items-center justify-between text-xs text-surface-400 mb-2">
                    <span>{t("petitionerWon")}: {outcomeData.petitioner_wins}</span>
                    <span>{t("respondentWon")}: {outcomeData.respondent_wins}</span>
                  </div>
                  <div className="h-4 rounded-full bg-surface-700 overflow-hidden flex">
                    {outcomeData.petitioner_wins > 0 && (
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-700"
                        style={{
                          width: `${(outcomeData.petitioner_wins / outcomeData.total_cases) * 100}%`,
                        }}
                      />
                    )}
                    {outcomeData.partial > 0 && (
                      <div
                        className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-700"
                        style={{
                          width: `${(outcomeData.partial / outcomeData.total_cases) * 100}%`,
                        }}
                      />
                    )}
                    {outcomeData.unclear > 0 && (
                      <div
                        className="h-full bg-gradient-to-r from-surface-500 to-surface-400 transition-all duration-700"
                        style={{
                          width: `${(outcomeData.unclear / outcomeData.total_cases) * 100}%`,
                        }}
                      />
                    )}
                    {outcomeData.respondent_wins > 0 && (
                      <div
                        className="h-full bg-gradient-to-r from-red-500 to-red-400 transition-all duration-700"
                        style={{
                          width: `${(outcomeData.respondent_wins / outcomeData.total_cases) * 100}%`,
                        }}
                      />
                    )}
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-surface-500">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" /> {t("petitioner")}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-red-500" /> {t("respondent")}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-amber-500" /> {t("partial")}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-surface-500" /> {t("unclear")}
                    </span>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="text-center p-3 rounded-xl bg-surface-800/50">
                    <div className="text-2xl font-display font-bold text-surface-50">
                      {outcomeData.total_cases}
                    </div>
                    <div className="text-[10px] uppercase tracking-widest text-surface-500">
                      {t("totalCases")}
                    </div>
                  </div>
                  <div className="text-center p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/10">
                    <div className="text-2xl font-display font-bold text-emerald-400">
                      {outcomeData.win_percentage}%
                    </div>
                    <div className="text-[10px] uppercase tracking-widest text-surface-500">
                      {t("winRate")}
                    </div>
                  </div>
                  <div className="text-center p-3 rounded-xl bg-surface-800/50">
                    <div className="text-2xl font-display font-bold text-amber-400">
                      {outcomeData.partial}
                    </div>
                    <div className="text-[10px] uppercase tracking-widest text-surface-500">
                      {t("partial")}
                    </div>
                  </div>
                  <div className="text-center p-3 rounded-xl bg-surface-800/50">
                    <div className="text-2xl font-display font-bold text-surface-400">
                      {outcomeData.unclear}
                    </div>
                    <div className="text-[10px] uppercase tracking-widest text-surface-500">
                      {t("unclear")}
                    </div>
                  </div>
                </div>
              </div>
            ) : outcomeData ? (
              /* All outcomes unclear — show a simple info message */
              <div className="glass-card p-6 border-l-4 border-l-surface-600">
                <p className="text-surface-400 text-sm flex items-center gap-2">
                  <span>📊</span>
                  <span>Outcome data is limited for this query — {outcomeData.total_cases} similar {outcomeData.total_cases === 1 ? "case" : "cases"} found but outcomes could not be determined from available judgment text.</span>
                </p>
              </div>
            ) : null}
          </div>
        )}

        {/* Law Cards */}
        {results.laws.length > 0 ? (
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-surface-400 mb-4">
              {t("applicableLaws")} ({results.laws.length})
            </h2>
            <div className="space-y-4">
              {results.laws.map((law, index) => (
                <LawCard
                  key={law.section_id}
                  law={law}
                  index={index}
                  isExpanded={expandedLawId === law.section_id}
                  onToggleExpand={() =>
                    setExpandedLawId(expandedLawId === law.section_id ? null : law.section_id)
                  }
                  onFileCase={(actCode) => setActiveFilingActCode(actCode)}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-16 animate-fade-in">
            <div className="text-5xl mb-4">🔍</div>
            <p className="text-surface-400 text-lg">{t("noResults")}</p>
          </div>
        )}

        {/* ── Similar Past Cases ───────────────────────────────────────── */}
        <div className="mt-12 animate-fade-up" style={{ animationDelay: "250ms" }}>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-brand-400 mb-4 flex items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.331 0 4.472.89 6.064 2.346m0-12.804A8.966 8.966 0 0118 3.75c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.346m0-12.804v12.804" />
            </svg>
            {t("similarCases")}
          </h2>

          {casesLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="glass-card p-5">
                  <div className="space-y-3">
                    <div className="h-4 bg-surface-700 rounded-lg shimmer w-3/4" />
                    <div className="h-3 bg-surface-700 rounded-lg shimmer w-1/2" />
                    <div className="h-3 bg-surface-700 rounded-lg shimmer w-full" />
                  </div>
                </div>
              ))}
            </div>
          ) : casesError ? (
            <div className="glass-card p-5 border-l-4 border-l-surface-600">
              <p className="text-surface-400 text-sm">{casesError}</p>
            </div>
          ) : similarCases.length > 0 ? (
            <div className="space-y-3">
              {similarCases.map((caseItem, index) => (
                <div
                  key={caseItem.doc_id}
                  className="glass-card p-5 animate-fade-up"
                  style={{ animationDelay: `${index * 80}ms` }}
                  id={`similar-case-${caseItem.doc_id}`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-display font-semibold text-surface-50 mb-1 leading-snug">
                        {caseItem.title}
                      </h3>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded-md">
                          {caseItem.court}
                        </span>
                        {caseItem.date && (
                          <span className="text-xs text-surface-500">
                            {caseItem.date}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-surface-300 leading-relaxed line-clamp-3">
                        {caseItem.snippet}
                      </p>
                    </div>
                    <a
                      href={caseItem.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 btn-secondary text-xs flex items-center gap-1.5 whitespace-nowrap"
                      id={`read-judgment-${caseItem.doc_id}`}
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
            <div className="glass-card p-5 text-center">
              <p className="text-surface-500 text-sm">{t("noSimilarCases")}</p>
            </div>
          )}
        </div>
      </main>

      {/* ── Footer ───────────────────────────────────────────────────── */}
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
