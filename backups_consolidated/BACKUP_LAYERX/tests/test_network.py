"""Quick network diagnostic for peer discovery"""
import socket
import json
import time

BROADCAST_PORT = 37020

print("=== NETWORK DIAGNOSTIC ===\n")

# Test 1: Check if we can create UDP socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    print("[OK] UDP socket created")
except Exception as e:
    print(f"[FAIL] Cannot create UDP socket: {e}")
    exit(1)

# Test 2: Get local IP
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    print(f"[OK] Local IP: {local_ip}")
except Exception as e:
    print(f"[FAIL] Cannot get local IP: {e}")
    local_ip = "unknown"

# Test 3: Try binding to port
try:
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    test_sock.bind(('', BROADCAST_PORT))
    test_sock.close()
    print(f"[OK] Port {BROADCAST_PORT} is available")
except Exception as e:
    print(f"[FAIL] Port {BROADCAST_PORT} in use or blocked: {e}")

# Test 4: Try broadcasting
try:
    test_data = json.dumps({"test": "hello"}).encode('utf-8')
    sock.sendto(test_data, ('<broadcast>', BROADCAST_PORT))
    print(f"[OK] Broadcast sent to port {BROADCAST_PORT}")
except Exception as e:
    print(f"[FAIL] Cannot broadcast: {e}")

# Test 5: Listen for 10 seconds
print(f"\n[*] Listening for broadcasts on port {BROADCAST_PORT} for 10 seconds...")
print("[*] Make sure alice's receiver.py is running on the other device!\n")

listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind(('', BROADCAST_PORT))
listener.settimeout(1.0)

start_time = time.time()
received_count = 0

while time.time() - start_time < 10:
    try:
        data, addr = listener.recvfrom(4096)
        received_count += 1
        try:
            info = json.loads(data.decode('utf-8'))
            print(f"[+] Received from {addr[0]}: {info.get('username', 'unknown')}")
        except:
            print(f"[+] Received data from {addr[0]} (not JSON)")
    except socket.timeout:
        continue

listener.close()
sock.close()

print(f"\n[*] Test complete. Received {received_count} broadcasts.")
if received_count == 0:
    print("\n[!] NO BROADCASTS RECEIVED!")
    print("    Possible causes:")
    print("    1. Alice's receiver.py is not running")
    print("    2. Firewall is blocking UDP port 37020")
    print("    3. Devices are on different networks")
    print("    4. Windows network profile is set to 'Public' (should be 'Private')")
