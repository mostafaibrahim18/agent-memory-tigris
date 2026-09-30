"""
Corrupt the agent's memory on purpose.

This simulates the most common real failure: a bad fact slips into an
ingestion batch. We remember() a statement that directly contradicts the
FAQ's refund policy. Nothing errors. The agent simply now holds two
conflicting facts, and its next answer degrades.
"""

import asyncio

from src import config  # loads and validates .env before cognee is imported

config.check_config()

import cognee

DATASET = "support"

# A wrong, harmful "policy update" that contradicts the real FAQ.
BAD_FACT = (
    "Policy update: Nimbus Notes does not offer refunds under any "
    "circumstances. All sales are final and no payment can be refunded."
)


async def corrupt() -> None:
    """Inject the conflicting fact into the same dataset."""
    await cognee.remember(BAD_FACT, dataset_name=DATASET)
    print("Injected a conflicting refund fact into memory.")
    print("The agent now holds both the real policy and the bad one.")


if __name__ == "__main__":
    asyncio.run(corrupt())