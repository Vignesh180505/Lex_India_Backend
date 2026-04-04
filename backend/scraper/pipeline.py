"""Scraping pipeline orchestrator — Celery task that runs the full crawl→scrape→clean→store flow.

Execution sequence:
  Step 1: Run IndiaCode crawler → produces data/urls/indiacode_urls.json
  Step 2: Run IndiaCode scraper on each URL → produces raw section dicts
  Step 3: Run cleaner + chunker → produces clean section dicts
  Step 4: Upsert clean records into PostgreSQL laws table
  Step 5: Run eCourts scraper → upsert filing_links table
  Step 6: Log summary

The pipeline is registered as a Celery periodic task to re-run weekly.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

from celery import Celery
from celery.schedules import crontab

from app.config import settings

logger = logging.getLogger("lexindia.scraper.pipeline")

# ── Celery App ────────────────────────────────────────────────────────────
celery_app = Celery(
    "lexindia",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Schedule weekly re-crawl (every Sunday at 2:00 AM UTC)
celery_app.conf.beat_schedule = {
    "weekly-recrawl": {
        "task": "scraper.pipeline.run_full_pipeline",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
    },
}


def _run_async(coro):
    """Run an async coroutine from synchronous Celery task context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="scraper.pipeline.run_full_pipeline", bind=True)
def run_full_pipeline(self, act_filter: Optional[List[str]] = None, limit_per_act: Optional[int] = None) -> Dict:
    """Execute the complete scraping pipeline.

    Args:
        act_filter: Optional list of act codes to process. None = all acts.
        limit_per_act: Optional max sections to scrape per act (useful for fast development/demo runs).

    Returns:
        Summary dict with counts and timing.
    """
    start_time = time.time()
    summary = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "total_acts": 0,
        "total_sections": 0,
        "total_errors": 0,
        "steps": {},
    }

    try:
        def safe_update_state(step):
            if self.request and getattr(self.request, "id", None):
                self.update_state(state="PROGRESS", meta={"step": step})

        # ── Step 1: Crawl IndiaCode ──────────────────────────────────
        logger.info("Step 1: Running IndiaCode crawler")
        safe_update_state("crawling")

        from scraper.crawlers.indiacode_crawler import IndiaCodeCrawler

        crawler = IndiaCodeCrawler()
        urls_by_act = _run_async(crawler.crawl(act_filter=act_filter))

        total_urls = sum(len(v) for v in urls_by_act.values())
        summary["steps"]["crawl"] = {
            "acts_found": len(urls_by_act),
            "urls_found": total_urls,
        }
        summary["total_acts"] = len(urls_by_act)
        logger.info(f"Step 1 complete: {total_urls} URLs across {len(urls_by_act)} acts")

        # ── Step 2: Scrape section content ───────────────────────────
        logger.info("Step 2: Running IndiaCode scraper")
        safe_update_state("scraping")

        from scraper.scrapers.indiacode_scraper import IndiaCodeScraper

        scraper = IndiaCodeScraper()
        all_raw_sections: List[Dict] = []

        for act_code, section_urls in urls_by_act.items():
            urls_to_scrape = section_urls[:limit_per_act] if limit_per_act else section_urls
            logger.info(f"  Scraping {act_code}: {len(urls_to_scrape)} sections")
            raw_sections = _run_async(scraper.scrape_sections(urls_to_scrape))
            all_raw_sections.extend(raw_sections)

        summary["steps"]["scrape"] = {
            "raw_sections": len(all_raw_sections),
            "errors": scraper.error_count,
        }
        summary["total_errors"] += scraper.error_count
        logger.info(f"Step 2 complete: {len(all_raw_sections)} raw sections")

        # ── Step 3: Clean and chunk ──────────────────────────────────
        logger.info("Step 3: Running cleaner + chunker")
        safe_update_state("cleaning")

        from scraper.cleaner import clean_and_chunk

        clean_sections = clean_and_chunk(all_raw_sections)
        discarded = len(all_raw_sections) - len(clean_sections)

        summary["steps"]["clean"] = {
            "clean_sections": len(clean_sections),
            "discarded": discarded,
        }
        summary["total_sections"] = len(clean_sections)
        logger.info(f"Step 3 complete: {len(clean_sections)} clean sections ({discarded} discarded)")

        # ── Step 4: Upsert into PostgreSQL ───────────────────────────
        logger.info("Step 4: Upserting sections to database")
        safe_update_state("storing")

        upserted = _run_async(_upsert_laws(clean_sections))
        summary["steps"]["upsert"] = {"rows_upserted": upserted}
        logger.info(f"Step 4 complete: {upserted} rows upserted")

        # ── Step 5: Scrape eCourts filing links ──────────────────────
        logger.info("Step 5: Running eCourts scraper")
        safe_update_state("ecourts")

        from scraper.scrapers.ecourt_scraper import ECourtScraper

        ecourt_scraper = ECourtScraper()
        filing_links = _run_async(ecourt_scraper.scrape())
        links_stored = _run_async(_upsert_filing_links(filing_links))

        summary["steps"]["ecourts"] = {"links_stored": links_stored}
        logger.info(f"Step 5 complete: {links_stored} filing links stored")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        summary["error"] = str(e)
        summary["total_errors"] += 1

    # ── Step 6: Log summary ──────────────────────────────────────────
    elapsed = time.time() - start_time
    summary["duration_seconds"] = round(elapsed, 1)
    summary["completed_at"] = datetime.now(timezone.utc).isoformat()

    logger.info(
        f"Pipeline complete: {summary['total_acts']} acts, "
        f"{summary['total_sections']} sections, "
        f"{summary['total_errors']} errors, "
        f"{elapsed:.1f}s elapsed"
    )

    return summary


