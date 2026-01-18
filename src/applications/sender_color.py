"""
LayerX Sender - COLOR STEGANOGRAPHY VERSION
- Embeds data in RGB channels independently
- Preserves visual color quality
"""

import sys
import os
import json
import socket
import time
from datetime import datetime

# Add module paths
sys.path.append('core_modules')

from a1_encryption import encrypt_message
from a2_key_management import generate_ecc_keypair, serialize_public_key, serialize_private_key
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color, save_image_color
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import embed_in_dwt_bands_color, bytes_to_bits
from a6_optimization import aco_optimize_positions
import numpy as np

IDENTITY_FILE = "my_identity.json"
BROADCAST_PORT = 37020
peers_list = {}


def load_or_create_identity():
    """Load existing identity"""
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, 'r') as f:
            data = json.load(f)
            print(f"\n✓ Welcome back, {data['username']}!")
            print(f"✓ Your address: {data['address']}")
            return data
    else:
        raise FileNotFoundError("Run receiver.py first to create identity!")


def send_encrypted_message_color(identity, recipient_username, message, cover_image_path="cover.png"):
    """Send encrypted message using COLOR steganography"""
    print("\n" + "="*70)
    print("LAYERX COLOR STEGANOGRAPHY - SENDER")
    print("="*70)
    
    try:
        # Get recipient info
        if recipient_username not in peers_list:
            print(f"[!] Peer '{recipient_username}' not found!")
            return
        
        recipient = peers_list[recipient_username]
        
        # Step 1: ENCRYPTION
        print("[1/5] ENCRYPTION (AES-256)...")
        ciphertext, salt, iv = encrypt_message(message, "temp_password")
        print(f"      [+] Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")
        
        # Step 2: COMPRESSION
        print("[2/5] COMPRESSION (Huffman)...")
        compressed, tree = compress_huffman(ciphertext)
        payload = create_payload(ciphertext, tree, compressed)
        payload_bits = bytes_to_bits(payload)
        print(f"      [+] Compressed: {len(ciphertext)} -> {len(payload)} bytes")
        
        # Step 3: READ COLOR IMAGE
        print("[3/5] LOADING COLOR COVER IMAGE...")
        cover_img = read_image_color(cover_image_path)
        print(f"      [+] Loaded: {cover_image_path} (shape: {cover_img.shape})")
        
        # Step 4: DWT DECOMPOSITION (3 channels)
        print("[4/5] DWT DECOMPOSITION (RGB)...")
        bands = dwt_decompose_color(cover_img, levels=2)
        print(f"      [+] Decomposed: 7 frequency bands × 3 channels")
        
        # Step 5: EMBEDDING
        print("[5/5] EMBEDDING INTO COLOR IMAGE...")
        modified_bands = embed_in_dwt_bands_color(payload_bits, bands)
        stego_img = dwt_reconstruct_color(modified_bands)
        
        # Calculate PSNR
        psnr_value = psnr_color(cover_img, stego_img)
        
        # Save stego image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stego_filename = f"stego_color_to_{recipient_username}_{timestamp}.png"
        save_image_color(stego_filename, stego_img)
        
        print(f"\n{'='*70}")
        print("[SUCCESS] MESSAGE EMBEDDED IN COLOR IMAGE!")
        print(f"{'='*70}")
        print(f"[*] PSNR Quality: {psnr_value:.2f} dB")
        print(f"[*] Payload Size: {len(payload)} bytes")
        print(f"[*] Stego Image: {stego_filename}")
        
        # Send to recipient
        print(f"\n[*] Sending to {recipient_username} at {recipient['ip']}...")
        send_file_tcp(recipient['ip'], stego_filename, salt, iv, len(payload_bits))
        print(f"[SUCCESS] Color image sent to {recipient_username}!")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()


def send_file_tcp(target_ip, stego_path, salt, iv, payload_bits_length, port=37021):
    """Send stego image via TCP"""
    import struct
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((target_ip, port))
    
    # Send metadata
    sock.send(struct.pack('!I', len(salt)))
    sock.send(salt)
    
    sock.send(struct.pack('!I', len(iv)))
    sock.send(iv)
    
    sock.send(struct.pack('!I', payload_bits_length))
    
    # Send image
    with open(stego_path, 'rb') as f:
        image_data = f.read()
    
    sock.send(struct.pack('!I', len(image_data)))
    sock.sendall(image_data)
    
    sock.close()


def main():
    """Main sender application"""
    identity = load_or_create_identity()
    
    print("\n" + "="*60)
    print("LAYERX COLOR SENDER - Ready to send")
    print("="*60)
    
    message = input("\nEnter message: ").strip()
    recipient = input("Enter recipient username: ").strip()
    
    # Mock peer (replace with actual discovery)
    peers_list[recipient] = {
        'ip': input("Enter recipient IP: ").strip(),
        'address': 'MOCK',
        'public_key': 'MOCK'
    }
    
    send_encrypted_message_color(identity, recipient, message)


if __name__ == "__main__":
    main()
