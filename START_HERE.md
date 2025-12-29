# 🚀 START HERE - LayerX Quick Start

Welcome to **LayerX** - Secure P2P Encrypted Steganography!

---

## ⚡ 60-Second Setup

### 1️⃣ Install (First Time Only)

```bash
pip install -r requirements.txt
```

### 2️⃣ Test It (2 Terminals)

**Terminal 1:**
```bash
python transceiver.py
# Username: alice
```

**Terminal 2:**
```bash
python transceiver.py  
# Username: bob
```

### 3️⃣ Send Message

**In Alice's terminal:**
```
Command: send
Select peer: 1
Enter message: Hello Bob!
Choose option (1-4): 1
[Press Enter]
```

### 4️⃣ View Message

**In Bob's terminal:**
```bash
cd applications
python stego_viewer.py
```
- Press `Ctrl+O` → select image
- Press `Ctrl+R` → enter PIN `1234`
- **Done!** Message appears! 🎉

---

## 📚 Documentation

| File | Description |
|------|-------------|
| **INSTALL.md** | Detailed installation guide |
| **README.md** | Complete feature documentation |
| **USAGE.md** | Quick command reference |

---

## 🎯 What You Can Do

✅ Send encrypted messages hidden in images  
✅ Auto-discover peers on local network  
✅ Self-destruct messages (1-view, timed, N-views)  
✅ Digital signatures verify sender  
✅ PSNR > 50dB image quality  

---

## 🔑 Default Settings

- **PIN**: `1234` (change with `python applications/set_pin.py`)
- **Cover Image**: `cover.png`
- **Ports**: 37020 (discovery), 37021 (transfer)

---

## ⚠️ Quick Troubleshooting

**No peers found?**
- Check same network
- Allow firewall (ports 37020, 37021)

**Can't decrypt?**
- Check PIN is correct
- Verify metadata file exists

**Self-destruct not working?**
- One-time messages delete when loading next image or closing viewer

---

## 🎮 Quick Commands

```bash
# Transceiver
send   - Send message
peers  - List peers
list   - List received
quit   - Exit

# Viewer (Shortcuts)
Ctrl+O - Load image
Ctrl+R - Reveal message
Ctrl+T - Toggle theme
Ctrl+Q - Quit
```

---

## 🔒 Security Notes

- Keep `my_identity.json` safe (your private key!)
- Self-destruct messages for sensitive data
- Change default PIN for better security

---

## 📖 Next Steps

1. ✅ Complete basic test above
2. 📖 Read [INSTALL.md](INSTALL.md) for network setup
3. 🎯 Read [USAGE.md](USAGE.md) for advanced features
4. 🚀 Try self-destruct messages!

---

**Ready? Let's go!** 🚀

```bash
python transceiver.py
```
