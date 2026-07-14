#!/usr/bin/env python3
"""Render PDF pages to images for multimodal translation.

This utility never extracts PDF text. Its output is intended to be inspected by the
current AI model using visual/multimodal capabilities.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def parse_page_ranges(value: str | None, total_pages: int) -> list[int]:
    if not value:
        return list(range(1, total_pages + 1))

    pages: list[int] = []
    seen: set[int] = set()
    for raw_part in value.split(","):
        part = raw_part.strip()
        if not part:
            raise ValueError("empty page-range component")
        if "-" in part:
            fields = part.split("-", 1)
            if len(fields) != 2 or not all(field.strip().isdigit() for field in fields):
                raise ValueError(f"invalid page range: {part}")
            start, end = (int(field.strip()) for field in fields)
        elif part.isdigit():
            start = end = int(part)
        else:
            raise ValueError(f"invalid page value: {part}")
        if start < 1 or end < start:
            raise ValueError(f"invalid page range: {part}")
        if end > total_pages:
            raise ValueError(f"page range {part} exceeds PDF page count {total_pages}")
        for page in range(start, end + 1):
            if page not in seen:
                seen.add(page)
                pages.append(page)
    return pages


def run_external(executable: str, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    """Run an executable, including Windows .cmd/.bat wrappers."""
    command: list[str]
    if Path(executable).suffix.lower() in {".cmd", ".bat"}:
        comspec = os.environ.get("COMSPEC", "cmd.exe")
        command_line = subprocess.list2cmdline([executable, *arguments])
        command = [comspec, "/d", "/s", "/c", command_line]
    else:
        command = [executable, *arguments]
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def find_executable(name: str) -> str | None:
    """Find a native executable, resolving common Codex Poppler wrappers."""
    candidate = shutil.which(name)
    if not candidate:
        return None
    path = Path(candidate)
    if path.suffix.lower() not in {".cmd", ".bat"}:
        return str(path)

    possible = [
        path.parent.parent.parent / "native" / "poppler" / "Library" / "bin" / f"{name}.exe",
        path.parent.parent / "Library" / "bin" / f"{name}.exe",
    ]
    for resolved in possible:
        if resolved.is_file():
            return str(resolved)
    return str(path)


def get_poppler_page_count(pdf_path: Path) -> int:
    pdfinfo = find_executable("pdfinfo")
    if not pdfinfo:
        raise RuntimeError("pdfinfo was not found; install Poppler or PyMuPDF")
    result = run_external(pdfinfo, [str(pdf_path)])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "pdfinfo failed")
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise RuntimeError("could not determine PDF page count from pdfinfo")
    return int(match.group(1))


def select_backend(requested: str) -> str:
    if requested == "pymupdf":
        try:
            import fitz  # noqa: F401
        except ImportError as exc:
            raise RuntimeError("PyMuPDF was requested but is not installed") from exc
        return "pymupdf"
    if requested == "pdftoppm":
        if not find_executable("pdftoppm") or not find_executable("pdfinfo"):
            raise RuntimeError("Poppler was requested but pdftoppm/pdfinfo were not found")
        return "pdftoppm"

    try:
        import fitz  # noqa: F401

        return "pymupdf"
    except ImportError:
        if find_executable("pdftoppm") and find_executable("pdfinfo"):
            return "pdftoppm"
    raise RuntimeError("no rendering backend found; install PyMuPDF or Poppler")


def render_with_pymupdf(
    pdf_path: Path,
    output_dir: Path,
    pages: list[int],
    dpi: int,
    image_format: str,
    crop: str,
    gutter_ratio: float,
) -> list[dict[str, object]]:
    import fitz

    document = fitz.open(str(pdf_path))
    if document.needs_pass:
        raise RuntimeError("the PDF is encrypted; provide a decrypted copy")

    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    rendered: list[dict[str, object]] = []
    for page_number in pages:
        page = document[page_number - 1]
        page_rect = page.rect
        clip = None
        region = "full"
        if crop != "full":
            half = page_rect.x0 + page_rect.width / 2
            gutter = page_rect.width * gutter_ratio
            if crop == "left":
                clip = fitz.Rect(page_rect.x0, page_rect.y0, half - gutter / 2, page_rect.y1)
            else:
                clip = fitz.Rect(half + gutter / 2, page_rect.y0, page_rect.x1, page_rect.y1)
            region = crop

        pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
        suffix = "jpg" if image_format == "jpeg" else "png"
        output_path = output_dir / f"page-{page_number:04d}-{region}.{suffix}"
        pixmap.save(str(output_path))
        rendered.append(
            {
                "page": page_number,
                "region": region,
                "path": str(output_path.resolve()),
                "width": pixmap.width,
                "height": pixmap.height,
            }
        )
    document.close()
    return rendered


def render_with_pdftoppm(
    pdf_path: Path,
    output_dir: Path,
    pages: list[int],
    dpi: int,
    image_format: str,
) -> list[dict[str, object]]:
    executable = find_executable("pdftoppm")
    if not executable:
        raise RuntimeError("pdftoppm was not found")

    rendered: list[dict[str, object]] = []
    suffix = "jpg" if image_format == "jpeg" else "png"
    format_flag = "-jpeg" if image_format == "jpeg" else "-png"
    for page_number in pages:
        prefix = output_dir / f"page-{page_number:04d}-full"
        command = [
            executable,
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            "-singlefile",
            "-r",
            str(dpi),
            format_flag,
            str(pdf_path),
            str(prefix),
        ]
        result = run_external(executable, command[1:])
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"pdftoppm failed on page {page_number}")
        output_path = prefix.with_suffix(f".{suffix}")
        if not output_path.exists():
            raise RuntimeError(f"renderer did not create expected file: {output_path}")
        rendered.append(
            {
                "page": page_number,
                "region": "full",
                "path": str(output_path.resolve()),
            }
        )
    return rendered


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render PDF pages as images for the pdf-trans2md multimodal vision workflow."
    )
    parser.add_argument("pdf_path", help="PDF file path")
    parser.add_argument("--pages", help="1-based ranges, for example 1-10,20-30")
    parser.add_argument("--output-dir", help="Output directory; defaults to <pdf-stem>_pages")
    parser.add_argument("--dpi", type=int, default=240, help="Rendering DPI (default: 240)")
    parser.add_argument("--format", choices=["png", "jpeg"], default="png")
    parser.add_argument("--backend", choices=["auto", "pymupdf", "pdftoppm"], default="auto")
    parser.add_argument(
        "--crop",
        choices=["full", "left", "right"],
        default="full",
        help="Optional column crop. Inspect the full page before using left/right.",
    )
    parser.add_argument(
        "--gutter-ratio",
        type=float,
        default=0.02,
        help="Fraction of page width excluded around the center for column crops.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    pdf_path = Path(args.pdf_path)
    if not pdf_path.is_file():
        parser.error(f"PDF file not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        parser.error(f"expected a .pdf file: {pdf_path}")
    if not 72 <= args.dpi <= 600:
        parser.error("--dpi must be between 72 and 600")
    if not 0 <= args.gutter_ratio < 0.25:
        parser.error("--gutter-ratio must be in [0, 0.25)")

    try:
        backend = select_backend(args.backend)
        if args.crop != "full" and backend != "pymupdf":
            raise RuntimeError("left/right crops require the PyMuPDF backend")

        if backend == "pymupdf":
            import fitz

            document = fitz.open(str(pdf_path))
            if document.needs_pass:
                raise RuntimeError("the PDF is encrypted; provide a decrypted copy")
            total_pages = document.page_count
            document.close()
        else:
            total_pages = get_poppler_page_count(pdf_path)

        pages = parse_page_ranges(args.pages, total_pages)
        output_dir = Path(args.output_dir) if args.output_dir else pdf_path.parent / f"{pdf_path.stem}_pages"
        output_dir.mkdir(parents=True, exist_ok=True)

        if backend == "pymupdf":
            rendered = render_with_pymupdf(
                pdf_path,
                output_dir,
                pages,
                args.dpi,
                args.format,
                args.crop,
                args.gutter_ratio,
            )
        else:
            rendered = render_with_pdftoppm(pdf_path, output_dir, pages, args.dpi, args.format)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    manifest = {
        "source": str(pdf_path.resolve()),
        "input_mode": "vision",
        "text_extracted": False,
        "backend": backend,
        "dpi": args.dpi,
        "total_pages": total_pages,
        "selected_pages": pages,
        "images": rendered,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Rendered {len(rendered)} page image(s) with {backend}; no PDF text was extracted.")
    print(f"Output:   {output_dir.resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
