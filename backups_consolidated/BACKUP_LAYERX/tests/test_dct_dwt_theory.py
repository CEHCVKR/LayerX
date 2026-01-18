"""
Test: Why does DCT on DWT bands not work?
The issue is that after embedding in DCT domain, we need to ensure
the spatial domain (after IDCT) actually changes the image pixels.
"""
import numpy as np
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from scipy.fftpack import dct, idct
import cv2

def apply_dct(band):
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

# Load and decompose
img = read_image("cover.png")
bands_original = dwt_decompose(img, levels=2)

# Test 1: Modify DWT band directly (our current fix)
print("TEST 1: Direct DWT modification")
print("="*70)
bands_test1 = {k: v.copy() if isinstance(v, np.ndarray) else v for k, v in bands_original.items()}
bands_test1['LH1'][10, 10] = 100.0  # Large change
img_test1 = dwt_reconstruct(bands_test1)
print(f"Original coeff: {bands_original['LH1'][10,10]:.2f}")
print(f"Modified coeff: {bands_test1['LH1'][10,10]:.2f}")
print(f"Image changed: {np.max(np.abs(img - img_test1)):.2f} pixels")
print(f"PSNR: {psnr(img, img_test1):.2f} dB")

# Test 2: Modify DCT of DWT band, then IDCT back
print("\nTEST 2: DCT→modify→IDCT on DWT band")
print("="*70)
bands_test2 = {k: v.copy() if isinstance(v, np.ndarray) else v for k, v in bands_original.items()}

# Apply DCT to LH1
dct_lh1 = apply_dct(bands_test2['LH1'])
print(f"Original DCT coeff: {dct_lh1[10,10]:.2f}")

# Modify DCT coefficient
dct_lh1[10, 10] = 100.0
print(f"Modified DCT coeff: {dct_lh1[10,10]:.2f}")

# Apply IDCT back to spatial DWT domain
bands_test2['LH1'] = apply_idct(dct_lh1)
print(f"After IDCT, spatial coeff: {bands_test2['LH1'][10,10]:.2f}")

# Reconstruct
img_test2 = dwt_reconstruct(bands_test2)
print(f"Image changed: {np.max(np.abs(img - img_test2)):.2f} pixels")
print(f"PSNR: {psnr(img, img_test2):.2f} dB")

# Test 3: Check if spatial changes are preserved after save/load
print("\nTEST 3: Does PNG save/load preserve changes?")
print("="*70)
cv2.imwrite("test_modified.png", img_test2.astype('uint8'))
img_loaded = read_image("test_modified.png")
bands_loaded = dwt_decompose(img_loaded, levels=2)
print(f"Original spatial: {bands_test2['LH1'][10,10]:.2f}")
print(f"After save/load:  {bands_loaded['LH1'][10,10]:.2f}")
print(f"Difference: {abs(bands_test2['LH1'][10,10] - bands_loaded['LH1'][10,10]):.4f}")

# Apply DCT again and check
dct_lh1_loaded = apply_dct(bands_loaded['LH1'])
print(f"\nOriginal DCT: {dct_lh1[10,10]:.2f}")
print(f"Loaded DCT:   {dct_lh1_loaded[10,10]:.2f}")
print(f"Difference: {abs(dct_lh1[10,10] - dct_lh1_loaded[10,10]):.4f}")

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("Test 1 (Direct DWT): Works, changes preserved")
print("Test 2 (DCT→IDCT): Should work if IDCT properly modifies spatial domain")
print("Test 3 (Round-trip): Need to check if DCT changes survive PNG compression")
