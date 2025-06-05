#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Titan Quest TEX to PNG Converter

Author: Yevhen Chefranov (https://github.com/chefranov/)
Site: titanquest.org.ua
GitHub: https://github.com/chefranov/tq-tex2png
"""

import struct
from pathlib import Path
from PIL import Image
import imagecodecs
import sys
import shutil
import argparse

def tex_to_dds(tex_bytes):
    """
    Extract DDS bytes from a Titan Quest TEX file.
    Supports both TEX v1 ('TEX\\x01') and v2 ('TEX\\x02') headers.
    """
    if len(tex_bytes) < 16:
        raise ValueError("TEX file too short")
    magic = struct.unpack_from("<I", tex_bytes, 0)[0]
    if magic not in (0x01584554, 0x02584554):
        raise ValueError("Not a valid TEX file")
    dds_offset = 12
    dds_bytes = bytearray(tex_bytes[dds_offset:])
    # Fix "DDSR" to "DDS "
    if dds_bytes[:4] == b'DDSR':
        dds_bytes[3] = 0x20
    if dds_bytes[:3] != b'DDS':
        raise ValueError("No DDS header found after TEX header")
    return bytes(dds_bytes)

def dds_parse_a8r8g8b8(dds_bytes):
    """
    Parse uncompressed DDS (A8R8G8B8/BGRA) from bytes and return as a Pillow Image.
    """
    height = struct.unpack_from("<I", dds_bytes, 12)[0]
    width = struct.unpack_from("<I", dds_bytes, 16)[0]
    bitcount = struct.unpack_from("<I", dds_bytes, 88)[0]
    if bitcount != 32:
        raise ValueError("Only 32-bit A8R8G8B8 supported")
    data = dds_bytes[128:]
    if len(data) < width * height * 4:
        raise ValueError("DDS data too short for A8R8G8B8")
    # DDS stores pixels as BGRA; Pillow expects RGBA
    img = Image.frombytes("RGBA", (width, height), data, "raw", "BGRA")
    return img

def dds_to_png(dds_bytes):
    """
    Decode DDS bytes to a Pillow Image.
    Supports both compressed and uncompressed DDS formats.
    """
    fourcc = dds_bytes[84:88]
    if fourcc == b'\x00\x00\x00\x00':
        return dds_parse_a8r8g8b8(dds_bytes)
    else:
        arr = imagecodecs.dds_decode(dds_bytes)
        img = Image.fromarray(arr)
        return img

def tex_bytes_to_png(tex_bytes):
    """
    Main utility function for use in other projects.
    Accepts TEX file bytes, returns Pillow Image object (PNG compatible).
    Raises ValueError if input is invalid or not a supported TEX.
    """
    dds_bytes = tex_to_dds(tex_bytes)
    return dds_to_png(dds_bytes)

def print_progress_bar(iteration, total, length=40):
    """
    Print a nice progress bar in the console.
    """
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\rProgress: |{bar}| {iteration}/{total} files ({percent}%)', end='\r')
    if iteration == total:
        print()  # New line on complete

def ensure_folders(import_dir, export_dir):
    """
    Ensure import and export folders exist. If not, create them.
    Clean export folder before conversion.
    """
    import_path = Path(import_dir)
    export_path = Path(export_dir)
    try:
        import_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Cannot create or access import folder '{import_dir}': {e}")
        sys.exit(1)
    try:
        export_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Cannot create or access export folder '{export_dir}': {e}")
        sys.exit(1)
    # Clean export folder
    for item in export_path.iterdir():
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"Error while cleaning export folder: {e}")

def convert_folder(import_dir='import', export_dir='export'):
    """
    Batch converts all .tex files in the import_dir to .png files in export_dir.
    Shows a progress bar and prints summary at the end.
    """
    ensure_folders(import_dir, export_dir)
    import_path = Path(import_dir)
    export_path = Path(export_dir)

    try:
        tex_files = list(import_path.glob('*.tex'))
    except Exception as e:
        print(f"Error: Cannot read from import folder '{import_dir}': {e}")
        sys.exit(1)

    if not tex_files:
        print("No .tex files found in the import folder. Nothing to convert.")
        return

    total = len(tex_files)
    success_count = 0
    error_count = 0
    failed_files = []

    for idx, tex_file in enumerate(tex_files, 1):
        try:
            with open(tex_file, 'rb') as f:
                tex_bytes = f.read()
            img = tex_bytes_to_png(tex_bytes)
            out_file = export_path / (tex_file.stem + '.png')
            img.save(out_file)
            success_count += 1
        except Exception as e:
            print(f"[Skipped] {tex_file.name}: {e}")
            error_count += 1
            failed_files.append(tex_file.name)
        print_progress_bar(idx, total)

    print("\nConversion complete.")
    print(f"Successfully converted: {success_count}")
    print(f"Skipped (errors): {error_count}")

    if failed_files:
        print("\nThe following files were skipped due to errors:")
        for fname in failed_files:
            print(f"  - {fname}")

def convert_file(tex_path, out_path):
    """
    Converts a single .tex file to .png at the specified output path.
    """
    tex_path = Path(tex_path)
    out_path = Path(out_path)
    try:
        with open(tex_path, 'rb') as f:
            tex_bytes = f.read()
        img = tex_bytes_to_png(tex_bytes)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
        print(f"Successfully converted: {tex_path.name} -> {out_path.name}")
    except Exception as e:
        print(f"Failed to convert {tex_path}: {e}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert Titan Quest .tex texture files to .png images."
    )
    parser.add_argument(
        "--input", "-i", type=str, help="Input directory containing .tex files (default: ./import)"
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Output directory for .png files (default: ./export)"
    )
    parser.add_argument(
        "--file", "-f", type=str, help="Convert a single .tex file (output will be placed in output dir or specify --out-file)"
    )
    parser.add_argument(
        "--out-file", type=str, help="Output file name for single file conversion (default: same name with .png extension in output dir)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    if args.file:
        # Single file conversion
        tex_path = Path(args.file)
        if not tex_path.exists() or not tex_path.is_file():
            print(f"Error: File not found: {tex_path}")
            sys.exit(1)
        if args.out_file:
            out_path = Path(args.out_file)
        else:
            # Use output dir if specified, else default, keep base name
            output_dir = Path(args.output) if args.output else Path("export")
            out_path = output_dir / (tex_path.stem + ".png")
        convert_file(tex_path, out_path)
    else:
        # Batch folder conversion
        import_dir = args.input if args.input else "import"
        export_dir = args.output if args.output else "export"
        convert_folder(import_dir, export_dir)

if __name__ == '__main__':
    main()