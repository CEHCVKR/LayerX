"""
LayerX Receiver - Stores Encrypted Metadata JSON
Features:
- Receives stego image
- Stores salt & IV in RSA-encrypted JSON file
- Separate decryption tool handles message extraction
"""

import sys
import os
import json
import socket
import threading
import time
from datetime import datetime

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')

from a2_key_management import (
    generate_ecc_keypair, serialize_public_key, serialize_private_key, 
    deserialize_public_key, deserialize_private_key
)
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import hmac

# Configuration
IDENTITY_FILE = "my_identity.json"
BROADCAST_PORT = 37020
DISCOVERY_INTERVAL = 5
peers_list = {}
peers_lock = threading.Lock()
running = True


def load_or_create_identity():
    """Load existing identity or create new one"""
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, 'r') as f:
            data = json.load(f)
            print(f"\n✓ Welcome back, {data['username']}!")
            print(f"✓ Your address: {data['address']}")
            return data
    else:
        print("\n" + "="*60)
        print("FIRST TIME SETUP - LayerX Receiver")
        print("="*60)
        username = input("\nEnter your username: ").strip()
        
        print("\n[*] Generating your ECC keypair (SECP256R1)...")
        private_key, public_key = generate_ecc_keypair()
        
        # Serialize keys
        private_pem = serialize_private_key(private_key)
        public_pem = serialize_public_key(public_key)
        
        # Create unique address
        import hashlib
        address = hashlib.sha256(public_pem).hexdigest()[:16].upper()
        
        identity = {
            "username": username,
            "address": address,
            "private_key": private_pem.decode('utf-8'),
            "public_key": public_pem.decode('utf-8'),
            "created": datetime.now().isoformat()
        }
        
        with open(IDENTITY_FILE, 'w') as f:
            json.dump(identity, f, indent=2)
        
        print(f"\n✅ Identity created!")
        print(f"   Username: {username}")
        print(f"   Address:  {address}")
        print(f"   Keys saved to: {IDENTITY_FILE}")
        
        return identity


def peer_discovery_listener(identity):
    """Listen for peer announcements"""
    global peers_list
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', BROADCAST_PORT))
    sock.settimeout(1)
    
    while running:
        try:
            data, addr = sock.recvfrom(4096)
            announcement = json.loads(data.decode('utf-8'))
            
            # Don't add self
            if announcement['username'] == identity['username']:
                continue
            
            username = announcement['username']
            
            with peers_lock:
                if username not in peers_list:
                    print(f"\n[+] New peer discovered: {username} @ {addr[0]}")
                
                peers_list[username] = {
                    'ip': addr[0],
                    'address': announcement['address'],
                    'public_key': announcement['public_key'],
                    'last_seen': time.time()
                }
        
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"[!] Discovery error: {e}")
    
    sock.close()


