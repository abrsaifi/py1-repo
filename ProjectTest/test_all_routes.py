import urllib.request
import urllib.error

routes = [
    ('http://localhost:5000/', 'Home'),
    ('http://localhost:5000/conversion?tool=To%20PDF', 'Conversion'),
    ('http://localhost:5000/tools', 'Tools')
]

print('Route Status Check:')
print('-' * 50)
for url, name in routes:
    try:
        response = urllib.request.urlopen(url)
        status = response.status
        ctype = response.headers.get('Content-Type', '')
        ctype_short = ctype.split(';')[0]
        print(f'{name:12} - Status: {status} - {ctype_short}')
    except Exception as e:
        print(f'{name:12} - ERROR: {str(e)[:50]}')
