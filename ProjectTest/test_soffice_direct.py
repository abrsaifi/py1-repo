#!/usr/bin/env python3
"""Detailed LibreOffice conversion diagnostic test."""

import sys
import os
import subprocess
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(__file__))

def test_soffice_directly():
    """Test soffice command directly."""
    print("=" * 70)
    print("LibreOffice (soffice) Direct Command Test")
    print("=" * 70)
    
    test_file = r'E:\OneDrive\Documents\py1\test_sample.xlsx'
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\nTest input: {test_file}")
        print(f"File exists: {os.path.exists(test_file)}")
        print(f"Output directory: {tmpdir}")
        
        soffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
        
        cmd = [
            soffice_path,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', tmpdir,
            test_file
        ]
        
        print(f"\nCommand: {' '.join(cmd)}")
        print(f"\nRunning conversion...")
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120, text=True)
            
            print(f"\nReturn code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            
            # Check what files were created
            files = os.listdir(tmpdir)
            print(f"\nFiles created in output dir: {files}")
            
            for f in files:
                fpath = os.path.join(tmpdir, f)
                fsize = os.path.getsize(fpath)
                print(f"  - {f} ({fsize} bytes)")
                
        except subprocess.TimeoutExpired:
            print("ERROR: LibreOffice conversion timed out (120 seconds)")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == '__main__':
    test_soffice_directly()
