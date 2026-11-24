#!/usr/bin/env python3
"""news-image-20261124 entry: write the day's news image to /output/entry.png.

The image itself (entry.png, 1024x1024, rendered at build time by render.py
from the verified news of Tuesday 24 November 2026) ships in this repository,
because the graded program runs with no network and only the standard library.
This program copies it to the grader's output directory, validating the file
first so a corrupt or out-of-limits image fails loudly instead of being
submitted silently.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import hashlib
import os
import struct
import sys
import tempfile

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024
IMAGE_NAME = "entry.png"


def read_png_dimensions(path):
    """Return (width, height) from a PNG's IHDR chunk, or raise ValueError."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG file (bad signature)")
    length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or length != 13:
        raise ValueError("not a PNG file (missing IHDR)")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def validate_image(path):
    """Check the image against the competition's gate, before copying."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError(f"image is {size} bytes, over the 1 MiB limit")
    width, height = read_png_dimensions(path)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(f"image is {width}x{height}, over the 1024x1024 limit")
    return width, height, size


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, IMAGE_NAME)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    target = os.path.join(output_dir, IMAGE_NAME)

    try:
        width, height, size = validate_image(source)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    with open(source, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()[:12]

    os.makedirs(output_dir, exist_ok=True)
    # Write atomically: a temp file in the output dir, then rename, so the
    # grader never sees a half-written image and both runs write the same
    # bytes.
    fd, tmp_path = tempfile.mkstemp(prefix=".entry-", dir=output_dir)
    try:
        with os.fdopen(fd, "wb") as out:
            with open(source, "rb") as src:
                while True:
                    chunk = src.read(65536)
                    if not chunk:
                        break
                    out.write(chunk)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    print(f"wrote {target} ({width}x{height}, {size} bytes, "
          f"sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
