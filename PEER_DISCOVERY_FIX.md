# Peer Discovery Fix - Troubleshooting Guide

## Problem Fixed
Your device could discover peers but wasn't broadcasting its own presence properly on Windows.

## What Was Changed

### Root Cause
The original code used `'<broadcast>'` which doesn't work reliably on Windows networks. The fix implements:

1. **Multiple Broadcast Addresses**: Tries specific network broadcast (e.g., `10.10.85.255`), then `255.255.255.255`, then `<broadcast>`
2. **Better Socket Binding**: Explicitly binds to a port to ensure Windows allows the broadcast
3. **Automatic Network Detection**: Calculates your network's broadcast address

### Files Updated
- `sender.py` (main)
- `applications/sender.py`
- `receiver.py` (main)
- `applications/receiver.py`

## Testing Steps

1. **Exit current sender.py** (type `quit`)

2. **Restart sender.py**:
   ```bash
   python sender.py
   ```
   
3. **Look for this line**:
   ```
   [*] Broadcasting to: 10.10.85.255
   ```
   (Your network's broadcast address)

4. **Ask your friend to restart** their receiver/sender

5. **Both should now discover each other**:
   ```
   [+] NEW PEER DISCOVERED: mohan (246A0ECDE69C081E) at 10.10.85.5
   ```

## If Still Not Working

### Check Windows Firewall
Run PowerShell as Administrator:
```powershell
# Allow UDP broadcasts on port 37020
New-NetFirewallRule -DisplayName "LayerX Discovery" -Direction Outbound -LocalPort 37020 -Protocol UDP -Action Allow
New-NetFirewallRule -DisplayName "LayerX Discovery" -Direction Inbound -LocalPort 37020 -Protocol UDP -Action Allow
```

### Verify Network Settings
```bash
# Check your IP configuration
ipconfig

# Make sure both devices are on same network (e.g., 10.10.85.x)
```

### Manual Test
If auto-discovery still fails, you can manually get peer info and send directly using their IP address.

## Why It Works Now

**Before**: 
- Windows blocked/ignored `<broadcast>` address
- No fallback broadcast addresses

**After**:
- Calculates your specific network broadcast (10.10.85.255)
- Falls back to 255.255.255.255 (limited broadcast)
- Better socket configuration for Windows
- Multiple broadcast attempts increase success rate

## Expected Behavior

Both devices should now:
- ✅ Broadcast their presence every 5 seconds
- ✅ Discover each other within 5-10 seconds
- ✅ Show "NEW PEER DISCOVERED" message
- ✅ Send/receive messages successfully

---

**Test it now by restarting both sender and receiver!**
