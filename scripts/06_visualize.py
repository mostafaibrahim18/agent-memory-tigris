"""
Render the knowledge graph around the refund policy, before and after corruption.

Run this twice to capture the before/after pair for the article:

  # after a clean ingest (scripts/01_ingest.py):
  python scripts/06_visualize.py clean

  # after injecting the bad fact (scripts/03_corrupt.py):
  python scripts/06_visualize.py corrupt

Each run writes a self-contained HTML file you open in a browser and screenshot.
We seed the view with the refund query so the render stays focused on the refund
neighborhood instead of the whole graph.
"""

import sys
import asyncio
from pathlib import Path

from src import config  # loads and validates .env before cognee is imported

config.check_config()

import cognee

DATASET = "support"
QUERY = "What is your refund policy?"
OUT_DIR = Path("graphs")


async def visualize(label: str) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    dest = OUT_DIR / f"graph_{label}.html"
    await cognee.visualize_graph(
        destination_file_path=str(dest.resolve()),
        dataset=DATASET,
        query=QUERY,                   # focus on the refund neighborhood
        include_session_events=False,  # graph only, no timeline overlay
    )
    print(f"Wrote {dest}")
    print("Open it in a browser and screenshot the Documents + Chunks columns.")


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "clean"
    if label not in ("clean", "corrupt"):
        print("Usage: python scripts/06_visualize.py [clean|corrupt]")
        sys.exit(1)
    asyncio.run(visualize(label))