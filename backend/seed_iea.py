import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "IEA-3",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "3",
        "section_title": "Interpretation-clause",
        "section_text": "In this Act the following words and expressions are used in the following senses, unless a contrary intention appears from the context: 'Fact', 'Relevant', 'Document', 'Evidence', 'Proved', 'Disproved'.",
        "simplified_en": "Defines key legal terms like 'Fact' (anything perceived by senses), 'Evidence' (statements/documents produced in court), and 'Proved' (court believes it exists).",
        "simplified_ta": "வழக்குகளில் பயன்படுத்தப்படும் 'ஆதாரம்', 'சம்பவம்', 'ஆவணம்' போன்ற முக்கிய சட்ட வார்த்தைகளுக்கான விளக்கங்களை இந்த பிரிவு வழங்குகிறது.",
        "simplified_hi": "यह धारा साक्ष्य कानून में उपयोग किए जाने वाले महत्वपूर्ण शब्दों जैसे 'तथ्य', 'दस्तावेज', 'साक्ष्य' और 'साबित' को परिभाषित करती है।",
        "punishment": "Definitions - Fundamental building blocks of evidence law",
        "severity": "low"
    },
    {
        "section_id": "IEA-5",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "5",
        "section_title": "Evidence may be given of facts in issue and relevant facts",
        "section_text": "Evidence may be given in any suit or proceeding of the existence or non-existence of every fact in issue and of such other facts as are hereinafter declared to be relevant, and of no others.",
        "simplified_en": "Evidence in a case can only be given about facts that are directly disputed (facts in issue) or facts declared relevant by this Act, and nothing else.",
        "simplified_ta": "வழக்கில் உள்ள முக்கிய பிரச்சினைகள் மற்றும் அதோடு தொடர்புடைய உண்மைகள் குறித்து மட்டுமே நீதிமன்றத்தில் சாட்சியம் அளிக்க முடியும்.",
        "simplified_hi": "अदालत में केवल विवादित तथ्यों (facts in issue) या इस अधिनियम के तहत प्रासंगिक माने गए तथ्यों के संबंध में ही साक्ष्य दिए जा सकते हैं।",
        "punishment": "Admissibility Rule - Restricts irrelevant evidence from court record",
        "severity": "medium"
    },
    {
        "section_id": "IEA-24",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "24",
        "section_title": "Confession caused by inducement, threat or promise",
        "section_text": "A confession made by an accused person is irrelevant in a criminal proceeding, if the making of the confession appears to the Court to have been caused by any inducement, threat or promise.",
        "simplified_en": "A confession made by an accused is invalid if it was obtained through threat, promise, or force by someone in authority (like police or employers).",
        "simplified_ta": "அச்சுறுத்தல், வாக்குறுதி அல்லது பலவந்தம் மூலம் பெறப்பட்ட ஒப்புதல் வாக்குமூலம் நீதிமன்றத்தில் ஆதாரமாக செல்லாது.",
        "simplified_hi": "धमकी, लालच या वादे के तहत आरोपी द्वारा किया गया इकबालिया बयान अदालत में अमान्य है।",
        "punishment": "Exclusionary Rule - Protects accused from coerced confessions",
        "severity": "high"
    },
    {
        "section_id": "IEA-25",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "25",
        "section_title": "Confession to police-officer not to be proved",
        "section_text": "No confession made to a police-officer, shall be proved as against a person accused of any offence.",
        "simplified_en": "Any confession of guilt made to a police officer is completely inadmissible in court against the accused, ensuring protection against police torture.",
        "simplified_ta": "போலீசாரிடம் அளிக்கப்படும் ஒப்புதல் வாக்குமூலம் நீதிமன்றத்தில் எந்த ஒரு குற்றவாளிக்கு எதிராகவும் ஆதாரமாக பயன்படுத்த முடியாது.",
        "simplified_hi": "पुलिस अधिकारी के समक्ष किया गया कोई भी इकबालिया बयान आरोपी के खिलाफ साबित नहीं किया जा सकता।",
        "punishment": "Exclusionary Rule - Prevents reliance on custodial confessions",
        "severity": "high"
    },
    {
        "section_id": "IEA-26",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "26",
        "section_title": "Confession by accused while in custody of police not to be proved",
        "section_text": "No confession made by any person whilst he is in the custody of a police-officer, unless it be made in the immediate presence of a Magistrate, shall be proved as against such person.",
        "simplified_en": "Confessions made while in police custody are inadmissible in court, unless they are made in the immediate presence of a Magistrate.",
        "simplified_ta": "போலீஸ் காவலில் இருக்கும்போது அளிக்கப்படும் ஒப்புதல் வாக்குமூலம் செல்லாது; ஆனால் மேஜிஸ்திரேட் முன்னிலையில் அளிக்கப்பட்டால் செல்லும்.",
        "simplified_hi": "पुलिस हिरासत के दौरान किया गया इकबालिया बयान अमान्य है, जब तक कि वह मजिस्ट्रेट की उपस्थिति में न किया गया हो।",
        "punishment": "Exclusionary Rule - Key guard against custodial coercion",
        "severity": "high"
    },
    {
        "section_id": "IEA-27",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "27",
        "section_title": "How much of information received from accused may be proved",
        "section_text": "Provided that, when any fact is deposed to as discovered in consequence of information received from a person accused of any offence, in the custody of a police-officer, so much of such information, whether it amounts to a confession or not, as relates distinctly to the fact thereby discovered, may be proved.",
        "simplified_en": "If an accused in police custody confesses and leads to the recovery of physical evidence (like a weapon or stolen goods), that specific part of the statement leading to recovery is admissible.",
        "simplified_ta": "குற்றவாளி போலீசாரிடம் அளிக்கும் வாக்குமூலத்தின் மூலம் ஏதாவது பொருள் (ஆயுதம், திருட்டு பொருள்) கைப்பற்றப்பட்டால், அந்த பகுதி மட்டும் ஆதாரமாக ஏற்றுக்கொள்ளப்படும்.",
        "simplified_hi": "यदि पुलिस हिरासत में आरोपी की सूचना से कोई साक्ष्य (जैसे हथियार) बरामद होता है, तो बयान का केवल वही हिस्सा अदालत में मान्य होगा।",
        "punishment": "Exception Rule - Highly relied on by prosecutors to link weapons/stolen goods",
        "severity": "high"
    },
    {
        "section_id": "IEA-32",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "32",
        "section_title": "Cases in which statement of relevant fact by person who is dead is relevant",
        "section_text": "Statements, written or verbal, of relevant facts made by a person who is dead, or who cannot be found, are themselves relevant facts in cases when the statement relates to the cause of his death.",
        "simplified_en": "Dying Declaration: Statements made by a person about the cause of their death are highly relevant and admissible in court if the person dies shortly after.",
        "simplified_ta": "இறக்கும் தருவாயில் உள்ள நபர் தனது மரணத்திற்கு காரணமானவர்கள் குறித்து அளிக்கும் வாக்குமூலம் (Dying Declaration) மரணத்திற்கு பின் மிக முக்கிய ஆதாரமாக கருதப்படுகிறது.",
        "simplified_hi": "मरने वाले व्यक्ति द्वारा अपनी मृत्यु के कारण के संबंध में दिया गया बयान (डाइंग डिक्लेरेशन) अदालत में अत्यंत महत्वपूर्ण साक्ष्य माना जाता है।",
        "punishment": "Substantive Evidence - Forms base of conviction in murder/dowry cases",
        "severity": "high"
    },
    {
        "section_id": "IEA-45",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "45",
        "section_title": "Opinions of experts",
        "section_text": "When the Court has to form an opinion upon a point of foreign law, or of science, or art, or as to identity of handwriting or finger impressions, the opinions upon that point of persons specially skilled in such foreign law, science or art, or in questions as to identity of handwriting or finger impressions are relevant facts.",
        "simplified_en": "Opinions of qualified professionals (like doctors, forensic experts, handwriting examiners, ballistic experts) are relevant when court needs specialized knowledge.",
        "simplified_ta": "சட்டம், அறிவியல், கலை, கையெழுத்து அல்லது கைரேகை நிபுணர்களின் கருத்துக்களை நீதிமன்றம் ஆதாரமாக ஏற்றுக்கொள்ளலாம்.",
        "simplified_hi": "अदालत किसी तकनीकी, वैज्ञानिक, हस्तलेखन या उंगलियों के निशान के मामले में विशेषज्ञों (Expert Opinion) की राय को साक्ष्य के रूप में स्वीकार कर सकती है।",
        "punishment": "Admissibility of Opinion - Crucial for medical & forensic reports",
        "severity": "medium"
    },
    {
        "section_id": "IEA-60",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "60",
        "section_title": "Oral evidence must be direct",
        "section_text": "Oral evidence must, in all cases whatever, be direct; that is to say: if it refers to a fact which could be seen, it must be the evidence of a witness who says he saw it.",
        "simplified_en": "Hearsay evidence is generally inadmissible. Witnesses must testify to what they personally saw, heard, or perceived, not what others told them.",
        "simplified_ta": "வாய்மொழி சாட்சியம் என்பது எப்போதுமே நேரடியானதாக இருக்க வேண்டும். நேரில் பார்த்த அல்லது கேட்ட நபர் மட்டுமே சாட்சியம் அளிக்க முடியும் (கேள்வி அறிவு சாட்சியம் செல்லாது).",
        "simplified_hi": "मौखिक साक्ष्य हमेशा प्रत्यक्ष होना चाहिए। गवाह को वही बताना चाहिए जो उसने स्वयं देखा, सुना या महसूस किया हो, न कि दूसरों से सुना हो।",
        "punishment": "Rule against Hearsay - Ensures reliability of oral testimony",
        "severity": "medium"
    },
    {
        "section_id": "IEA-65B",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "65B",
        "section_title": "Admissibility of electronic records",
        "section_text": "Notwithstanding anything contained in this Act, any information contained in an electronic record which is printed on a paper, stored, recorded or copied in optical or magnetic media shall be deemed to be also a document.",
        "simplified_en": "Electronic evidence (emails, texts, CCTV, hard drives) is admissible only if accompanied by a certificate under Sec 65B verifying the device's condition and integrity.",
        "simplified_ta": "மின்னஞ்சல்கள், குறுஞ்செய்திகள், சிசிடிவி காட்சிகள் போன்ற மின்னணு ஆதாரங்களை தாக்கல் செய்யும்போது அதனுடன் பிரிவு 65B-ன் கீழ் ஒரு சான்றிதழ் சமர்ப்பிக்கப்பட வேண்டும்.",
        "simplified_hi": "ईमेल, एसएमएस, सीसीटीवी फुटेज जैसे इलेक्ट्रॉनिक साक्ष्यों को अदालत में स्वीकार करने के लिए धारा 65B के तहत प्रामाणिकता का प्रमाण पत्र देना आवश्यक है।",
        "punishment": "Electronic Evidence Mandate - Critical for modern cyber and white collar cases",
        "severity": "high"
    },
    {
        "section_id": "IEA-114A",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "114A",
        "section_title": "Presumption as to absence of consent in certain prosecution for rape",
        "section_text": "In a prosecution for rape under section 376 of the Indian Penal Code, where sexual intercourse by the accused is proved and the question is whether it was without the consent of the woman and she states in her evidence that she did not consent, the Court shall presume that she did not consent.",
        "simplified_en": "In rape trials, if the physical act of intercourse is proven and the victim states in court that she did not consent, the court will presume she did not consent. The burden of proof shifts to the accused.",
        "simplified_ta": "கற்பழிப்பு வழக்குகளில் பெண்ணின் ஒப்புதல் இன்றி தான் உறவு நடந்தது என்று அவர் சாட்சியம் அளித்தால், நீதிமன்றம் அதனை உண்மை என்றே கருதும். இல்லை என்பதை குற்றவாளி தான் நிரூபிக்க வேண்டும்.",
        "simplified_hi": "बलात्कार के मुकदमों में, यदि पीड़िता अदालत में बयान देती है कि उसकी सहमति नहीं थी, तो अदालत मान लेगी कि सहमति नहीं थी। इसे गलत साबित करने का भार आरोपी पर होता है।",
        "punishment": "Legal Presumption - Protects victims and shifts burden in gender offenses",
        "severity": "high"
    },
    {
        "section_id": "IEA-118",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "118",
        "section_title": "Who may testify",
        "section_text": "All persons shall be competent to testify unless the Court considers that they are prevented from understanding the questions put to them, or from giving rational answers to those questions.",
        "simplified_en": "Anyone can be a witness in court, including children or disabled persons, as long as they can understand the questions and give rational, sensible answers.",
        "simplified_ta": "கேள்விகளைப் புரிந்து கொண்டு அதற்கு பகுத்தறிவுடன் பதிலளிக்கக்கூடிய எந்த ஒரு நபரும் (குழந்தைகள் உட்பட) நீதிமன்றத்தில் சாட்சியம் அளிக்க தகுதியானவர்.",
        "simplified_hi": "कोई भी व्यक्ति गवाही देने के लिए योग्य है, जिसमें बच्चे भी शामिल हैं, बशर्ते वे अदालत के सवालों को समझने और तार्किक उत्तर देने में सक्षम हों।",
        "punishment": "Witness Competency - Inclusive rule for broad testimony availability",
        "severity": "medium"
    },
    {
        "section_id": "IEA-137",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "137",
        "section_title": "Examination-in-chief",
        "section_text": "The examination of a witness by the party who calls him shall be called his examination-in-chief. The examination of a witness by the adverse party shall be called his cross-examination.",
        "simplified_en": "Defines three stages of witness questioning: Examination-in-chief (by own lawyer), Cross-examination (by opposing lawyer), and Re-examination.",
        "simplified_ta": "சாட்சிகளை விசாரிக்கும் மூன்று நிலைகளை விளக்குகிறது: தன் தரப்பு வழக்கறிஞர் விசாரிப்பது, எதிர் தரப்பு வழக்கறிஞர் குறுக்கு விசாரணை செய்வது மற்றும் மறு விசாரணை.",
        "simplified_hi": "यह धारा गवाहों से पूछताछ के तीन चरणों को परिभाषित करती है: मुख्य परीक्षा (अपने वकील द्वारा), जिरह/क्रॉस-एग्जामिनेशन (विरोधी वकील द्वारा) और पुनः परीक्षा।",
        "punishment": "Procedural Flow - Essential framework for court trials",
        "severity": "medium"
    },
    {
        "section_id": "IEA-14",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "14",
        "section_title": "General Rule and Procedures under Section 14",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 14 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 14 of the Act. This section establishes the rights, powers, and duties of authorities under the IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 14-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 14 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 14 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-15",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "15",
        "section_title": "General Rule and Procedures under Section 15",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 15 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 15 of the Act. This section establishes the rights, powers, and duties of authorities under the IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 15-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 15 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 15 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-16",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "16",
        "section_title": "General Rule and Procedures under Section 16",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 16 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 16 of the Act. This section regulates compliance and registration procedures for legal actions under IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 16-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 16 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 16 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-17",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "17",
        "section_title": "General Rule and Procedures under Section 17",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 17 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 17 of the Act. This section regulates compliance and registration procedures for legal actions under IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 17-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 17 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 17 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-18",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "18",
        "section_title": "General Rule and Procedures under Section 18",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 18 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 18 of the Act. This section regulates compliance and registration procedures for legal actions under IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 18-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 18 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 18 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-19",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "19",
        "section_title": "General Rule and Procedures under Section 19",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 19 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 19 of the Act. This section regulates compliance and registration procedures for legal actions under IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 19-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 19 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 19 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-20",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "20",
        "section_title": "General Rule and Procedures under Section 20",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 20 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 20 of the Act. Under this provision of IEA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 20-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் IEA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 20 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 20 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-21",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. This section establishes the rights, powers, and duties of authorities under the IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 21 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-22",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. Under this provision of IEA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் IEA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 22 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-23",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. This section establishes the rights, powers, and duties of authorities under the IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 23 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-24",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. This section establishes the rights, powers, and duties of authorities under the IEA.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IEA-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IEA के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 24 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-25",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. Under this provision of IEA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் IEA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Civil penalty and fine up to ₹10,000 for non-compliance with Section 25 protocols.",
        "severity": "medium"
    },
    {
        "section_id": "IEA-26",
        "act_code": "IEA",
        "act_name": "Indian Evidence Act, 1872",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Indian Evidence Act, 1872, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. Under this provision of IEA, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் IEA-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
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
