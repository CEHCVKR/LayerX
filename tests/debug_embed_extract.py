"""
Debug script to test embedding and extraction
"""
import numpy as np
import struct
from scipy.fftpack import dct, idct
from a3_image_processing import *
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a1_encryption import encrypt_message, decrypt_message

def apply_dct(band):
    """Apply 2D DCT to a band"""
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    """Apply inverse 2D DCT to a band"""
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

# Test message
message = "HOLAAAA"
print(f"Original message: {message}")

# Step 1: Encrypt
ciphertext, salt, iv = encrypt_message(message, "temp_password")
print(f"Encrypted: {len(ciphertext)} bytes")

# Step 2: Compress
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
print(f"Compressed payload: {len(payload)} bytes")
print(f"Payload first 16 bytes: {payload[:16].hex()}")

# Parse to verify
msg_len, tree_len = struct.unpack('I', payload[0:4])[0], struct.unpack('I', payload[4:8])[0]
print(f"msg_len: {msg_len}, tree_len: {tree_len}")
print(f"Expected minimum payload size: {8 + tree_len} bytes")

# Step 3: Load test image
img = read_image("test_lena.png")
bands = dwt_decompose(img, levels=2)

# Apply DCT
dct_bands = bands.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands:
        dct_bands[band_name] = apply_dct(bands[band_name])

# Step 4: Embed
payload_bits = bytes_to_bits(payload)
print(f"\nEmbedding {len(payload_bits)} bits ({len(payload)} bytes)")
modified_bands = embed_in_dwt_bands(payload_bits, dct_bands, optimization='fixed')

# Apply IDCT
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in modified_bands:
        modified_bands[band_name] = apply_idct(modified_bands[band_name])

# Reconstruct stego image
stego_img = dwt_reconstruct(modified_bands)

# Calculate PSNR
psnr_value = psnr(img, stego_img)
print(f"PSNR: {psnr_value:.2f} dB")

# Save stego image
import cv2
cv2.imwrite("debug_stego.png", stego_img)

# Step 5: Extract
print("\n" + "="*70)
print("EXTRACTION")
print("="*70)

# Read stego image
stego_img_read = read_image("debug_stego.png")
bands_stego = dwt_decompose(stego_img_read, levels=2)

# Apply DCT
dct_bands_stego = bands_stego.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands_stego:
        dct_bands_stego[band_name] = apply_dct(bands_stego[band_name])

# Extract
print(f"Extracting {len(payload_bits)} bits")
extracted_bits = extract_from_dwt_bands(dct_bands_stego, len(payload_bits), optimization='fixed')
extracted_payload = bits_to_bytes(extracted_bits)

print(f"Extracted {len(extracted_payload)} bytes")
print(f"Extracted first 16 bytes: {extracted_payload[:16].hex()}")

# Compare
print(f"\nOriginal payload:  {payload[:16].hex()}")
print(f"Extracted payload: {extracted_payload[:16].hex()}")
print(f"Match: {payload == extracted_payload[:len(payload)]}")

# Parse extracted payload
try:
    msg_len_ex, tree_len_ex = struct.unpack('I', extracted_payload[0:4])[0], struct.unpack('I', extracted_payload[4:8])[0]
    print(f"\nExtracted msg_len: {msg_len_ex}, tree_len: {tree_len_ex}")
    
    msg_len, tree, compressed = parse_payload(extracted_payload)
    decrypted_ciphertext = decompress_huffman(compressed, tree)
    decrypted_message = decrypt_message(decrypted_ciphertext, "temp_password", salt, iv)
    print(f"\n✅ SUCCESS! Decrypted message: {decrypted_message}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
