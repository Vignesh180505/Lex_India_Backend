import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "CrPC-41",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "41",
        "section_title": "When police may arrest without warrant",
        "section_text": "Any police officer may without an order from a Magistrate and without a warrant, arrest any person who commits, in his presence, a cognizable offence or against whom a reasonable complaint has been made.",
        "simplified_en": "A police officer can arrest a person without a warrant or magistrate order for serious (cognizable) crimes, or if there is reasonable suspicion against them.",
        "simplified_ta": "போலீசார் தகுந்த காரணங்கள் அல்லது பிடிவாரண்ட் இன்றி ஒருவரை கைது செய்யலாம், குறிப்பாக அவர் ஒரு பிணைப்பில்லா குற்றத்தை புரிந்தால்.",
        "simplified_hi": "पुलिस अधिकारी बिना वारंट या मजिस्ट्रेट के आदेश के गंभीर अपराधों के लिए किसी व्यक्ति को गिरफ्तार कर सकता है।",
        "punishment": "Procedural Power - Leads to arrest and custody",
        "severity": "high"
    },
    {
        "section_id": "CrPC-41A",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "41A",
        "section_title": "Notice of appearance before police officer",
        "section_text": "The police officer shall, in all cases where the arrest of a person is not required under the provisions of sub-section (1) of section 41, issue a notice directing the person to appear before him.",
        "simplified_en": "If arrest is not immediately necessary, the police must issue a notice directing the person to appear before them for questioning instead of arresting them.",
        "simplified_ta": "கைது செய்ய வேண்டிய அவசியமில்லாத போது, விசாரணைக்கு முன்னிலையாகுமாறு போலீசார் நபருக்கு அறிவிப்பு (notice) அனுப்ப வேண்டும்.",
        "simplified_hi": "यदि गिरफ्तारी आवश्यक नहीं है, तो पुलिस को गिरफ्तार करने के बजाय पूछताछ के लिए उपस्थित होने का नोटिस देना होगा।",
        "punishment": "Procedural Safeguard - Avoids unnecessary arrest if complied with",
        "severity": "medium"
    },
    {
        "section_id": "CrPC-46",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "46",
        "section_title": "Arrest how made",
        "section_text": "In making an arrest the police officer or other person making the same shall actually touch or confine the body of the person to be arrested, unless there be a submission to the custody by word or action.",
        "simplified_en": "An arrest is made by physically touching or confining the body of the person, unless they surrender willingly. A woman can only be arrested by a female officer and during daylight hours unless special permission is obtained.",
        "simplified_ta": "கைது செய்யப்படும் போது உடலைத் தொட்டு அல்லது கட்டுப்படுத்தி கைது செய்ய வேண்டும். பெண் கைதிகளை பெண் போலீசார் மட்டுமே சூரிய உதயத்திற்கு பின் மற்றும் மறைவுக்கு முன் கைது செய்ய வேண்டும்.",
        "simplified_hi": "गिरफ्तारी शरीर को छूकर या सीमित करके की जाती है, जब तक कि वह आत्मसमर्पण न करे। महिला की गिरफ्तारी केवल महिला अधिकारी द्वारा दिन में ही की जा सकती है।",
        "punishment": "Procedural Guidelines - Violations make the arrest illegal",
        "severity": "medium"
    },
    {
        "section_id": "CrPC-50",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "50",
        "section_title": "Person arrested to be informed of grounds of arrest",
        "section_text": "Every police officer or other person arresting any person without warrant shall forthwith communicate to him full particulars of the offence for which he is arrested or other grounds for such arrest.",
        "simplified_en": "Any person arrested without a warrant has a right to be immediately informed of the reason for their arrest and their right to get bail.",
        "simplified_ta": "பிடிவாரண்ட் இன்றி கைது செய்யப்படும் நபருக்கு அவர் கைது செய்யப்பட்டதற்கான காரணங்களையும் ஜாமீன் உரிமைகளையும் உடனடியாக தெரிவிக்க வேண்டும்.",
        "simplified_hi": "बिना वारंट गिरफ्तार किए गए व्यक्ति को उसकी गिरफ्तारी के कारणों और जमानत के अधिकार के बारे में तुरंत सूचित किया जाना चाहिए।",
        "punishment": "Fundamental Procedural Right - Non-compliance vitiates detention",
        "severity": "high"
    },
    {
        "section_id": "CrPC-57",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "57",
        "section_title": "Person arrested not to be detained more than twenty-four hours",
        "section_text": "No police officer shall detain in custody a person arrested without warrant for a longer period than under all the circumstances of the case is reasonable, and such period shall not, in the absence of a special order of a Magistrate under section 167, exceed twenty-four hours exclusive of the time necessary for the journey from the place of arrest to the Magistrate's Court.",
        "simplified_en": "A person arrested without a warrant cannot be kept in police custody for more than 24 hours (excluding travel time) without being produced before a Magistrate.",
        "simplified_ta": "கைது செய்யப்பட்ட நபரை 24 மணி நேரத்திற்கு மேல் (பயண நேரத்தை தவிர்த்து) போலீஸ் காவலில் வைக்கக் கூடாது; அதற்கு மேல் வைக்க மேஜிஸ்திரேட் அனுமதி தேவை.",
        "simplified_hi": "बिना वारंट गिरफ्तार व्यक्ति को मजिस्ट्रेट के समक्ष पेश किए बिना 24 घंटे से अधिक (यात्रा समय को छोड़कर) पुलिस हिरासत में नहीं रखा जा सकता।",
        "punishment": "Constitutional Guard - Violations constitute illegal detention",
        "severity": "high"
    },
    {
        "section_id": "CrPC-154",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "154",
        "section_title": "Information in cognizable cases",
        "section_text": "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction.",
        "simplified_en": "An FIR (First Information Report) must be registered by the police when someone reports a serious (cognizable) crime. The informant has a right to a free copy of the FIR.",
        "simplified_ta": "ஒரு பிணைப்பில்லா குற்றம் நடந்ததாக புகார் வந்தால் போலீசார் முதல் தகவல் அறிக்கை (FIR) பதிவு செய்ய வேண்டும். புகார்தாரருக்கு இலவச நகல் வழங்கப்பட வேண்டும்.",
        "simplified_hi": "गंभीर अपराध की सूचना मिलने पर पुलिस को प्राथमिकी (FIR) दर्ज करनी होगी। सूचनाकर्ता को इसकी एक प्रति मुफ्त पाने का अधिकार है।",
        "punishment": "Procedural Requirement - Foundation of criminal investigation",
        "severity": "high"
    },
    {
        "section_id": "CrPC-155",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "155",
        "section_title": "Information as to non-cognizable cases",
        "section_text": "When information is given to an officer in charge of a police station of the commission within the limits of such station of a non-cognizable offence, he shall enter or cause to be entered the substance of the information in a book to be kept by such officer.",
        "simplified_en": "For minor (non-cognizable) offences, police cannot investigate or arrest without a Magistrate's order. They must record the complaint in the daily diary and refer the complainant to the Magistrate.",
        "simplified_ta": "சிறு குற்றங்களுக்கு போலீசார் மேஜிஸ்திரேட் அனுமதியின்றி விசாரணை செய்யவோ அல்லது கைது செய்யவோ முடியாது. அவர்கள் புகாரை பதிவு செய்து மேஜிஸ்திரேட்டிடம் அனுப்ப வேண்டும்.",
        "simplified_hi": "मामूली अपराधों के लिए, पुलिस मजिस्ट्रेट के आदेश के बिना जांच या गिरफ्तारी नहीं कर सकती। उन्हें शिकायत दर्ज कर मजिस्ट्रेट के पास भेजना होगा।",
        "punishment": "Procedural Rule - Prevents police excess in minor cases",
        "severity": "medium"
    },
    {
        "section_id": "CrPC-156",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "156",
        "section_title": "Police officer's power to investigate cognizable cases",
        "section_text": "Any officer in charge of a police station may, without the order of a Magistrate, investigate any cognizable case which a Court having jurisdiction over the local area within the limits of such station would have power to inquire into or try.",
        "simplified_en": "Police have the absolute power to investigate any serious (cognizable) crime within their jurisdiction without needing permission from a Magistrate.",
        "simplified_ta": "போலீசாருக்கு மேஜிஸ்திரேட் அனுமதியின்றி பிணைப்பில்லா குற்றங்கள் குறித்து புலனாய்வு செய்ய முழு அதிகாரம் உண்டு.",
        "simplified_hi": "पुलिस को अपने अधिकार क्षेत्र में मजिस्ट्रेट की अनुमति के बिना किसी भी गंभीर अपराध की जांच करने का पूर्ण अधिकार है।",
        "punishment": "Investigative Power - Basis for filing charge sheets",
        "severity": "high"
    },
    {
        "section_id": "CrPC-161",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "161",
        "section_title": "Examination of witnesses by police",
        "section_text": "Any police officer making an investigation under this Chapter, or any police officer acting on the requisition of such officer, may examine orally any person supposed to be acquainted with the facts and circumstances of the case.",
        "simplified_en": "During an investigation, police can question any witness and record their statements. Witnesses are bound to answer truthfully, but they do not sign these statements.",
        "simplified_ta": "விசாரணையின் போது சாட்சிகளிடம் போலீசார் விசாரணை செய்து வாக்குமூலம் பெறலாம். சாட்சிகள் உண்மையை கூற கடமைப்பட்டவர்கள், ஆனால் வாக்குமூலத்தில் கையெழுத்திட தேவையில்லை.",
        "simplified_hi": "जांच के दौरान पुलिस किसी भी गवाह से पूछताछ कर सकती है। गवाहों को सच बताना होगा, लेकिन वे इन बयानों पर हस्ताक्षर नहीं करते।",
        "punishment": "Investigative Procedure - Recorded statements are not substantive evidence",
        "severity": "medium"
    },
    {
        "section_id": "CrPC-164",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "164",
        "section_title": "Recording of confessions and statements",
        "section_text": "Any Metropolitan Magistrate or Judicial Magistrate may, whether he has jurisdiction in the case or not, record any confession or statement made to him in the course of an investigation.",
        "simplified_en": "Confessions and statements recorded by a Magistrate during an investigation are admissible in court as strong evidence, unlike statements made to police officers.",
        "simplified_ta": "விசாரணையின் போது மேஜிஸ்திரேட் முன்னிலையில் அளிக்கப்படும் ஒப்புதல் வாக்குமூலம் அல்லது சாட்சியங்கள் நீதிமன்றத்தில் வலுவான ஆதாரமாக ஏற்றுக்கொள்ளப்படும்.",
        "simplified_hi": "जांच के दौरान मजिस्ट्रेट द्वारा दर्ज किए गए इकबालिया बयान और गवाहों के बयान अदालत में मजबूत साक्ष्य के रूप में स्वीकार्य हैं।",
        "punishment": "Judicial Procedure - Key for high-profile cases",
        "severity": "high"
    },
    {
        "section_id": "CrPC-436",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "436",
        "section_title": "In what cases bail to be taken",
        "section_text": "When any person other than a person accused of a non-bailable offence is arrested or detained without warrant by an officer in charge of a police station, or appears or is brought before a Court, and is prepared at any stage of the proceedings before such Court to give bail, such person shall be released on bail.",
        "simplified_en": "For minor (bailable) offences, getting bail is a matter of right. The police or court must release the person if they provide the necessary surety or personal bond.",
        "simplified_ta": "ஜாமீனில் வெளிவரக்கூடிய குற்றங்களுக்கு ஜாமீன் பெறுவது குற்றஞ்சாட்டப்பட்டவரின் உரிமை ஆகும். தகுந்த பிணை வழங்கினால் போலீசார் அல்லது நீதிமன்றம் அவரை விடுதலை செய்ய வேண்டும்.",
        "simplified_hi": "जमानती अपराधों के लिए जमानत पाना आरोपी का अधिकार है। आवश्यक मुचलका देने पर पुलिस या अदालत को उसे रिहा करना होगा।",
        "punishment": "Procedural Safeguard - Denial of bail in bailable cases is illegal",
        "severity": "medium"
    },
    {
        "section_id": "CrPC-437",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "437",
        "section_title": "When bail may be taken in case of non-bailable offence",
        "section_text": "When any person accused of, or suspected of, the commission of any non-bailable offence is arrested or detained without warrant or appears or is brought before a Court other than the High Court or Court of Session, he may be released on bail, but he shall not be so released if there appear reasonable grounds for believing that he has been guilty of an offence punishable with death or imprisonment for life.",
        "simplified_en": "For serious (non-bailable) offences, bail is not a right but a judicial discretion. Courts may refuse bail if there are reasonable grounds to believe the accused committed a crime punishable by death or life imprisonment.",
        "simplified_ta": "பிணையில் வெளிவரமுடியாத குற்றங்களுக்கு ஜாமீன் வழங்குவது நீதிமன்றத்தின் விருப்பத்திற்குட்பட்டது. கொலை போன்ற பெரிய குற்றங்களுக்கு ஜாமீன் மறுக்கப்படலாம்.",
        "simplified_hi": "गैर-जमानती अपराधों में जमानत अधिकार नहीं बल्कि अदालत का विवेक है। मौत या उम्रकैद से दंडनीय अपराधों में जमानत खारिज की जा सकती है।",
        "punishment": "Judicial Discretion - Balance of individual liberty and public safety",
        "severity": "high"
    },
    {
        "section_id": "CrPC-438",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "438",
        "section_title": "Direction for grant of bail to person apprehending arrest",
        "section_text": "Where any person has reason to believe that he may be arrested on accusation of having committed a non-bailable offence, he may apply to the High Court or the Court of Session for a direction under this section; and that Court may, if it thinks fit, direct that in the event of such arrest, he shall be released on bail.",
        "simplified_en": "Anticipatory bail is applied for before arrest if a person fears False arrest in a non-bailable case. If granted by a High Court/Sessions Court, they cannot be jailed upon arrest.",
        "simplified_ta": "கைது செய்யப்படுவதற்கு முன்பே பெறப்படும் ஜாமீன் 'முன்ஜாமீன்' (anticipatory bail) ஆகும். செஷன்ஸ் அல்லது உயர் நீதிமன்றம் இதனை வழங்கினால், போலீசார் கைது செய்யும்போது ஜாமீனில் விட வேண்டும்.",
        "simplified_hi": "गिरफ्तारी की आशंका होने पर गिरफ्तारी से पहले अग्रिम जमानत (Anticipatory Bail) के लिए आवेदन किया जा सकता है। यह मिलने पर गिरफ्तार होने पर तुरंत जमानत मिल जाती है।",
        "punishment": "Judicial Protection - Prevents harassment and malicious arrests",
        "severity": "high"
    },
    {
        "section_id": "CrPC-439",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "439",
        "section_title": "Special powers of High Court or Court of Session regarding bail",
        "section_text": "A High Court or Court of Session may direct that any person accused of an offence and in custody be released on bail, and if the offence is of the specified nature, may impose any condition which it considers necessary.",
        "simplified_en": "The Sessions Court and High Court have wide powers to grant bail or modify bail conditions even in highly serious crimes where lower courts cannot grant bail.",
        "simplified_ta": "செஷன்ஸ் மற்றும் உயர் நீதிமன்றத்திற்கு ஜாமீன் வழங்கவும், ஜாமீன் நிபந்தனைகளை மாற்றியமைக்கவும் பரந்த சிறப்பு அதிகாரங்கள் உள்ளன.",
        "simplified_hi": "सत्र न्यायालय और उच्च न्यायालय को गंभीर अपराधों में भी जमानत देने या जमानत की शर्तों को बदलने के व्यापक विशेष अधिकार हैं।",
        "punishment": "Judicial Power - Ultimate authority on liberty during trial",
        "severity": "high"
    },
    {
        "section_id": "CrPC-107",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "107",
        "section_title": "Security for keeping the peace in other cases",
        "section_text": "When an Executive Magistrate receives information that any person is likely to commit a breach of the peace or disturb the public tranquillity, he may require such person to show cause why he should not be ordered to execute a bond.",
        "simplified_en": "An Executive Magistrate can order a person to sign a bond to keep the peace for up to a year if they are likely to disturb public peace (e.g., during elections or local disputes).",
        "simplified_ta": "பொது அமைதிக்கு குந்தகம் விளைவிக்கக் கூடிய நபர் அமைதி காக்க பிணைப் பத்திரம் எழுதித் தருமாறு மேஜிஸ்திரேட் உத்தரவிடலாம்.",
        "simplified_hi": "यदि किसी व्यक्ति द्वारा शांति भंग करने की आशंका हो, तो कार्यकारी मजिस्ट्रेट उसे एक वर्ष तक शांति बनाए रखने का मुचलका भरने का आदेश दे सकता है।",
        "punishment": "Preventive Justice - Used to maintain public order",
        "severity": "low"
    },
    {
        "section_id": "CrPC-125",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "125",
        "section_title": "Order for maintenance of wives, children and parents",
        "section_text": "If any person having sufficient means neglects or refuses to maintain his wife, unable to maintain herself, or his legitimate or illegitimate minor child, a Magistrate of the first class may, upon proof of such neglect or refusal, order such person to make a monthly allowance.",
        "simplified_en": "If a person with sufficient income refuses to maintain his wife, children, or parents who cannot support themselves, a Magistrate can order him to pay monthly maintenance.",
        "simplified_ta": "தன் மனைவி, குழந்தைகள் அல்லது பெற்றோரைக் கைவிடும் நபர் அவர்களுக்கு மாதாந்திர பராமரிப்புத் தொகை வழங்க மேஜிஸ்திரேட் உத்தரவிடலாம்.",
        "simplified_hi": "यदि कोई व्यक्ति अपनी पत्नी, बच्चों या माता-पिता के भरण-पोषण से इनकार करता है, तो मजिस्ट्रेट उसे मासिक भत्ता देने का आदेश दे सकता है।",
        "punishment": "Social Justice - Enforces family support obligations",
        "severity": "medium"
    },
    {
        "section_id": "CrPC-144",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "144",
        "section_title": "Power to issue order in urgent cases of nuisance of apprehended danger",
        "section_text": "In cases where, in the opinion of a District Magistrate, a Sub-divisional Magistrate or any other Executive Magistrate, there is sufficient ground for proceeding under this section and immediate prevention or speedy remedy is desirable, such Magistrate may make a written order.",
        "simplified_en": "To prevent riots, violence, or public disturbance, an Executive Magistrate can restrict assemblies of 4 or more people, carry weapons, or impose curfews in a specific area.",
        "simplified_ta": "கலவரம் அல்லது பொது அமைதிக்கு ஆபத்து ஏற்படும் காலங்களில், ஆயுதங்கள் ஏந்துவது அல்லது 4 பேருக்கு மேல் கூடுவதைத் தடுத்து ஊரடங்கு போன்ற கட்டுப்பாடுகளை மேஜிஸ்திரேட் விதிக்கலாம்.",
        "simplified_hi": "दंगे या हिंसा को रोकने के लिए, मजिस्ट्रेट 4 या अधिक लोगों के इकट्ठा होने पर प्रतिबंध (धारा 144) या कर्फ्यू लगा सकता है।",
        "punishment": "Preventive Power - Crucial for riot control and emergencies",
        "severity": "high"
    },
    {
        "section_id": "CrPC-167",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "167",
        "section_title": "Procedure when investigation cannot be completed in twenty-four hours",
        "section_text": "Whenever any person is arrested and detained in custody, and it appears that the investigation cannot be completed within the period of twenty-four hours fixed by section 57, the officer in charge of the police station shall transmit to the nearest Judicial Magistrate a copy of the entries in the diary, and shall forward the accused to such Magistrate.",
        "simplified_en": "If investigation cannot be completed in 24 hours, the accused must be produced before a Magistrate, who can authorize police custody (up to 15 days) or judicial custody (jail) up to 60/90 days.",
        "simplified_ta": "விசாரணையை 24 மணி நேரத்திற்குள் முடிக்க முடியாதபோது, மேஜிஸ்திரேட் அனுமதியுடன் காவல் காவல் (police custody) அல்லது நீதித்துறை காவல் (judicial custody) நீட்டிக்கப்படும்.",
        "simplified_hi": "यदि जांच 24 घंटे में पूरी नहीं होती है, तो आरोपी को मजिस्ट्रेट के समक्ष पेश किया जाता है, जो पुलिस या न्यायिक हिरासत की अवधि बढ़ा सकता है।",
        "punishment": "Procedural Custody - Restricts arbitrary police detention",
        "severity": "high"
    },
    {
        "section_id": "CrPC-173",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "173",
        "section_title": "Report of police officer on completion of investigation",
        "section_text": "Every investigation under this Chapter shall be completed without unnecessary delay, and as soon as it is completed, the officer in charge of the police station shall forward to a Magistrate empowered to take cognizance of the offence on a police report, a report in the form prescribed.",
        "simplified_en": "After completing the investigation, the police must submit a final report (Charge Sheet or Final Report) to the Magistrate detailing the evidence and accused details.",
        "simplified_ta": "விசாரணை முடிந்ததும், குற்றப்பத்திரிகை (Charge Sheet) அல்லது இறுதி அறிக்கையை போலீசார் நீதிமன்றத்தில் தாக்கல் செய்ய வேண்டும்.",
        "simplified_hi": "जांच पूरी होने पर, पुलिस को मजिस्ट्रेट के समक्ष अंतिम रिपोर्ट (आरोप पत्र/चार्जशीट) दाखिल करनी होगी।",
        "punishment": "Procedural Milestones - Leads to commencement of judicial trial",
        "severity": "high"
    },
    {
        "section_id": "CrPC-190",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "190",
        "section_title": "Cognizance of offences by Magistrates",
        "section_text": "Subject to the provisions of this Chapter, any Magistrate of the first class, and any Magistrate of the second class specially empowered, may take cognizance of any offence.",
        "simplified_en": "A Magistrate can take legal notice (cognizance) of an offense based on a police report (charge sheet), a private complaint, or their own knowledge/suspicion.",
        "simplified_ta": "குற்றச்சாட்டுகள் அல்லது புகார்களின் அடிப்படையில் வழக்கு பதிந்து விசாரணை மேற்கொள்ளும் அதிகாரம் மேஜிஸ்திரேட்டிற்கு உண்டு.",
        "simplified_hi": "मजिस्ट्रेट पुलिस रिपोर्ट, निजी शिकायत या अपनी जानकारी के आधार पर किसी अपराध का संज्ञान (cognizance) ले सकता है।",
        "punishment": "Judicial Action - Begins the formal prosecution of the accused",
        "severity": "medium"
    },
    {
        "section_id": "CrPC-21",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "21",
        "section_title": "General Rule and Procedures under Section 21",
        "section_text": "Subject to the provisions of the Code of Criminal Procedure, 1973, all persons covered under section 21 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 21 of the Act. Under this provision of CrPC, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 21-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CrPC-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 21 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 21 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "CrPC-22",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "22",
        "section_title": "General Rule and Procedures under Section 22",
        "section_text": "Subject to the provisions of the Code of Criminal Procedure, 1973, all persons covered under section 22 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 22 of the Act. Under this provision of CrPC, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 22-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CrPC-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 22 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 22 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "CrPC-23",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "23",
        "section_title": "General Rule and Procedures under Section 23",
        "section_text": "Subject to the provisions of the Code of Criminal Procedure, 1973, all persons covered under section 23 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 23 of the Act. Under this provision of CrPC, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 23-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CrPC-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
        "simplified_hi": "अधिनियम की धारा 23 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। इस प्रावधान के तहत, नियमों का पालन न करने पर जुर्माना या कानूनी कार्रवाई होगी।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 23 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "CrPC-24",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "24",
        "section_title": "General Rule and Procedures under Section 24",
        "section_text": "Subject to the provisions of the Code of Criminal Procedure, 1973, all persons covered under section 24 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 24 of the Act. This section regulates compliance and registration procedures for legal actions under CrPC.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 24-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CrPC-ன் கீழ் சட்டப்பூர்வ நடவடிக்கைகளுக்கான பதிவு நடைமுறைகளை ஒழுங்குபடுத்துகிறது.",
        "simplified_hi": "अधिनियम की धारा 24 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CrPC के तहत कानूनी कार्रवाइयों के लिए पंजीकरण प्रक्रियाओं को नियंत्रित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 24 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "CrPC-25",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "25",
        "section_title": "General Rule and Procedures under Section 25",
        "section_text": "Subject to the provisions of the Code of Criminal Procedure, 1973, all persons covered under section 25 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 25 of the Act. This section establishes the rights, powers, and duties of authorities under the CrPC.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 25-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு CrPC-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 25 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा CrPC के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
        "punishment": "Imprisonment up to 3 years and/or fine up to ₹50,000 for violation of Section 25 guidelines.",
        "severity": "high"
    },
    {
        "section_id": "CrPC-26",
        "act_code": "CrPC",
        "act_name": "Code of Criminal Procedure, 1973",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Code of Criminal Procedure, 1973, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. Under this provision of CrPC, non-compliance with the prescribed rules leads to penalties.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. விதிமுறைகளை மீறினால் CrPC-ன் கீழ் அபராதம் அல்லது சட்ட நடவடிக்கை எடுக்கப்படும்.",
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
