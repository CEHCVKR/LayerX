"""
Automated LayerX Feature Testing Script
Tests all features and generates a report
"""

import os
import sys
import time
import glob
from datetime import datetime

# Test configuration
RECEIVER_DIR = r"H:\Layerx TEST"
SENDER_DIR = r"H:\LAYERX"

print("="*70)
print("   LAYERX AUTOMATED FEATURE TESTING")
print("="*70)
print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Sender Directory: {SENDER_DIR}")
print(f"Receiver Directory: {RECEIVER_DIR}")
print("="*70)

# Test Case 1: Check file naming
print("\n[TEST 1] File Naming Verification")
print("-" * 70)
os.chdir(RECEIVER_DIR)

# Find received files
png_files = glob.glob("*.png")
json_files = glob.glob("*.json")

# Exclude system files from validation
system_files = ['my_identity.json', 'message_history.json']
json_files_to_check = [f for f in json_files if f not in system_files]

print(f"Found {len(png_files)} PNG files")
print(f"Found {len(json_files_to_check)} JSON metadata files (excluding system files)")

# Check naming format
import re
# Pattern: username_YYYYMMDD_HHMMSS_address.(png|json)
# Address can be IP (169_254_88_214) or hex ID (8D0229E6FB1F3F01)
naming_pattern = r'^[a-zA-Z0-9_]+_\d{8}_\d{6}_[a-zA-Z0-9_]+\.(png|json)$'

valid_names = 0
for file in png_files + json_files_to_check:
    if re.match(naming_pattern, file):
        valid_names += 1
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - Invalid format")

tc1_pass = valid_names == len(png_files) + len(json_files_to_check)
print(f"\n[TEST 1] {'✅ PASS' if tc1_pass else '❌ FAIL'} - {valid_names}/{len(png_files) + len(json_files)} files correctly named")

# Test Case 2: PSNR Verification from metadata
print("\n[TEST 2] PSNR Quality Check")
print("-" * 70)

import json

psnr_values = []
for json_file in json_files:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            metadata = data.get('metadata', {})
            psnr = metadata.get('psnr')
            if psnr:
                psnr_values.append((json_file, psnr))
                quality = "Excellent" if psnr > 50 else "Good" if psnr > 40 else "Fair"
                color = "🟢" if psnr > 50 else "🟡" if psnr > 40 else "🔴"
                print(f"  {color} {json_file[:30]}... PSNR: {psnr:.2f} dB ({quality})")
    except:
        pass

tc2_pass = all(psnr >= 40 for _, psnr in psnr_values)
avg_psnr = sum(p for _, p in psnr_values) / len(psnr_values) if psnr_values else 0
print(f"\n[TEST 2] {'✅ PASS' if tc2_pass else '❌ FAIL'} - Average PSNR: {avg_psnr:.2f} dB")

# Test Case 3: File Pairing
print("\n[TEST 3] Image-Metadata Pairing")
print("-" * 70)

paired = 0
for png in png_files:
    base_name = os.path.splitext(png)[0]
    json_pair = f"{base_name}.json"
    if os.path.exists(json_pair):
        paired += 1
        print(f"  ✅ {png} ↔ {json_pair}")
    else:
        print(f"  ❌ {png} - No matching JSON")

tc3_pass = paired == len(png_files)
print(f"\n[TEST 3] {'✅ PASS' if tc3_pass else '❌ FAIL'} - {paired}/{len(png_files)} files properly paired")

# Test Case 4: Metadata Structure
print("\n[TEST 4] Metadata Structure Validation")
print("-" * 70)

required_fields = ['salt', 'iv', 'payload_bits_length', 'sender_username', 'sender_address']
valid_metadata = 0

for json_file in json_files_to_check:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            metadata = data.get('metadata', {})
            
            has_all_fields = all(field in metadata for field in required_fields)
            if has_all_fields:
                valid_metadata += 1
                print(f"  ✅ {json_file[:40]}...")
            else:
                missing = [f for f in required_fields if f not in metadata]
                print(f"  ❌ {json_file[:40]}... Missing: {missing}")
    except Exception as e:
        print(f"  ❌ {json_file} - Error: {e}")

tc4_pass = valid_metadata == len(json_files_to_check)
print(f"\n[TEST 4] {'✅ PASS' if tc4_pass else '❌ FAIL'} - {valid_metadata}/{len(json_files_to_check)} valid metadata")

