"""
LayerX Peer Discovery Diagnostic Tool
Tests if peer discovery is working properly
"""

import socket
import json
import time
import threading
import sys

BROADCAST_PORT = 37020
running = True

def test_listener():
    """Test if we can receive broadcast messages"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', BROADCAST_PORT))
        sock.settimeout(1.0)
        
        print(f"✓ Listener bound to port {BROADCAST_PORT}")
        
        received_count = 0
        start_time = time.time()
        
        while running and (time.time() - start_time) < 15:
            try:
                data, addr = sock.recvfrom(4096)
                peer_info = json.loads(data.decode('utf-8'))
                print(f"\n✓ Received broadcast from: {peer_info['username']} at {addr[0]}")
                print(f"  Address: {peer_info['address']}")
                received_count += 1
            except socket.timeout:
                continue
            except Exception as e:
                print(f"⚠️  Error receiving: {e}")
        
        sock.close()
        
        if received_count == 0:
            print("\n❌ No broadcasts received in 15 seconds")
            print("   Possible causes:")
            print("   1. No other peers are running")
            print("   2. Firewall is blocking UDP port 37020")
            print("   3. Network doesn't support broadcasts")
        else:
            print(f"\n✓ Successfully received {received_count} broadcasts")
            
    except Exception as e:
        print(f"❌ Failed to create listener: {e}")
        if "Permission denied" in str(e):
            print("   → Run as Administrator")
        elif "Address already in use" in str(e):
            print("   → Port 37020 is already in use (transceiver running?)")

def test_announcer():
    """Test if we can send broadcast messages"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        test_message = json.dumps({
            'username': 'TEST_PEER',
            'address': 'TEST_ADDRESS',
            'public_key': 'TEST_PUBLIC_KEY'
        }).encode('utf-8')
        
        print(f"\n✓ Broadcasting test messages every 2 seconds...")
        print(f"  Target: 255.255.255.255:{BROADCAST_PORT}")
        
        sent_count = 0
        for i in range(7):
            try:
                sock.sendto(test_message, ('255.255.255.255', BROADCAST_PORT))
                sent_count += 1
                print(f"  Sent broadcast #{sent_count}")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️  Error sending: {e}")
                if "Permission denied" in str(e):
                    print("   → Broadcasts blocked by network/firewall")
                
        sock.close()
        print(f"\n✓ Sent {sent_count} broadcasts")
        
    except Exception as e:
        print(f"❌ Failed to create sender: {e}")

def main():
    global running
    
    print("="*60)
    print("LayerX Peer Discovery Diagnostic Tool")
    print("="*60)
    print("\nThis will test peer discovery for 15 seconds")
    print("For best results, run this on TWO different computers/terminals\n")
    
    input("Press Enter to start test...")
    
    print("\n[*] Starting listener thread...")
    listener_thread = threading.Thread(target=test_listener, daemon=True)
    listener_thread.start()
    
    time.sleep(1)
    
    print("\n[*] Starting announcer thread...")
    announcer_thread = threading.Thread(target=test_announcer, daemon=True)
    announcer_thread.start()
    
    try:
        time.sleep(16)
    except KeyboardInterrupt:
        print("\n\n[*] Test interrupted")
    
    running = False
    time.sleep(1)
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)
    print("\nIf no broadcasts were received:")
    print("1. Run this test on a SECOND computer/terminal on the same network")
    print("2. Check Windows Firewall settings")
    print("3. Try: netsh advfirewall firewall add rule name=\"LayerX UDP\" dir=in action=allow protocol=UDP localport=37020")
    print("4. Make sure both devices are on the same subnet")
    print("\n")

if __name__ == "__main__":
    main()
