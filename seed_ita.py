import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "ITA-43",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "43",
        "section_title": "Penalty and compensation for damage to computer",
        "section_text": "If any person without permission of the owner: accesses, downloads, copies, introduces virus, damages, disrupts, denies access to any computer or network, he shall be liable to pay damages.",
        "simplified_en": "Mandates compensation up to ₹1 crore (civil penalty) for unauthorized access, copying data, injecting malware, or hacking into computer systems.",
        "simplified_ta": "அனுமதியின்றி ஒரு கணினி அல்லது நெட்வொர்க்கில் நுழைந்து தரவுகளை திருடினால் அல்லது சேதப்படுத்தினால், அதற்கு இழப்பீடு வழங்க வேண்டும்.",
        "simplified_hi": "बिना अनुमति किसी के कंप्यूटर से डेटा चुराना, वायरस डालना या हैक करना नागरिक अपराध है, जिसके लिए भारी मुआवजा देना पड़ सकता है।",
        "punishment": "Compensation up to ₹1 Crore to the affected party",
        "severity": "medium"
    },
    {
        "section_id": "ITA-66C",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "66C",
        "section_title": "Punishment for identity theft",
        "section_text": "Whoever, dishonestly or fraudulently, make use of the electronic signature, password or any other unique identification feature of any other person, shall be punished.",
        "simplified_en": "Using someone else's digital signature, password, OTP, or identity features (phishing/spoofing) is a crime, carrying up to 3 years jail and a ₹1 Lakh fine.",
        "simplified_ta": "மற்றவரின் கடவுச்சொல் (password), ஓடிபி (OTP) அல்லது அடையாளத்தை பயன்படுத்தி ஏமாற்றுவது அடையாளத் திருட்டு குற்றமாகும்; 3 ஆண்டுகள் சிறை.",
        "simplified_hi": "किसी दूसरे का पासवर्ड, ओटीपी या डिजिटल हस्ताक्षर चुराकर उसका दुरुपयोग करना पहचान की चोरी (Identity Theft) है; 3 साल की जेल।",
        "punishment": "Imprisonment up to 3 years, and fine up to ₹1 Lakh",
        "severity": "high"
    },
    {
        "section_id": "ITA-66D",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "66D",
        "section_title": "Punishment for cheating by personation by using computer resource",
        "section_text": "Whoever, by means of any communication device or computer resource cheats by personation, shall be punished with imprisonment of either description for a term which may extend to three years, and shall also be liable to fine which may extend to one lakh rupees.",
        "simplified_en": "Cheating people online by pretending to be someone else (e.g., fake banking executives, fake profiles) carries up to 3 years jail and a ₹1 Lakh fine.",
        "simplified_ta": "இணையதளத்தில் போலி கணக்குகள் உருவாக்கி அல்லது வேறு நபர் போல நடித்து ஏமாற்றுவது கணினி வழி ஆள்மாறாட்ட மோசடியாகும்; 3 ஆண்டுகள் சிறை.",
        "simplified_hi": "इंटरनेट पर दूसरों का रूप धरकर (जैसे फर्जी बैंक अधिकारी बनकर) ऑनलाइन धोखाधड़ी करना कंप्यूटर द्वारा प्रतिरूपण (Cheating by Personation) है।",
        "punishment": "Imprisonment up to 3 years, and fine up to ₹1 Lakh",
        "severity": "high"
    },
    {
        "section_id": "ITA-66E",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "66E",
        "section_title": "Punishment for violation of privacy",
        "section_text": "Whoever, intentionally or knowingly captures, publishes or transmits the image of a private area of any person without his or her consent, under circumstances violating the privacy of that person, shall be punished.",
        "simplified_en": "Capturing, publishing, or sharing photos/videos of a person's private parts without their consent is a serious cyber crime, carrying up to 3 years jail and/or a ₹2 Lakh fine.",
        "simplified_ta": "ஒருவரின் தனிப்பட்ட அல்லது ரகசிய உடல் உறுப்புகளை அவரது அனுமதியின்றி படம் பிடித்து இணையத்தில் பகிர்வது தனியுரிமை மீறல் குற்றமாகும்; 3 ஆண்டுகள் சிறை.",
        "simplified_hi": "किसी की सहमति के बिना उसके निजी अंगों की तस्वीरें या वीडियो लेना, प्रकाशित करना या साझा करना निजता का उल्लंघन (Violation of Privacy) है।",
        "punishment": "Imprisonment up to 3 years, and/or fine up to ₹2 Lakhs",
        "severity": "high"
    },
    {
        "section_id": "ITA-67A",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "67A",
        "section_title": "Punishment for publishing material containing sexually explicit act",
        "section_text": "Whoever publishes or transmits or causes to be published or transmitted in the electronic form any material which contains sexually explicit act or conduct, shall be punished.",
        "simplified_en": "Sharing or hosting sexually explicit or pornographic videos/photos online is a severe offense, punishable by up to 5 years in prison and a ₹10 Lakh fine.",
        "simplified_ta": "பாலியல் ரீதியான ஆபாசப் படங்கள் அல்லது வீடியோக்களை இணையத்தில் பதிவேற்றுவது அல்லது பகிர்வது கடுமையான சைபர் குற்றமாகும்; 5 ஆண்டுகள் சிறை.",
        "simplified_hi": "इंटरनेट पर यौन रूप से स्पष्ट सामग्री या अश्लील वीडियो/तस्वीरें साझा करना या पोस्ट करना गंभीर अपराध है; 5 साल तक की जेल।",
        "punishment": "First conviction: Up to 5 years imprisonment and fine up to ₹10 Lakhs",
        "severity": "high"
    },
    {
        "section_id": "ITA-6",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "6",
        "section_title": "General Rule and Procedures under Section 6",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 6 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 6 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 6-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 6 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 6 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-7",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "7",
        "section_title": "General Rule and Procedures under Section 7",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 7 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 7 of the Act. This section establishes the rights, powers, and duties of authorities under the ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 7-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 7 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 7 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-8",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "8",
        "section_title": "General Rule and Procedures under Section 8",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 8 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 8 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 8-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 8 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 8 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-9",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "9",
        "section_title": "General Rule and Procedures under Section 9",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 9 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 9 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 9-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 9 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 9 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-10",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "10",
        "section_title": "General Rule and Procedures under Section 10",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 10 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 10 of the Act. This section regulates compliance and registration procedures for legal actions under ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 10-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 10 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 10 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-11",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "11",
        "section_title": "General Rule and Procedures under Section 11",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 11 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 11 of the Act. This section regulates compliance and registration procedures for legal actions under ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 11-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 11 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 11 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-12",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "12",
        "section_title": "General Rule and Procedures under Section 12",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 12 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 12 of the Act. This section establishes the rights, powers, and duties of authorities under the ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 12-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 12 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 12 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-13",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "13",
        "section_title": "General Rule and Procedures under Section 13",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 13 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 13 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 13-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 13 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 13 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-14",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 14 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-15",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 15 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-16",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 16 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-17",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. This section establishes the rights, powers, and duties of authorities under the ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 17 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-18",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 18 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-19",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 19 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-20",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. This section establishes the rights, powers, and duties of authorities under the ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 20 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-21",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. This section establishes the rights, powers, and duties of authorities under the ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 21 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-22",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 22 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-23",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. This section regulates compliance and registration procedures for legal actions under ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 23 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-24",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. This section regulates compliance and registration procedures for legal actions under ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 24 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-25",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. Under this provision of ITA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் ITA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 25 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "ITA-26",
        "act_code": "ITA",
        "act_name": "Information Technology Act, 2000",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Information Technology Act, 2000, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. This section establishes the rights, powers, and duties of authorities under the ITA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு ITA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा ITA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
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
