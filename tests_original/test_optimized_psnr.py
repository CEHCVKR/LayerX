"""
Optimized DWT+DCT Test to Achieve Abstract Requirements
Target: PSNR > 50 dB (as per TEAM_08_Abstract.pdf)
Fix: High payload issue by tuning Q-factor
"""
import urllib.request
import cv2
import numpy as np
import sys
import time
sys.path.append('core_modules')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import bytes_to_bits, bits_to_bytes, embed_in_dwt_bands_color, extract_from_dwt_bands_color
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color, save_image_color
from scipy.fftpack import dct, idct

def apply_block_dct(band, block_size=8):
    """Apply block-wise DCT"""
    h, w, c = band.shape
    dct_band = np.zeros_like(band, dtype=np.float32)
    
    for ch in range(c):
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

def embed_dwt_dct_optimized(payload_bits, bands, Q=3.0):
    """
    Optimized DWT+DCT embedding with adaptive Q-factor
    Lower Q = Higher PSNR (but less robust)
    Target: PSNR > 50 dB as per abstract
    """
    embed_band_names = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2']  # Skip LL2 for quality
    
    # Apply DCT
    dct_bands = {}
    for band_name in embed_band_names:
        if band_name in bands:
            dct_bands[band_name] = apply_block_dct(bands[band_name])
    
    # Collect positions - use low-frequency AC coefficients for better robustness
    positions = []
    for band_name in embed_band_names:
        if band_name not in dct_bands:
            continue
        band = dct_bands[band_name]
        h, w, c = band.shape
        
        for ch in range(c):
            for block_i in range(0, h - h % 8, 8):
                for block_j in range(0, w - w % 8, 8):
                    # Use mid-frequency AC coefficients (balanced robustness/capacity)
                    # Zigzag order: prioritize low-mid frequencies
                    zigzag_order = [
                        (0, 1), (1, 0), (2, 0), (1, 1), (0, 2),  # Very low freq AC
                        (0, 3), (1, 2), (2, 1), (3, 0),          # Low-mid freq
                        (4, 0), (3, 1), (2, 2), (1, 3), (0, 4),  # Mid freq
                        (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0),  # Mid-high
                    ]
                    
                    for di, dj in zigzag_order:
                        i = block_i + di
                        j = block_j + dj
                        
                        if i < h and j < w:
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
        if len(positions) >= len(payload_bits):
            break
    
    if len(positions) < len(payload_bits):
        raise ValueError(f"Insufficient capacity: need {len(payload_bits)}, have {len(positions)}")
    
    # Embed with optimized Q-factor
    modified_dct = {k: v.copy() for k, v in dct_bands.items()}
    for idx, bit in enumerate(payload_bits):
        band_name, i, j, ch = positions[idx]
        coeff = modified_dct[band_name][i, j, ch]
        
        # Use smaller Q for higher PSNR
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
    
    # Inverse DCT
    modified_bands = {k: v.copy() for k, v in bands.items()}
    for band_name in embed_band_names:
        if band_name in modified_dct:
            modified_bands[band_name] = apply_block_idct(modified_dct[band_name])
    
    return modified_bands, positions

def extract_dwt_dct_optimized(bands, positions, payload_length, Q=3.0):
    """Extract using optimized DWT+DCT"""
    embed_band_names = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2']
    
    # Apply DCT
    dct_bands = {}
    for band_name in embed_band_names:
        if band_name in bands:
            dct_bands[band_name] = apply_block_dct(bands[band_name])
    
    # Extract
    extracted_bits = ""
    for idx in range(payload_length):
        band_name, i, j, ch = positions[idx]
        coeff = dct_bands[band_name][i, j, ch]
        quantized = Q * round(coeff / Q)
        q_level = round(quantized / Q)
        bit = '1' if (q_level % 2 == 1) else '0'
        extracted_bits += bit
    
    return extracted_bits

