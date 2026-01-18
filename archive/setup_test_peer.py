"""
Quick Peer Discovery Test
Creates a second transceiver instance for testing
"""

import os
import sys
import shutil

def setup_test_peer():
    """Setup a second peer instance for testing"""
    
    print("\n" + "="*60)
    print("LayerX Peer Discovery Test Setup")
    print("="*60)
    
    test_dir = "test_peer_instance"
    
    if os.path.exists(test_dir):
        print(f"\n[!] Test directory already exists: {test_dir}")
        response = input("Delete and recreate? (y/n): ").strip().lower()
        if response == 'y':
            shutil.rmtree(test_dir)
        else:
            print("[*] Using existing test directory")
            print(f"[*] cd {test_dir}")
            print(f"[*] python transceiver.py")
            return
    
    print(f"\n[*] Creating test directory: {test_dir}")
    os.makedirs(test_dir, exist_ok=True)
    
    # Copy necessary files
    files_to_copy = [
        'transceiver.py',
        'a1_encryption.py',
        'a2_key_management.py', 
        'a3_image_processing_color.py',
        'a3_image_processing.py',
        'a4_compression.py',
        'a5_embedding_extraction.py',
        'a6_optimization.py',
        'a7_communication.py',
        'requirements.txt'
    ]
    
    print("[*] Copying files...")
    for filename in files_to_copy:
        if os.path.exists(filename):
            shutil.copy2(filename, test_dir)
            print(f"    ✓ {filename}")
    
    # Copy core_modules directory
    if os.path.exists('core_modules'):
        print("[*] Copying core_modules...")
        shutil.copytree('core_modules', os.path.join(test_dir, 'core_modules'), dirs_exist_ok=True)
        print("    ✓ core_modules/")
    
    # Create necessary directories
    os.makedirs(os.path.join(test_dir, 'received_images'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'keys'), exist_ok=True)
    
    print("\n" + "="*60)
    print("✓ Test instance created successfully!")
    print("="*60)
    print("\nNow follow these steps:")
    print("\n1. Open a NEW terminal window")
    print(f"2. cd {test_dir}")
    print("3. python transceiver.py")
    print("4. Enter a DIFFERENT username (e.g., 'Alice', 'Bob', 'Test2')")
    print("\n5. In your ORIGINAL terminal, type: peers")
    print("   You should see the new peer discovered!")
    print("\n" + "="*60)
    
    # Show current instance info
    if os.path.exists('my_identity.json'):
        import json
        with open('my_identity.json', 'r') as f:
            identity = json.load(f)
            print(f"\nCurrent instance: {identity['username']}")
            print(f"Address: {identity['address']}")
            print("\nMake sure the new instance uses a DIFFERENT username!")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        setup_test_peer()
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
