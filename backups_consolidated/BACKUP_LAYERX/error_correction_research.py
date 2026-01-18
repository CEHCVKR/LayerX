#!/usr/bin/env python3
"""
LayerX Error Correction Research
===============================
CRITICAL PRIORITY: Implement error correction to improve robustness from 15.6%

Test error correction codes (Hamming, Reed-Solomon, BCH) for robustness against:
- JPEG compression
- Noise addition
- Image modifications

Goal: Achieve ≥80% robustness through error correction
"""

import os
import sys
import json
import time
import datetime
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from a5_embedding_extraction import embed, extract
from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_data, decompress_data
from a6_optimization import OptimizeEmbedding

def handle_encryption_decryption(data, key, operation):
    """Simple encryption/decryption wrapper"""
    try:
        if operation == "encrypt":
            if isinstance(data, bytes):
                data = data.decode('latin-1')  # Convert bytes to string for encryption
            encrypted, salt, iv = encrypt_message(data, key)
            return salt + iv + encrypted  # Concatenate for storage
        elif operation == "decrypt":
            if len(data) < 32:  # Need at least salt + iv
                return None
            salt = data[:16]
            iv = data[16:32]
            ciphertext = data[32:]
            decrypted = decrypt_message(ciphertext, key, salt, iv)
            return decrypted.encode('latin-1')  # Convert back to bytes
    except Exception as e:
        print(f"Encryption/decryption error: {e}")
        return None

@dataclass
class ErrorCorrectionResult:
    method: str
    original_size: int
    encoded_size: int
    redundancy_ratio: float
    success_rate: float
    avg_psnr: float
    test_count: int
    modification_resistance: Dict[str, float]

