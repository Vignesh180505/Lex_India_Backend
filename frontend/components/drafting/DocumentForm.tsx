"use client";

/**
 * DocumentForm — Multi-step form for Legal Notice, RTI, FIR, and Affidavit.
 * Collects sender/recipient details, incident info, and calls the draft API.
 */

import { useState } from "react";
import { generateDraft } from "@/lib/api";

type DocumentType = "legal_notice" | "rti_application" | "fir_draft" | "affidavit";

interface Props {
  documentType: DocumentType;
  onDraftGenerated: (text: string, disclaimer: string) => void;
  prefillAct?: string;
  prefillSection?: string;
}

export default function DocumentForm({
  documentType,
  onDraftGenerated,
  prefillAct,
  prefillSection,
}: Props) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sender details
  const [senderName, setSenderName] = useState("");
  const [senderAddress, setSenderAddress] = useState("");
  const [senderPhone, setSenderPhone] = useState("");
  const [senderEmail, setSenderEmail] = useState("");

  // Recipient details
  const [recipientName, setRecipientName] = useState("");
  const [recipientAddress, setRecipientAddress] = useState("");
  const [recipientPhone, setRecipientPhone] = useState("");

  // Incident / Subject
  const [subject, setSubject] = useState("");
  const [incidentDate, setIncidentDate] = useState("");
  const [incidentLocation, setIncidentLocation] = useState("");
  const [desiredOutcome, setDesiredOutcome] = useState("");

  const needsRecipient = documentType === "legal_notice" || documentType === "fir_draft";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const payload: any = {
        document_type: documentType,
        sender: {
          full_name: senderName,
          address: senderAddress,
          phone: senderPhone || undefined,
          email: senderEmail || undefined,
        },
        subject,
        language: "en",
      };

      if (needsRecipient && recipientName) {
        payload.recipient = {
          full_name: recipientName,
          address: recipientAddress,
          phone: recipientPhone || undefined,
        };
      }

      if (incidentDate) payload.incident_date = incidentDate;
      if (incidentLocation) payload.incident_location = incidentLocation;
      if (desiredOutcome) payload.desired_outcome = desiredOutcome;

      // Pre-fill from search results
      if (prefillAct) payload.act_name = prefillAct;
      if (prefillSection) payload.law_section_id = prefillSection;

      const result = await generateDraft(payload);
      onDraftGenerated(result.draft_text, result.disclaimer);
    } catch (err: any) {
      console.error("Draft generation failed:", err);
      
      // Handle error response
      const errorDetail = err?.response?.data?.detail;
      let errorMessage = "Failed to generate the document. Please try again.";
      
      if (typeof errorDetail === "string") {
        errorMessage = errorDetail;
      } else if (Array.isArray(errorDetail)) {
        // Pydantic validation errors
        errorMessage = errorDetail
          .map((e: any) => `${e.loc?.join(".")}: ${e.msg}`)
          .join(" | ");
      } else if (errorDetail && typeof errorDetail === "object") {
        errorMessage = JSON.stringify(errorDetail);
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-8 animate-fade-up">
      {/* ── Section: Your Details ─────────────────────────────────────── */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-display font-semibold text-surface-50 mb-5 flex items-center gap-2">
          <span className="text-brand-400">①</span>
          Your Details
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Full Name *</label>
            <input
              type="text"
              value={senderName}
              onChange={(e) => setSenderName(e.target.value)}
              className="input-glass"
              placeholder="Enter your full legal name"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Address *</label>
            <textarea
              value={senderAddress}
              onChange={(e) => setSenderAddress(e.target.value)}
              className="input-glass min-h-[80px]"
              placeholder="Enter your complete address"
              required
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Phone</label>
              <input
                type="tel"
                value={senderPhone}
                onChange={(e) => setSenderPhone(e.target.value)}
                className="input-glass"
                placeholder="+91 XXXX XXXXXX"
              />
            </div>
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Email</label>
              <input
                type="email"
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
                className="input-glass"
                placeholder="your@email.com"
              />
            </div>
          </div>
        </div>
      </div>

      {/* ── Section: Recipient Details (conditional) ───────────────────── */}
      {needsRecipient && (
        <div className="glass-card p-6">
          <h2 className="text-lg font-display font-semibold text-surface-50 mb-5 flex items-center gap-2">
            <span className="text-brand-400">②</span>
            {documentType === "fir_draft" ? "Accused / Against Whom" : "Recipient Details"}
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Full Name *</label>
              <input
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                className="input-glass"
                placeholder="Enter recipient's full name"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Address *</label>
              <textarea
                value={recipientAddress}
                onChange={(e) => setRecipientAddress(e.target.value)}
                className="input-glass min-h-[80px]"
                placeholder="Enter recipient's complete address"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Phone</label>
              <input
                type="tel"
                value={recipientPhone}
                onChange={(e) => setRecipientPhone(e.target.value)}
                className="input-glass"
                placeholder="+91 XXXX XXXXXX"
              />
            </div>
          </div>
        </div>
      )}

      {/* ── Section: Subject / Incident ────────────────────────────────── */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-display font-semibold text-surface-50 mb-5 flex items-center gap-2">
          <span className="text-brand-400">{needsRecipient ? "③" : "②"}</span>
          {documentType === "rti_application"
            ? "Information Sought"
            : documentType === "affidavit"
            ? "Declaration Details"
            : "Incident Details"}
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">
              {documentType === "rti_application"
                ? "What information do you want to request? *"
                : documentType === "affidavit"
                ? "What are you declaring? *"
                : "Describe the incident in detail *"}
            </label>
            <textarea
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="input-glass min-h-[120px]"
              placeholder={
                documentType === "rti_application"
                  ? "Describe the specific information you want from the government department..."
                  : documentType === "affidavit"
                  ? "State the facts you wish to declare under oath..."
                  : "Describe what happened, including all relevant details..."
              }
              required
              minLength={10}
            />
          </div>

          {(documentType === "legal_notice" || documentType === "fir_draft") && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-surface-300 mb-1.5">Date of Incident</label>
                <input
                  type="date"
                  value={incidentDate}
                  onChange={(e) => setIncidentDate(e.target.value)}
                  className="input-glass"
                />
              </div>
              <div>
                <label className="block text-sm text-surface-300 mb-1.5">Location</label>
                <input
                  type="text"
                  value={incidentLocation}
                  onChange={(e) => setIncidentLocation(e.target.value)}
                  className="input-glass"
                  placeholder="City, State"
                />
              </div>
            </div>
          )}

          {documentType === "legal_notice" && (
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Desired Outcome</label>
              <input
                type="text"
                value={desiredOutcome}
                onChange={(e) => setDesiredOutcome(e.target.value)}
                className="input-glass"
                placeholder="e.g., Refund of ₹50,000 within 15 days"
              />
            </div>
          )}
        </div>
      </div>

      {/* Pre-fill indicator */}
      {(prefillAct || prefillSection) && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-500/10 border border-brand-500/20 text-sm text-brand-300">
          <span>📎</span>
          <span>
            Law context attached: <strong>{prefillSection || prefillAct}</strong>
          </span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="px-5 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="btn-primary w-full text-center py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-3">
            <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Generating Document...
          </span>
        ) : (
          "✨ Generate Document with AI"
        )}
      </button>
    </form>
  );
}
