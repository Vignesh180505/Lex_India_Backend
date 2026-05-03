"""Seed child labour related legal sections into `laws` table.

Run:
    python seed_child_labour_data.py
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import async_session_factory


CHILD_LABOUR_LAWS = [
    {
        "section_id": "CONST-24",
        "act_name": "Constitution of India",
        "act_code": "CONST",
        "section_number": "Art. 24",
        "section_title": "Prohibition of employment of children in factories, etc.",
        "section_text": (
            "No child below the age of fourteen years shall be employed to work in any factory or "
            "mine or engaged in any other hazardous employment."
        ),
        "simplified_en": (
            "Children below 14 years cannot be employed in factories, mines, or hazardous jobs. "
            "This is a constitutional protection against child labour."
        ),
        "severity": "high",
        "punishment": "Constitutional violation; statutory penalties apply under labour laws.",
        "filing_link": "https://labour.gov.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
    {
        "section_id": "CLPRA-3",
        "act_name": "Child and Adolescent Labour (Prohibition and Regulation) Act, 1986",
        "act_code": "CLPRA",
        "section_number": "3",
        "section_title": "Prohibition of employment of children",
        "section_text": (
            "No child shall be employed or permitted to work in any occupation or process, "
            "subject to limited statutory exceptions."
        ),
        "simplified_en": (
            "Employing a child is prohibited under law, except narrow legal exceptions. "
            "Using child labour in regular commercial work is illegal."
        ),
        "severity": "high",
        "punishment": "Punishable under Section 14 of the same Act.",
        "filing_link": "https://pencil.gov.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
    {
        "section_id": "CLPRA-3A",
        "act_name": "Child and Adolescent Labour (Prohibition and Regulation) Act, 1986",
        "act_code": "CLPRA",
        "section_number": "3A",
        "section_title": "Prohibition of employment of adolescents in hazardous occupations and processes",
        "section_text": (
            "No adolescent shall be employed or permitted to work in any hazardous occupation "
            "or process set out in the Schedule."
        ),
        "simplified_en": (
            "Teenagers (adolescents) cannot be made to work in hazardous jobs or processes. "
            "Hazardous child labour is strictly prohibited."
        ),
        "severity": "high",
        "punishment": "Punishable under Section 14 of the same Act.",
        "filing_link": "https://pencil.gov.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
    {
        "section_id": "CLPRA-14",
        "act_name": "Child and Adolescent Labour (Prohibition and Regulation) Act, 1986",
        "act_code": "CLPRA",
        "section_number": "14",
        "section_title": "Penalties",
        "section_text": (
            "Whoever employs a child or an adolescent in contravention of Section 3 or Section 3A "
            "shall be punishable with imprisonment and/or fine as prescribed."
        ),
        "simplified_en": (
            "If an employer uses child labour or hazardous adolescent labour, they can face jail and fines. "
            "The law provides criminal penalties."
        ),
        "severity": "high",
        "punishment": "Imprisonment and fine as prescribed in the Act.",
        "filing_link": "https://pencil.gov.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
    {
        "section_id": "CLPRA-14A",
        "act_name": "Child and Adolescent Labour (Prohibition and Regulation) Act, 1986",
        "act_code": "CLPRA",
        "section_number": "14A",
        "section_title": "Offences to be cognizable",
        "section_text": (
            "Notwithstanding the Code of Criminal Procedure, offences under section 3 and section 14 "
            "are cognizable."
        ),
        "simplified_en": (
            "Police can register and investigate child labour offences as cognizable offences. "
            "Immediate complaint action is legally supported."
        ),
        "severity": "high",
        "punishment": "Procedural provision enabling criminal enforcement.",
        "filing_link": "https://www.indiacode.nic.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
    {
        "section_id": "BLSA-16",
        "act_name": "Bonded Labour System (Abolition) Act, 1976",
        "act_code": "BLSA",
        "section_number": "16",
        "section_title": "Punishment for enforcement of bonded labour",
        "section_text": (
            "Whoever compels any person to render bonded labour shall be punishable with imprisonment "
            "and fine as provided under this Act."
        ),
        "simplified_en": (
            "Forcing anyone, including children, into bonded labour is a criminal offence with jail and fine."
        ),
        "severity": "high",
        "punishment": "Imprisonment up to 3 years and fine as per statute.",
        "filing_link": "https://labour.gov.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
    {
        "section_id": "JJA-75",
        "act_name": "Juvenile Justice (Care and Protection of Children) Act, 2015",
        "act_code": "JJA",
        "section_number": "75",
        "section_title": "Punishment for cruelty to child",
        "section_text": (
            "Whoever, having actual charge of, or control over, a child, assaults, abandons, abuses, "
            "or wilfully neglects the child and causes unnecessary mental or physical suffering, "
            "shall be punishable."
        ),
        "simplified_en": (
            "Any cruel or abusive treatment of a child by a person in charge is punishable. "
            "This can apply in exploitative child labour situations."
        ),
        "severity": "high",
        "punishment": "Imprisonment and fine as provided under the Act.",
        "filing_link": "https://ncpcr.gov.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
    {
        "section_id": "IPC-374",
        "act_name": "Indian Penal Code, 1860",
        "act_code": "IPC",
        "section_number": "374",
        "section_title": "Unlawful compulsory labour",
        "section_text": (
            "Whoever unlawfully compels any person to labour against the will of that person "
            "shall be punished with imprisonment or fine or both."
        ),
        "simplified_en": (
            "Forcing someone to work against their will is a crime. "
            "This can be invoked in forced labour and child labour exploitation cases."
        ),
        "severity": "high",
        "punishment": "Imprisonment up to 1 year, or fine, or both.",
        "filing_link": "https://www.indiacode.nic.in/",
        "source_url": "https://www.indiacode.nic.in/",
    },
]


UPSERT_SQL = text(
    """
    INSERT INTO laws (
        section_id, act_name, act_code, section_number, section_title,
        section_text, simplified_en, simplified_ta, simplified_hi,
        severity, punishment, source_url, filing_link, scraped_at, updated_at
    ) VALUES (
        :section_id, :act_name, :act_code, :section_number, :section_title,
        :section_text, :simplified_en, '', '',
        :severity, :punishment, :source_url, :filing_link, NOW(), NOW()
    )
    ON CONFLICT (section_id) DO UPDATE SET
        act_name = EXCLUDED.act_name,
        act_code = EXCLUDED.act_code,
        section_number = EXCLUDED.section_number,
        section_title = EXCLUDED.section_title,
        section_text = EXCLUDED.section_text,
        simplified_en = EXCLUDED.simplified_en,
        severity = EXCLUDED.severity,
        punishment = EXCLUDED.punishment,
        source_url = EXCLUDED.source_url,
        filing_link = EXCLUDED.filing_link,
        embedding = NULL,
        updated_at = NOW()
    """
)


async def seed_child_labour_data() -> None:
    async with async_session_factory() as session:
        for law in CHILD_LABOUR_LAWS:
            await session.execute(UPSERT_SQL, law)
        await session.commit()

    print(f"Inserted/updated {len(CHILD_LABOUR_LAWS)} child-labour related sections.")


if __name__ == "__main__":
    asyncio.run(seed_child_labour_data())
