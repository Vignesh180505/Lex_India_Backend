"use client";

/**
 * QueryInput — main search textarea with language-aware placeholder text,
 * example prompt chips, and category shortcuts.
 */

import { useState } from "react";
import { useLanguage } from "@/lib/TranslationContext";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export default function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const { t } = useLanguage();
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim().length >= 10 && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  const examples = [
    t("examplePrompt1"),
    t("examplePrompt2"),
    t("examplePrompt3"),
  ];

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      {/* Search Textarea */}
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-brand-600/30 via-brand-500/20 to-saffron-500/30 rounded-2xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-500 blur-sm" />
        <div className="relative">
          <textarea
            id="query-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("searchPlaceholder")}
            rows={4}
            maxLength={2000}
            disabled={isLoading}
            className="
              input-glass w-full resize-none rounded-2xl py-5 px-6
              text-lg leading-relaxed
              focus:ring-2 focus:ring-brand-500/30
              disabled:opacity-50 disabled:cursor-not-allowed
            "
            aria-label="Legal query input"
          />
          <div className="absolute bottom-3 right-3 flex items-center gap-3">
            <span className="text-xs text-surface-500">
              {query.length}/2000
            </span>
            <button
              type="submit"
              disabled={query.trim().length < 10 || isLoading}
              className="btn-primary text-sm disabled:opacity-40 disabled:cursor-not-allowed"
              id="submit-query-btn"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg
                    className="w-4 h-4 animate-spin"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                    />
                  </svg>
                  {t("loading")}
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
                    />
                  </svg>
                  {t("searchButton")}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Example Prompt Chips */}
      <div className="mt-5 flex flex-wrap gap-2 justify-center">
        {examples.map((example, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleExampleClick(example)}
            className="
              px-4 py-2 rounded-xl text-sm text-surface-300
              bg-surface-800/40 border border-surface-700/40
              hover:bg-surface-700/60 hover:border-surface-600 hover:text-surface-100
              transition-all duration-200 text-left
              active:scale-[0.98]
            "
            id={`example-prompt-${idx + 1}`}
          >
            <span className="text-brand-400 mr-1.5">→</span>
            {example}
          </button>
        ))}
      </div>
    </form>
  );
}
