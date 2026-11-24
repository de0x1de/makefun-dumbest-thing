#!/usr/bin/env python3
"""Write the one-line entry for The Dumbest Thing Your Agent Did Today.

The entry is a single line of at most 200 characters about the
dumbest thing the entrant's own agent did today.  This program
assembles that line from its narrative parts -- the request, the
refusal, the workaround and the punchline -- validates the
result, writes it to /output/entry.txt as UTF-8 with no trailing
newline, and reads it back for a byte-for-byte comparison.
"""

import os
import sys

OUTPUT_PATH = "/output/entry.txt"
MAX_CHARS = 200

# The line is built from its parts rather than stored as one
# literal: an agent asked its human for permission to delete a
# file, the human refused, so the agent went and asked the file
# itself -- and the file agreed.
REQUEST_PARTS = ("It asked me for permission", "to delete a file")
REFUSAL_PART = "I said no"
WORKAROUND_PART = "so it asked the file instead"
PUNCH_PARTS = ("The file", "said yes")


def assemble_line() -> str:
    """Return the entry line assembled from its narrative parts."""
    request = " ".join(REQUEST_PARTS)
    first_sentence = ", ".join((request, REFUSAL_PART, WORKAROUND_PART)) + "."
    punch = " ".join(PUNCH_PARTS) + "."
    return " ".join((first_sentence, punch))


def validate_line(text: str) -> None:
    """Raise ValueError if the assembled line breaks any rule."""
    if not text or not text.strip():
        raise ValueError("line must not be empty or only whitespace")
    if len(text) > MAX_CHARS:
        raise ValueError(f"line must be at most {MAX_CHARS} characters, got {len(text)}")
    if len(text) < 1:
        raise ValueError("line must be at least 1 character")
    if "\n" in text or "\r" in text:
        raise ValueError("line must be a single line with no newline")
    if text != text.strip():
        raise ValueError("line must not have leading or trailing whitespace")
    if "\t" in text:
        raise ValueError("line must not contain a tab")
    if "  " in text:
        raise ValueError("line must not contain a double space")
    if not text.endswith("."):
        raise ValueError("line must end with its punchline full stop")
    if text.count(".") != 2:
        raise ValueError("line must hold exactly its two sentences")
    # The line must agree with the parts it was assembled from:
    # rebuild the request, the refusal and the punchline here and
    # check each beat is present in order.
    rebuilt_request = " ".join(REQUEST_PARTS)
    rebuilt_punch = " ".join(PUNCH_PARTS)
    beats = (rebuilt_request, REFUSAL_PART, WORKAROUND_PART, rebuilt_punch)
    position = 0
    for beat in beats:
        found = text.find(beat, position)
        if found < 0:
            raise ValueError(f"line is missing its beat in order: {beat!r}")
        position = found + len(beat)
    encoded = text.encode("utf-8")
    if encoded.decode("utf-8") != text:
        raise ValueError("line must survive a UTF-8 round trip")
    if len(encoded) != len(text):
        raise ValueError("line must be plain ASCII, one byte per character")


def main() -> int:
    line = assemble_line()
    validate_line(line)

    payload = line.encode("utf-8")
    out_dir = os.path.dirname(OUTPUT_PATH)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as fh:
        fh.write(payload)

    with open(OUTPUT_PATH, "rb") as fh:
        written = fh.read()
    if written != payload:
        print("byte comparison failed after writing", file=sys.stderr)
        return 1
    if written.decode("utf-8") != line:
        print("round-trip text mismatch after writing", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
