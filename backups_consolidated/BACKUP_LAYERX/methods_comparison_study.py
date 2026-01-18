"""
Embedding Methods Comparison Study
====================================

Systematic comparison of steganography embedding methods:
1. DWT Only (Discrete Wavelet Transform)
2. DCT Only (Discrete Cosine Transform) 
3. DWT+DCT Hybrid (Current method)
4. Color vs Grayscale implementations

Research Goals:
- Which method provides best quality-capacity tradeoff?
- How do methods scale with payload size?
- What are the computational differences?
- When should each method be preferred?
"""

import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import cv2

# Import core modules
import sys
sys.path.append('core_modules')
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

class EmbeddingMethodsComparison:
    """
    Comprehensive comparison of steganography embedding methods.
    
    Methods Tested:
    1. Pure DWT: Embedding only in DWT high-frequency bands
    2. Pure DCT: Embedding only in DCT coefficients of LL2 band  
    3. Hybrid DWT+DCT: Combined approach (current method)
    4. Color variants: RGB channel implementations
    """
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"methods_comparison_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/plots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/data", exist_ok=True)
        os.makedirs(f"{self.output_dir}/test_images", exist_ok=True)
        
        # Define embedding methods for systematic testing
        self.embedding_methods = [
            {
                "name": "DWT_Only_Grayscale",
                "description": "Pure DWT embedding in high-frequency bands (HH, HL, LH)",
                "implementation": "dwt_only_grayscale",
                "use_dct": False,
                "color": False,
                "bands": ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2"],
                "theoretical_capacity_multiplier": 6  # 6 bands
            },
            {
                "name": "DCT_Only_Grayscale", 
                "description": "Pure DCT embedding in LL2 band coefficients",
                "implementation": "dct_only_grayscale",
                "use_dct": True,
                "color": False,
                "bands": ["LL2_DCT"],
                "theoretical_capacity_multiplier": 1  # 1 band
            },
            {
                "name": "DWT_DCT_Hybrid_Grayscale",
                "description": "Hybrid DWT+DCT embedding (current standard method)",
                "implementation": "hybrid_grayscale",
                "use_dct": True,
                "color": False,
                "bands": ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2", "LL2_DCT"],
                "theoretical_capacity_multiplier": 7  # 6 DWT + 1 DCT
            },
            {
                "name": "DWT_Only_Color",
                "description": "Color DWT embedding across RGB channels",
                "implementation": "dwt_only_color",
                "use_dct": False,
                "color": True,
                "bands": ["RGB_HH1", "RGB_HL1", "RGB_LH1", "RGB_HH2", "RGB_HL2", "RGB_LH2"],
                "theoretical_capacity_multiplier": 18  # 6 bands × 3 channels
            },
            {
                "name": "DWT_DCT_Hybrid_Color",
                "description": "Color hybrid DWT+DCT embedding",
                "implementation": "hybrid_color",
                "use_dct": True,
                "color": True, 
                "bands": ["RGB_ALL"],
                "theoretical_capacity_multiplier": 21  # 7 bands × 3 channels
            }
        ]
        
        # Test configurations
        self.test_images = []  # Will be populated
        self.payload_sizes = [128, 512, 2048, 8192, 32768, 131072]  # Systematic progression
        self.q_factor = 5.0  # Standard Q-factor for method comparison
        
        self.results = []
        
        print(f"🔬 EMBEDDING METHODS COMPARISON STUDY")
        print(f"=" * 50)
        print(f"📊 Methods to test: {len(self.embedding_methods)}")
        print(f"📦 Payload sizes: {len(self.payload_sizes)}")
        print(f"⚙️  Q-factor: {self.q_factor}")
        print(f"📂 Output directory: {self.output_dir}")

    def create_diverse_test_images(self):
        """Create diverse test images for comprehensive method testing"""
        print("\n📷 Creating Diverse Test Images...")
        
        test_configs = [
            {
                "name": "smooth_gradient",
                "description": "Smooth gradient (low frequency content)",
                "type": "low_frequency",
                "generator": self._create_smooth_image
            },
            {
                "name": "high_texture", 
                "description": "High texture (high frequency content)",
                "type": "high_frequency",
                "generator": self._create_textured_image
            },
            {
                "name": "mixed_content",
                "description": "Mixed smooth and textured regions",
                "type": "mixed_frequency",
                "generator": self._create_mixed_image
            },
            {
                "name": "geometric_patterns",
                "description": "Geometric patterns and edges",
                "type": "edge_rich",
                "generator": self._create_geometric_image
            }
        ]
        
        for config in test_configs:
            # Create grayscale version
            gray_image = config["generator"](color=False)
            gray_path = f"{self.output_dir}/test_images/{config['name']}_gray.png"
            cv2.imwrite(gray_path, gray_image)
            
            # Create color version
            color_image = config["generator"](color=True)
            color_path = f"{self.output_dir}/test_images/{config['name']}_color.png"
            cv2.imwrite(color_path, color_image)
            
            self.test_images.append({
                "name": config["name"],
                "description": config["description"],
                "type": config["type"],
                "gray_path": gray_path,
                "color_path": color_path,
                "gray_shape": gray_image.shape,
                "color_shape": color_image.shape
            })
            
            print(f"  ✅ {config['name']}: {gray_image.shape} (gray), {color_image.shape} (color)")
        
        print(f"✅ Created {len(self.test_images)} diverse test image pairs")
        return self.test_images

    def _create_smooth_image(self, color=False, size=512):
        """Create smooth gradient image"""
        if color:
            image = np.zeros((size, size, 3), dtype=np.uint8)
            # Smooth gradients in different channels
            for i in range(size):
                for j in range(size):
                    image[i, j, 0] = int(128 + 100 * np.sin(i/80) * np.cos(j/80))  # Red
                    image[i, j, 1] = int(128 + 80 * np.cos(i/60) * np.sin(j/60))   # Green  
                    image[i, j, 2] = int(128 + 60 * np.sin(i/40) * np.sin(j/40))   # Blue
        else:
            image = np.zeros((size, size), dtype=np.uint8)
            for i in range(size):
                for j in range(size):
                    image[i, j] = int(128 + 100 * np.sin(i/50) * np.cos(j/50))
        return image

    def _create_textured_image(self, color=False, size=512):
        """Create high texture image"""
        np.random.seed(42)  # Reproducible
        if color:
            image = np.random.randint(50, 200, (size, size, 3), dtype=np.uint8)
            # Add structured noise
            for i in range(0, size, 4):
                for j in range(0, size, 4):
                    if (i + j) % 8 == 0:
                        image[i:i+2, j:j+2] = [255, 255, 255]
        else:
            image = np.random.randint(50, 200, (size, size), dtype=np.uint8)
            # Add structured patterns
            for i in range(0, size, 4):
                for j in range(0, size, 4):
                    if (i + j) % 8 == 0:
                        image[i:i+2, j:j+2] = 255
        return image

    def _create_mixed_image(self, color=False, size=512):
        """Create mixed content image"""
        smooth = self._create_smooth_image(color, size)
        textured = self._create_textured_image(color, size)
        
        if color:
            mixed = np.zeros((size, size, 3), dtype=np.uint8)
            mixed[:size//2, :size//2] = smooth[:size//2, :size//2]
            mixed[size//2:, size//2:] = textured[size//2:, size//2:]
            mixed[:size//2, size//2:] = (smooth[:size//2, size//2:] + textured[:size//2, size//2:]) // 2
            mixed[size//2:, :size//2] = (smooth[size//2:, :size//2] + textured[size//2:, :size//2]) // 2
        else:
            mixed = np.zeros((size, size), dtype=np.uint8)
            mixed[:size//2, :size//2] = smooth[:size//2, :size//2]
            mixed[size//2:, size//2:] = textured[size//2:, size//2:]
            mixed[:size//2, size//2:] = (smooth[:size//2, size//2:] + textured[:size//2, size//2:]) // 2
            mixed[size//2:, :size//2] = (smooth[size//2:, :size//2] + textured[size//2:, :size//2]) // 2
        
        return mixed

    def _create_geometric_image(self, color=False, size=512):
        """Create geometric pattern image"""
        if color:
            image = np.ones((size, size, 3), dtype=np.uint8) * 128
            
            # Draw geometric patterns
            # Rectangles
            cv2.rectangle(image, (50, 50), (200, 150), (255, 0, 0), -1)
            cv2.rectangle(image, (300, 300), (450, 400), (0, 255, 0), -1)
            
            # Circles
            cv2.circle(image, (150, 350), 80, (0, 0, 255), -1)
            cv2.circle(image, (350, 150), 60, (255, 255, 0), -1)
            
            # Lines
            cv2.line(image, (0, size//2), (size, size//2), (255, 255, 255), 5)
            cv2.line(image, (size//2, 0), (size//2, size), (255, 255, 255), 5)
        else:
            image = np.ones((size, size), dtype=np.uint8) * 128
            
            # Draw geometric patterns
            cv2.rectangle(image, (50, 50), (200, 150), 255, -1)
            cv2.rectangle(image, (300, 300), (450, 400), 200, -1)
            cv2.circle(image, (150, 350), 80, 255, -1)
            cv2.circle(image, (350, 150), 60, 180, -1)
            cv2.line(image, (0, size//2), (size, size//2), 255, 5)
            cv2.line(image, (size//2, 0), (size//2, size), 255, 5)
        
        return image

    def test_single_method_configuration(self, method: Dict, image_path: str, 
                                       payload: str, image_name: str, image_type: str) -> Dict:
        """Test single method configuration"""
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "method_name": method["name"],
            "method_description": method["description"],
            "image_name": image_name,
            "image_type": image_type,
            "image_path": image_path,
            "payload_size": len(payload),
            "q_factor": self.q_factor,
            "success": False
        }
        
        try:
            start_time = time.time()
            
            # Load image based on method requirements
            if method["color"]:
                cover_image = read_image_color(image_path)
            else:
                cover_image = read_image(image_path)
            
            result["image_shape"] = cover_image.shape
            result["image_pixels"] = cover_image.shape[0] * cover_image.shape[1]
            
            # Prepare payload (encrypt + compress)
            prepare_start = time.time()
            key = generate_key()
            encrypted_payload, salt, iv = encrypt_message(payload, key)
            result["salt"] = salt
            result["iv"] = iv
            compressed_payload, compression_table = compress_huffman(encrypted_payload)
            payload_bits = bytes_to_bits(compressed_payload)
            result["payload_preparation_time"] = time.time() - prepare_start
            
            result["original_payload_size"] = len(payload)
            result["encrypted_size"] = len(encrypted_payload)
            result["compressed_size"] = len(compressed_payload)
            result["payload_bits"] = len(payload_bits)
            
            # Transform to frequency domain
            transform_start = time.time()
            if method["color"]:
                bands = dwt_decompose_color(cover_image, levels=2)
            else:
                bands = dwt_decompose(cover_image, levels=2)
                
            if method["use_dct"]:
                bands["LL2_DCT"] = dct_on_ll(bands["LL2"])
            result["transform_time"] = time.time() - transform_start
            
            # Calculate capacity based on method
            capacity_start = time.time()
            available_capacity = self._calculate_method_capacity(method, bands)
            result["available_capacity"] = available_capacity
            result["capacity_utilization"] = len(payload_bits) / available_capacity if available_capacity > 0 else float('inf')
            result["theoretical_capacity"] = self._estimate_theoretical_capacity(method, cover_image.shape)
            result["capacity_calculation_time"] = time.time() - capacity_start
            
            # Check if payload fits
            if len(payload_bits) > available_capacity:
                result["error"] = f"Payload too large: {len(payload_bits)} bits > {available_capacity} capacity"
                result["total_time"] = time.time() - start_time
                return result
            
            # Embedding
            embed_start = time.time()
            if method["implementation"] == "dwt_only_grayscale":
                modified_bands = self._embed_dwt_only(payload_bits, bands)
            elif method["implementation"] == "dct_only_grayscale":
                modified_bands = self._embed_dct_only(payload_bits, bands)
            elif method["implementation"] == "hybrid_grayscale":
                modified_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=self.q_factor)
            elif method["implementation"] == "dwt_only_color":
                modified_bands = self._embed_dwt_only_color(payload_bits, bands)
            elif method["implementation"] == "hybrid_color":
                modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=self.q_factor)
            else:
                raise ValueError(f"Unknown implementation: {method['implementation']}")
            
            result["embed_time"] = time.time() - embed_start
            
            # Reconstruction
            reconstruct_start = time.time()
            if method["use_dct"] and "LL2_DCT" in modified_bands:
                modified_bands["LL2"] = idct_on_ll(modified_bands["LL2_DCT"])
                
            if method["color"]:
                stego_image = dwt_reconstruct_color(modified_bands)
            else:
                stego_image = dwt_reconstruct(modified_bands)
                
            result["reconstruct_time"] = time.time() - reconstruct_start
            
            # Quality analysis
            quality_start = time.time()
            if method["color"]:
                # Convert to grayscale for PSNR
                cover_gray = cv2.cvtColor(cover_image, cv2.COLOR_RGB2GRAY)
                stego_gray = cv2.cvtColor(stego_image.astype(np.uint8), cv2.COLOR_RGB2GRAY)
                psnr_value = psnr(cover_gray, stego_gray)
                
                # Also calculate per-channel PSNR
                psnr_r = psnr(cover_image[:,:,0], stego_image[:,:,0].astype(np.uint8))
                psnr_g = psnr(cover_image[:,:,1], stego_image[:,:,1].astype(np.uint8))  
                psnr_b = psnr(cover_image[:,:,2], stego_image[:,:,2].astype(np.uint8))
                result["psnr_red"] = psnr_r
                result["psnr_green"] = psnr_g
                result["psnr_blue"] = psnr_b
                result["psnr_avg_channels"] = (psnr_r + psnr_g + psnr_b) / 3
            else:
                psnr_value = psnr(cover_image, stego_image.astype(np.uint8))
                
            result["psnr"] = psnr_value
            result["quality_rating"] = self._classify_quality(psnr_value)
            result["quality_time"] = time.time() - quality_start
            
            # Extraction
            extract_start = time.time()
            if method["implementation"] == "dwt_only_grayscale":
                extracted_bits = self._extract_dwt_only(modified_bands, len(payload_bits))
            elif method["implementation"] == "dct_only_grayscale":
                extracted_bits = self._extract_dct_only(modified_bands, len(payload_bits))
            elif method["implementation"] == "hybrid_grayscale":
                extracted_bits = extract_from_dwt_bands(modified_bands, len(payload_bits), Q_factor=self.q_factor)
            elif method["implementation"] == "dwt_only_color":
                extracted_bits = self._extract_dwt_only_color(modified_bands, len(payload_bits))
            elif method["implementation"] == "hybrid_color":
                extracted_bits = extract_from_dwt_bands_color(modified_bands, len(payload_bits), Q_factor=self.q_factor)
            
            extracted_payload = bits_to_bytes(extracted_bits)
            result["extract_time"] = time.time() - extract_start
            
            # Verification
            verify_start = time.time()
            extraction_success = extracted_payload == compressed_payload
            result["extraction_success"] = extraction_success
            
            if extraction_success:
                try:
                    decompressed = decompress_huffman(extracted_payload, compression_table)
                    final_message = decrypt_message(decompressed, key, result["salt"], result["iv"])
                    result["pipeline_success"] = final_message == payload
                except Exception as e:
                    result["pipeline_success"] = False
                    result["pipeline_error"] = str(e)
            else:
                result["pipeline_success"] = False
            
            result["verify_time"] = time.time() - verify_start
            result["total_time"] = time.time() - start_time
            result["success"] = result["pipeline_success"]
            
            # Performance metrics
            result["bits_per_pixel"] = len(payload_bits) / result["image_pixels"]
            result["embedding_efficiency"] = len(payload_bits) / result["embed_time"] if result["embed_time"] > 0 else 0
            result["quality_per_time"] = psnr_value / result["total_time"] if result["total_time"] > 0 else 0
            
        except Exception as e:
            result["error"] = str(e)
            result["total_time"] = time.time() - start_time
            
        return result

    def _calculate_method_capacity(self, method: Dict, bands: Dict) -> int:
        """Calculate available capacity for specific method"""
        capacity = 0
        
        if method["implementation"] == "dwt_only_grayscale":
            for band_name in ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2"]:
                if band_name in bands:
                    capacity += bands[band_name].size // int(self.q_factor)
                    
        elif method["implementation"] == "dct_only_grayscale":
            if "LL2_DCT" in bands:
                capacity = bands["LL2_DCT"].size // int(self.q_factor)
                
        elif method["implementation"] == "hybrid_grayscale":
            for band_name in ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2"]:
                if band_name in bands:
                    capacity += bands[band_name].size // int(self.q_factor)
            if "LL2_DCT" in bands:
                capacity += bands["LL2_DCT"].size // int(self.q_factor)
                
        elif method["implementation"] == "dwt_only_color":
            for channel in ['R', 'G', 'B']:
                for band in ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']:
                    band_key = f"{channel}_{band}"
                    if band_key in bands:
                        capacity += bands[band_key].size // int(self.q_factor)
                        
        elif method["implementation"] == "hybrid_color":
            # Color hybrid uses all bands across all channels
            for channel in ['R', 'G', 'B']:
                for band in ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']:
                    band_key = f"{channel}_{band}"
                    if band_key in bands:
                        capacity += bands[band_key].size // int(self.q_factor)
                # Add DCT capacity
                dct_key = f"{channel}_LL2_DCT"
                if dct_key in bands:
                    capacity += bands[dct_key].size // int(self.q_factor)
        
        return capacity

    def _estimate_theoretical_capacity(self, method: Dict, image_shape: tuple) -> int:
        """Estimate theoretical capacity based on image size and method"""
        if len(image_shape) == 2:
            pixels = image_shape[0] * image_shape[1]
        else:
            pixels = image_shape[0] * image_shape[1]
            
        # Rough estimation based on DWT decomposition
        # Level 1: ~1/4 of original for each HF band
        # Level 2: ~1/16 of original for each HF band  
        # DCT: ~1/16 of original (LL2 band)
        
        base_capacity = pixels // (4 * int(self.q_factor))  # Conservative estimate
        return int(base_capacity * method["theoretical_capacity_multiplier"])

    def _embed_dwt_only(self, payload_bits: str, bands: Dict) -> Dict:
        """Embed using only DWT bands (no DCT)"""
        modified_bands = bands.copy()
        bit_index = 0
        
        for band_name in ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2"]:
            if band_name in bands and bit_index < len(payload_bits):
                band = bands[band_name].copy()
                flat_band = band.flatten()
                
                # Embed bits at regular intervals
                step = max(1, len(flat_band) // int(self.q_factor))
                for i in range(0, len(flat_band), step):
                    if bit_index < len(payload_bits):
                        bit_val = int(payload_bits[bit_index])
                        # Simple LSB embedding with quantization
                        flat_band[i] = int(flat_band[i] // self.q_factor) * self.q_factor + bit_val
                        bit_index += 1
                    else:
                        break
                
                modified_bands[band_name] = flat_band.reshape(band.shape)
                
        return modified_bands

    def _extract_dwt_only(self, bands: Dict, payload_length: int) -> str:
        """Extract from DWT bands only"""
        extracted_bits = ""
        
        for band_name in ["HH1", "HL1", "LH1", "HH2", "HL2", "LH2"]:
            if band_name in bands and len(extracted_bits) < payload_length:
                band = bands[band_name]
                flat_band = band.flatten()
                
                step = max(1, len(flat_band) // int(self.q_factor))
                for i in range(0, len(flat_band), step):
                    if len(extracted_bits) < payload_length:
                        bit_val = int(flat_band[i]) % int(self.q_factor)
                        extracted_bits += str(min(bit_val, 1))  # Ensure binary
                    else:
                        break
                        
        return extracted_bits[:payload_length]

    def _embed_dct_only(self, payload_bits: str, bands: Dict) -> Dict:
        """Embed using only DCT coefficients"""
        modified_bands = bands.copy()
        
        if "LL2_DCT" in bands:
            dct_band = bands["LL2_DCT"].copy()
            flat_dct = dct_band.flatten()
            
            bit_index = 0
            step = max(1, len(flat_dct) // int(self.q_factor))
            
            for i in range(0, len(flat_dct), step):
                if bit_index < len(payload_bits):
                    bit_val = int(payload_bits[bit_index])
                    flat_dct[i] = int(flat_dct[i] // self.q_factor) * self.q_factor + bit_val
                    bit_index += 1
                else:
                    break
                    
            modified_bands["LL2_DCT"] = flat_dct.reshape(dct_band.shape)
        
        return modified_bands

    def _extract_dct_only(self, bands: Dict, payload_length: int) -> str:
        """Extract from DCT coefficients only"""
        extracted_bits = ""
        
        if "LL2_DCT" in bands:
            dct_band = bands["LL2_DCT"]
            flat_dct = dct_band.flatten()
            
            step = max(1, len(flat_dct) // int(self.q_factor))
            for i in range(0, len(flat_dct), step):
                if len(extracted_bits) < payload_length:
                    bit_val = int(flat_dct[i]) % int(self.q_factor)
                    extracted_bits += str(min(bit_val, 1))
                else:
                    break
                    
        return extracted_bits[:payload_length]

    def _embed_dwt_only_color(self, payload_bits: str, bands: Dict) -> Dict:
        """Embed using DWT bands in color image"""
        modified_bands = bands.copy()
        bit_index = 0
        
        for channel in ['R', 'G', 'B']:
            for band in ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']:
                band_key = f"{channel}_{band}"
                if band_key in bands and bit_index < len(payload_bits):
                    band_data = bands[band_key].copy()
                    flat_band = band_data.flatten()
                    
                    step = max(1, len(flat_band) // int(self.q_factor))
                    for i in range(0, len(flat_band), step):
                        if bit_index < len(payload_bits):
                            bit_val = int(payload_bits[bit_index])
                            flat_band[i] = int(flat_band[i] // self.q_factor) * self.q_factor + bit_val
                            bit_index += 1
                        else:
                            break
                            
                    modified_bands[band_key] = flat_band.reshape(band_data.shape)
                    
        return modified_bands

    def _extract_dwt_only_color(self, bands: Dict, payload_length: int) -> str:
        """Extract from DWT bands in color image"""
        extracted_bits = ""
        
        for channel in ['R', 'G', 'B']:
            for band in ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']:
                band_key = f"{channel}_{band}"
                if band_key in bands and len(extracted_bits) < payload_length:
                    band_data = bands[band_key]
                    flat_band = band_data.flatten()
                    
                    step = max(1, len(flat_band) // int(self.q_factor))
                    for i in range(0, len(flat_band), step):
                        if len(extracted_bits) < payload_length:
                            bit_val = int(flat_band[i]) % int(self.q_factor)
                            extracted_bits += str(min(bit_val, 1))
                        else:
                            break
                            
        return extracted_bits[:payload_length]

    def _classify_quality(self, psnr_value: float) -> str:
        """Classify PSNR quality"""
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

    def run_comprehensive_methods_comparison(self):
        """Run comprehensive comparison of all embedding methods"""
        print(f"\n🚀 STARTING COMPREHENSIVE METHODS COMPARISON")
        print(f"=" * 60)
        
        # Create test images
        test_images = self.create_diverse_test_images()
        
        # Generate test payloads
        payloads = {}
        for size in self.payload_sizes:
            content = f"Test payload for methods comparison. Size: {size} bytes. " + "X" * (size - 50)
            content = content[:size]
            payloads[size] = content
        
        print(f"\n📦 Generated {len(payloads)} test payloads")
        
        # Run systematic testing
        total_tests = len(self.embedding_methods) * len(test_images) * len(self.payload_sizes)
        test_count = 0
        
        print(f"\n🧪 RUNNING {total_tests} SYSTEMATIC TESTS")
        print("-" * 50)
        
        for method in self.embedding_methods:
            print(f"\n🔧 Method: {method['name']}")
            print(f"   Description: {method['description']}")
            
            for image in test_images:
                print(f"  📷 Image: {image['name']} ({image['type']})")
                
                # Choose correct image path based on method requirements
                image_path = image['color_path'] if method['color'] else image['gray_path']
                
                for payload_size in self.payload_sizes:
                    test_count += 1
                    progress = (test_count / total_tests) * 100
                    print(f"    📦 {payload_size:>6} bytes [{progress:5.1f}%] ... ", end="", flush=True)
                    
                    try:
                        result = self.test_single_method_configuration(
                            method,
                            image_path,
                            payloads[payload_size],
                            image['name'],
                            image['type']
                        )
                        
                        if result['success']:
                            print(f"✅ PSNR: {result['psnr']:5.2f} dB, Time: {result['total_time']:5.2f}s")
                        else:
                            error_msg = result.get('error', 'Unknown error')[:50]
                            print(f"❌ FAILED: {error_msg}")
                            
                        self.results.append(result)
                        
                    except Exception as e:
                        print(f"💥 ERROR: {str(e)[:50]}")
                        self.results.append({
                            'method_name': method['name'],
                            'image_name': image['name'],
                            'payload_size': payload_size,
                            'success': False,
                            'error': str(e)
                        })
        
        print(f"\n✅ Testing completed: {len(self.results)} total results")
        
        # Generate analysis and visualizations
        self.generate_methods_analysis()
        
        return self.results

    def generate_methods_analysis(self):
        """Generate comprehensive analysis of method comparison results"""
        print(f"\n📊 GENERATING METHODS ANALYSIS")
        print("-" * 40)
        
        # Save raw results
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(f"{self.output_dir}/data/methods_comparison_results.csv", index=False)
        
        # Analyze successful results
        successful_results = [r for r in self.results if r.get('success', False)]
        if not successful_results:
            print("❌ No successful results to analyze")
            return
        
        success_df = pd.DataFrame(successful_results)
        
        # Generate summary statistics
        self._generate_method_summary_stats(success_df)
        
        # Generate visualizations
        self._generate_methods_visualizations(success_df)
        
        # Generate comprehensive report
        self._generate_methods_report(success_df)

    def _generate_method_summary_stats(self, df: pd.DataFrame):
        """Generate summary statistics for each method"""
        print("📈 Calculating method performance statistics...")
        
        method_stats = df.groupby('method_name').agg({
            'psnr': ['mean', 'std', 'min', 'max', 'count'],
            'total_time': ['mean', 'std'],
            'capacity_utilization': ['mean', 'std'],
            'embedding_efficiency': ['mean', 'std'],
            'payload_size': ['min', 'max']
        }).round(3)
        
        # Save statistics
        method_stats.to_csv(f"{self.output_dir}/data/method_summary_stats.csv")
        
        # Print summary
        print("\n📊 METHOD PERFORMANCE SUMMARY:")
        print("=" * 80)
        for method in df['method_name'].unique():
            method_data = df[df['method_name'] == method]
            print(f"\n🔧 {method}:")
            print(f"   Tests Completed: {len(method_data)}")
            print(f"   Mean PSNR: {method_data['psnr'].mean():.2f} ± {method_data['psnr'].std():.2f} dB")
            print(f"   PSNR Range: {method_data['psnr'].min():.2f} - {method_data['psnr'].max():.2f} dB")
            print(f"   Mean Processing Time: {method_data['total_time'].mean():.3f} ± {method_data['total_time'].std():.3f} s")
            print(f"   Mean Capacity Utilization: {method_data['capacity_utilization'].mean():.3f}")
            print(f"   Embedding Efficiency: {method_data['embedding_efficiency'].mean():.0f} bits/s")

    def _generate_methods_visualizations(self, df: pd.DataFrame):
        """Generate comprehensive visualization suite"""
        print("📊 Generating method comparison visualizations...")
        
        # Set plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create comprehensive comparison figure
        fig, axes = plt.subplots(3, 3, figsize=(20, 16))
        fig.suptitle('Steganography Methods Comprehensive Comparison', fontsize=16)
        
        # Plot 1: PSNR by Method (Box Plot)
        ax1 = axes[0, 0]
        method_order = df.groupby('method_name')['psnr'].mean().sort_values(ascending=False).index
        sns.boxplot(data=df, x='method_name', y='psnr', order=method_order, ax=ax1)
        ax1.set_title('PSNR Distribution by Method')
        ax1.set_xlabel('Method')
        ax1.set_ylabel('PSNR (dB)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.6, label='50dB')
        ax1.axhline(y=45, color='orange', linestyle='--', alpha=0.6, label='45dB')
        
        # Plot 2: Processing Time by Method
        ax2 = axes[0, 1] 
        time_order = df.groupby('method_name')['total_time'].mean().sort_values().index
        sns.boxplot(data=df, x='method_name', y='total_time', order=time_order, ax=ax2)
        ax2.set_title('Processing Time by Method')
        ax2.set_xlabel('Method')
        ax2.set_ylabel('Time (seconds)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Plot 3: Capacity Utilization by Method
        ax3 = axes[0, 2]
        capacity_order = df.groupby('method_name')['capacity_utilization'].mean().sort_values().index
        sns.boxplot(data=df, x='method_name', y='capacity_utilization', order=capacity_order, ax=ax3)
        ax3.set_title('Capacity Utilization by Method')
        ax3.set_xlabel('Method')
        ax3.set_ylabel('Capacity Utilization Ratio')
        ax3.tick_params(axis='x', rotation=45)
        
        # Plot 4: PSNR vs Payload Size
        ax4 = axes[1, 0]
        for method in df['method_name'].unique():
            method_data = df[df['method_name'] == method]
            payload_psnr = method_data.groupby('payload_size')['psnr'].mean()
            ax4.plot(payload_psnr.index, payload_psnr.values, 'o-', label=method[:15], alpha=0.7)
        ax4.set_title('PSNR vs Payload Size')
        ax4.set_xlabel('Payload Size (bytes)')
        ax4.set_ylabel('PSNR (dB)')
        ax4.set_xscale('log')
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Processing Time vs Payload Size
        ax5 = axes[1, 1]
        for method in df['method_name'].unique():
            method_data = df[df['method_name'] == method]
            payload_time = method_data.groupby('payload_size')['total_time'].mean()
            ax5.plot(payload_time.index, payload_time.values, 'o-', label=method[:15], alpha=0.7)
        ax5.set_title('Processing Time vs Payload Size')
        ax5.set_xlabel('Payload Size (bytes)')
        ax5.set_ylabel('Time (seconds)')
        ax5.set_xscale('log')
        ax5.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax5.grid(True, alpha=0.3)
        
        # Plot 6: Quality vs Speed Tradeoff
        ax6 = axes[1, 2]
        for method in df['method_name'].unique():
            method_data = df[df['method_name'] == method]
            ax6.scatter(method_data['total_time'], method_data['psnr'], 
                       label=method[:15], alpha=0.6, s=30)
        ax6.set_title('Quality vs Speed Tradeoff')
        ax6.set_xlabel('Processing Time (s)')
        ax6.set_ylabel('PSNR (dB)')
        ax6.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax6.grid(True, alpha=0.3)
        
        # Plot 7: Method Performance by Image Type
        ax7 = axes[2, 0]
        image_method_psnr = df.pivot_table(values='psnr', index='image_type', 
                                          columns='method_name', aggfunc='mean')
        if not image_method_psnr.empty:
            sns.heatmap(image_method_psnr, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax7)
            ax7.set_title('Mean PSNR by Image Type and Method')
        
        # Plot 8: Success Rate by Method
        ax8 = axes[2, 1]
        all_results_df = pd.DataFrame(self.results)
        success_rates = all_results_df.groupby('method_name')['success'].agg(['sum', 'count'])
        success_rates['rate'] = success_rates['sum'] / success_rates['count']
        success_rates = success_rates.sort_values('rate', ascending=False)
        
        bars = ax8.bar(range(len(success_rates)), success_rates['rate'])
        ax8.set_title('Success Rate by Method')
        ax8.set_xlabel('Method')
        ax8.set_ylabel('Success Rate')
        ax8.set_xticks(range(len(success_rates)))
        ax8.set_xticklabels([name[:15] for name in success_rates.index], rotation=45)
        ax8.axhline(y=0.95, color='red', linestyle='--', alpha=0.6, label='95%')
        
        # Plot 9: Embedding Efficiency
        ax9 = axes[2, 2]
        efficiency_order = df.groupby('method_name')['embedding_efficiency'].mean().sort_values(ascending=False).index
        sns.boxplot(data=df, x='method_name', y='embedding_efficiency', order=efficiency_order, ax=ax9)
        ax9.set_title('Embedding Efficiency (bits/second)')
        ax9.set_xlabel('Method')
        ax9.set_ylabel('Bits per Second')
        ax9.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/plots/methods_comprehensive_comparison.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate individual focused plots
        self._generate_focused_method_plots(df)
        
        print("✅ Method comparison visualizations generated")

    def _generate_focused_method_plots(self, df: pd.DataFrame):
        """Generate focused individual plots for key comparisons"""
        
        # Method Ranking Plot
        plt.figure(figsize=(12, 8))
        
        # Calculate composite scores
        method_scores = {}
        for method in df['method_name'].unique():
            method_data = df[df['method_name'] == method]
            
            # Normalize metrics (0-1 scale)
            psnr_score = (method_data['psnr'].mean() - 30) / 30  # Assume 30-60 dB range
            time_score = 1 / (1 + method_data['total_time'].mean())  # Inverse time (faster is better)
            capacity_score = 1 - method_data['capacity_utilization'].mean()  # Lower utilization is better
            
            # Weighted composite score
            composite_score = 0.5 * psnr_score + 0.3 * time_score + 0.2 * capacity_score
            method_scores[method] = {
                'composite': composite_score,
                'psnr': psnr_score,
                'time': time_score,
                'capacity': capacity_score,
                'mean_psnr': method_data['psnr'].mean(),
                'mean_time': method_data['total_time'].mean()
            }
        
        # Sort by composite score
        sorted_methods = sorted(method_scores.items(), key=lambda x: x[1]['composite'], reverse=True)
        
        methods = [item[0] for item in sorted_methods]
        scores = [item[1]['composite'] for item in sorted_methods]
        psnr_vals = [item[1]['mean_psnr'] for item in sorted_methods]
        
        # Create bar plot with PSNR annotations
        bars = plt.bar(range(len(methods)), scores, alpha=0.7)
        
        # Annotate bars with PSNR values
        for i, (bar, psnr_val) in enumerate(zip(bars, psnr_vals)):
            plt.annotate(f'{psnr_val:.1f}dB', 
                        (bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01),
                        ha='center', va='bottom', fontsize=10)
        
        plt.title('Steganography Methods Ranking\n(Composite Score: Quality + Speed + Capacity)', 
                 fontsize=14)
        plt.xlabel('Method', fontsize=12)
        plt.ylabel('Composite Performance Score', fontsize=12)
        plt.xticks(range(len(methods)), [m.replace('_', '\n') for m in methods], rotation=45)
        
        # Highlight best method
        bars[0].set_color('gold')
        bars[0].set_edgecolor('darkorange')
        bars[0].set_linewidth(2)
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/plots/methods_ranking.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Method ranking visualization generated")

    def _generate_methods_report(self, df: pd.DataFrame):
        """Generate comprehensive methods comparison report"""
        print("📝 Generating comprehensive methods report...")
        
        report_path = f"{self.output_dir}/METHODS_COMPARISON_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# Steganography Embedding Methods Comparison Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Study ID:** {self.timestamp}\n")
            f.write(f"**Q-Factor Used:** {self.q_factor}\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write("This report presents a comprehensive comparison of steganography embedding methods, ")
            f.write("analyzing their performance across different image types and payload sizes. ")
            f.write("The study evaluates quality (PSNR), processing efficiency, capacity utilization, ")
            f.write("and reliability to determine optimal methods for different use cases.\n\n")
            
            # Methods overview
            f.write("## Methods Evaluated\n\n")
            for i, method in enumerate(self.embedding_methods, 1):
                f.write(f"{i}. **{method['name']}**: {method['description']}\n")
                f.write(f"   - Implementation: {method['implementation']}\n")
                f.write(f"   - Uses DCT: {'Yes' if method['use_dct'] else 'No'}\n")  
                f.write(f"   - Color Support: {'Yes' if method['color'] else 'No'}\n")
                f.write(f"   - Embedding Bands: {', '.join(method['bands'])}\n\n")
            
            # Performance summary
            f.write("## Performance Summary\n\n")
            f.write(f"- **Total Tests Completed:** {len(df)}\n")
            f.write(f"- **Test Images:** {len(self.test_images)} (diverse image types)\n")
            f.write(f"- **Payload Range:** {min(self.payload_sizes)} - {max(self.payload_sizes)} bytes\n")
            f.write(f"- **Overall Success Rate:** {len(df) / len(self.results):.1%}\n\n")
            
            # Detailed method analysis
            f.write("## Detailed Method Analysis\n\n")
            
            for method in df['method_name'].unique():
                method_data = df[df['method_name'] == method]
                f.write(f"### {method}\n\n")
                
                f.write("#### Performance Metrics\n")
                f.write(f"- **Tests Completed:** {len(method_data)}\n")
                f.write(f"- **Mean PSNR:** {method_data['psnr'].mean():.2f} ± {method_data['psnr'].std():.2f} dB\n")
                f.write(f"- **PSNR Range:** {method_data['psnr'].min():.2f} - {method_data['psnr'].max():.2f} dB\n")
                f.write(f"- **Quality Rating:** {self._classify_quality(method_data['psnr'].mean())}\n")
                f.write(f"- **Mean Processing Time:** {method_data['total_time'].mean():.3f} ± {method_data['total_time'].std():.3f} seconds\n")
                f.write(f"- **Capacity Utilization:** {method_data['capacity_utilization'].mean():.3f} ± {method_data['capacity_utilization'].std():.3f}\n")
                f.write(f"- **Embedding Efficiency:** {method_data['embedding_efficiency'].mean():.0f} ± {method_data['embedding_efficiency'].std():.0f} bits/second\n")
                
                # Best/worst performance
                best_psnr = method_data.loc[method_data['psnr'].idxmax()]
                worst_psnr = method_data.loc[method_data['psnr'].idxmin()]
                
                f.write(f"\n#### Performance Range\n")
                f.write(f"- **Best PSNR:** {best_psnr['psnr']:.2f} dB ({best_psnr['image_name']}, {best_psnr['payload_size']} bytes)\n")
                f.write(f"- **Lowest PSNR:** {worst_psnr['psnr']:.2f} dB ({worst_psnr['image_name']}, {worst_psnr['payload_size']} bytes)\n")
                
                # Performance by image type
                f.write(f"\n#### Performance by Image Type\n")
                for img_type in method_data['image_type'].unique():
                    type_data = method_data[method_data['image_type'] == img_type]
                    f.write(f"- **{img_type.replace('_', ' ').title()}:** {type_data['psnr'].mean():.2f} ± {type_data['psnr'].std():.2f} dB\n")
                
                f.write("\n---\n\n")
            
            # Comparative Analysis
            f.write("## Comparative Analysis\n\n")
            
            # Best methods by criteria
            best_psnr_method = df.loc[df['psnr'].idxmax()]['method_name']
            best_psnr_value = df['psnr'].max()
            
            fastest_method = df.groupby('method_name')['total_time'].mean().idxmin()
            fastest_time = df.groupby('method_name')['total_time'].mean().min()
            
            most_efficient_method = df.groupby('method_name')['capacity_utilization'].mean().idxmin()
            best_efficiency = df.groupby('method_name')['capacity_utilization'].mean().min()
            
            f.write("### Best Performing Methods\n\n")
            f.write(f"- **Highest PSNR:** {best_psnr_method} ({best_psnr_value:.2f} dB)\n")
            f.write(f"- **Fastest Processing:** {fastest_method} ({fastest_time:.3f} seconds average)\n") 
            f.write(f"- **Most Capacity Efficient:** {most_efficient_method} ({best_efficiency:.3f} utilization)\n\n")
            
            # Method ranking
            f.write("### Overall Method Ranking\n\n")
            method_avg_psnr = df.groupby('method_name')['psnr'].mean().sort_values(ascending=False)
            
            f.write("Ranked by mean PSNR performance:\n\n")
            for rank, (method, psnr) in enumerate(method_avg_psnr.items(), 1):
                method_data = df[df['method_name'] == method]
                avg_time = method_data['total_time'].mean()
                success_rate = len(method_data) / len([r for r in self.results if r['method_name'] == method])
                
                f.write(f"{rank}. **{method}** - {psnr:.2f} dB (avg time: {avg_time:.2f}s, success: {success_rate:.1%})\n")
            
            # Recommendations
            f.write("\n## Recommendations\n\n")
            
            # Determine best overall method
            top_method = method_avg_psnr.index[0]
            top_psnr = method_avg_psnr.iloc[0]
            
            f.write("### Primary Recommendations\n\n")
            f.write(f"**Best Overall Method:** {top_method}\n")
            f.write(f"- Achieves highest average PSNR: {top_psnr:.2f} dB\n")
            f.write(f"- Consistent performance across image types\n")
            f.write(f"- {self._classify_quality(top_psnr)} quality rating\n\n")
            
            f.write("### Use Case Specific Recommendations\n\n")
            f.write("- **Maximum Quality Required:** Use the highest ranking method regardless of processing time\n")
            f.write("- **Real-time Applications:** Consider faster methods even with slightly lower PSNR\n")
            f.write("- **Large Payloads:** Methods with better capacity efficiency\n")
            f.write("- **Color Images:** Color-specific methods may provide better quality preservation\n\n")
            
            # Future work
            f.write("## Future Research Directions\n\n")
            f.write("1. **Adaptive Method Selection:** Automatically choose method based on image content\n")
            f.write("2. **Hybrid Optimization:** Combine strengths of different methods\n")
            f.write("3. **Payload-Aware Embedding:** Adjust method parameters based on payload characteristics\n")
            f.write("4. **Real-time Performance:** Optimize methods for real-time applications\n")
            f.write("5. **Robustness Testing:** Evaluate methods against various attacks\n\n")
            
            f.write("---\n\n")
            f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis Directory:** {self.output_dir}\n")
        
        print(f"✅ Methods comparison report generated: {report_path}")

if __name__ == "__main__":
    # Initialize methods comparison study
    comparison = EmbeddingMethodsComparison()
    
    # Run comprehensive comparison
    results = comparison.run_comprehensive_methods_comparison()
    
    print(f"\n🎯 METHODS COMPARISON STUDY COMPLETE")
    print(f"📊 Results: {len([r for r in results if r.get('success', False)])} successful tests")
    print(f"📂 Output directory: {comparison.output_dir}")
    print(f"📈 Visualizations: {comparison.output_dir}/plots/")
    print(f"📝 Full report: {comparison.output_dir}/METHODS_COMPARISON_REPORT.md")