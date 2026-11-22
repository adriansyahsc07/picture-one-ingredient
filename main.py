"""Deliver the finished picture to wherever the runner wants it.

The artwork already exists as ``entry.png`` next to this script (it is
rendered ahead of time by ``gen_image.py``), so the job here is simply
to carry those exact bytes across to the output folder untouched.
"""

import os
import shutil
from pathlib import Path

FALLBACK_FOLDER = "/output"
ENV_VAR = "MAKEFUN_OUTPUT_DIR"
ARTWORK_NAME = "entry.png"


def source_artwork() -> Path:
    """Locate the picture that ships beside this file."""
    return Path(__file__).resolve().parent / ARTWORK_NAME


def destination_folder() -> Path:
    """Honour the runner's chosen folder, else use the default."""
    chosen = os.environ.get(ENV_VAR, "").strip()
    return Path(chosen) if chosen else Path(FALLBACK_FOLDER)


def main() -> None:
    origin = source_artwork()
    folder = destination_folder()
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / ARTWORK_NAME
    shutil.copyfile(origin, target)
    print(f"Delivered {origin.name} -> {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
