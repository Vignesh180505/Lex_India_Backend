"""Indiacode.nic.in Scraper Service — Fetch official Indian law sections.

Uses Playwright to scrape indiacode.nic.in for the most up-to-date and official
Indian law sections directly from the government source.

Website: https://indiacode.nic.in/
No API key required - direct web scraping with Playwright (headless browser)
"""

import logging
import re
from typing import List, Optional
import asyncio

logger = logging.getLogger("lexindia.services.indiacode_scraper")

# Indiacode base URL
INDIACODE_BASE = "https://indiacode.nic.in"
INDIACODE_SEARCH = f"{INDIACODE_BASE}/handle/123456789/1362"


async def search_indiacode_mock(query: str, limit: int = 5) -> List[dict]:
    """A reliable mock scraper that returns valid, structured data."""
    logger.info(f"Executing MOCK search for: {query}")
    
    # This structure is guaranteed to pass Pydantic validation
    mock_results = [
        {
            "section_id": f"IC-MOCK-{i}",
            "act_name": "The Mock Motor Vehicles Act, 1988",
            "act_code": "MVA",
            "section_number": f"18{i}",
            "section_title": f"Mock Title for Query: '{query}'",
            "section_text": "This is the original legal text for a mock section related to motor vehicles. It is verbose and contains legal jargon to simulate a real law.",
            "simplified_en": "This is a simplified explanation in English. It clarifies that this mock law deals with traffic violations.",
            "simplified_ta": "இது ஒரு எளிமைப்படுத்தப்பட்ட விளக்கம் (தமிழ்).",
            "simplified_hi": "यह एक सरलीकृत व्याख्या है (हिंदी)।",
            "severity": "medium",
            "punishment": "A fine of up to Rs. 5000 or imprisonment for up to 3 months.",
            "filing_link": "https://vcourts.gov.in/virtualcourt/",
            "relevance_score": 0.85 - (i * 0.05)  # Decreasing score for variety
        }
        for i in range(1, limit + 1)
    ]
    return mock_results


async def fetch_law_details(section_url: str) -> Optional[dict]:
    """Fetch detailed law section from Indiacode.
    
    Args:
        section_url: Full URL to the law section on indiacode.nic.in
        
    Returns:
        Dictionary with section details or None if error
    """
    try:
        logger.info(f"Fetching Indiacode section: {section_url}")
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.warning("Playwright not installed")
            return None
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(section_url, wait_until="networkidle")
                
                # Extract section details
                section_data = await page.evaluate("""() => {
                    return {
                        title: document.querySelector('h1, .section-title')?.textContent?.trim(),
                        content: document.querySelector('.section-content, .content-area, main')?.textContent?.trim(),
                        section_no: document.querySelector('.section-number, [data-section]')?.textContent?.trim()
                    };
                }""")
                
                logger.info(f"Retrieved section: {section_data.get('section_no', 'Unknown')}")
                return section_data
                
            finally:
                await browser.close()
                
    except Exception as e:
        logger.error(f"Error fetching law details: {e}")
        return None


async def search_by_act_name(act_name: str, limit: int = 5) -> List[dict]:
    """Search for all sections of a specific act.
    
    Args:
        act_name: Name of the act (e.g., "Indian Penal Code", "Domestic Violence Act")
        limit: Maximum results
        
    Returns:
        List of law sections from that act
    """
    try:
        logger.info(f"Searching Indiacode for act: {act_name}")
        return await search_indiacode(f"{act_name} sections", limit=limit)
    except Exception as e:
        logger.error(f"Error searching by act name: {e}")
        return []
