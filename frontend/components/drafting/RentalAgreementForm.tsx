"use client";

/**
 * RentalAgreementForm — Specialised form for creating rental agreements.
 * Includes landlord/tenant details, property info, and 3 toggleable clauses:
 *   1. No Pets Allowed
 *   2. Lock-in Period (11 months)
 *   3. Maintenance by Tenant
 */

import { useState } from "react";
import { generateDraft } from "@/lib/api";

interface Props {
  onDraftGenerated: (text: string, disclaimer: string) => void;
  prefillAct?: string;
  prefillSection?: string;
}

export default function RentalAgreementForm({
  onDraftGenerated,
  prefillAct,
  prefillSection,
}: Props) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Landlord
  const [landlordName, setLandlordName] = useState("");
  const [landlordAddress, setLandlordAddress] = useState("");
  const [landlordPhone, setLandlordPhone] = useState("");

  // Tenant
  const [tenantName, setTenantName] = useState("");
  const [tenantAddress, setTenantAddress] = useState("");
  const [tenantPhone, setTenantPhone] = useState("");

  // Property & Terms
  const [propertyAddress, setPropertyAddress] = useState("");
  const [monthlyRent, setMonthlyRent] = useState("");
  const [securityDeposit, setSecurityDeposit] = useState("");
  const [startDate, setStartDate] = useState("");
  const [duration, setDuration] = useState("11");

  // 3 Fixed Clauses
  const [noPets, setNoPets] = useState(false);
  const [lockIn, setLockIn] = useState(false);
  const [maintenanceByTenant, setMaintenanceByTenant] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        document_type: "rental_agreement",
        sender: {
          full_name: landlordName,
          address: landlordAddress,
          phone: landlordPhone || undefined,
        },
        recipient: {
          full_name: tenantName,
          address: tenantAddress,
          phone: tenantPhone || undefined,
        },
        subject: `Rental agreement for property at ${propertyAddress}`,
        rental_details: {
          property_address: propertyAddress,
          monthly_rent: parseFloat(monthlyRent),
          security_deposit: parseFloat(securityDeposit),
          agreement_start_date: startDate,
          duration_months: parseInt(duration),
          clauses: {
            no_pets_allowed: noPets,
            lock_in_period: lockIn,
            maintenance_by_tenant: maintenanceByTenant,
          },
        },
        language: "en",
        act_name: prefillAct || undefined,
        law_section_id: prefillSection || undefined,
      };

      const result = await generateDraft(payload);
      onDraftGenerated(result.draft_text, result.disclaimer);
    } catch (err: any) {
      console.error("Draft generation failed:", err);
      
      // Handle error response
      const errorDetail = err?.response?.data?.detail;
      let errorMessage = "Failed to generate the agreement. Please try again.";
      
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
      {/* ── Landlord Details ──────────────────────────────────────────── */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-display font-semibold text-surface-50 mb-5 flex items-center gap-2">
          <span className="text-amber-400">①</span>
          Landlord Details
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Full Name *</label>
            <input
              type="text"
              value={landlordName}
              onChange={(e) => setLandlordName(e.target.value)}
              className="input-glass"
              placeholder="Landlord's full legal name"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Address *</label>
            <textarea
              value={landlordAddress}
              onChange={(e) => setLandlordAddress(e.target.value)}
              className="input-glass min-h-[70px]"
              placeholder="Landlord's permanent address"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Phone</label>
            <input
              type="tel"
              value={landlordPhone}
              onChange={(e) => setLandlordPhone(e.target.value)}
              className="input-glass"
              placeholder="+91 XXXX XXXXXX"
            />
          </div>
        </div>
      </div>

      {/* ── Tenant Details ────────────────────────────────────────────── */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-display font-semibold text-surface-50 mb-5 flex items-center gap-2">
          <span className="text-amber-400">②</span>
          Tenant Details
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Full Name *</label>
            <input
              type="text"
              value={tenantName}
              onChange={(e) => setTenantName(e.target.value)}
              className="input-glass"
              placeholder="Tenant's full legal name"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Current Address *</label>
            <textarea
              value={tenantAddress}
              onChange={(e) => setTenantAddress(e.target.value)}
              className="input-glass min-h-[70px]"
              placeholder="Tenant's current address"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Phone</label>
            <input
              type="tel"
              value={tenantPhone}
              onChange={(e) => setTenantPhone(e.target.value)}
              className="input-glass"
              placeholder="+91 XXXX XXXXXX"
            />
          </div>
        </div>
      </div>

      {/* ── Property & Terms ──────────────────────────────────────────── */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-display font-semibold text-surface-50 mb-5 flex items-center gap-2">
          <span className="text-amber-400">③</span>
          Property & Terms
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-surface-300 mb-1.5">Property Address *</label>
            <textarea
              value={propertyAddress}
              onChange={(e) => setPropertyAddress(e.target.value)}
              className="input-glass min-h-[70px]"
              placeholder="Complete address of the rental property"
              required
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Monthly Rent (₹) *</label>
              <input
                type="number"
                value={monthlyRent}
                onChange={(e) => setMonthlyRent(e.target.value)}
                className="input-glass"
                placeholder="15000"
                min="1"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Security Deposit (₹) *</label>
              <input
                type="number"
                value={securityDeposit}
                onChange={(e) => setSecurityDeposit(e.target.value)}
                className="input-glass"
                placeholder="50000"
                min="0"
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Start Date *</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="input-glass"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-surface-300 mb-1.5">Duration (months)</label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="input-glass"
              >
                <option value="6">6 months</option>
                <option value="11">11 months</option>
                <option value="12">12 months</option>
                <option value="24">24 months</option>
                <option value="36">36 months</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* ── Optional Clauses ──────────────────────────────────────────── */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-display font-semibold text-surface-50 mb-5 flex items-center gap-2">
          <span className="text-amber-400">④</span>
          Optional Clauses
        </h2>
        <div className="space-y-4">
          {/* No Pets */}
          <label className="flex items-center gap-4 p-4 rounded-xl border border-surface-700/30 bg-surface-800/30 hover:bg-surface-800/50 transition-colors cursor-pointer">
            <div className="relative">
              <input
                type="checkbox"
                checked={noPets}
                onChange={(e) => setNoPets(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 rounded-full bg-surface-700 peer-checked:bg-amber-500 transition-colors" />
              <div className="absolute left-0.5 top-0.5 w-5 h-5 rounded-full bg-white shadow-md transition-transform peer-checked:translate-x-5" />
            </div>
            <div>
              <span className="text-surface-100 font-medium block">🐾 No Pets Allowed</span>
              <span className="text-sm text-surface-400">Tenant shall not keep any pets on the premises.</span>
            </div>
          </label>

          {/* Lock-in Period */}
          <label className="flex items-center gap-4 p-4 rounded-xl border border-surface-700/30 bg-surface-800/30 hover:bg-surface-800/50 transition-colors cursor-pointer">
            <div className="relative">
              <input
                type="checkbox"
                checked={lockIn}
                onChange={(e) => setLockIn(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 rounded-full bg-surface-700 peer-checked:bg-amber-500 transition-colors" />
              <div className="absolute left-0.5 top-0.5 w-5 h-5 rounded-full bg-white shadow-md transition-transform peer-checked:translate-x-5" />
            </div>
            <div>
              <span className="text-surface-100 font-medium block">🔒 Lock-in Period (11 months)</span>
              <span className="text-sm text-surface-400">Neither party may terminate during the first 11 months.</span>
            </div>
          </label>

          {/* Maintenance by Tenant */}
          <label className="flex items-center gap-4 p-4 rounded-xl border border-surface-700/30 bg-surface-800/30 hover:bg-surface-800/50 transition-colors cursor-pointer">
            <div className="relative">
              <input
                type="checkbox"
                checked={maintenanceByTenant}
                onChange={(e) => setMaintenanceByTenant(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 rounded-full bg-surface-700 peer-checked:bg-amber-500 transition-colors" />
              <div className="absolute left-0.5 top-0.5 w-5 h-5 rounded-full bg-white shadow-md transition-transform peer-checked:translate-x-5" />
            </div>
            <div>
              <span className="text-surface-100 font-medium block">🔧 Maintenance by Tenant</span>
              <span className="text-sm text-surface-400">Tenant is responsible for all minor repairs and routine maintenance.</span>
            </div>
          </label>
        </div>
      </div>

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
            Generating Agreement...
          </span>
        ) : (
          "🏠 Generate Rental Agreement"
        )}
      </button>
    </form>
  );
}
