import urllib.request
import urllib.error
import sys

try:
    url = 'http://localhost:5000/conversion?tool=To%20PDF'
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    
    print(f'Status Code: {response.status}')
    print(f'Content Type: {response.headers.get("Content-Type")}')
    
    # Check if we got HTML or error JSON
    if response.status == 200 and 'text/html' in response.headers.get('Content-Type', ''):
        if 'endblock' in content.lower() or '"error"' in content.lower():
            print('❌ FAILED: Still has Jinja2 error')
            print(content[:500])
        else:
            print('✅ SUCCESS: Page loads without Jinja2 errors')
            print(f'Content length: {len(content)} chars')
    else:
        print('First 500 chars:')
        print(content[:500])
except urllib.error.HTTPError as e:
    print(f'HTTP Error {e.code}: {e.reason}')
    print(e.read().decode('utf-8')[:500])
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
