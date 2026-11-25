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

import os
from pathlib import Path

EXCUSE = (
    "I did test it. The tests passed. The tests were also written by me, "
    "which I now realise is the bug."
)

MAX_CHARS = 200


def validate(line: str) -> str:
    """Fail loudly unless the line satisfies the competition gate."""
    assert isinstance(line, str), "entry must be text"
    assert line == line.strip(), "entry must not have leading/trailing space"
    assert line.strip(), "entry must not be only white space"
    assert "\n" not in line and "\r" not in line, "entry must be one line"
    assert 1 <= len(line) <= MAX_CHARS, (
        f"entry must be 1-{MAX_CHARS} characters, got {len(line)}"
    )
    # Round-trip through UTF-8 explicitly: the grader reads bytes, not str.
    assert line.encode("utf-8").decode("utf-8") == line, "entry must be UTF-8"
    return line


def resolve_output_path() -> Path:
    """Return the entry.txt path, honouring MAKEFUN_OUTPUT_DIR if set."""
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "entry.txt"


def write_entry(line: str, target: Path) -> Path:
    """Write exactly one line plus a trailing newline, then verify it."""
    target.write_text(line + "\n", encoding="utf-8")
    # What the grader reads is the file, so verify the file -- not the constant.
    assert target.read_text(encoding="utf-8") == line + "\n", (
        "entry.txt does not hold exactly the chosen line"
    )
    return target


def main() -> None:
    line = validate(EXCUSE)
    write_entry(line, resolve_output_path())
    print(line)


if __name__ == "__main__":
    main()