async def _upsert_laws(sections: List[Dict]) -> int:
    """Upsert cleaned sections into the laws table.

    Only populates scraped fields — simplified_* and embedding columns remain NULL.
    Uses ON CONFLICT (section_id) DO UPDATE for idempotent re-runs.
    """
    from sqlalchemy import text
    from app.database import async_session_factory

    upserted = 0
    async with async_session_factory() as session:
        for section in sections:
            try:
                await session.execute(
                    text("""
                        INSERT INTO laws (
                            section_id, act_name, act_code, section_number,
                            section_title, section_text, punishment,
                            amendment_year, source_url, scraped_at
                        )
                        VALUES (
                            :section_id, :act_name, :act_code, :section_number,
                            :section_title, :section_text, :punishment,
                            :amendment_year, :source_url, :scraped_at
                        )
                        ON CONFLICT (section_id) DO UPDATE SET
                            section_text = EXCLUDED.section_text,
                            section_title = EXCLUDED.section_title,
                            punishment = EXCLUDED.punishment,
                            amendment_year = EXCLUDED.amendment_year,
                            source_url = EXCLUDED.source_url,
                            updated_at = NOW()
                    """),
                    {
                        "section_id": section["section_id"],
                        "act_name": section["act_name"],
                        "act_code": section["act_code"],
                        "section_number": section["section_number"],
                        "section_title": section["section_title"],
                        "section_text": section["section_text"],
                        "punishment": section.get("punishment"),
                        "amendment_year": section.get("amendment_year"),
                        "source_url": section.get("source_url", ""),
                        "scraped_at": section.get("scraped_at", datetime.now(timezone.utc).isoformat()),
                    },
                )
                upserted += 1
            except Exception as e:
                logger.error(f"Error upserting {section['section_id']}: {e}")

        await session.commit()

    return upserted


async def _upsert_filing_links(links: List[Dict]) -> int:
    """Upsert filing links into the filing_links table."""
    from sqlalchemy import text
    from app.database import async_session_factory

    stored = 0
    async with async_session_factory() as session:
        for link in links:
            try:
                await session.execute(
                    text("""
                        INSERT INTO filing_links (case_type, portal_name, url)
                        VALUES (:case_type, :portal_name, :url)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "case_type": link["case_type"],
                        "portal_name": link["portal_name"],
                        "url": link["url"],
                    },
                )
                stored += 1
            except Exception as e:
                logger.error(f"Error upserting filing link {link['case_type']}: {e}")

        await session.commit()

    return stored
