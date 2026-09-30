"""Ask the agent a question from the command line.

Usage:
  python scripts/02_ask.py "What is your refund policy?"
"""

import sys
import asyncio
from src.ask import ask


async def main() -> None:
    question = sys.argv[1] if len(sys.argv) > 1 else "What is your refund policy?"
    answer = await ask(question)
    print(f"Q: {question}")
    print(f"A: {answer}")


if __name__ == "__main__":
    asyncio.run(main())