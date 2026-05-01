"use client";

/**
 * DocumentTypeSelector — Card grid for picking the document type to draft.
 * 5 cards: Legal Notice, RTI Application, FIR Draft, Rental Agreement, Affidavit.
 */

type DocumentType =
  | "legal_notice"
  | "rti_application"
  | "fir_draft"
  | "rental_agreement"
  | "affidavit";

interface Props {
  onSelect: (type: DocumentType) => void;
}

const DOCUMENT_TYPES: {
  id: DocumentType;
  icon: string;
  title: string;
  description: string;
  color: string;
}[] = [
  {
    id: "legal_notice",
    icon: "⚖️",
    title: "Legal Notice",
    description:
      "Formal notice for cheque bounce, consumer disputes, property matters, or contract breaches.",
    color: "from-blue-500/20 to-blue-600/10 border-blue-500/20 hover:border-blue-400/50",
  },
  {
    id: "rti_application",
    icon: "📋",
    title: "RTI Application",
    description:
      "Right to Information request to any government department under RTI Act, 2005.",
    color: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/20 hover:border-emerald-400/50",
  },
  {
    id: "fir_draft",
    icon: "🚔",
    title: "FIR Draft",
    description:
      "First Information Report complaint draft to be filed at a police station.",
    color: "from-red-500/20 to-red-600/10 border-red-500/20 hover:border-red-400/50",
  },
  {
    id: "rental_agreement",
    icon: "🏠",
    title: "Rental Agreement",
    description:
      "Standard rental/lease agreement with optional clauses for No Pets, Lock-in, and Maintenance.",
    color: "from-amber-500/20 to-amber-600/10 border-amber-500/20 hover:border-amber-400/50",
  },
  {
    id: "affidavit",
    icon: "📜",
    title: "Affidavit",
    description:
      "General-purpose sworn affidavit for court submissions, verification, or declarations.",
    color: "from-purple-500/20 to-purple-600/10 border-purple-500/20 hover:border-purple-400/50",
  },
];

export default function DocumentTypeSelector({ onSelect }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 animate-fade-up">
      {DOCUMENT_TYPES.map((doc, index) => (
        <button
          key={doc.id}
          onClick={() => onSelect(doc.id)}
          className={`
            text-left p-6 rounded-2xl border backdrop-blur-sm
            bg-gradient-to-br ${doc.color}
            hover:scale-[1.02] active:scale-[0.98]
            transition-all duration-200 group
          `}
          style={{ animationDelay: `${index * 80}ms` }}
          id={`doc-type-${doc.id}`}
        >
          <span className="text-3xl block mb-3 group-hover:scale-110 transition-transform">
            {doc.icon}
          </span>
          <h3 className="text-lg font-display font-semibold text-surface-50 mb-2">
            {doc.title}
          </h3>
          <p className="text-sm text-surface-400 leading-relaxed">
            {doc.description}
          </p>
        </button>
      ))}
    </div>
  );
}
