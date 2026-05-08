"use client";

/**
 * SeverityBadge — colour-coded severity indicator.
 * Red = high, Amber = medium, Green = low.
 */

import { useLanguage } from "@/lib/TranslationContext";

interface SeverityBadgeProps {
  severity: "low" | "medium" | "high" | string;
}

const SEVERITY_CONFIG: Record<string, { className: string; icon: string; key: "low" | "medium" | "high" }> = {
  high: {
    className: "badge-high",
    icon: "⚠",
    key: "high"
  },
  medium: {
    className: "badge-medium",
    icon: "●",
    key: "medium"
  },
  low: {
    className: "badge-low",
    icon: "✓",
    key: "low"
  },
};

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  const { t } = useLanguage();
  const normalizedSeverity = severity?.toLowerCase() || "medium";
  const config = SEVERITY_CONFIG[normalizedSeverity] || SEVERITY_CONFIG.medium;

  return (
    <span className={config.className} id={`severity-${normalizedSeverity}`}>
      <span className="mr-1">{config.icon}</span>
      {t(config.key)}
    </span>
  );
}
