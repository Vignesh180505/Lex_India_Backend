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


async def search_indiacode(query: str, limit: int = 5) -> List[dict]:
    """Search indiacode.nic.in for law sections.
    
    Args:
        query: Search query (act name, section number, or keyword)
        limit: Maximum results to return
        
    Returns:
        List of law sections with title, text, and link
        
    NOTE: This is a placeholder for Playwright-based scraping.
    In production, integrate:
    - pip install playwright
    - playwright install chromium
    - Use async Playwright to scrape indiacode.nic.in
    """
    try:
        logger.info(f"Scraping Indiacode for: {query}")
        
        # Try importing Playwright (might not be installed yet)
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.warning("Playwright not installed. Install with: pip install playwright")
            logger.info("Run: playwright install chromium")
            return []
        
        results = []
        
        async with async_playwright() as p:
            # Launch headless browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to Indiacode search
                search_url = f"{INDIACODE_BASE}/handle/123456789/1362?query={query}"
                logger.info(f"Navigating to: {search_url}")
                
                await page.goto(search_url, wait_until="networkidle")
                await page.wait_for_selector("div.container, div.search-results, h3, a", timeout=5000)
                
                # Extract law sections from search results
                # Selectors may vary - adjust based on actual page structure
                items = await page.query_selector_all(".search-results-item, .result-item, tr.search-result")
                
                for item in items[:limit]:
                    try:
                        # Extract title
                        title_elem = await item.query_selector("h3, .title, a")
                        title = await title_elem.text_content() if title_elem else "Unknown"
                        
                        # Extract link
                        link_elem = await item.query_selector("a")
                        link = await link_elem.get_attribute("href") if link_elem else ""
                        
                        # Extract snippet/summary
                        snippet_elem = await item.query_selector(".snippet, .description, p")
                        snippet = await snippet_elem.text_content() if snippet_elem else ""
                        
                        if title and link:
                            result = {
                                "title": title.strip(),
                                "url": f"{INDIACODE_BASE}{link}" if link.startswith("/") else link,
                                "summary": snippet.strip()[:200] if snippet else "No summary",
                                "source": "indiacode.nic.in"
                            }
                            results.append(result)
                            logger.info(f"  Found: {result['title'][:50]}...")
                    except Exception as e:
                        logger.warning(f"Error parsing search result item: {e}")
                        continue
                
                logger.info(f"Indiacode search returned {len(results)} results")
                
            except Exception as e:
                logger.error(f"Error during Indiacode scraping: {e}")
                
            finally:
                await browser.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Unexpected error in Indiacode search: {e}")
        return []


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
