"""Generate a CSV (~600KB), convert it to PDF using csv_to_pdf, and report sizes."""
import os
import tempfile
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen.canvas import Canvas


def csv_to_pdf(csv_path, output_pdf, **kwargs):
    try:
        import csv as _csv
        # Read CSV file
        data = []
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = _csv.reader(f)
            for row in reader:
                if any(row):
                    data.append(row)

        if not data:
            return False

        orientation = kwargs.get('orientation', 'landscape').lower()
        pagesize = landscape(A4) if orientation == 'landscape' else A4

        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=pagesize,
            topMargin=20*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        num_cols = len(data[0]) if data else 1
        available_width = pagesize[0] - 40*mm
        col_width = max(10*mm, available_width / max(1, num_cols))

        base_font_size = 9
        if num_cols > 8:
            base_font_size = 7
        elif num_cols > 5:
            base_font_size = 8

        para_style = ParagraphStyle(
            name='Cell',
            fontName='Helvetica',
            fontSize=base_font_size,
            leading=base_font_size + 1,
            wordWrap='LTR'
        )

        wrapped_data = []
        for row in data:
            wrapped_row = []
            for cell in row:
                text = '' if cell is None else str(cell)
                text = text.replace('\t', '    ')
                wrapped_row.append(Paragraph(text, para_style))
            wrapped_data.append(wrapped_row)

        table = Table(wrapped_data, colWidths=[col_width] * num_cols, repeatRows=1)

        style_commands = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), base_font_size),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]

        table.setStyle(TableStyle(style_commands))

        class CompressingCanvas(Canvas):
            def __init__(self, *a, **kw):
                Canvas.__init__(self, *a, **kw)
                try:
                    self.setPageCompression(1)
                except Exception:
                    pass

        elements = [table]
        doc.build(elements, canvasmaker=CompressingCanvas)

        return os.path.exists(output_pdf)
    except Exception as e:
        print('csv_to_pdf error:', e)
        return False


def generate_csv(path, target_bytes=600*1024, cols=8):
    header = [f"col{i+1}" for i in range(cols)]
    row = ["Sample text with numbers 1234567890 and some extra words" for _ in range(cols)]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(','.join(header) + '\n')
        size = f.tell()
        while size < target_bytes:
            f.write(','.join(row) + '\n')
            size = f.tell()


def run_test():
    tmpdir = tempfile.mkdtemp(prefix='csvtest_')
    csv_path = os.path.join(tmpdir, 'test_input.csv')
    pdf_path = os.path.join(tmpdir, 'test_output.pdf')

    print('Generating CSV (~600KB)...')
    generate_csv(csv_path)
    in_size = os.path.getsize(csv_path)
    print(f'Input CSV: {csv_path} ({in_size} bytes)')

    print('Converting to PDF using csv_to_pdf...')
    ok = csv_to_pdf(csv_path, pdf_path)
    if not ok:
        print('csv_to_pdf returned False (conversion failed)')
        return

    out_size = os.path.getsize(pdf_path)
    print(f'Output PDF: {pdf_path} ({out_size} bytes)')

    # Basic heuristic: if PDF > 5x CSV size, warn
    ratio = out_size / max(in_size, 1)
    print(f'Output/Input size ratio: {ratio:.2f}')
    if ratio > 5:
        print('WARNING: PDF is significantly larger than CSV; consider compression or alternate renderers')


if __name__ == '__main__':
    run_test()
