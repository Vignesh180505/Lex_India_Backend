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

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ta: { translation: ta },
      hi: { translation: hi },
    },
    fallbackLng: "en",
    supportedLngs: ["en", "ta", "hi"],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: "lexindia-lang",
      caches: ["localStorage"],
    },
  });

export default i18n;
