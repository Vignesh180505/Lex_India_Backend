"use client";

/**
 * Document Drafting Hub — Legal Tools page for generating legal documents.
 * Users select a document type, fill in details, preview AI-generated text,
 * and download as PDF.
 */

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import "@/lib/i18n";

import DocumentTypeSelector from "@/components/drafting/DocumentTypeSelector";
import DocumentForm from "@/components/drafting/DocumentForm";
import RentalAgreementForm from "@/components/drafting/RentalAgreementForm";
import DraftPreview from "@/components/drafting/DraftPreview";

type DocumentType =
  | "legal_notice"
  | "rti_application"
  | "fir_draft"
  | "rental_agreement"
  | "affidavit";

type Step = "select" | "form" | "preview";

function DraftingContent() {
  const searchParams = useSearchParams();
  const [step, setStep] = useState<Step>("select");
  const [selectedType, setSelectedType] = useState<DocumentType | null>(null);
  const [draftText, setDraftText] = useState("");
  const [disclaimer, setDisclaimer] = useState("");

  // Pre-fill from search results (via LawCard "Draft Document" button)
  const prefillAct = searchParams.get("act") || "";
  const prefillSection = searchParams.get("section") || "";

  const handleTypeSelect = (type: DocumentType) => {
    setSelectedType(type);
    setStep("form");
  };

  const handleDraftGenerated = (text: string, disc: string) => {
    setDraftText(text);
    setDisclaimer(disc);
    setStep("preview");
  };

  const handleBack = () => {
    if (step === "preview") {
      setStep("form");
    } else if (step === "form") {
      setStep("select");
      setSelectedType(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Navigation ───────────────────────────────────────────────── */}
      <nav className="w-full px-6 py-4 flex items-center justify-between border-b border-surface-800/50 backdrop-blur-xl bg-surface-950/80 sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <a href="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-saffron-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <span className="text-white font-bold text-sm">LI</span>
            </div>
            <span className="font-display font-bold text-xl text-surface-50">
              Lex<span className="gradient-text">India</span>
            </span>
          </a>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="/browse"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors hidden sm:block"
          >
            Browse Laws
          </a>
          <a
            href="/"
            className="text-sm text-surface-400 hover:text-surface-200 transition-colors"
          >
            Search
          </a>
        </div>
      </nav>

      {/* ── Main Content ─────────────────────────────────────────────── */}
      <main className="flex-1 px-6 py-10 max-w-5xl mx-auto w-full">
        {/* Back Button */}
        {step !== "select" && (
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-surface-400 hover:text-surface-200 mb-6 transition-colors group"
          >
            <span className="text-lg group-hover:-translate-x-1 transition-transform">←</span>
            <span className="text-sm">Back</span>
          </button>
        )}

        {/* Page Title */}
        <div className="mb-10 text-center animate-fade-up">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-4">
            <span className="text-sm">📝</span>
            <span className="text-sm text-emerald-300 font-medium">
              AI Document Drafting
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-bold text-surface-50 mb-3">
            {step === "select" && "What would you like to draft?"}
            {step === "form" && getFormTitle(selectedType)}
            {step === "preview" && "Review Your Document"}
          </h1>
          <p className="text-surface-400 max-w-xl mx-auto">
            {step === "select" &&
              "Select a document type below. Our AI will help you generate a professional legal document."}
            {step === "form" &&
              "Fill in the details below. All fields marked with * are required."}
            {step === "preview" &&
              "Review the AI-generated document below. You can download it as a PDF when ready."}
          </p>
        </div>

        {/* Step Content */}
        {step === "select" && (
          <DocumentTypeSelector onSelect={handleTypeSelect} />
        )}

        {step === "form" && selectedType === "rental_agreement" && (
          <RentalAgreementForm
            onDraftGenerated={handleDraftGenerated}
            prefillAct={prefillAct}
            prefillSection={prefillSection}
          />
        )}

        {step === "form" && selectedType && selectedType !== "rental_agreement" && (
          <DocumentForm
            documentType={selectedType}
            onDraftGenerated={handleDraftGenerated}
            prefillAct={prefillAct}
            prefillSection={prefillSection}
          />
        )}

        {step === "preview" && selectedType && (
          <DraftPreview
            draftText={draftText}
            disclaimer={disclaimer}
            documentType={selectedType}
          />
        )}
      </main>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer className="w-full px-6 py-6 text-center border-t border-surface-800/50">
        <p className="text-sm text-surface-500">
          LexIndia — AI-powered legal access for every Indian citizen
        </p>
      </footer>
    </div>
  );
}

export default function DraftingPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-surface-400">Loading...</div>}>
      <DraftingContent />
    </Suspense>
  );
}

function getFormTitle(type: DocumentType | null): string {
  switch (type) {
    case "legal_notice":
      return "Draft a Legal Notice";
    case "rti_application":
      return "Draft an RTI Application";
    case "fir_draft":
      return "Draft an FIR Complaint";
    case "rental_agreement":
      return "Create a Rental Agreement";
    case "affidavit":
      return "Draft an Affidavit";
    default:
      return "Draft a Document";
  }
}
