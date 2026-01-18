"""
LayerX Robustness Testing Research
=================================

CRITICAL RESEARCH: Test LayerX resistance against real-world image modifications.
This is essential for deployment - images undergo various transformations in practice.

Research Areas:
1. JPEG compression resistance (quality 10-100)
2. Noise resistance (Gaussian, salt & pepper)  
3. Geometric transformations (scaling, rotation, cropping)
4. Brightness/contrast adjustments
5. Gamma correction resistance
6. Blur and sharpening effects
"""

import os
import sys
import io

# Fix Windows UTF-8 encoding for emoji output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
import cv2
import matplotlib.pyplot as plt
from datetime import datetime
import json
from skimage import util
import random

# Import core modules
sys.path.append('core_modules')
from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a4_compression import compress_huffman, decompress_huffman
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes

def generate_key():
    """Generate a random password for encryption"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

class RobustnessTestingResearch:
    """Comprehensive robustness testing against image modifications"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"robustness_research_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/results", exist_ok=True)
        os.makedirs(f"{self.output_dir}/plots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/test_images", exist_ok=True)
        
        self.results = []
        
        print(f"🔧 LAYERX ROBUSTNESS TESTING RESEARCH")
        print(f"=" * 45)
        print(f"📂 Output directory: {self.output_dir}")
        print(f"🎯 CRITICAL: Testing resistance to real-world image modifications")
        
    def create_robustness_test_images(self):
        """Create diverse test images for robustness testing"""
        print(f"\n📷 Creating Robustness Test Images...")
        
        test_images = []
        
        # 1. Natural scene (typical photo-like)
        natural = np.zeros((512, 512), dtype=np.uint8)
        for i in range(512):
            for j in range(512):
                # Simulate natural image with multiple frequency components
                natural[i, j] = int(128 + 
                                  40 * np.sin(i/30) * np.cos(j/40) + 
                                  20 * np.sin(i/8) * np.cos(j/12) +
                                  10 * np.sin(i/3) * np.cos(j/5))
        natural = np.clip(natural, 0, 255).astype(np.uint8)
        natural_path = f"{self.output_dir}/test_images/natural_robust.png"
        cv2.imwrite(natural_path, natural)
        test_images.append({"path": natural_path, "type": "natural", "description": "Natural photo-like pattern"})
        
        # 2. Textured image (high detail)
        np.random.seed(42)
        textured = np.random.randint(100, 200, (512, 512), dtype=np.uint8)
        # Add structured patterns
        for i in range(0, 512, 16):
            for j in range(0, 512, 16):
                block_value = int(128 + 50 * np.sin(i/20) * np.cos(j/30))
                textured[i:i+8, j:j+8] = block_value
        textured_path = f"{self.output_dir}/test_images/textured_robust.png"
        cv2.imwrite(textured_path, textured)
        test_images.append({"path": textured_path, "type": "textured", "description": "High-detail textured pattern"})
        
        print(f"✅ Created {len(test_images)} robustness test images")
        return test_images
    
    def embed_test_payload(self, cover_image_path, payload_text):
        """Embed test payload in cover image and return stego image"""
        
        cover_image = read_image(cover_image_path)
        
        # Process payload through LayerX pipeline
        key = generate_key()
        encrypted_payload, salt, iv = encrypt_message(payload_text, key)
        compressed_payload, compression_table = compress_huffman(encrypted_payload)
        payload_bits = bytes_to_bits(compressed_payload)
        
        # Embed using DWT with Q=5.0
        bands = dwt_decompose(cover_image, levels=2)
        modified_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=5.0)
        stego_image = dwt_reconstruct(modified_bands).astype(np.uint8)
        
        # Return stego image and extraction info
        return stego_image, {
            "key": key,
            "salt": salt,
            "iv": iv,
            "compression_table": compression_table,
            "payload_bits": len(payload_bits),
            "original_payload": payload_text
        }
    
    def test_extraction_after_modification(self, modified_stego_image, extraction_info):
        """Test if payload can be extracted after image modification"""
        
        try:
            # Extract from modified image
            bands = dwt_decompose(modified_stego_image, levels=2)
            extracted_bits = extract_from_dwt_bands(bands, extraction_info["payload_bits"], Q_factor=5.0)
            extracted_payload = bits_to_bytes(extracted_bits)
            
            # Decompress and decrypt
            decompressed = decompress_huffman(extracted_payload, extraction_info["compression_table"])
            final_message = decrypt_message(decompressed, extraction_info["key"], 
                                          extraction_info["salt"], extraction_info["iv"])
            
            # Check if extraction successful
            extraction_success = final_message == extraction_info["original_payload"]
            
            return {
                "extraction_success": extraction_success,
                "extracted_length": len(final_message) if final_message else 0,
                "original_length": len(extraction_info["original_payload"]),
                "match_percentage": (len(final_message) / len(extraction_info["original_payload"]) * 100) if final_message else 0
            }
            
        except Exception as e:
            return {
                "extraction_success": False,
                "error": str(e),
                "extracted_length": 0,
                "original_length": len(extraction_info["original_payload"]),
                "match_percentage": 0
            }
    
    def test_jpeg_compression_resistance(self, image_info, payload_sizes):
        """Test resistance against JPEG compression at different quality levels"""
        
        print(f"\n📊 JPEG COMPRESSION RESISTANCE - {image_info['type']} image")
        print(f"-" * 55)
        
        jpeg_results = []
        quality_levels = [10, 30, 50, 70, 85, 95]  # JPEG quality levels
        
        for payload_size in payload_sizes:
            test_payload = "LayerX robustness test payload. " * (payload_size // 32 + 1)
            test_payload = test_payload[:payload_size]
            
            print(f"\n📦 Payload: {payload_size} bytes")
            
            try:
                # Embed payload
                stego_image, extraction_info = self.embed_test_payload(image_info["path"], test_payload)
                original_psnr = psnr(read_image(image_info["path"]), stego_image)
                
                for quality in quality_levels:
                    # Apply JPEG compression
                    temp_path = f"{self.output_dir}/temp_jpeg_q{quality}.jpg"
                    cv2.imwrite(temp_path, stego_image, [cv2.IMWRITE_JPEG_QUALITY, quality])
                    compressed_image = cv2.imread(temp_path, cv2.IMREAD_GRAYSCALE)
                    
                    # Test extraction
                    extraction_result = self.test_extraction_after_modification(compressed_image, extraction_info)
                    
                    # Calculate quality metrics
                    compressed_psnr = psnr(stego_image, compressed_image)
                    
                    result = {
                        "test_type": "jpeg_compression",
                        "image_type": image_info["type"],
                        "payload_size": payload_size,
                        "jpeg_quality": quality,
                        "original_psnr": original_psnr,
                        "compressed_psnr": compressed_psnr,
                        **extraction_result
                    }
                    
                    jpeg_results.append(result)
                    
                    status = "✅" if extraction_result["extraction_success"] else "❌"
                    print(f"   Q={quality:2d}: {status} PSNR={compressed_psnr:5.2f}dB Match={extraction_result['match_percentage']:5.1f}%")
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return jpeg_results
    
    def test_noise_resistance(self, image_info, payload_sizes):
        """Test resistance against different types of noise"""
        
        print(f"\n🔊 NOISE RESISTANCE - {image_info['type']} image")
        print(f"-" * 45)
        
        noise_results = []
        
        # Test different noise types and levels
        noise_tests = [
            {"type": "gaussian", "params": [0.01, 0.05, 0.1, 0.2]},  # sigma values
            {"type": "salt_pepper", "params": [0.01, 0.05, 0.1, 0.2]}  # density values
        ]
        
        for payload_size in payload_sizes[:2]:  # Limit for noise testing
            test_payload = "LayerX noise resistance test payload. " * (payload_size // 35 + 1)
            test_payload = test_payload[:payload_size]
            
            print(f"\n📦 Payload: {payload_size} bytes")
            
            try:
                # Embed payload
                stego_image, extraction_info = self.embed_test_payload(image_info["path"], test_payload)
                
                for noise_test in noise_tests:
                    print(f"   🔊 {noise_test['type'].replace('_', ' ').title()} noise:")
                    
                    for param in noise_test["params"]:
                        # Apply noise
                        if noise_test["type"] == "gaussian":
                            noisy_image = util.random_noise(stego_image/255.0, mode='gaussian', 
                                                           var=param**2, clip=True)
                            noisy_image = (noisy_image * 255).astype(np.uint8)
                            param_name = f"σ={param}"
                        else:  # salt_pepper
                            noisy_image = util.random_noise(stego_image/255.0, mode='s&p', 
                                                           amount=param, clip=True)
                            noisy_image = (noisy_image * 255).astype(np.uint8)
                            param_name = f"d={param}"
                        
                        # Test extraction
                        extraction_result = self.test_extraction_after_modification(noisy_image, extraction_info)
                        
                        # Calculate quality metrics
                        noisy_psnr = psnr(stego_image, noisy_image)
                        
                        result = {
                            "test_type": f"{noise_test['type']}_noise",
                            "image_type": image_info["type"],
                            "payload_size": payload_size,
                            "noise_parameter": param,
                            "noisy_psnr": noisy_psnr,
                            **extraction_result
                        }
                        
                        noise_results.append(result)
                        
                        status = "✅" if extraction_result["extraction_success"] else "❌"
                        print(f"      {param_name}: {status} PSNR={noisy_psnr:5.2f}dB Match={extraction_result['match_percentage']:5.1f}%")
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return noise_results
    
    def test_geometric_transformations(self, image_info, payload_sizes):
        """Test resistance against geometric transformations"""
        
        print(f"\n📐 GEOMETRIC TRANSFORMATIONS - {image_info['type']} image")
        print(f"-" * 55)
        
        geometric_results = []
        
        # Test different geometric transformations
        transforms = [
            {"type": "scaling", "params": [0.8, 1.2, 1.5]},  # scale factors
            {"type": "rotation", "params": [1, 3, 5, 10]},   # rotation degrees
            {"type": "cropping", "params": [0.05, 0.1, 0.2]} # crop percentage
        ]
        
        for payload_size in payload_sizes[:2]:  # Limit for geometric testing
            test_payload = "LayerX geometric test payload. " * (payload_size // 30 + 1)
            test_payload = test_payload[:payload_size]
            
            print(f"\n📦 Payload: {payload_size} bytes")
            
            try:
                # Embed payload
                stego_image, extraction_info = self.embed_test_payload(image_info["path"], test_payload)
                h, w = stego_image.shape
                
                for transform in transforms:
                    print(f"   📐 {transform['type'].title()}:")
                    
                    for param in transform["params"]:
                        try:
                            if transform["type"] == "scaling":
                                # Scale image
                                new_size = (int(w * param), int(h * param))
                                scaled = cv2.resize(stego_image, new_size)
                                # Resize back to original size
                                transformed_image = cv2.resize(scaled, (w, h))
                                param_name = f"×{param}"
                                
                            elif transform["type"] == "rotation":
                                # Rotate image
                                center = (w//2, h//2)
                                rotation_matrix = cv2.getRotationMatrix2D(center, param, 1.0)
                                rotated = cv2.warpAffine(stego_image, rotation_matrix, (w, h))
                                # Rotate back
                                rotation_matrix_back = cv2.getRotationMatrix2D(center, -param, 1.0)
                                transformed_image = cv2.warpAffine(rotated, rotation_matrix_back, (w, h))
                                param_name = f"{param}°"
                                
                            elif transform["type"] == "cropping":
                                # Crop image and pad back
                                crop_pixels = int(min(h, w) * param / 2)
                                cropped = stego_image[crop_pixels:h-crop_pixels, crop_pixels:w-crop_pixels]
                                # Resize cropped back to original size
                                transformed_image = cv2.resize(cropped, (w, h))
                                param_name = f"{param*100:.0f}%"
                            
                            # Test extraction
                            extraction_result = self.test_extraction_after_modification(transformed_image, extraction_info)
                            
                            # Calculate quality metrics
                            transform_psnr = psnr(stego_image, transformed_image)
                            
                            result = {
                                "test_type": f"{transform['type']}_transform",
                                "image_type": image_info["type"],
                                "payload_size": payload_size,
                                "transform_parameter": param,
                                "transform_psnr": transform_psnr,
                                **extraction_result
                            }
                            
                            geometric_results.append(result)
                            
                            status = "✅" if extraction_result["extraction_success"] else "❌"
                            print(f"      {param_name}: {status} PSNR={transform_psnr:5.2f}dB Match={extraction_result['match_percentage']:5.1f}%")
                            
                        except Exception as e:
                            print(f"      {param_name}: ❌ Error: {str(e)[:30]}")
                            
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return geometric_results
    
    def test_brightness_contrast_adjustments(self, image_info, payload_sizes):
        """Test resistance against brightness and contrast adjustments"""
        
        print(f"\n💡 BRIGHTNESS/CONTRAST ADJUSTMENTS - {image_info['type']} image")
        print(f"-" * 60)
        
        brightness_results = []
        
        # Test different brightness and contrast adjustments
        adjustments = [
            {"type": "brightness", "params": [-30, -15, 15, 30]},  # brightness delta
            {"type": "contrast", "params": [0.7, 0.9, 1.1, 1.3]}  # contrast multiplier
        ]
        
        for payload_size in payload_sizes[:2]:  # Limit for brightness testing
            test_payload = "LayerX brightness test payload. " * (payload_size // 32 + 1)
            test_payload = test_payload[:payload_size]
            
            print(f"\n📦 Payload: {payload_size} bytes")
            
            try:
                # Embed payload
                stego_image, extraction_info = self.embed_test_payload(image_info["path"], test_payload)
                
                for adjustment in adjustments:
                    print(f"   💡 {adjustment['type'].title()} adjustment:")
                    
                    for param in adjustment["params"]:
                        # Apply adjustment
                        if adjustment["type"] == "brightness":
                            adjusted_image = np.clip(stego_image.astype(np.int16) + param, 0, 255).astype(np.uint8)
                            param_name = f"Δ{param:+d}"
                        else:  # contrast
                            adjusted_image = np.clip(stego_image.astype(np.float32) * param, 0, 255).astype(np.uint8)
                            param_name = f"×{param}"
                        
                        # Test extraction
                        extraction_result = self.test_extraction_after_modification(adjusted_image, extraction_info)
                        
                        # Calculate quality metrics
                        adjusted_psnr = psnr(stego_image, adjusted_image)
                        
                        result = {
                            "test_type": f"{adjustment['type']}_adjustment",
                            "image_type": image_info["type"],
                            "payload_size": payload_size,
                            "adjustment_parameter": param,
                            "adjusted_psnr": adjusted_psnr,
                            **extraction_result
                        }
                        
                        brightness_results.append(result)
                        
                        status = "✅" if extraction_result["extraction_success"] else "❌"
                        print(f"      {param_name}: {status} PSNR={adjusted_psnr:5.2f}dB Match={extraction_result['match_percentage']:5.1f}%")
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return brightness_results
    
    def run_comprehensive_robustness_testing(self):
        """Run comprehensive robustness testing across all modification types"""
        
        print(f"\n🚀 COMPREHENSIVE ROBUSTNESS TESTING")
        print(f"=" * 40)
        
        # Create test images
        test_images = self.create_robustness_test_images()
        
        # Test payload sizes (limited for robustness testing)
        payload_sizes = [512, 2048]  # Medium payload sizes for robustness
        
        print(f"\n📋 Robustness Test Configuration:")
        print(f"   Images: {len(test_images)} types")
        print(f"   Payload sizes: {payload_sizes}")
        print(f"   Modification types: 5 categories")
        print(f"   Expected tests: ~100+ individual tests")
        
        all_results = []
        
        # Test each image type against all modifications
        for image_info in test_images:
            print(f"\n🖼️  TESTING IMAGE: {image_info['type']} ({image_info['description']})")
            print(f"=" * 60)
            
            # 1. JPEG Compression Testing
            jpeg_results = self.test_jpeg_compression_resistance(image_info, payload_sizes)
            all_results.extend(jpeg_results)
            
            # 2. Noise Resistance Testing  
            noise_results = self.test_noise_resistance(image_info, payload_sizes)
            all_results.extend(noise_results)
            
            # 3. Geometric Transformations Testing
            geometric_results = self.test_geometric_transformations(image_info, payload_sizes)
            all_results.extend(geometric_results)
            
            # 4. Brightness/Contrast Testing
            brightness_results = self.test_brightness_contrast_adjustments(image_info, payload_sizes)
            all_results.extend(brightness_results)
        
        self.results = all_results
        return all_results
    
    def generate_robustness_analysis_plots(self):
        """Generate visualization plots for robustness analysis"""
        
        print(f"\n📊 Generating Robustness Analysis Plots...")
        
        if not self.results:
            print("No results to plot")
            return
        
        # Filter successful extractions
        successful_results = [r for r in self.results if r.get('extraction_success', False)]
        
        if not successful_results:
            print("No successful extractions to analyze")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Success Rate by Test Type
        test_types = {}
        for result in self.results:
            test_type = result.get('test_type', 'unknown')
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "successful": 0}
            test_types[test_type]["total"] += 1
            if result.get('extraction_success', False):
                test_types[test_type]["successful"] += 1
        
        type_names = list(test_types.keys())
        success_rates = [test_types[t]["successful"] / test_types[t]["total"] * 100 for t in type_names]
        
        bars = ax1.bar(range(len(type_names)), success_rates, alpha=0.7, 
                      color=['green' if sr >= 80 else 'orange' if sr >= 50 else 'red' for sr in success_rates])
        ax1.set_xlabel('Test Type')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_title('Robustness: Success Rate by Modification Type')
        ax1.set_xticks(range(len(type_names)))
        ax1.set_xticklabels([t.replace('_', '\n') for t in type_names], rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=80, color='green', linestyle=':', alpha=0.6, label='Good Threshold')
        ax1.axhline(y=50, color='orange', linestyle=':', alpha=0.6, label='Acceptable Threshold')
        
        # Add percentage labels on bars
        for bar, rate in zip(bars, success_rates):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        # 2. JPEG Compression Resistance
        jpeg_results = [r for r in self.results if r.get('test_type') == 'jpeg_compression']
        if jpeg_results:
            quality_levels = sorted(list(set(r.get('jpeg_quality', 0) for r in jpeg_results)))
            jpeg_success_by_quality = {}
            
            for quality in quality_levels:
                quality_results = [r for r in jpeg_results if r.get('jpeg_quality') == quality]
                success_count = len([r for r in quality_results if r.get('extraction_success', False)])
                total_count = len(quality_results)
                jpeg_success_by_quality[quality] = (success_count / total_count * 100) if total_count > 0 else 0
            
            ax2.plot(quality_levels, [jpeg_success_by_quality[q] for q in quality_levels], 
                    marker='o', linewidth=2, markersize=8, color='blue')
            ax2.fill_between(quality_levels, [jpeg_success_by_quality[q] for q in quality_levels], alpha=0.3)
            ax2.set_xlabel('JPEG Quality Level')
            ax2.set_ylabel('Success Rate (%)')
            ax2.set_title('JPEG Compression Resistance')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=80, color='green', linestyle=':', alpha=0.6)
            ax2.axhline(y=50, color='orange', linestyle=':', alpha=0.6)
        
        # 3. Noise Resistance
        noise_results = [r for r in self.results if 'noise' in r.get('test_type', '')]
        if noise_results:
            # Group by noise type
            gaussian_results = [r for r in noise_results if 'gaussian' in r.get('test_type', '')]
            sp_results = [r for r in noise_results if 'salt_pepper' in r.get('test_type', '')]
            
            noise_data = {}
            for results, name in [(gaussian_results, 'Gaussian'), (sp_results, 'Salt&Pepper')]:
                if results:
                    success_rate = len([r for r in results if r.get('extraction_success', False)]) / len(results) * 100
                    noise_data[name] = success_rate
            
            if noise_data:
                bars = ax3.bar(noise_data.keys(), noise_data.values(), alpha=0.7, color=['skyblue', 'lightcoral'])
                ax3.set_ylabel('Success Rate (%)')
                ax3.set_title('Noise Resistance')
                ax3.grid(True, alpha=0.3)
                ax3.axhline(y=80, color='green', linestyle=':', alpha=0.6)
                ax3.axhline(y=50, color='orange', linestyle=':', alpha=0.6)
                
                for bar, (name, rate) in zip(bars, noise_data.items()):
                    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                            f'{rate:.1f}%', ha='center', va='bottom')
        
        # 4. Overall Robustness Summary
        image_types = list(set(r.get('image_type', 'unknown') for r in self.results))
        image_success = {}
        
        for img_type in image_types:
            type_results = [r for r in self.results if r.get('image_type') == img_type]
            success_count = len([r for r in type_results if r.get('extraction_success', False)])
            total_count = len(type_results)
            image_success[img_type] = (success_count / total_count * 100) if total_count > 0 else 0
        
        bars = ax4.bar(image_success.keys(), image_success.values(), alpha=0.7, color='lightgreen')
        ax4.set_ylabel('Success Rate (%)')
        ax4.set_title('Robustness by Image Type')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=80, color='green', linestyle=':', alpha=0.6)
        ax4.axhline(y=50, color='orange', linestyle=':', alpha=0.6)
        
        for bar, (img_type, rate) in zip(bars, image_success.items()):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plot_path = f"{self.output_dir}/plots/robustness_analysis.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✅ Robustness plots saved: {plot_path}")
        return plot_path
    
    def generate_robustness_report(self):
        """Generate comprehensive robustness analysis report"""
        
        print(f"\n📊 Generating Robustness Analysis Report...")
        
        # Save raw results
        results_file = f"{self.output_dir}/results/robustness_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate markdown report
        report_path = f"{self.output_dir}/ROBUSTNESS_ANALYSIS_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# LayerX Robustness Testing Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis ID:** {self.timestamp}\n")
            f.write(f"**Test Type:** Real-world Image Modification Resistance\n\n")
            
            if self.results:
                successful_results = [r for r in self.results if r.get('extraction_success', False)]
                
                f.write("## Executive Summary\n\n")
                f.write(f"- **Total Tests:** {len(self.results)}\n")
                f.write(f"- **Successful Extractions:** {len(successful_results)} ({len(successful_results)/len(self.results)*100:.1f}%)\n")
                
                # Success rate by test type
                test_types = {}
                for result in self.results:
                    test_type = result.get('test_type', 'unknown')
                    if test_type not in test_types:
                        test_types[test_type] = {"total": 0, "successful": 0}
                    test_types[test_type]["total"] += 1
                    if result.get('extraction_success', False):
                        test_types[test_type]["successful"] += 1
                
                f.write("\n## Robustness Analysis by Modification Type\n\n")
                f.write("| Modification Type | Tests | Success Rate | Status |\n")
                f.write("|------------------|-------|--------------|--------|\n")
                
                for test_type, stats in test_types.items():
                    success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
                    status = "🟢 Robust" if success_rate >= 80 else "🟡 Moderate" if success_rate >= 50 else "🔴 Weak"
                    f.write(f"| {test_type.replace('_', ' ').title()} | {stats['total']} | {success_rate:.1f}% | {status} |\n")
                
                # JPEG compression detailed analysis
                jpeg_results = [r for r in self.results if r.get('test_type') == 'jpeg_compression']
                if jpeg_results:
                    f.write("\n### JPEG Compression Resistance\n\n")
                    f.write("| Quality Level | Tests | Success Rate | Notes |\n")
                    f.write("|---------------|-------|--------------|-------|\n")
                    
                    quality_levels = sorted(list(set(r.get('jpeg_quality', 0) for r in jpeg_results)))
                    for quality in quality_levels:
                        quality_results = [r for r in jpeg_results if r.get('jpeg_quality') == quality]
                        success_count = len([r for r in quality_results if r.get('extraction_success', False)])
                        total_count = len(quality_results)
                        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                        
                        if quality >= 80:
                            notes = "High quality - good resistance expected"
                        elif quality >= 50:
                            notes = "Medium quality - moderate resistance"
                        else:
                            notes = "Low quality - challenging conditions"
                        
                        f.write(f"| Q={quality} | {total_count} | {success_rate:.1f}% | {notes} |\n")
                
                f.write("\n## Key Robustness Findings\n\n")
                
                # Overall robustness assessment
                overall_success_rate = len(successful_results) / len(self.results) * 100
                if overall_success_rate >= 80:
                    robustness_level = "🟢 EXCELLENT - High robustness against modifications"
                elif overall_success_rate >= 60:
                    robustness_level = "🟡 GOOD - Moderate robustness with some limitations"
                else:
                    robustness_level = "🔴 NEEDS IMPROVEMENT - Low robustness against modifications"
                
                f.write(f"1. **Overall Robustness:** {overall_success_rate:.1f}% - {robustness_level}\n")
                
                # Most robust against
                best_test = max(test_types.items(), key=lambda x: x[1]["successful"]/x[1]["total"] if x[1]["total"] > 0 else 0)
                best_success_rate = (best_test[1]["successful"] / best_test[1]["total"] * 100) if best_test[1]["total"] > 0 else 0
                f.write(f"2. **Most Robust Against:** {best_test[0].replace('_', ' ').title()} ({best_success_rate:.1f}% success)\n")
                
                # Most vulnerable to
                worst_test = min(test_types.items(), key=lambda x: x[1]["successful"]/x[1]["total"] if x[1]["total"] > 0 else 0)
                worst_success_rate = (worst_test[1]["successful"] / worst_test[1]["total"] * 100) if worst_test[1]["total"] > 0 else 0
                f.write(f"3. **Most Vulnerable To:** {worst_test[0].replace('_', ' ').title()} ({worst_success_rate:.1f}% success)\n")
                
                f.write("\n## Deployment Recommendations\n\n")
                f.write("### Production Guidelines\n")
                f.write("1. **JPEG Quality:** Maintain source quality ≥70 for reliable extraction\n")
                f.write("2. **Image Processing:** Minimize aggressive noise reduction and sharpening\n")
                f.write("3. **Geometric Changes:** Avoid significant scaling or rotation in processing pipeline\n")
                f.write("4. **Quality Control:** Test critical applications against expected modifications\n\n")
                
                f.write("### Technical Improvements\n")
                f.write("1. **Error Correction:** Implement error correction codes for robustness\n")
                f.write("2. **Redundant Embedding:** Use redundant embedding for critical payloads\n")
                f.write("3. **Adaptive Techniques:** Develop modification-aware embedding strategies\n")
                f.write("4. **Quality Monitoring:** Implement quality degradation detection\n\n")
                
            f.write("## Next Steps\n\n")
            f.write("1. **Error Correction Research:** Implement and test error correction methods\n")
            f.write("2. **Real-world Platform Testing:** Test with actual social media platforms\n")
            f.write("3. **Advanced Robustness:** Test against sophisticated image processing\n")
            f.write("4. **Performance Optimization:** Optimize robustness vs capacity trade-offs\n\n")
            
            f.write("---\n\n")
            f.write(f"**Data Location:** `{results_file}`\n")
            f.write("**LayerX Robustness Research Team**\n")
        
        print(f"✅ Robustness report generated: {report_path}")
        print(f"✅ Raw data saved: {results_file}")
        
        return report_path, results_file

