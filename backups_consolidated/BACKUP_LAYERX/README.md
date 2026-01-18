# LayerX - P2P Encrypted Steganography System

A secure peer-to-peer steganography system with ECC encryption, self-destruct messages, and automatic network discovery.

## Features

✅ **End-to-End Encryption** - ECC (Elliptic Curve Cryptography) with AES-256  
✅ **Steganography** - Hide messages in images using DWT/DCT  
✅ **P2P Network** - Automatic peer discovery on local network  
✅ **Digital Signatures** - Verify message authenticity  
✅ **Self-Destruct Messages** - One-time view, timer-based, or view-count limits  
✅ **High Image Quality** - PSNR > 50dB  
✅ **User-Friendly GUI** - Modern dark/light theme viewer  

---

## Installation

### 1. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import cv2, pywt, cryptography; print('✓ All dependencies installed')"
```

---

## Quick Start

### **Sender (Alice)**

1. **Start the transceiver:**
   ```bash
   python transceiver.py
   ```

2. **First time setup:**
   - Enter your username (e.g., `alice`)
   - ECC keypair will be generated automatically

3. **Send a message:**
   - Wait for peer discovery (Bob appears)
   - Type `send`
   - Select peer number
   - Enter your message
   - Choose self-destruct option:
     - `1` - No self-destruct (default)
     - `2` - Delete after reading (1 view)
     - `3` - Delete after N minutes
     - `4` - Delete after N views
   - Press Enter to use default cover image

### **Receiver (Bob)**

1. **Start the transceiver:**
   ```bash
   python transceiver.py
   ```

2. **Setup your identity:**
   - Enter your username (e.g., `bob`)

3. **Receive messages:**
   - Messages are automatically received
   - Saved as `received_stego_*.png` with metadata

4. **Decrypt and view:**
   ```bash
   cd applications
   python stego_viewer.py
   ```
   - Load the received image (Ctrl+O)
   - Metadata auto-detects
   - Press Ctrl+R to reveal message
   - Enter PIN (default: 1234)

---

## Directory Structure

```
LayerX/
├── core_modules/           # Core steganography & encryption modules
│   ├── a1_encryption.py
│   ├── a2_key_management.py
│   ├── a3_image_processing_color.py
│   ├── a4_compression.py
│   └── a5_embedding_extraction.py
├── applications/           # User applications
│   ├── stego_viewer.py    # GUI message viewer
│   ├── sender.py          # Standalone sender
│   ├── receiver.py        # Standalone receiver
│   └── generate_keys.py   # Key generation tool
├── tests/                  # Test scripts
├── cover.png              # Default cover image
├── transceiver.py         # Main P2P application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## Usage Guide

### Transceiver Commands

| Command | Description |
|---------|-------------|
| `send` | Send encrypted message as stego image |
| `peers` | List available peers on network |
| `list` | List received stego images |
| `quit` | Exit application |

### Stego Viewer Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Load image |
| Ctrl+M | Load metadata |
| Ctrl+R | Reveal message |
| Ctrl+T | Toggle dark/light theme |
| Ctrl+Q | Quit viewer |

### Self-Destruct Options

**1. One-Time View**
- Message deleted after viewing
- Deleted when loading another image or closing viewer

**2. Timer-Based**
- Message deleted after N minutes
- Countdown shown in viewer
- Deleted automatically when timer expires

**3. View Count**
- Message deleted after N views
- View counter increments each time
- Deleted when max views reached

---

## Security Features

### Encryption
- **ECC**: secp256r1 curve for key exchange
- **AES-256**: Session key encryption
- **Random IV/Salt**: Unique per message

### Digital Signatures
- ECDSA signatures verify sender identity
- Detects tampering attempts
- Rejects unverified messages

### Steganography
- **DWT (Discrete Wavelet Transform)** + **DCT (Discrete Cosine Transform)**
- 7800+ bits capacity per image
- PSNR > 50dB (imperceptible changes)
- Huffman compression for efficiency

---

## Network Configuration

### Default Ports
- **Peer Discovery**: 37020 (UDP broadcast)
- **File Transfer**: 37021 (TCP)

### Firewall Rules (if needed)
```bash
# Windows
netsh advfirewall firewall add rule name="LayerX Discovery" dir=in action=allow protocol=UDP localport=37020
netsh advfirewall firewall add rule name="LayerX Transfer" dir=in action=allow protocol=TCP localport=37021
```

---

## Troubleshooting

### Peer not discovered?
- Check if both devices are on same network
- Verify firewall allows UDP port 37020
- Restart both transceivers

### Message won't decrypt?
- Verify you're using correct identity (same as receiver)
- Check if PIN is set correctly (use `applications/set_pin.py`)
- Ensure metadata file exists alongside image

### Self-destruct not working?
- One-time messages delete when loading another image or closing viewer
- Timer messages need viewer to stay open for countdown
- Check console for deletion messages

---

## Advanced Usage

### Custom Cover Image
```bash
# When prompted for cover image:
Enter cover image path: path/to/your/image.png
```

### Set Custom PIN
```bash
python applications/set_pin.py
# Enter new PIN when prompted
```

### Generate New Identity
```bash
# Delete old identity
rm my_identity.json
# Restart transceiver - new identity created
python transceiver.py
```

---

## Technical Specifications

| Feature | Specification |
|---------|--------------|
| Encryption | ECC (secp256r1) + AES-256-CFB |
| Steganography | DWT-DCT Hybrid |
| Image Quality | PSNR > 50dB |
| Capacity | 7800+ bits per 512x512 image |
| Compression | Huffman encoding |
| Network | P2P UDP broadcast + TCP transfer |

---

## File Formats

### Identity File (`my_identity.json`)
```json
{
  "username": "alice",
  "address": "B6E7105A322215A6",
  "private_key": "-----BEGIN PRIVATE KEY-----...",
  "public_key": "-----BEGIN PUBLIC KEY-----...",
  "created": "2025-12-29T19:00:00"
}
```

### Metadata File (`received_stego_*_metadata.json`)
```json
{
  "sender": "alice",
  "sender_address": "B6E7105A322215A6",
  "encrypted_aes_key": "hex_encoded_key",
  "salt": "hex_encoded_salt",
  "iv": "hex_encoded_iv",
  "payload_bits_length": 7800,
  "timestamp": "2025-12-29T19:21:47",
  "self_destruct": {
    "type": "one_time",
    "max_views": 1
  }
}
```

---

## License

Educational and research use only.

---

## Credits

Developed with advanced steganography and cryptography techniques.

