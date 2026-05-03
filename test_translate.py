import asyncio
import sys
import json
from app.services.generate_service import _call_llm_with_fallback
from app.config import settings

async def main():
    law_results = [
        {"act_name": "Consumer Protection Act", "section_title": "Defective Products", "punishment": "Not specified"},
        {"act_name": "Indian Penal Code", "section_title": "Cheating", "punishment": "Up to 7 years"}
    ]
    lang_name = "Hindi"
    
    translation_prompt = f"""Translate these legal metadata fields into {lang_name}.
Return ONLY a valid JSON array of objects with translated 'act_name', 'section_title', and 'punishment'.
Keep the exact same array order. Do not translate English legal codes like 'IPC' or 'CrPC' - keep them as is or transliterate."""
    
    payload = [
        {"act_name": l["act_name"], "section_title": l["section_title"], "punishment": l["punishment"]}
        for l in law_results
    ]
    
    print("Calling LLM...")
    translated_data = await _call_llm_with_fallback(
        translation_prompt,
        json.dumps(payload),
        f"Batch translate law metadata to {lang_name}"
    )
    
    print("Type of translated_data:", type(translated_data))
    print("Content:", translated_data)

if __name__ == "__main__":
    asyncio.run(main())
