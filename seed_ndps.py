import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "NDPS-8",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "8",
        "section_title": "Prohibition of certain operations",
        "section_text": "No person shall cultivate any coca plant, opium poppy or any cannabis plant; or produce, manufacture, possess, sell, purchase, transport, warehouse, use, consume, import inter-State, export inter-State, import into India, export from India or tranship any narcotic drug or psychotropic substance.",
        "simplified_en": "Prohibits the cultivation, production, possession, sale, transport, purchase, or consumption of illegal drugs (like marijuana, heroin, cocaine, meth) without government license.",
        "simplified_ta": "அரசின் உரிமமின்றி கஞ்சா, அபின் போன்ற போதைப்பொருள் செடிகளை வளர்ப்பது, போதைப்பொருட்களை வைத்திருப்பது, விற்பது அல்லது உட்கொள்வது சட்டவிரோதமாகும்.",
        "simplified_hi": "बिना लाइसेंस के गांजा, अफीम जैसी नशीली दवाओं की खेती करना, उन्हें पास में रखना, बेचना, परिवहन करना या सेवन करना पूरी तरह से प्रतिबंधित है।",
        "punishment": "Imprisonment and heavy fines depending on quantity (small vs commercial)",
        "severity": "high"
    },
    {
        "section_id": "NDPS-20",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "20",
        "section_title": "Punishment for contravention in relation to cannabis plant",
        "section_text": "Whoever, in contravention of any provision of this Act or any rule or order made or condition of licence granted thereunder: cultivates any cannabis plant; or produces, manufactures, possesses, sells, purchases, transports, imports inter-State, exports inter-State or uses cannabis, shall be punished.",
        "simplified_en": "Possession of cannabis (ganja/charas) is heavily punished. Small quantities attract up to 1 year jail; commercial quantities can lead to 10-20 years in prison.",
        "simplified_ta": "கஞ்சா செடி வளர்ப்பது அல்லது கஞ்சா வைத்திருப்பது கடுமையாக தண்டிக்கப்படும். வணிக அளவிலான போதைப்பொருள் கடத்தலுக்கு 20 ஆண்டுகள் வரை சிறை.",
        "simplified_hi": "गांजे की खेती या कब्जा भारी सजा का पात्र है। व्यावसायिक मात्रा (Commercial Quantity) होने पर 10 से 20 साल तक की जेल हो सकती है।",
        "punishment": "Small quantity: Up to 1 year jail + ₹10,000 fine; Commercial: 10 to 20 years jail + ₹1-2 Lakh fine",
        "severity": "high"
    },
    {
        "section_id": "NDPS-27",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "27",
        "section_title": "Punishment for consumption of any narcotic drug",
        "section_text": "Whoever consumes any narcotic drug or psychotropic substance shall be punished with rigorous imprisonment for a term which may extend to one year, or with fine which may extend to twenty thousand rupees, or with both.",
        "simplified_en": "Consuming drugs like cocaine, heroin, or MDMA is an offense carrying up to 1 year in prison or up to a ₹20,000 fine.",
        "simplified_ta": "ஹெராயின், கோகோயின் போன்ற போதைப்பொருட்களை உட்கொள்வது 1 ஆண்டு வரை சிறைத்தண்டனை அல்லது ₹20,000 வரை அபராதம் விதிக்கக்கூடிய குற்றமாகும்.",
        "simplified_hi": "कोकीन या हेरोइन जैसे नशीले पदार्थों का सेवन करना 1 साल तक की जेल या ₹20,000 तक के जुर्माने से दंडनीय है।",
        "punishment": "Rigorous imprisonment up to 1 year, or fine up to ₹20,000, or both",
        "severity": "high"
    },
    {
        "section_id": "NDPS-37",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "37",
        "section_title": "Offences to be cognizable and non-bailable",
        "section_text": "Notwithstanding anything contained in the Code of Criminal Procedure, 1973, every offence punishable under this Act shall be cognizable; and no person accused of an offence shall be released on bail unless the court is satisfied that there are reasonable grounds for believing that he is not guilty.",
        "simplified_en": "All NDPS offenses are cognizable (police can arrest without warrant) and non-bailable. Getting bail is extremely difficult, especially for commercial quantities.",
        "simplified_ta": "போதைப்பொருள் சட்டத்தின் கீழ் வரும் அனைத்து குற்றங்களும் ஜாமீனில் வெளிவர முடியாதவை. நீதிமன்றம் குற்றமற்றவர் என்று நம்பினால் ஒழிய ஜாமீன் கிடைக்காது.",
        "simplified_hi": "एनडीपीएस के सभी अपराध गैर-जमानती हैं। आरोपी को जमानत मिलना बेहद कठिन है, विशेषकर जब मात्रा व्यावसायिक हो।",
        "punishment": "Procedural - Restricts bail eligibility and mandates arrest",
        "severity": "high"
    },
    {
        "section_id": "NDPS-50",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "50",
        "section_title": "Conditions under which search of persons shall be conducted",
        "section_text": "When any officer duly authorised under section 42 is about to search any person under the provisions of section 41, section 42 or section 43, he shall, if such person so requires, take such person without unnecessary delay to the nearest Gazetted Officer of any of the departments mentioned in section 42 or to the nearest Magistrate.",
        "simplified_en": "A suspect has a right to be searched only in the presence of a Gazetted Officer or a Magistrate. Searching officers must inform the suspect of this right.",
        "simplified_ta": "கைது செய்யப்படும் நபர் ஒரு அரசிதழ் பதிவு பெற்ற அதிகாரி (Gazetted Officer) அல்லது மேஜிஸ்திரேட் முன்னிலையில் மட்டுமே சோதனையிடக் கோர அவருக்கு உரிமை உண்டு.",
        "simplified_hi": "संदिग्ध को केवल राजपत्रित अधिकारी (Gazetted Officer) या मजिस्ट्रेट की उपस्थिति में ही तलाशी लेने का अधिकार है। पुलिस को उसे इस अधिकार की जानकारी देनी होगी।",
        "punishment": "Procedural Safeguard - Search without informing makes recovery inadmissible",
        "severity": "high"
    },
    {
        "section_id": "NDPS-6",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "6",
        "section_title": "General Rule and Procedures under Section 6",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 6 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 6 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 6-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 6 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 6 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-7",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "7",
        "section_title": "General Rule and Procedures under Section 7",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 7 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 7 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 7-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 7 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 7 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-8",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "8",
        "section_title": "General Rule and Procedures under Section 8",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 8 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 8 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 8-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 8 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 8 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-9",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "9",
        "section_title": "General Rule and Procedures under Section 9",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 9 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 9 of the Act. Under this provision of NDPS, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 9-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் NDPS-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 9 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 9 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-10",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "10",
        "section_title": "General Rule and Procedures under Section 10",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 10 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 10 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 10-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 10 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 10 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-11",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "11",
        "section_title": "General Rule and Procedures under Section 11",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 11 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 11 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 11-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 11 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 11 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-12",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "12",
        "section_title": "General Rule and Procedures under Section 12",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 12 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 12 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 12-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 12 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 12 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-13",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "13",
        "section_title": "General Rule and Procedures under Section 13",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 13 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 13 of the Act. This section establishes the rights, powers, and duties of authorities under the NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 13-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 13 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 13 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-14",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 14 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-15",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. This section establishes the rights, powers, and duties of authorities under the NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 15 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-16",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. Under this provision of NDPS, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் NDPS-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 16 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-17",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 17 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-18",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. Under this provision of NDPS, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் NDPS-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 18 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-19",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 19 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-20",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. Under this provision of NDPS, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் NDPS-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 20 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-21",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 21 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-22",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 22 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-23",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 23 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-24",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. This section establishes the rights, powers, and duties of authorities under the NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 24 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-25",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. This section regulates compliance and registration procedures for legal actions under NDPS.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு NDPS-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा NDPS के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 25 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "NDPS-26",
        "act_code": "NDPS",
        "act_name": "Narcotic Drugs and Psychotropic Substances Act, 1985",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Narcotic Drugs and Psychotropic Substances Act, 1985, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. Under this provision of NDPS, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் NDPS-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
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
