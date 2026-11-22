#!/usr/bin/env python3
"""Entry point: copy the prebuilt entry.png to the output directory.

Stdlib only, no sibling imports — safe under `python3 -P -s main.py`.
The picture itself is rendered by gen_image.py (see README).
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
