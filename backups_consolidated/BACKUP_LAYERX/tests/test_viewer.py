"""
LayerX Viewer Feature Testing Script
Tests keyboard shortcuts, PSNR display, and other UI features
"""

import sys
import os

print("="*70)
print("   LAYERX VIEWER FEATURE TEST")
print("="*70)

print("""
This script will guide you through testing the viewer features.

🎯 **KEYBOARD SHORTCUTS TO TEST:**

1. Press Ctrl+I - Image Metadata Inspector (check terminal output)
2. Press Ctrl+T - Toggle Theme (Dark ↔ Light)
3. Press Ctrl+R - Reveal Message (asks for PIN: 1234)
4. Press Ctrl+Q - Quit Application
5. Press F5 - Refresh Recent Files

🔍 **VISUAL FEATURES TO VERIFY:**

1. PSNR Indicator:
   - Check bottom-right of status bar
   - Should show: "PSNR: XX.X dB (Quality)"
   - Color coded: Green/Yellow/Red

2. Self-Destruct Timer:
   - If message has timer, shows: "⏱️ Self-Destruct: MM:SS"
   - Located in status bar

3. Secret Button:
   - Invisible button beside "MESSAGE INFO"
   - Hover mouse over top-right of MESSAGE INFO header
   - Cursor should change to hand
   - Click to trigger PIN prompt

4. Theme Toggle:
   - Moon icon (🌙) in top-right corner
   - Click to switch Dark/Light mode

5. Drag & Drop:
   - Drag PNG file from explorer
   - Drop anywhere on window
   - Should load and auto-detect metadata

📊 **TERMINAL OUTPUT FEATURES:**

When you press Ctrl+I, terminal should show:

   IMAGE METADATA INSPECTOR
   ============================================================
   📁 FILE: [filename]
   📏 Size: [XX.XX] KB
   🖼️  Dimensions: [width] x [height] pixels
   🎨 Mode: RGB/RGBA
   📊 Format: PNG
   
   📝 EXIF DATA: [if available]
   
   🔐 EMBEDDING STATISTICS:
      Payload Size: [bytes]
      Total Capacity: ~[bytes]
      Used: [%]
      Remaining: ~[bytes]
   
   📊 QUALITY METRICS:
      PSNR: [value] dB (Excellent/Good/Fair)

🧪 **MANUAL TESTING STEPS:**

1. Run: python stego_viewer.py
2. Load any stego image (Ctrl+O or Load Image button)
3. Metadata should auto-load (if paired JSON exists)
4. Try each keyboard shortcut listed above
5. Check PSNR display in status bar
6. Test PIN authentication (hover MESSAGE INFO, click invisible button)
7. Enter PIN: 1234
8. Verify message decrypts

✅ **SUCCESS CRITERIA:**
- All keyboard shortcuts respond
- PSNR displays correctly with color coding
- PIN authentication works (wrong PIN blocks, correct PIN reveals)
- Metadata inspector shows in terminal
- Theme toggle changes colors
- Drag & drop works (if tkinterdnd2 installed)

""")

print("="*70)
print("Ready to test? Launch the viewer with:")
print("  python stego_viewer.py")
print("="*70)
