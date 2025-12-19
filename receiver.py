"""
LayerX Receiver - Complete Steganographic Pipeline with Peer Discovery
Features:
- Automatic peer discovery (UDP broadcast every 5 seconds)
- Username + automatic ECC key generation
- Full pipeline: Extract → Reverse Optimization → Reverse DWT+DCT → Decryption → Message
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

from a1_encryption import decrypt_message
from a2_key_management import generate_ecc_keypair, serialize_public_key, serialize_private_key
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
from scipy.fftpack import dct, idct
from a4_compression import decompress_huffman, parse_payload
from a5_embedding_extraction import extract_from_dwt_bands, bits_to_bytes
import numpy as np
import cv2

# Helper functions
def apply_dct(band):
    """Apply 2D DCT to a band"""
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    """Apply inverse 2D DCT to a band"""
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

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
    
    announcement = json.dumps({
        'username': identity['username'],
        'address': identity['address'],
        'public_key': identity['public_key']
    }).encode('utf-8')
    
    while running:
        try:
            sock.sendto(announcement, ('<broadcast>', BROADCAST_PORT))
            
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


def receive_file_listener(port=37021):
    """Listen for incoming stego images"""
    global running
    
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', port))
    server_sock.listen(1)
    server_sock.settimeout(1)
    
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
            payload_size = struct.unpack('!I', conn.recv(4))[0]
            
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
            
            # Save received image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"received_stego_{timestamp}.png"
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            print(f"[+] File received: {filename}")
            print(f"[+] Salt: {salt.hex()}")
            print(f"[+] IV: {iv.hex()}")
            print(f"[+] Payload bits: {payload_size} bits")
            print(f"\n[*] Auto-decrypting message...")
            
            # Auto-decrypt
            receive_encrypted_message_auto(filename, salt, iv, payload_size)
            
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"[!] File receive error: {e}")
    
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


def receive_encrypted_message_auto(stego_image_path, salt, iv, payload_bits_length):
    """Auto-decrypt received message (called by file listener)"""
    try:
        # Step 1: READ STEGO IMAGE
        stego_img = read_image(stego_image_path)
        
        # Step 2: DWT DECOMPOSITION
        bands = dwt_decompose(stego_img, levels=2)
        
        # Step 3: EXTRACTION (directly from DWT bands - no DCT needed)
        extracted_bits = extract_from_dwt_bands(bands, payload_bits_length, optimization='fixed')
        extracted_payload = bits_to_bytes(extracted_bits)
        
        # Step 4: DECOMPRESSION
        msg_len, tree, compressed = parse_payload(extracted_payload)
        decrypted_ciphertext = decompress_huffman(compressed, tree)
        
        # Step 5: DECRYPTION
        decrypted_message = decrypt_message(decrypted_ciphertext, "temp_password", salt, iv)
        
        print(f"\n{'='*70}")
        print("[SUCCESS] MESSAGE DECRYPTED!")
        print(f"{'='*70}")
        print(f">>> {decrypted_message}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"[!] Decryption failed: {e}")
        import traceback
        traceback.print_exc()


def receive_encrypted_message(identity, stego_image_path, salt_hex, iv_hex):
    """Complete receiver pipeline"""
    print("\n" + "="*70)
    print("LAYERX RECEIVER - COMPLETE STEGANOGRAPHIC PIPELINE")
    print("="*70)
    
    try:
        # Convert hex to bytes
        salt = bytes.fromhex(salt_hex)
        iv = bytes.fromhex(iv_hex)
        
        # Step 1: READ STEGO IMAGE
        print("[1/5] READING STEGO IMAGE...")
        stego_img = read_image(stego_image_path)
        print(f"      [+] Loaded: {stego_image_path}")
        
        # Step 2: DWT + DCT TRANSFORM
        print("[2/5] DWT + DCT TRANSFORM...")
        bands = dwt_decompose(stego_img, levels=2)
        
        # Apply DCT to extraction bands
        dct_bands = {}
        for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
            if band_name in bands:
                dct_bands[band_name] = apply_dct(bands[band_name])
        print(f"      [+] Transformed: 7 frequency bands")
        
        # Step 3: EXTRACTION
        print("[3/5] EXTRACTING HIDDEN DATA...")
        
        # Extract length header first (32 bits)
        length_bits = ""
        bit_index = 0
        for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
            if band_name not in dct_bands:
                continue
            band = dct_bands[band_name]
            rows, cols = band.shape
            
            for i in range(rows):
                for j in range(cols):
                    if len(length_bits) < 32:
                        coeff = band[i, j]
                        if abs(coeff) > 8:  # Threshold
                            length_bits += str(int(coeff) & 1)
                    else:
                        break
                if len(length_bits) >= 32:
                    break
            if len(length_bits) >= 32:
                break
        
        payload_length = int(length_bits, 2) * 8  # Convert to bits
        print(f"      [+] Payload length: {payload_length // 8} bytes")
        
        # Extract full payload
        extracted_bits = extract_from_dwt_bands(dct_bands, payload_length)
        payload = bits_to_bytes(extracted_bits)
        print(f"      [+] Extracted: {len(payload)} bytes")
        
        # Step 4: DECOMPRESSION
        print("[4/5] DECOMPRESSION (Huffman)...")
        msg_len, tree, compressed = parse_payload(payload)
        ciphertext = decompress_huffman(compressed, tree)
        print(f"      [+] Decompressed: {len(payload)} -> {len(ciphertext)} bytes")
        
        # Step 5: DECRYPTION
        print("[5/5] DECRYPTION (AES-256)...")
        message = decrypt_message(ciphertext, "temp_password", salt, iv)
        print(f"      [+] Decrypted: {len(ciphertext)} bytes -> {len(message)} chars")
        
        print(f"\n{'='*70}")
        print("[SUCCESS] MESSAGE EXTRACTED SUCCESSFULLY!")
        print(f"{'='*70}")
        print(f"\n[*] DECRYPTED MESSAGE:")
        print(f"{'='*70}")
        print(f"{message}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n[!] ERROR during extraction: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main receiver application"""
    global running
    
    # Load or create identity
    identity = load_or_create_identity()
    
    # Start peer discovery threads
    listener_thread = threading.Thread(target=peer_discovery_listener, args=(identity,), daemon=True)
    announcer_thread = threading.Thread(target=peer_discovery_announcer, args=(identity,), daemon=True)
    
    # Start file receiver thread for automatic file transfer
    file_receiver_thread = threading.Thread(target=receive_file_listener, daemon=True)
    
    listener_thread.start()
    announcer_thread.start()
    file_receiver_thread.start()
    
    print("\n" + "="*60)
    print("LAYERX RECEIVER - Ready to receive encrypted messages")
    print("="*60)
    print("Commands:")
    print("  receive - Receive and decrypt message from image")
    print("  peers   - List discovered peers")
    print("  quit    - Exit application")
    print("="*60)
    
    try:
        while True:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'receive':
                stego_path = input("Enter stego image path: ").strip()
                salt_hex = input("Enter salt (hex): ").strip()
                iv_hex = input("Enter IV (hex): ").strip()
                
                if not os.path.exists(stego_path):
                    print(f"[!] Image '{stego_path}' not found!")
                    continue
                
                receive_encrypted_message(identity, stego_path, salt_hex, iv_hex)
            
            elif cmd == 'peers':
                list_peers()
            
            elif cmd == 'quit':
                print("\n[*] Shutting down...")
                break
            
            else:
                print("[!] Unknown command. Use: receive, peers, quit")
    
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    
    finally:
        running = False
        time.sleep(0.5)
        print("✓ Goodbye!")


if __name__ == "__main__":
    main()
