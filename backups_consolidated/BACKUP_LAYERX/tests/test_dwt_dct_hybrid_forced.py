"""
Force DWT+DCT Hybrid Test with Internet Image
This test FORCES the use of DWT+DCT hybrid embedding (not just pure DWT)
to satisfy the abstract requirement: "2-level DWT followed by DCT"
"""
import urllib.request
import cv2
import numpy as np
import sys
sys.path.append('core_modules')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import bytes_to_bits, bits_to_bytes
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color, save_image_color
from scipy.fftpack import dct, idct

print("="*70)
print("FORCING DWT+DCT HYBRID TEST (As per Abstract)")
print("="*70)
print("\nAbstract Requirement:")
print("'2-level DWT decomposition followed by DCT on frequency bands'")
print("="*70)

# Download a test image
print("\n[1] DOWNLOADING TEST IMAGE FROM INTERNET...")
url = 'https://picsum.photos/1024/768'
filename = "dwt_dct_test_image.jpg"
try:
    urllib.request.urlretrieve(url, filename)
    print(f"    [+] Downloaded: {filename}")
except Exception as e:
    print(f"    [!] Download failed: {e}")
    print("    [*] Using existing cover.png instead...")
    filename = "cover.png"

# Load image
print("\n[2] LOADING IMAGE...")
img = read_image_color(filename)
print(f"    [+] Image shape: {img.shape}")

# Prepare message
message = "This message is embedded using DWT+DCT hybrid as specified in the abstract!"
print(f"\n[3] MESSAGE: '{message}'")
print(f"    Length: {len(message)} characters")

# Encrypt & compress
ciphertext, salt, iv = encrypt_message(message, "dwt_dct_key")
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
payload_bits = bytes_to_bits(payload)
print(f"    [+] Payload: {len(payload)} bytes ({len(payload_bits)} bits)")

# Step 1: DWT decomposition
print("\n[4] DWT DECOMPOSITION (2-level Haar)...")
bands = dwt_decompose_color(img, levels=2)
print(f"    [+] 7 bands extracted: LH1, HL1, LH2, HL2, HH1, HH2, LL2")

# Step 2: FORCE DCT APPLICATION (Block-based 8x8)
print("\n[5] APPLYING DCT TO DWT BANDS (Hybrid DWT+DCT)...")

def apply_block_dct(band, block_size=8):
    """Apply block-wise DCT (JPEG-style)"""
    h, w, c = band.shape
    dct_band = np.zeros_like(band, dtype=np.float32)
    
    for ch in range(c):  # For each color channel
        for i in range(0, h - h % block_size, block_size):
            for j in range(0, w - w % block_size, block_size):
                block = band[i:i+block_size, j:j+block_size, ch]
                dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
                dct_band[i:i+block_size, j:j+block_size, ch] = dct_block
    
    return dct_band

def apply_block_idct(dct_band, block_size=8):
    """Apply inverse block-wise DCT"""
    h, w, c = dct_band.shape
    spatial_band = np.zeros_like(dct_band, dtype=np.float32)
    
    for ch in range(c):
        for i in range(0, h - h % block_size, block_size):
            for j in range(0, w - w % block_size, block_size):
                dct_block = dct_band[i:i+block_size, j:j+block_size, ch]
                block = idct(idct(dct_block, axis=1, norm='ortho'), axis=0, norm='ortho')
                spatial_band[i:i+block_size, j:j+block_size, ch] = block
    
    return spatial_band

# Apply DCT to DWT bands
dct_bands = {}
embed_band_names = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
for band_name in embed_band_names:
    if band_name in bands:
        dct_bands[band_name] = apply_block_dct(bands[band_name])
        print(f"    [+] DCT applied to {band_name}: {dct_bands[band_name].shape}")

# Step 3: EMBED IN DCT COEFFICIENTS
print("\n[6] EMBEDDING IN DCT COEFFICIENTS...")

Q = 10.0  # Higher Q for block DCT
positions = []

# Collect embedding positions (skip DC coefficients)
for band_name in embed_band_names:
    if band_name not in dct_bands:
        continue
    band = dct_bands[band_name]
    h, w, c = band.shape
    
    # For each 8x8 block, skip DC (0,0) position
    for ch in range(c):
        for block_i in range(0, h - h % 8, 8):
            for block_j in range(0, w - w % 8, 8):
                # AC coefficients only (skip DC at relative position 0,0)
                for i in range(block_i, min(block_i+8, h)):
                    for j in range(block_j, min(block_j+8, w)):
                        if (i % 8 != 0 or j % 8 != 0):  # Skip DC
                            positions.append((band_name, i, j, ch))
                            if len(positions) >= len(payload_bits):
                                break
                    if len(positions) >= len(payload_bits):
                        break
                if len(positions) >= len(payload_bits):
                    break
        if len(positions) >= len(payload_bits):
            break
    if len(positions) >= len(payload_bits):
        break

