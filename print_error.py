import asyncio
from scraper.pipeline import run_full_pipeline
import logging

logging.basicConfig(level=logging.INFO)

res = run_full_pipeline(act_filter=['IPC', 'CPA'], limit_per_act=5)
with open('error_dump.txt', 'w', encoding='utf-8') as f:
    f.write(repr(res.get('error', 'No error')))
