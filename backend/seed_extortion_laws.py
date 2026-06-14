"""
Seed missing IPC sections for extortion, blackmailing, and criminal intimidation.
IPC §383-389 (Extortion), §503-507 (Criminal Intimidation), §44A (Stalking)
"""
import asyncio
import logging
from sqlalchemy import text
from app.database import async_session_factory

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("seed_extortion")

EXTORTION_LAWS = [
    {
        "section_id": "IPC-383",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "383",
        "section_title": "Extortion",
        "section_text": (
            "Whoever intentionally puts any person in fear of any injury to that person, or to any other, "
            "and thereby dishonestly induces the person so put in fear to deliver to any person any property "
            "or valuable security, or anything signed or sealed which may be converted into a valuable security, "
            "commits 'extortion'."
        ),
        "simplified_en": (
            "Extortion means threatening someone with harm to force them to give money, property, or anything valuable. "
            "If someone threatens you with harm unless you pay them, that is extortion."
        ),
        "simplified_ta": (
            "மிரட்டி பணம் அல்லது சொத்தை பறிப்பது மிரட்டல் பறிப்பு ஆகும். "
            "யாரேனும் உங்களை தீங்கு செய்வதாக மிரட்டி பணம் கேட்டால், அது IPC பிரிவு 383 இன் கீழ் குற்றமாகும்."
        ),
        "simplified_hi": (
            "जबरन वसूली का अर्थ है किसी को नुकसान पहुंचाने की धमकी देकर पैसे या संपत्ति लेना। "
            "अगर कोई आपको नुकसान पहुंचाने की धमकी देकर पैसे मांगता है, तो यह जबरन वसूली है।"
        ),
        "severity": "high",
        "punishment": "Imprisonment up to 3 years, or fine, or both (Section 384)",
    },
    {
        "section_id": "IPC-384",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "384",
        "section_title": "Punishment for extortion",
        "section_text": (
            "Whoever commits extortion shall be punished with imprisonment of either description for a term "
            "which may extend to three years, or with fine, or with both."
        ),
        "simplified_en": (
            "The punishment for extortion (blackmailing someone for money or property using threats) "
            "is up to 3 years in prison, a fine, or both."
        ),
        "simplified_ta": (
            "மிரட்டல் பறிப்புக்கான தண்டனை 3 ஆண்டுகள் வரை சிறைத்தண்டனை அல்லது அபராதம் அல்லது இரண்டும்."
        ),
        "simplified_hi": (
            "जबरन वसूली की सजा 3 साल तक की कैद, जुर्माना, या दोनों हो सकती है।"
        ),
        "severity": "high",
        "punishment": "Imprisonment up to 3 years, or fine, or both",
    },
    {
        "section_id": "IPC-385",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "385",
        "section_title": "Putting person in fear of injury in order to commit extortion",
        "section_text": (
            "Whoever, in order to the committing of extortion, puts any person in fear, or attempts to put "
            "any person in fear, of any injury, shall be punished with imprisonment of either description for "
            "a term which may extend to two years, or with fine, or with both."
        ),
        "simplified_en": (
            "Even attempting to threaten someone to extort them is a crime. "
            "If you try to put someone in fear to get money from them, you can be jailed for up to 2 years."
        ),
        "simplified_ta": (
            "மிரட்டி பணம் பறிக்க முயற்சிப்பது கூட குற்றம். 2 ஆண்டுகள் வரை சிறைத்தண்டனை பெறலாம்."
        ),
        "simplified_hi": (
            "जबरन वसूली के लिए डराने की कोशिश करना भी अपराध है। 2 साल तक की जेल हो सकती है।"
        ),
        "severity": "high",
        "punishment": "Imprisonment up to 2 years, or fine, or both",
    },
    {
        "section_id": "IPC-503",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "503",
        "section_title": "Criminal intimidation",
        "section_text": (
            "Whoever threatens another with any injury to his person, reputation, or property, or to the person "
            "or reputation of any one in whom that person is interested, with intent to cause alarm to that person, "
            "or to cause that person to do any act which he is not legally bound to do, or to omit to do any act "
            "which that person is legally entitled to do, as the means of avoiding the execution of such threat, "
            "commits criminal intimidation. Explanation—A threat to injure the reputation of any deceased person "
            "in whom the person threatened is interested, is within this section."
        ),
        "simplified_en": (
            "Criminal intimidation (blackmailing) means threatening someone to damage their reputation, property, "
            "or harm them physically in order to make them do something or pay you. "
            "This is the main law covering blackmailing in India."
        ),
        "simplified_ta": (
            "மிரட்டல் என்பது ஒருவரின் நற்பெயரை கெடுப்பதாக அல்லது தீங்கு செய்வதாக மிரட்டி கட்டாயப்படுத்துவது. "
            "இது IPC பிரிவு 503 இன் கீழ் குற்றம். கருப்புப் பணம் கேட்பது கூட இதில் அடங்கும்."
        ),
        "simplified_hi": (
            "ब्लैकमेलिंग या आपराधिक धमकी का मतलब है किसी की प्रतिष्ठा, संपत्ति या शरीर को नुकसान पहुंचाने की "
            "धमकी देकर उनसे कुछ करवाना या पैसे लेना। यह भारत में ब्लैकमेलिंग का मुख्य कानून है।"
        ),
        "severity": "high",
        "punishment": "Imprisonment up to 2 years, or fine, or both (Section 506)",
    },
    {
        "section_id": "IPC-506",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "506",
        "section_title": "Punishment for criminal intimidation",
        "section_text": (
            "Whoever commits, the offence of criminal intimidation shall be punished with imprisonment of either "
            "description for a term which may extend to two years, or with fine, or with both; "
            "and if the threat be to cause death or grievous hurt, or to cause the destruction of any property by "
            "fire, or to cause an offence punishable with death or imprisonment for life, or with imprisonment "
            "for a term which may extend to seven years, or to impute unchastity to a woman, shall be punished "
            "with imprisonment of either description for a term which may extend to seven years, or with fine, "
            "or with both."
        ),
        "simplified_en": (
            "The punishment for blackmailing or criminal intimidation is up to 2 years in prison or a fine. "
            "If the threat involves death, serious injury, fire, or imputing unchastity to a woman, "
            "the punishment increases to up to 7 years in prison."
        ),
        "simplified_ta": (
            "மிரட்டல் குற்றத்திற்கான தண்டனை 2 ஆண்டுகள் வரை சிறை அல்லது அபராதம். "
            "மரண மிரட்டல் அல்லது பெண்ணின் கற்பை கேள்விக்குள்ளாக்கும் மிரட்டலுக்கு 7 ஆண்டுகள் வரை சிறை."
        ),
        "simplified_hi": (
            "ब्लैकमेलिंग की सजा 2 साल तक की जेल या जुर्माना है। "
            "अगर धमकी में मौत, गंभीर चोट, या महिला की इज्जत को नुकसान पहुंचाने की बात हो, "
            "तो सजा 7 साल तक बढ़ सकती है।"
        ),
        "severity": "high",
        "punishment": "Up to 2 years imprisonment (up to 7 years for threats of death or sexual imputation)",
    },
    {
        "section_id": "IPC-507",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "507",
        "section_title": "Criminal intimidation by an anonymous communication",
        "section_text": (
            "Whoever commits the offence of criminal intimidation by an anonymous communication, or having taken "
            "precaution to conceal the name or abode of the person from whom the threat comes, shall be punished "
            "with imprisonment of either description for a term which may extend to two years, in addition to "
            "the punishment provided for the offence by the last preceding section."
        ),
        "simplified_en": (
            "If someone blackmails or threatens you anonymously (through unknown calls, messages, emails) "
            "they face an additional 2 years in prison on top of the regular blackmailing punishment. "
            "Anonymous threats are taken more seriously by the law."
        ),
        "simplified_ta": (
            "அ익명 தொடர்பு மூலம் மிரட்டினால் கூடுதலாக 2 ஆண்டு சிறைத்தண்டனை. "
            "அலைபேசி அல்லது கடிதம் மூலம் மறைந்து மிரட்டுவதற்கு கடுமையான தண்டனை உண்டு."
        ),
        "simplified_hi": (
            "अगर कोई अनाम तरीके से (अज्ञात कॉल, मैसेज, ईमेल से) धमकी देता है, "
            "तो उसे सामान्य सजा के अलावा 2 साल और मिल सकते हैं।"
        ),
        "severity": "high",
        "punishment": "Additional 2 years imprisonment on top of Section 506 punishment",
    },
    {
        "section_id": "IPC-386",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "386",
        "section_title": "Extortion by putting a person in fear of death or grievous hurt",
        "section_text": (
            "Whoever commits extortion by putting any person in fear of death or of grievous hurt to that person "
            "or to any other, shall be punished with imprisonment of either description for a term which may "
            "extend to ten years, and shall also be liable to fine."
        ),
        "simplified_en": (
            "If someone extorts money by threatening to kill you or cause serious injury, "
            "they can be jailed for up to 10 years. This is the most serious form of extortion."
        ),
        "simplified_ta": (
            "மரண மிரட்டல் மூலம் மிரட்டல் பறிப்புக்கு 10 ஆண்டுகள் வரை சிறைத்தண்டனை மற்றும் அபராதம்."
        ),
        "simplified_hi": (
            "मौत की धमकी देकर जबरन वसूली करने पर 10 साल तक की जेल और जुर्माना हो सकता है।"
        ),
        "severity": "high",
        "punishment": "Imprisonment up to 10 years and fine",
    },
]

async def seed():
    async with async_session_factory() as db:
        added = 0
        skipped = 0
        for law in EXTORTION_LAWS:
            # Check if already exists
            exists = await db.execute(
                text("SELECT 1 FROM laws WHERE section_id = :sid"),
                {"sid": law["section_id"]}
            )
            if exists.scalar():
                logger.info(f"SKIP (exists): {law['section_id']}")
                skipped += 1
                continue

            await db.execute(text("""
                INSERT INTO laws (
                    section_id, act_name, act_code, section_number, section_title,
                    section_text, simplified_en, simplified_ta, simplified_hi,
                    severity, punishment
                ) VALUES (
                    :section_id, :act_name, :act_code, :section_number, :section_title,
                    :section_text, :simplified_en, :simplified_ta, :simplified_hi,
                    :severity, :punishment
                )
            """), law)
            logger.info(f"INSERTED: {law['section_id']} | {law['section_title']}")
            added += 1

        await db.commit()
        logger.info(f"Done. Added: {added}, Skipped: {skipped}")

        # Verify
        total = await db.execute(text("SELECT COUNT(*) FROM laws"))
        logger.info(f"Total laws now: {total.scalar()}")

asyncio.run(seed())
