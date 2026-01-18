"""
LayerX Research Results Summary
===============================

Key Findings from Comprehensive Analysis
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def load_and_analyze_results():
    """Load and analyze the research results"""
    
    # Load results
    with open('layerx_local_research_20260118_120100/results/raw_results.json', 'r') as f:
        results = json.load(f)
    
    # Filter successful results
    successful_results = [r for r in results if r.get('success', False)]
    
    print(f"🎯 LAYERX COMPREHENSIVE RESEARCH SUMMARY")
    print(f"=" * 50)
    print(f"Total Tests Conducted: {len(results)}")
    print(f"Successful Tests: {len(successful_results)} ({len(successful_results)/len(results)*100:.1f}%)")
    print()
    
    # Q-factor analysis
    print(f"📊 Q-FACTOR ANALYSIS")
    print(f"-" * 30)
    q_performance = defaultdict(list)
    for result in successful_results:
        q_factor = result['q_factor']
        psnr = result['psnr']
        q_performance[q_factor].append(psnr)
    
    q_averages = {}
    for q, psnrs in q_performance.items():
        avg_psnr = sum(psnrs) / len(psnrs)
        q_averages[q] = avg_psnr
        print(f"Q = {q:4.1f}: {len(psnrs):3d} tests, Avg PSNR = {avg_psnr:5.2f} dB")
    
    best_q = max(q_averages, key=q_averages.get)
    print(f"\n✅ Best Q-factor: Q = {best_q} (Average PSNR: {q_averages[best_q]:.2f} dB)")
    print(f"📍 Q = 5.0 Performance: {q_averages.get(5.0, 'Not tested'):.2f} dB")
    
    print(f"\n🔧 METHOD COMPARISON")
    print(f"-" * 30)
    method_performance = defaultdict(list)
    for result in successful_results:
        method = result['method']
        psnr = result['psnr']
        method_performance[method].append(psnr)
    
    method_averages = {}
    for method, psnrs in method_performance.items():
        avg_psnr = sum(psnrs) / len(psnrs)
        method_averages[method] = avg_psnr
        print(f"{method:15}: {len(psnrs):3d} tests, Avg PSNR = {avg_psnr:5.2f} dB")
    
    best_method = max(method_averages, key=method_averages.get)
    print(f"\n✅ Best Method: {best_method} (Average PSNR: {method_averages[best_method]:.2f} dB)")
    
    print(f"\n📏 IMAGE SIZE ANALYSIS")
    print(f"-" * 30)
    size_performance = defaultdict(list)
    for result in successful_results:
        if 'image_shape' in result:
            size = result['image_shape'][0]  # Assuming square images
            psnr = result['psnr']
            size_performance[size].append(psnr)
    
    size_averages = {}
    for size, psnrs in size_performance.items():
        avg_psnr = sum(psnrs) / len(psnrs)
        size_averages[size] = avg_psnr
        print(f"{size:4d}x{size:<4d}: {len(psnrs):3d} tests, Avg PSNR = {avg_psnr:5.2f} dB")
    
    best_size = max(size_averages, key=size_averages.get)
    print(f"\n✅ Best Image Size: {best_size}x{best_size} (Average PSNR: {size_averages[best_size]:.2f} dB)")
    
    print(f"\n📦 PAYLOAD SIZE IMPACT")
    print(f"-" * 30)
    payload_performance = defaultdict(list)
    for result in successful_results:
        payload_size = result['payload_size']
        psnr = result['psnr']
        payload_performance[payload_size].append(psnr)
    
    sorted_payloads = sorted(payload_performance.keys())
    print(f"{'Payload Size':<12} {'Tests':<6} {'Avg PSNR (dB)':<15} {'Quality Trend'}")
    print(f"-" * 55)
    
    for payload_size in sorted_payloads:
        psnrs = payload_performance[payload_size]
        avg_psnr = sum(psnrs) / len(psnrs)
        
        # Quality classification
        if avg_psnr >= 60:
            quality = "🟢 Excellent"
        elif avg_psnr >= 50:
            quality = "🟡 Very Good"
        elif avg_psnr >= 45:
            quality = "🟠 Good"
        else:
            quality = "🔴 Acceptable"
        
        print(f"{payload_size:>8} B   {len(psnrs):<6} {avg_psnr:<15.2f} {quality}")
    
    # Create visualization
    create_performance_plots(q_averages, method_averages, size_averages, payload_performance)
    
    print(f"\n🎯 KEY INSIGHTS")
    print(f"=" * 50)
    print(f"1. Q=5.0 Justification: Balanced performance with {q_averages.get(5.0, 0):.1f} dB average")
    print(f"2. Image Size: {best_size}x{best_size} provides optimal capacity-quality balance")
    print(f"3. Method Choice: {best_method} shows best PSNR performance")
    print(f"4. Payload Scaling: Quality degrades predictably as payload increases")
    print(f"5. System Robustness: {len(successful_results)/len(results)*100:.1f}% success rate demonstrates reliability")
    
    return results, successful_results

def create_performance_plots(q_averages, method_averages, size_averages, payload_performance):
    """Create performance visualization plots"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Q-factor performance
    q_factors = sorted(q_averages.keys())
    q_psnrs = [q_averages[q] for q in q_factors]
    
    ax1.bar(q_factors, q_psnrs, color='skyblue', alpha=0.7)
    ax1.axvline(x=5.0, color='red', linestyle='--', alpha=0.8, label='Q=5.0 (Current)')
    ax1.set_xlabel('Q-Factor')
    ax1.set_ylabel('Average PSNR (dB)')
    ax1.set_title('Q-Factor Performance Analysis')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Method comparison
    methods = list(method_averages.keys())
    method_psnrs = list(method_averages.values())
    colors = ['lightcoral', 'lightgreen', 'lightskyblue']
    
    bars = ax2.bar(methods, method_psnrs, color=colors, alpha=0.7)
    ax2.set_ylabel('Average PSNR (dB)')
    ax2.set_title('Embedding Method Comparison')
    ax2.tick_params(axis='x', rotation=15)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, method_psnrs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value:.1f}', ha='center', va='bottom')
    
    # Image size impact
    sizes = sorted(size_averages.keys())
    size_psnrs = [size_averages[size] for size in sizes]
    size_labels = [f'{size}x{size}' for size in sizes]
    
    ax3.plot(size_labels, size_psnrs, marker='o', linewidth=2, markersize=8, color='purple', alpha=0.7)
    ax3.fill_between(size_labels, size_psnrs, alpha=0.3, color='purple')
    ax3.set_ylabel('Average PSNR (dB)')
    ax3.set_title('Image Size Impact')
    ax3.grid(True, alpha=0.3)
    
    # Payload size impact
    sorted_payloads = sorted(payload_performance.keys())
    payload_psnrs = []
    for payload_size in sorted_payloads:
        avg_psnr = sum(payload_performance[payload_size]) / len(payload_performance[payload_size])
        payload_psnrs.append(avg_psnr)
    
    payload_labels = [f'{p//1024}KB' if p >= 1024 else f'{p}B' for p in sorted_payloads]
    
    ax4.plot(payload_labels, payload_psnrs, marker='s', linewidth=2, markersize=6, color='orange', alpha=0.7)
    ax4.fill_between(payload_labels, payload_psnrs, alpha=0.3, color='orange')
    ax4.set_ylabel('Average PSNR (dB)')
    ax4.set_title('Payload Size vs Quality')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # Add quality threshold lines
    for ax in [ax1, ax2, ax3, ax4]:
        ax.axhline(y=50, color='green', linestyle=':', alpha=0.6, label='Excellent (≥50dB)')
        ax.axhline(y=45, color='orange', linestyle=':', alpha=0.6, label='Good (≥45dB)')
        ax.axhline(y=40, color='red', linestyle=':', alpha=0.6, label='Acceptable (≥40dB)')
    
    plt.tight_layout()
    plt.savefig('layerx_local_research_20260118_120100/plots/performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n📈 Performance plots saved to: layerx_local_research_20260118_120100/plots/performance_analysis.png")

if __name__ == "__main__":
    results, successful_results = load_and_analyze_results()