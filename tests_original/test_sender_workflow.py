"""
Test sender.py embedding workflow (without networking)
"""

import sys
import os

sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('06. Optimization Module')

from a1_encryption import encrypt_message
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import bytes_to_bits
from a6_optimization import optimize_coefficients_aco
from scipy.fftpack import dct, idct
import numpy as np

def apply_dct(band):
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

print("\n" + "="*70)
print("SENDER WORKFLOW TEST (Simulated)")
print("="*70 + "\n")

# Test message
message = "Hello World!"
print(f"[*] Test message: '{message}'")

# Step 1: Encryption
print("\n[1/5] ENCRYPTION...")
ciphertext, salt, iv = encrypt_message(message, "test_password")
print(f"      [+] Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")

# Step 2: Compression
print("[2/5] COMPRESSION...")
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
print(f"      [+] Compressed: {len(ciphertext)} -> {len(payload)} bytes")

# Step 3: Check for cover image
if not os.path.exists('test_lena.png'):
    print("\n[!] test_lena.png not found, creating test image...")
    import cv2
    test_img = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
    cv2.imwrite('test_lena.png', test_img)
    print("[+] Test image created")

# Step 4: DWT + DCT
print("[3/5] DWT + DCT TRANSFORM...")
img = read_image('test_lena.png')
bands = dwt_decompose(img, levels=2)

# Apply DCT (keep metadata)
dct_bands = bands.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands:
        dct_bands[band_name] = apply_dct(bands[band_name])
print(f"      [+] Transformed: 7 frequency bands ready")

# Step 5: Optimization
print("[4/5] OPTIMIZATION (ACO)...")
payload_bits = bytes_to_bits(payload)
optimized_coeffs = optimize_coefficients_aco(dct_bands, len(payload_bits))
print(f"      [+] Optimized: {len(optimized_coeffs)} coefficients selected")

# Step 6: Embedding
print("[5/5] EMBEDDING INTO IMAGE...")
from a5_embedding_extraction import embed_in_dwt_bands

try:
    modified_bands = embed_in_dwt_bands(payload_bits, dct_bands, optimization='aco')
    
    # Inverse DCT
    for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
        if band_name in modified_bands:
            modified_bands[band_name] = apply_idct(modified_bands[band_name])
    
    # Inverse DWT
    stego_img = dwt_reconstruct(modified_bands)
    
    # Calculate PSNR
    psnr_value = psnr(img, stego_img)
    
    print(f"      [+] Embedding successful!")
    print(f"\n" + "="*70)
    print("SUCCESS!")
    print("="*70)
    print(f"[+] PSNR Quality: {psnr_value:.2f} dB")
    print(f"[+] Payload Size: {len(payload)} bytes")
    print(f"[+] Sender workflow working correctly!")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
