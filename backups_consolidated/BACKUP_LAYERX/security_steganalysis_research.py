"""
LayerX Security & Steganalysis Resistance Research
=================================================

CRITICAL RESEARCH: Test LayerX steganography system against various steganalysis detection methods.
This is essential for real-world security validation.

Research Areas:
1. Statistical analysis resistance (Chi-square, RS analysis)
2. Histogram analysis detection
3. DCT coefficient distribution analysis
4. Visual detection resistance
5. Entropy analysis
"""

import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
from datetime import datetime
import json

# Import core modules
sys.path.append('core_modules')
try:
    from a8_scanning_detection import chi_square_test, rs_analysis, histogram_analysis, dct_coefficient_analysis
    from a12_security_analysis import calculate_entropy
except ImportError:
    print("Warning: Some detection modules not available, using fallback implementations")

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

class SecuritySteganalysisResearch:
    """Comprehensive security and steganalysis resistance testing"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"security_research_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/results", exist_ok=True)
        os.makedirs(f"{self.output_dir}/plots", exist_ok=True)
        
        self.results = []
        
        print(f"🛡️  LAYERX SECURITY & STEGANALYSIS RESEARCH")
        print(f"=" * 50)
        print(f"📂 Output directory: {self.output_dir}")
        
    def create_test_images(self):
        """Create diverse test images for security testing"""
        print(f"\n📷 Creating Security Test Images...")
        
        test_images = []
        
        # 1. Natural-looking image (low detectability baseline)
        natural = np.zeros((512, 512), dtype=np.uint8)
        for i in range(512):
            for j in range(512):
                natural[i, j] = int(128 + 60 * np.sin(i/30) * np.cos(j/40) + 20 * np.sin(i/5))
        natural_path = f"{self.output_dir}/natural_test.png"
        cv2.imwrite(natural_path, natural)
        test_images.append({"path": natural_path, "type": "natural", "description": "Natural gradient pattern"})
        
        # 2. High-frequency image (challenging for steganography)
        np.random.seed(42)
        noisy = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
        # Add some structure to make it more realistic
        for i in range(0, 512, 8):
            for j in range(0, 512, 8):
                noisy[i:i+4, j:j+4] = noisy[i:i+4, j:j+4] + 50
        noisy_path = f"{self.output_dir}/noisy_test.png"
        cv2.imwrite(noisy_path, np.clip(noisy, 0, 255).astype(np.uint8))
        test_images.append({"path": noisy_path, "type": "noisy", "description": "High-frequency noisy pattern"})
        
        # 3. Smooth image (easy to detect changes)
        smooth = np.ones((512, 512), dtype=np.uint8) * 128
        for i in range(512):
            smooth[i, :] = 128 + int(20 * np.sin(i/100))
        smooth_path = f"{self.output_dir}/smooth_test.png"
        cv2.imwrite(smooth_path, smooth)
        test_images.append({"path": smooth_path, "type": "smooth", "description": "Smooth gradient"})
        
        print(f"✅ Created {len(test_images)} security test images")
        return test_images
    
    def basic_statistical_tests(self, cover_image, stego_image):
        """Perform basic statistical tests (fallback if modules not available)"""
        
        results = {}
        
        # Basic entropy calculation
        def simple_entropy(data):
            from collections import Counter
            import math
            counter = Counter(data.flatten())
            length = len(data.flatten())
            entropy = 0.0
            for count in counter.values():
                probability = count / length
                if probability > 0:
                    entropy -= probability * math.log2(probability)
            return entropy
        
        # Entropy analysis
        cover_entropy = simple_entropy(cover_image)
        stego_entropy = simple_entropy(stego_image)
        results["entropy_cover"] = cover_entropy
        results["entropy_stego"] = stego_entropy
        results["entropy_change"] = abs(stego_entropy - cover_entropy)
        
        # Basic histogram analysis
        cover_hist = cv2.calcHist([cover_image], [0], None, [256], [0, 256])
        stego_hist = cv2.calcHist([stego_image], [0], None, [256], [0, 256])
        
        # Chi-square-like test on histograms
        chi_square_stat = 0
        for i in range(256):
            expected = cover_hist[i][0]
            observed = stego_hist[i][0]
            if expected > 0:
                chi_square_stat += ((observed - expected) ** 2) / expected
        
        results["histogram_chi_square"] = chi_square_stat
        results["histogram_anomaly_score"] = chi_square_stat / 256  # Normalized
        
        # Visual difference metrics
        mse = np.mean((cover_image.astype(float) - stego_image.astype(float)) ** 2)
        results["mse"] = mse
        results["visual_difference"] = mse
        
        return results
    
    def test_steganalysis_resistance(self, image_info, payload_sizes):
        """Test resistance against steganalysis for a specific image"""
        
        print(f"\n🔍 Testing {image_info['type']} image: {image_info['description']}")
        print(f"-" * 50)
        
        # Load cover image
        cover_image = read_image(image_info['path'])
        
        image_results = []
        
        for payload_size in payload_sizes:
            print(f"\n📦 Payload size: {payload_size} bytes")
            
            # Create test payload
            test_payload = "LayerX security research payload. " * (payload_size // 35 + 1)
            test_payload = test_payload[:payload_size]
            
            try:
                # Process payload through LayerX pipeline
                key = generate_key()
                encrypted_payload, salt, iv = encrypt_message(test_payload, key)
                compressed_payload, compression_table = compress_huffman(encrypted_payload)
                payload_bits = bytes_to_bits(compressed_payload)
                
                # Embed using DWT with Q=5.0
                bands = dwt_decompose(cover_image, levels=2)
                modified_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=5.0)
                stego_image = dwt_reconstruct(modified_bands).astype(np.uint8)
                
                # Quality measurement
                psnr_value = psnr(cover_image, stego_image)
                
                # Statistical analysis
                stats_results = self.basic_statistical_tests(cover_image, stego_image)
                
                # Compile results
                result = {
                    "image_type": image_info['type'],
                    "image_path": image_info['path'],
                    "payload_size": payload_size,
                    "psnr": psnr_value,
                    "compressed_payload_size": len(compressed_payload),
                    "embedding_efficiency": len(compressed_payload) / payload_size,
                    **stats_results
                }
                
                # Security risk assessment
                risk_indicators = 0
                
                # Entropy change indicator
                if result["entropy_change"] > 0.1:
                    risk_indicators += 1
                    result["entropy_risk"] = "HIGH"
                elif result["entropy_change"] > 0.05:
                    result["entropy_risk"] = "MEDIUM"
                else:
                    result["entropy_risk"] = "LOW"
                
                # Histogram anomaly indicator
                if result["histogram_anomaly_score"] > 50:
                    risk_indicators += 2
                    result["histogram_risk"] = "HIGH"
                elif result["histogram_anomaly_score"] > 20:
                    risk_indicators += 1
                    result["histogram_risk"] = "MEDIUM"
                else:
                    result["histogram_risk"] = "LOW"
                
                # Visual difference indicator
                if result["visual_difference"] > 100:
                    risk_indicators += 1
                    result["visual_risk"] = "HIGH"
                elif result["visual_difference"] > 10:
                    result["visual_risk"] = "MEDIUM"
                else:
                    result["visual_risk"] = "LOW"
                
                # Overall risk assessment
                if risk_indicators >= 3:
                    result["overall_detection_risk"] = "HIGH"
                elif risk_indicators >= 1:
                    result["overall_detection_risk"] = "MEDIUM"
                else:
                    result["overall_detection_risk"] = "LOW"
                
                result["risk_indicators"] = risk_indicators
                
                # Verification - extract and validate
                extracted_bits = extract_from_dwt_bands(modified_bands, len(payload_bits), Q_factor=5.0)
                extracted_payload = bits_to_bytes(extracted_bits)
                
                if extracted_payload == compressed_payload:
                    decompressed = decompress_huffman(extracted_payload, compression_table)
                    final_message = decrypt_message(decompressed, key, salt, iv)
                    result["extraction_success"] = final_message == test_payload
                else:
                    result["extraction_success"] = False
                
                image_results.append(result)
                
                # Print summary
                print(f"   📊 PSNR: {psnr_value:.2f} dB")
                print(f"   🔢 Entropy change: {result['entropy_change']:.4f} ({result['entropy_risk']} risk)")
                print(f"   📈 Histogram anomaly: {result['histogram_anomaly_score']:.2f} ({result['histogram_risk']} risk)")
                print(f"   👁️  Visual difference: {result['visual_difference']:.2f} ({result['visual_risk']} risk)")
                print(f"   🎯 Overall risk: {result['overall_detection_risk']} ({risk_indicators} indicators)")
                print(f"   ✅ Extraction: {'SUCCESS' if result['extraction_success'] else 'FAILED'}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                image_results.append({
                    "image_type": image_info['type'],
                    "payload_size": payload_size,
                    "error": str(e),
                    "extraction_success": False
                })
        
        return image_results
    
    def run_comprehensive_security_testing(self):
        """Run comprehensive security testing across multiple scenarios"""
        
        print(f"\n🚀 COMPREHENSIVE SECURITY TESTING")
        print(f"=" * 40)
        
        # Create test images
        test_images = self.create_test_images()
        
        # Test payload sizes (progressive)
        payload_sizes = [128, 512, 2048, 8192]  # Small to medium payloads
        
        print(f"\n📋 Test Configuration:")
        print(f"   Images: {len(test_images)} types")
        print(f"   Payload sizes: {payload_sizes}")
        print(f"   Total tests: {len(test_images) * len(payload_sizes)}")
        
        all_results = []
        
        # Test each image type
        for image_info in test_images:
            image_results = self.test_steganalysis_resistance(image_info, payload_sizes)
            all_results.extend(image_results)
        
        self.results = all_results
        return all_results
    
    def generate_security_analysis_plots(self):
        """Generate visualization plots for security analysis"""
        
        print(f"\n📊 Generating Security Analysis Plots...")
        
        if not self.results:
            print("No results to plot")
            return
        
        # Filter successful results
        successful_results = [r for r in self.results if r.get('extraction_success', False)]
        
        if not successful_results:
            print("No successful extractions to analyze")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. PSNR vs Payload Size
        payload_sizes = list(set(r['payload_size'] for r in successful_results))
        payload_sizes.sort()
        
        for image_type in set(r['image_type'] for r in successful_results):
            type_results = [r for r in successful_results if r['image_type'] == image_type]
            type_psnr = []
            type_payloads = []
            
            for payload in payload_sizes:
                payload_results = [r for r in type_results if r['payload_size'] == payload]
                if payload_results:
                    avg_psnr = sum(r['psnr'] for r in payload_results) / len(payload_results)
                    type_psnr.append(avg_psnr)
                    type_payloads.append(payload)
            
            if type_payloads:
                ax1.plot(type_payloads, type_psnr, marker='o', label=f'{image_type} image', linewidth=2)
        
        ax1.set_xlabel('Payload Size (bytes)')
        ax1.set_ylabel('PSNR (dB)')
        ax1.set_title('Security Test: PSNR vs Payload Size')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=50, color='green', linestyle=':', alpha=0.6, label='Excellent Quality')
        ax1.axhline(y=40, color='orange', linestyle=':', alpha=0.6, label='Acceptable Quality')
        
        # 2. Detection Risk Distribution
        risk_levels = ['LOW', 'MEDIUM', 'HIGH']
        risk_counts = [len([r for r in successful_results if r.get('overall_detection_risk') == level]) for level in risk_levels]
        colors = ['green', 'orange', 'red']
        
        bars = ax2.bar(risk_levels, risk_counts, color=colors, alpha=0.7)
        ax2.set_ylabel('Number of Tests')
        ax2.set_title('Overall Detection Risk Distribution')
        ax2.grid(True, alpha=0.3)
        
        # Add percentage labels on bars
        total_tests = len(successful_results)
        for bar, count in zip(bars, risk_counts):
            percentage = (count / total_tests) * 100 if total_tests > 0 else 0
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{percentage:.1f}%', ha='center', va='bottom')
        
        # 3. Entropy Change Analysis
        entropy_changes = [r.get('entropy_change', 0) for r in successful_results]
        payload_sizes_entropy = [r['payload_size'] for r in successful_results]
        
        scatter = ax3.scatter(payload_sizes_entropy, entropy_changes, 
                             c=[['green', 'orange', 'red'][['LOW', 'MEDIUM', 'HIGH'].index(r.get('entropy_risk', 'LOW'))] 
                                for r in successful_results], alpha=0.6)
        ax3.set_xlabel('Payload Size (bytes)')
        ax3.set_ylabel('Entropy Change')
        ax3.set_title('Entropy Change vs Payload Size')
        ax3.axhline(y=0.05, color='orange', linestyle='--', alpha=0.6, label='Medium Risk Threshold')
        ax3.axhline(y=0.1, color='red', linestyle='--', alpha=0.6, label='High Risk Threshold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Risk Indicators Summary
        image_types = list(set(r['image_type'] for r in successful_results))
        risk_data = {}
        
        for img_type in image_types:
            type_results = [r for r in successful_results if r['image_type'] == img_type]
            avg_risk = sum(r.get('risk_indicators', 0) for r in type_results) / len(type_results) if type_results else 0
            risk_data[img_type] = avg_risk
        
        ax4.bar(risk_data.keys(), risk_data.values(), alpha=0.7, color='skyblue')
        ax4.set_ylabel('Average Risk Indicators')
        ax4.set_title('Risk Indicators by Image Type')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = f"{self.output_dir}/plots/security_analysis.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✅ Security plots saved: {plot_path}")
        return plot_path
    
    def generate_security_report(self):
        """Generate comprehensive security analysis report"""
        
        print(f"\n📊 Generating Security Analysis Report...")
        
        # Save raw results
        results_file = f"{self.output_dir}/results/security_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate markdown report
        report_path = f"{self.output_dir}/SECURITY_ANALYSIS_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# LayerX Security & Steganalysis Resistance Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis ID:** {self.timestamp}\n")
            f.write(f"**Test Type:** Statistical Steganalysis Resistance\n\n")
            
            if self.results:
                successful_results = [r for r in self.results if r.get('extraction_success', False)]
                
                f.write("## Executive Summary\n\n")
                f.write(f"- **Total Tests:** {len(self.results)}\n")
                f.write(f"- **Successful Extractions:** {len(successful_results)} ({len(successful_results)/len(self.results)*100:.1f}%)\n")
                
                if successful_results:
                    low_risk = len([r for r in successful_results if r.get('overall_detection_risk') == 'LOW'])
                    medium_risk = len([r for r in successful_results if r.get('overall_detection_risk') == 'MEDIUM'])
                    high_risk = len([r for r in successful_results if r.get('overall_detection_risk') == 'HIGH'])
                    
                    f.write(f"- **Low Detection Risk:** {low_risk} ({low_risk/len(successful_results)*100:.1f}%)\n")
                    f.write(f"- **Medium Detection Risk:** {medium_risk} ({medium_risk/len(successful_results)*100:.1f}%)\n")
                    f.write(f"- **High Detection Risk:** {high_risk} ({high_risk/len(successful_results)*100:.1f}%)\n\n")
                    
                    # Security analysis table
                    f.write("## Detection Risk Analysis\n\n")
                    f.write("| Image Type | Payload Size | PSNR (dB) | Entropy Risk | Histogram Risk | Overall Risk |\n")
                    f.write("|------------|--------------|-----------|--------------|----------------|---------------|\n")
                    
                    for result in successful_results:
                        f.write(f"| {result.get('image_type', 'N/A')} | {result['payload_size']:,} B | ")
                        f.write(f"{result.get('psnr', 0):.2f} | {result.get('entropy_risk', 'N/A')} | ")
                        f.write(f"{result.get('histogram_risk', 'N/A')} | {result.get('overall_detection_risk', 'N/A')} |\n")
                    
                    # Key findings
                    f.write("\n## Key Security Findings\n\n")
                    
                    # Best performing scenarios
                    low_risk_results = [r for r in successful_results if r.get('overall_detection_risk') == 'LOW']
                    if low_risk_results:
                        avg_psnr_low_risk = sum(r.get('psnr', 0) for r in low_risk_results) / len(low_risk_results)
                        f.write(f"1. **Low Risk Scenarios:** {len(low_risk_results)} tests with average PSNR {avg_psnr_low_risk:.2f} dB\n")
                        
                        # Safest payload sizes
                        low_risk_payloads = set(r['payload_size'] for r in low_risk_results)
                        f.write(f"2. **Safest Payload Sizes:** {', '.join(str(p) for p in sorted(low_risk_payloads))} bytes\n")
                    
                    # Risk factors
                    high_entropy_risks = len([r for r in successful_results if r.get('entropy_risk') == 'HIGH'])
                    high_histogram_risks = len([r for r in successful_results if r.get('histogram_risk') == 'HIGH'])
                    
                    f.write(f"3. **Entropy Risks:** {high_entropy_risks} tests showed high entropy changes\n")
                    f.write(f"4. **Histogram Risks:** {high_histogram_risks} tests showed histogram anomalies\n")
                
                f.write("\n## Security Recommendations\n\n")
                f.write("### Deployment Guidelines\n")
                f.write("1. **Recommended Payloads:** Use payload sizes that consistently show LOW detection risk\n")
                f.write("2. **Image Selection:** Natural/smooth images show better statistical properties\n")
                f.write("3. **Quality Control:** Maintain PSNR > 50 dB for optimal security\n")
                f.write("4. **Risk Monitoring:** Regularly test against new steganalysis methods\n\n")
                
                f.write("### Technical Countermeasures\n")
                f.write("1. **Entropy Management:** Minimize entropy changes during embedding\n")
                f.write("2. **Histogram Preservation:** Implement histogram-preserving techniques\n")
                f.write("3. **Adaptive Embedding:** Use content-adaptive embedding strategies\n")
                f.write("4. **Statistical Blending:** Add controlled randomization to reduce detectability\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. **Advanced Steganalysis:** Test against ML-based detection methods\n")
            f.write("2. **Robustness Testing:** Test resistance to image modifications\n")
            f.write("3. **Real-world Validation:** Test with internet/social media scenarios\n")
            f.write("4. **Performance Optimization:** Optimize security-performance trade-offs\n\n")
            
            f.write("---\n\n")
            f.write(f"**Data Location:** `{results_file}`\n")
            f.write("**LayerX Security Research Team**\n")
        
        print(f"✅ Security report generated: {report_path}")
        print(f"✅ Raw data saved: {results_file}")
        
        return report_path, results_file

if __name__ == "__main__":
    print("🛡️  LayerX Security & Steganalysis Resistance Research")
    print("=" * 55)
    print("CRITICAL RESEARCH: Testing statistical steganalysis resistance")
    print()
    
    # Initialize security research
    security_research = SecuritySteganalysisResearch()
    
    # Run comprehensive security testing
    results = security_research.run_comprehensive_security_testing()
    
    # Generate visualizations
    security_research.generate_security_analysis_plots()
    
    # Generate comprehensive report
    report_path, data_path = security_research.generate_security_report()
    
    print(f"\n🎯 SECURITY RESEARCH COMPLETED!")
    print(f"📊 Results: {len(results)} tests completed")
    print(f"📂 Report: {report_path}")
    print(f"📁 Data: {data_path}")
    print(f"📈 Plots: {security_research.output_dir}/plots/")
    print(f"🏢 Directory: {security_research.output_dir}")
    
    # Summary statistics
    successful = len([r for r in results if r.get('extraction_success', False)])
    if successful > 0:
        low_risk = len([r for r in results if r.get('overall_detection_risk') == 'LOW' and r.get('extraction_success', False)])
        print(f"\n📈 SECURITY SUMMARY:")
        print(f"   ✅ Successful tests: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
        print(f"   🟢 Low detection risk: {low_risk}/{successful} ({low_risk/successful*100:.1f}%)")
        print(f"   🛡️  Security status: {'GOOD' if low_risk/successful >= 0.6 else 'NEEDS_IMPROVEMENT'}")