# LayerX Project - Directory Structure

## 📁 Root Directory
```
H:\LAYERX\
├── .git/                           # Git version control
├── .gitignore                      # Git ignore rules
├── my_identity.json                # User identity configuration
├── requirements.txt                # Python dependencies
├── readme.md                       # Main project documentation
├── PROJECT_OVERVIEW.md             # Project overview
├── STEP_BY_STEP_EXPLANATION.md     # Implementation guide
├── PEER_DISCOVERY_FIX.md           # Peer discovery fixes
└── DIRECTORY_STRUCTURE.md          # This file
```

## 📁 Core Modules (`core_modules/`)
**Purpose**: Core steganography algorithms and utilities

```
core_modules/
├── a1_encryption.py                # AES-256 encryption/decryption
├── a2_key_management.py            # RSA key generation & management
├── a3_image_processing.py          # Grayscale DWT-DCT processing
├── a3_image_processing_color.py    # Color image DWT-DCT processing
├── a4_compression.py               # Data compression (zlib)
├── a5_embedding_extraction.py      # Steganography embed/extract
├── a6_optimization.py              # Performance optimization
├── a7_communication.py             # Network communication (P2P)
├── a8_scanning_detection.py        # Security scanning
├── a11_performance_monitoring.py   # Performance metrics
├── a12_security_analysis.py        # Security analysis tools
├── a17_testing_validation.py       # Validation utilities
└── a18_error_handling.py           # Error handling & logging
```

## 📁 Applications (`applications/`)
**Purpose**: End-user applications and tools

```
applications/
├── START_HERE.py                   # 🌟 Main launcher (start here!)
├── stego_viewer.py                 # 🖼️ Message viewer (current version)
├── sender.py                       # 📤 Basic sender
├── receiver.py                     # 📥 Basic receiver
├── sender_secure.py                # 📤 Secure sender with encryption
├── receiver_secure.py              # 📥 Secure receiver with encryption
├── sender_color.py                 # 🎨 Color steganography sender
├── chat_client.py                  # 💬 Chat client application
├── chat_server.py                  # 💬 Chat server application
├── decrypt_tool.py                 # 🔓 Standalone decryption tool
├── set_pin.py                      # 🔐 PIN configuration tool
├── generate_keys.py                # 🔑 RSA key generator
├── copy_to_peer.py                 # 📋 File transfer utility
├── close_handler.py                # 🔄 Window close handler
├── stego_viewer_new.py             # 🖼️ Viewer (legacy)
└── receiver_new.py                 # 📥 Receiver (legacy)
```

## 📁 Tests (`tests/`)
**Purpose**: Automated testing and validation

```
tests/
├── run_tests.py                    # ✅ Main test runner (file format validation)
├── test_system.py                  # ✅ System integration tests
├── test_advanced_features.py       # ✅ Advanced feature tests
├── test_viewer.py                  # Viewer functionality tests
├── test_viewer_automated.py        # Automated viewer tests
├── test_complete.py                # Complete system tests
├── comprehensive_test.py           # Comprehensive test suite
├── final_comprehensive_test.py     # Final validation tests
├── test_adaptive_system.py         # Adaptive Q-factor tests
├── test_color_stego.py             # Color steganography tests
├── test_psnr_optimization.py       # PSNR optimization tests
├── test_performance.py             # Performance benchmarks
├── test_network.py                 # Network communication tests
└── (50+ additional test files...)  # Various component tests
```

## 📁 Keys (`keys/`)
**Purpose**: Cryptographic keys storage

```
keys/
├── alice_private.pem               # Alice's RSA private key
└── alice_public.pem                # Alice's RSA public key
```

## 📁 Documentation (`documentation/`)
**Purpose**: Technical documentation and reports

```
documentation/
├── COMPLETE_RESEARCH_PAPER.md      # Full research paper
├── COMPLETE_SYSTEM_README.md       # Complete system guide
├── FINAL_DELIVERY.md               # Final delivery report
├── FINAL_STATUS_REPORT.md          # Status summary
├── PROJECT_COMPLETION_SUMMARY.md   # Completion summary
├── ANSWERS_TO_QUESTIONS.md         # FAQ and answers
├── QUICK_REFERENCE_GUIDE.md        # Quick reference
├── COLOR_STEGANOGRAPHY_GUIDE.md    # Color stego guide
├── AUTOMATIC_TRANSFER_GUIDE.md     # Auto-transfer guide
├── ABSTRACT_COMPLIANCE_FINAL_REPORT.md  # Compliance report
├── test_all_features.md            # Feature test documentation
├── TEST_RESULTS_SUMMARY.md         # Test results summary
└── (50+ additional documentation files)
```

## 📁 Analytics (`analytics/`)
**Purpose**: Performance analysis and reports

```
analytics/
├── analytics_psnr.py               # PSNR analytics tool
├── generate_psnr_report.py         # PSNR report generator
└── PSNR_ANALYTICS_REPORT.md        # PSNR analysis report
```

## 📁 Demo Outputs (`demo_outputs/`)
**Purpose**: Demo images and test outputs

```
demo_outputs/
├── IMAGE.jpg                       # Test image 1
├── IMAGE1.jpg                      # Test image 2
└── (various demo output files)
```

## 📁 Diagrams (`diagrams/`)
**Purpose**: Architecture and flow diagrams

```
diagrams/
└── SENDER_PROFESSIONAL             # Professional sender diagram
```

## 📁 Backups (`backups/`)
**Purpose**: Git bundle backups

```
backups/
└── layerx-backup-20251218-232539.bundle
```

## 📁 Scripts (`scripts/`)
**Purpose**: Utility scripts

```
scripts/
└── (utility scripts)
```

## 📁 Legacy (`legacy/`)
**Purpose**: Deprecated/old code

```
legacy/
└── (legacy implementations)
```

---

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Application**:
   ```bash
   python applications/START_HERE.py
   ```

3. **View Encrypted Messages**:
   ```bash
   python applications/stego_viewer.py
   ```

4. **Run Tests**:
   ```bash
   python tests/run_tests.py
   python tests/test_system.py
   ```

---

## 📊 Project Statistics

- **Core Modules**: 13 files
- **Applications**: 15 files  
- **Test Files**: 50+ files
- **Documentation**: 50+ files
- **Test Pass Rate**: 100% ✅

---

## 🔑 Key Features

✅ DWT-DCT Adaptive Steganography (Color & Grayscale)
✅ AES-256 + RSA Encryption
✅ Self-Destruct Messages (Timer & View Count)
✅ P2P Communication
✅ PIN-Based Authentication
✅ PSNR Quality Monitoring
✅ Drag & Drop Interface
✅ Auto-Detect Metadata
✅ Keyboard Shortcuts (Ctrl+R, Ctrl+O, etc.)
✅ Dark/Light Themes

---

*Last Updated: December 26, 2025*
