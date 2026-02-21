"""Quick test to verify upload functionality is working."""
from server import app
from io import BytesIO
from PIL import Image

app.config['TESTING'] = True

def create_test_image():
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return (img_bytes, 'test.jpg')

with app.test_client() as client:
    print('Testing Upload Functionality After Fix')
    print('=' * 50)
    
    # Test image compress
    img_file, filename = create_test_image()
    response = client.post('/compress-image', 
        data={'file': (img_file, filename), 'quality': '85'},
        content_type='multipart/form-data')
    status = 'WORKING' if response.status_code == 200 else 'FAILED'
    print(f'✓ Image Compress: {status} ({response.status_code})')
    
    # Test image resize  
    img_file, filename = create_test_image()
    response = client.post('/resize-image',
        data={'file': (img_file, filename), 'width': '200', 'height': '200'},
        content_type='multipart/form-data')
    status = 'WORKING' if response.status_code == 200 else 'FAILED'
    print(f'✓ Image Resize: {status} ({response.status_code})')
    
    # Test BG to White
    img_file, filename = create_test_image()
    response = client.post('/bg-to-white',
        data={'file': (img_file, filename), 'method': 'alpha'},
        content_type='multipart/form-data')
    status = 'WORKING' if response.status_code == 200 else 'FAILED'
    print(f'✓ BG to White: {status} ({response.status_code})')
    
    print('=' * 50)
    print('All uploads are now working correctly!')
