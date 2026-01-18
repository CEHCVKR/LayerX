# FILES TO SHARE WITH OTHER PEER

## Required Python Modules (7 files)
Copy these to the other device in the **same directory structure**:

```
LAYERX/
├── a1_encryption.py                    # AES-256 encryption
├── a2_key_management.py                # ECC key generation
├── a3_image_processing.py              # DWT/DCT transforms
├── a4_compression.py                   # Huffman compression
├── a5_embedding_extraction.py          # Steganography core
├── a6_optimization.py                  # ACO/Chaos optimization
├── a7_communication.py                 # Network utilities
├── sender.py                           # Sender program
├── receiver.py                         # Receiver program
├── requirements.txt                    # Python dependencies
└── cover.png                           # Cover image (512x512)
```

**Total: 11 files**

---

## Installation on Other Device

### Step 1: Copy Files
```bash
# Copy all files to other device
# Example: Via USB, network share, or email
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Programs

**On Sender Device:**
```bash
python sender.py
```

**On Receiver Device:**
```bash
python receiver.py
```

---

## What Happens Automatically

✅ **Identity Creation**: Each device auto-creates `my_identity.json` on first run  
✅ **ECC Keys**: Generated automatically (public/private key pair)  
✅ **Peer Discovery**: UDP broadcast finds peers every 5 seconds  
✅ **Cover Image**: Uses `cover.png` for embedding (must exist)

---

## Manual File Transfer Required

⚠️ **After sending a message, you must manually transfer:**

1. **Stego image** (e.g., `stego_output.png`) - Contains hidden message
2. **Salt & IV** - Displayed by sender, needed by receiver for decryption
3. **Message metadata** - Payload size shown by sender

### Example Workflow:

**Sender Side:**
```
[SEND MESSAGE]
Message: "Hello World"
Salt: 1a2b3c4d...
IV: 5e6f7g8h...
Payload: 4898 bytes
Stego image saved: stego_output.png

[*] Copy stego_output.png to receiver device
```

**Receiver Side:**
```
[RECEIVE MESSAGE]  
Enter stego image path: stego_output.png
Enter salt (hex): 1a2b3c4d...
Enter IV (hex): 5e6f7g8h...
Enter payload size: 4898

[SUCCESS] Decrypted message: Hello World
```

---

## Network Requirements

**Both devices must be on the SAME network:**
- Same WiFi network, OR
- Same LAN (wired), OR  
- Direct connection (crossover cable)

**Port:** UDP 37020 (must be open in firewall)

**Check connectivity:**
```bash
# On Windows
ping <other_device_ip>

# Check if port is listening
netstat -an | Select-String "37020"
```

---

## Optional Files (Not Required)

❌ **Do NOT copy these:**
- Test files (`test_*.py`)
- Documentation (`.md` files)
- Output files (`*.txt`, logs)
- `__pycache__/` directory
- `my_identity.json` (auto-generated per device)

---

## Minimal File List (11 Files Only)

```
✅ a1_encryption.py
✅ a2_key_management.py  
✅ a3_image_processing.py
✅ a4_compression.py
✅ a5_embedding_extraction.py
✅ a6_optimization.py
✅ a7_communication.py
✅ sender.py
✅ receiver.py
✅ requirements.txt
✅ cover.png (or any 512x512 PNG image)
```

**That's it!** Just 11 files needed for full functionality.

---

## Quick Setup Script

Save as `setup_peer.bat` (Windows):
```batch
@echo off
echo Installing LayerX dependencies...
pip install -r requirements.txt
echo.
echo Setup complete! Run:
echo   python sender.py   (to send messages)
echo   python receiver.py (to receive messages)
pause
```

Save as `setup_peer.sh` (Linux/Mac):
```bash
#!/bin/bash
echo "Installing LayerX dependencies..."
pip install -r requirements.txt
echo ""
echo "Setup complete! Run:"
echo "  python sender.py   (to send messages)"
echo "  python receiver.py (to receive messages)"
```

---

## Troubleshooting

### "No peers discovered"
- Check both devices are on same network
- Check firewall allows UDP port 37020
- Wait 10-15 seconds for discovery

### "ModuleNotFoundError"
- Run: `pip install -r requirements.txt`
- Check all 11 files are copied

### "cover.png not found"
- Create cover image: `python -c "import cv2; import numpy as np; cv2.imwrite('cover.png', np.random.randint(50,200,(512,512,3),dtype=np.uint8))"`
- Or copy any PNG image and rename to `cover.png`

### "Invalid payload length"
- Ensure Q-factor matches (both use default Q=5.0)
- Verify payload size is correct
- Check image wasn't compressed/modified during transfer

---

## Security Notes

🔒 **Each device has unique keys:**
- Private key stays on device (`my_identity.json`)
- Public key shared via peer discovery (automatic)
- Messages encrypted with AES-256 + ECC hybrid

🔒 **Manual salt/IV transfer:**
- Current design requires copy-paste (secure)
- Future enhancement: Automated ECC-encrypted exchange

---

## Ready to Test?

**Device 1:** Start `sender.py` → wait for peer → send message  
**Device 2:** Start `receiver.py` → wait for peer → receive stego image → extract message

**Both devices will see each other in peer list after 5-10 seconds!**
