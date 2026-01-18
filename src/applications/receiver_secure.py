"""
LayerX Secure Receiver - Enhanced Security Version
Features:
- ECDH decryption (Perfect Forward Secrecy)
- Digital signature verification
- AES-256-GCM decryption
- Self-destruct message handling
- Message history logging
"""

import sys
import os
import json
import socket
import threading
import time
from datetime import datetime, timedelta

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')

from a2_key_management import (
    generate_ecc_keypair, serialize_public_key, serialize_private_key,
    deserialize_public_key, deserialize_private_key
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import struct

# Configuration
IDENTITY_FILE = "my_identity.json"
HISTORY_FILE = "message_history.json"
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
        print("FIRST TIME SETUP - LayerX Secure Receiver")
        print("="*60)
        username = input("\nEnter your username: ").strip()
        
        print("\n[*] Generating your ECC keypair (SECP256R1)...")
        private_key, public_key = generate_ecc_keypair()
        
        private_pem = serialize_private_key(private_key)
        public_pem = serialize_public_key(public_key)
        
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


def decrypt_and_verify_metadata(encrypted_package, receiver_identity):
    """
    Decrypt metadata using ECDH and verify digital signature
    Returns: (metadata_dict, sender_verified)
    """
    # 1. Extract components
    ciphertext = base64.b64decode(encrypted_package['encrypted_data'])
    aes_iv = base64.b64decode(encrypted_package['aes_iv'])
    auth_tag = base64.b64decode(encrypted_package['auth_tag'])
    ephemeral_pub_key_bytes = base64.b64decode(encrypted_package['ephemeral_public_key'])
    sender_pub_key_bytes = base64.b64decode(encrypted_package['sender_public_key'])
    signature = base64.b64decode(encrypted_package['signature'])
    
    # 2. Deserialize keys
    ephemeral_pub_key = deserialize_public_key(ephemeral_pub_key_bytes)
    sender_pub_key = deserialize_public_key(sender_pub_key_bytes)
    receiver_private_key = deserialize_private_key(receiver_identity['private_key'].encode('utf-8'))
    
    # 3. Verify digital signature
    signature_data = ciphertext + aes_iv + auth_tag
    try:
        sender_pub_key.verify(signature, signature_data, ec.ECDSA(hashes.SHA256()))
        sender_verified = True
        print("[+] ✓ Digital signature verified - Sender authentic!")
    except Exception as e:
        print(f"[!] ✗ Digital signature verification FAILED: {e}")
        sender_verified = False
        raise Exception("Sender authentication failed!")
    
    # 4. Perform ECDH to derive shared secret
    shared_secret = receiver_private_key.exchange(ec.ECDH(), ephemeral_pub_key)
    
    # 5. Derive decryption key
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'layerx-metadata-v2',
        backend=default_backend()
    ).derive(shared_secret)
    
    # 6. Decrypt with AES-GCM
    cipher = Cipher(
        algorithms.AES(derived_key),
        modes.GCM(aes_iv, auth_tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # 7. Parse metadata
    metadata = json.loads(plaintext.decode('utf-8'))
    
    return metadata, sender_verified


def log_message_to_history(metadata, encrypted_package_path, sender_verified):
    """Log received message to history file"""
    if not os.path.exists(HISTORY_FILE):
        history = {'messages': []}
    else:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    
    history_entry = {
        'id': len(history['messages']) + 1,
        'sender_username': metadata.get('sender_username', 'Unknown'),
        'sender_address': metadata.get('sender_address', 'Unknown'),
        'timestamp': metadata.get('timestamp'),
        'received_timestamp': datetime.now().isoformat(),
        'stego_image': metadata.get('stego_image'),
        'metadata_file': encrypted_package_path,
        'sender_verified': sender_verified,
        'view_count': 0,
        'self_destruct': metadata.get('self_destruct'),
        'status': 'unread'
    }
    
    history['messages'].append(history_entry)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"[+] Message logged to history (ID: {history_entry['id']})")


def receive_file_listener(identity, port=37021):
    """Listen for incoming secure transmissions"""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', port))
    server_sock.listen(1)
    server_sock.settimeout(1)
    
    print(f"[*] Secure file listener active on port {port}")
    
    while running:
        try:
            conn, addr = server_sock.accept()
            print(f"\n[+] INCOMING SECURE TRANSMISSION from {addr[0]}...")
            
            # Receive metadata size
            metadata_size_bytes = conn.recv(4)
            if len(metadata_size_bytes) < 4:
                continue
            metadata_size = struct.unpack('!I', metadata_size_bytes)[0]
            
            # Receive metadata
            metadata_json = b''
            while len(metadata_json) < metadata_size:
                chunk = conn.recv(min(4096, metadata_size - len(metadata_json)))
                if not chunk:
                    break
                metadata_json += chunk
            
            encrypted_package = json.loads(metadata_json.decode('utf-8'))
            
            # Receive image size
            image_size_bytes = conn.recv(4)
            if len(image_size_bytes) < 4:
                continue
            image_size = struct.unpack('!I', image_size_bytes)[0]
            
            # Receive image data
            image_data = b''
            while len(image_data) < image_size:
                chunk = conn.recv(min(4096, image_size - len(image_data)))
                if not chunk:
                    break
                image_data += chunk
            
            conn.close()
            
            print(f"[+] Transmission complete ({len(image_data)} bytes)")
            
            # Decrypt and verify metadata
            print(f"[*] Decrypting metadata package...")
            metadata, sender_verified = decrypt_and_verify_metadata(encrypted_package, identity)
            
            # Generate filename with username, timestamp, and IP
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            username = metadata.get('sender_username', 'unknown')
            sender_ip = metadata.get('sender_address', addr[0]).replace(':', '_').replace('.', '_')
            
            # Create base filename: username_timestamp_ip
            base_filename = f"{username}_{timestamp}_{sender_ip}"
            stego_filename = f"{base_filename}.png"
            metadata_filename = f"{base_filename}.json"
            
            # Save stego image
            with open(stego_filename, 'wb') as f:
                f.write(image_data)
            
            # Update metadata with actual filename
            metadata['stego_image'] = stego_filename
            
            # Save encrypted package with updated stego path
            encrypted_package['decrypted_stego_path'] = stego_filename
            with open(metadata_filename, 'w') as f:
                json.dump({
                    'encrypted_package': encrypted_package,
                    'metadata': metadata,  # Also store decrypted for quick access
                    'sender_verified': sender_verified
                }, f, indent=2)
            
            print(f"\n{'='*70}")
            print("[SUCCESS] SECURE MESSAGE RECEIVED!")
            print(f"{'='*70}")
            print(f"[*] From: {metadata.get('sender_username')} ({metadata.get('sender_address')})")
            print(f"[*] Verified: {'✓ YES' if sender_verified else '✗ NO'}")
            print(f"[*] Protocol: {encrypted_package.get('protocol')}")
            print(f"[*] Stego Image: {stego_filename}")
            print(f"[*] Metadata: {metadata_filename}")
            
            if metadata.get('self_destruct'):
                sd = metadata['self_destruct']
                print(f"[*] Self-Destruct: {sd['type']}")
                if sd['type'] == 'timer':
                    print(f"    └─ Will delete in {sd['minutes']} minutes")
                elif sd['type'] == 'view_count':
                    print(f"    └─ Will delete after {sd['max_views']} view(s)")
            
            print(f"[*] Use stego_viewer.py to view the message")
            print(f"{'='*70}\n")
            
            # Log to history
            log_message_to_history(metadata, metadata_filename, sender_verified)
            
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"[!] Reception error: {e}")
                import traceback
                traceback.print_exc()
    
    server_sock.close()


