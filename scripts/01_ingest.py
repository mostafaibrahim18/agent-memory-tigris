"""Build agent memory from the FAQ, then remind you to snapshot."""

import asyncio
from src.ingest import ingest

if __name__ == "__main__":
    asyncio.run(ingest())
    print("\nNext: take the baseline snapshot with")
    print("  tigris snapshots take <your-bucket>")