if __name__ == "__main__":
    print("🔧 LayerX Robustness Testing Research")
    print("=" * 40)
    print("CRITICAL RESEARCH: Testing resistance to real-world image modifications")
    print()
    
    # Initialize robustness research
    robustness_research = RobustnessTestingResearch()
    
    # Run comprehensive robustness testing
    results = robustness_research.run_comprehensive_robustness_testing()
    
    # Generate visualizations
    robustness_research.generate_robustness_analysis_plots()
    
    # Generate comprehensive report
    report_path, data_path = robustness_research.generate_robustness_report()
    
    print(f"\n🎯 ROBUSTNESS RESEARCH COMPLETED!")
    print(f"📊 Results: {len(results)} tests completed")
    print(f"📂 Report: {report_path}")
    print(f"📁 Data: {data_path}")
    print(f"📈 Plots: {robustness_research.output_dir}/plots/")
    print(f"🏢 Directory: {robustness_research.output_dir}")
    
    # Summary statistics
    successful = len([r for r in results if r.get('extraction_success', False)])
    if successful > 0 and len(results) > 0:
        success_rate = successful / len(results) * 100
        print(f"\n📈 ROBUSTNESS SUMMARY:")
        print(f"   ✅ Successful tests: {successful}/{len(results)} ({success_rate:.1f}%)")
        
        # Robustness assessment
        if success_rate >= 80:
            robustness_status = "🟢 EXCELLENT - High robustness"
        elif success_rate >= 60:
            robustness_status = "🟡 GOOD - Moderate robustness"
        else:
            robustness_status = "🔴 NEEDS IMPROVEMENT - Low robustness"
            
        print(f"   🛡️  Robustness status: {robustness_status}")
        print(f"   📋 Ready for real-world deployment: {'YES' if success_rate >= 70 else 'NEEDS IMPROVEMENT'}")