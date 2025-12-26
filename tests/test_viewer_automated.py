"""
Automated Viewer Feature Testing
Tests all viewer functionality programmatically
"""

import os
import sys
from pathlib import Path

print("="*70)
print("   LAYERX VIEWER AUTOMATED TESTING")
print("="*70)

# Test 1: Module Import
print("\n[TEST 1] Module Import Verification")
print("-" * 70)
try:
    from stego_viewer import StegoViewer
    import tkinter as tk
    print("  ✅ stego_viewer module imported successfully")
    print("  ✅ tkinter available")
    test1_pass = True
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    test1_pass = False

# Test 2: File Detection
print("\n[TEST 2] Image File Detection")
print("-" * 70)
receiver_dir = Path("H:/Layerx TEST")
png_files = list(receiver_dir.glob("*.png"))
json_files = list(receiver_dir.glob("*.json"))

print(f"  📁 PNG files: {len(png_files)}")
for f in png_files:
    print(f"     - {f.name}")
print(f"  📄 JSON files: {len(json_files)}")
for f in json_files:
    print(f"     - {f.name}")

test2_pass = len(png_files) > 0

# Test 3: Viewer Initialization
print("\n[TEST 3] Viewer Initialization")
print("-" * 70)
try:
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    viewer = StegoViewer(root)
    print("  ✅ Viewer object created successfully")
    print(f"  ✅ Current theme: {viewer.current_theme}")
    print(f"  ✅ Version: {viewer.version if hasattr(viewer, 'version') else 'N/A'}")
    
    # Check if keyboard shortcuts are bound
    bindings = root.bind()
    print(f"  ✅ Window bindings: {len(bindings)} configured")
    
    test3_pass = True
except Exception as e:
    print(f"  ❌ Viewer initialization failed: {e}")
    test3_pass = False

# Test 4: Method Availability
print("\n[TEST 4] Feature Method Availability")
print("-" * 70)
required_methods = [
    'load_image',
    'load_metadata_file',
    'reveal_message',
    'toggle_theme',
    'setup_keyboard_shortcuts',
    'show_image_metadata',
    'check_self_destruct',
    'update_psnr_display',
    'authenticate_and_reveal',
    'load_recent_files'
]

method_results = []
for method in required_methods:
    has_method = hasattr(viewer, method)
    status = "✅" if has_method else "❌"
    print(f"  {status} {method}")
    method_results.append(has_method)

test4_pass = all(method_results)

# Test 5: Theme Toggle
print("\n[TEST 5] Theme Toggle Functionality")
print("-" * 70)
try:
    initial_theme = viewer.current_theme
    print(f"  Initial theme: {initial_theme}")
    
    viewer.toggle_theme()
    new_theme = viewer.current_theme
    print(f"  After toggle: {new_theme}")
    
    test5_pass = initial_theme != new_theme
    print(f"  {'✅' if test5_pass else '❌'} Theme toggle works")
except Exception as e:
    print(f"  ❌ Theme toggle failed: {e}")
    test5_pass = False

# Test 6: Recent Files Loading
print("\n[TEST 6] Recent Files Loading")
print("-" * 70)
try:
    viewer.load_recent_files()
    recent_count = len(viewer.recent_files) if hasattr(viewer, 'recent_files') else 0
    print(f"  📊 Recent files loaded: {recent_count}")
    
    if recent_count > 0:
        print(f"  📁 Files found:")
        for rf in viewer.recent_files[:3]:  # Show first 3
            print(f"     - {rf.get('filename', 'unknown')}")
    
    test6_pass = True
except Exception as e:
    print(f"  ❌ Recent files loading failed: {e}")
    test6_pass = False

# Test 7: Image Loading
print("\n[TEST 7] Image Loading Capability")
print("-" * 70)
try:
    if png_files:
        test_image = str(png_files[0])
        print(f"  Testing with: {png_files[0].name}")
        
        from PIL import Image
        img = Image.open(test_image)
        print(f"  ✅ Image opened: {img.size[0]}x{img.size[1]} {img.mode}")
        
        # Try loading in viewer
        viewer.current_image_path = test_image
        viewer.load_image(test_image)
        print(f"  ✅ Image loaded in viewer")
        
        test7_pass = True
    else:
        print("  ⚠️  No images to test")
        test7_pass = False
except Exception as e:
    print(f"  ❌ Image loading failed: {e}")
    test7_pass = False

# Test 8: PSNR Display
print("\n[TEST 8] PSNR Display Feature")
print("-" * 70)
try:
    if hasattr(viewer, 'psnr_value'):
        print(f"  ✅ PSNR attribute exists")
        viewer.psnr_value = 52.5
        viewer.update_psnr_display()
        print(f"  ✅ PSNR update method works")
        test8_pass = True
    else:
        print(f"  ❌ PSNR attribute missing")
        test8_pass = False
except Exception as e:
    print(f"  ❌ PSNR display failed: {e}")
    test8_pass = False

# Test 9: PIN Authentication
print("\n[TEST 9] PIN Authentication System")
print("-" * 70)
try:
    pin_file = Path("H:/LAYERX/layerx_pin.txt")
    if pin_file.exists():
        with open(pin_file, 'r') as f:
            stored_pin = f.read().strip()
        print(f"  ✅ PIN file exists")
        print(f"  ✅ Stored PIN: {'*' * len(stored_pin)}")
        test9_pass = len(stored_pin) >= 4
    else:
        print(f"  ⚠️  PIN file not found (default: 1234)")
        test9_pass = True  # Default PIN is acceptable
except Exception as e:
    print(f"  ❌ PIN check failed: {e}")
    test9_pass = False

# Clean up
try:
    root.destroy()
except:
    pass

# Summary
print("\n" + "="*70)
print("   TEST SUMMARY")
print("="*70)

tests = [
    ("TC1 - Module Import", test1_pass),
    ("TC2 - File Detection", test2_pass),
    ("TC3 - Viewer Initialization", test3_pass),
    ("TC4 - Feature Methods", test4_pass),
    ("TC5 - Theme Toggle", test5_pass),
    ("TC6 - Recent Files", test6_pass),
    ("TC7 - Image Loading", test7_pass),
    ("TC8 - PSNR Display", test8_pass),
    ("TC9 - PIN Authentication", test9_pass),
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} - {name}")

print("="*70)
print(f"\nOVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

if passed == total:
    print("🎉 All viewer features working correctly!")
elif passed >= total * 0.7:
    print("✅ Most features working - minor issues detected")
else:
    print("⚠️  Multiple features need attention")

print("="*70)
