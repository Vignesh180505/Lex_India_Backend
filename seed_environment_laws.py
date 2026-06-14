"""Seed the database with Environmental and Property Laws.

This dataset focuses on:
- Environment Protection Act, 1986
- Indian Forest Act, 1927
- Public Liability Insurance Act, 1991
- Constitutional Duties (Environment)
- General rules regarding tree felling and property rights.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.database import async_session_factory

ENVIRONMENT_LAWS = [
    # ─── Environment Protection Act, 1986 ──────────────────────────────────
    {
        "section_id": "EPA-7",
        "act_code": "EPA", "act_name": "Environment (Protection) Act, 1986",
        "section_number": "7", "section_title": "Persons carrying on industry, operation, etc., not to allow emission or discharge of environmental pollutants in excess of the standards",
        "section_text": "No person carrying on any industry, operation or process shall discharge or emit or permit to be discharged or emitted any environmental pollutant in excess of such standards as may be prescribed.",
        "simplified_en": "No factory or business is allowed to release smoke, chemicals, or pollution into the air, water, or land beyond the legally permitted limits.",
        "simplified_ta": "எந்தவொரு தொழிற்சாலையும் சட்டத்தால் அனுமதிக்கப்பட்ட அளவை விட அதிகமாக புகை அல்லது ரசாயனங்களை வெளியிடக்கூடாது.",
        "simplified_hi": "कोई भी कारखाना या व्यवसाय कानूनी सीमा से अधिक धुआं या रसायन हवा या पानी में नहीं छोड़ सकता।",
        "punishment": "Imprisonment up to 5 years and/or fine up to Rs. 1 Lakh",
        "severity": "high",
    },
    {
        "section_id": "EPA-15",
        "act_code": "EPA", "act_name": "Environment (Protection) Act, 1986",
        "section_number": "15", "section_title": "Penalty for contravention of the provisions of the Act",
        "section_text": "Whoever fails to comply with or contravenes any of the provisions of this Act, or the rules made or orders or directions issued thereunder, shall, in respect of each such failure or contravention, be punishable with imprisonment for a term which may extend to five years or with fine which may extend to one lakh rupees, or with both.",
        "simplified_en": "Violating environmental rules, such as illegal pollution or ignoring government directions, is a crime punishable with up to 5 years in jail and a Rs. 1 Lakh fine.",
        "simplified_ta": "சுற்றுச்சூழல் விதிகளை மீறுவது 5 ஆண்டு வரை சிறை மற்றும் ரூ. 1 லட்சம் அபராதம் விதிக்கக்கூடிய குற்றமாகும்.",
        "simplified_hi": "पर्यावरण नियमों का उल्लंघन करने पर 5 साल तक की जेल और 1 लाख रुपये का जुर्माना हो सकता है।",
        "punishment": "Imprisonment up to 5 years and/or fine up to Rs. 1 Lakh; additional fines for continuing offences.",
        "severity": "high",
    },
    # ─── Indian Forest Act, 1927 & Tree Preservation Acts ─────────────────
    {
        "section_id": "IFA-33",
        "act_code": "IFA", "act_name": "Indian Forest Act, 1927",
        "section_number": "33", "section_title": "Penalties for acts in protected forests",
        "section_text": "Any person who commits any of the following offences, namely: fells, girdles, lops, taps or burns any tree reserved under section 30, or strips off the bark or leaves from, or otherwise damages, any such tree, shall be punishable with imprisonment for a term which may extend to six months, or with fine which may extend to five hundred rupees, or with both.",
        "simplified_en": "Cutting down, damaging, or burning trees in protected areas without permission is illegal. Local State laws also require permission from the Forest Department or Tree Authority to cut old trees even on private property.",
        "simplified_ta": "பாதுகாக்கப்பட்ட மரங்களை வெட்டுவது அல்லது சேதப்படுத்துவது சட்டவிரோதமாகும். தனியார் நிலத்தில் மரங்களை வெட்டவும் அனுமதி தேவை.",
        "simplified_hi": "संरक्षित पेड़ों को काटना या नुकसान पहुंचाना गैरकानूनी है। निजी संपत्ति पर भी पेड़ काटने के लिए अनुमति आवश्यक है।",
        "punishment": "Imprisonment up to 6 months and/or fine. State laws may have stricter penalties.",
        "severity": "medium",
    },
    {
        "section_id": "TPA-GEN-1",
        "act_code": "TPA", "act_name": "State Tree Preservation Acts (General Provisions)",
        "section_number": "General Rule", "section_title": "Restriction on Felling of Trees",
        "section_text": "Under various State Tree Preservation Acts (e.g., Delhi, Maharashtra, Karnataka), no person shall fell, remove or dispose of any tree on any land, whether public or private, without obtaining prior permission of the designated Tree Officer or Authority.",
        "simplified_en": "In most Indian states, you cannot cut down a fully grown tree (even if it is on your own property or instructed by an HOA/society) without written permission from the local Tree Authority or Forest Department.",
        "simplified_ta": "உங்கள் சொந்த நிலத்தில் இருந்தாலும், வனத்துறையின் முன் அனுமதியின்றி நீங்கள் முழுமையாக வளர்ந்த மரத்தை வெட்ட முடியாது.",
        "simplified_hi": "आप अपनी खुद की संपत्ति पर भी वन विभाग की पूर्व अनुमति के बिना पूरी तरह से विकसित पेड़ नहीं काट सकते।",
        "punishment": "Fines varying by state (often Rs. 10,000+ per tree) and potential imprisonment. Compulsory afforestation (planting new trees).",
        "severity": "medium",
    },
    # ─── Constitution of India (Environmental Duties) ──────────────────────
    {
        "section_id": "CONST-51A-G",
        "act_code": "CONST", "act_name": "Constitution of India, 1950",
        "section_number": "Article 51A(g)", "section_title": "Fundamental Duties",
        "section_text": "It shall be the duty of every citizen of India to protect and improve the natural environment including forests, lakes, rivers and wild life, and to have compassion for living creatures.",
        "simplified_en": "Every Indian citizen has a fundamental duty to protect and improve the environment, including forests, lakes, and wildlife. This means citizens should actively oppose illegal tree cutting and pollution.",
        "simplified_ta": "காடுகள், ஏரிகள் மற்றும் வனவிலங்குகள் உள்ளிட்ட சுற்றுச்சூழலைப் பாதுகாப்பது ஒவ்வொரு இந்திய குடிமகனின் அடிப்படை கடமையாகும்.",
        "simplified_hi": "जंगलों, झीलों और वन्यजीवों सहित पर्यावरण की रक्षा करना प्रत्येक भारतीय नागरिक का मौलिक कर्तव्य है।",
        "punishment": "Fundamental Duty - Not directly punishable, but forms the basis for environmental public interest litigations (PILs).",
        "severity": "low",
    },
    # ─── Public Nuisance (IPC / BNS) ───────────────────────────────────────
    {
        "section_id": "IPC-268",
        "act_code": "IPC", "act_name": "Indian Penal Code, 1860",
        "section_number": "268", "section_title": "Public nuisance",
        "section_text": "A person is guilty of a public nuisance who does any act or is guilty of an illegal omission which causes any common injury, danger or annoyance to the public or to the people in general who dwell or occupy property in the vicinity.",
        "simplified_en": "Creating a 'public nuisance' by causing excessive noise, smoke, or danger to your neighbors is a punishable offence.",
        "simplified_ta": "அண்டை வீட்டாருக்கு அதிக சத்தம், புகை அல்லது ஆபத்தை ஏற்படுத்துவதன் மூலம் 'பொது தொல்லை' உருவாக்குவது தண்டனைக்குரிய குற்றமாகும்.",
        "simplified_hi": "अपने पड़ोसियों को अत्यधिक शोर, धुएं या खतरे का कारण बनकर 'सार्वजनिक उपद्रव' पैदा करना एक दंडनीय अपराध है।",
        "punishment": "Fine up to Rs. 200 (IPC 290) and potential injunctions to stop the nuisance.",
        "severity": "low",
    },
]

async def seed_environmental_laws():
    """Insert or update environmental laws in the database."""
    async with async_session_factory() as session:
        for law in ENVIRONMENT_LAWS:
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
                print(f"  [OK] {law['section_id']} ({law['act_code']})")
            except Exception as e:
                print(f"  [FAIL] Failed to seed {law['section_id']}: {e}")

        await session.commit()
        print(f"\n[DONE] Seeded {len(ENVIRONMENT_LAWS)} environmental law sections successfully.")

if __name__ == "__main__":
    print("Seeding LexIndia with Environmental and Property Laws...\n")
    asyncio.run(seed_environmental_laws())
