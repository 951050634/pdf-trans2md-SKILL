#!/usr/bin/env python3
"""Generate a small synthetic double-column journal PDF for skill evaluation."""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

OUTPUT = Path(__file__).with_name("double_column_journal_fixture.pdf")
PAGE_W, PAGE_H = A4
MARGIN = 42
GUTTER = 20
COL_W = (PAGE_W - 2 * MARGIN - GUTTER) / 2


def wrap(text, font, size, width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = word if not current else current + " " + word
        if stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraph(c, text, x, y, width, font="Times-Roman", size=9, leading=11):
    c.setFont(font, size)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y - 5


def draw_footer(c, page):
    c.setFont("Helvetica", 7)
    c.setFillGray(0.45)
    c.drawCentredString(PAGE_W / 2, 24, f"Synthetic Journal Fixture | Page {page}")
    c.setFillGray(0)


def page_one(c):
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 48, "Vision-First Translation of Double-Column Papers")
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 66, "A. Researcher, B. Scientist, and C. Engineer")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, PAGE_H - 92, "Abstract—")
    abstract = (
        "This synthetic article evaluates a multimodal workflow that reads journal pages visually before translation. "
        "The experiment focuses on column order, cross-column figures, mathematical notation, and bilingual output."
    )
    y = draw_paragraph(c, abstract, MARGIN + 48, PAGE_H - 92, PAGE_W - 2 * MARGIN - 48, size=8.5, leading=10)
    c.line(MARGIN, y + 2, PAGE_W - MARGIN, y + 2)

    top = y - 16
    lx = MARGIN
    rx = MARGIN + COL_W + GUTTER

    c.setFont("Helvetica-Bold", 10)
    c.drawString(lx, top, "1. INTRODUCTION")
    ly = top - 15
    ly = draw_paragraph(
        c,
        "The left column begins the main argument. Conventional text extraction may interleave lines from adjacent columns and detach captions from their figures. A vision-first model should inspect the complete page before reading any cropped region.",
        lx,
        ly,
        COL_W,
    )
    ly = draw_paragraph(
        c,
        "The workflow first identifies the title, abstract, body columns, figures, tables, equations, and footnotes. It then reads this entire left column from top to bottom before moving to the right column.",
        lx,
        ly,
        COL_W,
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawString(lx, ly, "2. METHOD")
    ly -= 15
    ly = draw_paragraph(
        c,
        "Each page is rendered at sufficient resolution. Small typography may require a higher-DPI crop, but the full-page image remains the source of layout truth. Uncertain characters are marked for review instead of being guessed.",
        lx,
        ly,
        COL_W,
    )
    ly = draw_paragraph(
        c,
        "A temporary terminology table keeps domain-specific phrases consistent across batches. Mathematical variables, software names, API identifiers, and digital object identifiers remain unchanged.",
        lx,
        ly,
        COL_W,
    )

    ry = top
    c.setFont("Helvetica-Bold", 10)
    c.drawString(rx, ry, "3. LAYOUT ANALYSIS")
    ry -= 15
    ry = draw_paragraph(
        c,
        "After the left column is complete, reading continues at the top of the right column. This sentence must therefore appear after the method discussion in any reconstructed Markdown output.",
        rx,
        ry,
        COL_W,
    )
    ry = draw_paragraph(
        c,
        "The model detects whether an object spans one column or both columns. Captions remain attached to their visual objects, while repeated headers, page numbers, and database watermarks are excluded.",
        rx,
        ry,
        COL_W,
    )

    fig_y = ry - 112
    c.setStrokeGray(0.25)
    c.rect(rx + 8, fig_y, COL_W - 16, 88)
    c.setFillColorRGB(0.25, 0.48, 0.75)
    c.rect(rx + 28, fig_y + 16, 28, 42, fill=1, stroke=0)
    c.setFillColorRGB(0.82, 0.43, 0.30)
    c.rect(rx + 74, fig_y + 16, 28, 61, fill=1, stroke=0)
    c.setFillColorRGB(0.35, 0.65, 0.42)
    c.rect(rx + 120, fig_y + 16, 28, 72, fill=1, stroke=0)
    c.setFillGray(0)
    c.setFont("Helvetica", 7)
    c.drawString(rx + 30, fig_y + 5, "Text")
    c.drawString(rx + 76, fig_y + 5, "OCR")
    c.drawString(rx + 117, fig_y + 5, "Vision")
    c.setStrokeGray(0)
    ry = fig_y - 12
    ry = draw_paragraph(
        c,
        "Figure 1. Reading-order accuracy for three input strategies. The visual workflow preserves the intended column sequence.",
        rx,
        ry,
        COL_W,
        font="Times-Italic",
        size=8,
        leading=9,
    )
    ry = draw_paragraph(
        c,
        "The figure caption belongs to Figure 1 and must not be merged into the surrounding body paragraph.",
        rx,
        ry,
        COL_W,
    )

    c.setFont("Times-Roman", 7)
    c.drawString(MARGIN, 46, "1 Footnote: This note follows the page body and should not interrupt either column.")
    draw_footer(c, 1)
    c.showPage()


def page_two(c):
    lx = MARGIN
    rx = MARGIN + COL_W + GUTTER
    top = PAGE_H - 50

    c.setFont("Helvetica-Bold", 10)
    c.drawString(lx, top, "4. RESULTS")
    ly = top - 15
    ly = draw_paragraph(
        c,
        "The second page continues in double-column format. The bilingual rendering places each original passage first and the Chinese translation in a Markdown quotation block immediately afterward.",
        lx,
        ly,
        COL_W,
    )
    ly = draw_paragraph(
        c,
        "For a page p, the layout-aware objective is defined below. The equation is preserved rather than translated, while its surrounding explanation is translated.",
        lx,
        ly,
        COL_W,
    )
    c.setFont("Times-Italic", 11)
    c.drawCentredString(lx + COL_W / 2, ly - 10, "L(p) = alpha C(p) + beta O(p) + gamma V(p)    (1)")
    ly -= 33
    ly = draw_paragraph(
        c,
        "Here C measures content coverage, O measures reading-order consistency, and V measures visual grounding. Higher values indicate a more reliable reconstruction.",
        lx,
        ly,
        COL_W,
    )

    c.setFont("Helvetica-Bold", 10)
    c.drawString(rx, top, "5. DISCUSSION")
    ry = top - 15
    ry = draw_paragraph(
        c,
        "The right column begins only after the left-column results have been read. This ordering assertion is deliberately explicit so automated evaluations can detect column interleaving.",
        rx,
        ry,
        COL_W,
    )
    ry = draw_paragraph(
        c,
        "Visual interpretation is especially useful for scanned articles and documents containing complex tables. A text backend remains available only when the user explicitly requests it.",
        rx,
        ry,
        COL_W,
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawString(rx, ry, "6. CONCLUSION")
    ry -= 15
    draw_paragraph(
        c,
        "Multimodal page reading provides a layout-faithful basis for Chinese Markdown translation. The workflow avoids silent fallback and exposes uncertainty whenever the source cannot be read reliably.",
        rx,
        ry,
        COL_W,
    )

    table_top = 248
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, table_top + 22, "TABLE 1. CROSS-COLUMN EVALUATION SUMMARY")
    widths = [150, 110, 110, 110]
    headers = ["Method", "Column order", "Figure link", "Bilingual rule"]
    rows = [
        ["Plain extraction", "Unstable", "Weak", "Variable"],
        ["Visual workflow", "Preserved", "Preserved", "Original first"],
    ]
    x = MARGIN
    y = table_top
    row_h = 22
    for width, header in zip(widths, headers):
        c.rect(x, y, width, row_h)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + width / 2, y + 7, header)
        x += width
    for row_index, row in enumerate(rows, 1):
        x = MARGIN
        row_y = y - row_h * row_index
        for width, value in zip(widths, row):
            c.rect(x, row_y, width, row_h)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + width / 2, row_y + 7, value)
            x += width

    c.setFont("Times-Italic", 8)
    c.drawString(MARGIN, table_top - 57, "The table spans both columns and must be inserted after the discussion rather than inside either column.")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, 130, "REFERENCES")
    c.setFont("Times-Roman", 7.5)
    c.drawString(MARGIN, 115, "[1] A. Author, 'Layout-aware document understanding,' Journal of Synthetic Tests, 2025.")
    c.drawString(MARGIN, 103, "[2] B. Author, 'Multimodal translation systems,' Proceedings of Example Research, 2026.")
    draw_footer(c, 2)
    c.showPage()


def main():
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, invariant=1)
    c.setTitle("Synthetic Double-Column Journal Fixture")
    page_one(c)
    page_two(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
