from pathlib import Path

from PIL import Image

from app.services.conversions import ConversionService


def test_conversion_service_resizes_images(tmp_path):
    input_path = tmp_path / 'input.png'
    output_path = tmp_path / 'output.png'

    Image.new('RGB', (40, 20), (255, 0, 0)).save(input_path)

    result = ConversionService.convert(
        str(input_path),
        'png',
        {
            'width': 10,
            'height': 8,
            'output_path': str(output_path),
        },
    )

    assert output_path.exists()
    assert result['output_path'] == str(output_path)

    with Image.open(output_path) as image:
        assert image.size == (10, 8)


def test_conversion_service_removes_background_when_tolerance_requested(tmp_path):
    input_path = tmp_path / 'input.png'
    output_path = tmp_path / 'transparent.png'

    image = Image.new('RGB', (12, 12), (255, 255, 255))
    for x in range(3, 9):
        for y in range(3, 9):
            image.putpixel((x, y), (255, 0, 0))
    image.save(input_path)

    ConversionService.convert(
        str(input_path),
        'png',
        {
            'tolerance': 10,
            'output_path': str(output_path),
        },
    )

    with Image.open(output_path) as converted:
        converted = converted.convert('RGBA')
        assert converted.getpixel((0, 0))[3] == 0
        assert converted.getpixel((5, 5))[3] == 255


def test_conversion_service_routes_pdf_to_docx(monkeypatch, tmp_path):
    input_path = tmp_path / 'input.pdf'
    output_path = tmp_path / 'output.docx'
    input_path.write_bytes(b'%PDF-1.4\n%stub\n')

    called = {}

    def fake_pdf_to_word(source, destination):
        called['source'] = source
        called['destination'] = destination
        Path(destination).write_bytes(b'docx-stub')
        return True

    import services.document_conversion as document_conversion

    monkeypatch.setattr(document_conversion, 'pdf_to_word', fake_pdf_to_word)

    result = ConversionService.convert(
        str(input_path),
        'docx',
        {'output_path': str(output_path)},
    )

    assert output_path.exists()
    assert called == {
        'source': str(input_path),
        'destination': str(output_path),
    }
    assert result['output_path'] == str(output_path)


def test_conversion_service_routes_excel_to_csv(tmp_path):
    input_path = tmp_path / 'input.xlsx'
    output_path = tmp_path / 'output.csv'

    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['name', 'value'])
    worksheet.append(['alpha', 1])
    workbook.save(input_path)
    workbook.close()

    result = ConversionService.convert(
        str(input_path),
        'csv',
        {'output_path': str(output_path)},
    )

    assert output_path.exists()
    assert 'alpha,1' in output_path.read_text(encoding='utf-8')
    assert result['output_path'] == str(output_path)
