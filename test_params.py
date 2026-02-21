import re

html_file = 'templates/Index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if SERVICE_PARAMETERS has 'To PDF' key
if "'To PDF'" in content:
    print('✅ "To PDF" found in SERVICE_PARAMETERS')
    
    # Count parameters for To PDF
    count = content.count("name: 'orientation'")
    print(f'✅ Found {count} reference to orientation param')
else:
    print('❌ "To PDF" NOT found in SERVICE_PARAMETERS')

# Check if function renderServiceSettings exists
if 'function renderServiceSettings' in content:
    print('✅ renderServiceSettings() function exists')
else:
    print('❌ renderServiceSettings() function NOT found')

print('\n--- Key checks ---')
print(f'Contains "To PDF": {"To PDF" in content}')
print(f'Contains "renderServiceSettings": {"renderServiceSettings" in content}')
print(f'Contains "presetsButtonGroup": {"presetsButtonGroup" in content}')
print(f'Contains preset event listener: {"addEventListener.*click.*Apply preset" in content}')
