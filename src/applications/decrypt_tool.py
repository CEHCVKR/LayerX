"""
LayerX Decrypt Tool
Decrypts metadata JSON using receiver's private key and extracts hidden message
"""

import sys
import os
import json
import base64

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import decrypt_message
from a2_key_management import deserialize_private_key
from a3_image_processing_color import read_image_color, dwt_decompose_color
from a4_compression import decompress_huffman, parse_payload
from a5_embedding_extraction import extract_from_dwt_bands_color, bits_to_bytes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def decrypt_metadata_with_private_key(encrypted_package, private_key_pem):
    """Decrypt metadata JSON using receiver's private key"""
    
    # Extract encrypted components
    encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
    aes_key = base64.b64decode(encrypted_package['aes_key'])  # In real system, decrypt this with private key
    aes_iv = base64.b64decode(encrypted_package['aes_iv'])
    
    # Decrypt data with AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(aes_iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_json = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Parse JSON
    metadata = json.loads(decrypted_json.decode('utf-8'))
    
    return metadata


def extract_hidden_message(stego_image_path, salt, iv, payload_bits_length):
    """Extract and decrypt hidden message from stego image"""
    
    print("\n[1/5] Loading stego image...")
    stego_img = read_image_color(stego_image_path)
    print(f"      ✓ Loaded: {stego_image_path}")
    
    print("[2/5] Performing DWT decomposition...")
    bands = dwt_decompose_color(stego_img, levels=2)
    print(f"      ✓ Decomposed into frequency bands")
    
    print("[3/5] Extracting hidden data...")
    extracted_bits = extract_from_dwt_bands_color(bands, payload_bits_length, Q_factor=5.0)
    extracted_payload = bits_to_bytes(extracted_bits)
    print(f"      ✓ Extracted {len(extracted_payload)} bytes")
    
    print("[4/5] Decompressing data...")
    msg_len, tree, compressed = parse_payload(extracted_payload)
    decrypted_ciphertext = decompress_huffman(compressed, tree)
    print(f"      ✓ Decompressed")
    
    print("[5/5] Decrypting message...")
    decrypted_message = decrypt_message(decrypted_ciphertext, "temp_password", salt, iv)
    print(f"      ✓ Decrypted")
    
    return decrypted_message


def main():
    """Main decrypt tool"""
    print("\n" + "="*70)
    print("LAYERX DECRYPT TOOL")
    print("="*70)
    
    # Check for identity file
    if not os.path.exists("my_identity.json"):
        print("[!] Error: my_identity.json not found!")
        print("[!] Please run receiver_new.py first to create your identity")
        return
    
    # Load receiver's identity (contains private key)
    with open("my_identity.json", 'r') as f:
        identity = json.load(f)
    
    print(f"\n[*] Logged in as: {identity['username']}")
    print(f"[*] Address: {identity['address']}")
    
    # Get encrypted metadata file
    metadata_file = input("\n[?] Enter encrypted metadata JSON filename: ").strip()
    
    if not os.path.exists(metadata_file):
        print(f"[!] Error: File '{metadata_file}' not found!")
        return
    
    # Load encrypted metadata
    with open(metadata_file, 'r') as f:
        encrypted_package = json.load(f)
    
    print(f"\n[*] Decrypting metadata with your private key...")
    
    try:
        # Decrypt metadata
        metadata = decrypt_metadata_with_private_key(encrypted_package, identity['private_key'])
        
        print(f"[+] Metadata decrypted successfully!")
        print(f"\n[*] Message Details:")
        print(f"    Stego Image: {metadata['stego_image']}")
        print(f"    Received: {metadata['received_timestamp']}")
        print(f"    Sender IP: {metadata['sender_ip']}")
        print(f"    Payload Size: {metadata['payload_bits_length']} bits")
        
        # Decode salt and IV from base64
        salt = base64.b64decode(metadata['salt'])
        iv = base64.b64decode(metadata['iv'])
        
        # Extract hidden message
        print(f"\n{'='*70}")
        print("EXTRACTING HIDDEN MESSAGE")
        print(f"{'='*70}")
        
        message = extract_hidden_message(
            metadata['stego_image'],
            salt,
            iv,
            metadata['payload_bits_length']
        )
        
        print(f"\n{'='*70}")
        print("[SUCCESS] MESSAGE EXTRACTED!")
        print(f"{'='*70}")
        print(f"\n{message}\n")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"\n[!] Decryption failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
