"use client";

/**
 * SeverityBadge — colour-coded severity indicator.
 * Red = high, Amber = medium, Green = low.
 */

interface SeverityBadgeProps {
  severity: "low" | "medium" | "high";
}

const SEVERITY_CONFIG = {
  high: {
    className: "badge-high",
    icon: "⚠",
  },
  medium: {
    className: "badge-medium",
    icon: "●",
  },
  low: {
    className: "badge-low",
    icon: "✓",
  },
};

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.medium;

  return (
    <span className={config.className} id={`severity-${severity}`}>
      <span className="mr-1">{config.icon}</span>
      {severity}
    </span>
  );
}
