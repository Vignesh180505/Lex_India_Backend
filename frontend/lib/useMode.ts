"use client";

import { useState, useEffect } from "react";

export function useMode() {
  const [mode, setMode] = useState<"citizen" | "lawyer">("citizen");

  useEffect(() => {
    setMode((localStorage.getItem("lexindia_mode") as "citizen" | "lawyer") ?? "citizen");

    const onModeChange = () => {
      setMode((localStorage.getItem("lexindia_mode") as "citizen" | "lawyer") ?? "citizen");
    };

    window.addEventListener("lexindia_mode_change", onModeChange);
    return () => {
      window.removeEventListener("lexindia_mode_change", onModeChange);
    };
  }, []);

  return mode;
}
