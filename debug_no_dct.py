"""
Test embedding DIRECTLY in DWT bands (no DCT)
"""
import numpy as np
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
import cv2

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

# Test payload
test_payload = b'\x10\x00\x00\x00'
payload_bits = bytes_to_bits(test_payload)
print(f"Test payload: {test_payload.hex()}")
print(f"Test payload bits: {payload_bits}")

# Load image
img = read_image("test_lena.png")
bands = dwt_decompose(img, levels=2)

# NO DCT - embed directly in DWT bands
Q = 5.0
embed_bands_list = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']

# Build coefficient list
all_coefficients = []
for band_name in embed_bands_list:
    if band_name in bands:
        band = bands[band_name]
        for i in range(8, band.shape[0]):
            for j in range(8, band.shape[1]):
                all_coefficients.append((band_name, i, j))
                if len(all_coefficients) >= len(payload_bits):
                    break
            if len(all_coefficients) >= len(payload_bits):
                break
    if len(all_coefficients) >= len(payload_bits):
        break

print(f"\nEmbedding {len(payload_bits)} bits directly in DWT bands")
print("First 8 bits embedding:")

# Create modified bands
modified_bands = {}
for band_name, band_data in bands.items():
    if isinstance(band_data, np.ndarray):
        modified_bands[band_name] = band_data.copy()
    else:
        modified_bands[band_name] = band_data

# Embed in spatial DWT coefficients
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
        print(f"  Bit {i} ('{bit}'): {band_name}[{row},{col}] = {original_coeff:.2f} -> {quantized:.2f}")

# Reconstruct directly
stego_img = dwt_reconstruct(modified_bands)

# Save
cv2.imwrite("debug_no_dct.png", stego_img.astype(np.uint8))

print(f"\nImage changed: {np.max(np.abs(img - stego_img)):.2f} pixels")

print("\n" + "="*70)
print("EXTRACTION")
print("="*70)

# Load
stego_loaded = read_image("debug_no_dct.png")
bands_loaded = dwt_decompose(stego_loaded, levels=2)

# Build same coefficient list
all_coefficients_extract = []
for band_name in embed_bands_list:
    if band_name in bands_loaded:
        band = bands_loaded[band_name]
        for i in range(8, band.shape[0]):
            for j in range(8, band.shape[1]):
                all_coefficients_extract.append((band_name, i, j))
                if len(all_coefficients_extract) >= len(payload_bits):
                    break
            if len(all_coefficients_extract) >= len(payload_bits):
                break
    if len(all_coefficients_extract) >= len(payload_bits):
        break

print("First 8 bits extraction:")

# Extract from spatial DWT coefficients
extracted_bits = []
for i in range(len(payload_bits)):
    band_name, row, col = all_coefficients_extract[i]
    coeff = bands_loaded[band_name][row, col]
    
    q_level = round(coeff / Q)
    extracted_bit = '1' if q_level % 2 == 1 else '0'
    extracted_bits.append(extracted_bit)
    
    if i < 8:
        print(f"  Bit {i}: {band_name}[{row},{col}] = {coeff:.2f} -> q_level={int(q_level)} -> bit '{extracted_bit}'")

extracted_bits_str = ''.join(extracted_bits)
extracted_bytes = bits_to_bytes(extracted_bits_str)

print(f"\nOriginal payload:  {test_payload.hex()}")
print(f"Extracted payload: {extracted_bytes[:len(test_payload)].hex()}")
print(f"Match: {test_payload == extracted_bytes[:len(test_payload)]} {'SUCCESS!' if test_payload == extracted_bytes[:len(test_payload)] else 'FAILED'}")
