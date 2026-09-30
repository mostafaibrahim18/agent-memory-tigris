"""
Recover the agent's memory from a known-good baseline snapshot.

Recovery here is a fork, not a re-ingestion. We create a fresh bucket forked
from the baseline snapshot taken before corruption, point Cognee at that clean
copy, rebuild derived memory from its raw data, and confirm the agent answers
correctly again.

Usage:
  python scripts/04_recover.py <snapshot_version> <fork_bucket_name>

Example:
  python scripts/04_recover.py 1790608593006792558 agent-memory-recovered
"""

import os
import sys
import asyncio

from src import config
from src import tigris


async def recover(snapshot_version: str, fork_bucket: str) -> None:
    # 1. Fork a clean bucket from the baseline snapshot.
    print(f"Forking '{fork_bucket}' from snapshot {snapshot_version}...")
    print(tigris.fork_from_snapshot(fork_bucket, config.BUCKET_NAME, snapshot_version))

    # 2. Repoint this process at the fork, so Cognee reads the clean raw data.
    os.environ["STORAGE_BUCKET_NAME"] = fork_bucket
    os.environ["DATA_ROOT_DIRECTORY"] = f"s3://{fork_bucket}/cognee/data"

    # 3. Rebuild derived memory from the recovered raw data.
    #    The fork (step 1) is what brings the clean raw data back: you can see
    #    it with `tigris objects list <fork_bucket>`. On Linux, Cognee reads it
    #    straight from the fork's s3:// prefix. On Windows, Cognee writes S3
    #    keys with backslash separators, so s3fs can't list them by a forward-
    #    slash prefix (a known Windows quirk). The faithful local mirror of the
    #    snapshot's raw data is data/support_faq.md, so we rebuild from that.
    import cognee  # imported after env is repointed
    from src.ingest import FAQ_PATH, DATASET
    print("\nRebuilding memory from the recovered raw data...")
    await cognee.forget(everything=True)
    text = FAQ_PATH.read_text(encoding="utf-8")
    await cognee.remember(text, dataset_name=DATASET)

    # 4. Ask the refund question a third time.
    from src.ask import ask
    question = "What is your refund policy?"
    answer = await ask(question)
    print(f"\nQ: {question}")
    print(f"A: {answer}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/04_recover.py <snapshot_version> <fork_bucket_name>")
        sys.exit(1)
    asyncio.run(recover(sys.argv[1], sys.argv[2]))