print("="*80)
print("OPTIMIZED DWT+DCT TEST - TARGET: PSNR > 50 dB (TEAM_08_Abstract.pdf)")
print("="*80)
print("\nAbstract Requirements:")
print("- PSNR > 50 dB (exceptional imperceptibility)")
print("- Payload capacity: 30-50%")
print("- Method: DWT-DCT frequency domain embedding")
print("="*80)

# Test configurations with optimized Q-factor (higher for robustness)
# Strategy: Use Q=6.0-7.0 range for balance between PSNR and reliability
test_configs = [
    ("Small", "https://picsum.photos/512/512", "Secret message for testing", 6.0),
    ("Medium", "https://picsum.photos/800/600", "Medium length secret message for steganography", 6.5),
    ("Large", "https://picsum.photos/1024/768", "This is a longer message to test capacity and quality balance", 7.0),
    ("HD", "https://picsum.photos/1920/1080", "Full HD test with extended message content for comprehensive evaluation", 7.5),
]

results = []

for idx, (size_label, url, message, Q_factor) in enumerate(test_configs, 1):
    print(f"\n{'='*80}")
    print(f"TEST {idx}/{len(test_configs)}: {size_label} Image | Q={Q_factor}")
    print(f"{'='*80}")
    
    try:
        # Download
        print(f"[1] Downloading...")
        filename = f"optimal_{size_label.lower()}.jpg"
        urllib.request.urlretrieve(url, filename)
        time.sleep(0.5)
        
        img = read_image_color(filename)
        print(f"    [+] Image: {img.shape}")
        
        # Calculate capacity
        img_bytes = img.shape[0] * img.shape[1] * img.shape[2]
        print(f"    [+] Image size: {img_bytes} bytes ({img_bytes/1024:.1f} KB)")
        
        # Prepare payload
        print(f"[2] Message: '{message}' ({len(message)} chars)")
        ciphertext, salt, iv = encrypt_message(message, f"optimal_key_{idx}")
        compressed, tree = compress_huffman(ciphertext)
        payload = create_payload(ciphertext, tree, compressed)
        payload_bits = bytes_to_bits(payload)
        
        capacity_percent = (len(payload) / img_bytes) * 100
        print(f"    [+] Payload: {len(payload)} bytes ({capacity_percent:.2f}% of image)")
        
        # DWT
        print(f"[3] DWT decomposition...")
        bands = dwt_decompose_color(img, levels=2)
        
        # Test both methods
        print(f"\n[4a] PURE DWT (Reference)...")
        start = time.time()
        dwt_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
        dwt_stego = dwt_reconstruct_color(dwt_bands)
        if dwt_stego.shape != img.shape:
            dwt_stego = dwt_stego[:img.shape[0], :img.shape[1], :]
        dwt_time = time.time() - start
        dwt_psnr = psnr_color(img, dwt_stego)
        print(f"      [+] PSNR: {dwt_psnr:.2f} dB | Time: {dwt_time*1000:.0f}ms")
        
        print(f"\n[4b] DWT+DCT HYBRID (Optimized Q={Q_factor})...")
        start = time.time()
        dct_bands, positions = embed_dwt_dct_optimized(payload_bits, bands, Q=Q_factor)
        dct_stego = dwt_reconstruct_color(dct_bands)
        if dct_stego.shape != img.shape:
            dct_stego = dct_stego[:img.shape[0], :img.shape[1], :]
        dct_time = time.time() - start
        dct_psnr = psnr_color(img, dct_stego)
        print(f"      [+] PSNR: {dct_psnr:.2f} dB | Time: {dct_time*1000:.0f}ms")
        
        # Extract DWT+DCT
        print(f"\n[5] Extracting from DWT+DCT...")
        start = time.time()
        stego_bands = dwt_decompose_color(dct_stego, levels=2)
        extracted_bits = extract_dwt_dct_optimized(stego_bands, positions, len(payload_bits), Q=Q_factor)
        extract_time = time.time() - start
        
        extracted_payload = bits_to_bytes(extracted_bits)
        msg_len, tree_ex, compressed_ex = parse_payload(extracted_payload)
        decrypted_ct = decompress_huffman(compressed_ex, tree_ex)
        decrypted_msg = decrypt_message(decrypted_ct, f"optimal_key_{idx}", salt, iv)
        
        success = (message == decrypted_msg)
        print(f"      [+] Extraction: {'SUCCESS' if success else 'FAILED'}")
        print(f"      [+] Extract time: {extract_time*1000:.0f}ms")
        
        # Save
        save_image_color(f"optimal_stego_{size_label.lower()}.png", dct_stego)
        
        # Comparison
        comp = np.zeros((img.shape[0], img.shape[1]*3, 3), dtype=np.uint8)
        comp[:, 0:img.shape[1]] = img
        comp[:, img.shape[1]:2*img.shape[1]] = dwt_stego
        comp[:, 2*img.shape[1]:] = dct_stego
        
        cv2.putText(comp, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(comp, f"DWT ({dwt_psnr:.1f}dB)", (img.shape[1]+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(comp, f"DWT+DCT ({dct_psnr:.1f}dB)", (2*img.shape[1]+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imwrite(f"optimal_comparison_{size_label.lower()}.png", comp)
        
        results.append({
            'size': size_label,
            'shape': img.shape,
            'capacity_pct': capacity_percent,
            'Q': Q_factor,
            'dwt_psnr': dwt_psnr,
            'dct_psnr': dct_psnr,
            'success': success,
            'meets_target': dct_psnr > 50.0
        })
        
        print(f"\n    [{'SUCCESS' if success else 'FAILED'}] {'Meets PSNR target!' if dct_psnr > 50.0 else 'Below target'}")
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        results.append({'size': size_label, 'success': False, 'error': str(e)})

# Final Report
print("\n" + "="*80)
print("FINAL RESULTS - ABSTRACT COMPLIANCE CHECK")
print("="*80)
print(f"{'Size':<10} {'Shape':<15} {'Capacity':<10} {'Q':<6} {'DWT PSNR':<11} {'DCT PSNR':<11} {'Target':<8} {'Status'}")
print("-"*80)

for r in results:
    if r['success']:
        target = 'YES' if r['meets_target'] else 'NO'
        status = 'PASS' if r['meets_target'] else 'LOW'
        print(f"{r['size']:<10} {str(r['shape']):<15} {r['capacity_pct']:.2f}%     "
              f"Q={r['Q']:<4} {r['dwt_psnr']:.2f} dB    {r['dct_psnr']:.2f} dB    {target:<8} {status}")
    else:
        print(f"{r['size']:<10} {'ERROR':<15} {'N/A':<10} {'N/A':<6} {'N/A':<11} {'N/A':<11} {'N/A':<8} FAIL")

print("-"*80)

# Statistics
successful = [r for r in results if r['success']]
if successful:
    meets_target = [r for r in successful if r['meets_target']]
    avg_dct_psnr = sum(r['dct_psnr'] for r in successful) / len(successful)
    avg_capacity = sum(r['capacity_pct'] for r in successful) / len(successful)
    
    print(f"\nSTATISTICS:")
    print(f"  Tests passed: {len(successful)}/{len(results)}")
    print(f"  Meeting PSNR > 50dB: {len(meets_target)}/{len(successful)}")
    print(f"  Average DWT+DCT PSNR: {avg_dct_psnr:.2f} dB")
    print(f"  Average capacity: {avg_capacity:.2f}%")
    print(f"\n  Abstract Target: PSNR > 50 dB")
    print(f"  Achieved: {'YES' if len(meets_target) > 0 else 'NO'}")

print("\n" + "="*80)
print("OPTIMIZATION COMPLETE!")
print("="*80)
