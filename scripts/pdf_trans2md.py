#!/usr/bin/env python3
"""
PDF to Chinese Markdown Translator (Claude-Guided Edition)

Architecture:
- Python script: PDF extraction, structure detection, formatting
- Claude: Actual translation work (guided by SKILL.md workflow)

Usage: python pdf_trans2md.py <pdf_path> [--pages RANGE] [--output OUTPUT] [--title TITLE] [--mode MODE]

This script prepares structured content for Claude to translate.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any


def parse_page_ranges(range_str: Optional[str]) -> Optional[List[Tuple[int, int]]]:
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


def extract_pdf_content(pdf_path: str, page_ranges: Optional[List[Tuple[int, int]]] = None) -> Tuple[List[Dict], int]:
    """Extract text content from PDF using pypdf

    Returns:
        Tuple of (content_list, total_pages)
        content_list: List of {'page': int, 'text': str}
    """
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


def detect_structure(text: str) -> List[Tuple[str, str]]:
    """Detect document structure (headers, code, lists)

    Returns list of (block_type, text) tuples:
    - 'chapter': Chapter title (CHAPTER X, 第X章)
    - 'section': Section header (numbered like 1.2, 2.3.1)
    - 'code': Code block line
    - 'bullet': List item
    - 'paragraph': Regular text
    - 'empty': Blank line
    """
    lines = text.split('\n')
    structured_lines = []

    # Track if we're inside a code block (consecutive indented lines)
    in_code_block = False
    code_block_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines but track them
        if not stripped:
            if in_code_block:
                # End of code block
                if code_block_lines:
                    structured_lines.append(('code', '\n'.join(code_block_lines)))
                    code_block_lines = []
                in_code_block = False
            structured_lines.append(('empty', ''))
            continue

        # Detect chapter titles
        if re.match(r'^(CHAPTER\s+\w+|第[一二三四五六七八九十\d]+章)', stripped, re.IGNORECASE):
            if in_code_block:
                structured_lines.append(('code', '\n'.join(code_block_lines)))
                code_block_lines = []
                in_code_block = False
            structured_lines.append(('chapter', stripped))
            continue

        # Detect section headers (numbered sections like 1.2, 2.3.1)
        if re.match(r'^\d+\.\d+(\.\d+)*\s+', stripped):
            if in_code_block:
                structured_lines.append(('code', '\n'.join(code_block_lines)))
                code_block_lines = []
                in_code_block = False
            structured_lines.append(('section', stripped))
            continue

        # Detect bullet points
        if re.match(r'^[\s]*[•\-\*\+]\s', line):
            if in_code_block:
                structured_lines.append(('code', '\n'.join(code_block_lines)))
                code_block_lines = []
                in_code_block = False
            structured_lines.append(('bullet', stripped))
            continue

        # Detect code blocks (indented lines or code-like patterns)
        is_indented = line.startswith('    ') or line.startswith('\t')

        # Code-like patterns (common programming keywords)
        code_patterns = [
            r'^(import|from|def|class|async|await|if __name__|for |while |try:|except)',
            r'^\s*(public|private|protected|static|void|int|String)',
            r'\{$|^\s*\}',  # Curly braces
            r'^\s*//|^\s*#|^\s*\*',  # Comments
        ]
        looks_like_code = any(re.match(p, stripped) for p in code_patterns)

        if is_indented or looks_like_code:
            if not in_code_block:
                in_code_block = True
                code_block_lines = []
            code_block_lines.append(line)
            continue
        else:
            if in_code_block:
                # Flush accumulated code block
                if code_block_lines:
                    structured_lines.append(('code', '\n'.join(code_block_lines)))
                    code_block_lines = []
                in_code_block = False

        # Regular paragraph
        if stripped:
            structured_lines.append(('paragraph', stripped))

    # Flush any remaining code block
    if in_code_block and code_block_lines:
        structured_lines.append(('code', '\n'.join(code_block_lines)))

    return structured_lines


def prepare_for_translation(content_blocks: List[Tuple[str, str]], mode: str = 'zh') -> Dict[str, Any]:
    """Prepare content blocks for Claude to translate

    This function does NOT translate - it structures the content
    so Claude can efficiently translate it according to SKILL.md guidelines.

    Returns a structured dict that Claude will use for translation.
    """
    translation_units = []

    for block_type, text in content_blocks:
        unit = {
            'type': block_type,
            'original': text,
            'translate': block_type not in ['code', 'empty'],  # Don't translate code or empty
            'preserve_format': block_type == 'code'
        }
        translation_units.append(unit)

    return {
        'mode': mode,
        'units': translation_units,
        'total_blocks': len(translation_units),
        'translatable_blocks': sum(1 for u in translation_units if u['translate'])
    }


def generate_translation_guide(translation_data: Dict[str, Any], title: Optional[str] = None) -> str:
    """Generate instructions for Claude on how to translate this content

    This creates a guide that tells Claude exactly how to approach the translation.
    """
    guide_lines = [
        "# PDF 翻译任务指南",
        "",
        "请按照以下规则翻译本 PDF 提取的内容：",
        "",
        "## 翻译模式",
        f"模式: {translation_data['mode']}",
        "",
        "## 翻译规则",
        "",
        "### 1. 代码块 (code) - 绝对不翻译",
        "- 保持所有代码内容完全不变",
        "- 保留所有缩进、注释、字符串",
        "- 代码中的自然语言注释可选择性翻译（双语模式）",
        "",
        "### 2. 章节标题 (chapter, section) - 准确翻译",
        "- 保持标题层级（# 数量）",
        "- 技术术语首次出现可保留英文+中文",
        "",
        "### 3. 段落 (paragraph) - 流畅翻译",
        "- 保持技术术语一致性",
        "- 代码标识符、API 名称保持英文",
        "",
        "### 4. 列表项 (bullet) - 翻译文本",
        "- 保持列表标记符（-, *, •）",
        "- 保持嵌套关系",
        "",
        "### 5. 双语模式特殊处理",
        "- 保留原文引用块：> **原文 (English):**",
        "- 中文翻译在前，原文在引用块中",
        "",
        "## 输出格式",
        "",
    ]

    if title:
        guide_lines.append(f"文档标题: {title}")
        guide_lines.append("")

    guide_lines.extend([
        "## 内容统计",
        f"- 总块数: {translation_data['total_blocks']}",
        f"- 需翻译块数: {translation_data['translatable_blocks']}",
        f"- 代码块数: {sum(1 for u in translation_data['units'] if u['type'] == 'code')}",
        "",
        "---",
        "",
        "## 待翻译内容（结构化 JSON）",
        "",
        "以下是提取的结构化内容，请逐块翻译：",
        "",
        "```json",
        json.dumps(translation_data, ensure_ascii=False, indent=2),
        "```",
        "",
        "---",
        "",
        "## 完成翻译后",
        "",
        "请将翻译结果保存为 Markdown 格式，文件名格式为：",
        "- 中文模式: `<原文件名>_zh.md`",
        "- 双语模式: `<原文件名>_bilingual.md`",
        "",
        "如果指定了 `--output` 参数，请使用指定路径。",
    ])

    return '\n'.join(guide_lines)


def save_intermediate_files(
    translation_data: Dict[str, Any],
    guide: str,
    output_dir: Path,
    base_name: str
) -> Tuple[Path, Path]:
    """Save intermediate files for Claude to process

    Returns:
        Tuple of (guide_path, json_path)
    """
    # Save the translation guide
    guide_path = output_dir / f"{base_name}_translation_guide.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)

    # Save the structured JSON
    json_path = output_dir / f"{base_name}_structured.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(translation_data, f, ensure_ascii=False, indent=2)

    return guide_path, json_path


def cleanup_intermediate_files(guide_path: Path, json_path: Path):
    """Remove intermediate files after successful translation

    Args:
        guide_path: Path to the translation guide file
        json_path: Path to the structured JSON file
    """
    try:
        if guide_path.exists():
            guide_path.unlink()
            print(f"[清理] Removed: {guide_path.name}")
        if json_path.exists():
            json_path.unlink()
            print(f"[清理] Removed: {json_path.name}")
    except Exception as e:
        print(f"[警告] Failed to remove intermediate files: {e}", file=sys.stderr)


def main():
    # Fix Windows console encoding
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass  # Python < 3.7

    parser = argparse.ArgumentParser(
        description='Prepare PDF for Claude-guided Chinese translation to Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Architecture: Python extracts & structures, Claude translates.

Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf --pages 16-32
  %(prog)s document.pdf --pages 1-10,20-30 --output output.md
  %(prog)s document.pdf --mode bilingual --title "第五章"
        """
    )

    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--pages', '-p', help='Page ranges (e.g., 16-32 or 1-10,20-30)')
    parser.add_argument('--output', '-o', help='Output Markdown file path')
    parser.add_argument('--title', '-t', help='Custom title for the output')
    parser.add_argument('--mode', '-m', choices=['zh', 'bilingual'], default='zh',
                        help='Translation mode: zh (Chinese only) or bilingual')
    parser.add_argument('--no-toc', action='store_true', help='Disable table of contents')
    parser.add_argument('--chapter', '-c', help='Translate specific chapter number')
    parser.add_argument('--no-structure', action='store_true',
                        help='Disable structure detection, use plain text mode')
    parser.add_argument('--prepare-only', action='store_true',
                        help='Only prepare files, do not attempt translation')
    parser.add_argument('--keep-intermediate', action='store_true',
                        help='Keep intermediate files (translation guide and JSON) after translation')

    args = parser.parse_args()

    # Validate PDF path
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Parse page ranges
    page_ranges = parse_page_ranges(args.pages) if args.pages else None

    print(f"[PDF] Extracting content from: {pdf_path}")
    content, total_pages = extract_pdf_content(str(pdf_path), page_ranges)

    if not content:
        print("Error: No text content extracted from PDF", file=sys.stderr)
        print("Note: If this is a scanned PDF, OCR processing is required first.", file=sys.stderr)
        sys.exit(1)

    print(f"[✓] Extracted {len(content)} pages (total: {total_pages})")

    # Process each page
    all_structured = []
    for page_data in content:
        if args.no_structure:
            # Plain text mode - treat everything as paragraphs
            for line in page_data['text'].split('\n'):
                if line.strip():
                    all_structured.append(('paragraph', line.strip()))
                else:
                    all_structured.append(('empty', ''))
        else:
            structured = detect_structure(page_data['text'])
            all_structured.extend(structured)

    print(f"[✓] Detected {len(all_structured)} content blocks")

    # Prepare for Claude translation
    print("🔧 Preparing structured content for translation...")
    translation_data = prepare_for_translation(all_structured, mode=args.mode)

    # Generate translation guide
    guide = generate_translation_guide(translation_data, title=args.title)

    # Determine output directory
    output_dir = pdf_path.parent
    base_name = pdf_path.stem

    # Save intermediate files
    guide_path, json_path = save_intermediate_files(translation_data, guide, output_dir, base_name)

    print(f"\n[准备] Prepared translation task:")
    print(f"   Guide: {guide_path}")
    print(f"   Data:  {json_path}")
    print(f"   Blocks to translate: {translation_data['translatable_blocks']}")

    if args.prepare_only:
        print("\n[✓] Preparation complete. Claude can now translate using the guide.")
        print(f"\nNext steps:")
        print(f"  1. Read: {guide_path}")
        print(f"  2. Follow the translation rules in SKILL.md")
        print(f"  3. Save result to: {args.output or output_dir / f'{base_name}_zh.md'}")
        return

    # If not prepare-only, provide instructions for Claude
    print(f"\n{'='*60}")
    print("🤖 CLAUDE TRANSLATION TASK")
    print(f"{'='*60}")
    print(f"\nPlease read the translation guide and translate the content:")
    print(f"  {guide_path}")
    print(f"\nAfter translation, save the Markdown to:")
    if args.output:
        print(f"  {args.output}")
    else:
        mode_suffix = '_bilingual' if args.mode == 'bilingual' else '_zh'
        print(f"  {output_dir / f'{base_name}{mode_suffix}.md'}")
    print(f"\nFollow the rules in SKILL.md for translation quality.")

    # Note about intermediate file cleanup
    if not args.keep_intermediate:
        print(f"\n[提示] 中间文件将在翻译完成后自动清理（使用 --keep-intermediate 保留）")


if __name__ == '__main__':
    main()
