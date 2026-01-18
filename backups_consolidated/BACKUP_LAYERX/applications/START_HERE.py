"""
LayerX Quick Start Guide
Run this to see what to do!
"""

print("""
╔══════════════════════════════════════════════════════════╗
║         LayerX Steganography - Quick Start              ║
╚══════════════════════════════════════════════════════════╝

🚀 ENHANCED SECURE VERSION (Recommended):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1️⃣  - RECEIVER (Run FIRST):
  → python receiver_secure.py
  
  What happens:
  ✓ Creates your identity (username + keys)
  ✓ Listens for incoming messages
  ✓ Saves encrypted metadata automatically
  ✓ Type 'history' to see received messages
  ✓ Type 'peers' to see who's online

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 2️⃣  - SENDER (Run SECOND):
  → python sender_secure.py
  
  What to do:
  ✓ Wait 5-10 seconds for peer discovery
  ✓ Type: send
  ✓ Select receiver from list
  ✓ Type your secret message
  ✓ Choose self-destruct option:
      1 = No self-destruct
      2 = Delete after 1 view
      3 = Delete after X minutes
      4 = Delete after N views
  ✓ Image sent automatically!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 3️⃣  - VIEW MESSAGE:
  → python stego_viewer.py
  
  How to use:
  ✓ Click "📂 Load Image" → select received_stego_*.png
  ✓ Metadata auto-loads! (or click "🔐 Load Metadata")
  ✓ Click "🔓 REVEAL MESSAGE"
  ✓ Message displays on right panel!
  ✓ Click "📤 Export Message" to save as .txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 VIEWER FEATURES:
  • Drag & Drop: Just drag PNG/JSON files into window!
  • Theme Toggle: Click "🌙 Toggle Theme"
  • Auto-detect: Finds matching metadata automatically
  • Export: Save message to text file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 BASIC VERSION (Original - simpler):
  Receiver:  python receiver_new.py
  Sender:    python sender.py
  Viewer:    python stego_viewer.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  REQUIREMENTS:
  ✓ IMAGE1.jpg must exist in same folder
  ✓ Both computers on same network
  ✓ Firewall allows port 37020 & 37021
  ✓ All core modules (a1-a8) present

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧪 QUICK TEST (one computer):
  Terminal 1: python receiver_secure.py
  Terminal 2: python sender_secure.py
  Terminal 3: python stego_viewer.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 SECURITY FEATURES (sender_secure.py + receiver_secure.py):
  ✓ Perfect Forward Secrecy (ECDH)
  ✓ Digital Signatures (verify sender)
  ✓ AES-256-GCM encryption
  ✓ Self-destruct messages
  ✓ Message history logging

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to start? Run receiver first!
""")
