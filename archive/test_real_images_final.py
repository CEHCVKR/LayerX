"""
Test LayerX with REAL Downloaded Images from Internet
======================================================
Uses: downloaded_abstract.jpg, downloaded_nature.jpg, downloaded_portrait.jpg
"""

import os
import sys
import time
import cv2
import numpy as np
from datetime import datetime

from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import dwt_decompose, dwt_reconstruct, psnr
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands

print("="*80)
print("LAYERX TEST WITH REAL INTERNET IMAGES")
print("="*80)
print()

# Real downloaded images
real_images = [
    ("demo_outputs/downloaded_abstract.jpg", "Abstract Art (Internet)"),
    ("demo_outputs/downloaded_nature.jpg", "Nature Photo (Internet)"),
    ("demo_outputs/downloaded_portrait.jpg", "Portrait Photo (Internet)")
]

password = "test_password_2026"
test_payloads = [128, 512, 2048, 8192]  # Bytes

results = []

for img_path, img_name in real_images:
    if not os.path.exists(img_path):
        print(f"❌ {img_name} not found at {img_path}")
        continue
    
    print(f"\n{'='*80}")
    print(f"Testing: {img_name}")
    print(f"{'='*80}")
    
    # Load image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"  ❌ Failed to load image")
        continue
    
    print(f"  Image Size: {img.shape[1]}×{img.shape[0]} pixels")
    print(f"  Capacity: ~{(img.shape[0]*img.shape[1])//16} bytes")
    print()
    
    for payload_size in test_payloads:
        print(f"  Payload: {payload_size} bytes")
        print(f"  {'-'*76}")
        
        try:
            # Create test message
            message = "X" * payload_size
            
            # Encrypt
            start = time.time()
            ciphertext, salt, iv = encrypt_message(message, password)
            encrypt_time = (time.time() - start) * 1000
            
            # Compress
            start = time.time()
            compressed, tree = compress_huffman(ciphertext)
            compress_time = (time.time() - start) * 1000
            compression_ratio = len(compressed) / len(ciphertext)
            
            # Create payload
            payload = create_payload(ciphertext, tree, compressed)
            
            # Convert to bits
            payload_bits = []
            for byte in payload:
                for i in range(8):
                    payload_bits.append((byte >> (7-i)) & 1)
            
            # Embed
            start = time.time()
            bands = dwt_decompose(img, levels=2)
            stego = embed_in_dwt_bands(img, bands, payload_bits, Q_factor=5.0)
            embed_time = (time.time() - start) * 1000
            
            # Calculate PSNR
            psnr_val = psnr(img, stego)
            
            # Extract
            start = time.time()
            stego_bands = dwt_decompose(stego, levels=2)
            extracted_bits = extract_from_dwt_bands(stego_bands, len(payload_bits), Q_factor=5.0)
            extract_time = (time.time() - start) * 1000
            
            # Convert bits to bytes
            extracted_bytes = bytearray()
            for i in range(0, len(extracted_bits), 8):
                if i+8 <= len(extracted_bits):
                    byte_val = 0
                    for j in range(8):
                        byte_val = (byte_val << 1) | extracted_bits[i+j]
                    extracted_bytes.append(byte_val)
            
            # Parse payload
            msg_len, tree_out, comp_out = parse_payload(bytes(extracted_bytes))
            
            # Decompress
            start = time.time()
            decompressed = decompress_huffman(comp_out, tree_out)
            decompress_time = (time.time() - start) * 1000
            
            # Decrypt
            start = time.time()
            decrypted = decrypt_message(decompressed, password, salt, iv)
            decrypt_time = (time.time() - start) * 1000
            
            # Verify
            success = decrypted == message
            
            # Results
            total_time = encrypt_time + compress_time + embed_time + extract_time + decompress_time + decrypt_time
            
            print(f"    ✓ PSNR: {psnr_val:.2f} dB")
            print(f"    ✓ Compression: {compression_ratio*100:.1f}%")
            print(f"    ✓ Total Time: {total_time:.1f} ms")
            print(f"    ✓ Extraction: {'SUCCESS' if success else 'FAILED'}")
            
            results.append({
                "image": img_name,
                "payload": payload_size,
                "psnr": psnr_val,
                "compression": compression_ratio,
                "time": total_time,
                "success": success
            })
            
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)[:60]}")
            results.append({
                "image": img_name,
                "payload": payload_size,
                "success": False,
                "error": str(e)
            })
        
        print()

# Summary
print("\n" + "="*80)
print("SUMMARY OF REAL IMAGE TESTS")
print("="*80)
print()

successful_tests = [r for r in results if r.get("success", False)]
if successful_tests:
    avg_psnr = sum(r["psnr"] for r in successful_tests) / len(successful_tests)
    avg_time = sum(r["time"] for r in successful_tests) / len(successful_tests)
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful_tests)} ({len(successful_tests)/len(results)*100:.1f}%)")
    print(f"Average PSNR: {avg_psnr:.2f} dB")
    print(f"Average Time: {avg_time:.1f} ms")
    print()
    
    # PSNR breakdown
    print("PSNR by Payload Size:")
    for payload in test_payloads:
        payload_results = [r for r in successful_tests if r["payload"] == payload]
        if payload_results:
            avg = sum(r["psnr"] for r in payload_results) / len(payload_results)
            print(f"  {payload:5d}B: {avg:.2f} dB (n={len(payload_results)})")
    
    print()
    print("✓ ALL TESTS USED REAL IMAGES DOWNLOADED FROM INTERNET")
else:
    print("❌ No successful tests")

print("="*80)
