"""
Automated Viewer Feature Testing - Functional Approach
Tests viewer functionality without GUI instantiation
"""

import os
import sys
from pathlib import Path

print("="*70)
print("   LAYERX VIEWER FEATURE TESTING (Functional)")
print("="*70)

# Test 1: File System Check
print("\n[TEST 1] File System Verification")
print("-" * 70)
receiver_dir = Path("H:/Layerx TEST")
sender_dir = Path("H:/LAYERX")

png_files = list(receiver_dir.glob("*.png"))
json_files = list(receiver_dir.glob("*.json"))
metadata_files = [f for f in json_files if not f.name in ['my_identity.json', 'message_history.json']]

print(f"  📁 Receiver directory: {receiver_dir}")
print(f"  📁 PNG images: {len(png_files)}")
print(f"  📄 JSON files: {len(json_files)}")
print(f"  📄 Metadata files: {len(metadata_files)}")

test1_pass = len(png_files) > 0
print(f"  {'✅' if test1_pass else '❌'} Images available for testing")

# Test 2: Module Import
print("\n[TEST 2] Viewer Module Import")
print("-" * 70)
try:
    sys.path.insert(0, str(sender_dir))
    import stego_viewer
    print("  ✅ stego_viewer module imported")
    
    # Check for key functions/classes in the module
    module_contents = dir(stego_viewer)
    print(f"  ✅ Module has {len(module_contents)} objects")
    
    # Check for specific attributes we expect
    expected_items = ['tk', 'ttk', 'Image', 'messagebox']
    found_items = [item for item in expected_items if item in module_contents]
    print(f"  ✅ Found {len(found_items)}/{len(expected_items)} expected imports")
    
    test2_pass = True
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    test2_pass = False

# Test 3: Image File Integrity
print("\n[TEST 3] Image File Integrity")
print("-" * 70)
try:
    from PIL import Image
    valid_images = 0
    
    for png_file in png_files:
        try:
            img = Image.open(png_file)
            w, h = img.size
            mode = img.mode
            size_kb = png_file.stat().st_size / 1024
            print(f"  ✅ {png_file.name}: {w}x{h} {mode} ({size_kb:.1f} KB)")
            valid_images += 1
        except Exception as e:
            print(f"  ❌ {png_file.name}: {e}")
    
    test3_pass = valid_images == len(png_files)
    print(f"\n  {valid_images}/{len(png_files)} images valid")
except Exception as e:
    print(f"  ❌ Image verification failed: {e}")
    test3_pass = False

# Test 4: PIN File Check
print("\n[TEST 4] PIN Authentication System")
print("-" * 70)
try:
    pin_file = sender_dir / "layerx_pin.txt"
    if pin_file.exists():
        pin = pin_file.read_text().strip()
        print(f"  ✅ PIN file exists")
        print(f"  ✅ PIN length: {len(pin)} characters")
        print(f"  ✅ PIN value: {'*' * len(pin)}")
        test4_pass = len(pin) >= 4
    else:
        print(f"  ⚠️  PIN file not found - using default (1234)")
        test4_pass = True
except Exception as e:
    print(f"  ❌ PIN check failed: {e}")
    test4_pass = False

# Test 5: File Naming Format
print("\n[TEST 5] File Naming Convention")
print("-" * 70)
import re

# Pattern matches: username_YYYYMMDD_HHMMSS_address.png
# Address can be IP (169_254_88_214) or hex ID (8D0229E6FB1F3F01)
new_format = re.compile(r'^[a-zA-Z0-9_]+_\d{8}_\d{6}_[a-zA-Z0-9_]+\.png$')
old_format = re.compile(r'^received_stego_\d{8}_\d{6}\.png$')

new_format_count = 0
old_format_count = 0
unknown_format = 0

for png_file in png_files:
    if new_format.match(png_file.name):
        print(f"  ✅ {png_file.name} - NEW format")
        new_format_count += 1
    elif old_format.match(png_file.name):
        print(f"  ⚠️  {png_file.name} - OLD format")
        old_format_count += 1
    else:
        print(f"  ❌ {png_file.name} - UNKNOWN format")
        unknown_format += 1

print(f"\n  New format: {new_format_count}")
print(f"  Old format: {old_format_count}")
print(f"  Unknown: {unknown_format}")

test5_pass = new_format_count > 0 or old_format_count > 0

