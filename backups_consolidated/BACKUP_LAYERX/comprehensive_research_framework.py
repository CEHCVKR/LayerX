"""
Comprehensive Steganography Research & Testing Framework
===========================================================

Systematic analysis of:
1. Different image sizes & resolutions (real internet images)
2. Different payload sizes (data hiding capacity)
3. Different embedding methods (DWT, DCT, DWT+DCT)
4. Different Q-factor values (quantization analysis)
5. Detailed process metrics (encryption, compression, embedding sizes)

Research Methodology: Following scientific experimental design for academic validation
"""

import os
import json
import time
import requests
import numpy as np
import struct
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
import pandas as pd
from urllib.request import urlretrieve
from io import BytesIO
from PIL import Image
import hashlib

# Import our core modules
import sys
sys.path.append('core_modules')
sys.path.append('applications')

from a1_encryption import encrypt_message, decrypt_message

def generate_key():
    """Generate a random password for encryption"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))
from a3_image_processing import read_image, dwt_decompose, dct_on_ll, idct_on_ll, dwt_reconstruct, psnr
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color
from a4_compression import compress_huffman, decompress_huffman
from a5_embedding_extraction import (embed_in_dwt_bands, extract_from_dwt_bands, 
                                   embed_in_dwt_bands_color, extract_from_dwt_bands_color, 
                                   bytes_to_bits, bits_to_bytes)

class ComprehensiveSteganographyResearch:
    """
    Scientific research framework for systematic steganography analysis.
    
    Research Questions:
    1. How do image dimensions affect embedding capacity and quality?
    2. What is the optimal payload-to-image size ratio?
    3. How do different embedding domains (DWT vs DCT vs Hybrid) compare?
    4. What is the scientific justification for Q=5.0 vs other values?
    5. What are the complete processing overheads at each stage?
    """
    
    def __init__(self):
        self.results = []
        self.experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"comprehensive_research_{self.experiment_id}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/images", exist_ok=True)
        os.makedirs(f"{self.output_dir}/outputs", exist_ok=True)
        os.makedirs(f"{self.output_dir}/analysis", exist_ok=True)
        os.makedirs(f"{self.output_dir}/plots", exist_ok=True)
        
        # Image test parameters (real internet images)
        self.image_configs = [
            # Small images
            {"size": 256, "name": "small_portrait", "url": "https://picsum.photos/256/256?random=1"},
            {"size": 256, "name": "small_landscape", "url": "https://picsum.photos/256/256?random=2"},
            
            # Medium images
            {"size": 512, "name": "medium_portrait", "url": "https://picsum.photos/512/512?random=3"}, 
            {"size": 512, "name": "medium_landscape", "url": "https://picsum.photos/512/512?random=4"},
            
            # Large images
            {"size": 1024, "name": "large_portrait", "url": "https://picsum.photos/1024/1024?random=5"},
            {"size": 1024, "name": "large_landscape", "url": "https://picsum.photos/1024/1024?random=6"},
            
            # High resolution images
            {"size": 2048, "name": "hires_portrait", "url": "https://picsum.photos/2048/2048?random=7"},
            {"size": 2048, "name": "hires_landscape", "url": "https://picsum.photos/2048/2048?random=8"},
        ]
        
        # Systematic payload sizes (bytes) - Scientific progression
        self.payload_sizes = [
            # Micro payloads (cryptographic keys, IDs)
            16, 32, 64, 128,
            # Small payloads (short messages, tokens)
            256, 512, 1024, 2048,
            # Medium payloads (text messages, small files)
            4096, 8192, 16384, 32768,
            # Large payloads (documents, larger files)
            65536, 131072, 262144, 524288,
            # Maximum capacity tests
            1048576, 2097152
        ]
        
        # Embedding methods for systematic comparison
        self.embedding_methods = [
            {
                "name": "DWT_Only",
                "description": "Pure DWT embedding in high-frequency bands",
                "use_dct": False,
                "color": False,
                "bands": ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2"]
            },
            {
                "name": "DCT_Only", 
                "description": "Pure DCT embedding in LL2 band",
                "use_dct": True,
                "color": False,
                "bands": ["LL2_DCT"]
            },
            {
                "name": "DWT_DCT_Hybrid",
                "description": "Hybrid DWT+DCT embedding (current method)",
                "use_dct": True,
                "color": False, 
                "bands": ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2", "LL2_DCT"]
            },
            {
                "name": "Color_DWT_DCT",
                "description": "Color image hybrid embedding",
                "use_dct": True,
                "color": True,
                "bands": ["RGB_ALL"]
            }
        ]
        
        # Q-factor scientific analysis range
        self.q_factors = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 15.0, 20.0]
        
        print(f"🔬 COMPREHENSIVE STEGANOGRAPHY RESEARCH FRAMEWORK")
        print(f"=" * 60)
        print(f"📊 Image Configurations: {len(self.image_configs)}")
        print(f"📏 Payload Sizes: {len(self.payload_sizes)} ({min(self.payload_sizes)} - {max(self.payload_sizes)} bytes)")
        print(f"🧪 Embedding Methods: {len(self.embedding_methods)}")
        print(f"⚙️  Q-Factor Range: {self.q_factors}")
        print(f"🎯 Total Planned Experiments: {len(self.image_configs) * len(self.payload_sizes) * len(self.embedding_methods) * len(self.q_factors)}")
        print(f"📂 Output Directory: {self.output_dir}")

    def download_test_images(self):
        """Download real images from internet for testing"""
        print("\n🌐 PHASE 1: Downloading Real Test Images from Internet")
        print("-" * 50)
        
        downloaded_images = []
        
        for config in self.image_configs:
            try:
                print(f"📥 Downloading {config['name']} ({config['size']}x{config['size']})...")
                
                # Download image
                response = requests.get(config['url'], timeout=30)
                response.raise_for_status()
                
                # Convert to image
                image = Image.open(BytesIO(response.content))
                
                # Resize to exact dimensions
                image = image.resize((config['size'], config['size']), Image.Resampling.LANCZOS)
                
                # Save in multiple formats for testing
                base_path = f"{self.output_dir}/images/{config['name']}_{config['size']}x{config['size']}"
                
                # Save as PNG (lossless)
                png_path = f"{base_path}.png"
                image.save(png_path, "PNG", optimize=True)
                
                # Save as JPEG (lossy) 
                jpg_path = f"{base_path}.jpg"
                image.save(jpg_path, "JPEG", quality=95)
                
                # Verify image properties
                test_img = cv2.imread(png_path)
                actual_size = test_img.shape
                
                image_info = {
                    "name": config['name'],
                    "size": config['size'],
                    "png_path": png_path,
                    "jpg_path": jpg_path,
                    "actual_dimensions": actual_size,
                    "file_size_png": os.path.getsize(png_path),
                    "file_size_jpg": os.path.getsize(jpg_path),
                    "url": config['url']
                }
                
                downloaded_images.append(image_info)
                
                print(f"  ✅ {config['name']}: {actual_size[0]}x{actual_size[1]} pixels")
                print(f"     PNG: {image_info['file_size_png']:,} bytes")
                print(f"     JPG: {image_info['file_size_jpg']:,} bytes")
                
            except Exception as e:
                print(f"  ❌ Failed to download {config['name']}: {str(e)}")
                continue
                
        print(f"\n✅ Successfully downloaded {len(downloaded_images)} test images")
        return downloaded_images

    def generate_test_payloads(self) -> Dict[int, Dict]:
        """Generate systematic test payloads of different sizes"""
        print("\n📝 PHASE 2: Generating Systematic Test Payloads")
        print("-" * 50)
        
        payloads = {}
        
        for size in self.payload_sizes:
            try:
                # Generate realistic payload content
                if size <= 64:
                    # Small: cryptographic data, IDs, tokens
                    content = os.urandom(size // 2).hex()[:size]
                elif size <= 1024:
                    # Medium: text messages, JSON data
                    base_text = "This is a test message for steganography research. " * 20
                    content = base_text[:size]
                elif size <= 32768:
                    # Large: documents, structured data
                    base_text = ("Scientific steganography research payload. " + 
                               "Testing embedding capacity and quality metrics. " +
                               "This payload contains realistic text data. ") * 100
                    content = base_text[:size]
                else:
                    # Very large: binary data, files
                    content = os.urandom(size).hex()[:size]
                
                # Ensure exact size
                if len(content) < size:
                    content = content + "X" * (size - len(content))
                content = content[:size]
                
                payload_info = {
                    "size_bytes": len(content),
                    "content": content,
                    "type": self._classify_payload_type(size),
                    "hash": hashlib.md5(content.encode()).hexdigest()
                }
                
                payloads[size] = payload_info
                print(f"  📦 {size:>8} bytes: {payload_info['type']}")
                
            except Exception as e:
                print(f"  ❌ Failed to generate {size} byte payload: {e}")
                
        print(f"\n✅ Generated {len(payloads)} systematic test payloads")
        return payloads

    def _classify_payload_type(self, size: int) -> str:
        """Classify payload by size for research categorization"""
        if size <= 128:
            return "Cryptographic"
        elif size <= 2048:
            return "Short Message"
        elif size <= 32768:
            return "Document"
        elif size <= 524288:
            return "Large File"
        else:
            return "Maximum Capacity"

    def test_single_configuration(self, image_path: str, payload: str, 
                                 method: Dict, q_factor: float) -> Dict:
        """Test single configuration and return detailed metrics"""
        
        start_time = time.time()
        
        # Initialize result structure
        result = {
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "payload_size": len(payload),
            "method": method["name"],
            "q_factor": q_factor,
            "success": False,
            "error": None
        }
        
        try:
            # STEP 1: Load and analyze image
            step1_start = time.time()
            if method["color"]:
                cover_image = read_image_color(image_path)
                image_shape = cover_image.shape
            else:
                cover_image = read_image(image_path)  
                image_shape = cover_image.shape
            
            result["image_dimensions"] = image_shape
            result["image_pixels"] = image_shape[0] * image_shape[1]
            result["image_file_size"] = os.path.getsize(image_path)
            result["step1_load_time"] = time.time() - step1_start
            
            # STEP 2: Encryption
            step2_start = time.time()
            key = generate_key()
            encrypted_payload, salt, iv = encrypt_message(payload, key)
            result["salt"] = salt
            result["iv"] = iv
            
            result["original_payload_size"] = len(payload)
            result["encrypted_size"] = len(encrypted_payload)
            result["encryption_overhead"] = len(encrypted_payload) - len(payload)
            result["encryption_ratio"] = len(encrypted_payload) / len(payload)
            result["key_size"] = len(key)
            result["step2_encrypt_time"] = time.time() - step2_start
            
            # STEP 3: Compression
            step3_start = time.time()
            compressed_payload, compression_table = compress_huffman(encrypted_payload)
            
            result["compressed_size"] = len(compressed_payload)
            result["compression_ratio"] = len(compressed_payload) / len(encrypted_payload)
            result["compression_efficiency"] = 1 - (len(compressed_payload) / len(encrypted_payload))
            result["compression_table_size"] = len(str(compression_table))
            result["step3_compress_time"] = time.time() - step3_start
            
            # STEP 4: Transform to frequency domain
            step4_start = time.time()
            if method["color"]:
                bands = dwt_decompose_color(cover_image, levels=2)
            else:
                bands = dwt_decompose(cover_image, levels=2)
                
            # Apply DCT if required
            if method["use_dct"]:
                bands["LL2_DCT"] = dct_on_ll(bands["LL2"])
                
            result["step4_transform_time"] = time.time() - step4_start
            
            # STEP 5: Calculate embedding capacity
            step5_start = time.time()
            payload_bits = bytes_to_bits(compressed_payload)
            required_bits = len(payload_bits)
            
            # Calculate available capacity based on method
            available_capacity = 0
            for band_name in method["bands"]:
                if band_name == "LL2_DCT":
                    available_capacity += bands["LL2_DCT"].size // q_factor
                elif "RGB_ALL" in band_name and method["color"]:
                    for channel in ['R', 'G', 'B']:
                        for band in ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']:
                            available_capacity += bands[f"{channel}_{band}"].size // q_factor
                else:
                    available_capacity += bands[band_name].size // q_factor
                    
            result["required_bits"] = required_bits
            result["available_capacity"] = available_capacity
            result["capacity_utilization"] = required_bits / available_capacity if available_capacity > 0 else float('inf')
            result["step5_capacity_time"] = time.time() - step5_start
            
            # Check if payload fits
            if required_bits > available_capacity:
                result["error"] = f"Payload too large: {required_bits} bits required, {available_capacity} available"
                return result
            
            # STEP 6: Embedding
            step6_start = time.time()
            if method["color"]:
                modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=q_factor)
            else:
                modified_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=q_factor)
            result["step6_embed_time"] = time.time() - step6_start
            
            # STEP 7: Reconstruct stego image
            step7_start = time.time()
            if method["use_dct"]:
                modified_bands["LL2"] = idct_on_ll(modified_bands["LL2_DCT"])
                
            if method["color"]:
                stego_image = dwt_reconstruct_color(modified_bands)
            else:
                stego_image = dwt_reconstruct(modified_bands)
            result["step7_reconstruct_time"] = time.time() - step7_start
            
            # STEP 8: Quality analysis
            step8_start = time.time()
            if method["color"]:
                # Convert to grayscale for PSNR calculation
                cover_gray = cv2.cvtColor(cover_image, cv2.COLOR_RGB2GRAY)
                stego_gray = cv2.cvtColor(stego_image.astype(np.uint8), cv2.COLOR_RGB2GRAY)
                psnr_value = psnr(cover_gray, stego_gray)
            else:
                psnr_value = psnr(cover_image, stego_image.astype(np.uint8))
                
            result["psnr_db"] = psnr_value
            result["quality_rating"] = self._classify_quality(psnr_value)
            result["step8_quality_time"] = time.time() - step8_start
            
            # STEP 9: Extraction verification
            step9_start = time.time()
            if method["color"]:
                extracted_bits = extract_from_dwt_bands_color(modified_bands, required_bits, Q_factor=q_factor)
            else:
                extracted_bits = extract_from_dwt_bands(modified_bands, required_bits, Q_factor=q_factor)
                
            extracted_payload = bits_to_bytes(extracted_bits)
            
            # Verify extraction
            extraction_success = extracted_payload == compressed_payload
            result["extraction_success"] = extraction_success
            result["step9_extract_time"] = time.time() - step9_start
            
            # STEP 10: Full pipeline verification
            step10_start = time.time()
            if extraction_success:
                try:
                    decompressed = decompress_huffman(extracted_payload, compression_table)
                    final_message = decrypt_message(decompressed, key, result["salt"], result["iv"])
                    result["pipeline_success"] = final_message == payload
                    result["final_message_length"] = len(final_message)
                except Exception as e:
                    result["pipeline_success"] = False
                    result["pipeline_error"] = str(e)
            else:
                result["pipeline_success"] = False
                result["pipeline_error"] = "Extraction failed"
            result["step10_verify_time"] = time.time() - step10_start
            
            # Overall metrics
            result["total_time"] = time.time() - start_time
            result["success"] = result["pipeline_success"]
            
            # Calculate efficiency metrics
            result["bits_per_pixel"] = required_bits / result["image_pixels"]
            result["payload_to_image_ratio"] = result["payload_size"] / result["image_file_size"]
            
        except Exception as e:
            result["error"] = str(e)
            result["total_time"] = time.time() - start_time
            
        return result

    def _classify_quality(self, psnr_value: float) -> str:
        """Classify PSNR quality according to research standards"""
        if psnr_value >= 50:
            return "Excellent"
        elif psnr_value >= 45:
            return "Very Good"
        elif psnr_value >= 40:
            return "Good"
        elif psnr_value >= 35:
            return "Acceptable"
        else:
            return "Poor"

    def run_q_factor_analysis(self, test_images: List[Dict], payloads: Dict[int, Dict]) -> List[Dict]:
        """Systematic Q-factor analysis for scientific justification"""
        print(f"\n⚙️  PHASE 3: Q-Factor Scientific Analysis")
        print("-" * 50)
        print(f"Testing Q-factors: {self.q_factors}")
        print(f"Research Question: Why Q=5.0? What's the optimal value?")
        
        q_analysis_results = []
        
        # Use representative test cases for Q-factor analysis
        representative_tests = [
            {"image": test_images[1], "payload_size": 1024},  # Medium image, medium payload
            {"image": test_images[3], "payload_size": 4096},  # Large image, large payload
        ]
        
        method = self.embedding_methods[2]  # DWT+DCT hybrid (current method)
        
        for test_case in representative_tests:
            print(f"\n📊 Testing image: {test_case['image']['name']}")
            print(f"    Payload size: {test_case['payload_size']} bytes")
            
            for q in self.q_factors:
                print(f"  🔧 Q = {q:4.1f}... ", end="", flush=True)
                
                try:
                    result = self.test_single_configuration(
                        test_case['image']['png_path'],
                        payloads[test_case['payload_size']]['content'],
                        method,
                        q
                    )
                    
                    if result['success']:
                        print(f"PSNR: {result['psnr_db']:5.2f} dB ({result['quality_rating']})")
                    else:
                        print(f"FAILED: {result.get('error', 'Unknown error')}")
                    
                    q_analysis_results.append(result)
                    
                except Exception as e:
                    print(f"ERROR: {str(e)}")
                    
        return q_analysis_results

    def run_comprehensive_testing(self):
        """Execute comprehensive testing framework"""
        print(f"\n🚀 STARTING COMPREHENSIVE STEGANOGRAPHY RESEARCH")
        print(f"=" * 60)
        
        # Phase 1: Download images
        test_images = self.download_test_images()
        if not test_images:
            print("❌ No test images available. Aborting.")
            return
            
        # Phase 2: Generate payloads
        payloads = self.generate_test_payloads()
        if not payloads:
            print("❌ No test payloads generated. Aborting.")
            return
            
        # Phase 3: Q-factor analysis
        q_results = self.run_q_factor_analysis(test_images, payloads)
        
        # Phase 4: Method comparison (using Q=5.0)
        print(f"\n🧪 PHASE 4: Embedding Method Comparison Analysis") 
        print("-" * 50)
        
        method_results = []
        q_factor = 5.0  # Standard value for method comparison
        
        # Test subset for method comparison
        test_subset = [
            {"image_idx": 1, "payload_sizes": [512, 2048, 8192]},  # Medium image
            {"image_idx": 3, "payload_sizes": [1024, 4096, 16384]}  # Large image
        ]
        
        for subset in test_subset:
            image = test_images[subset["image_idx"]]
            print(f"\n📊 Testing image: {image['name']} ({image['size']}x{image['size']})")
            
            for payload_size in subset["payload_sizes"]:
                if payload_size not in payloads:
                    continue
                    
                print(f"  📦 Payload: {payload_size} bytes")
                
                for method in self.embedding_methods:
                    print(f"    🔧 {method['name']:15} ... ", end="", flush=True)
                    
                    try:
                        result = self.test_single_configuration(
                            image['png_path'],
                            payloads[payload_size]['content'], 
                            method,
                            q_factor
                        )
                        
                        if result['success']:
                            print(f"PSNR: {result['psnr_db']:5.2f} dB, Time: {result['total_time']:5.2f}s")
                        else:
                            print(f"FAILED: {result.get('error', 'Unknown')}")
                            
                        method_results.append(result)
                        
                    except Exception as e:
                        print(f"ERROR: {str(e)}")
        
        # Phase 5: Generate comprehensive analysis
        self.generate_comprehensive_analysis(test_images, payloads, q_results, method_results)
        
        print(f"\n✅ COMPREHENSIVE RESEARCH COMPLETED")
        print(f"📂 Results saved in: {self.output_dir}")
        
        return {
            "test_images": test_images,
            "payloads": payloads, 
            "q_analysis": q_results,
            "method_comparison": method_results,
            "output_directory": self.output_dir
        }

    def generate_comprehensive_analysis(self, test_images, payloads, q_results, method_results):
        """Generate comprehensive research analysis and visualizations"""
        print(f"\n📊 PHASE 5: Generating Comprehensive Analysis")
        print("-" * 50)
        
        # Generate detailed research report
        report_path = f"{self.output_dir}/COMPREHENSIVE_RESEARCH_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# Comprehensive Steganography Research Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Experiment ID:** {self.experiment_id}\n\n")
            
            f.write("## Research Objectives\n\n")
            f.write("1. **Image Size Impact**: How do different image dimensions affect embedding capacity and quality?\n")
            f.write("2. **Payload Scaling**: What are the optimal payload-to-image size ratios?\n") 
            f.write("3. **Method Comparison**: How do DWT, DCT, and hybrid approaches compare?\n")
            f.write("4. **Q-Factor Optimization**: Scientific justification for Q=5.0 vs other values\n")
            f.write("5. **Process Efficiency**: Detailed analysis of processing overheads\n\n")
            
            # Q-Factor Analysis Section
            f.write("## Q-Factor Scientific Analysis\n\n")
            f.write("### Research Question: Why Q=5.0?\n\n")
            
            if q_results:
                # Group results by Q-factor
                q_grouped = {}
                for result in q_results:
                    if result['success']:
                        q = result['q_factor']
                        if q not in q_grouped:
                            q_grouped[q] = []
                        q_grouped[q].append(result)
                
                f.write("| Q-Factor | Avg PSNR (dB) | Quality Rating | Success Rate | Avg Time (s) |\n")
                f.write("|----------|---------------|----------------|--------------|---------------|\n")
                
                for q in sorted(q_grouped.keys()):
                    results = q_grouped[q]
                    avg_psnr = np.mean([r['psnr_db'] for r in results])
                    success_rate = len(results) / len([r for r in q_results if r['q_factor'] == q])
                    avg_time = np.mean([r['total_time'] for r in results])
                    quality = self._classify_quality(avg_psnr)
                    
                    f.write(f"| {q:6.1f} | {avg_psnr:11.2f} | {quality:14} | {success_rate:9.1%} | {avg_time:11.2f} |\n")
                
                f.write("\n### Q-Factor Analysis Conclusions:\n\n")
                
                # Find optimal Q-factor
                best_q = None
                best_score = 0
                for q in sorted(q_grouped.keys()):
                    results = q_grouped[q]
                    avg_psnr = np.mean([r['psnr_db'] for r in results])
                    success_rate = len(results) / len([r for r in q_results if r['q_factor'] == q])
                    
                    # Scoring: balance PSNR and reliability
                    score = avg_psnr * success_rate
                    if score > best_score:
                        best_score = score
                        best_q = q
                
                f.write(f"- **Optimal Q-Factor: {best_q}** (best balance of quality and reliability)\n")
                f.write(f"- **Q=5.0 Performance**: Widely used standard providing good quality-reliability tradeoff\n")
                
                # Compare Q=5.0 to optimal
                if 5.0 in q_grouped:
                    q5_results = q_grouped[5.0]
                    q5_psnr = np.mean([r['psnr_db'] for r in q5_results])
                    f.write(f"- **Q=5.0 Average PSNR**: {q5_psnr:.2f} dB\n")
                    
                if best_q and best_q != 5.0 and best_q in q_grouped:
                    best_results = q_grouped[best_q] 
                    best_psnr = np.mean([r['psnr_db'] for r in best_results])
                    f.write(f"- **Q={best_q} Average PSNR**: {best_psnr:.2f} dB (difference: {best_psnr-q5_psnr:+.2f} dB)\n")
            
            # Method Comparison Section
            f.write("\n## Embedding Method Comparison\n\n")
            
            if method_results:
                method_grouped = {}
                for result in method_results:
                    if result['success']:
                        method = result['method']
                        if method not in method_grouped:
                            method_grouped[method] = []
                        method_grouped[method].append(result)
                
                f.write("| Method | Tests | Avg PSNR (dB) | Success Rate | Avg Time (s) | Avg Capacity Util |\n")
                f.write("|--------|-------|---------------|--------------|--------------|--------------------|\n")
                
                for method_name in method_grouped:
                    results = method_grouped[method_name]
                    total_tests = len([r for r in method_results if r['method'] == method_name])
                    avg_psnr = np.mean([r['psnr_db'] for r in results])
                    success_rate = len(results) / total_tests
                    avg_time = np.mean([r['total_time'] for r in results])
                    avg_capacity = np.mean([r['capacity_utilization'] for r in results])
                    
                    f.write(f"| {method_name:14} | {len(results):5} | {avg_psnr:11.2f} | {success_rate:9.1%} | {avg_time:10.2f} | {avg_capacity:16.3f} |\n")
            
            # Detailed Process Analysis
            f.write("\n## Detailed Process Analysis\n\n")
            f.write("### Processing Stage Breakdown\n\n")
            
            if method_results:
                # Analyze successful results
                successful = [r for r in method_results if r['success']]
                
                if successful:
                    f.write("| Stage | Avg Time (s) | % of Total | Description |\n")
                    f.write("|-------|--------------|------------|-------------|\n")
                    
                    stages = [
                        ('step1_load_time', 'Image Loading'),
                        ('step2_encrypt_time', 'Encryption'), 
                        ('step3_compress_time', 'Compression'),
                        ('step4_transform_time', 'Frequency Transform'),
                        ('step6_embed_time', 'Embedding'),
                        ('step7_reconstruct_time', 'Reconstruction'),
                        ('step8_quality_time', 'Quality Analysis'),
                        ('step9_extract_time', 'Extraction'),
                        ('step10_verify_time', 'Verification')
                    ]
                    
                    total_avg_time = np.mean([r['total_time'] for r in successful])
                    
                    for stage_key, stage_name in stages:
                        if stage_key in successful[0]:
                            avg_time = np.mean([r.get(stage_key, 0) for r in successful])
                            percentage = (avg_time / total_avg_time) * 100
                            f.write(f"| {stage_name:20} | {avg_time:10.3f} | {percentage:8.1f}% | Processing stage |\n")
                
                # Size analysis  
                f.write("\n### Data Size Analysis\n\n")
                f.write("| Payload Size | Encrypted Size | Compressed Size | Compression Ratio | Encryption Overhead |\n")
                f.write("|--------------|----------------|-----------------|-------------------|-----------------------|\n")
                
                # Group by payload size
                size_grouped = {}
                for result in successful:
                    size = result['payload_size']
                    if size not in size_grouped:
                        size_grouped[size] = []
                    size_grouped[size].append(result)
                
                for size in sorted(size_grouped.keys()):
                    results = size_grouped[size]
                    avg_encrypted = np.mean([r['encrypted_size'] for r in results])
                    avg_compressed = np.mean([r['compressed_size'] for r in results])  
                    avg_comp_ratio = np.mean([r['compression_ratio'] for r in results])
                    avg_enc_overhead = np.mean([r['encryption_overhead'] for r in results])
                    
                    f.write(f"| {size:10,} B | {avg_encrypted:12.0f} B | {avg_compressed:13.0f} B | {avg_comp_ratio:15.3f} | {avg_enc_overhead:17.0f} B |\n")
        
        # Generate plots
        self.generate_research_plots(q_results, method_results)
        
        print(f"✅ Comprehensive analysis generated: {report_path}")

    def generate_research_plots(self, q_results, method_results):
        """Generate scientific research plots and visualizations"""
        print("📈 Generating research visualizations...")
        
        # Set scientific plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Plot 1: Q-Factor vs PSNR Analysis
        if q_results:
            successful_q = [r for r in q_results if r['success']]
            if successful_q:
                plt.figure(figsize=(12, 8))
                
                # Group by payload size for different series
                payload_groups = {}
                for result in successful_q:
                    size = result['payload_size']
                    if size not in payload_groups:
                        payload_groups[size] = {'q': [], 'psnr': []}
                    payload_groups[size]['q'].append(result['q_factor'])
                    payload_groups[size]['psnr'].append(result['psnr_db'])
                
                for size, data in payload_groups.items():
                    plt.scatter(data['q'], data['psnr'], label=f'{size} bytes', s=60, alpha=0.7)
                
                plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Excellent Quality (50dB)')
                plt.axhline(y=45, color='orange', linestyle='--', alpha=0.7, label='Good Quality (45dB)')
                plt.axvline(x=5.0, color='green', linestyle='-', alpha=0.8, label='Q=5.0 (Current)')
                
                plt.xlabel('Q-Factor')
                plt.ylabel('PSNR (dB)')
                plt.title('Q-Factor vs PSNR Analysis\nScientific Justification for Optimal Q Value')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(f"{self.output_dir}/plots/q_factor_analysis.png", dpi=300, bbox_inches='tight')
                plt.close()
        
        # Plot 2: Method Comparison
        if method_results:
            successful_methods = [r for r in method_results if r['success']]
            if successful_methods:
                # Group by method
                method_groups = {}
                for result in successful_methods:
                    method = result['method']
                    if method not in method_groups:
                        method_groups[method] = {'psnr': [], 'time': [], 'capacity': []}
                    method_groups[method]['psnr'].append(result['psnr_db'])
                    method_groups[method]['time'].append(result['total_time'])
                    method_groups[method]['capacity'].append(result['capacity_utilization'])
                
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
                
                # PSNR comparison
                methods = list(method_groups.keys())
                psnr_data = [method_groups[m]['psnr'] for m in methods]
                ax1.boxplot(psnr_data, labels=methods)
                ax1.set_ylabel('PSNR (dB)')
                ax1.set_title('PSNR by Embedding Method')
                ax1.tick_params(axis='x', rotation=45)
                
                # Processing time comparison
                time_data = [method_groups[m]['time'] for m in methods]
                ax2.boxplot(time_data, labels=methods)
                ax2.set_ylabel('Processing Time (s)')
                ax2.set_title('Processing Time by Method')
                ax2.tick_params(axis='x', rotation=45)
                
                # Capacity utilization
                capacity_data = [method_groups[m]['capacity'] for m in methods]
                ax3.boxplot(capacity_data, labels=methods)
                ax3.set_ylabel('Capacity Utilization Ratio')
                ax3.set_title('Capacity Efficiency by Method')
                ax3.tick_params(axis='x', rotation=45)
                
                # PSNR vs Processing Time scatter
                for method in methods:
                    data = method_groups[method]
                    ax4.scatter(data['time'], data['psnr'], label=method, s=50, alpha=0.7)
                
                ax4.set_xlabel('Processing Time (s)')
                ax4.set_ylabel('PSNR (dB)')
                ax4.set_title('Quality vs Speed Tradeoff')
                ax4.legend()
                
                plt.tight_layout()
                plt.savefig(f"{self.output_dir}/plots/method_comparison.png", dpi=300, bbox_inches='tight')
                plt.close()
        
        print("✅ Research plots generated")

if __name__ == "__main__":
    # Initialize comprehensive research framework
    research = ComprehensiveSteganographyResearch()
    
    # Run complete research study
    results = research.run_comprehensive_testing()
    
    print(f"\n🎯 RESEARCH COMPLETE")
    print(f"📊 Check results in: {research.output_dir}")
    print(f"📈 Analysis plots in: {research.output_dir}/plots/")
    print(f"📝 Full report: {research.output_dir}/COMPREHENSIVE_RESEARCH_REPORT.md")