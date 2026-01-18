#!/usr/bin/env python3
"""
LayerX Secure Messenger - SENDER (Manual Peer Management)
Encrypted messaging with steganographic embedding
"""

import os
import json
import base64
import socket
import struct
import cv2
import threading
import time
from nacl.public import PrivateKey, PublicKey, Box
from nacl.signing import SigningKey

# Import LayerX steganography modules
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
from a5_embedding_extraction import embed_in_dwt_bands

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
            existing = get_peer_by_ip(peer_info["ip"], peers_list)
            if not existing:
                peers_list.append(peer_info)
                save_peers(peers_list)
                print(f"\n🆕 Discovered: {peer_info['username']} ({peer_info['ip']})")
                print("Command: ", end='', flush=True)
        except socket.timeout:
            continue
        except:
            continue
    
    sock.close()

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

def get_peer_by_ip(ip, peers_list):
    """Find peer by IP address"""
    return next((p for p in peers_list if p["ip"] == ip), None)

def show_my_keys(my_identity):
    """Display public keys for sharing"""
    print("\n" + "="*70)
    print("YOUR PUBLIC KEYS (Share these with peers)")
    print("="*70)
    print(f"Username: {my_identity['username']}")
    print(f"IP: {my_identity['ip']}")
    print(f"X25519 Public: {my_identity['x25519_public']}")
    print(f"Signing Public: {my_identity['signing_public']}")
    print("="*70 + "\n")

def add_peer_interactive(peers_list):
    """Add peer manually"""
    print("\n--- Add New Peer ---")
    username = input("Peer username: ").strip()
    ip = input("Peer IP: ").strip()
    x25519_pub = input("Peer X25519 public key: ").strip()
    signing_pub = input("Peer signing public key: ").strip()
    
    if not all([username, ip, x25519_pub, signing_pub]):
        print("❌ All fields required!\n")
        return
    
    # Check if already exists
    existing = get_peer_by_ip(ip, peers_list)
    if existing:
        print(f"⚠️  Peer {existing['username']} ({ip}) already exists!\n")
        return
    
    peer = {
        "username": username,
        "ip": ip,
        "x25519_public": x25519_pub,
        "signing_public": signing_pub
    }
    
    peers_list.append(peer)
    save_peers(peers_list)
    print(f"✓ Added peer: {username} ({ip})\n")

def encrypt_message(message, peer, my_identity):
    """Encrypt message with NaCl Box"""
    my_priv = PrivateKey(base64.b64decode(my_identity["x25519_private"]))
    peer_pub = PublicKey(base64.b64decode(peer["x25519_public"]))
    box = Box(my_priv, peer_pub)
    
    # Encrypt message
    encrypted = box.encrypt(message.encode('utf-8'))
    
    # Sign encrypted data
    signing_key = SigningKey(base64.b64decode(my_identity["signing_private"]))
    signed_data = signing_key.sign(encrypted)
    
    # Create payload
    payload = {
        "sender": my_identity["username"],
        "signed_data": base64.b64encode(signed_data).decode()
    }
    
    return json.dumps(payload).encode('utf-8')

def embed_and_send(payload, peer_ip, cover_image="test_lena.png"):
    """Embed payload in image and send"""
    # Load and decompose image
    img = read_image(cover_image)
    bands = dwt_decompose(img)
    
    # Convert payload to bits
    payload_bits = ''.join(format(byte, '08b') for byte in payload)
    
    # Embed in DWT bands
    stego_bands = embed_in_dwt_bands(payload_bits, bands)
    
    # Reconstruct stego image
    stego_image = dwt_reconstruct(stego_bands)
    
    # Encode to PNG
    _, buffer = cv2.imencode('.png', stego_image)
    image_bytes = buffer.tobytes()
    
    # Send via TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((peer_ip, CHAT_PORT))
    sock.sendall(struct.pack('>I', len(image_bytes)))
    sock.sendall(image_bytes)
    sock.close()

def main():
    """Main sender loop"""
    print("="*70)
    print("LAYERX SECURE MESSENGER - SENDER")
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
    
    print("\nCommands:")
    print("  /list         - Show peers")
    print("  /add          - Add new peer")
    print("  /send <ip>    - Send message to peer")
    print("  /keys         - Show my public keys")
    print("  /image <path> - Change cover image")
    print("  /quit         - Exit\n")
    
    cover_image = "test_lena.png"
    
    try:
        while True:
            cmd = input("Command: ").strip()
            
            if not cmd:
                continue
            
            if cmd == "/list":
                if peers_list:
                    print("\n📋 Peers:")
                    for i, p in enumerate(peers_list, 1):
                        print(f"   {i}. {p['username']} ({p['ip']})")
                    print()
                else:
                    print("⚠️  No peers added yet. Use /add\n")
            
            elif cmd == "/add":
                add_peer_interactive(peers_list)
            
            elif cmd == "/keys":
                show_my_keys(my_identity)
            
            elif cmd.startswith("/send "):
                ip = cmd.split()[1] if len(cmd.split()) > 1 else None
                if not ip:
                    print("❌ Usage: /send <ip>")
                    continue
                
                peer = get_peer_by_ip(ip, peers_list)
                if not peer:
                    print(f"❌ Peer not found: {ip}")
                    print("   Use /add to add peer first\n")
                    continue
                
                message = input(f"Message to {peer['username']}: ").strip()
                if not message:
                    continue
                
                try:
                    print("📦 Encrypting... ", end='', flush=True)
                    payload = encrypt_message(message, peer, my_identity)
                    print("✓")
                    
                    print("🖼️  Embedding... ", end='', flush=True)
                    embed_and_send(payload, peer["ip"], cover_image)
                    print("✓")
                    
                    print(f"✅ Sent to {peer['username']} ({ip})\n")
                except Exception as e:
                    print(f"❌ Failed: {e}\n")
            
            elif cmd.startswith("/image "):
                path = cmd.split(maxsplit=1)[1]
                if os.path.exists(path):
                    cover_image = path
                    print(f"✓ Cover image: {path}\n")
                else:
                    print(f"❌ File not found: {path}\n")
            
            elif cmd == "/quit":
                print("👋 Goodbye!")
                stop_event.set()
                break
            
            else:
                print("❌ Unknown command\n")
    
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
        stop_event.set()

if __name__ == "__main__":
    main()
