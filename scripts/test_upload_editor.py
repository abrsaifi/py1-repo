import requests, base64, json

b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
img = base64.b64decode(b64)
upload_id = f'editor-test-{int(__import__('time').time())}'
files = {'chunk': ('edited.png', img, 'image/png')}
form = {'upload_id': upload_id, 'filename':'edited.png', 'index':'0', 'total':'1'}
try:
    r = requests.post('http://127.0.0.1:5060/api/upload-chunk', data=form, files=files, timeout=10)
    print('upload-chunk', r.status_code, r.text[:400])
    conv = requests.post('http://127.0.0.1:5060/api/convert-uploaded', json={
        'tool_slug':'editor', 'uploads':[{'upload_id':upload_id,'filename':'edited.png'}], 'target_format':'pdf', 'parameters':{}
    }, timeout=10)
    print('convert-uploaded', conv.status_code, conv.text[:400])
except Exception as e:
    print('error', e)
