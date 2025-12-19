"""
Create visual demonstration images:
1. Original color image
2. DWT-only embedding (current approach)
3. DWT+DCT hybrid embedding (with block DCT)
"""
import numpy as np
import cv2
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a1_encryption import encrypt_message, decrypt_message
from scipy.fftpack import dct, idct

def block_dct(band, block_size=8):
    """Apply block-wise DCT (like JPEG)"""
    h, w = band.shape
    dct_band = np.zeros_like(band)
    
    for i in range(0, h - h % block_size, block_size):
        for j in range(0, w - w % block_size, block_size):
            block = band[i:i+block_size, j:j+block_size]
            dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
            dct_band[i:i+block_size, j:j+block_size] = dct_block
    
    return dct_band

def block_idct(dct_band, block_size=8):
    """Apply block-wise IDCT"""
    h, w = dct_band.shape
    spatial_band = np.zeros_like(dct_band)
    
    for i in range(0, h - h % block_size, block_size):
        for j in range(0, w - w % block_size, block_size):
            dct_block = dct_band[i:i+block_size, j:j+block_size]
            block = idct(idct(dct_block, axis=1, norm='ortho'), axis=0, norm='ortho')
            spatial_band[i:i+block_size, j:j+block_size] = block
    
    return spatial_band

def embed_with_block_dct(payload_bits, bands, Q=5.0):
    """Embed using DWT + Block DCT approach"""
    embed_bands_list = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
    
    # Apply block DCT to bands
    dct_bands = {}
    for band_name in embed_bands_list:
        if band_name in bands:
            dct_bands[band_name] = block_dct(bands[band_name])
    
    # Collect embedding positions (skip DC coefficients)
    positions = []
    for band_name in embed_bands_list:
        if band_name not in dct_bands:
            continue
        band = dct_bands[band_name]
        h, w = band.shape
        
        # For each 8x8 block, use AC coefficients only
        for block_i in range(0, h - h % 8, 8):
            for block_j in range(0, w - w % 8, 8):
                # Start from (1,1) to skip DC at (0,0)
                for i in range(block_i+1, min(block_i+8, h)):
                    for j in range(block_j+1, min(block_j+8, w)):
                        positions.append((band_name, i, j))
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
    
    print(f"Block DCT: Using {len(positions)} positions for {len(payload_bits)} bits")
    
    # Embed using quantization
    modified_dct = {k: v.copy() if isinstance(v, np.ndarray) else v for k, v in dct_bands.items()}
    
    for idx, bit in enumerate(payload_bits):
        band_name, i, j = positions[idx]
        coeff = modified_dct[band_name][i, j]
        quantized = Q * round(coeff / Q)
        
        if bit == '1':
            q_level = round(quantized / Q)
            if q_level % 2 == 0:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        else:
            q_level = round(quantized / Q)
            if q_level % 2 == 1:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        
        modified_dct[band_name][i, j] = quantized
    
    # Apply inverse block DCT
    modified_bands = {k: v.copy() if isinstance(v, np.ndarray) else v for k, v in bands.items()}
    for band_name in embed_bands_list:
        if band_name in modified_dct:
            modified_bands[band_name] = block_idct(modified_dct[band_name])
    
    return modified_bands, positions

# Test message
message = "Secret: DWT vs DWT+DCT comparison"
print(f"Test message: {message}")
print("="*70)

# Encrypt and compress
ciphertext, salt, iv = encrypt_message(message, "demo_password")
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
payload_bits = bytes_to_bits(payload)

print(f"Payload: {len(payload)} bytes ({len(payload_bits)} bits)")

# Load cover image (grayscale version)
cover_gray = read_image("cover.png")
print(f"Cover image: {cover_gray.shape}")

# Method 1: Pure DWT (current approach)
print("\n" + "="*70)
print("METHOD 1: PURE DWT")
print("="*70)

bands1 = dwt_decompose(cover_gray, levels=2)
modified_bands1 = embed_in_dwt_bands(payload_bits, bands1, optimization='fixed')
stego1 = dwt_reconstruct(modified_bands1)
psnr1 = psnr(cover_gray, stego1)

cv2.imwrite("demo_dwt_only.png", stego1.astype('uint8'))
print(f"PSNR: {psnr1:.2f} dB")
print(f"Saved: demo_dwt_only.png")

# Method 2: DWT + Block DCT
print("\n" + "="*70)
print("METHOD 2: DWT + BLOCK DCT (8x8)")
print("="*70)

bands2 = dwt_decompose(cover_gray, levels=2)
modified_bands2, positions2 = embed_with_block_dct(payload_bits, bands2, Q=5.0)
stego2 = dwt_reconstruct(modified_bands2)
psnr2 = psnr(cover_gray, stego2)

cv2.imwrite("demo_dwt_dct.png", stego2.astype('uint8'))
print(f"PSNR: {psnr2:.2f} dB")
print(f"Saved: demo_dwt_dct.png")

# Create color visualization
print("\n" + "="*70)
print("CREATING COLOR COMPARISON IMAGE")
print("="*70)

# Load original as color
cover_color = cv2.imread("cover.png")
if cover_color is None:
    print("[!] Could not load cover.png")
else:
    h, w = cover_color.shape[:2]
    
    # Create comparison image (3 columns)
    comparison = np.zeros((h, w*3, 3), dtype=np.uint8)
    
    # Column 1: Original
    comparison[:, 0:w] = cover_color
    
    # Column 2: DWT only (grayscale to BGR)
    stego1_bgr = cv2.cvtColor(stego1.astype('uint8'), cv2.COLOR_GRAY2BGR)
    comparison[:, w:2*w] = stego1_bgr
    
    # Column 3: DWT+DCT (grayscale to BGR)  
    stego2_bgr = cv2.cvtColor(stego2.astype('uint8'), cv2.COLOR_GRAY2BGR)
    comparison[:, 2*w:3*w] = stego2_bgr
    
    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(comparison, "Original", (10, 30), font, 1, (0, 255, 0), 2)
    cv2.putText(comparison, f"DWT-only ({psnr1:.1f}dB)", (w+10, 30), font, 1, (0, 255, 0), 2)
    cv2.putText(comparison, f"DWT+DCT ({psnr2:.1f}dB)", (2*w+10, 30), font, 1, (0, 255, 0), 2)
    
    cv2.imwrite("comparison_dwt_vs_dct.png", comparison)
    print(f"Saved: comparison_dwt_vs_dct.png")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Pure DWT:     PSNR = {psnr1:.2f} dB")
print(f"DWT+Block DCT: PSNR = {psnr2:.2f} dB")
print(f"\nFiles created:")
print(f"  - demo_dwt_only.png")
print(f"  - demo_dwt_dct.png")
print(f"  - comparison_dwt_vs_dct.png")
print("="*70)
