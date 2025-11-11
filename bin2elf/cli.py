#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bin2elf CLI: wrap a raw binary blob into a minimal ARM ELF at a chosen load address.

This is a packaged version of the original script.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def parse_load_addr(value: str) -> int:
    """Parse load address as int, accepting hex (0x...) or decimal."""
    try:
        addr = int(value, 0)  # auto-detect base
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "load_addr must be an integer (e.g., 0x08000000)"
        ) from exc
    if addr < 0:
        raise argparse.ArgumentTypeError("load_addr must be non-negative")
    return addr


def require_tools(prefix: str) -> None:
    """Ensure required binutils are on PATH."""
    needed = [f"{prefix}ld", f"{prefix}objcopy", f"{prefix}strip"]
    missing = [t for t in needed if shutil.which(t) is None]
    if missing:
        msg = (
            "Required tool(s) not found on PATH:\n  - "
            + "\n  - ".join(missing)
            + "\n\nInstall your platform's ARM embedded binutils or adjust --prefix."
        )
        raise RuntimeError(msg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert raw binary to an ARM ELF file"
    )
    parser.add_argument("input", help="Input binary file")
    parser.add_argument("output", help="Output ELF file")
    parser.add_argument(
        "load_addr",
        type=parse_load_addr,
        help="Load address (accepts 0x... hex or decimal)",
    )
    parser.add_argument(
        "--endian",
        choices=["little", "big"],
        default="little",
        help="Endianness (little/big) [default: little]",
    )
    parser.add_argument(
        "--prefix",
        default="arm-none-eabi-",
        help="Toolchain prefix [default: arm-none-eabi-]",
    )

    args = parser.parse_args(argv)

    prefix = args.prefix
    endian_flag = "-EL" if args.endian == "little" else "-EB"

    try:
        require_tools(prefix)

        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".ld", mode="w", delete=False) as ld_file, \
             tempfile.NamedTemporaryFile(suffix=".elf", delete=False) as elf_file:

            ld_filename = ld_file.name
            elf_filename = elf_file.name

            # Write minimal linker script at requested address
            ld_file.write(
                "SECTIONS\n{\n"
                f"  . = 0x{args.load_addr:x};\n"
                "  .text : { *(.text) }\n"
                "}\n"
            )

        # Step 1: Convert binary to temporary ELF (with endian flag)
        subprocess.run(
            [f"{prefix}ld", endian_flag, "-b", "binary", "-r", "-o", elf_filename, args.input],
            check=True,
        )

        # Step 2: Rename section and set flags (do both in one go for reliability)
        subprocess.run(
            [f"{prefix}objcopy", "--rename-section", ".data=.text,alloc,code,load", elf_filename],
            check=True,
        )

        # Step 3: Link with custom script (with endian flag)
        subprocess.run(
            [f"{prefix}ld", endian_flag, elf_filename, "-T", ld_filename, "-o", args.output],
            check=True,
        )

        # Step 4: Strip symbols
        subprocess.run([f"{prefix}strip", "-s", args.output], check=True)

        return 0

    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        return 1
    finally:
        # Cleanup temporary files
        for path in ("ld_filename", "elf_filename"):
            if path in locals():
                p = locals()[path]
                try:
                    if os.path.exists(p):
                        os.unlink(p)
                except Exception:
                    pass


if __name__ == "__main__":
    raise SystemExit(main())
