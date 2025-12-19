"""
Color Steganography Test with Lena Image
Tests full pipeline with a classic test image
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
print("LENA COLOR STEGANOGRAPHY TEST")
print("="*70)

# Test message
message = "This secret message is hidden in the famous Lena image using LayerX DWT color steganography!"
print(f"\nTest message: {message}")
print(f"Length: {len(message)} characters")

# Step 1: Encrypt
print("\n[1/6] ENCRYPTION...")
ciphertext, salt, iv = encrypt_message(message, "lena_test_key")
print(f"   [+] Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")

# Step 2: Compress
print("[2/6] COMPRESSION...")
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
payload_bits = bytes_to_bits(payload)
print(f"   [+] Compressed: {len(ciphertext)} -> {len(payload)} bytes ({len(payload_bits)} bits)")

# Step 3: Load Lena image
print("[3/6] LOADING LENA IMAGE...")
try:
    lena_img = read_image_color("test_lena.png")
    print(f"   [+] Loaded: test_lena.png")
    print(f"   [+] Shape: {lena_img.shape}")
    print(f"   [+] Type: Color (BGR)")
except Exception as e:
    print(f"   [!] Error loading test_lena.png: {e}")
    print("   Creating sample color image instead...")
    lena_img = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
    cv2.imwrite("test_lena_color.png", lena_img)
    print(f"   [+] Created: test_lena_color.png")

# Step 4: DWT decompose
print("[4/6] DWT DECOMPOSITION (RGB)...")
bands = dwt_decompose_color(lena_img, levels=2)
print(f"   [+] Decomposed: 7 bands x 3 channels (B, G, R)")
print(f"   [+] Band 'LH1' shape: {bands['LH1'].shape}")

# Check capacity
total_positions = 0
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands:
        rows, cols, channels = bands[band_name].shape
        # Count positions (skip first 8 rows/cols)
        usable = max(0, (rows - 8) * cols + 8 * max(0, cols - 8)) * channels
        total_positions += usable

print(f"   [+] Available capacity: ~{total_positions} bits ({total_positions // 8} bytes)")
print(f"   [+] Required: {len(payload_bits)} bits ({len(payload)} bytes)")

if total_positions < len(payload_bits):
    print(f"   [!] INSUFFICIENT CAPACITY!")
    sys.exit(1)

# Step 5: EMBED
print("[5/6] EMBEDDING INTO COLOR IMAGE...")
modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
stego_img = dwt_reconstruct_color(modified_bands)

# Ensure same dimensions (crop if needed)
if stego_img.shape != lena_img.shape:
    print(f"   [*] Adjusting dimensions: {stego_img.shape} -> {lena_img.shape}")
    stego_img = stego_img[:lena_img.shape[0], :lena_img.shape[1], :]

# Calculate PSNR
psnr_value = psnr_color(lena_img, stego_img)
print(f"   [+] PSNR Quality: {psnr_value:.2f} dB")

if psnr_value < 30:
    print(f"   [!] Warning: PSNR is low (< 30 dB)")
elif psnr_value < 40:
    print(f"   [+] Good quality (30-40 dB)")
else:
    print(f"   [+] Excellent quality (> 40 dB)")

# Save stego image
save_image_color("stego_lena_color.png", stego_img)

# Step 6: EXTRACT and decrypt
print("[6/6] EXTRACTION & DECRYPTION...")

# Re-decompose stego image
stego_bands = dwt_decompose_color(stego_img, levels=2)

# Extract bits
extracted_bits = extract_from_dwt_bands_color(stego_bands, len(payload_bits), Q_factor=5.0)
extracted_payload = bits_to_bytes(extracted_bits)

# Decompress
try:
    msg_len, tree_extracted, compressed_extracted = parse_payload(extracted_payload)
    decrypted_ciphertext = decompress_huffman(compressed_extracted, tree_extracted)
    
    # Decrypt
    decrypted_message = decrypt_message(decrypted_ciphertext, "lena_test_key", salt, iv)
    
    print(f"   [+] Successfully extracted and decrypted!")
    
except Exception as e:
    print(f"   [!] Extraction failed: {e}")
    decrypted_message = None

# Results
print("\n" + "="*70)
print("RESULTS")
print("="*70)
print(f"Original message:  {message}")
print(f"Extracted message: {decrypted_message}")
print(f"\nMatch: {'YES!' if message == decrypted_message else 'NO - ERROR'}")
print(f"PSNR: {psnr_value:.2f} dB")
print(f"Payload: {len(payload)} bytes")
print("="*70)

# Create visual comparison
print("\n[*] Creating visual comparison...")
h, w = lena_img.shape[:2]
comparison = np.zeros((h, w*2, 3), dtype=np.uint8)
comparison[:, 0:w] = lena_img
comparison[:, w:2*w] = stego_img

# Add labels
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(comparison, "Original Lena", (10, 30), font, 1, (0, 255, 0), 2)
cv2.putText(comparison, f"Stego Lena ({psnr_value:.1f}dB)", (w+10, 30), font, 1, (0, 255, 0), 2)
cv2.putText(comparison, f"{len(message)} chars hidden", (10, h-20), font, 0.7, (255, 255, 0), 2)

cv2.imwrite("lena_comparison.png", comparison)
print("[+] Saved: lena_comparison.png")

# Create difference map
print("\n[*] Creating difference visualization...")
diff = cv2.absdiff(lena_img, stego_img)
diff_enhanced = cv2.convertScaleAbs(diff, alpha=10)  # Amplify differences

cv2.imwrite("lena_difference.png", diff_enhanced)
print("[+] Saved: lena_difference.png (differences amplified 10x)")

print("\n" + "="*70)
print("SUCCESS! All files generated:")
print("  - stego_lena_color.png (hidden message)")
print("  - lena_comparison.png (side-by-side)")
print("  - lena_difference.png (difference map)")
print("="*70)
