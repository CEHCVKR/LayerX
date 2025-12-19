"""
Test the fixed sender/receiver pipeline
"""
import sys
import struct
from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes
from a6_optimization import optimize_coefficients_aco
import cv2

# Test message
message = "HOLAAAA"
print(f"Original message: {message}")
print("="*70)

# Step 1: Encrypt
ciphertext, salt, iv = encrypt_message(message, "temp_password")
print(f"[1] Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")

# Step 2: Compress
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
print(f"[2] Compressed: {len(ciphertext)} -> {len(payload)} bytes")

# Step 3: Load image & decompose
img = read_image("cover.png")
bands = dwt_decompose(img, levels=2)
print(f"[3] DWT decomposed: 7 bands ready")

# Step 4: Embed (directly in DWT bands - NO DCT!)
payload_bits = bytes_to_bits(payload)
print(f"[4] Embedding {len(payload_bits)} bits...")
modified_bands = embed_in_dwt_bands(payload_bits, bands, optimization='fixed')

# Step 5: Reconstruct
stego_img = dwt_reconstruct(modified_bands)
psnr_value = psnr(img, stego_img)
print(f"[5] Reconstructed - PSNR: {psnr_value:.2f} dB")

# Save
cv2.imwrite("test_stego.png", stego_img.astype('uint8'))

print("\n" + "="*70)
print("EXTRACTION & DECRYPTION")
print("="*70)

# Step 1: Load stego image
stego_loaded = read_image("test_stego.png")
bands_loaded = dwt_decompose(stego_loaded, levels=2)
print(f"[1] Loaded stego image and decomposed")

# Step 2: Extract (directly from DWT bands - NO DCT!)
print(f"[2] Extracting {len(payload_bits)} bits...")
extracted_bits = extract_from_dwt_bands(bands_loaded, len(payload_bits), optimization='fixed')
extracted_payload = bits_to_bytes(extracted_bits)

# Step 3: Decompress
print(f"[3] Decompressing...")
msg_len, tree, compressed = parse_payload(extracted_payload)
decrypted_ciphertext = decompress_huffman(compressed, tree)

# Step 4: Decrypt
print(f"[4] Decrypting...")
decrypted_message = decrypt_message(decrypted_ciphertext, "temp_password", salt, iv)

print("\n" + "="*70)
print(f"✅ SUCCESS! Decrypted message: {decrypted_message}")
print("="*70)
