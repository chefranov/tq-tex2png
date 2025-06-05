# Titan Quest TEX to PNG Converter

A Python tool for batch conversion of Titan Quest `.tex` texture files to standard `.png` images.

## Features

- Supports both TEX v1 (`TEX\x01`) and TEX v2 (`TEX\x02`) file headers.
- Automatically detects and extracts embedded DDS textures.
- Handles both compressed DDS (DXT1/3/5 etc.) and uncompressed A8R8G8B8 (BGRA) formats.
- Processes all `.tex` files in a specified folder or a specific file with a single command.
- Prints a nice progress bar and summary.
- Can be used as a Python library for direct conversion in your own scripts.

## Requirements

- Python 3.8 or newer
- [Pillow](https://python-pillow.org/) (for image processing)
- [imagecodecs](https://pypi.org/project/imagecodecs/) (for DDS decoding)

Install dependencies with:

```sh
pip install -r requirements.txt
```

## Usage

### Batch Conversion (Default)

By default, all `.tex` files from the `import` directory will be converted to `.png` in the `export` directory:

```sh
python tq_tex2png.py
```

### Specify Input/Output Folder

```sh
python tq_tex2png.py --input path/to/texfiles --output path/to/pngoutput
```

### Convert a Single File

```sh
python tq_tex2png.py --file myfile.tex
```
The result will be saved in the export directory with the same base name.

You can specify both input file and output file:
```sh
python tq_tex2png.py --file myfile.tex --out-file output_dir/result.png
```

### Help

```sh
python tq_tex2png.py --help
```

## Library Usage

You can use the main logic in your own Python code for direct conversion:

```python
from tq_tex2png import tex_bytes_to_png

with open("somefile.tex", "rb") as f:
    tex_bytes = f.read()

img = tex_bytes_to_png(tex_bytes)
img.save("output.png")
```

This function raises `ValueError` if the input is not a valid TEX file.

## Notes

- The script will create the `import` and `export` folders if they do not exist.
- The export folder will be cleaned before each batch conversion.
- Any files that fail to convert will be reported and skipped.
- If no `.tex` files are found in the input folder, the script will notify you.

## License

MIT License

---

## Author

- Author: [Yevhen Chefranov](https://github.com/chefranov)
- Site: [titanquest.org.ua](https://titanquest.org.ua)
- GitHub: [https://github.com/chefranov/tq-tex2png](https://github.com/chefranov/tq-tex2png)