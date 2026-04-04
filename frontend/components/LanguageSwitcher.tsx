"use client";

/**
 * LanguageSwitcher — toggle between English, Tamil, and Hindi.
 * Persists selection in localStorage and re-renders all UI labels instantly.
 */

import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

const LANGUAGES = [
  { code: "en", label: "EN", native: "English" },
  { code: "ta", label: "தமி", native: "தமிழ்" },
  { code: "hi", label: "हिं", native: "हिन्दी" },
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [activeLang, setActiveLang] = useState("en");

  useEffect(() => {
    const stored = localStorage.getItem("lexindia-lang");
    if (stored && ["en", "ta", "hi"].includes(stored)) {
      setActiveLang(stored);
      i18n.changeLanguage(stored);
    }
  }, [i18n]);

  const switchLanguage = (code: string) => {
    setActiveLang(code);
    i18n.changeLanguage(code);
    localStorage.setItem("lexindia-lang", code);
  };

  return (
    <div className="flex items-center gap-1 p-1 rounded-xl bg-surface-800/60 border border-surface-700/50 backdrop-blur-sm">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          id={`lang-switch-${lang.code}`}
          onClick={() => switchLanguage(lang.code)}
          className={`
            relative px-3 py-1.5 rounded-lg text-sm font-medium
            transition-all duration-200 ease-out
            ${
              activeLang === lang.code
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
