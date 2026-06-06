# bin2elf

[![GitHub](https://img.shields.io/badge/GitHub-TAbdiukov/bin2elf-black?logo=github)](https://github.com/TAbdiukov/bin2elf)
[![PyPI Version](https://img.shields.io/pypi/v/bin2elf.svg)](https://pypi.org/project/bin2elf) 
![License](https://img.shields.io/github/license/TAbdiukov/bin2elf)

[![buymeacoffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/tabdiukov)

Convert a raw binary blob (e.g., a firmware dump) into a minimal **ARM ELF** file with a chosen load address - handy for disassemblers, debuggers, and reverse-engineering tools that expect ELF.

**macOS & Linux systems (Windows supported via WSL).**

This package provides a single CLI command:

```
bin2elf
```

It wraps GNU binutils (`arm-none-eabi-*`) in a tiny pipeline that:

1. wraps your raw bytes into a relocatable ELF,
2. marks the bytes as executable code,
3. links it at the address you provide, and
4. strips symbols for a clean, minimal output.

## Highlights

* 🔧 **Choose endianness**: little or big (`-EL` / `-EB`).
* 📍 **Explicit base address**: place `.text` exactly at `--load_addr` (e.g., `0x08000000`).
* 🧰 **Pure binutils** under the hood: predictable and portable.

## Requirements

* **Python** = 3.7
* **GNU ARM Embedded binutils** available on your `PATH`:

  * `arm-none-eabi-ld`
  * `arm-none-eabi-objcopy`
  * `arm-none-eabi-strip`

> Tip: Package names you might look for on your OS:
>
> * Debian/Ubuntu: `binutils-arm-none-eabi` (or the full `gcc-arm-none-eabi` toolchain)
> * Arch: `arm-none-eabi-binutils`
> * macOS (Homebrew): `arm-none-eabi-binutils`
> * Windows: use **WSL** or an ARM embedded toolchain (ensure `arm-none-eabi-*` tools are in `PATH`).

## Installation

```bash
pip install bin2elf
```

## Usage

```bash
bin2elf <input.bin> <output.elf> <load_addr> [--endian little|big] [--prefix arm-none-eabi-]
```

**Positional arguments**

* `input` – path to the raw binary file.
* `output` – desired ELF output path.
* `load_addr` – load address (e.g., `0x08000000`; accepts `0x` hex or decimal).

**Options**

* `--endian {little,big}` – **important**, target endianness (default: `little`).
* `--prefix` – toolchain prefix (default: `arm-none-eabi-`).

### Examples

Little-endian blob at `0x08000000`:

```bash
bin2elf firmware.bin firmware.elf 0x08000000
```

Big-endian blob at `0x00100000`:

```bash
bin2elf image.bin image_be.elf 0x00100000 --endian big
```

Analyze the result:

```bash
arm-none-eabi-readelf -h -S -l firmware.elf
arm-none-eabi-objdump -D firmware.elf | less
```

## Exit codes

* `0` – success
* `1` – an external tool returned an error (you’ll see the message on stderr)

## Security

This tool does not execute your binary; it just wraps bytes into an ELF container. Still, be mindful when opening unknown binaries in debuggers or emulators. Happy reversing! 🛠️📦


---
**Tim Abdiukov**
