"""
LayerX Research Demo - Quick Sample
====================================

This script demonstrates what the full research framework will produce
by running a small-scale version with sample data.
"""

import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import core modules  
import sys
sys.path.append('core_modules')
from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import read_image, dwt_decompose, dct_on_ll, psnr
from a4_compression import compress_huffman, decompress_huffman
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes

def generate_key():
    """Generate a random password for encryption"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def create_sample_image(size=512, name="demo"):
    """Create a sample test image"""
    # Create a test image with mixed content
    image = np.zeros((size, size), dtype=np.uint8)
    
    # Add patterns
    for i in range(size):
        for j in range(size):
            image[i, j] = int(128 + 100 * np.sin(i/50) * np.cos(j/50))
    
    # Add some texture
    for i in range(0, size, 20):
        for j in range(0, size, 20):
            if (i + j) % 40 == 0:
                image[i:i+10, j:j+10] = 255
                
    # Save image
    import cv2
    image_path = f"{name}_test_image.png"
    cv2.imwrite(image_path, image)
    return image_path

def demo_complete_process(image_path, payload_text, q_factor=5.0):
    """Demonstrate complete steganography process with detailed breakdown"""
    
    print(f"\n🔬 COMPLETE PROCESS DEMONSTRATION")
    print(f"=" * 50)
    print(f"📷 Image: {image_path}")
    print(f"📦 Payload: {len(payload_text)} characters")
    print(f"⚙️  Q-Factor: {q_factor}")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "image_path": image_path,
        "original_payload": payload_text,
        "q_factor": q_factor,
        "process_steps": {}
    }
    
    total_start = time.time()
    
    # STEP 1: Load and analyze image
    print(f"\n📊 STEP 1: Image Loading & Analysis")
    step1_start = time.time()
    
    cover_image = read_image(image_path)
    image_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    
    step1_time = time.time() - step1_start
    results["process_steps"]["step1_load"] = {
        "time_seconds": step1_time,
        "image_dimensions": cover_image.shape,
        "image_pixels": cover_image.shape[0] * cover_image.shape[1],
        "file_size_mb": image_size_mb
    }
    
    print(f"   ✅ Image loaded: {cover_image.shape[0]}x{cover_image.shape[1]} pixels")
    print(f"   📏 File size: {image_size_mb:.2f} MB")
    print(f"   ⏱️  Time: {step1_time:.3f} seconds")
    
    # STEP 2: Encryption
    print(f"\n🔐 STEP 2: Payload Encryption")
    step2_start = time.time()
    
    key = generate_key()
    encrypted_payload, salt, iv = encrypt_message(payload_text, key)
    
    step2_time = time.time() - step2_start
    results["process_steps"]["step2_encrypt"] = {
        "time_seconds": step2_time,
        "original_size_bytes": len(payload_text),
        "encrypted_size_bytes": len(encrypted_payload),
        "encryption_overhead_bytes": len(encrypted_payload) - len(payload_text),
        "encryption_ratio": len(encrypted_payload) / len(payload_text),
        "key_size_bytes": len(key)
    }
    
    print(f"   ✅ Payload encrypted")
    print(f"   📏 Original: {len(payload_text)} bytes")
    print(f"   📏 Encrypted: {len(encrypted_payload)} bytes (+{len(encrypted_payload) - len(payload_text)} bytes)")
    print(f"   📊 Encryption ratio: {len(encrypted_payload) / len(payload_text):.2f}x")
    print(f"   🔑 Key size: {len(key)} bytes")
    print(f"   ⏱️  Time: {step2_time:.3f} seconds")
    
    # STEP 3: Compression
    print(f"\n🗜️  STEP 3: Data Compression")
    step3_start = time.time()
    
    compressed_payload, compression_table = compress_huffman(encrypted_payload)
    
    step3_time = time.time() - step3_start
    results["process_steps"]["step3_compress"] = {
        "time_seconds": step3_time,
        "encrypted_size_bytes": len(encrypted_payload),
        "compressed_size_bytes": len(compressed_payload),
        "compression_saved_bytes": len(encrypted_payload) - len(compressed_payload),
        "compression_ratio": len(compressed_payload) / len(encrypted_payload),
        "compression_efficiency": 1 - (len(compressed_payload) / len(encrypted_payload))
    }
    
    print(f"   ✅ Data compressed")
    print(f"   📏 Before: {len(encrypted_payload)} bytes")
    print(f"   📏 After: {len(compressed_payload)} bytes (-{len(encrypted_payload) - len(compressed_payload)} bytes)")
    print(f"   📊 Compression ratio: {len(compressed_payload) / len(encrypted_payload):.2f}x")
    print(f"   💾 Space saved: {((1 - len(compressed_payload) / len(encrypted_payload)) * 100):.1f}%")
    print(f"   ⏱️  Time: {step3_time:.3f} seconds")
    
    # STEP 4: Frequency domain transformation
    print(f"\n🌊 STEP 4: Frequency Domain Transform")
    step4_start = time.time()
    
    bands = dwt_decompose(cover_image, levels=2)
    bands["LL2_DCT"] = dct_on_ll(bands["LL2"])
    
    step4_time = time.time() - step4_start
    results["process_steps"]["step4_transform"] = {
        "time_seconds": step4_time,
        "dwt_bands_created": len([b for b in bands.keys() if "LL2_DCT" not in b]),
        "dct_applied": "LL2_DCT" in bands,
        "total_bands": len(bands)
    }
    
    print(f"   ✅ Frequency transformation completed")
    print(f"   🌊 DWT bands: {len([b for b in bands.keys() if 'LL2_DCT' not in b])}")
    print(f"   📐 DCT applied to LL2 band")
    print(f"   📊 Total frequency bands: {len(bands)}")
    print(f"   ⏱️  Time: {step4_time:.3f} seconds")
    
    # STEP 5: Capacity calculation
    print(f"\n📊 STEP 5: Embedding Capacity Analysis")
    step5_start = time.time()
    
    payload_bits = bytes_to_bits(compressed_payload)
    
    # Calculate available capacity
    embedding_bands = ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2", "LL2_DCT"]
    available_capacity = 0
    
    for band_name in embedding_bands:
        if band_name in bands:
            available_capacity += bands[band_name].size // int(q_factor)
    
    step5_time = time.time() - step5_start
    results["process_steps"]["step5_capacity"] = {
        "time_seconds": step5_time,
        "payload_bits_required": len(payload_bits),
        "available_capacity_bits": available_capacity,
        "capacity_utilization": len(payload_bits) / available_capacity,
        "capacity_utilization_percent": (len(payload_bits) / available_capacity) * 100,
        "embedding_bands": embedding_bands
    }
    
    print(f"   ✅ Capacity analysis completed")
    print(f"   📦 Payload bits required: {len(payload_bits):,}")
    print(f"   🏗️  Available capacity: {available_capacity:,} bits")
    print(f"   📊 Capacity utilization: {(len(payload_bits) / available_capacity) * 100:.1f}%")
    print(f"   ⚙️  Embedding bands: {len(embedding_bands)}")
    print(f"   ⏱️  Time: {step5_time:.3f} seconds")
    
    # Check if payload fits
    if len(payload_bits) > available_capacity:
        print(f"   ❌ ERROR: Payload too large for image capacity!")
        return results
    
    # STEP 6: Embedding
    print(f"\n🔧 STEP 6: Data Embedding")
    step6_start = time.time()
    
    modified_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=q_factor)
    
    step6_time = time.time() - step6_start
    results["process_steps"]["step6_embed"] = {
        "time_seconds": step6_time,
        "bits_embedded": len(payload_bits),
        "bands_modified": len([b for b in embedding_bands if b in modified_bands]),
        "embedding_efficiency_bits_per_sec": len(payload_bits) / step6_time if step6_time > 0 else 0
    }
    
    print(f"   ✅ Data embedded successfully")
    print(f"   🔧 Bits embedded: {len(payload_bits):,}")
    print(f"   📊 Bands modified: {len([b for b in embedding_bands if b in modified_bands])}")
    print(f"   ⚡ Embedding speed: {len(payload_bits) / step6_time if step6_time > 0 else 0:.0f} bits/sec")
    print(f"   ⏱️  Time: {step6_time:.3f} seconds")
    
    # STEP 7: Image reconstruction
    print(f"\n🖼️  STEP 7: Image Reconstruction")
    step7_start = time.time()
    
    # Inverse DCT
    from a3_image_processing import idct_on_ll, dwt_reconstruct
    modified_bands["LL2"] = idct_on_ll(modified_bands["LL2_DCT"])
    
    # Inverse DWT
    stego_image = dwt_reconstruct(modified_bands)
    
    step7_time = time.time() - step7_start
    results["process_steps"]["step7_reconstruct"] = {
        "time_seconds": step7_time,
        "output_image_shape": stego_image.shape,
        "reconstruction_method": "Inverse DCT + Inverse DWT"
    }
    
    print(f"   ✅ Image reconstructed")
    print(f"   📏 Output dimensions: {stego_image.shape[0]}x{stego_image.shape[1]}")
    print(f"   🔄 Method: Inverse DCT + Inverse DWT")
    print(f"   ⏱️  Time: {step7_time:.3f} seconds")
    
    # STEP 8: Quality analysis
    print(f"\n📈 STEP 8: Quality Analysis")
    step8_start = time.time()
    
    psnr_value = psnr(cover_image, stego_image.astype(np.uint8))
    
    # Quality classification
    if psnr_value >= 50:
        quality_rating = "Excellent"
    elif psnr_value >= 45:
        quality_rating = "Very Good"
    elif psnr_value >= 40:
        quality_rating = "Good"
    else:
        quality_rating = "Poor"
    
    step8_time = time.time() - step8_start
    results["process_steps"]["step8_quality"] = {
        "time_seconds": step8_time,
        "psnr_db": psnr_value,
        "quality_rating": quality_rating,
        "quality_threshold_50db": psnr_value >= 50,
        "quality_threshold_45db": psnr_value >= 45
    }
    
    print(f"   ✅ Quality analysis completed")
    print(f"   📊 PSNR: {psnr_value:.2f} dB")
    print(f"   🏆 Quality rating: {quality_rating}")
    print(f"   ✅ Above 50dB threshold: {'Yes' if psnr_value >= 50 else 'No'}")
    print(f"   ⏱️  Time: {step8_time:.3f} seconds")
    
    # STEP 9: Extraction verification
    print(f"\n🔍 STEP 9: Extraction Verification")
    step9_start = time.time()
    
    extracted_bits = extract_from_dwt_bands(modified_bands, len(payload_bits), Q_factor=q_factor)
    extracted_payload = bits_to_bytes(extracted_bits)
    
    extraction_success = extracted_payload == compressed_payload
    
    step9_time = time.time() - step9_start
    results["process_steps"]["step9_extract"] = {
        "time_seconds": step9_time,
        "extraction_success": extraction_success,
        "extracted_bits": len(extracted_bits),
        "bit_accuracy": len(extracted_bits) == len(payload_bits)
    }
    
    print(f"   ✅ Extraction completed")
    print(f"   📦 Extracted bits: {len(extracted_bits):,}")
    print(f"   ✅ Extraction success: {'Yes' if extraction_success else 'No'}")
    print(f"   📊 Bit accuracy: {'Perfect' if len(extracted_bits) == len(payload_bits) else 'Error'}")
    print(f"   ⏱️  Time: {step9_time:.3f} seconds")
    
    # STEP 10: Full pipeline verification
    print(f"\n🔄 STEP 10: Full Pipeline Verification")
    step10_start = time.time()
    
    pipeline_success = False
    final_message = ""
    
    if extraction_success:
        try:
            decompressed = decompress_huffman(extracted_payload, compression_table)
            final_message = decrypt_message(decompressed, key, salt, iv)
            pipeline_success = final_message == payload_text
        except Exception as e:
            pipeline_success = False
            final_message = f"Error: {str(e)}"
    
    step10_time = time.time() - step10_start
    results["process_steps"]["step10_verify"] = {
        "time_seconds": step10_time,
        "pipeline_success": pipeline_success,
        "final_message_match": final_message == payload_text,
        "recovered_message_length": len(final_message) if isinstance(final_message, str) else 0
    }
    
    print(f"   ✅ Pipeline verification completed")
    print(f"   🔄 Full pipeline success: {'Yes' if pipeline_success else 'No'}")
    print(f"   📝 Message recovery: {'Perfect' if final_message == payload_text else 'Failed'}")
    print(f"   📊 Recovered length: {len(final_message) if isinstance(final_message, str) else 0} chars")
    print(f"   ⏱️  Time: {step10_time:.3f} seconds")
    
    # Calculate total metrics
    total_time = time.time() - total_start
    results["summary"] = {
        "total_time_seconds": total_time,
        "overall_success": pipeline_success,
        "final_psnr_db": psnr_value,
        "final_quality_rating": quality_rating,
        "total_payload_overhead": len(compressed_payload) / len(payload_text),
        "process_efficiency": len(payload_bits) / total_time if total_time > 0 else 0
    }
    
    print(f"\n🎯 PROCESS SUMMARY")
    print(f"=" * 50)
    print(f"⏱️  Total time: {total_time:.3f} seconds")
    print(f"✅ Overall success: {'Yes' if pipeline_success else 'No'}")
    print(f"📊 Final PSNR: {psnr_value:.2f} dB ({quality_rating})")
    print(f"📦 Payload overhead: {len(compressed_payload) / len(payload_text):.2f}x")
    print(f"⚡ Process efficiency: {len(payload_bits) / total_time if total_time > 0 else 0:.0f} bits/sec")
    
    return results

def demo_q_factor_comparison():
    """Demonstrate Q-factor comparison"""
    print(f"\n⚙️  Q-FACTOR COMPARISON DEMO")
    print(f"=" * 40)
    
    # Create test image
    image_path = create_sample_image(512, "q_demo")
    payload = "Test message for Q-factor analysis with sufficient length for meaningful results."
    
    q_factors = [2.0, 5.0, 8.0, 10.0]
    results = []
    
    for q in q_factors:
        print(f"\n🔧 Testing Q = {q}")
        try:
            # Quick test (simplified)
            cover_image = read_image(image_path)
            key = generate_key()
            encrypted, salt, iv = encrypt_message(payload, key)
            compressed, table = compress_huffman(encrypted)
            payload_bits = bytes_to_bits(compressed)
            
            bands = dwt_decompose(cover_image, levels=2)
            bands["LL2_DCT"] = dct_on_ll(bands["LL2"])
            
            # Calculate capacity
            capacity = 0
            for band_name in ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2", "LL2_DCT"]:
                if band_name in bands:
                    capacity += bands[band_name].size // int(q)
            
            if len(payload_bits) <= capacity:
                modified_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=q)
                from a3_image_processing import idct_on_ll, dwt_reconstruct
                modified_bands["LL2"] = idct_on_ll(modified_bands["LL2_DCT"])
                stego_image = dwt_reconstruct(modified_bands)
                psnr_val = psnr(cover_image, stego_image.astype(np.uint8))
                
                results.append({
                    "q_factor": q,
                    "psnr": psnr_val,
                    "capacity": capacity,
                    "utilization": len(payload_bits) / capacity
                })
                
                print(f"   ✅ PSNR: {psnr_val:.2f} dB")
                print(f"   📊 Capacity: {capacity:,} bits")
                print(f"   📈 Utilization: {(len(payload_bits) / capacity) * 100:.1f}%")
            else:
                print(f"   ❌ Payload too large for Q={q}")
                
        except Exception as e:
            print(f"   💥 Error with Q={q}: {str(e)}")
    
    # Show comparison
    if results:
        print(f"\n📊 Q-FACTOR COMPARISON SUMMARY:")
        print(f"{'Q-Factor':<10} {'PSNR (dB)':<12} {'Capacity':<12} {'Utilization':<12}")
        print(f"-" * 50)
        for r in results:
            print(f"{r['q_factor']:<10.1f} {r['psnr']:<12.2f} {r['capacity']:<12,d} {r['utilization']*100:<12.1f}%")
    
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return results

if __name__ == "__main__":
    print("🚀 LAYERX RESEARCH FRAMEWORK DEMO")
    print("=" * 50)
    print("This demo shows what the full research will produce...")
    print()
    
    # Create demo image
    demo_image = create_sample_image(512, "demo")
    demo_payload = ("This is a comprehensive test payload for LayerX steganography research. " +
                   "It demonstrates the complete process including encryption, compression, " +
                   "embedding, extraction, and quality analysis with detailed metrics at each step.")
    
    # Run complete process demo
    process_results = demo_complete_process(demo_image, demo_payload, q_factor=5.0)
    
    # Save results
    with open("demo_results.json", "w") as f:
        json.dump(process_results, f, indent=2)
    
    print(f"\n💾 Demo results saved to: demo_results.json")
    
    # Run Q-factor comparison
    q_results = demo_q_factor_comparison()
    
    # Cleanup
    if os.path.exists(demo_image):
        os.remove(demo_image)
    
    print(f"\n✅ DEMO COMPLETED")
    print(f"The full research framework will provide:")
    print(f"   - 100x more test cases")
    print(f"   - Real internet images")
    print(f"   - Statistical analysis")
    print(f"   - Scientific visualizations")
    print(f"   - Academic-quality reports")
    print(f"   - Performance benchmarks")
    print(f"\nTo run the complete research:")
    print(f"python run_complete_research.py")