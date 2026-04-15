#!/usr/bin/env python3
"""
pdf.py — Fit N PDF pages into one output page (N-up layout).

Usage:
    python pdf_nup.py input.pdf <slides_per_page> [output.pdf]

    slides_per_page: 2, 4, 6, 8, 9, or 16
    output.pdf     : optional; defaults to input_<N>up.pdf

Requirements:
    pip install pymupdf --break-system-packages
"""

import sys
import math
import argparse
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with:")
    print("  pip install pymupdf --break-system-packages")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

VALID_N = {1, 2, 4, 6, 8, 9, 16}


def grid_for_n(n: int) -> tuple[int, int]:
    """Return (cols, rows) for a given n-up value."""
    layouts = {
        1: (1, 1),
        2: (2, 1),   # landscape side-by-side
        4: (2, 2),
        6: (3, 2),
        8: (4, 2),
        9: (3, 3),
        16: (4, 4),
    }
    if n in layouts:
        return layouts[n]
    # Fallback: nearest square-ish grid
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return cols, rows


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def nup_pdf(input_path: str, slides_per_page: int, output_path: str | None = None) -> str:
    """
    Combine `slides_per_page` pages of the input PDF onto each output page.

    Parameters
    ----------
    input_path      : path to the source PDF
    slides_per_page : how many source pages to place on one output page
    output_path     : destination path; auto-generated when None

    Returns
    -------
    str: path of the written output file
    """
    if slides_per_page < 1:
        raise ValueError("slides_per_page must be >= 1")

    src = fitz.open(input_path)
    total_pages = len(src)

    if total_pages == 0:
        raise ValueError("Input PDF has no pages.")

    # Auto-generate output path
    if output_path is None:
        p = Path(input_path)
        output_path = str(p.parent / f"{p.stem}_{slides_per_page}up{p.suffix}")

    cols, rows = grid_for_n(slides_per_page)

    # Use the dimensions of the first source page as the cell size
    first_page = src[0]
    cell_w = first_page.rect.width
    cell_h = first_page.rect.height

    # Output page size
    page_w = cell_w * cols
    page_h = cell_h * rows

    out_doc = fitz.open()  # new empty PDF

    # Process source pages in batches of slides_per_page
    for batch_start in range(0, total_pages, slides_per_page):
        batch = list(range(batch_start, min(batch_start + slides_per_page, total_pages)))

        # Create one output page
        out_page = out_doc.new_page(width=page_w, height=page_h)

        for idx, src_page_num in enumerate(batch):
            col = idx % cols
            row = idx // cols

            # Target rectangle on the output page
            x0 = col * cell_w
            y0 = row * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h
            target_rect = fitz.Rect(x0, y0, x1, y1)

            # Render the source page as a pixmap and paste it
            src_page = src[src_page_num]
            clip = src_page.rect            # full source page
            mat = fitz.Matrix(1, 1)         # identity; scaling done via show_pdf_page

            # show_pdf_page handles scaling automatically
            out_page.show_pdf_page(target_rect, src, src_page_num, clip=clip)

    out_doc.save(output_path, garbage=4, deflate=True)
    out_doc.close()
    src.close()

    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fit N PDF pages onto each output page (N-up / multi-up layout)."
    )
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument(
        "slides_per_page",
        type=int,
        help=f"Number of source pages per output page (recommended: {sorted(VALID_N)})",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Path for the output PDF (default: <input>_<N>up.pdf)",
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.input).is_file():
        print(f"Error: '{args.input}' not found.")
        sys.exit(1)

    if args.slides_per_page < 1:
        print("Error: slides_per_page must be a positive integer.")
        sys.exit(1)

    if args.slides_per_page not in VALID_N:
        print(
            f"Warning: {args.slides_per_page} is not a standard N-up value.\n"
            f"  Standard values: {sorted(VALID_N)}\n"
            f"  Continuing anyway with a {grid_for_n(args.slides_per_page)} grid…"
        )

    print(f"Input  : {args.input}")
    print(f"Layout : {args.slides_per_page}-up  {grid_for_n(args.slides_per_page)} grid")

    try:
        output = nup_pdf(args.input, args.slides_per_page, args.output)
        print(f"Output : {output}")
        print("Done ✓")
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()