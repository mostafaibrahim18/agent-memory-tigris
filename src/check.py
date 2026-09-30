"""
Let the agent judge its own memory.

Recovery should not wait for a human to notice a wrong answer. This module
asks the agent to rate how well its memory supports an answer, so a low score
can trigger recovery automatically.

The check is deliberately simple: recall the answer, then ask the model
whether the retrieved memory is consistent and sufficient to answer. It
returns a verdict ("ok" or "degraded") and a one-line reason. With the
corrupted memory holding two contradictory refund facts, a good check reports
the contradiction instead of confidently picking one.
"""

import asyncio
import json

from src import config  # loads and validates .env before cognee is imported

config.check_config()

import cognee

DATASET = "support"

_CHECK_PROMPT = (
    "You are checking an AI agent's own memory for reliability.\n"
    "Question: {question}\n"
    "Answer the memory produced: {answer}\n\n"
    "Does the retrieved memory contain a single, consistent basis for this "
    "answer, or does it contain conflicting or contradictory statements?\n"
    "Reply with strict JSON: "
    '{{"verdict": "ok" or "degraded", "reason": "one short sentence"}}'
)


async def check(question: str) -> dict:
    """Return {'answer', 'verdict', 'reason'} for a question.

    verdict == 'degraded' means memory looks corrupted or contradictory and
    the caller should consider recovering from a known-good snapshot.
    """
    results = await cognee.recall(question, datasets=[DATASET])
    answer = getattr(results[0], "text", str(results[0])) if results else ""

    # Ask the model to audit the answer against retrieved memory.
    verdict_raw = await cognee.recall(
        _CHECK_PROMPT.format(question=question, answer=answer),
        datasets=[DATASET],
    )
    verdict_text = getattr(verdict_raw[0], "text", str(verdict_raw[0])) if verdict_raw else ""

    # Models sometimes wrap JSON in ```json ... ``` fences; strip them.
    cleaned = verdict_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        verdict = parsed.get("verdict", "unknown")
        reason = parsed.get("reason", "")
    except Exception:
        # If the model didn't return clean JSON, fall back to a keyword scan.
        low = verdict_text.lower()
        verdict = "degraded" if ("conflict" in low or "contradict" in low) else "ok"
        reason = verdict_text.strip()[:120]

    return {"answer": answer, "verdict": verdict, "reason": reason}


async def _demo() -> None:
    result = await check("What is your refund policy?")
    print(f"Answer:  {result['answer']}")
    print(f"Verdict: {result['verdict']}")
    print(f"Reason:  {result['reason']}")


if __name__ == "__main__":
    asyncio.run(_demo())