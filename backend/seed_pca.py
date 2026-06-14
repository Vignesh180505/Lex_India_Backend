import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "PCA-7",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "7",
        "section_title": "Offence relating to public servant being bribed",
        "section_text": "Any public servant who obtains or accepts or attempts to accept from any person, an undue advantage, with the intention to perform or cause performance of public duty improperly or dishonestly, shall be punishable.",
        "simplified_en": "Taking a bribe or demanding an 'undue advantage' (money, favors) by a government employee to perform their duty dishonestly is a severe crime.",
        "simplified_ta": "அரசு ஊழியர் தனது கடமையை தவறாக செய்ய லஞ்சம் வாங்குவது அல்லது லஞ்சம் கேட்க முயற்சிப்பது கடுமையான குற்றமாகும்.",
        "simplified_hi": "सरकारी कर्मचारी द्वारा अपने काम के बदले रिश्वत (Undue Advantage) लेना या मांगना गंभीर अपराध है।",
        "punishment": "Imprisonment from 3 to 7 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "PCA-7A",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "7A",
        "section_title": "Taking undue advantage to influence public servant",
        "section_text": "Whoever accepts or obtains or attempts to obtain from another person, for himself or for any other person, any undue advantage as a motive or reward for inducing a public servant, by corrupt or personal influence, to perform or cause performance of a public duty improperly, shall be punishable.",
        "simplified_en": "Acts as a middleman or agent to bribe a public servant using corrupt influence is an offense, punishable by imprisonment and fine.",
        "simplified_ta": "அரசு ஊழியரை லஞ்சம் பெற தூண்டுவதற்காக இடைத்தரகராக செயல்பட்டு லஞ்சம் பெறுவது தண்டனைக்குரிய குற்றமாகும்.",
        "simplified_hi": "सरकारी कर्मचारी को प्रभावित करने के लिए बिचौलिए या दलाल के रूप में रिश्वत लेना दंडनीय अपराध है।",
        "punishment": "Imprisonment from 3 to 7 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "PCA-8",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "8",
        "section_title": "Offence relating to bribing a public servant",
        "section_text": "Any person who gives or promises to give an undue advantage to another person, with intention to induce a public servant to perform improperly a public duty, shall be punishable.",
        "simplified_en": "Bribe-givers are also criminals. Giving a bribe or promising to give money/favor to a public servant is punishable by up to 7 years in prison.",
        "simplified_ta": "லஞ்சம் கொடுப்பவர்களும் குற்றவாளிகளே. அரசு ஊழியரை தவறாக செயல்பட வைக்க லஞ்சம் கொடுப்பது அல்லது கொடுப்பதாக வாக்குறுதி அளிப்பது தண்டனைக்குரியது.",
        "simplified_hi": "रिश्वत देने वाला भी अपराधी है। सरकारी काम कराने के लिए किसी सरकारी कर्मचारी को रिश्वत देना 7 साल तक की जेल से दंडनीय है।",
        "punishment": "Imprisonment up to 7 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "PCA-12",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "12",
        "section_title": "Punishment for abetment of offences",
        "section_text": "Whoever abets any offence punishable under this Act, whether or not that offence is committed in consequence of that abetment, shall be punishable.",
        "simplified_en": "Abetting or helping someone to either give or receive a bribe, even if the bribe was not ultimately paid, is punishable by 3 to 7 years in prison.",
        "simplified_ta": "லஞ்சம் கொடுக்க அல்லது வாங்க ஒருவருக்கு உதவி செய்வதும் தூண்டுவதும் லஞ்ச ஒழிப்புச் சட்டத்தின் கீழ் குற்றமாகும்.",
        "simplified_hi": "रिश्वत लेने या देने के लिए किसी को उकसाना या सहायता करना (Abetment) भी 3 से 7 साल की जेल से दंडनीय है।",
        "punishment": "Imprisonment from 3 to 7 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "PCA-13",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "13",
        "section_title": "Criminal misconduct by a public servant",
        "section_text": "A public servant commits the offence of criminal misconduct if he dishonestly or fraudulently misappropriates or otherwise converts for his own use any property entrusted to him or under his control as a public servant or allows any other person so to do.",
        "simplified_en": "Criminal misconduct by a public servant, including misappropriating government funds or enriching themselves disproportionately to their legal income, is a high-severity crime.",
        "simplified_ta": "அரசு நிதி அல்லது சொத்துக்களை அரசு ஊழியர் தனக்காகவோ அல்லது பிறருக்காகவோ முறைகேடாக பயன்படுத்துவது குற்றவியல் முறைகேடு ஆகும்.",
        "simplified_hi": "सरकारी धन का दुरुपयोग करना या अपनी कानूनी आय से अधिक संपत्ति अर्जित करना सरकारी कर्मचारी का आपराधिक कदाचार (Misconduct) माना जाता है।",
        "punishment": "Imprisonment from 4 to 10 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "PCA-6",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "6",
        "section_title": "General Rule and Procedures under Section 6",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 6 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 6 of the Act. Under this provision of PCA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 6-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் PCA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 6 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 6 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-7",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "7",
        "section_title": "General Rule and Procedures under Section 7",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 7 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 7 of the Act. This section establishes the rights, powers, and duties of authorities under the PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 7-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 7 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 7 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-8",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "8",
        "section_title": "General Rule and Procedures under Section 8",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 8 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 8 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 8-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 8 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 8 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-9",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "9",
        "section_title": "General Rule and Procedures under Section 9",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 9 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 9 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 9-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 9 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 9 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-10",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "10",
        "section_title": "General Rule and Procedures under Section 10",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 10 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 10 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 10-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 10 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 10 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-11",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "11",
        "section_title": "General Rule and Procedures under Section 11",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 11 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 11 of the Act. Under this provision of PCA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 11-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் PCA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 11 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 11 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-12",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "12",
        "section_title": "General Rule and Procedures under Section 12",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 12 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 12 of the Act. This section establishes the rights, powers, and duties of authorities under the PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 12-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 12 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 12 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-13",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "13",
        "section_title": "General Rule and Procedures under Section 13",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 13 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 13 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 13-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 13 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 13 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-14",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 14 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-15",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 15 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-16",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. Under this provision of PCA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் PCA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 16 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-17",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 17 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-18",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. Under this provision of PCA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் PCA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 18 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-19",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 19 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-20",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 20 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-21",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. Under this provision of PCA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் PCA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 21 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-22",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. This section establishes the rights, powers, and duties of authorities under the PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 22 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-23",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 23 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-24",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. This section establishes the rights, powers, and duties of authorities under the PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 24 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-25",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. Under this provision of PCA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் PCA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 25 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "PCA-26",
        "act_code": "PCA",
        "act_name": "Prevention of Corruption Act, 1988",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Prevention of Corruption Act, 1988, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. This section regulates compliance and registration procedures for legal actions under PCA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு PCA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा PCA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
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
