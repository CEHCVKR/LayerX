"""
Peer Discovery Debugging Tool
Tests UDP broadcast and listening
"""

import socket
import json
import time
import threading

BROADCAST_PORT = 37020

def test_broadcast_listener():
    """Test if we can receive UDP broadcasts"""
    print("\n[TEST 1] Testing UDP Broadcast Listener")
    print("="*60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', BROADCAST_PORT))
        sock.settimeout(5.0)
        
        print(f"✓ Socket bound to port {BROADCAST_PORT}")
        print("  Listening for broadcasts (5 seconds)...")
        
        messages_received = 0
        start_time = time.time()
        
        while time.time() - start_time < 5:
            try:
                data, addr = sock.recvfrom(4096)
                messages_received += 1
                print(f"  ✓ Received from {addr[0]}:{addr[1]}")
                try:
                    peer_info = json.loads(data.decode('utf-8'))
                    print(f"    Username: {peer_info.get('username')}")
                    print(f"    Address: {peer_info.get('address')}")
                except:
                    print(f"    Raw data: {data}")
            except socket.timeout:
                continue
        
        sock.close()
        
        if messages_received > 0:
            print(f"\n  ✓ SUCCESS: Received {messages_received} broadcast(s)")
            return True
        else:
            print(f"\n  ⚠ WARNING: No broadcasts received")
            return False
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def test_broadcast_sender():
    """Test if we can send UDP broadcasts"""
    print("\n[TEST 2] Testing UDP Broadcast Sender")
    print("="*60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        test_data = json.dumps({
            'username': 'TestUser',
            'address': 'TEST1234',
            'public_key': 'test_public_key'
        }).encode('utf-8')
        
        print(f"  Sending test broadcast to 255.255.255.255:{BROADCAST_PORT}")
        
        # Send multiple times
        for i in range(3):
            sock.sendto(test_data, ('255.255.255.255', BROADCAST_PORT))
            print(f"  ✓ Broadcast sent #{i+1}")
            time.sleep(0.5)
        
        sock.close()
        print("\n  ✓ SUCCESS: Broadcasts sent")
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def test_loopback():
    """Test if broadcasts can be received on the same machine"""
    print("\n[TEST 3] Testing Loopback (Send & Receive on same machine)")
    print("="*60)
    
    received = []
    
    def listener():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', BROADCAST_PORT))
            sock.settimeout(3.0)
            
            while True:
                try:
                    data, addr = sock.recvfrom(4096)
                    received.append(data.decode('utf-8'))
                except socket.timeout:
                    break
            sock.close()
        except Exception as e:
            print(f"  Listener error: {e}")
    
    # Start listener thread
    listener_thread = threading.Thread(target=listener, daemon=True)
    listener_thread.start()
    
    time.sleep(0.5)  # Give listener time to start
    
    # Send broadcast
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        test_msg = json.dumps({'test': 'loopback', 'username': 'TestUser'})
        
        for i in range(3):
            sock.sendto(test_msg.encode('utf-8'), ('255.255.255.255', BROADCAST_PORT))
            print(f"  ✓ Sent broadcast #{i+1}")
            time.sleep(0.3)
        
        sock.close()
    except Exception as e:
        print(f"  ❌ Send error: {e}")
    
    # Wait for listener
    listener_thread.join(timeout=4)
    
    if received:
        print(f"\n  ✓ SUCCESS: Received {len(received)} message(s) via loopback")
        for msg in received:
            print(f"    - {msg}")
        return True
    else:
        print(f"\n  ⚠ WARNING: No loopback messages received")
        return False


def check_network_info():
    """Display network information"""
    print("\n[INFO] Network Configuration")
    print("="*60)
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"  Hostname: {hostname}")
        print(f"  Local IP: {local_ip}")
        
        # Get all network interfaces
        import subprocess
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        
        # Extract IPv4 addresses
        lines = result.stdout.split('\n')
        ips = []
        for line in lines:
            if 'IPv4 Address' in line:
                ip = line.split(':')[-1].strip()
                if ip:
                    ips.append(ip)
        
        if ips:
            print(f"\n  All IPv4 Addresses:")
            for ip in ips:
                print(f"    - {ip}")
        
    except Exception as e:
        print(f"  ⚠ Could not retrieve network info: {e}")


def check_firewall_suggestions():
    """Provide firewall troubleshooting suggestions"""
    print("\n[TROUBLESHOOTING] Firewall & Network Suggestions")
    print("="*60)
    print("""
  1. Windows Firewall:
     - Open 'Windows Defender Firewall'
     - Click 'Allow an app through firewall'
     - Add Python or allow UDP port 37020
  
  2. Command to allow port (run as Administrator):
     netsh advfirewall firewall add rule name="LayerX Discovery" ^
       dir=in action=allow protocol=UDP localport=37020
  
  3. Test from another machine:
     - Ensure both machines are on same network
     - Check if antivirus is blocking connections
     - Verify network is not set to 'Public' (should be 'Private')
  
  4. Quick test:
     - Temporarily disable Windows Firewall
     - Run transceiver.py on both machines
     - If it works, add firewall exception
    """)


def main():
    print("\n" + "="*60)
    print("LayerX Peer Discovery Diagnostic Tool")
    print("="*60)
    
    check_network_info()
    
    # Run tests
    test1_pass = test_broadcast_listener()
    time.sleep(1)
    test2_pass = test_broadcast_sender()
    time.sleep(1)
    test3_pass = test_loopback()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"  Broadcast Listener: {'✓ PASS' if test1_pass else '⚠ FAIL'}")
    print(f"  Broadcast Sender:   {'✓ PASS' if test2_pass else '⚠ FAIL'}")
    print(f"  Loopback Test:      {'✓ PASS' if test3_pass else '⚠ FAIL'}")
    
    if not test3_pass:
        print("\n  ⚠ LIKELY ISSUE: Firewall is blocking UDP broadcasts")
        check_firewall_suggestions()
    elif test1_pass or test2_pass:
        print("\n  ✓ Network communication appears functional")
        print("    If peers still not discovered:")
        print("    - Ensure both machines run transceiver.py")
        print("    - Check they're on the same subnet")
        print("    - Verify router allows broadcasts")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
