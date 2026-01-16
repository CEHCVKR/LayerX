"""
LayerX Transceiver - Send & Receive Images Only
- Creates stego images with encrypted messages
- Sends/receives stego images between peers
- For decryption, use: applications/stego_viewer.py
"""

import sys
import os
import json
import socket
import threading
import time
from datetime import datetime

sys.path.append('core_modules')

from a1_encryption import encrypt_message, decrypt_message, encrypt_with_aes_key, decrypt_with_aes_key
from a2_key_management import (
    generate_ecc_keypair, serialize_public_key, serialize_private_key,
    deserialize_public_key, deserialize_private_key,
    encrypt_aes_key_with_ecc, decrypt_aes_key_with_ecc
)
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed_in_dwt_bands_color, extract_from_dwt_bands_color, bytes_to_bits, bits_to_bytes
import numpy as np
import cv2
import secrets

IDENTITY_FILE = "my_identity.json"
BROADCAST_PORT = 37020
FILE_TRANSFER_PORT = 37021
DISCOVERY_INTERVAL = 5
peers_list = {}
peers_lock = threading.Lock()
running = True


def write_image(path, img):
    import numpy as np
    cv2.imwrite(path, img.astype(np.uint8))


def load_or_create_identity():
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, 'r') as f:
            data = json.load(f)
            print(f"\nWelcome back, {data['username']}!")
            return data
    else:
        print("\n" + "="*60)
        print("FIRST TIME SETUP - LayerX Transceiver")
        print("="*60)
        username = input("\nEnter your username: ").strip()
        
        print("\n[*] Generating ECC keypair...")
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
        
        print(f"\nIdentity created: {username} ({address})")
        return identity


def peer_discovery_listener(identity):
    global peers_list
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', BROADCAST_PORT))
    sock.settimeout(1.0)
    
    print(f"[*] Peer discovery active on port {BROADCAST_PORT}")
    
    while running:
        try:
            data, addr = sock.recvfrom(4096)
            peer_info = json.loads(data.decode('utf-8'))
            
            if peer_info['address'] == identity['address']:
                continue
            
            with peers_lock:
                username = peer_info['username']
                if username not in peers_list:
                    print(f"\n[+] NEW PEER: {username} at {addr[0]}")
                
                peers_list[username] = {
                    'ip': addr[0],
                    'address': peer_info['address'],
                    'public_key': peer_info['public_key'],
                    'last_seen': time.time()
                }
        except socket.timeout:
            continue
        except Exception:
            if running:
                pass
    sock.close()


def peer_discovery_announcer(identity):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    announcement = json.dumps({
        'username': identity['username'],
        'address': identity['address'],
        'public_key': identity['public_key']
    }).encode('utf-8')
    
    broadcast_addresses = ['255.255.255.255', '10.10.198.255']
    
    while running:
        try:
            for broadcast_addr in broadcast_addresses:
                try:
                    sock.sendto(announcement, (broadcast_addr, BROADCAST_PORT))
                except:
                    pass
            
            with peers_lock:
                current_time = time.time()
                stale = [u for u, p in peers_list.items() if current_time - p['last_seen'] > 20]
                for username in stale:
                    print(f"\n[-] Peer {username} went offline")
                    del peers_list[username]
            
            time.sleep(DISCOVERY_INTERVAL)
        except Exception:
            if running:
                pass
    sock.close()


