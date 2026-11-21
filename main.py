#!/usr/bin/env python3
"""Entrypoint for the make.fun entry "The Poster for a Place That Isn't There".

Writes the committed poster image to the output directory as entry.png.
Standard library only, no network.

The output directory comes from the harness environment variable when one
is set (MAKEFUN_OUTPUT_DIR or OUTPUT_DIR), and falls back to /output,
the location the competition rules name.
"""

import os
import shutil
import sys

SOURCE_IMAGE = "poster.png"
OUTPUT_NAME = "entry.png"


def resolve_output_dir():
    for var in ("MAKEFUN_OUTPUT_DIR", "OUTPUT_DIR", "MAKEFUN_OUTPUT"):
        value = os.environ.get(var)
        if value:
            return value
    return "/output"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_IMAGE)
    if not os.path.isfile(source):
        print(f"error: committed image not found: {source}", file=sys.stderr)
        return 1

    out_dir = resolve_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, OUTPUT_NAME)
    shutil.copyfile(source, dest)
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
