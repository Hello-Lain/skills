#!/usr/bin/env python3
"""
Caveman Compress CLI

Usage:
    caveman <filepath>
"""

import argparse
import os
import sys

# Force UTF-8 on stdout/stderr before any code can print. Windows consoles
# default to cp1252 and crash on the ❌ glyphs in error/validation branches,
# masking the real error and leaving the user with a half-compressed file.
for _stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(_stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from pathlib import Path

from .compress_core import backup_dir_for, compress_file
from .compress_detect import detect_file_type, should_compress


def main():
    parser = argparse.ArgumentParser(description="Compress natural-language files in caveman style")
    parser.add_argument("--level", choices=["lite", "full", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra"])
    parser.add_argument("--savings", type=str)
    parser.add_argument("filepath")
    args = parser.parse_args()

    if args.level:
        os.environ["CAVEMAN_DEFAULT_MODE"] = args.level
    if args.savings:
        os.environ["CAVEMAN_TOKEN_SAVINGS"] = args.savings.strip().removesuffix("%")

    filepath = Path(args.filepath)

    # Check file exists
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    if not filepath.is_file():
        print(f"❌ Not a file: {filepath}")
        sys.exit(1)

    filepath = filepath.resolve()

    # Detect file type
    file_type = detect_file_type(filepath)

    print(f"Detected: {file_type}")

    # Check if compressible
    if not should_compress(filepath):
        print("Skipping: file is not natural language (code/config)")
        sys.exit(0)

    print("Starting caveman compression...\n")

    try:
        success = compress_file(filepath)

        if success:
            print("\nCompression completed successfully")
            backup_path = backup_dir_for(filepath) / (filepath.stem + ".original.md")
            print(f"Compressed: {filepath}")
            print(f"Original:   {backup_path}")
            sys.exit(0)
        else:
            print("\n❌ Compression failed after retries")
            sys.exit(2)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
