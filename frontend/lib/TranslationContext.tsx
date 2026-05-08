"use client";

/**
 * TranslationContext — React context providing language state and translation
 * function to the entire app.
 *
 * KEY DESIGN: Defaults to "english" on BOTH server and client initial render
 * to prevent hydration mismatch. After mount (useEffect), reads the real
 * language from the cookie and updates state. This causes a single re-render
 * on the client (invisible to the user) instead of a hydration crash.
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";

import {
  type Language,
  type TranslationKey,
  translations,
  t as translate,
} from "./translations";

import {
  getLanguage,
  setLanguage as setCookieLanguage,
  languageToCode,
} from "./language-cookie";

interface TranslationContextValue {
  /** Current UI language. Defaults to "english" during SSR. */
  language: Language;
  /** Set language — updates both React state and the cookie. */
  setLanguage: (lang: Language) => void;
  /** Translate a key using the current language. */
  t: (key: TranslationKey) => string;
  /** Whether the real language has been read from the cookie (client only). */
  isHydrated: boolean;
  /** Convert current language to backend code (en/ta/hi). */
  langCode: string;
}

const TranslationContext = createContext<TranslationContextValue>({
  language: "english",
  setLanguage: () => {},
  t: (key) => translate(key, "english"),
  isHydrated: false,
  langCode: "en",
});

export function TranslationProvider({ children }: { children: ReactNode }) {
  // Start with "english" to match SSR — prevents hydration error
  const [language, setLanguageState] = useState<Language>("english");
  const [isHydrated, setIsHydrated] = useState(false);

  // On mount, read the real language from the cookie
  useEffect(() => {
    const cookieLang = getLanguage();
    setLanguageState(cookieLang);
    setIsHydrated(true);
  }, []);

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    setCookieLanguage(lang);
  }, []);

  const t = useCallback(
    (key: TranslationKey) => translate(key, language),
    [language]
  );

  const langCode = languageToCode(language);

  return (
    <TranslationContext.Provider
      value={{ language, setLanguage, t, isHydrated, langCode }}
    >
      {children}
    </TranslationContext.Provider>
  );
}

/**
 * useLanguage — access the current language, setter, and translation fn.
 */
export function useLanguage() {
  const ctx = useContext(TranslationContext);
  if (!ctx) {
    throw new Error("useLanguage must be used within a TranslationProvider");
  }
  return ctx;
}
