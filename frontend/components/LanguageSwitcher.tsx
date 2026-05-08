"use client";

/**
 * LanguageSwitcher — toggle between English, Tamil, and Hindi.
 * Uses the cookie-based TranslationContext to avoid hydration errors.
 */

import { useLanguage } from "@/lib/TranslationContext";
import type { Language } from "@/lib/translations";

const LANGUAGES: { code: Language; label: string; native: string }[] = [
  { code: "english", label: "EN", native: "English" },
  { code: "tamil", label: "தமி", native: "தமிழ்" },
  { code: "hindi", label: "हि", native: "हिन्दी" },
];

export default function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex items-center gap-1 p-1 rounded-xl bg-surface-800/60 border border-surface-700/50 backdrop-blur-sm">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          id={`lang-switch-${lang.code}`}
          onClick={() => setLanguage(lang.code)}
          className={`
            relative px-3 py-1.5 rounded-lg text-sm font-medium
            transition-all duration-200 ease-out
            ${
              language === lang.code
                ? "bg-brand-600 text-white shadow-md shadow-brand-500/25"
                : "text-surface-400 hover:text-surface-200 hover:bg-surface-700/50"
            }
          `}
          title={lang.native}
          aria-label={`Switch to ${lang.native}`}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