class ErrorCorrectionResearch:
    def __init__(self):
        self.results_dir = f"error_correction_research_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(f"{self.results_dir}/results", exist_ok=True)
        os.makedirs(f"{self.results_dir}/plots", exist_ok=True)
        os.makedirs(f"{self.results_dir}/test_images", exist_ok=True)
        
        self.optimize = OptimizeEmbedding()
        
        # Test parameters
        self.test_payloads = [512, 1024, 2048]  # bytes
        self.image_size = (512, 512)
        
        # Error correction methods to test
        self.error_correction_methods = {
            'none': self.no_error_correction,
            'repetition': self.repetition_code,
            'hamming': self.hamming_code,
            'reed_solomon': self.reed_solomon_code,
            'checksum': self.checksum_code
        }
        
        # Modification tests
        self.modification_tests = {
            'jpeg_50': lambda img: self.apply_jpeg_compression(img, 50),
            'jpeg_70': lambda img: self.apply_jpeg_compression(img, 70),
            'gaussian_noise_01': lambda img: self.apply_gaussian_noise(img, 0.01),
            'gaussian_noise_05': lambda img: self.apply_gaussian_noise(img, 0.05),
            'salt_pepper_01': lambda img: self.apply_salt_pepper_noise(img, 0.01),
            'rotation_1deg': lambda img: self.apply_rotation(img, 1),
            'brightness_minus15': lambda img: self.apply_brightness(img, -15),
            'brightness_plus15': lambda img: self.apply_brightness(img, 15)
        }
        
        print("🔧 LayerX Error Correction Research")
        print("=" * 40)
        print("CRITICAL PRIORITY: Implement error correction to improve robustness")
        print(f"📂 Output directory: {self.results_dir}")
        print("🎯 Goal: Achieve ≥80% robustness through error correction\n")
    
    def create_test_images(self):
        """Create test images with different characteristics"""
        print("📷 Creating Error Correction Test Images...")
        
        # Natural image pattern
        natural_img = np.zeros(self.image_size, dtype=np.uint8)
        for i in range(self.image_size[0]):
            for j in range(self.image_size[1]):
                natural_img[i, j] = int(128 + 50 * np.sin(i/10) * np.cos(j/15) + 30 * np.random.randn())
        
        natural_img = np.clip(natural_img, 0, 255)
        cv2.imwrite(f"{self.results_dir}/test_images/natural.png", natural_img)
        
        # Textured image
        textured_img = np.random.randint(0, 256, self.image_size, dtype=np.uint8)
        for i in range(0, self.image_size[0], 8):
            for j in range(0, self.image_size[1], 8):
                textured_img[i:i+4, j:j+4] = np.random.randint(0, 128)
                textured_img[i+4:i+8, j+4:j+8] = np.random.randint(128, 256)
        
        cv2.imwrite(f"{self.results_dir}/test_images/textured.png", textured_img)
        
        print("✅ Created test images: natural, textured")
        return ['natural', 'textured']
    
    # Error Correction Methods
    def no_error_correction(self, data: bytes) -> Tuple[bytes, Dict]:
        """No error correction - baseline"""
        return data, {'redundancy': 1.0, 'method': 'none'}
    
    def repetition_code(self, data: bytes) -> Tuple[bytes, Dict]:
        """Simple repetition code - repeat each bit 3 times"""
        result = bytearray()
        for byte in data:
            # Repeat each bit 3 times
            for bit_pos in range(8):
                bit = (byte >> bit_pos) & 1
                # Store 3 copies of the bit
                result.extend([bit] * 3)
        
        # Pack bits back to bytes
        encoded = bytearray()
        for i in range(0, len(result), 8):
            byte_val = 0
            for j in range(min(8, len(result) - i)):
                if result[i + j]:
                    byte_val |= (1 << j)
            encoded.append(byte_val)
        
        return bytes(encoded), {'redundancy': len(encoded) / len(data), 'method': 'repetition_3'}
    
    def hamming_code(self, data: bytes) -> Tuple[bytes, Dict]:
        """Hamming (7,4) error correction code"""
        result = bytearray()
        
        for byte in data:
            # Split byte into two 4-bit nibbles
            high_nibble = (byte >> 4) & 0x0F
            low_nibble = byte & 0x0F
            
            # Encode each nibble with Hamming (7,4)
            high_encoded = self.encode_hamming_7_4(high_nibble)
            low_encoded = self.encode_hamming_7_4(low_nibble)
            
            # Store as two bytes (7 bits each, use 8 bits)
            result.append(high_encoded)
            result.append(low_encoded)
        
        return bytes(result), {'redundancy': len(result) / len(data), 'method': 'hamming_7_4'}
    
    def encode_hamming_7_4(self, nibble: int) -> int:
        """Encode 4 data bits to 7-bit Hamming code"""
        d1, d2, d3, d4 = [(nibble >> i) & 1 for i in range(4)]
        
        # Parity bits
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4
        
        # 7-bit codeword: p1 p2 d1 p3 d2 d3 d4
        return p1 | (p2 << 1) | (d1 << 2) | (p3 << 3) | (d2 << 4) | (d3 << 5) | (d4 << 6)
    
    def decode_hamming_7_4(self, codeword: int) -> int:
        """Decode 7-bit Hamming code to 4 data bits with error correction"""
        bits = [(codeword >> i) & 1 for i in range(7)]
        p1, p2, d1, p3, d2, d3, d4 = bits
        
        # Calculate syndrome
        s1 = p1 ^ d1 ^ d2 ^ d4
        s2 = p2 ^ d1 ^ d3 ^ d4
        s3 = p3 ^ d2 ^ d3 ^ d4
        
        syndrome = s1 | (s2 << 1) | (s3 << 2)
        
        # Correct single bit error if detected
        if syndrome != 0:
            error_pos = syndrome - 1
            if 0 <= error_pos < 7:
                bits[error_pos] ^= 1
                p1, p2, d1, p3, d2, d3, d4 = bits
        
        return d1 | (d2 << 1) | (d3 << 2) | (d4 << 3)
    
    def reed_solomon_code(self, data: bytes) -> Tuple[bytes, Dict]:
        """Simplified Reed-Solomon-like code using polynomial math"""
        try:
            # Simple implementation: add parity bytes
            parity_count = min(16, len(data) // 4)  # 25% redundancy
            result = bytearray(data)
            
            # Generate parity bytes using XOR combinations
            for i in range(parity_count):
                parity = 0
                for j in range(0, len(data), parity_count):
                    if j + i < len(data):
                        parity ^= data[j + i]
                result.append(parity)
            
            return bytes(result), {'redundancy': len(result) / len(data), 'method': 'reed_solomon_simple'}
        except Exception as e:
            print(f"Reed-Solomon encoding failed: {e}")
            return data, {'redundancy': 1.0, 'method': 'reed_solomon_failed'}
    
    def checksum_code(self, data: bytes) -> Tuple[bytes, Dict]:
        """Simple checksum error detection"""
        result = bytearray(data)
        
        # Add CRC32-like checksum
        checksum = 0
        for byte in data:
            checksum ^= byte
            for _ in range(8):
                if checksum & 0x80:
                    checksum = (checksum << 1) ^ 0x1D
                else:
                    checksum <<= 1
                checksum &= 0xFF
        
        # Add block checksums
        block_size = 16
        for i in range(0, len(data), block_size):
            block = data[i:i+block_size]
            block_checksum = sum(block) & 0xFF
            result.append(block_checksum)
        
        result.append(checksum)  # Overall checksum
        
        return bytes(result), {'redundancy': len(result) / len(data), 'method': 'checksum'}
    
    # Image modification methods
    def apply_jpeg_compression(self, img: np.ndarray, quality: int) -> np.ndarray:
        """Apply JPEG compression"""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encoded_img = cv2.imencode('.jpg', img, encode_param)
        return cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
    
    def apply_gaussian_noise(self, img: np.ndarray, sigma: float) -> np.ndarray:
        """Add Gaussian noise"""
        noise = np.random.normal(0, sigma * 255, img.shape)
        noisy = img.astype(np.float32) + noise
        return np.clip(noisy, 0, 255).astype(np.uint8)
    
    def apply_salt_pepper_noise(self, img: np.ndarray, density: float) -> np.ndarray:
        """Add salt and pepper noise"""
        noisy = img.copy()
        num_salt = np.ceil(density * img.size * 0.5).astype(int)
        num_pepper = np.ceil(density * img.size * 0.5).astype(int)
        
        # Salt noise
        coords = [np.random.randint(0, i - 1, num_salt) for i in img.shape]
        noisy[tuple(coords)] = 255
        
        # Pepper noise
        coords = [np.random.randint(0, i - 1, num_pepper) for i in img.shape]
        noisy[tuple(coords)] = 0
        
        return noisy
    
    def apply_rotation(self, img: np.ndarray, angle: float) -> np.ndarray:
        """Apply rotation"""
        center = (img.shape[1] // 2, img.shape[0] // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
    
    def apply_brightness(self, img: np.ndarray, delta: int) -> np.ndarray:
        """Apply brightness adjustment"""
        result = img.astype(np.int16) + delta
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def test_error_correction_method(self, method_name: str, image_name: str, payload_size: int) -> ErrorCorrectionResult:
        """Test specific error correction method"""
        print(f"   🧪 Testing {method_name} error correction...")
        
        # Load test image
        img_path = f"{self.results_dir}/test_images/{image_name}.png"
        test_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        # Generate test payload
        original_payload = os.urandom(payload_size)
        
        # Apply error correction
        encoded_payload, ec_info = self.error_correction_methods[method_name](original_payload)
        
        # Encrypt and compress
        encrypted_payload = handle_encryption_decryption(encoded_payload, "test_key_123", "encrypt")
        compressed_payload = compress_data(encrypted_payload)
        
        # Embed into image
        try:
            stego_path = f"{self.results_dir}/temp_stego.png"
            success = embed(compressed_payload, img_path, stego_path)
            if not success:
                print(f"      ❌ Embedding failed for {method_name}")
                return ErrorCorrectionResult(
                    method=method_name,
                    original_size=len(original_payload),
                    encoded_size=len(encoded_payload),
                    redundancy_ratio=ec_info['redundancy'],
                    success_rate=0.0,
                    avg_psnr=0.0,
                    test_count=0,
                    modification_resistance={}
                )
            
            # Load stego image
            stego_img = cv2.imread(stego_path, cv2.IMREAD_GRAYSCALE)
        except Exception as e:
            print(f"      ❌ Embedding error for {method_name}: {e}")
            return ErrorCorrectionResult(
                method=method_name,
                original_size=len(original_payload),
                encoded_size=len(encoded_payload),
                redundancy_ratio=ec_info['redundancy'],
                success_rate=0.0,
                avg_psnr=0.0,
                test_count=0,
                modification_resistance={}
            )
        
        # Test robustness against modifications
        successful_tests = 0
        total_tests = 0
        psnr_values = []
        modification_results = {}
        
        for mod_name, mod_func in self.modification_tests.items():
            total_tests += 1
            try:
                # Apply modification
                modified_img = mod_func(stego_img.copy())
                modified_path = f"{self.results_dir}/temp_modified.png"
                cv2.imwrite(modified_path, modified_img)
                
                # Calculate PSNR
                psnr = cv2.PSNR(stego_img, modified_img)
                psnr_values.append(psnr)
                
                # Extract data
                extracted_compressed = extract(modified_path)
                if extracted_compressed is None:
                    modification_results[mod_name] = 0.0
                    continue
                
                # Decrypt and decompress
                extracted_encrypted = decompress_data(extracted_compressed)
                if extracted_encrypted is None:
                    modification_results[mod_name] = 0.0
                    continue
                
                extracted_encoded = handle_encryption_decryption(extracted_encrypted, "test_key_123", "decrypt")
                if extracted_encoded is None:
                    modification_results[mod_name] = 0.0
                    continue
                
                # Decode error correction
                if method_name == 'hamming':
                    decoded_payload = self.decode_hamming_payload(extracted_encoded)
                else:
                    decoded_payload = extracted_encoded[:len(original_payload)]  # Simple truncation
                
                # Check match
                if decoded_payload == original_payload:
                    successful_tests += 1
                    modification_results[mod_name] = 1.0
                else:
                    modification_results[mod_name] = 0.0
                    
            except Exception as e:
                modification_results[mod_name] = 0.0
                print(f"         Error in {mod_name}: {e}")
        
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0
        avg_psnr = np.mean(psnr_values) if psnr_values else 0.0
        
        print(f"      ✅ Success rate: {success_rate:.1%} ({successful_tests}/{total_tests})")
        
        return ErrorCorrectionResult(
            method=method_name,
            original_size=len(original_payload),
            encoded_size=len(encoded_payload),
            redundancy_ratio=ec_info['redundancy'],
            success_rate=success_rate,
            avg_psnr=avg_psnr,
            test_count=total_tests,
            modification_resistance=modification_results
        )
    
    def decode_hamming_payload(self, encoded_data: bytes) -> bytes:
        """Decode Hamming-encoded payload"""
        result = bytearray()
        
        for i in range(0, len(encoded_data), 2):
            if i + 1 < len(encoded_data):
                high_decoded = self.decode_hamming_7_4(encoded_data[i])
                low_decoded = self.decode_hamming_7_4(encoded_data[i + 1])
                
                original_byte = (high_decoded << 4) | low_decoded
                result.append(original_byte)
        
        return bytes(result)
    
    def run_comprehensive_error_correction_research(self):
        """Run comprehensive error correction research"""
        print("🚀 COMPREHENSIVE ERROR CORRECTION RESEARCH")
        print("=" * 50)
        
        # Create test images
        test_images = self.create_test_images()
        
        all_results = []
        
        print(f"\n📋 Error Correction Test Configuration:")
        print(f"   Images: {len(test_images)} types")
        print(f"   Payload sizes: {self.test_payloads}")
        print(f"   Error correction methods: {len(self.error_correction_methods)}")
        print(f"   Modification tests: {len(self.modification_tests)}")
        print(f"   Expected total tests: ~{len(test_images) * len(self.test_payloads) * len(self.error_correction_methods)}")
        
        for image_name in test_images:
            print(f"\n🖼️  TESTING IMAGE: {image_name}")
            print("=" * 60)
            
            for payload_size in self.test_payloads:
                print(f"\n📦 Testing payload size: {payload_size} bytes")
                print("-" * 40)
                
                for method_name in self.error_correction_methods.keys():
                    result = self.test_error_correction_method(method_name, image_name, payload_size)
                    result_dict = {
                        'image': image_name,
                        'payload_size': payload_size,
                        'method': result.method,
                        'original_size': result.original_size,
                        'encoded_size': result.encoded_size,
                        'redundancy_ratio': result.redundancy_ratio,
                        'success_rate': result.success_rate,
                        'avg_psnr': result.avg_psnr,
                        'test_count': result.test_count,
                        'modification_resistance': result.modification_resistance,
                        'timestamp': time.time()
                    }
                    all_results.append(result_dict)
        
        return all_results
    
    def generate_error_correction_analysis(self, results: List[Dict]):
        """Generate comprehensive error correction analysis"""
        print("\n📊 Generating Error Correction Analysis...")
        
        # Analysis by method
        method_analysis = {}
        for result in results:
            method = result['method']
            if method not in method_analysis:
                method_analysis[method] = {
                    'total_tests': 0,
                    'successful_tests': 0,
                    'avg_redundancy': 0,
                    'avg_psnr': 0,
                    'modification_resistance': {}
                }
            
            method_analysis[method]['total_tests'] += 1
            method_analysis[method]['successful_tests'] += result['success_rate'] * result['test_count']
            method_analysis[method]['avg_redundancy'] += result['redundancy_ratio']
            method_analysis[method]['avg_psnr'] += result['avg_psnr']
            
            for mod_name, resistance in result['modification_resistance'].items():
                if mod_name not in method_analysis[method]['modification_resistance']:
                    method_analysis[method]['modification_resistance'][mod_name] = []
                method_analysis[method]['modification_resistance'][mod_name].append(resistance)
        
        # Calculate averages
        for method in method_analysis:
            data = method_analysis[method]
            data['success_rate'] = data['successful_tests'] / max(data['total_tests'] * len(self.modification_tests), 1)
            data['avg_redundancy'] /= max(data['total_tests'], 1)
            data['avg_psnr'] /= max(data['total_tests'], 1)
            
            for mod_name in data['modification_resistance']:
                data['modification_resistance'][mod_name] = np.mean(data['modification_resistance'][mod_name])
        
        # Generate plots
        self.plot_error_correction_analysis(method_analysis)
        
        # Generate report
        self.generate_error_correction_report(method_analysis, results)
        
        # Save raw results
        with open(f"{self.results_dir}/results/error_correction_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        return method_analysis
    
    def plot_error_correction_analysis(self, method_analysis: Dict):
        """Create error correction analysis plots"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        methods = list(method_analysis.keys())
        success_rates = [method_analysis[m]['success_rate'] * 100 for m in methods]
        redundancy_ratios = [method_analysis[m]['avg_redundancy'] for m in methods]
        avg_psnrs = [method_analysis[m]['avg_psnr'] for m in methods]
        
        # Success rates
        ax1.bar(methods, success_rates, color=['red' if sr < 50 else 'orange' if sr < 80 else 'green' for sr in success_rates])
        ax1.set_title('Error Correction Success Rates', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)
        for i, v in enumerate(success_rates):
            ax1.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # Redundancy ratios
        ax2.bar(methods, redundancy_ratios, color='blue', alpha=0.7)
        ax2.set_title('Error Correction Redundancy Ratios', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Redundancy Ratio')
        ax2.grid(True, alpha=0.3)
        for i, v in enumerate(redundancy_ratios):
            ax2.text(i, v + 0.05, f'{v:.2f}x', ha='center', fontweight='bold')
        
        # PSNR values
        ax3.bar(methods, avg_psnrs, color='purple', alpha=0.7)
        ax3.set_title('Average PSNR After Modifications', fontsize=12, fontweight='bold')
        ax3.set_ylabel('PSNR (dB)')
        ax3.grid(True, alpha=0.3)
        for i, v in enumerate(avg_psnrs):
            ax3.text(i, v + 1, f'{v:.1f}', ha='center', fontweight='bold')
        
        # Modification resistance heatmap
        mod_names = list(self.modification_tests.keys())
        resistance_matrix = []
        for method in methods:
            row = []
            for mod_name in mod_names:
                resistance = method_analysis[method]['modification_resistance'].get(mod_name, 0)
                row.append(resistance * 100)
            resistance_matrix.append(row)
        
        im = ax4.imshow(resistance_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        ax4.set_title('Modification Resistance Matrix (%)', fontsize=12, fontweight='bold')
        ax4.set_xticks(range(len(mod_names)))
        ax4.set_xticklabels(mod_names, rotation=45, ha='right')
        ax4.set_yticks(range(len(methods)))
        ax4.set_yticklabels(methods)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax4)
        cbar.set_label('Resistance (%)')
        
        plt.tight_layout()
        plt.savefig(f"{self.results_dir}/plots/error_correction_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Error correction plots saved")
    
    def generate_error_correction_report(self, method_analysis: Dict, results: List[Dict]):
        """Generate detailed error correction report"""
        report_path = f"{self.results_dir}/ERROR_CORRECTION_ANALYSIS_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# LayerX Error Correction Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis ID:** {os.path.basename(self.results_dir)}\n")
            f.write("**Test Type:** Error Correction Robustness Enhancement\n\n")
            
            # Executive Summary
            total_tests = sum(len(r['modification_resistance']) for r in results)
            best_method = max(method_analysis.keys(), key=lambda m: method_analysis[m]['success_rate'])
            best_success = method_analysis[best_method]['success_rate'] * 100
            
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Tests:** {total_tests}\n")
            f.write(f"- **Best Method:** {best_method} ({best_success:.1f}% success)\n")
            f.write(f"- **Target Achievement:** {'✅ ACHIEVED' if best_success >= 80 else '❌ NOT ACHIEVED'} (Target: ≥80%)\n\n")
            
            # Method Comparison
            f.write("## Error Correction Method Analysis\n\n")
            f.write("| Method | Success Rate | Redundancy | Avg PSNR | Status |\n")
            f.write("|--------|--------------|------------|----------|--------|\n")
            
            for method in sorted(method_analysis.keys(), key=lambda m: method_analysis[m]['success_rate'], reverse=True):
                data = method_analysis[method]
                success = data['success_rate'] * 100
                redundancy = data['avg_redundancy']
                psnr = data['avg_psnr']
                status = '🟢 Excellent' if success >= 80 else '🟡 Good' if success >= 50 else '🔴 Weak'
                
                f.write(f"| {method} | {success:.1f}% | {redundancy:.2f}x | {psnr:.1f}dB | {status} |\n")
            
            # Detailed findings
            f.write(f"\n## Key Findings\n\n")
            f.write(f"1. **Best Performing Method:** {best_method} with {best_success:.1f}% success rate\n")
            
            # Find most robust against specific modifications
            best_jpeg = max(method_analysis.keys(), key=lambda m: method_analysis[m]['modification_resistance'].get('jpeg_70', 0))
            best_noise = max(method_analysis.keys(), key=lambda m: method_analysis[m]['modification_resistance'].get('gaussian_noise_01', 0))
            
            f.write(f"2. **Best JPEG Resistance:** {best_jpeg} ({method_analysis[best_jpeg]['modification_resistance'].get('jpeg_70', 0)*100:.1f}%)\n")
            f.write(f"3. **Best Noise Resistance:** {best_noise} ({method_analysis[best_noise]['modification_resistance'].get('gaussian_noise_01', 0)*100:.1f}%)\n")
            
            # Recommendations
            f.write(f"\n## Implementation Recommendations\n\n")
            if best_success >= 80:
                f.write(f"✅ **Deploy {best_method}** - Achieves target robustness\n")
            else:
                f.write(f"❌ **Continue Research** - Target not achieved\n")
            
            f.write(f"\n### Production Guidelines\n")
            f.write(f"1. **Recommended Method:** {best_method}\n")
            f.write(f"2. **Expected Overhead:** {method_analysis[best_method]['avg_redundancy']:.1f}x size increase\n")
            f.write(f"3. **Quality Impact:** {method_analysis[best_method]['avg_psnr']:.1f}dB PSNR\n")
            
            # Next steps
            f.write(f"\n## Next Steps\n\n")
            if best_success < 80:
                f.write("1. **Advanced Error Correction:** Implement BCH or Reed-Solomon codes\n")
                f.write("2. **Hybrid Approaches:** Combine multiple error correction methods\n")
                f.write("3. **Adaptive Correction:** Use different methods based on expected modifications\n")
            else:
                f.write("1. **Real-world Validation:** Test with actual social media platforms\n")
                f.write("2. **Performance Optimization:** Optimize encoding/decoding speed\n")
                f.write("3. **Integration Testing:** Integrate into main LayerX pipeline\n")
            
            f.write(f"\n---\n\n")
            f.write(f"**Data Location:** `{self.results_dir}/results/error_correction_results.json`\n")
            f.write("**LayerX Error Correction Research Team**\n")
        
        print("✅ Error correction report generated")

def main():
    research = ErrorCorrectionResearch()
    
    # Run comprehensive error correction research
    results = research.run_comprehensive_error_correction_research()
    
    # Generate analysis
    method_analysis = research.generate_error_correction_analysis(results)
    
    # Summary
    total_tests = sum(len(r['modification_resistance']) for r in results)
    best_method = max(method_analysis.keys(), key=lambda m: method_analysis[m]['success_rate'])
    best_success = method_analysis[best_method]['success_rate'] * 100
    
    print(f"\n🎯 ERROR CORRECTION RESEARCH COMPLETED!")
    print(f"📊 Results: {total_tests} tests completed")
    print(f"📂 Report: {research.results_dir}/ERROR_CORRECTION_ANALYSIS_REPORT.md")
    print(f"📁 Data: {research.results_dir}/results/error_correction_results.json")
    print(f"📈 Plots: {research.results_dir}/plots/")
    print(f"🏢 Directory: {research.results_dir}")
    
    print(f"\n📈 ERROR CORRECTION SUMMARY:")
    print(f"   🏆 Best method: {best_method} ({best_success:.1f}% success)")
    print(f"   🎯 Target achievement: {'✅ ACHIEVED' if best_success >= 80 else '❌ NOT ACHIEVED'} (≥80%)")
    print(f"   📋 Ready for deployment: {'YES' if best_success >= 80 else 'NEEDS MORE RESEARCH'}")

if __name__ == "__main__":
    main()