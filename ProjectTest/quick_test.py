import requests
import sys

try:
    response = requests.get('http://localhost:5000/conversion?tool=To%20PDF')
    print(f'Status Code: {response.status_code}')
    print(f'Content Type: {response.headers.get("content-type")}')
    
    # Check if we got HTML or error JSON
    if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
        print('✅ SUCCESS: Page loads without Jinja2 errors')
    elif 'endblock' in response.text.lower() or 'error' in response.text.lower():
        print('❌ FAILED: Still has Jinja2 error')
        print(response.text[:500])
    else:
        print('First 500 chars:')
        print(response.text[:500])
except Exception as e:
    print(f'Connection Error (server may not be running): {e}')
    sys.exit(1)
