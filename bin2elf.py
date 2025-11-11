#!/usr/bin/env python3
# -*- coding: utf8 -*-
import os
import argparse
import tempfile
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Convert raw binary to ELF file')
    parser.add_argument('input', help='Input binary file')
    parser.add_argument('output', help='Output ELF file')
    parser.add_argument('load_addr', help='Load address (hex format)')
    parser.add_argument('--endian', choices=['little', 'big'], default='little',
                        help='Endianness (little/big) [default: little]')
    args = parser.parse_args()

    prefix = 'arm-none-eabi-'
    endian_flag = '-EL' if args.endian == 'little' else '-EB'
    
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.ld', mode='w', delete=False) as ld_file, \
             tempfile.NamedTemporaryFile(suffix='.elf', delete=False) as elf_file:
            
            ld_filename = ld_file.name
            elf_filename = elf_file.name
            
            # Write linker script
            ld_file.write(f"SECTIONS\n{{\n . = {args.load_addr};\n .text : {{ *(.text) }}\n}}\n")
        
        # Step 1: Convert binary to temporary ELF (with endian flag)
        subprocess.run([
            f'{prefix}ld', endian_flag, '-b', 'binary', '-r', '-o', elf_filename, args.input
        ], check=True)
        
        # Step 2: Rename section and set flags (NO endian flag for objcopy)
        subprocess.run([
            f'{prefix}objcopy',
            '--rename-section', '.data=.text',
            '--set-section-flags', '.data=alloc,code,load',
            elf_filename
        ], check=True)
        
        # Step 3: Link with custom script (with endian flag)
        subprocess.run([
            f'{prefix}ld', endian_flag, elf_filename, '-T', ld_filename, '-o', args.output
        ], check=True)
        
        # Step 4: Strip symbols (NO endian flag needed)
        subprocess.run([f'{prefix}strip', '-s', args.output], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Cleanup temporary files
        if 'ld_filename' in locals() and os.path.exists(ld_filename):
            os.unlink(ld_filename)
        if 'elf_filename' in locals() and os.path.exists(elf_filename):
            os.unlink(elf_filename)

if __name__ == '__main__':
    main()