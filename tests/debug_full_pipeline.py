"""
Test full pipeline: DCT → IDCT → DWT Reconstruct → Save → Load → DWT Decompose → DCT
"""
import numpy as np
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
import cv2
from scipy.fftpack import dct, idct

def apply_dct(band):
    """Apply 2D DCT"""
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    """Apply inverse 2D DCT"""
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

# Load image
img = read_image("test_lena.png")
bands = dwt_decompose(img, levels=2)

# Apply DCT to bands
dct_bands = bands.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands:
        dct_bands[band_name] = apply_dct(bands[band_name])

print("Testing full pipeline with quantization")
print("="*70)

# Test some positions across different bands
test_data = [
    ('LH1', 10, 10),
    ('HL1', 15, 15),
    ('LH2', 20, 20),
    ('HH1', 12, 12),
]

Q = 5.0

# Embed test bits
test_bits = '10101010'
for i, bit in enumerate(test_bits):
    if i < len(test_data):
        band_name, row, col = test_data[i]
        coeff = dct_bands[band_name][row, col]
        quantized = Q * round(coeff / Q)
        
        if bit == '1':
            q_level = round(quantized / Q)
            if q_level % 2 == 0:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        else:
            q_level = round(quantized / Q)
            if q_level % 2 == 1:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        
        dct_bands[band_name][row, col] = quantized
        print(f"Embedded bit '{bit}' in {band_name}[{row},{col}]: {coeff:.2f} → {quantized:.2f}")

# Apply IDCT
modified_bands = bands.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in dct_bands:
        modified_bands[band_name] = apply_idct(dct_bands[band_name])

# Reconstruct image
stego_img = dwt_reconstruct(modified_bands)

# Save and reload
cv2.imwrite("debug_full_pipeline.png", stego_img.astype(np.uint8))
stego_img_loaded = read_image("debug_full_pipeline.png")

# Decompose again
bands_loaded = dwt_decompose(stego_img_loaded, levels=2)

# Apply DCT again
dct_bands_loaded = bands_loaded.copy()
for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
    if band_name in bands_loaded:
        dct_bands_loaded[band_name] = apply_dct(bands_loaded[band_name])

# Extract bits
print("\nExtraction:")
extracted_bits = []
for i, bit in enumerate(test_bits):
    if i < len(test_data):
        band_name, row, col = test_data[i]
        coeff = dct_bands_loaded[band_name][row, col]
        q_level = round(coeff / Q)
        extracted_bit = '1' if q_level % 2 == 1 else '0'
        extracted_bits.append(extracted_bit)
        print(f"Extracted from {band_name}[{row},{col}]: {coeff:.2f} → q_level={int(q_level)} → bit '{extracted_bit}'")

extracted_str = ''.join(extracted_bits)
print(f"\nOriginal bits:  {test_bits[:len(extracted_bits)]}")
print(f"Extracted bits: {extracted_str}")
print(f"Match: {test_bits[:len(extracted_bits)] == extracted_str} {'✅' if test_bits[:len(extracted_bits)] == extracted_str else '❌'}")
