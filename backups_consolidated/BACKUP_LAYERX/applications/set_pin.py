"""
LayerX PIN Configuration
Set a custom PIN for message viewer authentication
"""

import os

print("\n" + "="*50)
print("   LayerX PIN Configuration")
print("="*50)

current_pin = "1234"  # default
pin_file = "layerx_pin.txt"

if os.path.exists(pin_file):
    with open(pin_file, 'r') as f:
        current_pin = f.read().strip()
    print(f"\nCurrent PIN: {current_pin}")
else:
    print(f"\nCurrent PIN: {current_pin} (default)")

print("\nSet a new PIN for message viewer authentication")
print("(Press Enter to keep current PIN)")

new_pin = input("\nEnter new PIN (4-8 digits): ").strip()

if new_pin:
    if len(new_pin) < 4:
        print("❌ PIN must be at least 4 characters")
    else:
        with open(pin_file, 'w') as f:
            f.write(new_pin)
        print(f"\n✅ PIN updated successfully!")
        print(f"New PIN: {new_pin}")
else:
    print(f"\n✓ Keeping current PIN: {current_pin}")

print("\n" + "="*50)
print("Use this PIN when viewing messages in stego_viewer.py")
print("="*50 + "\n")
