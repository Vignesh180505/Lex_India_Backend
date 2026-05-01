/**
 * i18next configuration — supports English (en), Tamil (ta), and Hindi (hi).
 * Uses browser language detection and localStorage for persistence.
 */

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "../public/locales/en/translation.json";
import ta from "../public/locales/ta/translation.json";
import hi from "../public/locales/hi/translation.json";

const isBrowser = typeof window !== "undefined";

const resources = {
  en: { translation: en },
  ta: { translation: ta },
  hi: { translation: hi },
};

const i18nInstance = i18n.createInstance();

// Client-side vs. Server-side initialization
const initOptions = {
  resources,
  supportedLngs: ["en", "ta", "hi"],
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
  react: {
    useSuspense: false, // Important for avoiding hydration issues
  },
  // Explicitly set language on server
  lng: isBrowser ? undefined : "en",
};

if (isBrowser) {
  i18nInstance.use(LanguageDetector);
}

i18nInstance.use(initReactI18next).init(initOptions);

export default i18nInstance;
