"""
Quick script to copy all required files to a folder for sharing with peer
Run this to prepare files for USB/network transfer
"""

import os
import shutil
from pathlib import Path

def create_peer_package():
    """Create a folder with all files needed for peer device"""
    
    # Required files
    required_files = [
        'a1_encryption.py',
        'a2_key_management.py',
        'a3_image_processing.py',
        'a4_compression.py',
        'a5_embedding_extraction.py',
        'a6_optimization.py',
        'a7_communication.py',
        'sender.py',
        'receiver.py',
        'requirements.txt',
        'cover.png'
    ]
    
    # Create output folder
    output_dir = 'LAYERX_PEER_PACKAGE'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    print(f"\n{'='*70}")
    print("CREATING PEER PACKAGE")
    print(f"{'='*70}\n")
    
    copied = 0
    missing = []
    
    for filename in required_files:
        if os.path.exists(filename):
            shutil.copy2(filename, output_dir)
            size = os.path.getsize(filename)
            print(f"[+] Copied: {filename:<30} ({size:>7,} bytes)")
            copied += 1
        else:
            print(f"[!] Missing: {filename}")
            missing.append(filename)
    
    # Create README in package
    readme_content = """# LayerX Steganographic Security Framework - Peer Package

## Quick Start

1. Install dependencies:
   pip install -r requirements.txt

2. Run sender (to send messages):
   python sender.py

3. Run receiver (to receive messages):
   python receiver.py

## Requirements
- Python 3.11+
- Same network as other peer (WiFi/LAN)
- Port 37020 open (UDP)

## Files Included
- 7 core modules (a1-a7.py)
- sender.py & receiver.py
- requirements.txt
- cover.png (sample cover image)

## First Run
- Program will create my_identity.json automatically
- Wait 5-10 seconds for peer discovery
- Peers will appear in list automatically

## Sending Messages
1. Run sender.py
2. Wait for peer to appear
3. Choose 'send' command
4. Select recipient
5. Type message
6. Copy stego image to receiver device

## Receiving Messages  
1. Run receiver.py
2. Choose 'receive' command
3. Enter stego image path
4. Enter salt/IV from sender
5. Enter payload size
6. Message will be decrypted and displayed

## Network Setup
Both devices must be on SAME network!
Check IP: ipconfig (Windows) or ifconfig (Linux/Mac)

## Troubleshooting
- No peers? Wait 15 seconds, check network
- Module errors? Run: pip install -r requirements.txt
- Cover.png missing? Any 512x512 PNG works

## Support
See full documentation in main repository.

Team 08 - CSE(CIC) IV Year Project
Guide: Mr. O. T. GOPI KRISHNA
"""
    
    with open(os.path.join(output_dir, 'README.txt'), 'w') as f:
        f.write(readme_content)
    print(f"[+] Created: README.txt")
    
    # Create setup script for Windows
    setup_bat = """@echo off
echo ============================================
echo LayerX Setup Script
echo ============================================
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Dependencies installed!
    echo.
    echo Ready to run:
    echo   python sender.py   ^(send messages^)
    echo   python receiver.py ^(receive messages^)
) else (
    echo [ERROR] Installation failed!
    echo Please install Python 3.11+ and try again.
)
echo.
pause
"""
    
    with open(os.path.join(output_dir, 'setup.bat'), 'w') as f:
        f.write(setup_bat)
    print(f"[+] Created: setup.bat (Windows setup script)")
    
    # Create setup script for Linux/Mac
    setup_sh = """#!/bin/bash
echo "============================================"
echo "LayerX Setup Script"
echo "============================================"
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Dependencies installed!"
    echo ""
    echo "Ready to run:"
    echo "  python sender.py   (send messages)"
    echo "  python receiver.py (receive messages)"
else
    echo ""
    echo "[ERROR] Installation failed!"
    echo "Please install Python 3.11+ and try again."
fi
echo ""
"""
    
    with open(os.path.join(output_dir, 'setup.sh'), 'w') as f:
        f.write(setup_sh)
    
    # Make setup.sh executable on Unix systems
    try:
        os.chmod(os.path.join(output_dir, 'setup.sh'), 0o755)
    except:
        pass
    
    print(f"[+] Created: setup.sh (Linux/Mac setup script)")
    
    # Summary
    print(f"\n{'='*70}")
    print("PACKAGE SUMMARY")
    print(f"{'='*70}")
    print(f"Files copied: {copied}/{len(required_files)}")
    if missing:
        print(f"\nMissing files:")
        for f in missing:
            print(f"  - {f}")
            if f == 'cover.png':
                print(f"    (Will be auto-created on first run)")
    
    print(f"\nPackage location: ./{output_dir}/")
    print(f"\nNext steps:")
    print(f"  1. Copy '{output_dir}' folder to USB/network drive")
    print(f"  2. Transfer to other device")
    print(f"  3. On other device, run 'setup.bat' (Windows) or 'setup.sh' (Linux/Mac)")
    print(f"  4. Run 'python sender.py' or 'python receiver.py'")
    print(f"{'='*70}\n")
    
    # Create cover.png if missing
    if 'cover.png' in missing:
        print(f"[*] Creating sample cover.png...")
        try:
            import cv2
            import numpy as np
            img = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
            cv2.imwrite(os.path.join(output_dir, 'cover.png'), img)
            print(f"[+] Created: cover.png (512x512 sample image)")
        except Exception as e:
            print(f"[!] Could not create cover.png: {e}")
            print(f"[!] Please copy a PNG image manually")

if __name__ == '__main__':
    create_peer_package()
