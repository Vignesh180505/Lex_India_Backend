"""Scraper for IndiaCode section pages — extracts structured law section data.

Uses BeautifulSoup4 to parse HTML content from IndiaCode section pages.
Each section produces one structured dict that becomes one database row.

Implements exponential backoff with max 3 retries for network resilience.
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeout

logger = logging.getLogger("lexindia.scraper.indiacode")

MAX_RETRIES = 3
REQUEST_DELAY = 2  # seconds between requests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class IndiaCodeScraper:
    """Extracts section text and metadata from IndiaCode section pages."""

    def __init__(self) -> None:
        """Initialize the scraper."""
        self.scraped_count = 0
        self.error_count = 0

    async def _fetch_page_html(self, page: Page, url: str) -> Optional[str]:
        """Fetch page HTML with exponential backoff retries."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                if response and response.status >= 400:
                    logger.warning(f"HTTP {response.status} for {url} (attempt {attempt})")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return None

                html = await page.content()
                return html

            except PWTimeout:
                logger.warning(f"Timeout for {url} (attempt {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Error fetching {url}: {e} (attempt {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)

        return None

    def _parse_section(
        self, html: str, url: str, act_name: str, act_code: str, section_number: str
    ) -> Optional[Dict]:
        """Parse HTML and extract structured section data."""
        soup = BeautifulSoup(html, "lxml")

        # Extract section title — typically in h2 or a heading element
        section_title = ""
        title_candidates = soup.select("h2, h3, .section-title, .act-title")
        for el in title_candidates:
            text = el.get_text(strip=True)
            if text and len(text) > 5:
                section_title = text
                break

        if not section_title:
            # Fallback: use page title
            title_tag = soup.find("title")
            section_title = title_tag.get_text(strip=True) if title_tag else f"Section {section_number}"

        # Extract section text — main content area
        section_text = ""
        content_selectors = [
            ".WordSection1",        # Common IndiaCode content class
            ".section-content",
            "#sectionContent",
            "article",
            ".content-area",
            "main",
        ]

        for selector in content_selectors:
            content_el = soup.select_one(selector)
            if content_el:
                section_text = content_el.get_text(separator="\n", strip=True)
                if len(section_text) > 20:
                    break

        # Fallback: get all paragraph text
        if len(section_text) < 20:
            paragraphs = soup.find_all("p")
            section_text = "\n".join(
                p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
            )

        if not section_text or len(section_text) < 20:
            logger.warning(f"Insufficient text for {act_code}-{section_number} at {url}")
            return None

        # Extract punishment clause if present
        punishment = self._extract_punishment(section_text)

        # Extract amendment year if mentioned
        amendment_year = self._extract_amendment_year(section_text)

        # Build section_id
        section_id = f"{act_code}-{section_number}" if section_number else f"{act_code}-unknown"

        return {
            "section_id": section_id,
            "act_name": act_name,
            "act_code": act_code,
            "section_number": section_number,
            "section_title": section_title,
            "section_text": section_text,
            "punishment": punishment,
            "amendment_year": amendment_year,
            "source_url": url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _extract_punishment(text: str) -> Optional[str]:
        """Extract punishment clause from section text if present."""
        punishment_patterns = [
            r"(?:shall be punished|shall be liable)[^.]*\.",
            r"(?:imprisonment|fine|penalty)[^.]*(?:years?|months?|rupees)[^.]*\.",
            r"(?:punishable with)[^.]*\.",
        ]
        for pattern in punishment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return None

    @staticmethod
    def _extract_amendment_year(text: str) -> Optional[int]:
        """Extract the most recent amendment year mentioned in the text."""
        years = re.findall(r"\b(19\d{2}|20[0-2]\d)\b", text)
        if years:
            return max(int(y) for y in years)
        return None

    async def scrape_sections(
        self, section_urls: List[Dict[str, str]]
    ) -> List[Dict]:
        """Scrape all section URLs and return structured section data.

        Args:
            section_urls: List of dicts with keys: url, act_name, act_code, section_number.

        Returns:
            List of parsed section dicts.
        """
        results: List[Dict] = []
        total = len(section_urls)

        logger.info(f"Starting scrape of {total} section URLs")

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 720},
            )
            page = await context.new_page()

            for idx, section_info in enumerate(section_urls, 1):
                url = section_info["url"]
                act_name = section_info.get("act_name", "")
                act_code = section_info.get("act_code", "")
                section_number = section_info.get("section_number", "")

                try:
                    html = await self._fetch_page_html(page, url)
                    if not html:
                        self.error_count += 1
                        continue

                    parsed = self._parse_section(html, url, act_name, act_code, section_number)
                    if parsed:
                        results.append(parsed)
                        self.scraped_count += 1
                    else:
                        self.error_count += 1

                    if idx % 50 == 0 or idx == total:
                        logger.info(f"Progress: {idx}/{total} scraped ({self.scraped_count} ok, {self.error_count} errors)")

                    await asyncio.sleep(REQUEST_DELAY)

                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    self.error_count += 1
                    continue

            await browser.close()

        logger.info(
            f"Scraping complete: {self.scraped_count} sections, {self.error_count} errors"
        )
        return results


async def main() -> None:
    """Entry point for standalone scraper execution."""
    import json
    from pathlib import Path

    urls_file = Path(__file__).resolve().parents[2] / "data" / "urls" / "indiacode_urls.json"
    if not urls_file.exists():
        logger.error("No URLs file found. Run the crawler first.")
        return

    with open(urls_file, "r", encoding="utf-8") as f:
        all_urls = json.load(f)

    # Scrape IPC sections for testing
    ipc_urls = all_urls.get("IPC", [])
    if not ipc_urls:
        logger.error("No IPC URLs found in checkpoint file.")
        return

    scraper = IndiaCodeScraper()
    results = await scraper.scrape_sections(ipc_urls)
    logger.info(f"Scraped {len(results)} IPC sections")


if __name__ == "__main__":
    asyncio.run(main())
