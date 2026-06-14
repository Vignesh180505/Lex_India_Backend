"""Run the data pipeline synchronously (no Celery required)."""

import asyncio
import sys
from pathlib import Path

# Fix python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scraper.pipeline import run_full_pipeline

# Run the pipeline function directly, stripping the @celery_app decorator via direct caller 
# if needed, but calling it as a standard python function works because Celery @tasks are callable locally.
if __name__ == "__main__":
    print("Starting pipeline synchronously...")
    import sys
    limit = 15 if "--demo" in sys.argv else None
    try:
        # Crawl target acts (IPC and CPA for demo)
        result = run_full_pipeline(act_filter=["IPC", "CPA"], limit_per_act=limit)
        print("\nScraping Pipeline Completed successfully!")
        print(f"Stats: {result}")
        
        # Seed environmental laws
        from seed_environment_laws import seed_environmental_laws
        print("\nSeeding environmental laws...")
        asyncio.run(seed_environmental_laws())
        
    except Exception as e:
        print(f"Script failed: {e}")
