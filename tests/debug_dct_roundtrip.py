"""
Test DCT round-trip with quantized coefficients
"""
import numpy as np
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
import cv2
from scipy.fftpack import dct, idct

def apply_dct(band):
    """Apply 2D DCT"""
    return dct(dct(band.T, norm='ortho').T, norm='ortho')

def apply_idct(band):
    """Apply 2D inverse DCT"""
    return idct(idct(band.T, norm='ortho').T, norm='ortho')

# Load image
img = read_image("test_lena.png")
bands = dwt_decompose(img, levels=2)

# Take one band for testing
test_band_name = 'LH1'
original_band = bands[test_band_name].copy()

print(f"Testing DCT round-trip on {test_band_name}")
print(f"Band shape: {original_band.shape}")
print("="*70)

# Apply DCT
dct_band = apply_dct(original_band)

# Sample some coefficients
test_positions = [(10, 10), (10, 20), (20, 10), (20, 20), (30, 30)]

print("\nOriginal DCT coefficients (before quantization):")
for i, (row, col) in enumerate(test_positions):
    print(f"  Position ({row},{col}): {dct_band[row, col]:.6f}")

# Simulate quantization with Q=5.0
Q = 5.0
quantized_band = dct_band.copy()

for row, col in test_positions:
    orig = dct_band[row, col]
    quantized = Q * round(orig / Q)
    quantized_band[row, col] = quantized

print(f"\nQuantized DCT coefficients (Q={Q}):")
for row, col in test_positions:
    print(f"  Position ({row},{col}): {quantized_band[row, col]:.6f}")

# Apply IDCT
idct_band = apply_idct(quantized_band)

# Apply DCT again (simulating extraction)
dct_band_recovered = apply_dct(idct_band)

print("\nRecovered DCT coefficients (after IDCT → DCT):")
for row, col in test_positions:
    print(f"  Position ({row},{col}): {dct_band_recovered[row, col]:.6f}")

print("\nDifferences:")
for row, col in test_positions:
    original = quantized_band[row, col]
    recovered = dct_band_recovered[row, col]
    diff = recovered - original
    print(f"  Position ({row},{col}): diff = {diff:.6f} ({diff/Q:.3f} × Q)")

print("\n" + "="*70)
print("Testing embedded bit recovery")
print("="*70)

# Embed some bits
test_bits = '10101010'
positions = [(10+i, 10) for i in range(len(test_bits))]

print(f"\nEmbedding bits: {test_bits}")

# Embed in DCT domain
for i, bit in enumerate(test_bits):
    row, col = positions[i]
    coeff = dct_band[row, col]
    quantized = Q * round(coeff / Q)
    
    if bit == '1':
        q_level = round(quantized / Q)
        if q_level % 2 == 0:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    else:
        q_level = round(quantized / Q)
        if q_level % 2 == 1:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    
    quantized_band[row, col] = quantized
    print(f"  Bit '{bit}' at ({row},{col}): {coeff:.2f} → {quantized:.2f} (q_level={int(round(quantized/Q))})")

# Reconstruct through full pipeline
idct_result = apply_idct(quantized_band)
dct_result = apply_dct(idct_result)

# Extract bits
extracted_bits = []
for i, (row, col) in enumerate(positions):
    coeff = dct_result[row, col]
    q_level = round(coeff / Q)
    extracted_bit = '1' if q_level % 2 == 1 else '0'
    extracted_bits.append(extracted_bit)
    print(f"  Position ({row},{col}): {coeff:.2f} → q_level={int(q_level)} → bit '{extracted_bit}'")

extracted_str = ''.join(extracted_bits)
print(f"\nOriginal bits:  {test_bits}")
print(f"Extracted bits: {extracted_str}")
print(f"Match: {test_bits == extracted_str} {'✅' if test_bits == extracted_str else '❌'}")
