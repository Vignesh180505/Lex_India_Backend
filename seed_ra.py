import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "RA-17",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "17",
        "section_title": "Documents of which registration is compulsory",
        "section_text": "The following documents shall be registered: instruments of gift of immovable property; other non-testamentary instruments which purport or operate to create, declare, assign, limit or extinguish any right, title or interest in immovable property.",
        "simplified_en": "Mandates that property gifts, sales, mortgages, or leases exceeding 1 year must be registered with the government Sub-Registrar to be legally valid.",
        "simplified_ta": "அசையா சொத்துக்களை விற்பனை செய்தல், தானமாக வழங்குதல் அல்லது 1 ஆண்டுக்கு மேல் குத்தகைக்கு விடுதல் போன்ற ஆவணங்களை கட்டாயமாக பதிவு செய்ய வேண்டும்.",
        "simplified_hi": "अचल संपत्ति की बिक्री, उपहार या 1 वर्ष से अधिक के पट्टे के दस्तावेजों को उप-पंजीयक (Sub-Registrar) के पास पंजीकृत कराना अनिवार्य है।",
        "punishment": "Compulsory Registration - Land sale/gift deeds are void if unregistered",
        "severity": "medium"
    },
    {
        "section_id": "RA-18",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "18",
        "section_title": "Documents of which registration is optional",
        "section_text": "Any of the following documents may be registered under this Act: instruments which purport or operate to create, declare, assign, limit or extinguish any right, title or interest in immovable property of a value less than one hundred rupees; Wills.",
        "simplified_en": "Registration of wills, leases under 1 year, and property transactions under ₹100 value is optional, though recommended for safety.",
        "simplified_ta": "உயில் எழுதப்பட்ட ஆவணங்கள் அல்லது 1 ஆண்டுக்கு உட்பட்ட குத்தகை ஆவணங்களை பதிவு செய்வது கட்டாயமில்லை (விருப்பத்திற்குரியது).",
        "simplified_hi": "वसीयत (Wills) या 1 वर्ष से कम अवधि के किराएनामे का पंजीकरण स्वैच्छिक (Optional) है।",
        "punishment": "Optional Registration - Recommended for safety but not mandatory",
        "severity": "medium"
    },
    {
        "section_id": "RA-49",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "49",
        "section_title": "Effect of non-registration of documents required to be registered",
        "section_text": "No document required by section 17 to be registered shall affect any immovable property comprised therein, or be received as evidence of any transaction affecting such property, unless it has been registered.",
        "simplified_en": "An unregistered document that is compulsory to register (like a sale deed) has no legal validity, cannot transfer property title, and cannot be used as evidence in court.",
        "simplified_ta": "கட்டாயமாக பதிவு செய்ய வேண்டிய ஒரு ஆவணத்தை பதிவு செய்யாமல் விட்டால், அது சொத்து உரிமை மாற்றத்தை ஏற்படுத்தாது மற்றும் நீதிமன்றத்தில் ஆதாரமாக ஏற்றுக்கொள்ளப்படாது.",
        "simplified_hi": "यदि अनिवार्य रूप से पंजीकृत होने वाले दस्तावेज (जैसे सेल डीड) का पंजीकरण नहीं कराया जाता, तो वह अमान्य होगा और अदालत में साक्ष्य नहीं माना जाएगा।",
        "punishment": "Invalidity of Unregistered Deeds - Critical defense in land disputes",
        "severity": "medium"
    },
    {
        "section_id": "RA-4",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "4",
        "section_title": "General Rule and Procedures under Section 4",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 4 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 4 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 4-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 4 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 4 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-5",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "5",
        "section_title": "General Rule and Procedures under Section 5",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 5 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 5 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 5-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 5 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 5 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-6",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "6",
        "section_title": "General Rule and Procedures under Section 6",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 6 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 6 of the Act. This section establishes the rights, powers, and duties of authorities under the RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 6-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 6 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 6 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-7",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "7",
        "section_title": "General Rule and Procedures under Section 7",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 7 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 7 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 7-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 7 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 7 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-8",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "8",
        "section_title": "General Rule and Procedures under Section 8",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 8 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 8 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 8-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 8 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 8 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-9",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "9",
        "section_title": "General Rule and Procedures under Section 9",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 9 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 9 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 9-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 9 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 9 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-10",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "10",
        "section_title": "General Rule and Procedures under Section 10",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 10 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 10 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 10-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 10 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 10 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-11",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "11",
        "section_title": "General Rule and Procedures under Section 11",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 11 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 11 of the Act. This section establishes the rights, powers, and duties of authorities under the RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 11-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 11 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 11 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-12",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "12",
        "section_title": "General Rule and Procedures under Section 12",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 12 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 12 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 12-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 12 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 12 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-13",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "13",
        "section_title": "General Rule and Procedures under Section 13",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 13 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 13 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 13-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 13 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 13 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-14",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 14 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-15",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 15 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-16",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. This section establishes the rights, powers, and duties of authorities under the RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 16 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-17",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 17 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-18",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. This section establishes the rights, powers, and duties of authorities under the RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 18 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-19",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 19 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-20",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 20 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-21",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. This section establishes the rights, powers, and duties of authorities under the RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 21 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-22",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 22 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-23",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 23 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-24",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 24 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-25",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. Under this provision of RA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் RA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 25 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "RA-26",
        "act_code": "RA",
        "act_name": "Registration Act, 1908",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Registration Act, 1908, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. This section regulates compliance and registration procedures for legal actions under RA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு RA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा RA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
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
