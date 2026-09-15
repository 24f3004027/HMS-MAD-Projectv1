import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "PulseCare HMS — Technical Project Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "IIT Madras BS Degree — PulseCare HMS (GNU GPLv3)")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)

        self.restoreState()

def build_pdf(md_filepath, pdf_filepath):
    with open(md_filepath, "r", encoding="utf-8") as f:
        content = f.read()

    doc = SimpleDocTemplate(
        pdf_filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0284c7")
    SECONDARY = colors.HexColor("#0f172a")
    ACCENT = colors.HexColor("#0d9488")
    TEXT_MAIN = colors.HexColor("#1e293b")
    BG_LIGHT = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        alignment=0,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "ReportH1",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=SECONDARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "ReportH2",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "ReportBody",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_MAIN,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        "ReportCode",
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=8
    )

    flowables = []

    lines = content.split("\n")
    in_code_block = False
    code_lines = []
    in_table = False
    table_data = []

    for line in lines:
        stripped = line.strip()

        # Handle Code Blocks
        if stripped.startswith("```"):
            if in_code_block:
                code_text = "\n".join(code_lines)
                flowables.append(Paragraph(code_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(stripped)
            continue

        # Handle Tables
        if "|" in stripped and stripped.startswith("|"):
            if "---" in stripped:
                continue
            cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
            if cells:
                table_data.append(cells)
                in_table = True
            continue
        elif in_table:
            if table_data:
                formatted_table_data = []
                for row_idx, row in enumerate(table_data):
                    formatted_row = []
                    for cell in row:
                        cell_p_style = ParagraphStyle(
                            "TableCell",
                            parent=body_style,
                            fontSize=9,
                            leading=11,
                            fontName="Helvetica-Bold" if row_idx == 0 else "Helvetica",
                            textColor=colors.white if row_idx == 0 else TEXT_MAIN
                        )
                        formatted_row.append(Paragraph(cell, cell_p_style))
                    formatted_table_data.append(formatted_row)

                t = Table(formatted_table_data, colWidths=None)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ]))
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 8))
            table_data = []
            in_table = False

        if not stripped:
            continue

        # Headings
        if stripped.startswith("# "):
            flowables.append(Paragraph(stripped[2:], title_style))
            flowables.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=4, spaceAfter=12))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(stripped[3:], h1_style))
            flowables.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceBefore=2, spaceAfter=6))
        elif stripped.startswith("### "):
            flowables.append(Paragraph(stripped[4:], h2_style))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            text = stripped[2:]
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', text)
            flowables.append(Paragraph(f"• {text}", bullet_style))
        else:
            text = stripped
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', text)
            text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<font color="#0284c7"><u>\1</u></font>', text)
            flowables.append(Paragraph(text, body_style))

    doc.build(flowables, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF report: {pdf_filepath}")

if __name__ == "__main__":
    md_path = "/Users/ramrupsatpati/Documents/HMS-MAD-Projectv1/report.md"
    pdf_path = "/Users/ramrupsatpati/Documents/HMS-MAD-Projectv1/report.pdf"
    build_pdf(md_path, pdf_path)
