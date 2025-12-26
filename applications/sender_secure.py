"""
LayerX Sender - Enhanced Security Version
Features:
- ECDH key exchange (Perfect Forward Secrecy)
- Digital signatures for authenticity
- AES-256-GCM encryption
- Self-destruct message support
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
from a2_key_management import (
    generate_ecc_keypair, serialize_public_key, serialize_private_key,
    deserialize_public_key, deserialize_private_key
)
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color
from scipy.fftpack import dct, idct
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import embed_in_dwt_bands_color, bytes_to_bits
from a6_optimization import optimize_coefficients_aco, select_coefficients_chaos
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import numpy as np
import cv2
import base64
import struct

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
        print("FIRST TIME SETUP - LayerX Steganographic Messenger")
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


def create_secure_metadata_package(salt, iv, payload_bits_length, stego_filename, 
                                    sender_identity, receiver_public_key_pem,
                                    self_destruct_config=None):
    """
    Create encrypted metadata with ECDH + Digital Signature
    """
    # Load sender's private key
    sender_private_key = deserialize_private_key(sender_identity['private_key'].encode('utf-8'))
    sender_public_key_pem = sender_identity['public_key'].encode('utf-8')
    
    # 1. Generate ephemeral keypair (Perfect Forward Secrecy)
    ephemeral_private_key, ephemeral_public_key = generate_ecc_keypair()
    
    # 2. Perform ECDH with receiver's public key
    receiver_pub_key = deserialize_public_key(receiver_public_key_pem.encode('utf-8'))
    shared_secret = ephemeral_private_key.exchange(ec.ECDH(), receiver_pub_key)
    
    # 3. Derive encryption key using HKDF
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'layerx-metadata-v2',
        backend=default_backend()
    ).derive(shared_secret)
    
    # 4. Create metadata
    metadata = {
        'stego_image': stego_filename,
        'salt': base64.b64encode(salt).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'payload_bits_length': payload_bits_length,
        'sender_username': sender_identity['username'],
        'sender_address': sender_identity['address'],
        'timestamp': datetime.now().isoformat()
    }
    
    # Add self-destruct configuration if specified
    if self_destruct_config:
        metadata['self_destruct'] = self_destruct_config
    
    metadata_json = json.dumps(metadata).encode('utf-8')
    
    # 5. Encrypt with AES-GCM
    aes_iv = os.urandom(12)  # GCM recommended IV size
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(aes_iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(metadata_json) + encryptor.finalize()
    auth_tag = encryptor.tag
    
    # 6. Create digital signature
    signature_data = ciphertext + aes_iv + auth_tag
    signature = sender_private_key.sign(signature_data, ec.ECDSA(hashes.SHA256()))
    
    # 7. Build encrypted package
    package = {
        'version': '2.0',
        'protocol': 'ECDH-AES256-GCM',
        'encrypted_data': base64.b64encode(ciphertext).decode('utf-8'),
        'aes_iv': base64.b64encode(aes_iv).decode('utf-8'),
        'auth_tag': base64.b64encode(auth_tag).decode('utf-8'),
        'ephemeral_public_key': base64.b64encode(serialize_public_key(ephemeral_public_key)).decode('utf-8'),
        'sender_public_key': base64.b64encode(sender_public_key_pem).decode('utf-8'),
        'sender_username': sender_identity['username'],
        'sender_address': sender_identity['address'],
        'signature': base64.b64encode(signature).decode('utf-8'),
        'timestamp': datetime.now().isoformat()
    }
    
    return package


def send_secure_file(peer_ip, stego_path, metadata_package, port=37021):
    """Send stego image and encrypted metadata"""
    try:
        # Read stego image
        with open(stego_path, 'rb') as f:
            image_data = f.read()
        
        # Serialize metadata package
        metadata_json = json.dumps(metadata_package).encode('utf-8')
        
        # Create packet: [metadata_size][metadata][image_size][image]
        packet = struct.pack('!I', len(metadata_json))
        packet += metadata_json
        packet += struct.pack('!I', len(image_data))
        packet += image_data
        
        # Connect and send
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((peer_ip, port))
        sock.sendall(packet)
        sock.close()
        
        return True
        
    except Exception as e:
        raise Exception(f"Secure transfer failed: {str(e)}")


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


def send_encrypted_message(identity, cover_image_path):
    """Complete sender pipeline with enhanced security"""
    print("\n" + "="*70)
    print("LAYERX SENDER - SECURE STEGANOGRAPHIC PIPELINE")
    print("="*70)
    
    # Select peer
    peer_usernames = list_peers()
    if not peer_usernames:
        return
    
    choice = int(input("\nSelect peer number: ")) - 1
    if choice < 0 or choice >= len(peer_usernames):
        print("[!] Invalid choice")
        return
    
    receiver_username = peer_usernames[choice]
    receiver_info = peers_list[receiver_username]
    
    # Get message
    print(f"\n[*] Sending to: {receiver_username}")
    message = input("Enter your secret message: ")
    
    # Self-destruct options
    print("\n[?] Self-destruct options:")
    print("  1. No self-destruct")
    print("  2. Delete after reading (1 view)")
    print("  3. Delete after time (minutes)")
    print("  4. Delete after N views")
    
    sd_choice = input("Choose option (1-4): ").strip()
    self_destruct_config = None
    
    if sd_choice == '2':
        self_destruct_config = {'type': 'view_count', 'max_views': 1}
    elif sd_choice == '3':
        minutes = int(input("Delete after how many minutes? "))
        self_destruct_config = {'type': 'timer', 'minutes': minutes}
    elif sd_choice == '4':
        max_views = int(input("Delete after how many views? "))
        self_destruct_config = {'type': 'view_count', 'max_views': max_views}
    
    # Encryption pipeline
    print("\n[1/5] ENCRYPTION (AES-256)...")
    ciphertext, salt, iv = encrypt_message(message, "temp_password")
    print(f"      [+] Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")
    
    print("[2/5] COMPRESSION (Huffman)...")
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    print(f"      [+] Compressed: {len(ciphertext)} -> {len(payload)} bytes")
    
    print("[3/5] DWT DECOMPOSITION...")
    img = read_image_color(cover_image_path)
    bands = dwt_decompose_color(img, levels=2)
    print(f"      [+] Decomposed: 7 frequency bands ready")
    
    print("[4/5] OPTIMIZATION...")
    payload_bits = bytes_to_bits(payload)
    print(f"      [+] Prepared: {len(payload_bits)} bits for embedding")
    
    print("[5/5] EMBEDDING INTO IMAGE...")
    modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
    stego_img = dwt_reconstruct_color(modified_bands)
    psnr_value = psnr_color(img, stego_img)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stego_path = f"stego_to_{receiver_username}_{timestamp}.png"
    write_image(stego_path, stego_img)
    
    print(f"\n[6/6] CREATING SECURE METADATA PACKAGE...")
    metadata_package = create_secure_metadata_package(
        salt, iv, len(payload_bits), stego_path,
        identity, receiver_info['public_key'],
        self_destruct_config
    )
    
    print(f"\n{'='*70}")
    print("[SUCCESS] MESSAGE EMBEDDED WITH ENHANCED SECURITY!")
    print(f"{'='*70}")
    print(f"[*] PSNR Quality: {psnr_value:.2f} dB")
    print(f"[*] Encryption: ECDH + AES-256-GCM")
    print(f"[*] Digital Signature: ECDSA-SHA256")
    print(f"[*] Perfect Forward Secrecy: ✓")
    if self_destruct_config:
        print(f"[*] Self-Destruct: {self_destruct_config['type']}")
    print(f"[*] Stego Image: {stego_path}")
    
    # Send securely
    try:
        print(f"\n[*] Sending to {receiver_username} at {receiver_info['ip']}...")
        send_secure_file(receiver_info['ip'], stego_path, metadata_package)
        print(f"[SUCCESS] Secure transfer complete!")
        print(f"{'='*70}")
    except Exception as e:
        print(f"[!] Transfer failed: {e}")


def main():
    """Main sender application"""
    global running
    
    identity = load_or_create_identity()
    
    listener_thread = threading.Thread(target=peer_discovery_listener, args=(identity,), daemon=True)
    announcer_thread = threading.Thread(target=peer_discovery_announcer, args=(identity,), daemon=True)
    
    listener_thread.start()
    announcer_thread.start()
    
    print("\n" + "="*60)
    print("LAYERX SECURE SENDER - Ready")
    print("="*60)
    print("Commands: send, peers, quit")
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
                print("[!] Unknown command")
    
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted")
    
    finally:
        running = False
        time.sleep(0.5)
        print("✓ Goodbye!")


if __name__ == "__main__":
    main()
