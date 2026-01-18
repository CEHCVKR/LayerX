#!/usr/bin/env python3
"""
Quick Robustness Test: Old vs New Pipeline under JPEG Compression
=================================================================
"""

import sys
import os
import cv2
import numpy as np
import pickle

sys.path.append('core_modules')
from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes

print("⚡ QUICK ROBUSTNESS TEST: Old vs New Pipeline")
print("=" * 50)

# Create test image
test_img = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
test_message = "LayerX robustness test!"

def test_pipeline_robustness(use_reed_solomon=False, jpeg_quality=50):
    """Test pipeline robustness against JPEG compression"""
    
    try:
        key = "test_key_12345"
        encrypted, salt, iv = encrypt_message(test_message, key)
        compressed, tree = compress_huffman(encrypted)
        
        if use_reed_solomon:
            payload = create_payload(test_message.encode(), pickle.dumps(tree), compressed)
            pipeline_name = f"Reed-Solomon ECC"
        else:
            payload = compressed
            pipeline_name = f"No ECC"
            
        payload_bits = bytes_to_bits(payload)
        
        # Embed
        bands = dwt_decompose(test_img, levels=2)
        stego_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=5.0)
        stego = dwt_reconstruct(stego_bands).astype(np.uint8)
        
        # Apply JPEG compression
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        result, encoded_img = cv2.imencode('.jpg', stego, encode_param)
        jpeg_compressed = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
        
        # Try to extract
        compressed_bands = dwt_decompose(jpeg_compressed, levels=2)
        extracted_bits = extract_from_dwt_bands(compressed_bands, len(payload_bits), Q_factor=5.0)
        extracted_payload = bits_to_bytes(extracted_bits)
        
        if use_reed_solomon:
            # Parse Reed-Solomon protected payload
            msg_len, tree_bytes, compressed_data = parse_payload(extracted_payload)
            tree_recovered = pickle.loads(tree_bytes)
            decompressed = decompress_huffman(compressed_data, tree_recovered)
        else:
            # Direct decompression
            decompressed = decompress_huffman(extracted_payload, tree)
        
        original_message = decrypt_message(decompressed, key, salt, iv)
        
        success = (original_message == test_message)
        return success, pipeline_name, len(payload)
        
    except Exception as e:
        return False, f"{pipeline_name} (ERROR: {str(e)[:50]})", len(payload) if 'payload' in locals() else 0

# Test both pipelines at different JPEG qualities
jpeg_qualities = [10, 30, 50, 70, 90]

print(f"🧪 Testing message: '{test_message}'")
print(f"📊 JPEG Quality Levels: {jpeg_qualities}")
print()

for quality in jpeg_qualities:
    print(f"📷 JPEG Quality = {quality}:")
    
    # Test old pipeline (no ECC)
    old_success, old_name, old_size = test_pipeline_robustness(use_reed_solomon=False, jpeg_quality=quality)
    
    # Test new pipeline (Reed-Solomon ECC)
    new_success, new_name, new_size = test_pipeline_robustness(use_reed_solomon=True, jpeg_quality=quality)
    
    print(f"   ❌ No ECC ({old_size} bytes): {'✅ SUCCESS' if old_success else '❌ FAILED'}")
    print(f"   🛡️  Reed-Solomon ({new_size} bytes): {'✅ SUCCESS' if new_success else '❌ FAILED'}")
    
    if new_success and not old_success:
        print(f"   🎯 IMPROVEMENT: Reed-Solomon ECC saves the day!")
    elif old_success and new_success:
        print(f"   ✅ Both work at this quality level")
    elif not old_success and not new_success:
        print(f"   💀 Both fail - very harsh conditions")
    
    print()

print("🏆 CONCLUSION:")
print("This quick test shows if Reed-Solomon ECC actually improves robustness!")
print("If Reed-Solomon performs better, our 15.6% result was completely wrong!")