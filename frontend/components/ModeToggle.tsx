"use client";

import { useEffect, useState } from "react";

export default function ModeToggle() {
  const [mode, setMode] = useState<"citizen" | "lawyer">("citizen");

  useEffect(() => {
    // Initial read
    const stored = (localStorage.getItem("lexindia_mode") as "citizen" | "lawyer") ?? "citizen";
    if (stored !== mode) {
      setMode(stored);
    }

    // Listener for changes
    const onModeChange = () => {
      setMode((localStorage.getItem("lexindia_mode") as "citizen" | "lawyer") ?? "citizen");
    };

    window.addEventListener("lexindia_mode_change", onModeChange);
    return () => {
      window.removeEventListener("lexindia_mode_change", onModeChange);
    };
  }, []);

  const toggleMode = () => {
    const newMode = mode === "citizen" ? "lawyer" : "citizen";
    setMode(newMode);
    localStorage.setItem("lexindia_mode", newMode);
    window.dispatchEvent(new Event("lexindia_mode_change"));
  };

  return (
    <div className="flex items-center gap-2">
      <span className={`text-xs font-medium uppercase tracking-wider ${mode === "citizen" ? "text-brand-400" : "text-surface-500"}`}>
        Citizen
      </span>
      <button
        onClick={toggleMode}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          mode === "lawyer" ? "bg-amber-500" : "bg-brand-500"
        }`}
        id="mode-toggle"
        title="Toggle Lawyer Mode"
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            mode === "lawyer" ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
      <span className={`text-xs font-medium uppercase tracking-wider flex items-center gap-1 ${mode === "lawyer" ? "text-amber-500" : "text-surface-500"}`}>
        Lawyer
        {mode === "lawyer" && (
          <span className="bg-amber-500 text-amber-950 px-1.5 py-0.5 rounded text-[10px] font-bold">MODE</span>
        )}
      </span>
    </div>
  );
}
