# ✅ LayerX - Clean Installation Complete!

## 📁 Project Structure

```
LayerX/
├── 📄 START_HERE.md          ← Begin here!
├── 📄 INSTALL.md             ← Installation guide
├── 📄 README.md              ← Full documentation
├── 📄 USAGE.md               ← Quick reference
├── 📄 requirements.txt       ← Python dependencies
├── 📄 transceiver.py         ← Main P2P application
├── 🖼️ cover.png              ← Default cover image
│
├── 📁 core_modules/          ← Core functionality
│   ├── a1_encryption.py      (ECC + AES encryption)
│   ├── a2_key_management.py  (Key generation & management)
│   ├── a3_image_processing_color.py (DWT/DCT steganography)
│   ├── a4_compression.py     (Huffman compression)
│   └── a5_embedding_extraction.py (Bit embedding)
│
├── 📁 applications/          ← User tools
│   ├── stego_viewer.py       (GUI message viewer)
│   ├── sender.py             (Standalone sender)
│   ├── receiver.py           (Standalone receiver)
│   ├── generate_keys.py      (Key generator)
│   └── set_pin.py            (PIN configuration)
│
├── 📁 tests/                 ← Test scripts
├── 📁 documentation/         ← Additional docs
└── 📁 backups/               ← Backup files
```

---

## 🚀 Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python -c "import cv2, pywt, cryptography; print('✓ Ready!')"
```

---

## ⚡ Quick Start (2 Terminals)

### Terminal 1 - Alice
```bash
python transceiver.py
# Enter username: alice
# Wait for Bob to appear
Command: send
Select peer: 1
Enter message: Hello Bob!
Choose option: 1
[Press Enter]
```

### Terminal 2 - Bob
```bash
python transceiver.py
# Enter username: bob
# Message received automatically!

# View message:
cd applications
python stego_viewer.py
# Ctrl+O → select image
# Ctrl+R → PIN: 1234
```

---

## 📚 Documentation Guide

| File | When to Read |
|------|-------------|
| **START_HERE.md** | First time users - 60 second start |
| **INSTALL.md** | Detailed setup & troubleshooting |
| **README.md** | Full features & specifications |
| **USAGE.md** | Daily usage & command reference |

---

## ✨ Key Features

- ✅ **P2P Network** - Automatic peer discovery
- ✅ **ECC Encryption** - secp256r1 + AES-256
- ✅ **Steganography** - DWT/DCT, PSNR > 50dB
- ✅ **Digital Signatures** - ECDSA authentication
- ✅ **Self-Destruct** - One-time, timer, view-count
- ✅ **GUI Viewer** - Modern dark/light theme

---

## 🎮 Command Reference

### Transceiver
```
send   - Send encrypted message
peers  - List available peers
list   - List received messages
quit   - Exit
```

### Stego Viewer
```
Ctrl+O - Load image
Ctrl+R - Reveal message (PIN: 1234)
Ctrl+T - Toggle theme
Ctrl+Q - Quit
```

---

## 🔒 Security Defaults

- **Encryption**: ECC (secp256r1) + AES-256
- **PIN**: 1234 (change with `applications/set_pin.py`)
- **Ports**: 37020 (UDP discovery), 37021 (TCP transfer)

---

## 🗑️ Cleaned Up

**Removed:**
- ❌ Test PNG files (test_*.png, stego_*.png)
- ❌ Test scripts (test_*.py)
- ❌ Backup files (*_backup.py)
- ❌ Old documentation (*.md except README)
- ❌ Python cache (__pycache__)
- ❌ Temporary metadata files

**Kept:**
- ✅ Core modules
- ✅ Applications
- ✅ Cover image
- ✅ Main transceiver
- ✅ Documentation (new)
- ✅ Tests folder (organized)

---

## 📦 Files Created During Use

These files are automatically generated (ignored by git):

```
my_identity.json              # Your ECC keypair
layerx_pin.txt               # Custom PIN (optional)
received_stego_*.png          # Received images
received_*_metadata.json      # Decryption keys
stego_to_*.png               # Sent images (copies)
```

---

## 🛠️ Maintenance

### Reset Identity
```bash
rm my_identity.json
python transceiver.py  # Creates new keypair
```

### Clean Received Messages
```bash
rm received_*
```

### Change PIN
```bash
python applications/set_pin.py
```

---

## ✅ System is Ready!

Everything is organized and ready to use:

1. ✅ Clean directory structure
2. ✅ All dependencies documented
3. ✅ Multiple documentation levels
4. ✅ Git ignore configured
5. ✅ Test files removed
6. ✅ Production ready

---

## 🎯 Next Steps

1. Read **START_HERE.md** for immediate start
2. Follow **INSTALL.md** for network setup
3. Reference **USAGE.md** while using
4. Check **README.md** for advanced features

---

**Ready to start?**

```bash
python transceiver.py
```

**Happy secure messaging! 🚀🔒**
