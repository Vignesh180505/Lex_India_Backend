/**
 * translations.ts — Complete static translation dictionary for LexIndia.
 *
 * All UI strings for English, Tamil (தமிழ்), and Hindi (हिंदी).
 * This replaces the i18next JSON files to eliminate the hydration mismatch
 * caused by async i18n initialization on the client.
 */

export type Language = "english" | "tamil" | "hindi";

export const translations = {
  english: {
    // ── General ──────────────────────────────────────────────────────
    appName: "LexIndia",
    tagline: "AI-Powered Indian Legal Access",
    searchPlaceholder: "Describe your legal problem in plain language...",
    searchJudgmentsPlaceholder:
      "Search for judgments... (e.g. 'property dispute', 'tenant eviction')",
    searchButton: "Find Applicable Laws",
    clearButton: "Clear",
    loading: "Searching Indian legal database...",
    error: "Something went wrong. Please try again.",
    retry: "Retry",
    close: "Close",
    readMore: "Read More",
    noResults: "No directly applicable laws found for your query.",
    newSearch: "New search",
    yourQuery: "Your query:",

    // ── Navigation ───────────────────────────────────────────────────
    navHome: "Home",
    navBrowse: "Browse Laws",
    navJudgments: "Judgments",
    navDraft: "Legal Tools",

    // ── Browse Laws ──────────────────────────────────────────────────
    browseLaws: "Browse Laws",
    browseSubtitle:
      "Explore Indian laws by Act. Click on an Act to filter sections.",
    allActs: "All Acts",
    sectionsFound: "sections found",
    page: "Page",
    of: "of",

    // ── Browse Judgments ──────────────────────────────────────────────
    browseJudgments: "Browse Judgments",
    browseByCourtCategory: "Browse by Court & Category",
    courtJudgmentsDatabase: "Court Judgments Database",
    judgmentsBrowseTitle: "Browse Court Judgments",
    judgmentsBrowseSubtitle:
      "Search through Indian court judgments from the Supreme Court, High Courts, and District Courts. Filter by court type and legal category.",
    searchCourtJudgments: "Search Indian Court Judgments",
    searchCourtJudgmentsSubtitle:
      "Enter a legal topic, case type, or keywords above to search through thousands of court judgments from Indian courts.",
    noJudgmentsFound: "No judgments found for your search.",
    tryDifferentKeywords: "Try different keywords or remove filters.",
    showing: "Showing",
    judgments: "judgments",
    searching: "Searching…",
    searchJudgments: "Search Judgments",
    readFullJudgment: "Read Full Judgment",

    // ── Severity ─────────────────────────────────────────────────────
    high: "HIGH",
    medium: "MEDIUM",
    low: "LOW",

    // ── Law Card ─────────────────────────────────────────────────────
    legalPenalty: "Legal Penalty",
    legalPunishment: "Legal Punishment",
    viewFullLaw: "View Full Law",
    viewOriginal: "View original law text",
    hideOriginal: "Hide original law text",
    fileCase: "File a Case",
    filingCase: "Filing Case",
    draftDocument: "Draft Document",
    relevance: "Relevance",

    // ── Filters ──────────────────────────────────────────────────────
    court: "Court",
    category: "Category",
    date: "Date",
    outcome: "Outcome",
    allCourts: "All Courts",
    allCategories: "All Categories",

    // ── Courts ───────────────────────────────────────────────────────
    supremeCourt: "Supreme Court",
    highCourt: "High Court",
    districtCourt: "District Court",

    // ── Categories ───────────────────────────────────────────────────
    criminal: "Criminal",
    civil: "Civil",
    family: "Family",
    property: "Property",
    labour: "Labour",
    consumer: "Consumer",

    // ── Results page ─────────────────────────────────────────────────
    similarCases: "Similar Past Cases",
    winsFor: "Wins for",
    inCases: "in",
    totalCases: "Total Cases",
    winRate: "Win Rate",
    petitionerWon: "Petitioner Won",
    respondentWon: "Respondent Won",
    partial: "Partial",
    unclear: "Unclear",
    petitioner: "Petitioner",
    respondent: "Respondent",
    whoDoesLawFavour: "Who Does the Law Favour?",
    analysingOutcomes: "Analysing judgment outcomes…",
    noSimilarCases: "No similar past cases found for this query.",
    couldNotLoadCases: "Could not load similar cases.",
    resultsFound: "results found in",
    resultFound: "result found in",
    detected: "Detected",
    tamilLang: "Tamil",
    hindiLang: "Hindi",

    // ── AI Summary ───────────────────────────────────────────────────
    explanation: "Explanation",
    applicableLaws: "Applicable Laws",
    advice: "Advice",
    aiSummaryTitle: "AI Legal Summary",

    // ── Pagination ───────────────────────────────────────────────────
    nextPage: "Next →",
    prevPage: "← Previous",
    previous: "Previous",
    next: "Next",

    // ── Mode ─────────────────────────────────────────────────────────
    citizenMode: "Citizen",
    lawyerMode: "Lawyer",

    // ── Language ─────────────────────────────────────────────────────
    languageLabel: "EN",

    // ── Categories (home page) ───────────────────────────────────────
    categoryCriminal: "Criminal",
    categoryCivil: "Civil",
    categoryConsumer: "Consumer",

    // ── Example prompts ──────────────────────────────────────────────
    examplePrompt1: "My landlord is not returning my security deposit",
    examplePrompt2: "Someone threatened me online on social media",
    examplePrompt3:
      "I bought a defective product and the seller refuses a refund",

    // ── Footer / Disclaimer ──────────────────────────────────────────
    footerText: "LexIndia — AI-powered legal access for every Indian citizen",
    disclaimer:
      "This is general legal information, not legal advice. Consult a qualified lawyer.",
    aiPoweredLegalAccess: "AI-Powered Legal Access",
    knowYourRights: "Know Your Rights",
    underIndianLaw: "Under Indian Law",
  },

  tamil: {
    appName: "LexIndia",
    tagline: "செயற்கை நுண்ணறிவு மூலம் இந்திய சட்ட அணுகல்",
    searchPlaceholder: "உங்கள் சட்ட சிக்கலை எளிய மொழியில் விவரிக்கவும்...",
    searchJudgmentsPlaceholder:
      "தீர்ப்புகளைத் தேடுங்கள்... (எ.கா. 'சொத்து தகராறு', 'குத்தகையாளர் வெளியேற்றம்')",
    searchButton: "பொருந்தும் சட்டங்களைக் கண்டறியவும்",
    clearButton: "அழி",
    loading: "இந்திய சட்ட தரவுத்தளத்தில் தேடுகிறது...",
    error: "ஏதோ தவறு ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.",
    retry: "மீண்டும் முயற்சிக்க",
    close: "மூடு",
    readMore: "மேலும் படிக்க",
    noResults:
      "உங்கள் வினவலுக்கு நேரடியாகப் பொருந்தும் சட்டங்கள் எதுவும் கிடைக்கவில்லை.",
    newSearch: "புதிய தேடல்",
    yourQuery: "உங்கள் வினவல்:",

    navHome: "முகப்பு",
    navBrowse: "சட்டங்களை உலாவுக",
    navJudgments: "தீர்ப்புகள்",
    navDraft: "சட்ட கருவிகள்",

    browseLaws: "சட்டங்களை உலாவுக",
    browseSubtitle:
      "சட்டத்தின்படி இந்திய சட்டங்களை ஆராயுங்கள். பிரிவுகளை வடிகட்ட ஒரு சட்டத்தை கிளிக் செய்யவும்.",
    allActs: "அனைத்து சட்டங்கள்",
    sectionsFound: "பிரிவுகள் கண்டறியப்பட்டன",
    page: "பக்கம்",
    of: "இல்",

    browseJudgments: "தீர்ப்புகளை உலாவுக",
    browseByCourtCategory: "நீதிமன்றம் & வகை வாரியாக",
    courtJudgmentsDatabase: "நீதிமன்ற தீர்ப்புகள் தரவுத்தளம்",
    judgmentsBrowseTitle: "நீதிமன்ற தீர்ப்புகளை உலாவுக",
    judgmentsBrowseSubtitle:
      "உச்ச நீதிமன்றம், உயர் நீதிமன்றங்கள் மற்றும் மாவட்ட நீதிமன்றங்களின் இந்திய நீதிமன்ற தீர்ப்புகளில் தேடுங்கள்.",
    searchCourtJudgments: "இந்திய நீதிமன்ற தீர்ப்புகளை தேடுங்கள்",
    searchCourtJudgmentsSubtitle:
      "ஆயிரக்கணக்கான நீதிமன்ற தீர்ப்புகளில் தேட மேலே ஒரு சட்ட தலைப்பு அல்லது முக்கிய வார்த்தைகளை உள்ளிடவும்.",
    noJudgmentsFound: "உங்கள் தேடலுக்கு தீர்ப்புகள் எதுவும் கிடைக்கவில்லை.",
    tryDifferentKeywords:
      "வேறு முக்கிய வார்த்தைகளை முயற்சிக்கவும் அல்லது வடிகட்டிகளை அகற்றவும்.",
    showing: "காண்பிக்கிறது",
    judgments: "தீர்ப்புகள்",
    searching: "தேடுகிறது…",
    searchJudgments: "தீர்ப்புகளைத் தேடு",
    readFullJudgment: "முழு தீர்ப்பைப் படிக்க",

    high: "அதிகம்",
    medium: "நடுத்தரம்",
    low: "குறைவு",

    legalPenalty: "சட்டபூர்வமான அபராதம்",
    legalPunishment: "சட்டபூர்வமான தண்டனை",
    viewFullLaw: "முழு சட்டத்தைக் காண்க",
    viewOriginal: "அசல் சட்ட உரையைக் காண்க",
    hideOriginal: "அசல் சட்ட உரையை மறைக்க",
    fileCase: "வழக்குத் தாக்கல் செய்யவும்",
    filingCase: "வழக்கு தாக்கல்",
    draftDocument: "ஆவணம் தயாரிக்க",
    relevance: "தொடர்பு",

    court: "நீதிமன்றம்",
    category: "வகை",
    date: "தேதி",
    outcome: "முடிவு",
    allCourts: "அனைத்து நீதிமன்றங்கள்",
    allCategories: "அனைத்து வகைகள்",

    supremeCourt: "உச்ச நீதிமன்றம்",
    highCourt: "உயர் நீதிமன்றம்",
    districtCourt: "மாவட்ட நீதிமன்றம்",

    criminal: "குற்றவியல்",
    civil: "சிவில்",
    family: "குடும்பம்",
    property: "சொத்து",
    labour: "தொழிலாளர்",
    consumer: "நுகர்வோர்",

    similarCases: "ஒத்த வழக்குகள்",
    winsFor: "வெற்றி",
    inCases: "இல்",
    totalCases: "மொத்த வழக்குகள்",
    winRate: "வெற்றி விகிதம்",
    petitionerWon: "மனுதாரர் வெற்றி",
    respondentWon: "எதிர்மனு தாரர் வெற்றி",
    partial: "பகுதி",
    unclear: "தெளிவற்றது",
    petitioner: "மனுதாரர்",
    respondent: "எதிர்மனு தாரர்",
    whoDoesLawFavour: "சட்டம் யாருக்கு சாதகமானது?",
    analysingOutcomes: "தீர்ப்பு முடிவுகளை பகுப்பாய்வு செய்கிறது…",
    noSimilarCases:
      "இந்த வினவலுக்கு ஒத்த வழக்குகள் எதுவும் கிடைக்கவில்லை.",
    couldNotLoadCases: "ஒத்த வழக்குகளை ஏற்ற முடியவில்லை.",
    resultsFound: "முடிவுகள் கிடைத்தன",
    resultFound: "முடிவு கிடைத்தது",
    detected: "கண்டறியப்பட்டது",
    tamilLang: "தமிழ்",
    hindiLang: "ஹிந்தி",

    explanation: "விளக்கம்",
    applicableLaws: "பொருந்தும் சட்டங்கள்",
    advice: "அறிவுரை",
    aiSummaryTitle: "AI சட்ட சுருக்கம்",

    nextPage: "அடுத்து →",
    prevPage: "← முந்தைய",
    previous: "முந்தைய",
    next: "அடுத்து",

    citizenMode: "குடிமகன்",
    lawyerMode: "வழக்கறிஞர்",

    languageLabel: "தமி",

    categoryCriminal: "குற்றவியல்",
    categoryCivil: "சிவில்",
    categoryConsumer: "நுகர்வோர்",

    examplePrompt1:
      "என் வீட்டு உரிமையாளர் எனது பாதுகாப்பு வைப்புத்தொகையைத் திருப்பித் தரவில்லை",
    examplePrompt2:
      "சமூக ஊடகத்தில் யாரோ என்னை ஆன்லைனில் மிரட்டினார்கள்",
    examplePrompt3:
      "நான் குறைபாடுள்ள பொருளை வாங்கினேன், விற்பனையாளர் பணத்தைத் திருப்பித் தர மறுக்கிறார்",

    footerText:
      "LexIndia — ஒவ்வொரு இந்திய குடிமகனுக்கும் AI-இயங்கும் சட்ட அணுகல்",
    disclaimer:
      "இது பொதுவான சட்ட தகவல், சட்ட ஆலோசனை அல்ல. தகுதியான வழக்கறிஞரை அணுகவும்.",
    aiPoweredLegalAccess: "AI-இயங்கும் சட்ட அணுகல்",
    knowYourRights: "உங்கள் உரிமைகளை அறியுங்கள்",
    underIndianLaw: "இந்திய சட்டத்தின் கீழ்",
  },

  hindi: {
    appName: "LexIndia",
    tagline: "AI-संचालित भारतीय कानूनी पहुँच",
    searchPlaceholder: "अपनी कानूनी समस्या सरल भाषा में बताएं...",
    searchJudgmentsPlaceholder:
      "फैसलों की खोज करें... (जैसे 'संपत्ति विवाद', 'किरायेदार बेदखली')",
    searchButton: "लागू कानून खोजें",
    clearButton: "हटाएं",
    loading: "भारतीय कानूनी डेटाबेस में खोज रहे हैं...",
    error: "कुछ गलत हो गया। कृपया पुनः प्रयास करें।",
    retry: "पुनः प्रयास करें",
    close: "बंद करें",
    readMore: "और पढ़ें",
    noResults: "आपकी क्वेरी के लिए कोई सीधे लागू कानून नहीं मिले।",
    newSearch: "नई खोज",
    yourQuery: "आपकी क्वेरी:",

    navHome: "होम",
    navBrowse: "कानून ब्राउज़ करें",
    navJudgments: "फैसले",
    navDraft: "कानूनी उपकरण",

    browseLaws: "कानून ब्राउज़ करें",
    browseSubtitle:
      "अधिनियम द्वारा भारतीय कानूनों का अन्वेषण करें। धाराओं को फ़िल्टर करने के लिए किसी अधिनियम पर क्लिक करें।",
    allActs: "सभी अधिनियम",
    sectionsFound: "धाराएं मिलीं",
    page: "पृष्ठ",
    of: "का",

    browseJudgments: "फैसले ब्राउज़ करें",
    browseByCourtCategory: "न्यायालय और श्रेणी द्वारा",
    courtJudgmentsDatabase: "न्यायालय के फैसलों का डेटाबेस",
    judgmentsBrowseTitle: "न्यायालय के फैसले ब्राउज़ करें",
    judgmentsBrowseSubtitle:
      "सर्वोच्च न्यायालय, उच्च न्यायालय और जिला न्यायालयों के भारतीय न्यायालय फैसलों में खोज करें।",
    searchCourtJudgments: "भारतीय न्यायालय के फैसले खोजें",
    searchCourtJudgmentsSubtitle:
      "हजारों न्यायालय फैसलों में खोज करने के लिए ऊपर एक कानूनी विषय या कीवर्ड दर्ज करें।",
    noJudgmentsFound: "आपकी खोज के लिए कोई फैसले नहीं मिले।",
    tryDifferentKeywords:
      "अलग कीवर्ड आज़माएं या फ़िल्टर हटाएं।",
    showing: "दिखा रहे हैं",
    judgments: "फैसले",
    searching: "खोज रहे हैं…",
    searchJudgments: "फैसले खोजें",
    readFullJudgment: "पूरा फैसला पढ़ें",

    high: "उच्च",
    medium: "मध्यम",
    low: "निम्न",

    legalPenalty: "कानूनी जुर्माना",
    legalPunishment: "कानूनी सजा",
    viewFullLaw: "पूरा कानून देखें",
    viewOriginal: "मूल कानून पाठ देखें",
    hideOriginal: "मूल कानून पाठ छिपाएं",
    fileCase: "मामला दर्ज करें",
    filingCase: "मामला दायर करना",
    draftDocument: "दस्तावेज़ का मसौदा",
    relevance: "प्रासंगिकता",

    court: "न्यायालय",
    category: "श्रेणी",
    date: "तिथि",
    outcome: "परिणाम",
    allCourts: "सभी न्यायालय",
    allCategories: "सभी श्रेणियाँ",

    supremeCourt: "सर्वोच्च न्यायालय",
    highCourt: "उच्च न्यायालय",
    districtCourt: "जिला न्यायालय",

    criminal: "आपराधिक",
    civil: "सिविल",
    family: "पारिवारिक",
    property: "संपत्ति",
    labour: "श्रम",
    consumer: "उपभोक्ता",

    similarCases: "समान पिछले मामले",
    winsFor: "जीत",
    inCases: "में",
    totalCases: "कुल मामले",
    winRate: "जीत दर",
    petitionerWon: "याचिकाकर्ता जीता",
    respondentWon: "प्रतिवादी जीता",
    partial: "आंशिक",
    unclear: "अस्पष्ट",
    petitioner: "याचिकाकर्ता",
    respondent: "प्रतिवादी",
    whoDoesLawFavour: "कानून किसके पक्ष में है?",
    analysingOutcomes: "फैसलों के परिणामों का विश्लेषण कर रहे हैं…",
    noSimilarCases:
      "इस क्वेरी के लिए कोई समान पिछले मामले नहीं मिले।",
    couldNotLoadCases: "समान मामलों को लोड नहीं कर सके।",
    resultsFound: "परिणाम मिले",
    resultFound: "परिणाम मिला",
    detected: "पहचाना गया",
    tamilLang: "तमिल",
    hindiLang: "हिंदी",

    explanation: "स्पष्टीकरण",
    applicableLaws: "लागू कानून",
    advice: "सलाह",
    aiSummaryTitle: "AI कानूनी सारांश",

    nextPage: "अगला →",
    prevPage: "← पिछला",
    previous: "पिछला",
    next: "अगला",

    citizenMode: "नागरिक",
    lawyerMode: "वकील",

    languageLabel: "हि",

    categoryCriminal: "आपराधिक",
    categoryCivil: "सिविल",
    categoryConsumer: "उपभोक्ता",

    examplePrompt1:
      "मेरा मकान मालिक मेरी सिक्योरिटी डिपॉजिट वापस नहीं कर रहा",
    examplePrompt2:
      "किसी ने सोशल मीडिया पर मुझे ऑनलाइन धमकी दी",
    examplePrompt3:
      "मैंने एक खराब उत्पाद खरीदा और विक्रेता रिफंड देने से मना कर रहा है",

    footerText:
      "LexIndia — हर भारतीय नागरिक के लिए AI-संचालित कानूनी पहुँच",
    disclaimer:
      "यह सामान्य कानूनी जानकारी है, कानूनी सलाह नहीं। योग्य वकील से परामर्श करें।",
    aiPoweredLegalAccess: "AI-संचालित कानूनी पहुँच",
    knowYourRights: "अपने अधिकार जानें",
    underIndianLaw: "भारतीय कानून के तहत",
  },
} as const;

export type TranslationKey = keyof (typeof translations)["english"];

/**
 * Get a translated string for a given key and language.
 * Falls back to English if the key is missing for the requested language.
 */
export function t(key: TranslationKey, lang: Language): string {
  const dict = translations[lang] || translations.english;
  return (dict as Record<string, string>)[key] || (translations.english as Record<string, string>)[key] || key;
}
