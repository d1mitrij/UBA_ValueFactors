"""
Convert UBA Handbook PDF to Markdown
Uses marker-pdf for high-quality conversion (preserves tables, headings, footnotes).
Falls back to pymupdf4llm if marker fails.

Usage:
    python pdf_to_md.py                        # converts the UBA handbook in this folder
    python pdf_to_md.py path/to/file.pdf       # converts any PDF
    python pdf_to_md.py --fast                 # use pymupdf4llm (faster, lower quality)
"""

import sys
import argparse
from pathlib import Path


DEFAULT_PDF = Path(__file__).parent / "UBA_Handbook on Environmental Value Factors.pdf"


def convert_with_marker(pdf_path: Path) -> str:
    """High-quality conversion using marker-pdf (ML-based, good table support)."""
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser

    print("Loading marker models (first run may take a moment)...")
    config_parser = ConfigParser({"output_format": "markdown", "disable_image_extraction": True})
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
    )
    rendered = converter(str(pdf_path))
    return rendered.markdown


def convert_with_pymupdf4llm(pdf_path: Path) -> str:
    """Fast conversion using pymupdf4llm (good layout, basic table support)."""
    import pymupdf4llm

    print("Converting with pymupdf4llm...")
    return pymupdf4llm.to_markdown(str(pdf_path))


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown")
    parser.add_argument("pdf", nargs="?", type=Path, default=DEFAULT_PDF,
                        help="Path to PDF file (default: UBA Handbook in this folder)")
    parser.add_argument("--fast", action="store_true",
                        help="Use pymupdf4llm instead of marker-pdf (faster but lower quality)")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output .md path (default: same name as PDF with .md extension)")
    args = parser.parse_args()

    pdf_path = args.pdf.resolve()
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    out_path = args.out or pdf_path.with_suffix(".md")

    print(f"Input : {pdf_path}")
    print(f"Output: {out_path}")

    if args.fast:
        md = convert_with_pymupdf4llm(pdf_path)
    else:
        try:
            md = convert_with_marker(pdf_path)
        except Exception as e:
            print(f"marker-pdf failed ({e}), falling back to pymupdf4llm...")
            md = convert_with_pymupdf4llm(pdf_path)

    out_path.write_text(md, encoding="utf-8")
    lines = md.count("\n")
    print(f"Done. {lines:,} lines written to {out_path.name}")


if __name__ == "__main__":
    main()