# Test Case 5: Sender Verification
print("\n[TEST 5] Sender Verification Check")
print("-" * 70)

verified_count = 0
for json_file in json_files_to_check:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            sender_verified = data.get('sender_verified', False)
            metadata = data.get('metadata', {})
            sender = metadata.get('sender_username', 'Unknown')
            
            if sender_verified:
                verified_count += 1
                print(f"  ✅ {json_file[:40]}... from {sender} (Verified)")
            else:
                print(f"  ⚠️  {json_file[:40]}... from {sender} (Not verified)")
    except:
        pass

tc5_pass = verified_count > 0
print(f"\n[TEST 5] {'✅ PASS' if tc5_pass else '⚠️  WARNING'} - {verified_count}/{len(json_files_to_check)} messages verified")

# Test Case 6: Self-Destruct Configuration
print("\n[TEST 6] Self-Destruct Configuration")
print("-" * 70)

sd_messages = 0
for json_file in json_files_to_check:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            metadata = data.get('metadata', {})
            sd = metadata.get('self_destruct')
            
            if sd:
                sd_messages += 1
                sd_type = sd.get('type', 'none')
                if sd_type == 'timer':
                    print(f"  ⏱️  {json_file[:40]}... Timer: {sd.get('minutes')} minutes")
                elif sd_type == 'view_count':
                    print(f"  👁️  {json_file[:40]}... Views: {sd.get('max_views')}")
                else:
                    print(f"  🔓 {json_file[:40]}... No self-destruct")
    except:
        pass

print(f"\n[TEST 6] ℹ️  INFO - {sd_messages}/{len(json_files_to_check)} messages have self-destruct enabled")

# Test Case 7: Image File Integrity
print("\n[TEST 7] Image File Integrity")
print("-" * 70)

from PIL import Image

valid_images = 0
for png in png_files:
    try:
        img = Image.open(png)
        width, height = img.size
        mode = img.mode
        
        if width > 0 and height > 0 and mode in ['RGB', 'RGBA', 'L']:
            valid_images += 1
            print(f"  ✅ {png[:40]}... {width}x{height} {mode}")
        else:
            print(f"  ❌ {png} - Invalid image properties")
        img.close()
    except Exception as e:
        print(f"  ❌ {png} - Error: {e}")

tc7_pass = valid_images == len(png_files)
print(f"\n[TEST 7] {'✅ PASS' if tc7_pass else '❌ FAIL'} - {valid_images}/{len(png_files)} valid images")

# Test Case 8: Capacity Analysis
print("\n[TEST 8] Embedding Capacity Analysis")
print("-" * 70)

for png in png_files[:3]:  # Check first 3
    try:
        img = Image.open(png)
        base_name = os.path.splitext(png)[0]
        json_file = f"{base_name}.json"
        
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
                metadata = data.get('metadata', {})
                payload_bits = metadata.get('payload_bits_length', 0)
                
                # Calculate capacity
                total_pixels = img.size[0] * img.size[1]
                channels = len(img.mode)
                capacity_bits = int(total_pixels * channels * 0.20)
                used_percent = (payload_bits / capacity_bits) * 100 if capacity_bits > 0 else 0
                
                print(f"  📊 {png[:30]}...")
                print(f"      Used: {payload_bits} bits ({used_percent:.1f}% of capacity)")
                print(f"      Remaining: {capacity_bits - payload_bits} bits")
        img.close()
    except:
        pass

print(f"\n[TEST 8] ℹ️  INFO - Capacity analysis complete")

# Summary
print("\n" + "="*70)
print("   TEST SUMMARY")
print("="*70)

tests = [
    ("TC1 - File Naming", tc1_pass),
    ("TC2 - PSNR Quality", tc2_pass),
    ("TC3 - File Pairing", tc3_pass),
    ("TC4 - Metadata Structure", tc4_pass),
    ("TC5 - Sender Verification", tc5_pass),
    ("TC7 - Image Integrity", tc7_pass),
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for test_name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} - {test_name}")

print("="*70)
print(f"\nOVERALL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")

if passed == total:
    print("🎉 ALL TESTS PASSED! System is working correctly.")
else:
    print("⚠️  Some tests failed. Review the output above.")

print("\n" + "="*70)
print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
