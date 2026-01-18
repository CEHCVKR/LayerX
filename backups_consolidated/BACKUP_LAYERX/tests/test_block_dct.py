"""
Proper DWT+DCT Hybrid Approach using Block DCT (8x8 blocks like JPEG)
This is the correct way to do DWT+DCT steganography
"""
import numpy as np
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from scipy.fftpack import dct, idct
import cv2

def block_dct(band, block_size=8):
    """Apply DCT to 8x8 blocks"""
    h, w = band.shape
    dct_band = np.zeros_like(band)
    
    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):
            block = band[i:i+block_size, j:j+block_size]
            dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
            dct_band[i:i+block_size, j:j+block_size] = dct_block
    
    return dct_band

def block_idct(dct_band, block_size=8):
    """Apply IDCT to 8x8 blocks"""
    h, w = dct_band.shape
    spatial_band = np.zeros_like(dct_band)
    
    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):
            dct_block = dct_band[i:i+block_size, j:j+block_size]
            block = idct(idct(dct_block, axis=1, norm='ortho'), axis=0, norm='ortho')
            spatial_band[i:i+block_size, j:j+block_size] = block
    
    return spatial_band

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bit_string):
    while len(bit_string) % 8 != 0:
        bit_string += '0'
    result = bytearray()
    for i in range(0, len(bit_string), 8):
        result.append(int(bit_string[i:i+8], 2))
    return bytes(result)

# Test payload
test_payload = b'\x10\x00\x00\x00'
payload_bits = bytes_to_bits(test_payload)
print(f"Test payload: {test_payload.hex()}")
print(f"Payload bits: {payload_bits}")

# Load image
img = read_image("cover.png")
bands = dwt_decompose(img, levels=2)

print("\nTesting Block DCT (8x8) on DWT bands:")
print("="*70)

# Apply block DCT to LH1
dct_lh1 = block_dct(bands['LH1'])

print(f"Original band shape: {bands['LH1'].shape}")
print(f"DCT band shape: {dct_lh1.shape}")

# Embed bits using quantization
Q = 5.0
band_name = 'LH1'
embed_positions = []

# Collect positions (skip DC coefficients at block corners)
for block_i in range(0, dct_lh1.shape[0] - 8 + 1, 8):
    for block_j in range(0, dct_lh1.shape[1] - 8 + 1, 8):
        # Use AC coefficients (not DC at [0,0] of each block)
        for i in range(block_i+1, min(block_i+8, dct_lh1.shape[0])):
            for j in range(block_j+1, min(block_j+8, dct_lh1.shape[1])):
                embed_positions.append((i, j))
                if len(embed_positions) >= len(payload_bits):
                    break
            if len(embed_positions) >= len(payload_bits):
                break
        if len(embed_positions) >= len(payload_bits):
            break
    if len(embed_positions) >= len(payload_bits):
        break

print(f"Collected {len(embed_positions)} embedding positions")

# Embed
modified_dct = dct_lh1.copy()
for idx, bit in enumerate(payload_bits):
    i, j = embed_positions[idx]
    coeff = modified_dct[i, j]
    quantized = Q * round(coeff / Q)
    
    if bit == '1':
        q_level = round(quantized / Q)
        if q_level % 2 == 0:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    else:
        q_level = round(quantized / Q)
        if q_level % 2 == 1:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    
    modified_dct[i, j] = quantized
    
    if idx < 4:
        print(f"  Bit {idx} ('{bit}'): [{i},{j}] = {coeff:.2f} -> {quantized:.2f}")

# Apply inverse block DCT
modified_spatial = block_idct(modified_dct)

# Create modified bands
modified_bands = {k: v.copy() if isinstance(v, np.ndarray) else v for k, v in bands.items()}
modified_bands[band_name] = modified_spatial

# Reconstruct
stego_img = dwt_reconstruct(modified_bands)
psnr_value = psnr(img, stego_img)

print(f"\nImage changed: {np.max(np.abs(img - stego_img)):.2f} pixels")
print(f"PSNR: {psnr_value:.2f} dB")

# Save and reload
cv2.imwrite("test_block_dct.png", stego_img.astype('uint8'))
stego_loaded = read_image("test_block_dct.png")

# Extract
bands_loaded = dwt_decompose(stego_loaded, levels=2)
dct_loaded = block_dct(bands_loaded[band_name])

print("\nExtraction:")
extracted_bits = []
for idx in range(len(payload_bits)):
    i, j = embed_positions[idx]
    coeff = dct_loaded[i, j]
    q_level = round(coeff / Q)
    bit = '1' if q_level % 2 == 1 else '0'
    extracted_bits.append(bit)
    
    if idx < 4:
        print(f"  Bit {idx}: [{i},{j}] = {coeff:.2f} -> q_level={int(q_level)} -> '{bit}'")

extracted_str = ''.join(extracted_bits)
extracted_bytes = bits_to_bytes(extracted_str)

print(f"\nOriginal payload:  {test_payload.hex()}")
print(f"Extracted payload: {extracted_bytes[:len(test_payload)].hex()}")
print(f"Match: {test_payload == extracted_bytes[:len(test_payload)]} {'✅ SUCCESS!' if test_payload == extracted_bytes[:len(test_payload)] else '❌ FAILED'}")
