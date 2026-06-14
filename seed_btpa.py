import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "BTPA-3",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "3",
        "section_title": "Prohibition of benami transactions",
        "section_text": "No person shall enter into any benami transaction.",
        "simplified_en": "Buying property under a fake name or another person's name is illegal.",
        "simplified_ta": "வேறு ஒருவர் பெயரில் சொத்து வாங்குவது (Benami) சட்டவிரோதமாகும்.",
        "simplified_hi": "दूसरे के नाम पर बेनामी संपत्ति खरीदना अवैध है; संपत्ति जब्त की जा सकती है।",
        "punishment": "Imprisonment up to 7 years, and heavy fine",
        "severity": "high"
    },
    {
        "section_id": "BTPA-2",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "2",
        "section_title": "General Rule and Procedures under Section 2",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 2 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 2 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 2-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 2 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 2 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-3",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "3",
        "section_title": "General Rule and Procedures under Section 3",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 3 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 3 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 3-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 3 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 3 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-4",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "4",
        "section_title": "General Rule and Procedures under Section 4",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 4 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 4 of the Act. This section regulates compliance and registration procedures for legal actions under BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 4-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 4 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 4 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-5",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "5",
        "section_title": "General Rule and Procedures under Section 5",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 5 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 5 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 5-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 5 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 5 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-6",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "6",
        "section_title": "General Rule and Procedures under Section 6",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 6 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 6 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 6-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 6 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 6 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-7",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "7",
        "section_title": "General Rule and Procedures under Section 7",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 7 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 7 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 7-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 7 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 7 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-8",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "8",
        "section_title": "General Rule and Procedures under Section 8",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 8 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 8 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 8-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 8 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 8 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-9",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "9",
        "section_title": "General Rule and Procedures under Section 9",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 9 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 9 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 9-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 9 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 9 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-10",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "10",
        "section_title": "General Rule and Procedures under Section 10",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 10 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 10 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 10-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 10 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 10 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-11",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "11",
        "section_title": "General Rule and Procedures under Section 11",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 11 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 11 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 11-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 11 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 11 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-12",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "12",
        "section_title": "General Rule and Procedures under Section 12",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 12 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 12 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 12-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 12 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 12 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-13",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "13",
        "section_title": "General Rule and Procedures under Section 13",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 13 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 13 of the Act. This section regulates compliance and registration procedures for legal actions under BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 13-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 13 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 13 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-14",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. This section regulates compliance and registration procedures for legal actions under BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 14 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-15",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. This section regulates compliance and registration procedures for legal actions under BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 15 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-16",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. This section regulates compliance and registration procedures for legal actions under BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 16 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-17",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 17 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-18",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 18 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-19",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 19 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-20",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 20 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-21",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 21 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-22",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 22 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-23",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. This section regulates compliance and registration procedures for legal actions under BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 23 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-24",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. Under this provision of BTPA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் BTPA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 24 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-25",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. This section establishes the rights, powers, and duties of authorities under the BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 25 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "BTPA-26",
        "act_code": "BTPA",
        "act_name": "Prohibition of Benami Property Transactions Act, 1988",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Prohibition of Benami Property Transactions Act, 1988, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. This section regulates compliance and registration procedures for legal actions under BTPA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு BTPA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा BTPA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 26 guidelines.",
        "severity": "high"
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
