"""Scraper for eCourts portal — extracts court filing portal links.

Scrapes https://ecourts.gov.in/ecourts_home/ to extract direct URLs
for each case filing type (civil, criminal, consumer, etc.).
Results are stored in the filing_links PostgreSQL table.

Implements exponential backoff with max 3 retries.
"""

import asyncio
import logging
from typing import Dict, List

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

logger = logging.getLogger("lexindia.scraper.ecourt")

MAX_RETRIES = 3
ECOURTS_URL = "https://ecourts.gov.in/ecourts_home/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Known filing portal URLs — fallback if scraping fails
DEFAULT_FILING_LINKS = [
    {
        "case_type": "civil",
        "portal_name": "eFiling - Civil Cases",
        "url": "https://efiling.ecourts.gov.in/",
    },
    {
        "case_type": "criminal",
        "portal_name": "eFiling - Criminal Cases",
        "url": "https://efiling.ecourts.gov.in/",
    },
    {
        "case_type": "consumer",
        "portal_name": "eDAKHIL - Consumer Cases",
        "url": "https://edaakhil.nic.in/",
    },
    {
        "case_type": "high_court",
        "portal_name": "High Court eFiling",
        "url": "https://efiling.ecourts.gov.in/",
    },
    {
        "case_type": "district_court",
        "portal_name": "District Court eFiling",
        "url": "https://efiling.ecourts.gov.in/",
    },
    {
        "case_type": "supreme_court",
        "portal_name": "Supreme Court eFiling",
        "url": "https://efiling.sci.gov.in/",
    },
    {
        "case_type": "labour",
        "portal_name": "CLMS - Labour Cases",
        "url": "https://clc.gov.in/clc/clms",
    },
    {
        "case_type": "cyber_crime",
        "portal_name": "National Cyber Crime Portal",
        "url": "https://cybercrime.gov.in/",
    },
    {
        "case_type": "rti",
        "portal_name": "RTI Online Portal",
        "url": "https://rtionline.gov.in/",
    },
    {
        "case_type": "women_helpline",
        "portal_name": "National Commission for Women",
        "url": "http://ncw.nic.in/",
    },
]


class ECourtScraper:
    """Scrapes eCourts portal for filing links."""

    def __init__(self) -> None:
        """Initialize the eCourt scraper."""
        self.filing_links: List[Dict[str, str]] = []

    async def _fetch_with_backoff(self, page, url: str) -> bool:
        """Fetch URL with exponential backoff."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                if response and response.status < 400:
                    return True
                logger.warning(f"HTTP {response.status if response else 'None'} for {url}")
            except PWTimeout:
                logger.warning(f"Timeout for {url} (attempt {attempt}/{MAX_RETRIES})")
            except Exception as e:
                logger.error(f"Error fetching {url}: {e} (attempt {attempt}/{MAX_RETRIES})")

            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 ** attempt)

        return False

    async def scrape(self) -> List[Dict[str, str]]:
        """Scrape eCourts portal and extract filing links.

        Returns default filing links as fallback if scraping fails.
        """
        logger.info("Scraping eCourts portal for filing links")

        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=USER_AGENT)
                page = await context.new_page()

                success = await self._fetch_with_backoff(page, ECOURTS_URL)
                if not success:
                    logger.warning("eCourts portal unreachable — using default links")
                    return DEFAULT_FILING_LINKS

                html = await page.content()
                soup = BeautifulSoup(html, "lxml")

                # Extract links from the eCourts page
                links = soup.find_all("a", href=True)
                scraped_links = []

                for link in links:
                    href = link.get("href", "")
                    text = link.get_text(strip=True)

                    if not href or not text or len(text) < 3:
                        continue

                    # Filter for filing-related links
                    filing_keywords = [
                        "filing", "efiling", "edaakhil", "case", "complaint",
                        "petition", "appeal", "portal",
                    ]
                    if any(kw in href.lower() or kw in text.lower() for kw in filing_keywords):
                        full_url = href if href.startswith("http") else f"https://ecourts.gov.in{href}"
                        case_type = self._classify_case_type(text, full_url)
                        scraped_links.append({
                            "case_type": case_type,
                            "portal_name": text[:200],
                            "url": full_url,
                        })

                await browser.close()

                if scraped_links:
                    logger.info(f"Scraped {len(scraped_links)} filing links from eCourts")
                    # Merge with defaults to ensure coverage
                    return self._merge_with_defaults(scraped_links)
                else:
                    logger.info("No filing links found on page — using defaults")
                    return DEFAULT_FILING_LINKS

        except Exception as e:
            logger.error(f"eCourts scraping failed: {e} — using default links")
            return DEFAULT_FILING_LINKS

    @staticmethod
    def _classify_case_type(text: str, url: str) -> str:
        """Classify the case type based on link text and URL."""
        combined = f"{text} {url}".lower()
        if "consumer" in combined or "edaakhil" in combined:
            return "consumer"
        if "criminal" in combined or "fir" in combined:
            return "criminal"
        if "civil" in combined:
            return "civil"
        if "supreme" in combined:
            return "supreme_court"
        if "high" in combined:
            return "high_court"
        if "district" in combined:
            return "district_court"
        if "labour" in combined or "labor" in combined:
            return "labour"
        if "cyber" in combined:
            return "cyber_crime"
        return "general"

    @staticmethod
    def _merge_with_defaults(scraped: List[Dict]) -> List[Dict]:
        """Merge scraped links with defaults, preferring scraped versions."""
        merged = {link["case_type"]: link for link in DEFAULT_FILING_LINKS}
        for link in scraped:
            merged[link["case_type"]] = link  # Scraped overwrites default
        return list(merged.values())


async def main() -> None:
    """Entry point for standalone eCourt scraper execution."""
    scraper = ECourtScraper()
    links = await scraper.scrape()
    for link in links:
        logger.info(f"  {link['case_type']}: {link['portal_name']} → {link['url']}")


if __name__ == "__main__":
    asyncio.run(main())
