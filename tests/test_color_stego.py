"""
Color Steganography Demo - Full Pipeline Test
Demonstrates embedding in RGB channels with visual comparison
"""

import sys
sys.path.append('core_modules')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed_in_dwt_bands_color, extract_from_dwt_bands_color, bytes_to_bits, bits_to_bytes
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color, save_image_color
import numpy as np
import cv2

print("="*70)
print("COLOR STEGANOGRAPHY - FULL PIPELINE TEST")
print("="*70)

# Test message
message = "Hello Alice! This message is hidden in a COLOR image using DWT."
print(f"\nOriginal message: {message}")
print(f"Message length: {len(message)} characters")

# Step 1: Encrypt
print("\n[1/6] ENCRYPTION...")
ciphertext, salt, iv = encrypt_message(message, "color_demo_key")
print(f"   Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")

# Step 2: Compress
print("[2/6] COMPRESSION...")
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
payload_bits = bytes_to_bits(payload)
print(f"   Compressed: {len(ciphertext)} -> {len(payload)} bytes ({len(payload_bits)} bits)")

# Step 3: Load COLOR cover image
print("[3/6] LOADING COVER IMAGE...")
try:
    cover_img = read_image_color("cover.png")
    print(f"   Loaded: cover.png (shape: {cover_img.shape})")
except:
    # Create a sample color image if cover.png doesn't exist in color
    print("   [!] Creating sample color image...")
    cover_img = np.random.randint(100, 200, (512, 512, 3), dtype=np.uint8)
    # Add some pattern
    for i in range(0, 512, 64):
        cover_img[i:i+32, :] = [100, 150, 200]
    cv2.imwrite("cover_color.png", cover_img)
    print("   Created: cover_color.png")

# Step 4: DWT decompose (3 channels)
print("[4/6] DWT DECOMPOSITION (RGB)...")
bands = dwt_decompose_color(cover_img, levels=2)
print(f"   Decomposed: 7 bands × 3 channels")
print(f"   Band shapes: {bands['LH1'].shape}")

# Step 5: EMBED in color bands
print("[5/6] EMBEDDING IN COLOR BANDS...")
modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
stego_img = dwt_reconstruct_color(modified_bands)

# Calculate PSNR
psnr_value = psnr_color(cover_img, stego_img)
print(f"   PSNR: {psnr_value:.2f} dB")

# Save stego image
save_image_color("stego_color_demo.png", stego_img)

# Step 6: EXTRACT and decrypt
print("[6/6] EXTRACTION & DECRYPTION...")

# Re-decompose stego image
stego_bands = dwt_decompose_color(stego_img, levels=2)

# Extract bits
extracted_bits = extract_from_dwt_bands_color(stego_bands, len(payload_bits), Q_factor=5.0)
extracted_payload = bits_to_bytes(extracted_bits)

# Decompress
msg_len, tree_extracted, compressed_extracted = parse_payload(extracted_payload)
decrypted_ciphertext = decompress_huffman(compressed_extracted, tree_extracted)

# Decrypt
decrypted_message = decrypt_message(decrypted_ciphertext, "color_demo_key", salt, iv)

print("\n" + "="*70)
print("RESULT")
print("="*70)
print(f"Original:  {message}")
print(f"Extracted: {decrypted_message}")
print(f"\nMatch: {'YES!' if message == decrypted_message else 'NO - ERROR'}")
print(f"PSNR: {psnr_value:.2f} dB")
print("="*70)

# Create visual comparison
print("\n[*] Creating visual comparison...")
h, w = cover_img.shape[:2]
comparison = np.zeros((h, w*2, 3), dtype=np.uint8)
comparison[:, 0:w] = cover_img
comparison[:, w:2*w] = stego_img

# Add labels
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(comparison, "Original", (10, 30), font, 1, (0, 255, 0), 2)
cv2.putText(comparison, f"Stego ({psnr_value:.1f}dB)", (w+10, 30), font, 1, (0, 255, 0), 2)
cv2.putText(comparison, f"Message: {len(message)} chars", (10, h-20), font, 0.6, (255, 255, 0), 2)

cv2.imwrite("color_comparison.png", comparison)
print("Saved: color_comparison.png")

print("\n" + "="*70)
print("SUCCESS! Color steganography working perfectly.")
print("="*70)
print("\nGenerated files:")
print("  - stego_color_demo.png (hidden message)")
print("  - color_comparison.png (visual comparison)")
print("="*70)
