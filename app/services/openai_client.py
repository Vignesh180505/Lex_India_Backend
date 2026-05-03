"""Shared AsyncOpenAI client instance.

Both generate_service.py (citizen mode) and lawyer_rag_service.py
(lawyer mode) import from this module. Initialised once at startup.
Never import from generate_service.py directly for the client.
"""

from openai import AsyncOpenAI
from app.config import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
