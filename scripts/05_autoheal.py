"""
Self-healing memory: detect corruption, then recover automatically.

This ties the pieces together into one loop. The agent audits its own memory
with check(); if the verdict is 'degraded', it recovers on its own by forking
the latest known-good snapshot, repointing at the clean copy, and rebuilding
derived memory, then re-asks the question to confirm it is healthy again. No
human has to notice the bad answer first.

Recovery here is a fork, not a re-ingestion from scratch. The fork brings the
clean raw data back from the snapshot; the derived graph and vectors are then
rebuilt from that recovered data (on Linux/WSL straight from the fork's s3://
prefix, on Windows from the local mirror of the same data).

Usage:
  python scripts/05_autoheal.py
  python scripts/05_autoheal.py "What is your refund policy?"

It uses the latest snapshot of the configured bucket as the recovery point, so
take a baseline snapshot (scripts/01_ingest.py then `tigris snapshots take`)
before corrupting anything.
"""

import os
import sys
import time
import asyncio

from src import config
from src import tigris
from src.check import check

config.check_config()


async def autoheal(question: str) -> None:
    # 1. Let the agent audit its own memory.
    print(f"Checking memory for: {question!r}")
    verdict = await check(question)
    print(f"  verdict: {verdict['verdict']}")
    print(f"  reason:  {verdict['reason']}")

    if verdict["verdict"] != "degraded":
        print("\nMemory looks healthy. Nothing to recover.")
        return

    # 2. Degraded: recover automatically from the latest known-good snapshot.
    print("\nMemory is degraded. Recovering automatically...")
    source_bucket = config.BUCKET_NAME
    snapshot_version = tigris.latest_snapshot(source_bucket)
    fork_bucket = f"{source_bucket}-heal-{int(time.time())}"  # unique, avoids name cooldown
    print(f"  forking '{fork_bucket}' from snapshot {snapshot_version}...")
    print("  " + tigris.fork_from_snapshot(fork_bucket, source_bucket, snapshot_version))

    # 3. Repoint this process at the clean fork.
    os.environ["STORAGE_BUCKET_NAME"] = fork_bucket
    os.environ["DATA_ROOT_DIRECTORY"] = f"s3://{fork_bucket}/cognee/data"

    # 4. Rebuild derived memory from the recovered raw data.
    import cognee  # imported after env is repointed
    from src.ingest import FAQ_PATH, DATASET
    print("  rebuilding memory from the recovered raw data...")
    await cognee.forget(everything=True)
    text = FAQ_PATH.read_text(encoding="utf-8")
    await cognee.remember(text, dataset_name=DATASET)

    # 5. Confirm the agent is healthy again.
    verdict_after = await check(question)
    from src.ask import ask
    answer = await ask(question)
    print(f"\nRecovered. New verdict: {verdict_after['verdict']}")
    print(f"Q: {question}")
    print(f"A: {answer}")


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "What is your refund policy?"
    asyncio.run(autoheal(q))