def file_transfer_listener(identity):
    global running
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', FILE_TRANSFER_PORT))
    server_sock.listen(5)
    server_sock.settimeout(1.0)
    
    print(f"[*] File transfer listener on port {FILE_TRANSFER_PORT}")
    
    while running:
        try:
            client_sock, addr = server_sock.accept()
            
            metadata_size = int.from_bytes(client_sock.recv(4), 'big')
            metadata = json.loads(client_sock.recv(metadata_size).decode('utf-8'))
            
            # Skip if receiving own message (loopback)
            if metadata.get('sender_address') == identity['address']:
                client_sock.close()
                continue
            
            print(f"\n[RX] Receiving from {metadata['sender']}: {metadata['filename']}")
            
            # Verify digital signature if present
            if 'signature' in metadata and 'sender_public_key' in metadata:
                try:
                    sender_pub_key = deserialize_public_key(metadata['sender_public_key'].encode('utf-8'))
                    signature = bytes.fromhex(metadata['signature'])
                    
                    # Receive file data first to verify
                    file_data = b''
                    remaining = metadata['size']
                    while remaining > 0:
                        chunk = client_sock.recv(min(4096, remaining))
                        if not chunk:
                            break
                        file_data += chunk
                        remaining -= len(chunk)
                    
                    # Verify signature
                    signature_data = (
                        metadata['sender'].encode() + 
                        metadata['filename'].encode() + 
                        metadata['timestamp'].encode() +
                        file_data[:1000]  # First 1KB
                    )
                    sender_pub_key.verify(signature, signature_data, ec.ECDSA(hashes.SHA256()))
                    print("[✓] Signature verified - message authentic!")
                    
                except Exception as e:
                    print(f"[!] Signature verification FAILED: {e}")
                    print("[!] Message rejected - potential tampering detected!")
                    client_sock.close()
                    continue
            else:
                # No signature - receive normally
                file_data = b''
                remaining = metadata['size']
                while remaining > 0:
                    chunk = client_sock.recv(min(4096, remaining))
                    if not chunk:
                        break
                    file_data += chunk
                    remaining -= len(chunk)
            
            client_sock.close()
            
            filename = f"received_{metadata['filename']}"
            with open(filename, 'wb') as f:
                f.write(file_data)
            
            print(f"[OK] Saved as: {filename}")
            
            # Store metadata for stego_viewer to use
            try:
                if metadata['filename'].startswith('stego_') and 'encrypted_aes_key' in metadata:
                    metadata_file = filename.replace('.png', '_metadata.json')
                    
                    metadata_to_save = {
                        'sender': metadata['sender'],
                        'sender_username': metadata['sender'],  # For stego_viewer compatibility
                        'sender_address': metadata.get('sender_address', 'Unknown'),
                        'encrypted_aes_key': metadata['encrypted_aes_key'],
                        'salt': metadata['salt'],
                        'iv': metadata['iv'],
                        'payload_bits_length': metadata['payload_bits'],  # stego_viewer expects payload_bits_length
                        'stego_image': filename,  # Path to received stego image
                        'timestamp': metadata['timestamp'],
                        'signature_verified': 'signature' in metadata
                    }
                    
                    # Add self-destruct info if present
                    if 'self_destruct' in metadata:
                        metadata_to_save['self_destruct'] = metadata['self_destruct']
                        sd = metadata['self_destruct']
                        if sd['type'] == 'one_time':
                            print(f"[!] WARNING: Message will self-destruct after 1 view!")
                        elif sd['type'] == 'timer':
                            print(f"[!] WARNING: Message will self-destruct in {sd['minutes']} minutes!")
                        elif sd['type'] == 'view_count':
                            print(f"[!] WARNING: Message will self-destruct after {sd['max_views']} views!")
                    
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata_to_save, f, indent=2)
                    
                    print(f"[i] Metadata saved: {metadata_file}")
                    print("[i] To decrypt: python applications/stego_viewer.py")
            except Exception as e:
                print(f"[ERROR] Failed to save metadata: {e}")
            
        except socket.timeout:
            continue
        except Exception:
            if running:
                pass
    server_sock.close()


