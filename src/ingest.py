"""
Ingest the support knowledge base into Cognee memory.

remember() ingests the raw text AND builds the knowledge graph and vector
index in the same call. Raw data is written to Tigris; the derived graph and
vectors are built in the local system directory (see .env).
"""

import asyncio
from pathlib import Path

from src import config  # loads and validates .env before cognee is imported

config.check_config()

import cognee

# The knowledge base file and the dataset it lands in.
FAQ_PATH = Path(__file__).resolve().parent.parent / "data" / "support_faq.md"
DATASET = "support"


async def ingest(reset: bool = True) -> None:
    """Build agent memory from the FAQ.

    reset=True clears existing memory first, so a re-run starts clean.
    """
    if reset:
        await cognee.forget(everything=True)

    text = FAQ_PATH.read_text(encoding="utf-8")
    await cognee.remember(text, dataset_name=DATASET)
    print(f"Ingested {FAQ_PATH.name} into dataset '{DATASET}'.")


if __name__ == "__main__":
    asyncio.run(ingest())