def peer_discovery_announcer(identity):
    """Broadcast presence to network"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    announcement = json.dumps({
        'username': identity['username'],
        'address': identity['address'],
        'public_key': identity['public_key']
    }).encode('utf-8')
    
    while running:
        try:
            sock.sendto(announcement, ('<broadcast>', BROADCAST_PORT))
            time.sleep(DISCOVERY_INTERVAL)
        except Exception as e:
            if running:
                print(f"[!] Broadcast error: {e}")
    
    sock.close()


def encrypt_metadata_with_ecdh(metadata_dict, receiver_public_key_pem, sender_private_key, sender_public_key, sender_username):
    """
    Encrypt metadata using ECDH (Perfect Forward Secrecy)
    - Uses ephemeral key for each message
    - Digital signature for authenticity
    - Hybrid encryption (ECDH + AES)
    """
    # 1. Generate ephemeral keypair for this session (Perfect Forward Secrecy)
    ephemeral_private_key, ephemeral_public_key = generate_ecc_keypair()
    
    # 2. Perform ECDH key exchange with receiver's public key
    receiver_pub_key = deserialize_public_key(receiver_public_key_pem.encode('utf-8'))
    shared_key = ephemeral_private_key.exchange(ec.ECDH(), receiver_pub_key)
    
    # 3. Derive AES key from shared secret using HKDF
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'layerx-metadata-encryption',
        backend=default_backend()
    ).derive(shared_key)
    
    # 4. Serialize metadata to JSON
    metadata_json = json.dumps(metadata_dict).encode('utf-8')
    
    # 5. Encrypt metadata with derived AES key
    aes_iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(aes_iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(metadata_json) + encryptor.finalize()
    auth_tag = encryptor.tag
    
    # 6. Create digital signature (sign with sender's private key)
    signature_data = encrypted_data + aes_iv + serialize_public_key(ephemeral_public_key)
    signature = sender_private_key.sign(
        signature_data,
        ec.ECDSA(hashes.SHA256())
    )
    
    # 7. Create encrypted package
    encrypted_package = {
        'version': '2.0',
        'encryption_type': 'ECDH-AES-256-GCM',
        'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
        'aes_iv': base64.b64encode(aes_iv).decode('utf-8'),
        'auth_tag': base64.b64encode(auth_tag).decode('utf-8'),
        'ephemeral_public_key': base64.b64encode(serialize_public_key(ephemeral_public_key)).decode('utf-8'),
        'sender_public_key': base64.b64encode(sender_public_key).decode('utf-8'),
        'sender_username': sender_username,
        'signature': base64.b64encode(signature).decode('utf-8'),
        'timestamp': datetime.now().isoformat()
    }
    
    return encrypted_package


def receive_file_listener(identity, port=37021):
    """Listen for incoming stego images and save encrypted metadata"""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', port))
    server_sock.listen(1)
    server_sock.settimeout(1)
    
    print(f"[*] File listener active on port {port}")
    
    while running:
        try:
            conn, addr = server_sock.accept()
            print(f"\n[+] INCOMING FILE from {addr[0]}...")
            
            # Receive metadata
            import struct
            
            # Salt
            salt_len = struct.unpack('!I', conn.recv(4))[0]
            salt = conn.recv(salt_len)
            
            # IV
            iv_len = struct.unpack('!I', conn.recv(4))[0]
            iv = conn.recv(iv_len)
            
            # Payload size
            payload_bits_length = struct.unpack('!I', conn.recv(4))[0]
            
            # Image size
            image_size = struct.unpack('!I', conn.recv(4))[0]
            
            # Receive image data
            image_data = b''
            while len(image_data) < image_size:
                chunk = conn.recv(min(4096, image_size - len(image_data)))
                if not chunk:
                    break
                image_data += chunk
            
            conn.close()
            
            # Save received stego image with better naming
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sender_ip = addr[0].replace(':', '_').replace('.', '_')
            
            # Create base filename: sender-ip_timestamp
            base_filename = f"{sender_ip}_{timestamp}"
            stego_filename = f"{base_filename}.png"
            
            with open(stego_filename, 'wb') as f:
                f.write(image_data)
            
            print(f"[+] Stego image saved: {stego_filename}")
            print(f"[+] Image size: {len(image_data)} bytes")
            
            # Create metadata JSON with encryption parameters
            metadata = {
                'stego_image': stego_filename,
                'salt': base64.b64encode(salt).decode('utf-8'),
                'iv': base64.b64encode(iv).decode('utf-8'),
                'payload_bits_length': payload_bits_length,
                'sender_ip': addr[0],
                'received_timestamp': timestamp,
                'receiver_address': identity['address']
            }
            
            # Encrypt metadata with receiver's public key (simplified - using AES)
            encrypted_metadata = encrypt_metadata_with_public_key(metadata, identity['public_key'])
            
            # Save encrypted metadata JSON with matching filename
            metadata_filename = f"{base_filename}.json"
            with open(metadata_filename, 'w') as f:
                json.dump(encrypted_metadata, f, indent=2)
            
            print(f"[+] Encrypted metadata saved: {metadata_filename}")
            print(f"\n{'='*70}")
            print("[SUCCESS] STEGO IMAGE & ENCRYPTED METADATA RECEIVED!")
            print(f"{'='*70}")
            print(f"[*] Stego Image: {stego_filename}")
            print(f"[*] Metadata: {metadata_filename}")
            print(f"[*] Use 'decrypt_tool.py' to extract the hidden message")
            print(f"{'='*70}\n")
            
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"[!] File receive error: {e}")
                import traceback
                traceback.print_exc()
    
    server_sock.close()


def list_peers():
    """Display available peers"""
    with peers_lock:
        if not peers_list:
            print("\n[!] No peers discovered yet. Wait a few seconds...")
            return None
        
        print("\n" + "="*60)
        print("AVAILABLE PEERS")
        print("="*60)
        for i, (username, info) in enumerate(peers_list.items(), 1):
            print(f"{i}. {username} ({info['address'][:8]}...) @ {info['ip']}")
        print("="*60)
        
        return list(peers_list.keys())


def main():
    """Main receiver application"""
    global running
    
    # Load or create identity
    identity = load_or_create_identity()
    
    # Start peer discovery threads
    listener_thread = threading.Thread(target=peer_discovery_listener, args=(identity,), daemon=True)
    announcer_thread = threading.Thread(target=peer_discovery_announcer, args=(identity,), daemon=True)
    
    # Start file receiver thread
    file_receiver_thread = threading.Thread(target=receive_file_listener, args=(identity,), daemon=True)
    
    listener_thread.start()
    announcer_thread.start()
    file_receiver_thread.start()
    
    print("\n" + "="*60)
    print("LAYERX RECEIVER - Waiting for encrypted messages")
    print("="*60)
    print("Commands:")
    print("  peers   - List discovered peers")
    print("  quit    - Exit application")
    print("="*60)
    print("\n[*] Listening for incoming stego images...")
    print("[*] Encrypted metadata will be saved automatically")
    
    try:
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'peers':
                list_peers()
            
            elif cmd == 'quit':
                print("\n[*] Shutting down...")
                break
            
            else:
                print("[!] Unknown command. Use: peers, quit")
    
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    
    finally:
        running = False
        time.sleep(0.5)
        print("✓ Goodbye!")


if __name__ == "__main__":
    main()
