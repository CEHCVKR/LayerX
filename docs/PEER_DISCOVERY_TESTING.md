# How to Test Peer Discovery on Your Network

## ✓ Good News!
Your peer discovery system is **working correctly**. The diagnostic shows:
- ✓ UDP broadcasts are being sent
- ✓ UDP broadcasts are being received
- ✓ No firewall blocking

## The Issue
You're the only peer on the network! The system filters out your own broadcasts (by design).

---

## Solution 1: Test with Another Computer

### On Computer 1 (Current - 10.10.198.169):
```
Already running transceiver.py as "Venkat"
```

### On Computer 2 (Another machine on same network):
```batch
# 1. Copy the entire LayerX folder to the second computer

# 2. Open terminal on Computer 2
cd path\to\LayerX

# 3. Run transceiver
python transceiver.py

# 4. When prompted, enter a DIFFERENT username (e.g., "Alice")

# Both should now discover each other!
```

---

## Solution 2: Test with Two Instances on Same Machine

### Terminal 1 (Current):
```
Keep running as "Venkat"
```

### Terminal 2 (New terminal window):
```batch
# 1. Create a test directory
cd H:\LAYERX
mkdir test_peer2
cd test_peer2

# 2. Copy files
copy ..\*.py .
xcopy /E /I ..\core_modules core_modules

# 3. Run transceiver
python transceiver.py

# 4. Enter DIFFERENT username: "Bob"
```

**Important**: Delete `my_identity.json` in test_peer2 folder if you want to create a new identity.

---

## Expected Output When Working

### Terminal 1 (Venkat):
```
[*] Discovering peers...
[+] NEW PEER: Bob at 10.10.198.169
```

### Terminal 2 (Bob):
```
[*] Discovering peers...
[+] NEW PEER: Venkat at 10.10.198.169
```

---

## Verify Peer Discovery

Once both are running, type:
```
Command: peers
```

You should see the other peer listed!

---

## Network Requirements

✓ **Same subnet**: Both computers must be on same network (10.10.198.x)  
✓ **Firewall**: Port 37020 UDP must be open (currently working)  
✓ **Different identities**: Each instance needs different username  

---

## Quick Test Script

Run this to see if another peer exists:
```batch
python test_peer_discovery_debug.py
```

If you see broadcasts from other usernames besides "Venkat", those are potential peers!
