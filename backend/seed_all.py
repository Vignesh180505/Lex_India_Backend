import asyncio
import importlib
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# The 40 acts to import and seed
ACTS = [
    "ipc", "crpc", "iea", "pca", "ndps", "tpa", "ra", "sra", "btpa", "cpa",
    "cpc", "la", "aca", "hma", "hsa", "mpl", "sma", "gwa", "mwpsca", "ida",
    "mwa", "pwa", "fa", "eca", "cla", "ita", "ita2008", "nia", "sarfaesi",
    "ibc", "pmla", "ita61", "const", "pcr", "rte", "pwd", "epa", "wpa",
    "wpa74", "apa"
]

async def seed_all():
    print("Starting Master Database Seeding for all 40 acts...")
    
    for idx, act in enumerate(ACTS, 1):
        module_name = f"seed_{act}"
        print(f"\n[{idx:2d}/40] Running {module_name}...")
        try:
            # Dynamically import the module
            module = importlib.import_module(module_name)
            # Run its async seed function
            await module.seed()
        except Exception as e:
            print(f"  [FAIL] Failed to execute {module_name}: {e}")
            
    print("\nMaster Database Seeding Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(seed_all())
