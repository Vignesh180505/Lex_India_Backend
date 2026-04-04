"""LLM text generation service with fallback support (OpenAI, Gemini, Grok).

This service manages multiple LLM providers to ensure reliability. 
If the primary provider (OpenAI) fails due to rate limits or other issues,
it falls back to Gemini or Grok based on the configured order.
"""

import json
import logging
import asyncio
from typing import Optional, List, Dict, Any

from openai import AsyncOpenAI
import google.generativeai as genai

from app.config import settings

logger = logging.getLogger("lexindia.services.generate")

# ── LLM Clients ───────────────────────────────────────────────────────────
_openai_client: Optional[AsyncOpenAI] = None
_grok_client: Optional[AsyncOpenAI] = None
_gemini_model: Optional[genai.GenerativeModel] = None

def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client

def get_grok_client() -> AsyncOpenAI:
    global _grok_client
    if _grok_client is None:
        # X.AI (Grok) provides an OpenAI-compatible API
        _grok_client = AsyncOpenAI(
            api_key=settings.GROK_API_KEY,
            base_url="https://api.x.ai/v1"
        )
    return _grok_client

def get_gemini_model() -> genai.GenerativeModel:
    global _gemini_model
    if _gemini_model is None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-pro")
    return _gemini_model

# ── System Prompts ────────────────────────────────────────────────────────
SIMPLIFY_SYSTEM_PROMPT = """You are a legal simplification assistant for Indian law.
Given a section of Indian law, your task is to:
1. Rewrite it in plain English at an 8th-grade reading level. Maximum 80 words.
2. Translate that simplified English into Tamil (simplified_ta).
3. Translate that simplified English into Hindi (simplified_hi).
4. Classify the severity of this section as one of: low, medium, high.
   - high: criminal offence with imprisonment, serious penalty, or fundamental right violation
   - medium: civil liability, financial penalty, or enforceable obligation
   - low: procedural rule, definition, or administrative provision
5. Extract or describe the specific 'punishment' or penalty (e.g. "Imprisonment up to 3 years and fine"). If none, output "None".

Respond ONLY in valid JSON with exactly these keys:
{
  "simplified_en": "...",
  "simplified_ta": "...",
  "simplified_hi": "...",
  "severity": "low|medium|high",
  "punishment": "..."
}
Do not include any text outside the JSON object."""

QUERY_SYSTEM_PROMPT = """You are LexIndia, an AI legal assistant specialising in Indian law.
You will be given a citizen's problem and a set of law sections retrieved from
an Indian legal database. Your tasks are:

1. Identify which retrieved sections are most directly applicable to the problem.
2. Rank them by relevance (most relevant first).
3. Write an ai_summary: 3-4 plain sentences explaining the citizen's legal
   position and their strongest options. Write for a citizen with no legal background.
4. Return severity for each law: low | medium | high.

Rules:
- Use ONLY the law sections provided. Do not invent or recall laws from memory.
- Do not include sections with relevance below 0.50.
- Respond ONLY in valid JSON with keys: ai_summary (string), laws (array).
- Each law in the array: section_id, relevance_score (float 0-1), severity."""

# ── Provider Specific Implementations ──────────────────────────────────────

async def _call_openai(system_prompt: str, user_message: str, response_format: str = "json_object") -> str:
    client = get_openai_client()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": response_format},
        max_tokens=800,
        temperature=0.2,
    )
    return response.choices[0].message.content

async def _call_grok(system_prompt: str, user_message: str, response_format: str = "json_object") -> str:
    client = get_grok_client()
    response = await client.chat.completions.create(
        model="grok-beta", # Replace with actual Grok model name
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": response_format},
        max_tokens=800,
        temperature=0.2,
    )
    return response.choices[0].message.content

async def _call_gemini(system_prompt: str, user_message: str) -> str:
    model = get_gemini_model()
    # Combine system prompt and user message for Gemini
    full_prompt = f"{system_prompt}\n\nUSER INPUT:\n{user_message}"
    response = await model.generate_content_async(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json",
            max_output_tokens=800,
            temperature=0.2,
        )
    )
    return response.text

# ── Fallback Orchestrator ──────────────────────────────────────────────────

