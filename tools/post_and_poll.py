"""Post a generated CSV to /api/convert/start, poll status, download result, and report sizes."""
import os
import tempfile
import time
import json
import requests


def generate_csv(path, target_bytes=600*1024, cols=8):
    header = [f"col{i+1}" for i in range(cols)]
    row = ["Sample text with numbers 1234567890 and some extra words" for _ in range(cols)]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(','.join(header) + '\n')
        size = f.tell()
        while size < target_bytes:
            f.write(','.join(row) + '\n')
            size = f.tell()


def post_and_wait(server_url='http://localhost:5000'):
    tmpdir = tempfile.mkdtemp(prefix='csvpost_')
    csv_path = os.path.join(tmpdir, 'upload.csv')
    generate_csv(csv_path)

    print('Posting CSV to server...')
    files = {'files': open(csv_path, 'rb')}
    data = {'tool_name': 'To PDF', 'use_simple_renderer': 'false'}

    try:
        resp = requests.post(f'{server_url}/api/convert/start', files=files, data=data, timeout=30)
    except Exception as e:
        print('POST error:', e)
        return

    print('Start response:', resp.status_code, resp.text)
    try:
        j = resp.json()
    except Exception:
        print('Invalid JSON response')
        return

    if not j.get('success'):
        print('Server returned error:', j.get('error'))
        return

    job_id = j.get('job_id')
    print('Job ID:', job_id)

    # Poll status
    status = None
    for _ in range(120):  # up to 2 minutes
        try:
            s = requests.get(f'{server_url}/api/convert/status/{job_id}', timeout=10)
            sj = s.json()
        except Exception as e:
            print('Status poll error:', e)
            time.sleep(1)
            continue

        print('Status:', sj.get('status'), 'progress:', sj.get('progress'))
        status = sj.get('status')
        if status == 'complete':
            files_list = sj.get('files', [])
            if not files_list:
                print('Complete but no files returned')
                return

            # Download all returned files (PDF + any logs)
            for fmeta in files_list:
                download_url = fmeta.get('download_url')
                name = fmeta.get('name') or os.path.basename(download_url or '')
                if not download_url:
                    continue
                dl = requests.get(f'{server_url}{download_url}', stream=True, timeout=60)
                out_path = os.path.join(tmpdir, name)
                with open(out_path, 'wb') as out_f:
                    for chunk in dl.iter_content(8192):
                        out_f.write(chunk)

                print(f'Downloaded result: {out_path} ({os.path.getsize(out_path)} bytes)')
                if out_path.endswith('.log'):
                    print('--- LIBREOFFICE LOG START ---')
                    try:
                        with open(out_path, 'r', encoding='utf-8', errors='ignore') as rl:
                            print(rl.read())
                    except Exception as e:
                        print('Could not read log file:', e)
                    print('--- LIBREOFFICE LOG END ---')

            in_size = os.path.getsize(csv_path)
            # Find the first downloaded PDF to report ratio
            pdf_files = [os.path.join(tmpdir, f['name']) for f in files_list if f['name'].lower().endswith('.pdf')]
            if pdf_files:
                out_size = os.path.getsize(pdf_files[0])
                print(f'Input CSV: {csv_path} ({in_size} bytes)')
                print(f'Primary PDF: {pdf_files[0]} ({out_size} bytes)')
                print(f'Ratio out/in: {out_size/in_size:.2f}')
            return

        elif status == 'error':
            print('Job error:', sj.get('error'))
            return

        time.sleep(1)

    print('Timeout waiting for job completion')


if __name__ == '__main__':
    post_and_wait()
