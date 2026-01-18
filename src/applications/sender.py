"""
LayerX Sender - Complete Steganographic Pipeline with Peer Discovery
Features:
- Automatic peer discovery (UDP broadcast every 5 seconds)
- Username + automatic ECC key generation
- Full pipeline: Message → Encryption → DWT+DCT → Optimization → Embed
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
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('06. Optimization Module')

from a1_encryption import encrypt_message
from a2_key_management import generate_ecc_keypair, serialize_public_key, serialize_private_key, deserialize_public_key
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color
from scipy.fftpack import dct, idct
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import embed_in_dwt_bands_color, bytes_to_bits
from a6_optimization import optimize_coefficients_aco, select_coefficients_chaos
import numpy as np
import cv2

# Helper functions
def apply_dct(band):
    """Apply 2D DCT to a band"""
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    """Apply inverse 2D DCT to a band"""
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

def write_image(path, img):
    """Write image to file"""
    cv2.imwrite(path, img.astype(np.uint8))

# Configuration
IDENTITY_FILE = "my_identity.json"
BROADCAST_PORT = 37020
DISCOVERY_INTERVAL = 5  # seconds
peers_list = {}  # {username: {ip, public_key, last_seen}}
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
        print("FIRST TIME SETUP - LayerX Steganographic Messenger")
        print("="*60)
        username = input("\nEnter your username: ").strip()
        
        print("\n[*] Generating your ECC keypair (SECP256R1)...")
        private_key, public_key = generate_ecc_keypair()
        
        # Serialize keys
        private_pem = serialize_private_key(private_key)
        public_pem = serialize_public_key(public_key)
        
        # Create unique address (first 8 chars of public key hash)
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
    sock.settimeout(1.0)
    
    print(f"[*] Peer discovery active on port {BROADCAST_PORT}")
    
    while running:
        try:
            data, addr = sock.recvfrom(4096)
            peer_info = json.loads(data.decode('utf-8'))
            
            # Ignore self
            if peer_info['address'] == identity['address']:
                continue
            
            with peers_lock:
                username = peer_info['username']
                if username not in peers_list:
                    print(f"\n[+] NEW PEER DISCOVERED: {username} ({peer_info['address']}) at {addr[0]}")
                
                peers_list[username] = {
                    'ip': addr[0],
                    'address': peer_info['address'],
                    'public_key': peer_info['public_key'],
                    'last_seen': time.time()
                }
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                pass  # Suppress errors during shutdown
    
    sock.close()


def peer_discovery_announcer(identity):
    """Broadcast presence every 5 seconds"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # Try to bind to specific interface (helps with Windows)
    try:
        sock.bind(('', 0))  # Bind to any available port
    except:
        pass
    
    announcement = json.dumps({
        'username': identity['username'],
        'address': identity['address'],
        'public_key': identity['public_key']
    }).encode('utf-8')
    
    # Use 255.255.255.255 for cross-subnet discovery (works across different subnets)
    broadcast_addresses = ['255.255.255.255']
    
    # Also try subnet-specific broadcast as backup
    try:
        import socket as sock_module
        hostname = sock_module.gethostname()
        local_ip = sock_module.gethostbyname(hostname)
        # Calculate broadcast for common /24 network
        ip_parts = local_ip.split('.')
        if len(ip_parts) == 4:
            broadcast_addresses.append(f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.255")
    except:
        pass
    
    print(f"[*] Broadcasting to: {', '.join(broadcast_addresses)}")
    
    while running:
        try:
            # Try broadcasting to multiple addresses
            for broadcast_addr in broadcast_addresses:
                try:
                    sock.sendto(announcement, (broadcast_addr, BROADCAST_PORT))
                except:
                    pass  # Continue to next address
            
            # Clean up stale peers (not seen in 20 seconds)
            with peers_lock:
                current_time = time.time()
                stale = [u for u, p in peers_list.items() if current_time - p['last_seen'] > 20]
                for username in stale:
                    print(f"\n[-] Peer {username} went offline")
                    del peers_list[username]
            
            time.sleep(DISCOVERY_INTERVAL)
        except Exception as e:
            if running:
                pass  # Suppress errors during shutdown
    
    sock.close()


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


def send_file_to_peer(peer_ip, stego_path, salt, iv, payload_bits_length, port=37021):
    """Send stego image and metadata to peer via TCP"""
    try:
        # Read stego image
        with open(stego_path, 'rb') as f:
            image_data = f.read()
        
        # Create metadata packet
        import struct
        metadata = struct.pack('!I', len(salt))  # Salt length
        metadata += salt
        metadata += struct.pack('!I', len(iv))   # IV length
        metadata += iv
        metadata += struct.pack('!I', payload_bits_length)  # Payload bits length
        metadata += struct.pack('!I', len(image_data))  # Image size
        
        # Connect to receiver
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((peer_ip, port))
        
        # Send metadata first
        sock.sendall(metadata)
        time.sleep(0.1)  # Give receiver time to process
        
        # Send image data in chunks
        chunk_size = 4096
        for i in range(0, len(image_data), chunk_size):
            sock.sendall(image_data[i:i+chunk_size])
        
        sock.close()
        return True
        
    except Exception as e:
        raise Exception(f"File transfer failed: {str(e)}")


def send_encrypted_message(identity, cover_image_path):
    """Complete sender pipeline"""
    print("\n" + "="*70)
    print("LAYERX SENDER - COMPLETE STEGANOGRAPHIC PIPELINE")
    print("="*70)
    
    # Step 1: Select peer
    peer_usernames = list_peers()
    if not peer_usernames:
        return
    
    choice = int(input("\nSelect peer number: ")) - 1
    if choice < 0 or choice >= len(peer_usernames):
        print("[!] Invalid choice")
        return
    
    receiver_username = peer_usernames[choice]
    receiver_info = peers_list[receiver_username]
    receiver_public_key = deserialize_public_key(receiver_info['public_key'].encode('utf-8'))
    
    # Step 2: Get message
    print(f"\n[*] Sending to: {receiver_username}")
    message = input("Enter your secret message: ")
    
    # Step 3: ENCRYPTION (AES-256)
    print("\n[1/5] ENCRYPTION (AES-256)...")
    ciphertext, salt, iv = encrypt_message(message, "temp_password")
    print(f"      [+] Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")
    
    # Step 4: COMPRESSION (Huffman)
    print("[2/5] COMPRESSION (Huffman)...")
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    print(f"      [+] Compressed: {len(ciphertext)} -> {len(payload)} bytes")
    
    # Step 5: DWT DECOMPOSITION
    print("[3/5] DWT DECOMPOSITION...")
    img = read_image_color(cover_image_path)
    bands = dwt_decompose_color(img, levels=2)
    print(f"      [+] Decomposed: 7 frequency bands ready")
    
    # Step 6: OPTIMIZATION (ACO) - Skip for color (uses deterministic selection)
    print("[4/5] OPTIMIZATION (Color Mode - Deterministic)...")
    # Color embedding uses deterministic position selection internally
    payload_bits = bytes_to_bits(payload)
    print(f"      [+] Prepared: {len(payload_bits)} bits for embedding")
    

    # Step 7: EMBEDDING
    print("[5/5] EMBEDDING INTO IMAGE...")
    
    # Embed directly in DWT bands (no DCT/IDCT needed)
    modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
    
    # Inverse DWT to reconstruct image
    stego_img = dwt_reconstruct_color(modified_bands)
    
    # Calculate PSNR
    psnr_value = psnr_color(img, stego_img)
    
    # Save stego image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stego_path = f"stego_to_{receiver_username}_{timestamp}.png"
    write_image(stego_path, stego_img)
    
    print(f"\n{'='*70}")
    print("[SUCCESS] MESSAGE EMBEDDED SUCCESSFULLY!")
    print(f"{'='*70}")
    print(f"[*] PSNR Quality: {psnr_value:.2f} dB")
    print(f"[*] Payload Size: {len(payload)} bytes")
    print(f"[*] Stego Image: {stego_path}")
    print(f"\n[*] Sending to {receiver_username} at {receiver_info['ip']}...")
    
    # Send file automatically to receiver
    try:
        send_file_to_peer(receiver_info['ip'], stego_path, salt, iv, len(payload_bits))
        print(f"[SUCCESS] File sent to {receiver_username}!")
        print(f"{'='*70}")
    except Exception as e:
        print(f"[!] Failed to send file: {e}")
        print(f"\n[*] MANUAL TRANSFER REQUIRED:")
        print(f"   Salt: {salt.hex()}")
        print(f"   IV:   {iv.hex()}")
        print(f"   Payload Bits: {len(payload_bits)} bits")
        print(f"   File: {stego_path}")
        print(f"{'='*70}")


def main():
    """Main sender application"""
    global running
    
    # Load or create identity
    identity = load_or_create_identity()
    
    # Start peer discovery threads
    listener_thread = threading.Thread(target=peer_discovery_listener, args=(identity,), daemon=True)
    announcer_thread = threading.Thread(target=peer_discovery_announcer, args=(identity,), daemon=True)
    
    listener_thread.start()
    announcer_thread.start()
    
    print("\n" + "="*60)
    print("LAYERX SENDER - Ready to send encrypted messages")
    print("="*60)
    print("Commands:")
    print("  send   - Send encrypted message to peer")
    print("  peers  - List discovered peers")
    print("  quit   - Exit application")
    print("="*60)
    
    try:
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'send':
                if not os.path.exists('IMAGE1.jpg'):
                    print("[!] Cover image 'IMAGE1.jpg' not found!")
                    continue
                send_encrypted_message(identity, 'IMAGE1.jpg')
            
            elif cmd == 'peers':
                list_peers()
            
            elif cmd == 'quit':
                print("\n[*] Shutting down...")
                break
            
            else:
                print("[!] Unknown command. Use: send, peers, quit")
    
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    
    finally:
        running = False
        time.sleep(0.5)
        print("✓ Goodbye!")


if __name__ == "__main__":
    main()
