#!/usr/bin/env python3
"""
LayerX Secure Messenger - RECEIVER (Manual Peer Management)
Receives and decrypts steganographic messages
"""

import os
import json
import base64
import socket
import struct
import numpy as np
import cv2
import threading
import time
from nacl.public import PrivateKey, PublicKey, Box
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Import LayerX steganography modules
from a3_image_processing import dwt_decompose
from a5_embedding_extraction import extract_from_dwt_bands

# Configuration
CHAT_PORT = 9000
BROADCAST_PORT = 65432
MY_IDENTITY_FILE = 'my_identity.json'
PEERS_FILE = 'peers.json'

def get_local_ip():
    """Get local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def generate_keys(username):
    """Generate keys for new user"""
    from nacl.signing import SigningKey
    from nacl.public import PrivateKey
    
    signing_key = SigningKey.generate()
    encryption_key = PrivateKey.generate()
    
    return {
        "username": username,
        "ip": get_local_ip(),
        "signing_private": base64.b64encode(bytes(signing_key)).decode(),
        "signing_public": base64.b64encode(bytes(signing_key.verify_key)).decode(),
        "x25519_private": base64.b64encode(bytes(encryption_key)).decode(),
        "x25519_public": base64.b64encode(bytes(encryption_key.public_key)).decode()
    }

def load_or_create_identity():
    """Load or create identity"""
    if os.path.exists(MY_IDENTITY_FILE):
        with open(MY_IDENTITY_FILE) as f:
            identity = json.load(f)
        identity["ip"] = get_local_ip()
        with open(MY_IDENTITY_FILE, "w") as f:
            json.dump(identity, f, indent=2)
        print(f"✓ Loaded identity: {identity['username']} ({identity['ip']})")
        return identity
    
    username = input("Enter your username: ").strip()
    identity = generate_keys(username)
    with open(MY_IDENTITY_FILE, "w") as f:
        json.dump(identity, f, indent=2)
    print(f"✓ Created identity: {username}")
    print(f"\n📋 Your Public Keys (share with peers):")
    print(f"   X25519: {identity['x25519_public']}")
    print(f"   Signing: {identity['signing_public']}\n")
    return identity

def load_peers():
    """Load peers list"""
    if os.path.exists(PEERS_FILE):
        with open(PEERS_FILE) as f:
            peers = json.load(f)
            if isinstance(peers, list):
                return peers
            return list(peers.values()) if isinstance(peers, dict) else []
    return []

def save_peers(peers_list):
    """Save peers list"""
    with open(PEERS_FILE, "w") as f:
        json.dump(peers_list, f, indent=2)

def broadcast_identity(my_identity, stop_event):
    """Broadcast identity to network"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    announce = {
        "username": my_identity["username"],
        "ip": my_identity["ip"],
        "x25519_public": my_identity["x25519_public"],
        "signing_public": my_identity["signing_public"]
    }
    message = json.dumps(announce).encode('utf-8')
    
    while not stop_event.is_set():
        try:
            sock.sendto(message, ('<broadcast>', BROADCAST_PORT))
        except:
            pass
        time.sleep(5)
    sock.close()

