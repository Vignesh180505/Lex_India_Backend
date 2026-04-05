"use client";

import React, { useState } from "react";
import {
  getFilingPortal,
  getOptionTypeColor,
  FilingPortalInfo,
  FilingOption,
} from "@/lib/filingPortals";

interface FilingModalProps {
  actCode: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function FilingModal({ actCode, isOpen, onClose }: FilingModalProps) {
  const [selectedOption, setSelectedOption] = useState<FilingOption | null>(null);
  const portalInfo = getFilingPortal(actCode);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 transition-opacity duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Container */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Modal Header */}
          <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 text-white flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">{portalInfo.actName}</h2>
              <p className="text-blue-100 text-sm mt-1">File a case under this act</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-blue-800 rounded-full p-2 transition-colors"
              aria-label="Close modal"
            >
              ✕
            </button>
          </div>

          {/* Modal Content */}
          <div className="p-6">
            {/* Default Court Info */}
            {portalInfo.defaultCourt && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-gray-600">
                  <strong>Primary Forum:</strong> {portalInfo.defaultCourt}
                </p>
                {portalInfo.timelineInfo && (
                  <p className="text-sm text-gray-600 mt-2">
                    <strong>Timeline:</strong> {portalInfo.timelineInfo}
                  </p>
                )}
              </div>
            )}

            {/* Filing Options */}
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-800 mb-4">
                How to file your case:
              </h3>

              {portalInfo.filingOptions.map((option, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedOption(option)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedOption === option
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-blue-300 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0">{option.icon}</span>
                    <div className="flex-grow">
                      <div className="font-semibold text-gray-900">
                        {option.title}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        {option.description}
                      </div>
                      <div className={`mt-2 inline-block px-3 py-1 rounded-full text-xs font-medium ${getOptionTypeColor(option.type)}`}>
                        {option.type.replace("_", " ").toUpperCase()}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            {/* Selected Option Details */}
            {selectedOption && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-3">
                  Next Step: {selectedOption.title}
                </h4>
                <p className="text-sm text-green-800 mb-4">
                  {selectedOption.description}
                </p>

                {/* Action Button */}
                {selectedOption.url.startsWith("tel:") ? (
                  <a
                    href={selectedOption.url}
                    className="inline-block w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg text-center transition-colors"
                  >
                    📞 Call Now
                  </a>
                ) : (
                  <a
                    href={selectedOption.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg text-center transition-colors"
                  >
                    🌐 Open Portal / Visit Website →
                  </a>
                )}

                <p className="text-xs text-green-700 mt-3">
                  💡 Tip: Keep your law section number, query details, and supporting documents ready before proceeding.
                </p>
              </div>
            )}

            {/* Important Notice */}
            <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>⚠️ Important:</strong> This information is for guidance only.
                Consult a qualified lawyer for legal advice specific to your case.
              </p>
            </div>
          </div>

          {/* Modal Footer */}
          <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-lg transition-colors"
            >
              Close
            </button>
            {selectedOption && selectedOption.url.startsWith("tel:") === false && (
              <a
                href={selectedOption.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg text-center transition-colors"
              >
                Open Portal →
              </a>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
