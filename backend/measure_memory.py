"""
Measure actual RAM usage of the backend at startup and under load.
Checks each heavy component individually.
"""
import os, sys, subprocess

def get_size_mb(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except:
                pass
    return total / (1024 * 1024)

print("=" * 60)
print("LexIndia Backend — Size & Memory Analysis")
print("=" * 60)

# ── 1. Disk sizes of key packages ────────────────────────────
import importlib.util, sysconfig

site_packages = sysconfig.get_path('purelib')
print(f"\nSite-packages dir: {site_packages}")

packages = {
    "torch": "torch",
    "sentence_transformers": "sentence_transformers",
    "transformers": "transformers",
    "fastapi": "fastapi",
    "langchain": "langchain",
    "langchain_openai": "langchain_openai",
    "openai": "openai",
    "google_genai": "google",
    "sqlalchemy": "sqlalchemy",
    "pydantic": "pydantic",
    "uvicorn": "uvicorn",
    "reportlab": "reportlab",
    "numpy": "numpy",
    "scipy": "scipy",
    "scikit_learn": "sklearn",
}

print(f"\n{'Package':<25} {'Disk Size':>12}")
print("-" * 40)
total_disk = 0
for label, pkg_dir in packages.items():
    path = os.path.join(site_packages, pkg_dir)
    if os.path.exists(path):
        size = get_size_mb(path)
        total_disk += size
        marker = " [HEAVY]" if size > 100 else ""
        print(f"{label:<25} {size:>10.1f} MB{marker}")
    else:
        print(f"{label:<25} {'not found':>12}")

print(f"\n{'TOTAL (measured packages)':<25} {total_disk:>10.1f} MB")

# ── 2. RAM measurement — baseline Python ─────────────────────
import psutil, os
proc = psutil.Process(os.getpid())
baseline_mb = proc.memory_info().rss / (1024 * 1024)
print(f"\n{'Baseline Python process':<40} {baseline_mb:>8.1f} MB RSS")

# ── 3. RAM after importing FastAPI stack ──────────────────────
import fastapi, uvicorn, pydantic, sqlalchemy, httpx, redis
after_web = proc.memory_info().rss / (1024 * 1024)
print(f"{'After: FastAPI + SQLAlchemy + Redis':<40} {after_web:>8.1f} MB RSS")

# ── 4. RAM after importing LLM clients ───────────────────────
import openai, google.genai
after_llm = proc.memory_info().rss / (1024 * 1024)
print(f"{'After: OpenAI + Google GenAI':<40} {after_llm:>8.1f} MB RSS")

# ── 5. RAM after importing torch (the big one) ───────────────
import torch
after_torch = proc.memory_info().rss / (1024 * 1024)
print(f"{'After: PyTorch import':<40} {after_torch:>8.1f} MB RSS  <- KEY")

# ── 6. RAM after loading sentence-transformers model ─────────
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
after_model = proc.memory_info().rss / (1024 * 1024)
print(f"{'After: all-MiniLM-L6-v2 loaded':<40} {after_model:>8.1f} MB RSS  <- KEY")

# ── 7. RAM after running an embedding ────────────────────────
_ = model.encode("test query for legal search", normalize_embeddings=True)
after_encode = proc.memory_info().rss / (1024 * 1024)
print(f"{'After: first encode() call':<40} {after_encode:>8.1f} MB RSS")

# ── 8. Verdict ────────────────────────────────────────────────
print()
print("=" * 60)
print("VERDICT")
print("=" * 60)
render_limit = 512
fits = after_encode < render_limit * 0.85  # 85% = safety margin

print(f"Estimated runtime RAM: {after_encode:.0f} MB")
print(f"Render.com free limit: {render_limit} MB")
print(f"Safety margin (85%):   {render_limit * 0.85:.0f} MB")
print()
if fits:
    print("PASS: FITS within Render free tier (with margin)")
else:
    headroom = after_encode - render_limit
    print(f"FAIL: EXCEEDS Render free tier by ~{headroom:.0f} MB")
    print()
    print("Main culprit: PyTorch (sentence-transformers dependency)")
    print("Recommended fix: Replace with fastembed (ONNX-based, ~45MB RAM)")
