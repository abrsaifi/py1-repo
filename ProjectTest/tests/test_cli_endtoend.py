import os
import tempfile

from click.testing import CliRunner

import app.cli as cli


def create_simple_pdf(path):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(path, pagesize=letter)
    c.drawString(100, 750, "Test PDF for CLI end-to-end")
    c.save()


def test_cli_end_to_end(tmp_path):
    runner = CliRunner()

    in_pdf = tmp_path / "input_test.pdf"
    out_pdf = tmp_path / "output_test.pdf"

    create_simple_pdf(str(in_pdf))

    result = runner.invoke(cli.pdf_to_true_bw, [str(in_pdf), str(out_pdf), "--dpi", "100", "--threshold", "128"])

    assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
    assert out_pdf.exists(), "Output PDF was not created"
    assert out_pdf.stat().st_size > 0, "Output PDF is empty"