print(f"    [+] Using {len(positions)} DCT AC coefficients")

# Embed using quantization
modified_dct = {k: v.copy() for k, v in dct_bands.items()}

for idx, bit in enumerate(payload_bits):
    band_name, i, j, ch = positions[idx]
    coeff = modified_dct[band_name][i, j, ch]
    
    # Quantization
    quantized = Q * round(coeff / Q)
    
    if bit == '1':
        q_level = round(quantized / Q)
        if q_level % 2 == 0:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    else:
        q_level = round(quantized / Q)
        if q_level % 2 == 1:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    
    modified_dct[band_name][i, j, ch] = quantized

print(f"    [+] Embedded {len(payload_bits)} bits using quantization (Q={Q})")

# Step 4: INVERSE DCT
print("\n[7] APPLYING INVERSE DCT...")
modified_bands = {k: v.copy() if k not in embed_band_names else None for k, v in bands.items()}
for band_name in embed_band_names:
    if band_name in modified_dct:
        modified_bands[band_name] = apply_block_idct(modified_dct[band_name])
        print(f"    [+] IDCT applied to {band_name}")

# Step 5: INVERSE DWT
print("\n[8] INVERSE DWT RECONSTRUCTION...")
stego_img = dwt_reconstruct_color(modified_bands)

# Adjust dimensions
if stego_img.shape != img.shape:
    stego_img = stego_img[:img.shape[0], :img.shape[1], :]

# Calculate PSNR
psnr_val = psnr_color(img, stego_img)
print(f"    [+] PSNR: {psnr_val:.2f} dB")

# Save
save_image_color("stego_dwt_dct_hybrid.png", stego_img)

# EXTRACTION
print("\n[9] EXTRACTION (DWT -> DCT -> Extract -> IDCT -> IDWT)...")

# DWT
stego_bands = dwt_decompose_color(stego_img, levels=2)

# DCT
stego_dct_bands = {}
for band_name in embed_band_names:
    if band_name in stego_bands:
        stego_dct_bands[band_name] = apply_block_dct(stego_bands[band_name])

# Extract
extracted_bits = ""
for idx in range(len(payload_bits)):
    band_name, i, j, ch = positions[idx]
    coeff = stego_dct_bands[band_name][i, j, ch]
    
    quantized = Q * round(coeff / Q)
    q_level = round(quantized / Q)
    
    bit = '1' if (q_level % 2 == 1) else '0'
    extracted_bits += bit

extracted_payload = bits_to_bytes(extracted_bits)

# Decompress & decrypt
try:
    msg_len, tree_extracted, compressed_extracted = parse_payload(extracted_payload)
    decrypted_ciphertext = decompress_huffman(compressed_extracted, tree_extracted)
    decrypted_message = decrypt_message(decrypted_ciphertext, "dwt_dct_key", salt, iv)
    
    print(f"    [+] Extraction successful!")
    success = (message == decrypted_message)
except Exception as e:
    print(f"    [!] Extraction failed: {e}")
    decrypted_message = None
    success = False

# Results
print("\n" + "="*70)
print("RESULTS - DWT+DCT HYBRID TEST")
print("="*70)
print(f"Original:  {message}")
print(f"Extracted: {decrypted_message}")
print(f"\nMatch: {'YES - SUCCESS!' if success else 'NO - FAILED'}")
print(f"PSNR: {psnr_val:.2f} dB")
print(f"Method: 2-level DWT + Block DCT (8x8) [As per Abstract]")
print("="*70)

# Create comparison
comparison = np.zeros((img.shape[0], img.shape[1]*2, 3), dtype=np.uint8)
comparison[:, 0:img.shape[1]] = img
comparison[:, img.shape[1]:] = stego_img

cv2.putText(comparison, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.putText(comparison, f"DWT+DCT Hybrid ({psnr_val:.1f}dB)", (img.shape[1]+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.putText(comparison, "Abstract: 2-level DWT + DCT", (10, img.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

cv2.imwrite("comparison_dwt_dct_hybrid.png", comparison)
print("\n[+] Saved: comparison_dwt_dct_hybrid.png")
print("[+] Saved: stego_dwt_dct_hybrid.png")

if success:
    print("\n" + "="*70)
    print("SUCCESS! DWT+DCT HYBRID WORKING AS PER ABSTRACT!")
    print("="*70)
