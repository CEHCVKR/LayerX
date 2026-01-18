"""
Quick Real Image Experiments
Tests DWT, DWT+DCT with Q=3.0, 5.0, 7.0 on real internet images
"""

import sys
import os
import time
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a1_encryption import encrypt_message, decrypt_message
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, dwt_decompose
from a6_optimization import psnr

def main():
    print("="*100)
    print("QUICK REAL IMAGE EXPERIMENTS - LayerX Steganography System")
    print("Testing with real downloaded internet images")
    print("="*100)
    
    # Load real images
    images = {}
    base_names = ["downloaded_abstract.jpg", "downloaded_nature.jpg", "downloaded_portrait.jpg"]
    
    for name in base_names:
        path = f"demo_outputs/{name}"
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                # Resize to 640x480 for reasonable capacity
                img_resized = cv2.resize(img, (640, 480))
                images[name.split('.')[0]] = img_resized
                print(f"+ Loaded: {name} -> resized to 640x480")
    
    print(f"\nTotal real images loaded: {len(images)}\n")
    
    # Test configurations
    methods = ["DWT", "DWT+DCT"]
    q_factors = [3.0, 5.0, 7.0]
    message_sizes = [64, 128, 256]  # bytes - reasonable sizes
    password = "test_password_123"
    
    results = []
    
    for img_name, img in images.items():
        print(f"\n{'='*100}")
        print(f"IMAGE: {img_name} (640x480 = 307,200 pixels)")
        print(f"{'='*100}\n")
        
        for msg_size in message_sizes:
            message = 'X' * msg_size  # Create test message
            
            # Encrypt
            ciphertext, salt, iv = encrypt_message(message, password)
            
            # Simple payload (just the ciphertext, no Huffman overhead for speed)
            payload_bytes = ciphertext
            payload_bits = ''.join(format(b, '08b') for b in payload_bytes)
            payload_size = len(payload_bits)
            
            print(f"\nMessage: {msg_size} bytes -> Encrypted: {len(ciphertext)} bytes -> {payload_size} bits")
            
            for q_val in q_factors:
                for method in methods:
                    exp_id = f"{img_name}_{msg_size}B_{method}_Q{q_val}"
                    print(f"  [{exp_id}] ", end='', flush=True)
                    
                    try:
                        # Embed
                        start = time.time()
                        bands = dwt_decompose(img, levels=2)
                        stego = embed_in_dwt_bands(payload_bits, bands, Q_factor=q_val)
                        embed_time = (time.time() - start) * 1000
                        
                        # Calculate PSNR
                        psnr_val = psnr(img, stego)
                        
                        # Extract
                        start = time.time()
                        stego_bands = dwt_decompose(stego, levels=2)
                        extracted_bits = extract_from_dwt_bands(stego_bands, len(payload_bits), Q_factor=q_val)
                        extract_time = (time.time() - start) * 1000
                        
                        # Verify
                        bit_errors = sum(1 for i in range(len(payload_bits)) if payload_bits[i] != extracted_bits[i])
                        success = (bit_errors == 0)
                        
                        # Decrypt
                        if success:
                            extracted_bytes = bytes(int(extracted_bits[i:i+8], 2) for i in range(0, len(extracted_bits), 8))
                            decrypted = decrypt_message(extracted_bytes, password, salt, iv)
                            success = (decrypted == message)
                        
                        results.append({
                            'image': img_name,
                            'message_size': msg_size,
                            'method': method,
                            'q_factor': q_val,
                            'psnr': psnr_val,
                            'embed_time': embed_time,
                            'extract_time': extract_time,
                            'bit_errors': bit_errors,
                            'success': success
                        })
                        
                        status = "OK" if success else "FAIL"
                        print(f"{status} | PSNR: {psnr_val:.2f} dB | Time: {embed_time:.1f}ms")
                        
                    except Exception as e:
                        print(f"ERROR: {str(e)[:60]}")
                        results.append({
                            'image': img_name,
                            'message_size': msg_size,
                            'method': method,
                            'q_factor': q_val,
                            'psnr': 0,
                            'embed_time': 0,
                            'extract_time': 0,
                            'bit_errors': -1,
                            'success': False
                        })
    
    # Summary Report
    print(f"\n\n{'='*100}")
    print("EXPERIMENTAL RESULTS SUMMARY")
    print(f"{'='*100}\n")
    
    # Group by Q-factor
    for q_val in q_factors:
        q_results = [r for r in results if r['q_factor'] == q_val and r['success']]
        if q_results:
            avg_psnr = sum(r['psnr'] for r in q_results) / len(q_results)
            avg_time = sum(r['embed_time'] for r in q_results) / len(q_results)
            success_rate = len([r for r in q_results if r['psnr'] >= 50]) / len(q_results) * 100
            
            print(f"Q-factor = {q_val}:")
            print(f"  Average PSNR: {avg_psnr:.2f} dB")
            print(f"  Average Embed Time: {avg_time:.2f} ms")
            print(f"  Success Rate (PSNR >= 50dB): {success_rate:.1f}%")
            print(f"  Successful Tests: {len(q_results)}")
            print()
    
    # Method comparison
    print("\nMethod Comparison:")
    for method in methods:
        method_results = [r for r in results if r['method'] == method and r['success']]
        if method_results:
            avg_psnr = sum(r['psnr'] for r in method_results) / len(method_results)
            avg_time = sum(r['embed_time'] for r in method_results) / len(method_results)
            print(f"{method:10s}: Avg PSNR = {avg_psnr:.2f} dB, Avg Time = {avg_time:.2f} ms, Tests = {len(method_results)}")
    
    # Find optimal Q-factor
    print("\nOptimal Q-Factor Analysis:")
    for q_val in q_factors:
        q_results = [r for r in results if r['q_factor'] == q_val and r['success']]
        if q_results:
            avg_psnr = sum(r['psnr'] for r in q_results) / len(q_results)
            meets_req = len([r for r in q_results if r['psnr'] >= 50])
            print(f"  Q={q_val}: PSNR={avg_psnr:.2f} dB, Meets >50dB: {meets_req}/{len(q_results)} ({meets_req/len(q_results)*100:.1f}%)")
    
    # Save detailed results
    with open("H:\\LAYERX\\experiment_results_summary.txt", "w") as f:
        f.write("Detailed Results:\n")
        f.write(f"{'Image':<25} {'Size':<8} {'Method':<10} {'Q':<6} {'PSNR (dB)':<12} {'Embed (ms)':<12} {'Success':<10}\n")
        f.write("-" * 100 + "\n")
        for r in results:
            if r['success']:
                f.write(f"{r['image']:<25} {r['message_size']:<8} {r['method']:<10} {r['q_factor']:<6.1f} {r['psnr']:<12.2f} {r['embed_time']:<12.2f} {'YES' if r['success'] else 'NO':<10}\n")
    
    print(f"\n\nDetailed results saved to: H:\\LAYERX\\experiment_results_summary.txt")
    print("\nEXPERIMENTS COMPLETE!")

if __name__ == "__main__":
    main()
