/**
 * Filing Portal Mapping
 * Maps Indian law acts to their corresponding filing portals and instructions
 */

export interface FilingOption {
  title: string;
  description: string;
  url: string;
  icon: string;
  type: "court" | "online_portal" | "helpline" | "legal_aid";
}

export interface FilingPortalInfo {
  actCode: string;
  actName: string;
  filingOptions: FilingOption[];
  defaultCourt?: string;
  timelineInfo?: string;
}

// Comprehensive mapping of Indian law acts to filing portals
const filingPortalsMap: Record<string, FilingPortalInfo> = {
  // PWDVA - Protection of Women from Domestic Violence Act
  PWDVA: {
    actCode: "PWDVA",
    actName: "Protection of Women from Domestic Violence Act",
    filingOptions: [
      {
        title: "File in Family Court",
        description: "File a case for protection order under PWDVA",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Women's Helpline",
        description: "24/7 Women's Helpline: 1090 or SMS ARAKSHAN to 56161",
        url: "tel:1090",
        icon: "📞",
        type: "helpline",
      },
      {
        title: "Legal Aid Services",
        description: "Free legal aid for women - Contact nearest Legal Aid Centre",
        url: "https://nalsa.gov.in/",
        icon: "⚖️",
        type: "legal_aid",
      },
      {
        title: "Police Station - Women's Cell",
        description: "File complaint with local police women's cell",
        url: "https://www.bhamashah.rajasthan.gov.in/",
        icon: "🚔",
        type: "court",
      },
    ],
    defaultCourt: "Family Court",
    timelineInfo: "Case typically decided within 60 days",
  },

  // IPC - Indian Penal Code (Criminal)
  IPC: {
    actCode: "IPC",
    actName: "Indian Penal Code",
    filingOptions: [
      {
        title: "File FIR (Criminal Case)",
        description: "File First Information Report at nearest police station",
        url: "https://www.ecourts.gov.in/",
        icon: "🚔",
        type: "court",
      },
      {
        title: "Criminal Court",
        description: "File case in District Criminal Court",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Legal Aid Services",
        description: "Free legal assistance for criminal cases",
        url: "https://nalsa.gov.in/",
        icon: "⚖️",
        type: "legal_aid",
      },
      {
        title: "Find Nearby Police Station",
        description: "Locate nearest police station",
        url: "https://maps.google.com/",
        icon: "📍",
        type: "court",
      },
    ],
    defaultCourt: "Criminal Court",
    timelineInfo: "FIR registration within 24 hours mandatory",
  },

  // CPA - Consumer Protection Act
  CPA: {
    actCode: "CPA",
    actName: "Consumer Protection Act",
    filingOptions: [
      {
        title: "District Consumer Forum",
        description: "File complaint in District Consumer Forum (online or offline)",
        url: "https://consumercomplaints.gov.in/",
        icon: "📝",
        type: "online_portal",
      },
      {
        title: "Online Complaint Portal (eDakhal)",
        description: "File complaint online through eDakhal portal",
        url: "https://edakhal.nic.in/",
        icon: "💻",
        type: "online_portal",
      },
      {
        title: "State Consumer Helpline",
        description: "Contact your state consumer protection authority",
        url: "https://consumercomplaints.gov.in/consumer-protection-authorities",
        icon: "📞",
        type: "helpline",
      },
      {
        title: "Consumer Guidance",
        description: "How to file consumer complaint - Step by step guide",
        url: "https://consumercomplaints.gov.in/guidance",
        icon: "📖",
        type: "legal_aid",
      },
    ],
    defaultCourt: "District Consumer Forum",
    timelineInfo: "Complaint should be filed within 2 years of cause of action",
  },

  // HMA - Hindu Marriage Act
  HMA: {
    actCode: "HMA",
    actName: "Hindu Marriage Act",
    filingOptions: [
      {
        title: "Family Court - Divorce",
        description: "File for divorce/dissolution of marriage",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Family Court - Maintenance",
        description: "File for maintenance and alimony",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Legal Aid Services",
        description: "Free legal consultation for family matters",
        url: "https://nalsa.gov.in/",
        icon: "⚖️",
        type: "legal_aid",
      },
      {
        title: "Mediation Services",
        description: "Family Counseling and Mediation",
        url: "https://www.ecourts.gov.in/",
        icon: "🤝",
        type: "legal_aid",
      },
    ],
    defaultCourt: "Family Court",
    timelineInfo: "Divorce case typically takes 1-3 years",
  },

  // ITA - Information Technology Act
  ITA: {
    actCode: "ITA",
    actName: "Information Technology Act",
    filingOptions: [
      {
        title: "Cybercrime Portal",
        description: "File cyber crime complaint with police",
        url: "https://cybercrime.gov.in/",
        icon: "🔐",
        type: "online_portal",
      },
      {
        title: "Criminal Court",
        description: "File case in District Criminal Court",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Report to Police",
        description: "File FIR at nearest police cybercrime cell",
        url: "tel:100",
        icon: "🚔",
        type: "helpline",
      },
      {
        title: "Legal Aid Services",
        description: "Free legal assistance for cyber crimes",
        url: "https://nalsa.gov.in/",
        icon: "⚖️",
        type: "legal_aid",
      },
    ],
    defaultCourt: "Criminal Court (Cyber Cell)",
    timelineInfo: "File complaint within 3 months for best results",
  },

  // RTI - Right to Information Act
  RTI: {
    actCode: "RTI",
    actName: "Right to Information Act",
    filingOptions: [
      {
        title: "File RTI Request Online",
        description: "Submit RTI request to government department",
        url: "https://rtionline.gov.in/",
        icon: "📋",
        type: "online_portal",
      },
      {
        title: "Department Official Portal",
        description: "Contact relevant department for RTI",
        url: "https://india.gov.in/",
        icon: "🏛️",
        type: "online_portal",
      },
      {
        title: "Central Information Commission",
        description: "Appeal to CIC if RTI request rejected",
        url: "https://www.cic.gov.in/",
        icon: "📞",
        type: "helpline",
      },
      {
        title: "RTI Guidelines & Help",
        description: "Learn how to file effective RTI requests",
        url: "https://rtionline.gov.in/help",
        icon: "📖",
        type: "legal_aid",
      },
    ],
    defaultCourt: "Central Information Commission",
    timelineInfo: "RTI response should be provided within 30 days",
  },

  // SC/ST Act - Scheduled Castes and Scheduled Tribes Act
  "SC/ST": {
    actCode: "SC/ST",
    actName: "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act",
    filingOptions: [
      {
        title: "File FIR (Atrocity Case)",
        description: "File First Information Report for atrocity case",
        url: "https://www.ecourts.gov.in/",
        icon: "🚔",
        type: "court",
      },
      {
        title: "Special Court (SC/ST Act)",
        description: "File case in special court designated for SC/ST Act",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "National Commission for SCs/STs",
        description: "Lodge complaint with NCSC/NCST",
        url: "https://ncsc.gov.in/",
        icon: "📞",
        type: "helpline",
      },
      {
        title: "Legal Aid Services",
        description: "Free legal assistance for SC/ST cases",
        url: "https://nalsa.gov.in/",
        icon: "⚖️",
        type: "legal_aid",
      },
    ],
    defaultCourt: "Special Court (SC/ST Act)",
    timelineInfo: "FIR must be registered without demanding bail or fees",
  },

  // CONST - Constitution of India
  CONST: {
    actCode: "CONST",
    actName: "Constitution of India",
    filingOptions: [
      {
        title: "Supreme Court",
        description: "File Writ Petition in Supreme Court",
        url: "https://www.supremecourtofindia.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "High Court",
        description: "File Writ Petition in High Court of your state",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Public Interest Litigation",
        description: "File PIL for public interest matters",
        url: "https://www.supremecourtofindia.gov.in/",
        icon: "📝",
        type: "court",
      },
      {
        title: "Legal Aid Services",
        description: "Free legal assistance for constitutional matters",
        url: "https://nalsa.gov.in/",
        icon: "⚖️",
        type: "legal_aid",
      },
    ],
    defaultCourt: "Supreme Court / High Court",
    timelineInfo: "Constitutional cases require written submissions and hearings",
  },

  // Child Marriage Act
  CHILD: {
    actCode: "CHILD",
    actName: "Prohibition of Child Marriage Act",
    filingOptions: [
      {
        title: "Family Court",
        description: "File to nullify child marriage in Family Court",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Police - Child Protection",
        description: "Report to police child protection unit",
        url: "tel:1098",
        icon: "🚔",
        type: "helpline",
      },
      {
        title: "Childline India",
        description: "24/7 Childline: Toll-free 1098",
        url: "tel:1098",
        icon: "📞",
        type: "helpline",
      },
      {
        title: "Women & Child Development Dept",
        description: "Contact WCD department of your state",
        url: "https://wcd.nic.in/",
        icon: "🏛️",
        type: "legal_aid",
      },
    ],
    defaultCourt: "Family Court",
    timelineInfo: "Child marriage nullification can be immediate in urgent cases",
  },

  // Default fallback
  DEFAULT: {
    actCode: "DEFAULT",
    actName: "Legal Matter",
    filingOptions: [
      {
        title: "Find Relevant Court",
        description: "Search for relevant court in your jurisdiction",
        url: "https://www.ecourts.gov.in/",
        icon: "⚖️",
        type: "court",
      },
      {
        title: "Legal Aid Services",
        description: "Free legal assistance in your state",
        url: "https://nalsa.gov.in/",
        icon: "⚖️",
        type: "legal_aid",
      },
      {
        title: "Bar Council",
        description: "Find registered lawyers in your area",
        url: "https://www.barcouncilofindia.org/",
        icon: "👨‍⚖️",
        type: "legal_aid",
      },
      {
        title: "Consult a Lawyer",
        description: "Book consultation with qualified lawyer",
        url: "https://www.lawyerscollective.org/",
        icon: "👨‍⚖️",
        type: "legal_aid",
      },
    ],
    defaultCourt: "District Court",
    timelineInfo: "Consult a qualified lawyer for proper guidance",
  },
};

