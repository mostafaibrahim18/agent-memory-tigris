"""
Thin Python wrapper around the Tigris CLI.

Snapshot, fork, and rebase are CLI-native operations, so rather than reach for
a storage SDK in another language, we call the `tigris` binary through
subprocess and keep the whole tutorial in Python. Each function returns the
CLI's stdout so callers can log or parse it.
"""

import os
import re
import shutil
import subprocess


def _tigris_bin() -> str:
    """Locate the tigris executable, even if PATH isn't inherited.

    On Windows the CLI is usually installed by npm as tigris.cmd under
    %APPDATA%\\npm. subprocess doesn't inherit the shell's PATH tweaks, so we
    resolve the full path here.
    """
    found = shutil.which("tigris") or shutil.which("tigris.cmd")
    if found:
        return found
    # Fall back to the npm global location on Windows.
    appdata = os.environ.get("APPDATA", "")
    for name in ("tigris.cmd", "tigris.exe", "tigris"):
        candidate = os.path.join(appdata, "npm", name)
        if os.path.isfile(candidate):
            return candidate
    raise RuntimeError(
        "Could not find the 'tigris' CLI. Ensure it is installed "
        "(npm install -g @tigrisdata/cli) and on PATH."
    )


def _run(args: list[str]) -> str:
    """Run a tigris CLI command and return stdout, raising on failure.

    The CLI prints UTF-8 (box-drawing characters, colors). We decode as UTF-8
    explicitly with errors='replace' so a stray byte never crashes the read on
    Windows, where subprocess would otherwise default to cp1252 and raise a
    UnicodeDecodeError on the CLI's table output.
    """
    result = subprocess.run(
        [_tigris_bin(), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            f"tigris {' '.join(args)} failed:\n{stderr}"
        )
    return (result.stdout or "").strip()


def take_snapshot(bucket: str) -> str:
    """Take a snapshot of a bucket. Returns the CLI output."""
    return _run(["snapshots", "take", bucket])


def list_snapshots(bucket: str) -> str:
    """List snapshots for a bucket."""
    return _run(["snapshots", "list", bucket])


def latest_snapshot(bucket: str) -> str:
    """Return the newest snapshot version for a bucket, or raise if none exist.

    Snapshot versions are monotonically increasing IDs, so the highest number is
    the most recent. We read them from `snapshots list` (which prints a table to
    stdout) rather than from `snapshots take` (whose confirmation goes to stderr).
    """
    table = list_snapshots(bucket)
    versions = re.findall(r"\d{15,}", table)
    if not versions:
        raise RuntimeError(f"No snapshots found for bucket '{bucket}'.")
    return max(versions, key=int)


def fork_from_snapshot(fork_name: str, source_bucket: str, snapshot_version: str) -> str:
    """Create a new bucket forked from a specific snapshot of the source.

    The fork is a copy-on-write clone of the source at that exact snapshot,
    so it starts as an independent, writable copy of the whole memory state.
    """
    return _run([
        "buckets", "create", fork_name,
        "--fork-of", source_bucket,
        "--source-snapshot", snapshot_version,
    ])


def list_objects(bucket: str) -> str:
    """List objects in a bucket (handles Windows backslash keys)."""
    return _run(["objects", "list", bucket])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(_run(sys.argv[1:]))
    else:
        print("Usage: python src/tigris.py <tigris args...>")