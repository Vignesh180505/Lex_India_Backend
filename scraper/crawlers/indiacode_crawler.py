"""Async Playwright crawler for indiacode.nic.in — discovers Act and Section URLs.

Crawls the IndiaCode portal to collect URLs for individual law sections.
IndiaCode pages are JavaScript-rendered, so Playwright (headless Chromium) is required.

Features:
- Async Playwright with headless Chromium
- 2-second delay between requests (rate limiting)
- Resume support via JSON checkpoint file
- Exponential backoff on errors (max 3 retries)
- Progress logging to logs/crawl.log
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional, Set

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PWTimeout

# ── Logging ───────────────────────────────────────────────────────────────
log_dir = Path(__file__).resolve().parents[2] / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_dir / "crawl.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("lexindia.crawler.indiacode")

# ── Constants ─────────────────────────────────────────────────────────────
BASE_URL = "https://www.indiacode.nic.in"
INDEX_URL = f"{BASE_URL}/handle/123456789/1362"
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "urls"
OUTPUT_FILE = DATA_DIR / "indiacode_urls.json"
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Priority Acts to crawl — (search keyword, act code, full name)
PRIORITY_ACTS = [
    ("Indian Penal Code", "IPC", "Indian Penal Code 1860"),
    ("Code of Criminal Procedure", "CrPC", "Code of Criminal Procedure 1973"),
    ("Code of Civil Procedure", "CPC", "Code of Civil Procedure 1908"),
    ("Information Technology Act", "ITA", "Information Technology Act 2000"),
    ("Consumer Protection Act", "CPA", "Consumer Protection Act 2019"),
    ("Protection of Women from Domestic Violence", "PWDVA", "Protection of Women from Domestic Violence Act 2005"),
    ("Right to Information Act", "RTI", "Right to Information Act 2005"),
    ("Motor Vehicles Act", "MVA", "Motor Vehicles Act 1988"),
    ("Indian Contract Act", "ICA", "Indian Contract Act 1872"),
    ("Negotiable Instruments Act", "NIA", "Negotiable Instruments Act 1881"),
]


class IndiaCodeCrawler:
    """Crawls indiacode.nic.in to discover Act and Section page URLs."""

    def __init__(self) -> None:
        """Initialize crawler with empty URL store."""
        self.discovered_urls: Dict[str, List[Dict[str, str]]] = {}
        self.visited_urls: Set[str] = set()
        self._load_checkpoint()

    def _load_checkpoint(self) -> None:
        """Load previously discovered URLs for resume support."""
        if OUTPUT_FILE.exists():
            try:
                with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                    self.discovered_urls = json.load(f)
                total = sum(len(v) for v in self.discovered_urls.values())
                logger.info(f"Loaded checkpoint: {total} URLs across {len(self.discovered_urls)} acts")
                # Mark all loaded URLs as visited
                for sections in self.discovered_urls.values():
                    for section in sections:
                        self.visited_urls.add(section.get("url", ""))
            except json.JSONDecodeError:
                logger.warning("Corrupted checkpoint file — starting fresh")
                self.discovered_urls = {}

    def _save_checkpoint(self) -> None:
        """Save discovered URLs to JSON for resume support."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.discovered_urls, f, indent=2, ensure_ascii=False)
        total = sum(len(v) for v in self.discovered_urls.values())
        logger.info(f"Checkpoint saved: {total} URLs")

    async def _retry_with_backoff(self, page: Page, url: str) -> bool:
        """Navigate to URL with exponential backoff retry logic."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                if response and response.status >= 400:
                    logger.warning(f"HTTP {response.status} for {url} (attempt {attempt}/{MAX_RETRIES})")
                    if attempt < MAX_RETRIES:
                        wait = 2 ** attempt
                        await asyncio.sleep(wait)
                        continue
                    return False
                return True
            except PWTimeout:
                logger.warning(f"Timeout loading {url} (attempt {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
            except Exception as e:
                logger.error(f"Error loading {url}: {e} (attempt {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        return False

    async def _find_act_page(self, page: Page, search_term: str) -> Optional[str]:
        """Search for an Act on IndiaCode and return its page URL."""
        search_url = f"{BASE_URL}/search?query={search_term.replace(' ', '+')}"
        logger.info(f"Searching for: {search_term}")

        success = await self._retry_with_backoff(page, search_url)
        if not success:
            logger.error(f"Failed to load search page for: {search_term}")
            return None

        await asyncio.sleep(REQUEST_DELAY)

        # Look for the Act link in search results
        try:
            links = await page.query_selector_all("a[href*='/handle/']")
            for link in links:
                text = await link.inner_text()
                if search_term.lower() in text.lower():
                    href = await link.get_attribute("href")
                    if href:
                        full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
                        logger.info(f"Found Act page: {full_url}")
                        return full_url
        except Exception as e:
            logger.error(f"Error finding Act link for {search_term}: {e}")

        return None

    async def _crawl_act_sections(
        self, page: Page, act_url: str, act_code: str, act_name: str
    ) -> List[Dict[str, str]]:
        """Crawl an Act page to discover all section URLs."""
        sections: List[Dict[str, str]] = []

        logger.info(f"Crawling Act: {act_name} ({act_url})")
        success = await self._retry_with_backoff(page, act_url)
        if not success:
            logger.error(f"Failed to load Act page: {act_url}")
            return sections

        await asyncio.sleep(REQUEST_DELAY)

        # Collect all section links on the Act page
        try:
            # IndiaCode typically renders sections as links within the Act page
            link_elements = await page.query_selector_all("a[href*='/handle/']")

            for link_el in link_elements:
                try:
                    href = await link_el.get_attribute("href")
                    title = (await link_el.inner_text()).strip()

                    if not href or not title:
                        continue

                    full_url = href if href.startswith("http") else f"{BASE_URL}{href}"

                    # Skip if already visited
                    if full_url in self.visited_urls:
                        continue

                    # Extract section number from the title if possible
                    section_number = self._extract_section_number(title)

                    section_data = {
                        "url": full_url,
                        "act_name": act_name,
                        "act_code": act_code,
                        "section_title": title,
                        "section_number": section_number,
                    }
                    sections.append(section_data)
                    self.visited_urls.add(full_url)

                except Exception as e:
                    logger.warning(f"Error processing link element: {e}")
                    continue

            logger.info(f"Found {len(sections)} section links for {act_name}")

        except Exception as e:
            logger.error(f"Error crawling sections for {act_name}: {e}")

        return sections

    @staticmethod
    def _extract_section_number(title: str) -> str:
        """Extract section number from a section title string."""
        import re
        # Common patterns: "Section 302", "S. 302", "302."
        match = re.search(r"(?:Section|S\.?)\s*(\d+[A-Za-z]*)", title, re.IGNORECASE)
        if match:
            return match.group(1)
        # Try leading number
        match = re.match(r"^(\d+[A-Za-z]*)", title.strip())
        if match:
            return match.group(1)
        return ""

    async def crawl(self, act_filter: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """Run the full crawl across all priority Acts.

        Args:
            act_filter: Optional list of act codes to crawl (e.g. ["IPC"]).
                       If None, crawls all priority Acts.
        """
        start_time = time.time()
        acts_to_crawl = PRIORITY_ACTS

        if act_filter:
            acts_to_crawl = [a for a in PRIORITY_ACTS if a[1] in act_filter]
            logger.info(f"Filtered to {len(acts_to_crawl)} acts: {act_filter}")

        async with async_playwright() as pw:
            browser: Browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 720},
            )
            page: Page = await context.new_page()

            for search_term, act_code, act_name in acts_to_crawl:
                # Skip if we already have URLs for this Act
                if act_code in self.discovered_urls and len(self.discovered_urls[act_code]) > 0:
                    logger.info(f"Skipping {act_code} — already have {len(self.discovered_urls[act_code])} URLs")
                    continue

                try:
                    # Step 1: Find the Act's page
                    act_url = await self._find_act_page(page, search_term)
                    if not act_url:
                        logger.warning(f"Could not find Act page for: {search_term}")
                        continue

                    # Step 2: Crawl all section URLs from the Act page
                    sections = await self._crawl_act_sections(page, act_url, act_code, act_name)

                    if sections:
                        self.discovered_urls[act_code] = sections
                        self._save_checkpoint()  # Save after each Act
                        logger.info(f"✓ {act_code}: {len(sections)} sections discovered")
                    else:
                        logger.warning(f"✗ {act_code}: no sections found")

                    await asyncio.sleep(REQUEST_DELAY)

                except Exception as e:
                    logger.error(f"Fatal error crawling {act_name}: {e}")
                    continue

            await browser.close()

        elapsed = time.time() - start_time
        total_urls = sum(len(v) for v in self.discovered_urls.values())
        logger.info(
            f"Crawl complete: {total_urls} section URLs across "
            f"{len(self.discovered_urls)} acts in {elapsed:.1f}s"
        )

        return self.discovered_urls


async def main() -> None:
    """Entry point for standalone crawler execution."""
    crawler = IndiaCodeCrawler()
    # Start with IPC only for initial testing
    results = await crawler.crawl(act_filter=["IPC"])
    logger.info(f"Crawl finished. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
