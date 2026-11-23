#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261123-r2 submission.

Copies the baked-in poster (entry.png, produced by paint_atlas.py) to the
output directory. Standard library only, no network, deterministic: the
same bytes are written on every run.
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEFAULT_OUTPUT = Path("/output/entry.png")
MAX_BYTES = 1_048_576  # make.fun entry limit: 1 MiB


def check_size(path: Path) -> int:
    """Return the file size, raising if the entry exceeds the 1 MiB cap."""
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"entry.png is {size} bytes, over the 1 MiB limit")
    return size


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    destination = out_dir / "entry.png"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, destination)
    size = check_size(destination)
    print(f"wrote {destination} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
