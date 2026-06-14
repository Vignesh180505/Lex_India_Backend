"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import {
  getFilingPortal,
  getOptionTypeColor,
  FilingOption,
} from "@/lib/filingPortals";

interface FilingModalProps {
  actCode: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function FilingModal({ actCode, isOpen, onClose }: FilingModalProps) {
  const [mounted, setMounted] = useState(false);
  const [selectedOption, setSelectedOption] = useState<FilingOption | null>(null);
  const portalInfo = getFilingPortal(actCode);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  // Reset selection when modal opens
  useEffect(() => {
    if (isOpen) setSelectedOption(null);
  }, [isOpen]);

  // Body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  // Close on Escape key
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  if (!isOpen || !mounted) return null;

  const typeLabels: Record<string, string> = {
    online: "Online",
    physical: "In Person",
    helpline: "Helpline",
    legal_aid: "Legal Aid",
  };

  const typeColors: Record<string, string> = {
    online: "bg-brand-500/15 text-brand-300 border border-brand-500/25",
    physical: "bg-amber-500/15 text-amber-300 border border-amber-500/25",
    helpline: "bg-emerald-500/15 text-emerald-300 border border-emerald-500/25",
    legal_aid: "bg-purple-500/15 text-purple-300 border border-purple-500/25",
  };

  return createPortal(
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/75 backdrop-blur-sm z-[9998] transition-opacity duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal — centered, full height constraint, flex column */}
      <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 sm:p-6">
        <div
          className="relative w-full max-w-xl flex flex-col rounded-2xl border border-surface-700/60 bg-surface-900 shadow-2xl shadow-black/60"
          style={{ maxHeight: "min(88vh, 680px)" }}
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          aria-labelledby="filing-modal-title"
        >
          {/* ── Header (fixed) ── */}
          <div className="flex-shrink-0 flex items-start justify-between gap-4 px-6 pt-6 pb-4 border-b border-surface-700/40">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">⚖️</span>
                <h2
                  id="filing-modal-title"
                  className="text-lg font-display font-bold text-surface-50"
                >
                  File a Case
                </h2>
              </div>
              <p className="text-sm text-surface-400 ml-8">
                {portalInfo.actName}
              </p>
            </div>
            <button
              onClick={onClose}
              className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-surface-800 hover:bg-surface-700 text-surface-400 hover:text-surface-100 transition-colors"
              aria-label="Close"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* ── Scrollable Body ── */}
          <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">

            {/* Court / Timeline info */}
            {(portalInfo.defaultCourt || portalInfo.timelineInfo) && (
              <div className="p-4 rounded-xl bg-brand-500/8 border border-brand-500/20 space-y-2">
                {portalInfo.defaultCourt && (
                  <div className="flex items-center gap-2">
                    <span className="text-brand-400">🏛️</span>
                    <p className="text-sm text-surface-200">
                      <span className="font-semibold text-surface-100">Primary Forum: </span>
                      {portalInfo.defaultCourt}
                    </p>
                  </div>
                )}
                {portalInfo.timelineInfo && (
                  <div className="flex items-center gap-2">
                    <span className="text-brand-400">🕐</span>
                    <p className="text-sm text-surface-300">
                      <span className="font-semibold text-surface-100">Timeline: </span>
                      {portalInfo.timelineInfo}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Filing options */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-widest text-surface-500 mb-3">
                How to file your case
              </h3>
              <div className="space-y-2">
                {portalInfo.filingOptions.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedOption(selectedOption === option ? null : option)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-150 ${
                      selectedOption === option
                        ? "border-brand-500/60 bg-brand-500/10"
                        : "border-surface-700/50 bg-surface-800/40 hover:border-surface-600 hover:bg-surface-800/70"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xl flex-shrink-0 mt-0.5">{option.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-semibold text-surface-100 text-sm">
                            {option.title}
                          </span>
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${typeColors[option.type] || "bg-surface-700 text-surface-300"}`}>
                            {typeLabels[option.type] || option.type}
                          </span>
                        </div>
                        <p className="text-xs text-surface-400 mt-1 leading-relaxed">
                          {option.description}
                        </p>
                      </div>
                      <svg
                        className={`w-4 h-4 flex-shrink-0 mt-1 text-surface-500 transition-transform duration-150 ${selectedOption === option ? "rotate-90 text-brand-400" : ""}`}
                        fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                      </svg>
                    </div>

                    {/* Expanded detail */}
                    {selectedOption === option && (
                      <div className="mt-3 pt-3 border-t border-surface-700/40 ml-9">
                        {option.url.startsWith("tel:") ? (
                          <a
                            href={option.url}
                            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-sm font-semibold hover:bg-emerald-500/25 transition-colors"
                          >
                            📞 Call Now — {option.url.replace("tel:", "")}
                          </a>
                        ) : (
                          <a
                            href={option.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-500/15 border border-brand-500/30 text-brand-300 text-sm font-semibold hover:bg-brand-500/25 transition-colors"
                          >
                            🌐 Visit Portal
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                            </svg>
                          </a>
                        )}
                        <p className="text-xs text-surface-500 mt-2">
                          💡 Keep your case details and supporting documents ready.
                        </p>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Disclaimer */}
            <div className="p-3 rounded-xl bg-amber-500/8 border border-amber-500/20">
              <p className="text-xs text-amber-300/90 leading-relaxed">
                ⚠️ <span className="font-semibold">Important:</span> This is for general guidance only.
                Consult a qualified lawyer for legal advice specific to your situation.
              </p>
            </div>
          </div>

          {/* ── Footer (fixed) ── */}
          <div className="flex-shrink-0 px-6 py-4 border-t border-surface-700/40 bg-surface-900/80">
            <button
              onClick={onClose}
              className="w-full py-2.5 rounded-xl bg-surface-800 hover:bg-surface-700 border border-surface-700/50 text-surface-300 hover:text-surface-100 text-sm font-semibold transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>,
    document.body
  );
}
