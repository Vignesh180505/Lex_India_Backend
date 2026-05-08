/**
 * language-cookie.ts — Cookie-based language persistence.
 *
 * Replaces localStorage to avoid SSR hydration mismatches.
 * Works on both server (next/headers) and client (js-cookie).
 */

import Cookies from "js-cookie";

export type Language = "english" | "tamil" | "hindi";

const COOKIE_NAME = "lexindia_lang";
const MAX_AGE_DAYS = 365;

/**
 * Map legacy i18n codes (en/ta/hi) to our canonical names.
 */
const LEGACY_MAP: Record<string, Language> = {
  en: "english",
  ta: "tamil",
  hi: "hindi",
};

const VALID_LANGUAGES: Language[] = ["english", "tamil", "hindi"];

/**
 * Read the current language from the cookie (client-side only).
 * Returns "english" as the default if no cookie is set or value is invalid.
 */
export function getLanguage(): Language {
  if (typeof window === "undefined") {
    // Server-side: return default — the actual value will be read
    // by middleware and passed as a header; components should use
    // TranslationContext which defaults to "english" on SSR.
    return "english";
  }

  const raw = Cookies.get(COOKIE_NAME);
  if (!raw) return "english";

  // Handle canonical values
  if (VALID_LANGUAGES.includes(raw as Language)) {
    return raw as Language;
  }

  // Handle legacy i18n codes
  if (raw in LEGACY_MAP) {
    return LEGACY_MAP[raw];
  }

  return "english";
}

/**
 * Set the language cookie (client-side).
 */
export function setLanguage(lang: Language): void {
  if (typeof window === "undefined") return;
  Cookies.set(COOKIE_NAME, lang, {
    expires: MAX_AGE_DAYS,
    path: "/",
    sameSite: "lax",
  });
}

/**
 * Convert our Language type to the legacy i18n code used by the backend.
 */
export function languageToCode(lang: Language): string {
  const map: Record<Language, string> = {
    english: "en",
    tamil: "ta",
    hindi: "hi",
  };
  return map[lang] || "en";
}

/**
 * Convert a backend language code to our Language type.
 */
export function codeToLanguage(code: string): Language {
  return LEGACY_MAP[code] || "english";
}
