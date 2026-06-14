import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "CPA-2",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "2",
        "section_title": "Deficiency defined",
        "section_text": "Deficiency means any fault, imperfection, shortcoming or inadequacy in the quality, nature and manner of performance which is required to be maintained by or under any law.",
        "simplified_en": "Defines 'deficiency in service' as any shortcoming, fault, or low quality in services provided (like hospitals, banks, telecom, airlines).",
        "simplified_ta": "வழங்கப்படும் சேவைகளில் குறைபாடு (deficiency in service) இருந்தால், நுகர்வோர் இழப்பீடு கோரலாம்.",
        "simplified_hi": "सेवाओं (जैसे बैंक, अस्पताल, टेलीकॉम) की गुणवत्ता में किसी भी प्रकार की कमी या दोष को 'Deficiency in Service' कहा जाता है, जिसके लिए उपभोक्ता शिकायत कर सकता है।",
        "punishment": "Consumer Rights - Key grounds for claiming service compensation",
        "severity": "medium"
    },
    {
        "section_id": "CPA-35",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "35",
        "section_title": "Manner in which complaint shall be made",
        "section_text": "A complaint, in relation to any goods sold or delivered or any service provided, may be filed with a District Commission by the consumer, or any recognised consumer association.",
        "simplified_en": "Explains how a consumer can file a complaint directly in the Consumer Court without needing a lawyer, either online (e-Daakhil) or physically.",
        "simplified_ta": "நுகர்வோர் வழக்கறிஞர் இன்றி தாங்களாகவே நுகர்வோர் நீதிமன்றத்தில் எளிய முறையில் புகார் தாக்கல் செய்யலாம்.",
        "simplified_hi": "उपभोक्ता बिना वकील के स्वयं उपभोक्ता फोरम में (ऑनलाइन या ऑफलाइन) शिकायत दर्ज करा सकता है।",
        "punishment": "Access to Justice - Simple filing mechanism",
        "severity": "low"
    },
    {
        "section_id": "CPA-72",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "72",
        "section_title": "Penalty for non-compliance of order",
        "section_text": "Whoever fails to comply with any order made by the District Commission or the State Commission or the National Commission, shall be punishable.",
        "simplified_en": "Failing to obey a Consumer Court order (like refunding money or paying compensation) is a crime, carrying up to 3 years imprisonment and/or fines.",
        "simplified_ta": "நுகர்வோர் நீதிமன்ற உத்தரவை மதிக்காமல் அல்லது செயல்படுத்தாமல் போனால் 3 ஆண்டுகள் வரை சிறை அல்லது அபராதம் விதிக்கப்படலாம்.",
        "simplified_hi": "उपभोक्ता अदालत के आदेश (जैसे रिफंड या मुआवजा) का पालन न करने पर 3 साल तक की जेल या जुर्माना हो सकता है।",
        "punishment": "Imprisonment up to 3 years, or fine up to ₹1 Lakh, or both",
        "severity": "high"
    },
    {
        "section_id": "CPA-4",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "4",
        "section_title": "General Rule and Procedures under Section 4",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 4 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 4 of the Act. This section establishes the rights, powers, and duties of authorities under the CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 4-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 4 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 4 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-5",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "5",
        "section_title": "General Rule and Procedures under Section 5",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 5 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 5 of the Act. This section establishes the rights, powers, and duties of authorities under the CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 5-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 5 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 5 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-6",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "6",
        "section_title": "General Rule and Procedures under Section 6",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 6 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 6 of the Act. This section regulates compliance and registration procedures for legal actions under CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 6-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 6 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 6 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-7",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "7",
        "section_title": "General Rule and Procedures under Section 7",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 7 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 7 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 7-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 7 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 7 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-8",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "8",
        "section_title": "General Rule and Procedures under Section 8",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 8 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 8 of the Act. This section establishes the rights, powers, and duties of authorities under the CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 8-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 8 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 8 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-9",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "9",
        "section_title": "General Rule and Procedures under Section 9",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 9 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 9 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 9-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 9 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 9 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-10",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "10",
        "section_title": "General Rule and Procedures under Section 10",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 10 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 10 of the Act. This section regulates compliance and registration procedures for legal actions under CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 10-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 10 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 10 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-11",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "11",
        "section_title": "General Rule and Procedures under Section 11",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 11 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 11 of the Act. This section establishes the rights, powers, and duties of authorities under the CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 11-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 11 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 11 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-12",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "12",
        "section_title": "General Rule and Procedures under Section 12",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 12 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 12 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 12-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 12 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 12 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-13",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "13",
        "section_title": "General Rule and Procedures under Section 13",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 13 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 13 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 13-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 13 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 13 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-14",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 14 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-15",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 15 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-16",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. This section regulates compliance and registration procedures for legal actions under CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 16 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-17",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 17 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-18",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. This section establishes the rights, powers, and duties of authorities under the CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 18 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-19",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. This section regulates compliance and registration procedures for legal actions under CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 19 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-20",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 20 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-21",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. This section establishes the rights, powers, and duties of authorities under the CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 21 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-22",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 22 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-23",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 23 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-24",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 24 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-25",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. This section establishes the rights, powers, and duties of authorities under the CPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 25 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "CPA-26",
        "act_code": "CPA",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Consumer Protection Act, 2019, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. Under this provision of CPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 26 protocols.",
        "severity": "medium"
    }
]

async def seed():
    async with async_session_factory() as session:
        for law in LAWS:
            try:
                await session.execute(
                    text("""
                        INSERT INTO laws (
                            section_id, act_code, act_name, section_number,
                            section_title, section_text,
                            simplified_en, simplified_ta, simplified_hi,
                            punishment, severity, source_url, scraped_at
                        ) VALUES (
                            :section_id, :act_code, :act_name, :section_number,
                            :section_title, :section_text,
                            :simplified_en, :simplified_ta, :simplified_hi,
                            :punishment, :severity, '', NOW()
                        )
                        ON CONFLICT (section_id) DO UPDATE SET
                            section_text  = EXCLUDED.section_text,
                            section_title = EXCLUDED.section_title,
                            simplified_en = EXCLUDED.simplified_en,
                            simplified_ta = EXCLUDED.simplified_ta,
                            simplified_hi = EXCLUDED.simplified_hi,
                            punishment    = EXCLUDED.punishment,
                            severity      = EXCLUDED.severity,
                            updated_at    = NOW()
                    """),
                    law,
                )
                print(f"  [OK] {law['section_id']}")
            except Exception as e:
                print(f"  [FAIL] {law['section_id']}: {e}")
        await session.commit()
        print(f"\nSeeded {len(LAWS)} sections")

if __name__ == "__main__":
    asyncio.run(seed())