# Test 6: Metadata Pairing
print("\n[TEST 6] Image-Metadata Pairing")
print("-" * 70)
paired_count = 0

for png_file in png_files:
    json_file = png_file.with_suffix('.json')
    if json_file.exists():
        print(f"  ✅ {png_file.name} ↔ {json_file.name}")
        paired_count += 1
    else:
        # Try old format pairing
        base_name = png_file.stem
        possible_json = receiver_dir / f"{base_name}.json"
        if possible_json.exists():
            print(f"  ✅ {png_file.name} ↔ {possible_json.name}")
            paired_count += 1
        else:
            print(f"  ❌ {png_file.name} - No metadata")

test6_pass = paired_count > 0
print(f"\n  {paired_count}/{len(png_files)} images paired with metadata")

# Test 7: Viewer Script Existence
print("\n[TEST 7] Required Scripts")
print("-" * 70)
required_scripts = {
    'stego_viewer.py': sender_dir / 'stego_viewer.py',
    'receiver_secure.py': sender_dir / 'receiver_secure.py',
    'sender_secure.py': sender_dir / 'sender_secure.py',
    'set_pin.py': sender_dir / 'set_pin.py',
}

scripts_found = 0
for name, path in required_scripts.items():
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"  ✅ {name} ({size_kb:.1f} KB)")
        scripts_found += 1
    else:
        print(f"  ❌ {name} - Missing")

test7_pass = scripts_found == len(required_scripts)

# Test 8: Keyboard Shortcut Configuration
print("\n[TEST 8] Feature Implementation Check")
print("-" * 70)
try:
    viewer_code = (sender_dir / 'stego_viewer.py').read_text(encoding='utf-8', errors='ignore')
    
    features = {
        'Keyboard Shortcuts': 'setup_keyboard_shortcuts',
        'PSNR Display': 'update_psnr_display',
        'Self-Destruct Timer': 'start_destruction_timer',
        'Metadata Inspector': 'show_image_metadata',
        'PIN Authentication': 'authenticate_and_reveal',
        'Recent Files': 'load_recent_files',
        'Theme Toggle': 'toggle_theme',
        'Drag & Drop': 'on_image_drop',
    }
    
    implemented = 0
    for feature, method in features.items():
        if f'def {method}' in viewer_code:
            print(f"  ✅ {feature}")
            implemented += 1
        else:
            print(f"  ❌ {feature} - Not found")
    
    test8_pass = implemented >= 6  # At least 6 features
    print(f"\n  {implemented}/{len(features)} features implemented")
except Exception as e:
    print(f"  ❌ Code check failed: {e}")
    test8_pass = False

# Test 9: Dependencies Check
print("\n[TEST 9] Python Dependencies")
print("-" * 70)
dependencies = {
    'tkinter': 'GUI framework',
    'PIL': 'Image processing',
    'cryptography': 'Encryption',
    'cv2': 'Computer vision',
    'numpy': 'Numerical arrays',
    'pywt': 'Wavelet transforms',
}

deps_available = 0
for module, description in dependencies.items():
    try:
        __import__(module)
        print(f"  ✅ {module:15s} - {description}")
        deps_available += 1
    except ImportError:
        print(f"  ❌ {module:15s} - {description} (MISSING)")

test9_pass = deps_available >= 4  # Core dependencies

# Summary
print("\n" + "="*70)
print("   TEST SUMMARY")
print("="*70)

tests = [
    ("TC1 - File System", test1_pass),
    ("TC2 - Module Import", test2_pass),
    ("TC3 - Image Integrity", test3_pass),
    ("TC4 - PIN Authentication", test4_pass),
    ("TC5 - File Naming", test5_pass),
    ("TC6 - Metadata Pairing", test6_pass),
    ("TC7 - Required Scripts", test7_pass),
    ("TC8 - Feature Implementation", test8_pass),
    ("TC9 - Dependencies", test9_pass),
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} - {name}")

print("="*70)
percentage = (passed/total*100)
print(f"\nOVERALL: {passed}/{total} tests passed ({percentage:.1f}%)")

if passed == total:
    print("🎉 All tests passed!")
elif percentage >= 70:
    print("✅ System functional - some issues detected")
else:
    print("⚠️  Critical issues detected")

print("\n💡 To test GUI features, run:")
print("   python stego_viewer.py")
print("\n💡 To send new test messages, run:")
print("   python sender_secure.py")

print("="*70)
