#!/usr/bin/env python3
"""
PDF to Chinese Markdown Translator
Usage: python pdf_trans2md.py <pdf_path> [--pages RANGE] [--output OUTPUT] [--title TITLE]
"""

import sys
import os
import re
import argparse
from pathlib import Path

def parse_page_ranges(range_str):
    """Parse page range string like '1-10,20-30' into list of (start, end) tuples"""
    if not range_str:
        return None

    ranges = []
    parts = range_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            ranges.append((start, end))
        else:
            page = int(part)
            ranges.append((page, page))

    return ranges

def extract_pdf_content(pdf_path, page_ranges=None):
    """Extract text content from PDF using pypdf"""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Error: pypdf not installed. Run: pip install pypdf", file=sys.stderr)
        sys.exit(1)

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    # If no page ranges specified, extract all pages
    if page_ranges is None:
        page_ranges = [(1, total_pages)]

    content = []
    for start, end in page_ranges:
        # Convert to 0-based indexing
        start_idx = max(0, start - 1)
        end_idx = min(total_pages, end)

        for i in range(start_idx, end_idx):
            text = reader.pages[i].extract_text()
            if text:
                content.append({
                    'page': i + 1,
                    'text': text
                })

    return content, total_pages

def detect_structure(text):
    """Detect document structure (headers, code, lists)"""
    lines = text.split('\n')
    structured_lines = []

    for line in lines:
        # Detect chapter/section headers (e.g., "CHAPTER FIVE", "5.1 Title")
        if re.match(r'^CHAPTER\s+\w+$', line.strip(), re.IGNORECASE):
            structured_lines.append(('chapter', line.strip()))
        elif re.match(r'^\d+\.\d+(\.\d+)?\s+', line.strip()):
            structured_lines.append(('section', line.strip()))
        # Detect code blocks (indented or containing common code patterns)
        elif line.startswith('    ') or line.startswith('\t'):
            structured_lines.append(('code', line))
        # Detect bullet points
        elif re.match(r'^[\s]*[•\-\*]\s', line):
            structured_lines.append(('bullet', line.strip()))
        # Regular paragraph
        else:
            if line.strip():
                structured_lines.append(('paragraph', line.strip()))
            else:
                structured_lines.append(('empty', ''))

    return structured_lines

def translate_to_chinese(content_blocks, mode='zh'):
    """Translate content blocks to Chinese

    Args:
        content_blocks: List of (block_type, text) tuples
        mode: 'zh' for Chinese only, 'bilingual' for Chinese with English references

    Returns:
        List of (block_type, original_text, translated_text) tuples
    """
    # This is a simplified version - in practice, this would call the LLM for translation
    translated = []

    for block_type, text in content_blocks:
        if block_type == 'code':
            # Keep code blocks unchanged - never translate
            translated.append((block_type, text, text))
        elif block_type == 'empty':
            translated.append((block_type, '', ''))
        else:
            if mode == 'bilingual':
                # In bilingual mode, we keep both original and placeholder for translation
                # In real implementation, this would call LLM for actual translation
                translated.append((block_type, text, f"[翻译] {text}"))
            else:
                # Chinese only mode
                translated.append((block_type, text, f"[翻译] {text}"))

    return translated

def generate_markdown(translated_blocks, title=None, include_toc=True, mode='zh'):
    """Generate Markdown from translated blocks

    Args:
        translated_blocks: List of (block_type, original_text, translated_text) tuples
        title: Optional custom title
        include_toc: Whether to include table of contents
        mode: 'zh' for Chinese only, 'bilingual' for Chinese with English quotes
    """
    md_lines = []

    if title:
        md_lines.append(f"# {title}\n")

    if include_toc:
        md_lines.append("## 目录\n")
        md_lines.append("（自动生成目录）\n\n")

    for block in translated_blocks:
        block_type = block[0]
        original = block[1] if len(block) > 1 else ""
        translated = block[2] if len(block) > 2 else original

        if block_type == 'chapter':
            md_lines.append(f"\n# {translated}\n")
            if mode == 'bilingual' and original != translated:
                md_lines.append(f"\n> **原文 (English):** {original}\n")
        elif block_type == 'section':
            # Determine header level based on numbering
            level = original.count('.') + 1 if original else 2
            if level > 6:
                level = 6
            md_lines.append(f"\n{'#' * level} {translated}\n")
            if mode == 'bilingual' and original != translated:
                md_lines.append(f"\n> **原文 (English):** {original}\n")
        elif block_type == 'code':
            # Code blocks are never translated
            md_lines.append(f"```\n{original}\n```")
        elif block_type == 'bullet':
            md_lines.append(f"- {translated}")
            if mode == 'bilingual' and original != translated:
                md_lines.append(f"  > {original}")
        elif block_type == 'paragraph':
            if mode == 'bilingual':
                if original and translated and original != translated:
                    md_lines.append(f"\n{translated}\n")
                    md_lines.append(f"\n> **原文 (English):**\n> {original}\n")
                else:
                    md_lines.append(f"\n{original}\n")
            else:
                md_lines.append(f"\n{translated}\n")
        elif block_type == 'empty':
            md_lines.append("")

    return '\n'.join(md_lines)

def main():
    parser = argparse.ArgumentParser(
        description='Translate PDF to Chinese Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf --pages 16-32
  %(prog)s document.pdf --pages 1-10,20-30 --output output.md
  %(prog)s document.pdf --title "第五章 Verilating"
        """
    )

    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--pages', '-p', help='Page ranges (e.g., 16-32 or 1-10,20-30)')
    parser.add_argument('--output', '-o', help='Output Markdown file path')
    parser.add_argument('--title', '-t', help='Custom title for the output')
    parser.add_argument('--mode', '-m', choices=['zh', 'bilingual'], default='zh',
                        help='Translation mode: zh (Chinese only) or bilingual (Chinese with English quotes)')
    parser.add_argument('--no-toc', action='store_true', help='Disable table of contents')
    parser.add_argument('--chapter', '-c', help='Translate specific chapter number')

    args = parser.parse_args()

    # Validate PDF path
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Parse page ranges
    page_ranges = parse_page_ranges(args.pages) if args.pages else None

    print(f"Extracting content from: {pdf_path}")
    content, total_pages = extract_pdf_content(str(pdf_path), page_ranges)

    if not content:
        print("Error: No text content extracted from PDF", file=sys.stderr)
        print("Note: If this is a scanned PDF, OCR processing is required first.", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(content)} pages (total: {total_pages})")

    # Process each page
    all_structured = []
    for page_data in content:
        structured = detect_structure(page_data['text'])
        all_structured.extend(structured)

    # Translate with mode parameter
    print("Translating content...")
    translated = translate_to_chinese(all_structured, mode=args.mode)

    # Generate Markdown
    print("Generating Markdown...")
    md_content = generate_markdown(
        translated,
        title=args.title,
        include_toc=not args.no_toc,
        mode=args.mode
    )

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = pdf_path.parent / f"{pdf_path.stem}_zh.md"

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n✓ Translation complete!")
    print(f"  Output: {output_path}")
    print(f"  Pages processed: {len(content)}")

if __name__ == '__main__':
    main()
