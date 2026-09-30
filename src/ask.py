"""
Ask the agent a question against its Cognee memory.

recall() auto-routes across graph, vector, and lexical search and returns the
grounded answer. This module exposes one helper so every script and the
notebook ask questions the same way.
"""

import asyncio

from src import config  # loads and validates .env before cognee is imported

config.check_config()

import cognee

DATASET = "support"


async def ask(question: str) -> str:
    """Return the agent's answer text for a question."""
    results = await cognee.recall(question, datasets=[DATASET])
    if not results:
        return "(no answer: memory returned nothing)"
    # recall() returns a list of result objects; the text field holds the answer.
    return getattr(results[0], "text", str(results[0]))


async def _demo() -> None:
    question = "What is your refund policy?"
    answer = await ask(question)
    print(f"Q: {question}")
    print(f"A: {answer}")


if __name__ == "__main__":
    asyncio.run(_demo())