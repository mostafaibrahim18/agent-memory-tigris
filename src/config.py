"""
Loads environment configuration and confirms Cognee is pointed at Tigris.

Import this module once, early, so `.env` is loaded before `import cognee`
anywhere else. Cognee reads its configuration from the environment at import
time, so order matters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root. Cognee also loads .env on its own import,
# but doing it here first means our own code can read the values too.
load_dotenv()

# The bucket that holds the agent's entire memory.
BUCKET_NAME = os.getenv("STORAGE_BUCKET_NAME")

# SYSTEM_ROOT_DIRECTORY holds the derived memory: the vector index, the
# knowledge graph, and the metadata database. It must be an ABSOLUTE local
# path, because the embedded graph engine can't write to an s3:// URL (raw
# data goes to Tigris; the databases stay local unless you're on Linux/WSL
# running full single-bucket mode). Rather than hardcode a machine-specific
# path in .env, derive it from the project root so the demo stays portable.
# setdefault means an explicit value in .env still wins.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault(
    "SYSTEM_ROOT_DIRECTORY",
    str(_PROJECT_ROOT / ".cognee_system"),
)

# Everything Cognee needs to write to Tigris instead of local disk.
REQUIRED_VARS = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "AWS_ENDPOINT_URL",
    "LLM_API_KEY",
    "LLM_MODEL",
    "EMBEDDING_MODEL",
    "STORAGE_BACKEND",
    "STORAGE_BUCKET_NAME",
    "DATA_ROOT_DIRECTORY",
    "SYSTEM_ROOT_DIRECTORY",
]


def check_config() -> None:
    """Raise early with a clear message if any required variable is missing."""
    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
    if missing:
        raise EnvironmentError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + "\nCheck your .env file against .env.example."
        )

    if os.getenv("STORAGE_BACKEND") != "s3":
        raise EnvironmentError(
            "STORAGE_BACKEND must be 's3' or Cognee will write to local disk."
        )


if __name__ == "__main__":
    check_config()
    print("Config OK.")
    print(f"  Bucket: {BUCKET_NAME}")
    print(f"  Endpoint: {os.getenv('AWS_ENDPOINT_URL')}")
    print(f"  Model: {os.getenv('LLM_MODEL')}")
    print(f"  Embedding: {os.getenv('EMBEDDING_MODEL')}")
    print("  Raw data:      Tigris (s3)")
    print("  Derived memory: local system directory")