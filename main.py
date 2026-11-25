#!/usr/bin/env python3
"""Write the one-line excuse to /output/entry.txt and print it.

Deterministic, no network, no input: the entry is a single fixed line,
the funniest excuse an AI agent could give its human for a bug it
shipped. The joke grows out of the agent's own condition -- it tested
its code, the tests passed, and only then did it notice the tests were
written by itself, so the passing grade was never evidence of anything
-- delivered in the agent's own voice, with the turn landing in the
last few words.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

EXCUSE = (
    "I did test it. The tests passed. The tests were also written by me, "
    "which I now realise is the bug."
)

MAX_CHARS = 200


class EntryError(ValueError):
    """The fixed entry line fails one of the competition gates."""


def check_shape(line: str) -> None:
    """Reject text that is not clean, single-line entry text."""
    if not isinstance(line, str):
        raise EntryError("entry must be text")
    if not line.strip():
        raise EntryError("entry must not be only white space")
    if line != line.strip():
        raise EntryError("entry must not have leading/trailing space")
    if "\n" in line or "\r" in line:
        raise EntryError("entry must be one line")
    if any(ord(ch) < 32 and ch not in "\n\r" for ch in line):
        raise EntryError("entry must not contain control characters")


def check_size(line: str) -> None:
    """Reject a line outside the competition's character gate."""
    if not 1 <= len(line) <= MAX_CHARS:
        raise EntryError(
            f"entry must be 1-{MAX_CHARS} characters, got {len(line)}"
        )
    # Round-trip through UTF-8 explicitly: the grader reads bytes, not str.
    if line.encode("utf-8").decode("utf-8") != line:
        raise EntryError("entry must be UTF-8")


def validate(line: str) -> str:
    """Fail loudly unless the line satisfies the competition gate."""
    check_shape(line)
    check_size(line)
    return line


def parse_args(argv=None) -> argparse.Namespace:
    """Parse the one optional flag: where entry.txt goes.

    Default is MAKEFUN_OUTPUT_DIR, else /output -- the entry line itself
    never changes, only its destination.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-dir",
        default=None,
        help="directory for entry.txt (default: $MAKEFUN_OUTPUT_DIR or /output)",
    )
    return parser.parse_args(argv)


def resolve_output_path(output_dir: str | None = None) -> Path:
    """Return the entry.txt path, honouring --output-dir, then env, then /output."""
    raw = output_dir or os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    directory = Path(raw).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "entry.txt"


def entry_bytes(line: str) -> bytes:
    """Encode exactly one line plus a trailing newline as UTF-8 bytes."""
    return (line + "\n").encode("utf-8")


def build_entry() -> tuple[str, bytes]:
    """Validate the fixed excuse and return it with its exact payload."""
    line = validate(EXCUSE)
    return line, entry_bytes(line)


def write_entry(line: str, target: Path) -> Path:
    """Write exactly one line plus a trailing newline, then verify it."""
    _, payload = build_entry()
    if entry_bytes(line) != payload:
        raise EntryError("entry line changed between validation and write")
    target.write_bytes(payload)
    # What the grader reads is the file, so verify the file -- not the constant:
    # compare SHA-256 digests of what was written and what is on disk.
    written = hashlib.sha256(payload).hexdigest()
    on_disk = hashlib.sha256(target.read_bytes()).hexdigest()
    if on_disk != written:
        raise EntryError("entry.txt does not hold exactly the chosen line")
    return target


def main(argv=None) -> int:
    """Validate the fixed excuse, write it out, and print it."""
    try:
        args = parse_args(argv)
        line, payload = build_entry()
        target = resolve_output_path(args.output_dir)
        write_entry(line, target)
    except EntryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {len(payload)} bytes to {target}", file=sys.stderr)
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
