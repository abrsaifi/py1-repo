import glob
import os

root = os.getenv('TEMP') or os.getenv('TMP') or 'C:\\Windows\\Temp'
found = []
# Search for temp dirs likely created by our tests
for d in glob.glob(os.path.join(root, '*csv*')) + glob.glob(os.path.join(root, '*csvpost*')) + glob.glob(os.path.join(root, '*csvtest*')):
    for f in glob.glob(os.path.join(d, 'libreoffice_*.log')):
        found.append(f)

# Also search workspace temp dirs
for d in glob.glob(os.path.join(os.getcwd(), 'tmp*')):
    for f in glob.glob(os.path.join(d, 'libreoffice_*.log')):
        found.append(f)

if not found:
    print('No libreoffice_*.log files found in temp dirs searched')
else:
    for f in found:
        print('--- LOG:', f)
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                data = fh.read()
                print(data)
        except Exception as e:
            print('Could not read', f, e)
