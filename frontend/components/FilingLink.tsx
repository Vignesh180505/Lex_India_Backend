"use client";

/**
 * FilingLink — button linking to the official eCourts case filing portal.
 */

import { useTranslation } from "react-i18next";

interface FilingLinkProps {
  url: string | null;
  actName?: string;
}

export default function FilingLink({ url, actName }: FilingLinkProps) {
  const { t } = useTranslation();

  if (!url) return null;

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      id="filing-link-btn"
      className="
        inline-flex items-center gap-2 px-4 py-2 rounded-lg
        text-sm font-semibold text-saffron-400
        bg-saffron-500/10 border border-saffron-500/20
        hover:bg-saffron-500/20 hover:border-saffron-500/30
        hover:shadow-lg hover:shadow-saffron-500/10
        active:scale-[0.98]
        transition-all duration-200
      "
      title={`File a case - ${actName || ""}`}
    >
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
          d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"
        />
      </svg>
      {t("fileCase")}
    </a>
  );
}
