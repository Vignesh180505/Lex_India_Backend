import asyncio
import logging
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.generate_service import simplify_section, generate_query_response
from app.config import settings

# Configure logging to see the fallback process
logging.basicConfig(level=logging.INFO)

async def test_fallback_flow():
    print("\n--- Testing Fallback Flow ---")
    
    # Mocking OpenAI to fail (rate limit)
    # Mocking Gemini to succeed
    
    with patch("app.services.generate_service.get_openai_client") as mock_openai, \
         patch("app.services.generate_service.get_gemini_model") as mock_gemini:
        
        # Setup OpenAI mock to raise an exception
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI Rate Limit Exceeded"))
        mock_openai.return_value = mock_openai_instance
        
        # Setup Gemini mock to return a success
        mock_gemini_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"simplified_en": "Simple English", "simplified_ta": "Simple Tamil", "simplified_hi": "Simple Hindi", "severity": "high", "punishment": "5 years"}'
        mock_gemini_instance.generate_content_async = AsyncMock(return_value=mock_response)
        mock_gemini.return_value = mock_gemini_instance
        
        # Ensure we have "keys" in settings for the test
        settings.OPENAI_API_KEY = "mock_openai_key"
        settings.GEMINI_API_KEY = "mock_gemini_key"
        settings.LLM_PROVIDER_ORDER = "openai,gemini"
        
        print("Starting simplification request...")
        result = await simplify_section("Original Text", "IPC-302", "Indian Penal Code")
        
        if result and result["simplified_en"] == "Simple English":
            print("✅ TEST PASSED: Successfully fell back from OpenAI to Gemini")
        else:
            print(f"❌ TEST FAILED: Result was {result}")

if __name__ == "__main__":
    asyncio.run(test_fallback_flow())
