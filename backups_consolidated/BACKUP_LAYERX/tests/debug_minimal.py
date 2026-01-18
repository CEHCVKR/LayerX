"""
Minimal test - embed and extract first few bytes only
"""
import numpy as np
import struct
from scipy.fftpack import dct, idct
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
import cv2

def apply_dct(band):
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bit_string):
    while len(bit_string) % 8 != 0:
        bit_string += '0'
    result = bytearray()
    for i in range(0, len(bit_string), 8):
        byte_bits = bit_string[i:i+8]
        result.append(int(byte_bits, 2))
    return bytes(result)

# Test with just 4 bytes
test_payload = b'\x10\x00\x00\x00'
print(f"Test payload: {test_payload.hex()}")
print(f"Test payload bits: {bytes_to_bits(test_payload)}")

# Load image
img = read_image("test_lena.png")
bands = dwt_decompose(img, levels=2)

# Apply DCT
dct_bands = bands.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands:
        dct_bands[band_name] = apply_dct(bands[band_name])

# Manual embedding (same logic as embed_in_dwt_bands)
Q = 5.0
payload_bits = bytes_to_bits(test_payload)
embed_bands = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']

# Build coefficient list
all_coefficients = []
for band_name in embed_bands:
    if band_name in dct_bands:
        band = dct_bands[band_name]
        for i in range(8, band.shape[0]):
            for j in range(8, band.shape[1]):
                all_coefficients.append((band_name, i, j))
                if len(all_coefficients) >= len(payload_bits):
                    break
            if len(all_coefficients) >= len(payload_bits):
                break
    if len(all_coefficients) >= len(payload_bits):
        break

print(f"\nEmbedding {len(payload_bits)} bits into {len(all_coefficients)} coefficients")
print("\nFirst 8 bits embedding:")

# Embed
modified_bands = {}
for band_name, band_data in dct_bands.items():
    if isinstance(band_data, np.ndarray):
        modified_bands[band_name] = band_data.copy()
    else:
        modified_bands[band_name] = band_data

for i, bit in enumerate(payload_bits):
    band_name, row, col = all_coefficients[i]
    original_coeff = modified_bands[band_name][row, col]
    
    quantized = Q * round(original_coeff / Q)
    
    if bit == '1':
        q_level = round(quantized / Q)
        if q_level % 2 == 0:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    else:
        q_level = round(quantized / Q)
        if q_level % 2 == 1:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    
    modified_bands[band_name][row, col] = quantized
    
    if i < 8:
        print(f"  Bit {i} ('{bit}'): {band_name}[{row},{col}] = {original_coeff:.2f} -> {quantized:.2f} (q_level={int(round(quantized/Q))})")

# Apply IDCT
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in modified_bands:
        modified_bands[band_name] = apply_idct(modified_bands[band_name])

# Reconstruct
stego_img = dwt_reconstruct(modified_bands)

# Save
cv2.imwrite("debug_minimal.png", stego_img.astype(np.uint8))

# Also check if image changed
print(f"\nImage difference (max pixel change): {np.max(np.abs(img - stego_img))}")

print("\n" + "="*70)
print("EXTRACTION")
print("="*70)

# Load
stego_loaded = read_image("debug_minimal.png")
bands_loaded = dwt_decompose(stego_loaded, levels=2)

# Apply DCT
dct_bands_loaded = bands_loaded.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands_loaded:
        dct_bands_loaded[band_name] = apply_dct(bands_loaded[band_name])

# Build same coefficient list
all_coefficients_extract = []
for band_name in embed_bands:
    if band_name in dct_bands_loaded:
        band = dct_bands_loaded[band_name]
        for i in range(8, band.shape[0]):
            for j in range(8, band.shape[1]):
                all_coefficients_extract.append((band_name, i, j))
                if len(all_coefficients_extract) >= len(payload_bits):
                    break
            if len(all_coefficients_extract) >= len(payload_bits):
                break
    if len(all_coefficients_extract) >= len(payload_bits):
        break

print(f"\nExtracting {len(payload_bits)} bits from {len(all_coefficients_extract)} coefficients")
print("\nFirst 8 bits extraction:")

# Extract
extracted_bits = []
for i in range(len(payload_bits)):
    band_name, row, col = all_coefficients_extract[i]
    coeff = dct_bands_loaded[band_name][row, col]
    
    q_level = round(coeff / Q)
    extracted_bit = '1' if q_level % 2 == 1 else '0'
    extracted_bits.append(extracted_bit)
    
    if i < 8:
        print(f"  Bit {i}: {band_name}[{row},{col}] = {coeff:.2f} -> q_level={int(q_level)} -> bit '{extracted_bit}'")

extracted_bits_str = ''.join(extracted_bits)
extracted_bytes = bits_to_bytes(extracted_bits_str)

print(f"\nOriginal payload: {test_payload.hex()}")
print(f"Extracted payload: {extracted_bytes[:len(test_payload)].hex()}")
print(f"Match: {test_payload == extracted_bytes[:len(test_payload)]}")

print(f"\nOriginal bits:  {bytes_to_bits(test_payload)}")
print(f"Extracted bits: {extracted_bits_str}")
