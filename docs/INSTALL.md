# LayerX - Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, Linux, or macOS
- **Network**: Local network access for P2P features

---

## Step-by-Step Installation

### 1. Clone or Download

```bash
git clone <repository-url>
cd LayerX
```

Or download and extract the ZIP file.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `opencv-python` - Image processing
- `PyWavelets` - Wavelet transforms for steganography
- `cryptography` - Encryption and key management
- `Pillow` - Image handling
- `numpy` - Numerical operations

### 3. Verify Installation

```bash
python -c "import cv2, pywt, cryptography; print('✓ Installation successful!')"
```

If you see `✓ Installation successful!`, you're ready to go!

---

## First Run

### Test Locally (Single Computer)

1. **Terminal 1 - Start Alice:**
   ```bash
   python transceiver.py
   # Enter username: alice
   ```

2. **Terminal 2 - Start Bob:**
   ```bash
   python transceiver.py
   # Enter username: bob
   ```

3. **Send a message from Alice:**
   - Wait for "NEW PEER: bob" message
   - Type `send`
   - Select `1` (bob)
   - Enter message: `Hello Bob!`
   - Choose option `1` (no self-destruct)
   - Press Enter (use default cover.png)

4. **View message on Bob's side:**
   - Bob receives message automatically
   - Open new terminal:
     ```bash
     cd applications
     python stego_viewer.py
     ```
   - Press Ctrl+O, select `received_stego_*.png`
   - Press Ctrl+R, enter PIN `1234`
   - Message appears!

---

## Network Setup (Two Computers)

### Computer 1 (Alice)
```bash
python transceiver.py
# Username: alice
```

### Computer 2 (Bob)
```bash
python transceiver.py
# Username: bob
```

Both computers should be on the **same local network**. Peer discovery happens automatically!

---

## Troubleshooting

### "Module not found" errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Firewall blocking connections (Windows)
```bash
# Allow Python through firewall
# Or add specific rules:
netsh advfirewall firewall add rule name="LayerX Discovery" dir=in action=allow protocol=UDP localport=37020
netsh advfirewall firewall add rule name="LayerX Transfer" dir=in action=allow protocol=TCP localport=37021
```

### No peers discovered
- Ensure both devices are on same network subnet
- Check firewall settings
- Try restarting both transceivers

---

## Optional: Change Default PIN

```bash
python applications/set_pin.py
# Enter new PIN when prompted
# Default PIN is 1234
```

---

## Quick Start Commands

```bash
# Start transceiver
python transceiver.py

# View received messages
cd applications
python stego_viewer.py

# Generate new keypair
python applications/generate_keys.py

# Set custom PIN
python applications/set_pin.py
```

---

## What's Next?

- Read [README.md](README.md) for full usage guide
- Try self-destruct messages
- Experiment with custom cover images
- Share with friends on same network!

---

**Need Help?** Check the Troubleshooting section in README.md