def listen_for_peers(my_identity, peers_list, stop_event):
    """Listen for peer announcements"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1.0)
    
    try:
        sock.bind(('', BROADCAST_PORT))
    except:
        sock.close()
        return
    
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(4096)
            peer_info = json.loads(data.decode('utf-8'))
            
            # Don't add ourselves
            if peer_info["username"] == my_identity["username"]:
                continue
            
            # Check if already exists
            existing = next((p for p in peers_list if p["ip"] == peer_info["ip"]), None)
            if not existing:
                peers_list.append(peer_info)
                save_peers(peers_list)
                print(f"\n🆕 Discovered: {peer_info['username']} ({peer_info['ip']})")
        except socket.timeout:
            continue
        except:
            continue
    
    sock.close()

def get_peer_by_username(username, peers_list):
    """Find peer by username"""
    return next((p for p in peers_list if p["username"] == username), None)

def receive_stego_image():
    """Receive steganographic image via TCP"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", CHAT_PORT))
    server.listen(1)
    
    print(f"📡 Listening on port {CHAT_PORT}...")
    print("⏳ Waiting for message...\n")
    
    conn, addr = server.accept()
    print(f"📨 Receiving from {addr[0]}...")
    
    # Receive size
    size_data = conn.recv(4)
    if len(size_data) < 4:
        conn.close()
        server.close()
        return None
    
    size = struct.unpack('>I', size_data)[0]
    
    # Receive image data
    data = b''
    remaining = size
    while remaining > 0:
        chunk = conn.recv(min(remaining, 8192))
        if not chunk:
            break
        data += chunk
        remaining -= len(chunk)
    
    conn.close()
    server.close()
    
    # Decode image
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    return img

def extract_and_decrypt(stego_image, my_identity, peers_list):
    """Extract and decrypt message from stego image"""
    # DWT decompose
    bands = dwt_decompose(stego_image)
    
    # Try multiple payload sizes
    for size_bits in [2048, 4096, 8192, 16384]:
        try:
            payload_bits = extract_from_dwt_bands(bands, size_bits)
            
            # Convert bits to bytes
            payload_bytes = bytearray()
            for i in range(0, len(payload_bits), 8):
                byte = int(payload_bits[i:i+8], 2)
                payload_bytes.append(byte)
            
            # Try to decode JSON
            try:
                payload = json.loads(payload_bytes.decode('utf-8', errors='ignore'))
                if "sender" not in payload or "signed_data" not in payload:
                    continue
            except:
                continue
            
            sender_name = payload["sender"]
            signed_data = base64.b64decode(payload["signed_data"])
            
            # Find sender peer
            peer = get_peer_by_username(sender_name, peers_list)
            if not peer:
                print(f"⚠️  Unknown sender: {sender_name}")
                print("   Use sender's IP and /add command to add them\n")
                return
            
            # Verify signature
            verify_key = VerifyKey(base64.b64decode(peer["signing_public"]))
            try:
                encrypted = verify_key.verify(signed_data)
            except BadSignatureError:
                print("❌ Signature verification failed!")
                return
            
            # Decrypt message
            my_priv = PrivateKey(base64.b64decode(my_identity["x25519_private"]))
            peer_pub = PublicKey(base64.b64decode(peer["x25519_public"]))
            box = Box(my_priv, peer_pub)
            
            message = box.decrypt(encrypted).decode('utf-8')
            
            print(f"✅ Message from {sender_name}:")
            print(f"   {message}\n")
            return
            
        except Exception as e:
            continue
    
    print("❌ Failed to extract/decrypt message\n")

def main():
    """Main receiver loop"""
    print("="*70)
    print("LAYERX SECURE MESSENGER - RECEIVER")
    print("="*70)
    
    my_identity = load_or_create_identity()
    peers_list = load_peers()
    
    # Start automatic peer discovery
    stop_event = threading.Event()
    
    broadcast_thread = threading.Thread(
        target=broadcast_identity,
        args=(my_identity, stop_event),
        daemon=True
    )
    listen_thread = threading.Thread(
        target=listen_for_peers,
        args=(my_identity, peers_list, stop_event),
        daemon=True
    )
    
    broadcast_thread.start()
    listen_thread.start()
    
    print("📡 Automatic peer discovery started...")
    time.sleep(2)
    print()
    
    try:
        while True:
            stego_image = receive_stego_image()
            
            if stego_image is None:
                print("❌ Failed to receive image\n")
                continue
            
            print("📦 Extracting... ", end='', flush=True)
            extract_and_decrypt(stego_image, my_identity, peers_list)
            
            print("⏳ Ready for next message...\n")
    
    except KeyboardInterrupt:
        print("\n👋 Stopped")
        stop_event.set()

if __name__ == "__main__":
    main()
