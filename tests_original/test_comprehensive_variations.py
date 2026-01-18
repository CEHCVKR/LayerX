"""
Comprehensive Test: Multiple Internet Images with Various Configurations
Tests different image sizes, payload sizes, and embedding methods (DWT vs DWT+DCT)
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

def embed_dwt_dct_hybrid(payload_bits, bands, Q=10.0):
    """Embed using DWT+DCT hybrid"""
    embed_band_names = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
    
    # Apply DCT
    dct_bands = {}
    for band_name in embed_band_names:
        if band_name in bands:
            dct_bands[band_name] = apply_block_dct(bands[band_name])
    
    # Collect positions (skip DC)
    positions = []
    for band_name in embed_band_names:
        if band_name not in dct_bands:
            continue
        band = dct_bands[band_name]
        h, w, c = band.shape
        
        for ch in range(c):
            for i in range(0, h, 8):
                for j in range(0, w, 8):
                    for bi in range(i, min(i+8, h)):
                        for bj in range(j, min(j+8, w)):
                            if (bi % 8 != 0 or bj % 8 != 0):
                                positions.append((band_name, bi, bj, ch))
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
    
    # Embed
    modified_dct = {k: v.copy() for k, v in dct_bands.items()}
    for idx, bit in enumerate(payload_bits):
        band_name, i, j, ch = positions[idx]
        coeff = modified_dct[band_name][i, j, ch]
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
    modified_bands = {k: v.copy() if k not in embed_band_names else None for k, v in bands.items()}
    for band_name in embed_band_names:
        if band_name in modified_dct:
            modified_bands[band_name] = apply_block_idct(modified_dct[band_name])
    
    return modified_bands, positions

def extract_dwt_dct_hybrid(bands, positions, payload_length, Q=10.0):
    """Extract using DWT+DCT hybrid"""
    embed_band_names = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
    
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

# Test configurations
test_configs = [
    # Format: (size, url, message, method)
    ("Small", "https://picsum.photos/512/512", "Short message", "DWT"),
    ("Small", "https://picsum.photos/512/512", "Short message", "DWT+DCT"),
    
    ("Medium", "https://picsum.photos/800/600", "Medium length message for testing capacity", "DWT"),
    ("Medium", "https://picsum.photos/800/600", "Medium length message for testing capacity", "DWT+DCT"),
    
    ("Large", "https://picsum.photos/1200/900", "This is a much longer message to test the capacity limits of the steganographic system with larger images and higher payloads!", "DWT"),
    ("Large", "https://picsum.photos/1200/900", "This is a much longer message to test the capacity limits of the steganographic system with larger images and higher payloads!", "DWT+DCT"),
    
    ("Portrait", "https://picsum.photos/600/800", "Portrait orientation test", "DWT"),
    ("Portrait", "https://picsum.photos/600/800", "Portrait orientation test", "DWT+DCT"),
    
    ("HD", "https://picsum.photos/1920/1080", "Full HD image with a very long secret message that tests the maximum capacity of the steganographic embedding algorithm. This message contains multiple sentences to ensure we're testing realistic payload sizes.", "DWT"),
    ("HD", "https://picsum.photos/1920/1080", "Full HD image with a very long secret message that tests the maximum capacity of the steganographic embedding algorithm. This message contains multiple sentences to ensure we're testing realistic payload sizes.", "DWT+DCT"),
]

results = []

print("="*80)
print("COMPREHENSIVE STEGANOGRAPHY TEST")
print("Multiple Images | Multiple Sizes | Multiple Methods | Multiple Payloads")
print("="*80)

for idx, (size_label, url, message, method) in enumerate(test_configs, 1):
    print(f"\n{'='*80}")
    print(f"TEST {idx}/{len(test_configs)}: {size_label} Image | {method} Method")
    print(f"{'='*80}")
    
    try:
        # Download
        print(f"[1] Downloading {size_label} image...")
        filename = f"test_{size_label.lower()}_{method.replace('+', '_')}_{idx}.jpg"
        urllib.request.urlretrieve(url, filename)
        time.sleep(0.5)  # Rate limit
        
        # Load
        img = read_image_color(filename)
        print(f"    [+] Size: {img.shape}")
        
        # Prepare payload
        print(f"[2] Message: '{message}' ({len(message)} chars)")
        ciphertext, salt, iv = encrypt_message(message, f"test_key_{idx}")
        compressed, tree = compress_huffman(ciphertext)
        payload = create_payload(ciphertext, tree, compressed)
        payload_bits = bytes_to_bits(payload)
        print(f"    [+] Payload: {len(payload)} bytes ({len(payload_bits)} bits)")
        
        # DWT
        print(f"[3] DWT decomposition (2-level)...")
        bands = dwt_decompose_color(img, levels=2)
        
        # Embed based on method
        start_time = time.time()
        
        if method == "DWT":
            print(f"[4] Embedding with PURE DWT (no DCT)...")
            modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
            positions = None
        else:  # DWT+DCT
            print(f"[4] Embedding with DWT+DCT HYBRID...")
            modified_bands, positions = embed_dwt_dct_hybrid(payload_bits, bands, Q=10.0)
        
        embed_time = time.time() - start_time
        
        # Reconstruct
        stego_img = dwt_reconstruct_color(modified_bands)
        if stego_img.shape != img.shape:
            stego_img = stego_img[:img.shape[0], :img.shape[1], :]
        
        # PSNR
        psnr_val = psnr_color(img, stego_img)
        print(f"    [+] PSNR: {psnr_val:.2f} dB")
        print(f"    [+] Embed time: {embed_time*1000:.1f} ms")
        
        # Save
        stego_filename = f"stego_{size_label.lower()}_{method.replace('+', '_')}_{idx}.png"
        save_image_color(stego_filename, stego_img)
        
        # Extract
        print(f"[5] Extracting...")
        start_time = time.time()
        
        stego_bands = dwt_decompose_color(stego_img, levels=2)
        
        if method == "DWT":
            extracted_bits = extract_from_dwt_bands_color(stego_bands, len(payload_bits), Q_factor=5.0)
        else:
            extracted_bits = extract_dwt_dct_hybrid(stego_bands, positions, len(payload_bits), Q=10.0)
        
        extract_time = time.time() - start_time
        
        extracted_payload = bits_to_bytes(extracted_bits)
        
        # Decrypt
        msg_len, tree_ex, compressed_ex = parse_payload(extracted_payload)
        decrypted_ct = decompress_huffman(compressed_ex, tree_ex)
        decrypted_msg = decrypt_message(decrypted_ct, f"test_key_{idx}", salt, iv)
        
        success = (message == decrypted_msg)
        print(f"    [+] Extract time: {extract_time*1000:.1f} ms")
        print(f"    [+] Match: {'YES' if success else 'NO'}")
        
        # Create comparison
        comp = np.zeros((img.shape[0], img.shape[1]*2, 3), dtype=np.uint8)
        comp[:, 0:img.shape[1]] = img
        comp[:, img.shape[1]:] = stego_img
        cv2.putText(comp, f"{size_label} Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(comp, f"{method} ({psnr_val:.1f}dB)", (img.shape[1]+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imwrite(f"comparison_{size_label.lower()}_{method.replace('+', '_')}_{idx}.png", comp)
        
        results.append({
            'test': idx,
            'size': size_label,
            'shape': img.shape,
            'method': method,
            'message_len': len(message),
            'payload_bytes': len(payload),
            'psnr': psnr_val,
            'embed_time': embed_time * 1000,
            'extract_time': extract_time * 1000,
            'success': success
        })
        
        print(f"    [SUCCESS] Test passed!")
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        results.append({
            'test': idx,
            'size': size_label,
            'method': method,
            'success': False,
            'error': str(e)
        })

# Summary
print("\n" + "="*80)
print("COMPREHENSIVE TEST SUMMARY")
print("="*80)
print(f"{'#':<4} {'Size':<10} {'Method':<10} {'Shape':<15} {'Msg':<5} {'Payload':<9} {'PSNR':<8} {'Time':<10} {'Result'}")
print("-"*80)

for r in results:
    if r['success']:
        print(f"{r['test']:<4} {r['size']:<10} {r['method']:<10} {str(r['shape']):<15} "
              f"{r['message_len']:<5} {r['payload_bytes']:<9} {r['psnr']:.2f} dB  "
              f"{r['embed_time']:.0f}ms/{r['extract_time']:.0f}ms  {'PASS'}")
    else:
        print(f"{r['test']:<4} {r['size']:<10} {r['method']:<10} {'N/A':<15} "
              f"{'N/A':<5} {'N/A':<9} {'N/A':<8} {'N/A':<10} FAIL")

print("-"*80)
passed = sum(1 for r in results if r['success'])
print(f"TOTAL: {passed}/{len(results)} tests passed ({passed*100//len(results)}%)")

# Statistics
if passed > 0:
    successful = [r for r in results if r['success']]
    
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    
    # By method
    dwt_only = [r for r in successful if r['method'] == 'DWT']
    dwt_dct = [r for r in successful if r['method'] == 'DWT+DCT']
    
    if dwt_only:
        avg_psnr_dwt = sum(r['psnr'] for r in dwt_only) / len(dwt_only)
        print(f"\nPure DWT ({len(dwt_only)} tests):")
        print(f"  Average PSNR: {avg_psnr_dwt:.2f} dB")
        print(f"  PSNR Range: {min(r['psnr'] for r in dwt_only):.2f} - {max(r['psnr'] for r in dwt_only):.2f} dB")
    
    if dwt_dct:
        avg_psnr_dct = sum(r['psnr'] for r in dwt_dct) / len(dwt_dct)
        print(f"\nDWT+DCT Hybrid ({len(dwt_dct)} tests):")
        print(f"  Average PSNR: {avg_psnr_dct:.2f} dB")
        print(f"  PSNR Range: {min(r['psnr'] for r in dwt_dct):.2f} - {max(r['psnr'] for r in dwt_dct):.2f} dB")
    
    # By size
    print(f"\nBy Image Size:")
    for size in ['Small', 'Medium', 'Large', 'Portrait', 'HD']:
        size_tests = [r for r in successful if r['size'] == size]
        if size_tests:
            avg_psnr = sum(r['psnr'] for r in size_tests) / len(size_tests)
            print(f"  {size}: {avg_psnr:.2f} dB average ({len(size_tests)} tests)")

print("\n" + "="*80)
print("TEST COMPLETE - All configurations tested!")
print("="*80)