async def _call_llm_with_fallback(system_prompt: str, user_message: str, task_name: str) -> Optional[dict]:
    """Try providers in order until one succeeds or all fail."""
    for provider in settings.llm_providers:
        try:
            logger.info(f"Attempting {task_name} with {provider.upper()}")
            
            if provider == "openai":
                if not settings.OPENAI_API_KEY: 
                    continue
                raw_content = await _call_openai(system_prompt, user_message)
            
            elif provider == "gemini":
                if not settings.GEMINI_API_KEY: 
                    continue
                raw_content = await _call_gemini(system_prompt, user_message)
            
            elif provider == "grok":
                if not settings.GROK_API_KEY: 
                    continue
                raw_content = await _call_grok(system_prompt, user_message)
            
            else:
                logger.warning(f"Unknown LLM provider: {provider}")
                continue

            parsed = json.loads(raw_content)
            logger.info(f"Successfully completed {task_name} using {provider.upper()}")
            return parsed

        except Exception as e:
            logger.error(f"{provider.upper()} failed for {task_name}: {e}")
            continue
            
    logger.error(f"All LLM providers failed for {task_name}")
    return None

# ── Public Service Methods ─────────────────────────────────────────────────

async def simplify_section(
    section_text: str,
    section_id: str,
    act_name: str,
) -> Optional[dict]:
    """Simplify a legal section using the fallback pipeline."""
    user_message = (
        f"Act: {act_name}\n"
        f"Section: {section_id}\n\n"
        f"Original legal text:\n{section_text}"
    )
    
    parsed = await _call_llm_with_fallback(
        SIMPLIFY_SYSTEM_PROMPT, 
        user_message, 
        f"Simplify {section_id}"
    )
    
    if parsed:
        # Basic validation of simplified output
        required_keys = ["simplified_en", "simplified_ta", "simplified_hi", "severity", "punishment"]
        for key in required_keys:
            if key not in parsed or not parsed[key]:
                logger.error(f"Missing key '{key}' in LLM response for {section_id}")
                return None
        
        # Validate severity
        if parsed.get("severity") not in ("low", "medium", "high"):
            parsed["severity"] = "medium"
            
    return parsed

async def generate_query_response(
    context: str,
) -> Optional[dict]:
    """Generate AI summary and rankings using the fallback pipeline."""
    parsed = await _call_llm_with_fallback(
        QUERY_SYSTEM_PROMPT, 
        context, 
        "Generate Query Response"
    )
    
    if parsed:
        if "ai_summary" not in parsed or "laws" not in parsed:
            logger.error("Missing ai_summary or laws in LLM query response")
            return None
            
    return parsed

async def general_legal_answer(issue_en: str, issue_original: str) -> str:
    """Generate general legal guidance when no specific laws found (LLM Tier 3 Fallback).
    
    Args:
        issue_en: Issue in English
        issue_original: Original issue as user typed it
        
    Returns:
        Legal guidance text with disclaimers
    """
    system_prompt = """You are a legal information assistant for Indian law. 
A user has asked a legal question that doesn't have a direct match in our law database.

Your task:
1. Provide general legal guidance related to their question
2. Mention relevant Indian laws or areas of law that might apply
3. Include strong disclaimers that this is NOT legal advice
4. Suggest they consult a qualified lawyer
5. Keep response under 500 words

Be helpful but cautious. Never give specific legal advice."""

    user_message = f"""User's Legal Question: {issue_original}

Please provide general legal information and guidance based on Indian law principles, 
but make clear this is NOT legal advice and they should consult a lawyer."""

    try:
        parsed = await _call_llm_with_fallback(
            system_prompt,
            user_message,
            "General Legal Answer"
        )
        
        if isinstance(parsed, dict):
            answer = parsed.get("text", parsed.get("answer", str(parsed)))
        else:
            answer = str(parsed)
            
        # Add legal disclaimer
        final_answer = f"""⚠️ LEGAL INFORMATION (NOT LEGAL ADVICE)

{answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DISCLAIMER: This is general legal information based on AI analysis, NOT legal advice.
• Laws change and may vary by state/jurisdiction
• Situation-specific factors are crucial
• Consult a qualified lawyer licensed in your jurisdiction for advice
• This information should not be relied upon for legal decisions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        return final_answer
        
    except Exception as e:
        logger.error(f"LLM general answer generation failed: {e}")
        return f"""Unable to retrieve specific legal information for your query.

For your question about: {issue_original}

Please contact:
• A qualified lawyer licensed in your jurisdiction
• Legal aid services if you cannot afford a lawyer: http://www.legalservicesindia.gov.in
• State legal services authority: Available in your state

DISCLAIMER: Always consult a qualified legal professional for advice specific to your situation.
Laws change frequently and vary by jurisdiction."""