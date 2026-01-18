"""
Download test images from internet and test color steganography
"""
import urllib.request
import cv2
import numpy as np
import sys
sys.path.append('core_modules')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed_in_dwt_bands_color, extract_from_dwt_bands_color, bytes_to_bits, bits_to_bytes
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color, save_image_color

print("="*70)
print("DOWNLOADING TEST IMAGES FROM INTERNET")
print("="*70)

# Sample images URLs (free stock photos)
test_images = [
    {
        'name': 'nature',
        'url': 'https://picsum.photos/800/600',
        'message': 'Hidden in nature scene'
    },
    {
        'name': 'abstract',
        'url': 'https://picsum.photos/1024/768',
        'message': 'Abstract art contains secret data'
    },
    {
        'name': 'portrait',
        'url': 'https://picsum.photos/600/800',
        'message': 'Portrait photo with embedded message using LayerX'
    }
]

results = []

for idx, img_info in enumerate(test_images, 1):
    print(f"\n{'='*70}")
    print(f"TEST {idx}/3: {img_info['name'].upper()}")
    print(f"{'='*70}")
    
    try:
        # Download image
        print(f"[1] Downloading from {img_info['url']}...")
        filename = f"downloaded_{img_info['name']}.jpg"
        urllib.request.urlretrieve(img_info['url'], filename)
        print(f"    [+] Saved: {filename}")
        
        # Load as color
        print(f"[2] Loading image...")
        img = read_image_color(filename)
        print(f"    [+] Shape: {img.shape}")
        
        # Prepare message
        message = img_info['message']
        print(f"[3] Message: '{message}' ({len(message)} chars)")
        
        # Encrypt & compress
        ciphertext, salt, iv = encrypt_message(message, "internet_test_key")
        compressed, tree = compress_huffman(ciphertext)
        payload = create_payload(ciphertext, tree, compressed)
        payload_bits = bytes_to_bits(payload)
        print(f"    [+] Payload: {len(payload)} bytes ({len(payload_bits)} bits)")
        
        # DWT decompose
        print(f"[4] DWT decomposition...")
        bands = dwt_decompose_color(img, levels=2)
        
        # Embed
        print(f"[5] Embedding...")
        modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=5.0)
        stego_img = dwt_reconstruct_color(modified_bands)
        
        # Adjust dimensions if needed
        if stego_img.shape != img.shape:
            stego_img = stego_img[:img.shape[0], :img.shape[1], :]
        
        # Calculate PSNR
        psnr_val = psnr_color(img, stego_img)
        print(f"    [+] PSNR: {psnr_val:.2f} dB")
        
        # Save stego
        stego_filename = f"stego_{img_info['name']}.png"
        save_image_color(stego_filename, stego_img)
        
        # Extract & decrypt
        print(f"[6] Extracting...")
        stego_bands = dwt_decompose_color(stego_img, levels=2)
        extracted_bits = extract_from_dwt_bands_color(stego_bands, len(payload_bits), Q_factor=5.0)
        extracted_payload = bits_to_bytes(extracted_bits)
        
        msg_len, tree_extracted, compressed_extracted = parse_payload(extracted_payload)
        decrypted_ciphertext = decompress_huffman(compressed_extracted, tree_extracted)
        decrypted_message = decrypt_message(decrypted_ciphertext, "internet_test_key", salt, iv)
        
        # Verify
        success = (message == decrypted_message)
        print(f"    [+] Extraction: {'SUCCESS' if success else 'FAILED'}")
        
        # Create comparison
        comparison = np.zeros((img.shape[0], img.shape[1]*2, 3), dtype=np.uint8)
        comparison[:, 0:img.shape[1]] = img
        comparison[:, img.shape[1]:] = stego_img
        
        cv2.putText(comparison, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(comparison, f"Stego ({psnr_val:.1f}dB)", (img.shape[1]+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        comp_filename = f"comparison_{img_info['name']}.png"
        cv2.imwrite(comp_filename, comparison)
        print(f"    [+] Comparison saved: {comp_filename}")
        
        results.append({
            'name': img_info['name'],
            'shape': img.shape,
            'psnr': psnr_val,
            'payload_bytes': len(payload),
            'success': success
        })
        
        print(f"    [SUCCESS] Test passed!")
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        results.append({
            'name': img_info['name'],
            'success': False,
            'error': str(e)
        })

# Summary
print("\n" + "="*70)
print("SUMMARY - INTERNET IMAGES TEST")
print("="*70)

for r in results:
    if r['success']:
        print(f"[OK] {r['name']:12s} | {str(r['shape']):20s} | PSNR: {r['psnr']:.2f} dB | {r['payload_bytes']} bytes")
    else:
        print(f"[FAIL] {r['name']:12s} | Error: {r.get('error', 'Unknown')}")

passed = sum(1 for r in results if r['success'])
print(f"\n{'='*70}")
print(f"RESULT: {passed}/{len(results)} tests passed")
print(f"{'='*70}")
