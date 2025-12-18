# LayerX Steganographic Security Framework

A comprehensive peer-to-peer secure messaging system using advanced steganography, encryption, and optimization techniques.

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Sender (Alice's device):**
   ```bash
   python applications/sender.py
   ```

3. **Run Receiver (Bob's device):**
   ```bash
   python applications/receiver.py
   ```

4. **Send a Message:**
   - Peers auto-discover every 5 seconds
   - Type `send` and follow prompts
   - Message automatically transfers and decrypts!

## 📁 Project Structure

```
LAYERX/
├── core_modules/          # Core steganography & encryption modules
│   ├── a1_encryption.py              # AES-256-CBC encryption
│   ├── a2_key_management.py          # ECC SECP256R1 key management
│   ├── a3_image_processing.py        # DWT decomposition & PSNR
│   ├── a4_compression.py             # Huffman compression
│   ├── a5_embedding_extraction.py    # DWT+DCT steganography
│   ├── a6_optimization.py            # ACO & chaos optimization
│   ├── a7_communication.py           # Network protocols
│   └── a8_scanning_detection.py      # Steganalysis detection
│
├── applications/          # User-facing applications
│   ├── sender.py         # P2P sender with auto file transfer
│   ├── receiver.py       # P2P receiver with auto decryption
│   └── generate_keys.py  # ECC keypair generator
│
├── tests/                # Test suite
│   ├── test_complete_system.py      # Full system integration tests
│   ├── test_sender_workflow.py      # Sender pipeline tests
│   └── test_q_factor_analysis.py    # PSNR quality tests
│
├── analytics/            # Performance analytics
│   ├── analytics_psnr.py            # Quick PSNR tests
│   ├── generate_psnr_report.py      # Detailed report generator
│   └── PSNR_ANALYTICS_REPORT.md     # Full analytics report
│
├── documentation/        # Project documentation
├── demo_outputs/         # Demo images and outputs
├── legacy/              # Archive of old versions
├── cover.png            # Default cover image (512x512)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Core Features

### Security
- **AES-256-CBC** encryption with PBKDF2 key derivation
- **ECC SECP256R1** public key cryptography
- **Reed-Solomon** error correction for robust data recovery

### Steganography
- **2-level Haar DWT** wavelet decomposition
- **2D DCT** frequency domain embedding
- **Quantization-based** embedding (Q-factor = 5.0)
- **7 frequency bands**: LH1, HL1, LH2, HL2, HH1, HH2, LL2

### Optimization
- **Fixed** position-based coefficient selection (deterministic)
- **ACO** (Ant Colony Optimization) for robust coefficient selection
- **Chaos** logistic map for pseudo-random selection

### Networking
- **UDP broadcast** peer discovery (port 37020, every 5 sec)
- **TCP file transfer** automatic stego image delivery (port 37021)
- **Auto-decryption** no manual salt/IV input needed

## 📊 Performance Metrics

| Message Size | Payload | PSNR | Quality |
|--------------|---------|------|---------|
| 2 chars | 1KB | 50.85 dB | Excellent |
| 50 chars | 5KB | 44.67 dB | Good |
| 200 chars | 12KB | 40.75 dB | Acceptable |
| 1000 chars | 22KB | 38.16 dB | Poor |

**Recommended:** Keep messages under 200 characters for PSNR >40 dB

## 🧪 Testing

Run complete system tests:
```bash
python tests/test_complete_system.py
```

Run sender workflow tests:
```bash
python tests/test_sender_workflow.py
```

Generate PSNR analytics:
```bash
python analytics/generate_psnr_report.py
```

## 📡 Network Requirements

- **Ports:** 37020 (UDP), 37021 (TCP)
- **Firewall:** Allow both ports for peer discovery and file transfer
- **Network:** Devices must be on same LAN
- **Protocol:** UDP broadcast for discovery, TCP for file transfer

## 🔐 Identity Management

On first run, each application creates `my_identity.json`:
```json
{
  "username": "alice",
  "address": "9DAA6BF262666E80",
  "private_key": "-----BEGIN EC PRIVATE KEY-----...",
  "public_key": "-----BEGIN PUBLIC KEY-----...",
  "created": "2025-12-18T23:00:00"
}
```

## 🎯 Usage Example

**Alice (Sender):**
```
> send
Select peer: 1. bob @ 192.168.31.214
Enter message: Hello Bob!

[SUCCESS] MESSAGE EMBEDDED!
PSNR: 50.92 dB
File sent to bob!
```

**Bob (Receiver):**
```
[+] INCOMING FILE from 192.168.31.170...
[*] Auto-decrypting...

[SUCCESS] MESSAGE DECRYPTED!
>>> Hello Bob!
```

## 📦 Dependencies

- numpy >= 1.21.0
- opencv-python >= 4.5.0
- PyWavelets >= 1.1.0
- scikit-image >= 0.18.0
- scipy >= 1.7.0
- pycryptodome >= 3.15.0
- PyNaCl >= 1.5.0
- reedsolo >= 1.7.0

## 🏆 Key Achievements

✅ **7/7 system tests passing**  
✅ **10/10 Q-factor tests passing**  
✅ **Peer-to-peer tested on 2 physical devices**  
✅ **Automatic file transfer working**  
✅ **PSNR >50 dB for small payloads**  
✅ **12/12 abstract requirements satisfied**

## 📝 License

Academic Project - Team 08

## 👥 Authors

- Member A: Encryption, Compression, Communication
- Member B: Image Processing, Optimization, Steganography

---

**Last Updated:** December 18, 2025

