"use client";

/**
 * LawCard — displays an individual law result with simplified explanation,
 * severity badge, collapsible original text, filing link, and relevance score.
 */

import { useState } from "react";
import { useLanguage } from "@/lib/TranslationContext";
import SeverityBadge from "./SeverityBadge";
import FilingLink from "./FilingLink";
import FilingModal from "./FilingModal";
import type { LawResult } from "@/lib/api";

interface LawCardProps {
  law: LawResult;
  index: number;
}

export default function LawCard({ law, index }: LawCardProps) {
  const { t } = useLanguage();
  const [showOriginal, setShowOriginal] = useState(false);
  const [showFilingModal, setShowFilingModal] = useState(false);
  const hasRelevance = law.relevance_score != null && !isNaN(law.relevance_score);
  const relevancePercent = hasRelevance ? Math.round((law.relevance_score ?? 0) * 100) : 0;

  return (
    <div
      className="glass-card p-6 animate-fade-up"
      style={{ animationDelay: `${index * 100}ms` }}
      id={`law-card-${law.section_id}`}
    >
      {/* Header: Act name + Section + Severity */}
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded-md">
              §{law.section_number}
            </span>
            <SeverityBadge severity={law.severity} />
          </div>
          <h3 className="text-lg font-display font-semibold text-surface-50 leading-snug">
            {law.section_title}
          </h3>
          <p className="text-sm text-surface-400 mt-0.5">{law.act_name}</p>
        </div>

        {/* Relevance Score — only shown for search results */}
        {hasRelevance && (
          <div className="flex flex-col items-end gap-1 shrink-0">
            <span className="text-2xl font-display font-bold gradient-text">
              {relevancePercent}%
            </span>
            <span className="text-[10px] uppercase tracking-widest text-surface-500">
              {t("relevance")}
            </span>
            <div className="score-bar w-16 mt-1">
              <div
                className="score-bar-fill"
                style={{ width: `${relevancePercent}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Simplified Explanation */}
      <div className="mb-4 p-4 rounded-xl bg-surface-800/50 border border-surface-700/30">
        <p className="text-surface-200 leading-relaxed text-[15px] mb-3">
          {law.simplified || law.simplified_en || law.section_text?.substring(0, 300) || "No description available."}
        </p>
        {law.punishment && law.punishment !== "Not specified" && (
          <div className="mt-4 pt-4 border-t border-surface-700/50">
            <div className="flex items-center gap-2 mb-2 text-brand-400">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span className="text-[10px] uppercase tracking-widest font-bold">
                {t("legalPunishment")}
              </span>
            </div>
            <div className="p-3 bg-brand-500/5 border border-brand-500/10 rounded-lg">
              <p className="text-sm text-surface-200 font-medium italic leading-relaxed">
                {law.punishment}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Actions Row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Toggle Original Text */}
        <button
          onClick={() => setShowOriginal(!showOriginal)}
          className="btn-secondary text-sm"
          id={`toggle-original-${law.section_id}`}
        >
          <span className="mr-1.5">{showOriginal ? "▾" : "▸"}</span>
          {showOriginal ? t("hideOriginal") : t("viewOriginal")}
        </button>

        {/* File Case Button */}
        <button
          onClick={() => setShowFilingModal(true)}
          className="btn-primary text-sm flex items-center gap-2"
          id={`file-case-${law.section_id}`}
          title={t("fileCase")}
        >
          <span className="text-lg">⚖️</span>
          {t("fileCase")}
        </button>

        {/* Draft Document Button — only for draftable acts */}
        {law.draftable && (
          <a
            href={`/drafting?act=${encodeURIComponent(law.act_name)}&section=${encodeURIComponent(law.section_id)}`}
            className="btn-secondary text-sm flex items-center gap-2 hover:border-emerald-500/40 hover:text-emerald-300"
            id={`draft-doc-${law.section_id}`}
            title={t("draftDocument")}
          >
            <span className="text-lg">📝</span>
            {t("draftDocument")}
          </a>
        )}

        {/* Filing Link */}
        <FilingLink url={law.filing_link ?? null} actName={law.act_name} />
      </div>

      {/* Filing Modal — NEW */}
      <FilingModal
        actCode={law.section_id || law.act_name || "DEFAULT"}
        isOpen={showFilingModal}
        onClose={() => setShowFilingModal(false)}
      />

      {/* Collapsible Original Text */}
      {showOriginal && (
        <div className="mt-4 p-4 rounded-xl bg-surface-900/60 border border-surface-700/20 animate-fade-in">
          <p className="text-sm text-surface-400 font-mono leading-relaxed whitespace-pre-wrap">
            {law.original_text}
          </p>
        </div>
      )}
    </div>
  );
}
