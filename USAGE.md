# LayerX - Quick Usage Guide

## Starting the System

```bash
# Start transceiver (P2P mode)
python transceiver.py

# Start viewer (to decrypt messages)
cd applications
python stego_viewer.py
```

---

## Transceiver Commands

| Command | Action |
|---------|--------|
| `send` | Send encrypted message |
| `peers` | List discovered peers |
| `list` | List received messages |
| `quit` | Exit |

---

## Sending Messages

1. Type `send`
2. Select peer number
3. Enter your message
4. Choose self-destruct option:
   - `1` = Normal message
   - `2` = Delete after 1 view
   - `3` = Delete after N minutes
   - `4` = Delete after N views
5. Press Enter (or specify custom cover image)

**Example:**
```
Command: send
Select peer: 1
Enter message: Secret meeting at 5pm
Choose option (1-4): 2
[Message sent with one-time view]
```

---

## Viewing Messages

### Method 1: Stego Viewer (Recommended)

```bash
cd applications
python stego_viewer.py
```

**Keyboard Shortcuts:**
- `Ctrl+O` - Load image
- `Ctrl+M` - Load metadata (auto-detects)
- `Ctrl+R` - Reveal message
- `Ctrl+T` - Toggle theme
- `Ctrl+Q` - Quit

**Steps:**
1. Press `Ctrl+O`
2. Select `received_stego_*.png`
3. Metadata loads automatically
4. Press `Ctrl+R`
5. Enter PIN (default: `1234`)
6. Message appears!

---

## Self-Destruct Messages

### One-Time View (Option 2)
- Message deleted after viewing
- Deleted when loading another image OR closing viewer
- Status bar shows: ⚠️ One-time message

### Timer-Based (Option 3)
```
Choose option: 3
Delete after how many minutes? 5
```
- Countdown timer appears
- Auto-deletes when time expires
- Also deleted when closing viewer

### View Count (Option 4)
```
Choose option: 4
Delete after how many views? 3
```
- Tracks view count
- Deleted after max views reached
- Shows remaining views

---

## File Locations

### Created Files
```
my_identity.json              # Your ECC keypair (keep safe!)
received_stego_*.png          # Received stego images
received_stego_*_metadata.json # Decryption metadata
stego_to_*.png                # Sent stego images (your copies)
```

### Important Files
```
cover.png                     # Default cover image
layerx_pin.txt               # Custom PIN (optional)
```

---

## Common Workflows

### Basic Message Exchange
```bash
# Alice
python transceiver.py
> send
> 1 (bob)
> Hello Bob!
> 1 (no self-destruct)

# Bob
python transceiver.py
# Message auto-received
cd applications
python stego_viewer.py
# Ctrl+O → select image → Ctrl+R → enter PIN
```

### Self-Destruct Message
```bash
# Alice
> send
> 1 (bob)
> This message will self-destruct!
> 2 (one-time view)

# Bob views once
# Message automatically deleted
```

### Timed Message
```bash
# Alice
> send
> 1 (bob)
> Read this within 5 minutes!
> 3 (timer)
> 5 (minutes)

# Bob has 5 minutes to read
# Auto-deletes after timer expires
```

---

## Tips & Tricks

### Custom Cover Image
```bash
# When prompted:
Enter cover image path: /path/to/image.png
# Or press Enter for default cover.png
```

### Change PIN
```bash
python applications/set_pin.py
# Enter new PIN: 8008
# PIN saved to layerx_pin.txt
```

### View Received Messages
```bash
# In transceiver
Command: list

# Output shows:
# 1. received_stego_to_bob_20251229_140527.png
# 2. received_stego_to_bob_20251229_192147.png
```

### Multiple Peers
```bash
Command: peers

# Shows:
# 1. bob - 192.168.1.100
# 2. charlie - 192.168.1.101
# 3. dave - 192.168.1.102

# Send to specific peer:
Command: send
Select peer: 2 (charlie)
```

---

## Status Indicators

### Transceiver
```
[+] NEW PEER: bob           # Peer discovered
[*] Creating stego image... # Encoding message
[OK] Sent to 192.168.1.2   # Transfer successful
[RX] Receiving from alice... # Incoming message
[✓] Signature verified     # Message authentic
[i] Metadata saved         # Ready to decrypt
```

### Stego Viewer
```
✓ Ready | Press Ctrl+R      # Ready to reveal
⚠️ One-time message         # Self-destruct active
⏱️ Self-Destruct: 2m 35s   # Timer countdown
✅ Message revealed          # Decryption successful
```

---

## Security Best Practices

1. **Keep `my_identity.json` safe** - Contains your private key
2. **Use self-destruct** for sensitive messages
3. **Verify signatures** - Check for [✓] Signature verified
4. **Change default PIN** - Use `set_pin.py`
5. **Delete old messages** - Use `list` command to track

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│ TRANSCEIVER                              │
├─────────────────────────────────────────┤
│ send   → Send message                    │
│ peers  → List peers                      │
│ list   → List received                   │
│ quit   → Exit                            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ STEGO VIEWER                             │
├─────────────────────────────────────────┤
│ Ctrl+O → Load image                      │
│ Ctrl+R → Reveal message                  │
│ Ctrl+T → Toggle theme                    │
│ Ctrl+Q → Quit                            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ SELF-DESTRUCT                            │
├─────────────────────────────────────────┤
│ 1 → Normal (no delete)                   │
│ 2 → One-time view                        │
│ 3 → Timer (N minutes)                    │
│ 4 → View count (N times)                 │
└─────────────────────────────────────────┘
```