/**
 * Get filing portal information based on act code
 * @param actCode - The act code (e.g., "PWDVA", "IPC", "CPA")
 * @returns FilingPortalInfo with all filing options
 */
export function getFilingPortal(actCode: string): FilingPortalInfo {
  // Extract base act code (e.g., "PWDVA-1" -> "PWDVA")
  const baseActCode = actCode.split("-")[0].toUpperCase();

  return filingPortalsMap[baseActCode] || filingPortalsMap.DEFAULT;
}

/**
 * Get all available act codes
 */
export function getAvailableActCodes(): string[] {
  return Object.keys(filingPortalsMap).filter((code) => code !== "DEFAULT");
}

/**
 * Get color for filing option type
 */
export function getOptionTypeColor(
  type: "court" | "online_portal" | "helpline" | "legal_aid"
): string {
  const colors: Record<string, string> = {
    court: "bg-blue-100 text-blue-800",
    online_portal: "bg-green-100 text-green-800",
    helpline: "bg-orange-100 text-orange-800",
    legal_aid: "bg-purple-100 text-purple-800",
  };
  return colors[type] || "bg-gray-100 text-gray-800";
}

/**
 * Get icon emoji for filing option type
 */
export function getOptionTypeIcon(
  type: "court" | "online_portal" | "helpline" | "legal_aid"
): string {
  const icons: Record<string, string> = {
    court: "⚖️",
    online_portal: "💻",
    helpline: "📞",
    legal_aid: "🤝",
  };
  return icons[type] || "📋";
}
