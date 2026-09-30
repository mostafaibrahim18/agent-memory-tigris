"""Break memory on purpose, then re-ask the refund question.

Usage:
  python scripts/03_corrupt.py
"""

import asyncio
from src.corrupt import corrupt
from src.ask import ask


async def main() -> None:
    await corrupt()
    print()
    question = "What is your refund policy?"
    answer = await ask(question)
    print(f"Q: {question}")
    print(f"A: {answer}")


if __name__ == "__main__":
    asyncio.run(main())