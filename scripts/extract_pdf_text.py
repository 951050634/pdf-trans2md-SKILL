#!/usr/bin/env python3
"""Explicit text-extraction fallback for the pdf-trans2md skill.

This helper is intentionally not the default translation path. It may be used only
when the user explicitly requests Python/PDF text extraction or passes
``--input-mode text``. It extracts and structures text; the current AI model still
performs the translation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


def parse_page_ranges(value: str | None, total_pages: int) -> list[int]:
    """Return validated, de-duplicated 1-based page numbers."""
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


def detect_structure(text: str) -> list[dict[str, Any]]:
    """Apply lightweight structure hints without claiming layout fidelity."""
    blocks: list[dict[str, Any]] = []
    code_lines: list[str] = []

    def flush_code() -> None:
        if code_lines:
            blocks.append(
                {
                    "type": "code",
                    "original": "\n".join(code_lines),
                    "translate": False,
                    "preserve_format": True,
                }
            )
            code_lines.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_code()
            if blocks and blocks[-1].get("type") != "empty":
                blocks.append({"type": "empty", "original": "", "translate": False})
            continue

        is_indented = line.startswith("    ") or line.startswith("\t")
        has_code_marker = bool(
            re.search(
                r"\b(def|class|import|from|return|function|const|let|var|public|private)\b|[{};]$",
                stripped,
            )
        )
        if is_indented and (code_lines or has_code_marker):
            code_lines.append(line)
            continue
        flush_code()

        if re.match(r"^(CHAPTER\s+\w+|第[一二三四五六七八九十百\d]+章)\b", stripped, re.I):
            block_type = "chapter"
        elif re.match(r"^\d+(?:\.\d+)+\s+\S", stripped):
            block_type = "section"
        elif re.match(r"^(?:[•*+\-]|\d+[.)]|[A-Za-z][.)])\s+", stripped):
            block_type = "list"
        else:
            block_type = "paragraph"

        blocks.append(
            {
                "type": block_type,
                "original": stripped,
                "translate": True,
                "preserve_format": False,
            }
        )

    flush_code()
    return blocks


def plain_blocks(text: str) -> list[dict[str, Any]]:
    return [
        {
            "type": "paragraph",
            "original": paragraph.strip(),
            "translate": True,
            "preserve_format": False,
        }
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]


def extract_pages(pdf_path: Path, page_spec: str | None, detect: bool) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required for explicit text mode: python -m pip install pypdf") from exc

    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        raise RuntimeError("the PDF is encrypted; provide a decrypted copy")

    page_numbers = parse_page_ranges(page_spec, len(reader.pages))
    result_pages: list[dict[str, Any]] = []
    for page_number in page_numbers:
        text = reader.pages[page_number - 1].extract_text() or ""
        result_pages.append(
            {
                "page": page_number,
                "text_available": bool(text.strip()),
                "blocks": detect_structure(text) if detect else plain_blocks(text),
            }
        )

    return {
        "input_mode": "text",
        "source": str(pdf_path.resolve()),
        "total_pages": len(reader.pages),
        "selected_pages": page_numbers,
        "pages": result_pages,
    }


def build_guide(data: dict[str, Any], mode: str, title: str | None) -> str:
    total_blocks = sum(len(page["blocks"]) for page in data["pages"])
    translatable = sum(
        1 for page in data["pages"] for block in page["blocks"] if block.get("translate")
    )
    lines = [
        "# 显式文本提取模式翻译指南",
        "",
        "> 本文件来自用户明确授权的 PDF 文本提取模式。文本层可能丢失双栏阅读顺序、公式、表格和图注关系；翻译时必须谨慎核对。",
        "",
        f"- 模式：`{mode}`",
        f"- 总页数：{data['total_pages']}",
        f"- 选中页：{', '.join(map(str, data['selected_pages']))}",
        f"- 内容块：{total_blocks}",
        f"- 待翻译块：{translatable}",
    ]
    if title:
        lines.append(f"- 输出标题：{title}")

    lines.extend(
        [
            "",
            "## 规则",
            "",
            "- 翻译由当前 AI 模型完成，不绑定任何特定模型。",
            "- 代码块、API、标识符、路径、公式变量和 DOI 保持原样。",
            "- 保留页面边界，发现疑似双栏交叉或结构错乱时必须标记，不得猜测。",
            "- `zh` 模式只输出中文。",
            "- `bilingual` 模式必须先原文，再输出中文引用块：",
            "",
            "```markdown",
            "Original text.",
            "",
            "> **译文：**",
            "> 中文译文。",
            "```",
            "",
            "## 结构化内容",
            "",
            "```json",
            json.dumps(data, ensure_ascii=False, indent=2),
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Explicit text-extraction fallback for pdf-trans2md (not the default vision workflow)."
    )
    parser.add_argument("pdf_path", help="PDF file path")
    parser.add_argument(
        "--input-mode",
        choices=["text"],
        required=True,
        help="Required guardrail. This helper only runs for explicit text mode.",
    )
    parser.add_argument("--pages", help="1-based ranges, for example 1-10,20-30")
    parser.add_argument("--output-dir", help="Directory for guide and JSON; defaults to the PDF directory")
    parser.add_argument("--title", help="Optional output title")
    parser.add_argument("--mode", choices=["zh", "bilingual"], default="zh")
    parser.add_argument("--no-structure", action="store_true", help="Treat extracted text as plain paragraphs")
    args = parser.parse_args(list(argv) if argv is not None else None)

    pdf_path = Path(args.pdf_path)
    if not pdf_path.is_file():
        parser.error(f"PDF file not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        parser.error(f"expected a .pdf file: {pdf_path}")

    try:
        data = extract_pages(pdf_path, args.pages, detect=not args.no_structure)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir) if args.output_dir else pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    base = pdf_path.stem
    json_path = output_dir / f"{base}_text_units.json"
    guide_path = output_dir / f"{base}_text_translation_guide.md"

    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    guide_path.write_text(build_guide(data, args.mode, args.title), encoding="utf-8")

    empty_pages = [page["page"] for page in data["pages"] if not page["text_available"]]
    print(f"Prepared explicit text mode for {len(data['selected_pages'])} page(s).")
    print(f"JSON:  {json_path}")
    print(f"Guide: {guide_path}")
    if empty_pages:
        print(
            "Warning: no text was extracted from page(s): " + ", ".join(map(str, empty_pages)),
            file=sys.stderr,
        )
        print("Do not silently switch modes; ask whether to use the default visual workflow.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
