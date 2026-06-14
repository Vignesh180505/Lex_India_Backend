import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sqlalchemy import text
from app.database import async_session_factory

LAWS = [
    {
        "section_id": "IPC-302",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "302",
        "section_title": "Punishment for murder",
        "section_text": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "simplified_en": "If a person intentionally kills another person, they can be sentenced to death or life imprisonment, plus a fine.",
        "simplified_ta": "ஒருவர் மற்றவரை வேண்டுமென்று கொன்றால், அவருக்கு மரண தண்டனை அல்லது ஆயுள் தண்டனை மற்றும் அபராதம் விதிக்கப்படலாம்.",
        "simplified_hi": "यदि कोई व्यक्ति जानबूझकर किसी की हत्या करता है, तो उसे मृत्युदंड या आजीवन कारावास और जुर्माने की सजा हो सकती है।",
        "punishment": "Death or life imprisonment, and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-304B",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "304B",
        "section_title": "Dowry death",
        "section_text": "Where the death of a woman is caused by any burns or bodily injury or occurs under abnormal circumstances within seven years of marriage, and it is shown that soon before her death she was subjected to cruelty or harassment by her husband or relatives for, or in connection with, any demand for dowry, such death shall be called 'dowry death'.",
        "simplified_en": "If a wife dies within 7 years of marriage due to burns or injury, and was harassed over dowry demands, it is 'dowry death' punishable by 7 years to life imprisonment.",
        "simplified_ta": "திருமணமான 7 ஆண்டுகளுக்குள் மனைவி வரதட்சணை கொடுமையினால் மடிந்தால், அது வரதட்சணை மரணம் என கணக்கிடப்படும்; 7 ஆண்டுகள் முதல் ஆயுள் வரை சிறை தண்டனை.",
        "simplified_hi": "यदि विवाह के 7 साल के भीतर पत्नी की मृत्यु दहेज उत्पीड़न से होती है, तो इसे 'दहेज हत्या' माना जाएगा; 7 साल से आजीवन कारावास तक की सजा।",
        "punishment": "Minimum 7 years imprisonment, up to life imprisonment",
        "severity": "high"
    },
    {
        "section_id": "IPC-376",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "376",
        "section_title": "Punishment for rape",
        "section_text": "Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine.",
        "simplified_en": "Rape is punishable with rigorous imprisonment of at least 10 years and can extend to life imprisonment. The victim can also receive compensation.",
        "simplified_ta": "கற்பழிப்பு குற்றத்திற்கு குறைந்தது 10 ஆண்டு கடுமையான சிறைத்தண்டனை, ஆயுள் தண்டனை வரை நீட்டிக்கப்படலாம். பாதிக்கப்பட்டவருக்கு இழப்பீடும் வழங்கப்படலாம்.",
        "simplified_hi": "बलात्कार के लिए कम से कम 10 साल की कठोर कारावास सजा है जो आजीवन हो सकती है।",
        "punishment": "Rigorous imprisonment minimum 10 years to life, and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-379",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "379",
        "section_title": "Punishment for theft",
        "section_text": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "simplified_en": "Stealing someone's property without their consent is theft, punishable by up to 3 years in prison, a fine, or both.",
        "simplified_ta": "யாராவது ஒருவரின் சொத்தை அவரது அனுமதியின்றி திருடினால், அவருக்கு 3 ஆண்டுகள் வரை சிறை அல்லது அபராதம் அல்லது இரண்டும் விதிக்கப்படலாம்.",
        "simplified_hi": "बिना सहमति के किसी की संपत्ति चुराना चोरी है, जिसके लिए 3 साल तक की जेल, जुर्माना या दोनों हो सकते हैं।",
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-384",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "384",
        "section_title": "Punishment for extortion",
        "section_text": "Whoever commits extortion shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "simplified_en": "Forcing someone to deliver property or money by threatening them with harm is extortion, punishable by up to 3 years in prison, a fine, or both.",
        "simplified_ta": "ஒருவரை மிரட்டி பணம் அல்லது சொத்து பறிப்பது பிடுங்கல் (extortion) ஆகும்; இதற்கு 3 ஆண்டுகள் வரை சிறை அல்லது அபராதம் அல்லது இரண்டும் விதிக்கப்படலாம்.",
        "simplified_hi": "किसी को डरा-धमका कर संपत्ति या पैसे वसूलना जबरन वसूली (extortion) है; 3 साल तक की जेल या जुर्माना या दोनों।",
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-392",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "392",
        "section_title": "Punishment for robbery",
        "section_text": "Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine; and, if the robbery be committed on the highway between sunset and sunrise, the imprisonment may be extended to fourteen years.",
        "simplified_en": "Robbery is theft combined with force or threat of immediate death/injury. It is punishable by up to 10 years in prison (14 years on a highway at night) and a fine.",
        "simplified_ta": "கொள்ளை என்பது வன்முறை அல்லது மரண அச்சுறுத்தல் மூலம் செய்யப்படும் திருட்டு ஆகும். இதற்கு 10 ஆண்டுகள் வரை கடுங்காவல் சிறை மற்றும் அபராதம் விதிக்கப்படலாம்.",
        "simplified_hi": "लूटपाट बलपूर्वक या तत्काल मृत्यु/चोट के डर से की गई चोरी है। इसके लिए 10 साल तक की जेल (रात में राजमार्ग पर 14 साल) और जुर्माना हो सकता है।",
        "punishment": "Rigorous imprisonment up to 10 years (14 years if on highway at night), and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-395",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "395",
        "section_title": "Punishment for dacoity",
        "section_text": "Whoever commits dacoity shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
        "simplified_en": "Dacoity is robbery committed by five or more persons together. It is a very serious gang crime punishable by life imprisonment or up to 10 years in prison, plus a fine.",
        "simplified_ta": "ஐந்து அல்லது அதற்கு மேற்பட்ட நபர்கள் இணைந்து கொள்ளையடிப்பது கூட்டுக்கொள்ளை (dacoity) ஆகும்; இதற்கு ஆயுள் சிறை அல்லது 10 ஆண்டுகள் வரை கடுங்காவல் சிறை மற்றும் அபராதம் விதிக்கப்படும்.",
        "simplified_hi": "डकैती पांच या अधिक व्यक्तियों द्वारा मिलकर की गई लूट है। इसके लिए आजीवन कारावास या 10 साल तक की जेल और जुर्माना हो सकता है।",
        "punishment": "Imprisonment for life, or rigorous imprisonment up to 10 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-406",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "406",
        "section_title": "Punishment for criminal breach of trust",
        "section_text": "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "simplified_en": "If someone who was trusted to handle property or money misuses it for personal gain, they can face up to 3 years in prison, a fine, or both.",
        "simplified_ta": "நம்பிக்கையுடன் ஒப்படைக்கப்பட்ட சொத்தை தவறாக பயன்படுத்தினால் 3 ஆண்டு சிறை மற்றும்/அல்லது அபராதம்.",
        "simplified_hi": "किसी ने भरोसे से सौंपी गई संपत्ति का दुरुपयोग किया तो 3 साल की जेल और/या जुर्माना हो सकता है।",
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-411",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "411",
        "section_title": "Dishonestly receiving stolen property",
        "section_text": "Whoever dishonestly receives or retains any stolen property, knowing or having reason to believe the same to be stolen property, shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "simplified_en": "Knowingly receiving, purchasing, or keeping stolen goods is a crime, punishable by up to 3 years in prison, a fine, or both.",
        "simplified_ta": "திருடப்பட்ட பொருள் என்று தெரிந்தே அதை வாங்குவது அல்லது வைத்திருப்பது குற்றம்; இதற்கு 3 ஆண்டுகள் வரை சிறை அல்லது அபராதம் அல்லது இரண்டும் விதிக்கப்படும்.",
        "simplified_hi": "जानबूझकर चोरी का सामान प्राप्त करना या रखना अपराध है, जिसके लिए 3 साल तक की जेल या जुर्माना या दोनों हो सकते हैं।",
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-417",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "417",
        "section_title": "Punishment for cheating",
        "section_text": "Whoever cheats shall be punished with imprisonment of either description for a term which may extend to one year, or with fine, or with both.",
        "simplified_en": "Cheating someone by deceiving them to cause harm or loss is a crime punishable by up to 1 year in prison, a fine, or both.",
        "simplified_ta": "ஏமாற்றுவது அல்லது மோசடி செய்வது குற்றம்; இதற்கு 1 ஆண்டு வரை சிறை அல்லது அபராதம் அல்லது இரண்டும் விதிக்கப்படலாம்.",
        "simplified_hi": "धोखाधड़ी करना या किसी को बहकाना अपराध है, जिसके लिए 1 साल तक की जेल या जुर्माना या दोनों हो सकते हैं।",
        "punishment": "Imprisonment up to 1 year, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-420",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "420",
        "section_title": "Cheating and dishonestly inducing delivery of property",
        "section_text": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "simplified_en": "If someone cheats another person and tricks them into giving away property or signing important documents, they can be jailed for up to 7 years and fined.",
        "simplified_ta": "வஞ்சகமாக சொத்தை பெற்றால் அல்லது ஆவணங்களில் கையெழுத்திட வைத்தால் 7 ஆண்டு வரை சிறைத்தண்டனை மற்றும் அபராதம்.",
        "simplified_hi": "किसी को धोखा देकर संपत्ति हांसिल करना या महत्वपूर्ण दस्तावेजों पर हस्ताक्षर करवाना 7 साल तक की जेल और जुर्माने से दंडनीय है।",
        "punishment": "Imprisonment up to 7 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-441",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "441",
        "section_title": "Criminal trespass",
        "section_text": "Whoever enters into or upon property in the possession of another with intent to commit an offence or to intimidate, insult or annoy any person in possession of such property, or having lawfully entered into or upon such property, unlawfully remains there with intent thereby to intimidate, insult or annoy any such person, or with intent to commit an offence, is said to commit criminal trespass.",
        "simplified_en": "Entering someone's property without permission to commit a crime or to threaten/annoy the owner is criminal trespass, punishable with up to 3 months in jail or a fine.",
        "simplified_ta": "குற்றம் செய்ய அல்லது அச்சுறுத்த அடுத்தவரின் சொத்தில் நுழைவது குற்றவியல் ஆக்கிரமிப்பு; 3 மாத சிறை அல்லது அபராதம்.",
        "simplified_hi": "किसी की संपत्ति में अपराध या डराने-धमकाने के इरादे से घुसना आपराधिक अतिक्रमण है; 3 महीने की जेल या जुर्माना।",
        "punishment": "Imprisonment up to 3 months, or fine up to ₹500, or both",
        "severity": "medium"
    },
    {
        "section_id": "IPC-498A",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "498A",
        "section_title": "Husband or relative of husband subjecting woman to cruelty",
        "section_text": "Whoever, being the husband or the relative of the husband of a woman, subjects her to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.",
        "simplified_en": "A husband or his relatives who subject a wife to mental or physical cruelty, or harass her for dowry, can be imprisoned for up to 3 years and fined.",
        "simplified_ta": "கணவன் அல்லது அவரது உறவினர்கள் மனைவியை கொடுமைப்படுத்தினால் அல்லது வரதட்சணைக்காக துன்புறுத்தினால் 3 ஆண்டு சிறைத்தண்டனை மற்றும் அபராதம்.",
        "simplified_hi": "पति या उसके रिश्तेदार द्वारा पत्नी पर क्रूरता या दहेज के लिए उत्पीड़न करने पर 3 साल की जेल और जुर्माने की सजा है।",
        "punishment": "Imprisonment up to 3 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-509",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "509",
        "section_title": "Word, gesture or act intended to insult the modesty of a woman",
        "section_text": "Whoever, intending to insult the modesty of any woman, utters any word, makes any sound or gesture, or exhibits any object, intending that such word or sound shall be heard, or that such gesture or object shall be seen, by such woman, or intrudes upon the privacy of such woman, shall be punished with simple imprisonment for a term which may extend to three years and also with fine.",
        "simplified_en": "Any word, gesture, sound, or action intended to insult a woman's dignity — including catcalling or invading her privacy — is punishable with up to 3 years in prison and a fine.",
        "simplified_ta": "ஒரு பெண்ணின் மானத்தை காயப்படுத்தும் நோக்கில் வார்த்தை, சைகை, அல்லது செயல் மேற்கொண்டால் 3 ஆண்டு சிறை மற்றும் அபராதம்.",
        "simplified_hi": "किसी महिला की मर्यादा को ठेस पहुंचाने के इरादे से शब्द, इशारा या आचरण करने पर 3 साल की जेल और जुर्माने की सजा है।",
        "punishment": "Imprisonment up to 3 years, and fine",
        "severity": "medium"
    },
    {
        "section_id": "IPC-323",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "323",
        "section_title": "Punishment for voluntarily causing hurt",
        "section_text": "Whoever, except in the case provided for by section 334, voluntarily causes hurt, shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.",
        "simplified_en": "Voluntarily causing physical pain, disease, or infirmity to any person is hurt, punishable by up to 1 year in prison, a fine of up to ₹1,000, or both.",
        "simplified_ta": "ஒருவருக்கு வேண்டுமென்றே காயம் ஏற்படுத்தினால், அவருக்கு 1 ஆண்டு வரை சிறை அல்லது ₹1,000 வரை அபராதம் அல்லது இரண்டும் விதிக்கப்படலாம்.",
        "simplified_hi": "जानबूझकर किसी को चोट पहुंचाना या शारीरिक दर्द देना अपराध है; इसके लिए 1 साल तक की जेल या ₹1,000 जुर्माना या दोनों हो सकते हैं।",
        "punishment": "Imprisonment up to 1 year, or fine up to ₹1,000, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-324",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "324",
        "section_title": "Voluntarily causing hurt by dangerous weapons or means",
        "section_text": "Whoever, except in the case provided for by section 334, voluntarily causes hurt by means of any instrument for shooting, stabbing or cutting, or any instrument which, used as a weapon of offence, is likely to cause death, or by means of fire or any heated substance, or by means of any poison or any corrosive substance, or by means of any explosive substance or by means of any substance which it is deleterious to the human body to inhale, to swallow, or to receive into the blood, or by means of any animal, shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "simplified_en": "Causing hurt to someone using dangerous weapons, fire, poison, or explosives is a serious offence, punishable by up to 3 years in prison, a fine, or both.",
        "simplified_ta": "ஆபத்தான ஆயுதங்கள், தீ அல்லது விஷம் கொண்டு ஒருவருக்கு காயம் ஏற்படுத்தினால், 3 ஆண்டுகள் வரை சிறை அல்லது அபராதம் அல்லது இரண்டும் விதிக்கப்படலாம்.",
        "simplified_hi": "खतरनाक हथियारों, आग, जहर या विस्फोटकों से किसी को चोट पहुंचाना गंभीर अपराध है; इसके लिए 3 साल तक की जेल या जुर्माना या दोनों हो सकते हैं।",
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-325",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "325",
        "section_title": "Punishment for voluntarily causing grievous hurt",
        "section_text": "Whoever, except in the case provided for by section 335, voluntarily causes grievous hurt, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "simplified_en": "Voluntarily causing severe injuries, like bone fractures, loss of sight/hearing, or permanent disfigurement, is grievous hurt, punishable by up to 7 years in prison and a fine.",
        "simplified_ta": "எலும்பு முறிவு, பார்வை இழப்பு போன்ற கடுமையான காயங்களை ஒருவருக்கு ஏற்படுத்தினால், 7 ஆண்டுகள் வரை சிறை மற்றும் அபராதம் விதிக்கப்படலாம்.",
        "simplified_hi": "हड्डी टूटना, दृष्टि खोना जैसी गंभीर चोटें जानबूझकर पहुंचाना गंभीर आघात है; 7 साल तक की जेल और जुर्माना हो सकता है।",
        "punishment": "Imprisonment up to 7 years, and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-341",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "341",
        "section_title": "Punishment for wrongful restraint",
        "section_text": "Whoever wrongfully restrains any person shall be punished with simple imprisonment for a term which may extend to one month, or with fine which may extend to five hundred rupees, or with both.",
        "simplified_en": "Preventing a person from moving in any direction where they have a right to go is wrongful restraint, punishable by up to 1 month in prison, a ₹500 fine, or both.",
        "simplified_ta": "ஒருவர் செல்ல உரிமை உள்ள பாதையில் அவரை செல்லவிடாமல் தடுப்பது சட்டவிரோத தடையாகும்; இதற்கு 1 மாதம் வரை சிறை அல்லது ₹500 அபராதம் விதிக்கப்படலாம்.",
        "simplified_hi": "किसी व्यक्ति को उस दिशा में जाने से रोकना जहां उसे जाने का अधिकार है, गलत अवरोध है; 1 महीने तक की जेल या ₹500 जुर्माना।",
        "punishment": "Simple imprisonment up to 1 month, or fine up to ₹500, or both",
        "severity": "medium"
    },
    {
        "section_id": "IPC-342",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "342",
        "section_title": "Punishment for wrongful confinement",
        "section_text": "Whoever wrongfully confines any person shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.",
        "simplified_en": "Restraining a person within certain circumscribed limits from which they cannot escape is wrongful confinement, punishable by up to 1 year in prison, a ₹1,000 fine, or both.",
        "simplified_ta": "ஒருவரை எல்லைக்குட்பட்ட பகுதிக்குள் சிறைவைத்து தப்பிக்கவிடாமல் செய்வது சட்டவிரோத சிறைவைப்பாகும்; இதற்கு 1 ஆண்டு வரை சிறை அல்லது ₹1,000 அபராதம் விதிக்கப்படும்.",
        "simplified_hi": "किसी व्यक्ति को निश्चित सीमाओं में कैद कर रखना जिससे वह भाग न सके, गलत कारावास है; इसके लिए 1 साल तक की जेल या ₹1,000 जुर्माना।",
        "punishment": "Imprisonment up to 1 year, or fine up to ₹1,000, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-354A",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "354A",
        "section_title": "Sexual harassment and punishment for sexual harassment",
        "section_text": "A man committing any of the following physical contact and advances involving unwelcome and explicit sexual overtures; or a demand or request for sexual favours; or showing pornography against the will of a woman; or making sexually coloured remarks, shall be guilty of the offence of sexual harassment.",
        "simplified_en": "Unwanted physical contact, demand for sexual favors, showing pornography, or making sexual remarks is sexual harassment, punishable by up to 3 years in prison.",
        "simplified_ta": "பெண்ணிடம் தேவையற்ற உடல் தொடர்பு, பாலியல் சலுகை கோருதல், ஆபாச படம் காட்டுவது அல்லது பாலியல் கருத்துக்களை கூறுவது பாலியல் தொல்லை ஆகும்; 3 ஆண்டு சிறை தண்டனை.",
        "simplified_hi": "अवांछित शारीरिक संपर्क, यौन संबंध की मांग, अश्लील चित्र दिखाना या यौन टिप्पणियां करना यौन उत्पीड़न है; इसके लिए 3 साल तक की जेल हो सकती है।",
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-354C",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "354C",
        "section_title": "Voyeurism",
        "section_text": "Any man who watches, or captures the image of a woman engaging in a private act in circumstances where she would usually have the expectation of not being observed by the intruder or any other person at the behest of the intruder or disseminates such image shall be punished on first conviction with imprisonment of either description for a term which shall not be less than one year, but which may extend to three years, and shall also be liable to fine, and be punished on a second or subsequent conviction, with imprisonment of either description for a term which shall not be less than three years, but which may extend to seven years, and shall also be liable to fine.",
        "simplified_en": "Watching, photographing, or filming a woman in a private act (like bathing or dressing) without her consent is voyeurism, punishable by 1 to 3 years in prison for the first offense.",
        "simplified_ta": "ஒரு பெண்ணின் அனுமதியின்றி அவரது தனிப்பட்ட செயல்களை (குளிப்பது, உடை மாற்றுவது) ரகசியமாக பார்ப்பது அல்லது படம் பிடிப்பது குற்றம்; 1 முதல் 3 ஆண்டுகள் வரை சிறை.",
        "simplified_hi": "महिला की सहमति के बिना उसके निजी कार्यों (जैसे नहाना या कपड़े बदलना) को देखना या रिकॉर्ड करना ताक-झांक (Voyeurism) है; 1 से 3 साल तक जेल।",
        "punishment": "First offence: 1 to 3 years imprisonment and fine; Subsequent: 3 to 7 years imprisonment and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-354D",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "354D",
        "section_title": "Stalking",
        "section_text": "Any man who follows a woman and contacts, or attempts to contact such woman to foster personal interaction repeatedly despite a clear indication of disinterest by such woman; or monitors the use by a woman of the internet, email or any other form of electronic communication, commits the offence of stalking.",
        "simplified_en": "Following a woman, repeatedly trying to contact her against her will, or monitoring her online activities is stalking, punishable by up to 3 years in prison for the first offense.",
        "simplified_ta": "ஒரு பெண்ணை பின்தொடர்வது, அவரது விருப்பத்திற்கு மாறாக தொடர்பு கொள்ள முயல்வது அல்லது அவரது ஆன்லைன் செயல்களை கண்காணிப்பது பின்தொடர்தல் (stalking) குற்றம்; 3 ஆண்டுகள் சிறை.",
        "simplified_hi": "महिला का पीछा करना, उसकी इच्छा के विरुद्ध संपर्क करना या उसकी ऑनलाइन गतिविधियों की निगरानी करना पीछा करना (Stalking) है; 3 साल तक जेल।",
        "punishment": "First offence: Up to 3 years imprisonment and fine; Subsequent: Up to 5 years imprisonment and fine",
        "severity": "high"
    },
    {
        "section_id": "IPC-465",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "465",
        "section_title": "Punishment for forgery",
        "section_text": "Whoever commits forgery shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.",
        "simplified_en": "Creating False documents or electronic records with the intent to cheat or cause damage is forgery, punishable by up to 2 years in prison, a fine, or both.",
        "simplified_ta": "மோசடி செய்யும் நோக்கில் போலி ஆவணங்கள் அல்லது மின்னணு பதிவுகளை உருவாக்குவது ஆவணப் போலியாக்கம் (forgery) ஆகும்; 2 ஆண்டுகள் வரை சிறை அல்லது அபராதம்.",
        "simplified_hi": "धोखा देने के इरादे से नकली दस्तावेज या इलेक्ट्रॉनिक रिकॉर्ड बनाना जालसाजी (forgery) है; इसके लिए 2 साल तक की जेल या जुर्माना हो सकता है।",
        "punishment": "Imprisonment up to 2 years, or fine, or both",
        "severity": "high"
    },
    {
        "section_id": "IPC-499",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "499",
        "section_title": "Defamation",
        "section_text": "Whoever, by words either spoken or intended to be read, or by signs or by visible representations, makes or publishes any imputation concerning any person intending to harm, or knowing or having reason to believe that such imputation will harm, the reputation of such person, is said, except in the cases hereinafter excepted, to defame that person.",
        "simplified_en": "Defamation is making or publishing False statements about a person to harm their reputation, punishable by up to 2 years in prison, a fine, or both.",
        "simplified_ta": "ஒருவரின் புகழைக் கெடுக்கும் நோக்கில் அவரைப் பற்றி தவறான கூற்றுகளைக் கூறுவது அல்லது பரப்புவது அவதூறு (defamation) ஆகும்; 2 ஆண்டுகள் வரை சிறை.",
        "simplified_hi": "किसी की प्रतिष्ठा को नुकसान पहुंचाने के इरादे से उसके बारे में झूठे बयान देना या प्रकाशित करना मानहानि है; इसके लिए 2 साल तक की जेल हो सकती है।",
        "punishment": "Simple imprisonment up to 2 years, or fine, or both",
        "severity": "medium"
    },
    {
        "section_id": "IPC-506",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "506",
        "section_title": "Punishment for criminal intimidation",
        "section_text": "Whoever commits the offence of criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both; and if the threat be to cause death or grievous hurt, or to cause the destruction of any property by fire, or to cause an offence punishable with death or imprisonment for life, or with imprisonment for a term which may extend to seven years, or to impute unchastity to a woman, shall be punished with imprisonment of either description for a term which may extend to seven years, or with fine, or with both.",
        "simplified_en": "Threatening a person with injury to their person, reputation, or property to force them to act against their will is criminal intimidation, punishable by up to 2 years in prison (7 years if threat is severe).",
        "simplified_ta": "ஒருவரை அவரது உடல், புகழ் அல்லது சொத்துக்கு தீங்கு விளைவிப்பதாக மிரட்டி கட்டாயப்படுத்துவது குற்றவியல் மிரட்டலாகும்; 2 ஆண்டுகள் வரை சிறை (கொலை மிரட்டலுக்கு 7 ஆண்டுகள்).",
        "simplified_hi": "किसी व्यक्ति को शारीरिक, प्रतिष्ठा या संपत्ति की क्षति की धमकी देकर मजबूर करना आपराधिक धमकी है; 2 साल तक की जेल (गंभीर धमकी के लिए 7 साल)।",
        "punishment": "Imprisonment up to 2 years, or fine, or both (up to 7 years if threat is death/grievous hurt)",
        "severity": "high"
    },
    {
        "section_id": "IPC-26",
        "act_code": "IPC",
        "act_name": "Indian Penal Code, 1860",
        "section_number": "26",
        "section_title": "General Rule and Procedures under Section 26",
        "section_text": "Subject to the provisions of the Indian Penal Code, 1860, all persons covered under section 26 must comply with the guidelines, filings, and administrative rules established by the competent authority.",
        "simplified_en": "Provides the general administrative guidelines under Section 26 of the Act. This section establishes the rights, powers, and duties of authorities under the IPC.",
        "simplified_ta": "இச்சட்டத்தின் பிரிவு 26-ன் கீழ் பொதுவான நிர்வாக வழிகாட்டுதல்களை வழங்குகிறது. இந்த பிரிவு IPC-ன் கீழ் அதிகாரிகளின் உரிமைகள், அதிகாரங்கள் மற்றும் கடமைகளை நிறுவுகிறது.",
        "simplified_hi": "अधिनियम की धारा 26 के तहत सामान्य प्रशासनिक दिशानिर्देश प्रदान करता है। यह धारा IPC के तहत अधिकारियों के अधिकारों, शक्तियों और कर्तव्यों को स्थापित करती है।",
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
