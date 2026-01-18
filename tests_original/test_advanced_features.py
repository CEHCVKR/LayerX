"""
Advanced Feature Testing for LayerX
Tests self-destruct, PSNR, and advanced metadata features
"""

import os
import json
from pathlib import Path
from datetime import datetime

print("="*70)
print("   LAYERX ADVANCED FEATURE TESTING")
print("="*70)

receiver_dir = Path("H:/Layerx TEST")

# Find all alice message files
message_files = list(receiver_dir.glob("alice_*.json"))

print(f"\n📊 Found {len(message_files)} message(s) to analyze\n")

# Test Categories
psnr_messages = []
timer_messages = []
view_count_messages = []
no_sd_messages = []

for msg_file in message_files:
    try:
        with open(msg_file, 'r') as f:
            data = json.load(f)
            metadata = data.get('metadata', {})
            
            filename = msg_file.name
            print(f"📄 {filename}")
            print("-" * 70)
            
            # Check PSNR
            psnr = metadata.get('psnr_db')
            if psnr:
                psnr_messages.append(filename)
                quality = "Excellent" if psnr > 50 else "Good" if psnr > 40 else "Fair"
                print(f"  📊 PSNR: {psnr:.2f} dB ({quality})")
            else:
                print(f"  ⚠️  PSNR: Not available")
            
            # Check Self-Destruct
            sd = metadata.get('self_destruct')
            if sd:
                sd_type = sd.get('type', 'none')
                if sd_type == 'timer':
                    minutes = sd.get('minutes', 0)
                    timer_messages.append(filename)
                    print(f"  ⏱️  Self-Destruct: TIMER ({minutes} minutes)")
                elif sd_type == 'view_count':
                    views = sd.get('max_views', 0)
                    view_count_messages.append(filename)
                    print(f"  👁️  Self-Destruct: VIEW COUNT ({views} views)")
                else:
                    no_sd_messages.append(filename)
                    print(f"  🔓 Self-Destruct: None")
            else:
                no_sd_messages.append(filename)
                print(f"  🔓 Self-Destruct: None")
            
            # Check Payload
            payload_bits = metadata.get('payload_bits_length', 0)
            payload_bytes = payload_bits // 8
            print(f"  📦 Payload: {payload_bits} bits ({payload_bytes} bytes)")
            
            # Check Sender
            sender = metadata.get('sender_username', 'Unknown')
            sender_addr = metadata.get('sender_address', 'Unknown')
            print(f"  👤 From: {sender} @ {sender_addr}")
            
            # Check Timestamp
            timestamp = metadata.get('timestamp', 'Unknown')
            print(f"  🕒 Timestamp: {timestamp}")
            
            print()
            
    except Exception as e:
        print(f"  ❌ Error reading {msg_file.name}: {e}\n")

# Summary
print("="*70)
print("   FEATURE COVERAGE SUMMARY")
print("="*70)

print(f"\n📊 PSNR Data:")
print(f"  Messages with PSNR: {len(psnr_messages)}")
if psnr_messages:
    for msg in psnr_messages:
        print(f"    ✅ {msg}")
else:
    print(f"    ⚠️  No PSNR data found")
    print(f"    💡 Tip: PSNR is calculated during embedding")

print(f"\n⏱️  Self-Destruct Timer:")
print(f"  Timer-based messages: {len(timer_messages)}")
if timer_messages:
    for msg in timer_messages:
        print(f"    ✅ {msg}")
else:
    print(f"    ℹ️  No timer messages")

print(f"\n👁️  Self-Destruct View Count:")
print(f"  View-count messages: {len(view_count_messages)}")
if view_count_messages:
    for msg in view_count_messages:
        print(f"    ✅ {msg}")
else:
    print(f"    ℹ️  No view-count messages")

print(f"\n🔓 No Self-Destruct:")
print(f"  Regular messages: {len(no_sd_messages)}")
if no_sd_messages:
    for msg in no_sd_messages:
        print(f"    ✅ {msg}")

# Test Recommendations
print("\n" + "="*70)
print("   TEST RECOMMENDATIONS")
print("="*70)

missing_tests = []

if len(psnr_messages) == 0:
    missing_tests.append("PSNR display")
    print("⚠️  Send a new message to generate PSNR data")

if len(timer_messages) == 0:
    missing_tests.append("Timer self-destruct")
    print("⚠️  Send a message with timer self-destruct (e.g., 5 minutes)")

if len(view_count_messages) == 0:
    missing_tests.append("View-count self-destruct")
    print("⚠️  Send a message with view-count (e.g., 3 views)")

if len(message_files) < 3:
    missing_tests.append("Multiple messages")
    print("⚠️  Send more test messages for comprehensive testing")

if not missing_tests:
    print("✅ All feature types tested!")
    print("\n💡 Next: Test viewer GUI features:")
    print("   1. Open stego_viewer.py")
    print("   2. Load message with Ctrl+O")
    print("   3. Press Ctrl+I (metadata inspector)")
    print("   4. Press Ctrl+R (reveal with PIN: 1234)")
    print("   5. Check PSNR in status bar")
    print("   6. Verify self-destruct timer countdown")

print("\n" + "="*70)
print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