def list_peers():
    """Display available peers"""
    with peers_lock:
        if not peers_list:
            print("\n[!] No peers discovered yet")
            return None
        
        print("\n" + "="*60)
        print("AVAILABLE PEERS")
        print("="*60)
        for i, (username, info) in enumerate(peers_list.items(), 1):
            print(f"{i}. {username} ({info['address'][:8]}...) @ {info['ip']}")
        print("="*60)
        
        return list(peers_list.keys())


def show_message_history():
    """Display message history"""
    if not os.path.exists(HISTORY_FILE):
        print("\n[!] No message history found")
        return
    
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    if not history['messages']:
        print("\n[!] No messages in history")
        return
    
    print("\n" + "="*70)
    print("MESSAGE HISTORY")
    print("="*70)
    for msg in history['messages']:
        status_icon = "📨" if msg['status'] == 'unread' else "✅"
        verified_icon = "✓" if msg['sender_verified'] else "✗"
        sd_icon = "🔥" if msg.get('self_destruct') else ""
        
        print(f"{status_icon} [{msg['id']}] {verified_icon} {msg['sender_username']} - {msg['timestamp'][:19]} {sd_icon}")
        print(f"    Views: {msg['view_count']} | File: {msg['metadata_file']}")
    print("="*70)


def main():
    """Main receiver application"""
    global running
    
    identity = load_or_create_identity()
    
    listener_thread = threading.Thread(target=peer_discovery_listener, args=(identity,), daemon=True)
    announcer_thread = threading.Thread(target=peer_discovery_announcer, args=(identity,), daemon=True)
    file_receiver_thread = threading.Thread(target=receive_file_listener, args=(identity,), daemon=True)
    
    listener_thread.start()
    announcer_thread.start()
    file_receiver_thread.start()
    
    print("\n" + "="*60)
    print("LAYERX SECURE RECEIVER - Listening")
    print("="*60)
    print("Commands: peers, history, quit")
    print("="*60)
    
    try:
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'peers':
                list_peers()
            
            elif cmd == 'history':
                show_message_history()
            
            elif cmd == 'quit':
                print("\n[*] Shutting down...")
                break
            
            else:
                print("[!] Unknown command")
    
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted")
    
    finally:
        running = False
        time.sleep(0.5)
        print("✓ Goodbye!")


if __name__ == "__main__":
    main()