def send_file_to_peer(peer_ip, filepath, sender_name, sender_identity, metadata_extra=None):
    """Send file to a peer with digital signature"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((peer_ip, FILE_TRANSFER_PORT))
        
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        metadata = {
            'sender': sender_name,
            'sender_address': sender_identity['address'],
            'sender_public_key': sender_identity['public_key'],
            'filename': os.path.basename(filepath),
            'size': len(file_data),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add extra metadata (for ECC encryption data)
        if metadata_extra:
            metadata.update(metadata_extra)
        
        # Create digital signature
        sender_private_key = deserialize_private_key(sender_identity['private_key'].encode('utf-8'))
        signature_data = (
            metadata['sender'].encode() + 
            metadata['filename'].encode() + 
            metadata['timestamp'].encode() +
            file_data[:1000]  # Sign first 1KB of file
        )
        signature = sender_private_key.sign(signature_data, ec.ECDSA(hashes.SHA256()))
        metadata['signature'] = signature.hex()
        
        metadata_json = json.dumps(metadata).encode('utf-8')
        sock.send(len(metadata_json).to_bytes(4, 'big'))
        sock.send(metadata_json)
        sock.sendall(file_data)
        sock.close()
        
        print(f"[OK] Sent to {peer_ip}")
        return True
    except Exception as e:
        print(f"[FAIL] Transfer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_stego_image_with_ecc(message, receiver_public_key_pem, cover_path, output_path):
    """Create stego image with ECC-encrypted message"""
    print("\n[*] Creating stego image with ECC encryption...")
    
    # Generate random AES session key
    aes_session_key = secrets.token_bytes(32)  # 256-bit AES key
    
    # Encrypt message with AES session key (direct, no PBKDF2)
    encrypted_data, salt, iv = encrypt_with_aes_key(message, aes_session_key)
    
    # Encrypt AES session key with receiver's ECC public key
    receiver_public_key = deserialize_public_key(receiver_public_key_pem.encode('utf-8'))
    encrypted_aes_key = encrypt_aes_key_with_ecc(aes_session_key, receiver_public_key)
    
    print(f"  - Message encrypted with AES-256 (direct)")
    print(f"  - AES key encrypted with receiver's ECC public key")
    
    # Compress and create payload
    compressed_data, huffman_tree = compress_huffman(encrypted_data)
    payload = create_payload(encrypted_data, huffman_tree, compressed_data)
    payload_bits = bytes_to_bits(payload)
    payload_bit_length = len(payload_bits)
    
    # Embed in image
    cover_img = read_image_color(cover_path)
    bands = dwt_decompose_color(cover_img, levels=2)
    stego_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
    stego_img = dwt_reconstruct_color(stego_bands)
    write_image(output_path, stego_img)
    
    psnr_val = psnr_color(cover_img, stego_img)
    print(f"[OK] PSNR: {psnr_val:.2f} dB | Output: {output_path}")
    
    return encrypted_aes_key, salt, iv, payload_bit_length


def list_peers():
    with peers_lock:
        if not peers_list:
            print("\n[i] No peers discovered yet")
            return None
        
        print("\n" + "="*60)
        print("AVAILABLE PEERS:")
        print("="*60)
        for i, (username, info) in enumerate(peers_list.items(), 1):
            print(f"{i}. {username} - {info['ip']}")
        print("="*60)
        return peers_list


def send_message(identity):
    peers = list_peers()
    if not peers:
        return
    
    try:
        choice = int(input("\nSelect peer: "))
        peer_username = list(peers.keys())[choice - 1]
        peer_info = peers[peer_username]
    except (ValueError, IndexError):
        print("[!] Invalid selection")
        return
    
    message = input("\nEnter message: ")
    
    # Self-destruct options
    print("\n[?] Self-destruct options:")
    print("  1. No self-destruct (default)")
    print("  2. Delete after reading (1 view)")
    print("  3. Delete after time (minutes)")
    print("  4. Delete after N views")
    
    sd_choice = input("Choose option (1-4) [default: 1]: ").strip() or "1"
    self_destruct_config = None
    
    if sd_choice == "2":
        self_destruct_config = {'type': 'one_time', 'max_views': 1}
    elif sd_choice == "3":
        minutes = int(input("Delete after how many minutes? "))
        self_destruct_config = {'type': 'timer', 'minutes': minutes}
    elif sd_choice == "4":
        max_views = int(input("Delete after how many views? "))
        self_destruct_config = {'type': 'view_count', 'max_views': max_views}
    
    # Ask for cover image path
    cover_image = input("Enter cover image path (or press Enter for 'cover.png'): ").strip()
    
    # Use default if empty
    if not cover_image:
        cover_image = "cover.png"
    
    if not os.path.exists(cover_image):
        print(f"[!] Cover image not found: {cover_image}")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stego_path = f"stego_to_{peer_username}_{timestamp}.png"
    
    try:
        # Create stego image with ECC encryption
        encrypted_aes_key, salt, iv, payload_bits = create_stego_image_with_ecc(
            message, 
            peer_info['public_key'],
            cover_image,
            stego_path
        )
        
        # Prepare metadata for ECC decryption
        metadata_extra = {
            'encrypted_aes_key': encrypted_aes_key.hex(),
            'salt': salt.hex(),
            'iv': iv.hex(),
            'payload_bits': payload_bits
        }
        
        # Add self-destruct config if set
        if self_destruct_config:
            metadata_extra['self_destruct'] = self_destruct_config
        
        # Send file with ECC metadata and digital signature
        send_file_to_peer(peer_info['ip'], stego_path, identity['username'], identity, metadata_extra)
        
    except Exception as e:
        print(f"[!] Failed: {e}")


def list_received():
    import glob
    from datetime import datetime
    
    received = glob.glob("received_stego_*.png")
    
    if not received:
        print("\n[i] No received stego images")
        return
    
    print("\n" + "="*60)
    print("RECEIVED STEGO IMAGES:")
    print("="*60)
    
    for i, f in enumerate(received, 1):
        size = os.path.getsize(f)
        
        # Try to extract sender and timestamp from filename
        # Format: received_stego_to_{peer}_{timestamp}.png
        sender = "Unknown"
        date_time = "Unknown"
        
        try:
            # Remove 'received_' prefix and '.png' suffix
            parts = f.replace("received_", "").replace(".png", "")
            
            # Split by underscore
            if "stego_to_" in parts:
                # Extract sender and timestamp
                after_to = parts.split("stego_to_")[1]
                parts_list = after_to.rsplit("_", 2)  # Split from right to get last 2 parts
                
                if len(parts_list) >= 3:
                    sender = parts_list[0]
                    timestamp_str = parts_list[1] + parts_list[2]  # YYYYMMDD_HHMMSS
                    
                    # Parse timestamp
                    try:
                        dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        date_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        # Try file modification time
                        mtime = os.path.getmtime(f)
                        dt = datetime.fromtimestamp(mtime)
                        date_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                        
        except Exception:
            # Fallback to file modification time
            try:
                mtime = os.path.getmtime(f)
                dt = datetime.fromtimestamp(mtime)
                date_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        print(f"\n{i}. {f}")
        print(f"   From: {sender}")
        print(f"   Date: {date_time}")
        print(f"   Size: {size:,} bytes")
    
    print("\n" + "="*60)
    print("[i] To decrypt: python applications/stego_viewer.py")


def send_file():
    peers = list_peers()
    if not peers:
        return
    
    try:
        choice = int(input("\nSelect peer: "))
        peer_username = list(peers.keys())[choice - 1]
        peer_info = peers[peer_username]
    except (ValueError, IndexError):
        print("[!] Invalid selection")
        return
    
    filepath = input("\nFile path: ").strip()
    
    if not os.path.exists(filepath):
        print(f"[!] File not found")
        return
    
    send_file_to_peer(peer_info['ip'], filepath, peer_username)


def main_menu(identity):
    while True:
        print("\n" + "="*60)
        print(f"LayerX Transceiver - {identity['username']}")
        print("="*60)
        print("send  - Send encrypted message as stego image")
        print("peers - List available peers")
        print("list  - List received stego images")
        print("quit  - Exit")
        print("="*60)
        
        choice = input("\nCommand: ").strip().lower()
        
        if choice == 'send':
            send_message(identity)
        elif choice == 'peers':
            list_peers()
        elif choice == 'list':
            list_received()
        elif choice == 'quit':
            print("\n[*] Shutting down...")
            global running
            running = False
            break
        else:
            print("[!] Invalid command. Use: send, peers, list, quit")


def main():
    global running
    
    print("\n" + "="*60)
    print("LayerX Transceiver - P2P Stego Transfer")
    print("="*60)
    
    identity = load_or_create_identity()
    
    threads = [
        threading.Thread(target=peer_discovery_listener, args=(identity,), daemon=True),
        threading.Thread(target=peer_discovery_announcer, args=(identity,), daemon=True),
        threading.Thread(target=file_transfer_listener, args=(identity,), daemon=True)
    ]
    
    for t in threads:
        t.start()
    
    print("\n[*] Network services started")
    print("[*] Discovering peers...")
    time.sleep(2)
    
    try:
        main_menu(identity)
    except KeyboardInterrupt:
        print("\n\n[*] Interrupted")
        running = False
    
    print("[*] Stopping services...")
    time.sleep(2)
    print("\n[*] Goodbye!\n")


if __name__ == "__main__":
    main()
