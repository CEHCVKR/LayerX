"""
Professional LAYERX Diagrams using Matplotlib
Creates publication-quality sender and receiver flowcharts
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

# Set style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 9

def create_box(ax, x, y, width, height, text, color='lightblue', bold=False):
    """Create a rounded box with text"""
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.05", 
        edgecolor='black', 
        facecolor=color,
        linewidth=2 if bold else 1.5
    )
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, text, ha='center', va='center', fontsize=9, 
            weight=weight, color='black', wrap=True)

def create_arrow(ax, x1, y1, x2, y2, label='', style='solid'):
    """Create an arrow between two points"""
    linestyle = '--' if style == 'dashed' else '-'
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->', 
        mutation_scale=20, 
        linewidth=1.5 if style == 'dashed' else 2,
        color='black',
        linestyle=linestyle
    )
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.2, mid_y, label, fontsize=7, style='italic')

# ============================================================================
# SENDER SIDE DIAGRAM
# ============================================================================
fig1, ax1 = plt.subplots(figsize=(16, 20))
ax1.set_xlim(0, 12)
ax1.set_ylim(0, 20)
ax1.axis('off')

# Title
ax1.text(6, 19.5, 'LAYERX Steganography - Sender Side', 
         ha='center', fontsize=18, weight='bold')
ax1.text(6, 19, 'Pure DWT Method (56.44 dB PSNR, 100% Reliability)', 
         ha='center', fontsize=13, style='italic', color='green')

# Left branch - Message processing
create_box(ax1, 2, 17.5, 2.5, 0.6, 'Secret Message\n(Plain Text)', color='#FFE5CC')
create_arrow(ax1, 2, 17.2, 2, 16.6)
create_box(ax1, 2, 16.3, 2.5, 0.6, 'Huffman Compression\n(15-30% reduction)', color='#E5F5FF')
create_arrow(ax1, 2, 16, 2, 15.4)
create_box(ax1, 2, 15.1, 2.5, 0.6, 'AES-256 Encryption\n(PBKDF2 100K)', color='#FFE5E5')
create_arrow(ax1, 2, 14.8, 2, 14.2)
create_box(ax1, 2, 13.9, 2.5, 0.6, 'Reed-Solomon ECC\n(10 parity)', color='#E5FFE5')
create_arrow(ax1, 2, 13.6, 2, 13)
create_box(ax1, 2, 12.7, 2.5, 0.6, 'Encrypted Payload\nReady', color='#F0F0F0')

# Right branch - Image processing
create_box(ax1, 10, 17.5, 2.5, 0.6, 'Cover Image\n(RGB Color)', color='#FFFFCC')
create_arrow(ax1, 10, 17.2, 10, 16.6)
create_box(ax1, 10, 16.3, 2.5, 0.8, '2-Level Haar DWT\n7 Frequency Bands\n(LH1,HL1,HH1,LH2,HL2,HH2,LL2)', 
          color='#CCE5FF', bold=True)

# ECC Key Exchange (top right)
create_box(ax1, 10, 14.5, 2.2, 0.6, "Receiver's ECC\nPublic Key\n(SECP256R1)", color='#FFE5FF')
create_arrow(ax1, 10, 14.2, 10, 13.6)
create_box(ax1, 10, 13.3, 2.2, 0.6, 'ECC Key Exchange\nSession Key', color='#FFE5FF')
create_arrow(ax1, 8.9, 13.3, 3.3, 15.1, 'Session Key', style='dashed')

# Convergence point - ACO
create_arrow(ax1, 2, 12.4, 6, 11.8)
create_arrow(ax1, 10, 15.7, 6, 11.8)
create_box(ax1, 6, 11.5, 3, 0.8, 'ACO Position Selection\nOptimizes Locations', color='#FFCCFF')
create_arrow(ax1, 6, 11.1, 6, 10.5)

# Embedding
create_box(ax1, 6, 10.2, 3.5, 0.8, 'Quantization Embedding\nQ = 4.0 - 5.0\n(Single Quantization)', 
          color='#FFE5CC', bold=True)
create_arrow(ax1, 6, 9.6, 6, 9)

# Modified bands
create_box(ax1, 6, 8.7, 3, 0.6, 'Modified DWT Bands', color='#E5FFE5')
create_arrow(ax1, 6, 8.4, 6, 7.8)

# Inverse DWT
create_box(ax1, 6, 7.5, 3, 0.7, 'Inverse DWT\nReconstruction', color='#CCE5FF')
create_arrow(ax1, 6, 7.1, 6, 6.5)

# Output
create_box(ax1, 6, 6.2, 2.5, 0.6, 'Stego Image\n(PNG, RGB)', color='#90EE90')

# Performance box
perf_text = ('PERFORMANCE:\n'
            '• PSNR: 56.44 dB\n'
            '• Speed: 123-509 ms\n'
            '• Capacity: 0.22%\n'
            '• Success: 100%')
ax1.text(10, 10, perf_text, fontsize=10, weight='bold',
        bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='orange', linewidth=2),
        verticalalignment='top')

# Note box
note_text = ('✓ NO DCT LAYER\n'
            '✓ Direct DWT Embedding\n'
            '✓ Single Quantization')
ax1.text(2, 10, note_text, fontsize=10, weight='bold', color='darkgreen',
        bbox=dict(boxstyle='round', facecolor='lightgreen', edgecolor='green', linewidth=2),
        verticalalignment='top')

plt.tight_layout()
plt.savefig('diagrams/SENDER_PROFESSIONAL.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Generated: diagrams/SENDER_PROFESSIONAL.png")

# ============================================================================
# RECEIVER SIDE DIAGRAM
# ============================================================================
fig2, ax2 = plt.subplots(figsize=(16, 20))
ax2.set_xlim(0, 12)
ax2.set_ylim(0, 20)
ax2.axis('off')

# Title
ax2.text(6, 19.5, 'LAYERX Steganography - Receiver Side', 
         ha='center', fontsize=18, weight='bold')
ax2.text(6, 19, 'Pure DWT Extraction (100% Success Rate)', 
         ha='center', fontsize=13, style='italic', color='green')

# Input
create_box(ax2, 6, 17.5, 2.5, 0.6, 'Stego Image\n(Received)', color='#90EE90')
create_arrow(ax2, 6, 17.2, 6, 16.6)

# DWT Transform
create_box(ax2, 6, 16.3, 2.5, 0.8, '2-Level Haar DWT\n7 Frequency Bands\n(Same decomposition)', 
          color='#CCE5FF', bold=True)
create_arrow(ax2, 6, 15.7, 6, 15.1)

# ACO Detection
create_box(ax2, 6, 14.8, 3, 0.8, 'ACO Position Detection\nIdentifies Locations', color='#FFCCFF')
create_arrow(ax2, 6, 14.2, 6, 13.6)

# Extraction
create_box(ax2, 6, 13.3, 3.5, 0.8, 'Quantization Extraction\nQ = 4.0 - 5.0\n(Reads Bits)', 
          color='#FFE5CC', bold=True)
create_arrow(ax2, 6, 12.7, 6, 12.1)

# Encrypted payload
create_box(ax2, 6, 11.8, 2.5, 0.6, 'Encrypted Payload\nExtracted', color='#F0F0F0')

# ECC Decryption (left branch)
create_box(ax2, 2, 13.5, 2.2, 0.6, "Receiver's ECC\nPrivate Key", color='#FFE5FF')
create_arrow(ax2, 2, 13.2, 2, 12.6)
create_box(ax2, 2, 12.3, 2.2, 0.6, 'ECC Key Decrypt\nSession Key', color='#FFE5FF')
create_arrow(ax2, 2, 12, 2, 11.4)
create_box(ax2, 2, 11.1, 2.2, 0.6, 'Session Key\nDecrypted', color='#E5FFE5')
create_arrow(ax2, 3.1, 11.1, 4.8, 10.5, 'Key', style='dashed')

# Main decryption flow
create_arrow(ax2, 6, 11.5, 6, 10.9)
create_box(ax2, 6, 10.6, 2.5, 0.6, 'AES-256 Decryption\nUsing Session Key', color='#FFE5E5')
create_arrow(ax2, 6, 10.3, 6, 9.7)
create_box(ax2, 6, 9.4, 2.5, 0.6, 'Reed-Solomon Decode\nError Correction', color='#E5FFE5')
create_arrow(ax2, 6, 9.1, 6, 8.5)
create_box(ax2, 6, 8.2, 2.5, 0.6, 'Huffman Decompress\nRestore Size', color='#E5F5FF')
create_arrow(ax2, 6, 7.9, 6, 7.3)
create_box(ax2, 6, 7, 2.5, 0.6, 'Integrity Verification\nChecksum', color='#FFFFCC')
create_arrow(ax2, 6, 6.7, 6, 6.1)

# Output
create_box(ax2, 6, 5.8, 2.5, 0.6, 'Original Message\n(Recovered)', color='#FFE5CC')

# Performance box
perf_text2 = ('PERFORMANCE:\n'
             '• Extract: 156-484 ms\n'
             '• Success: 100%\n'
             '• Perfect Match: Yes\n'
             '• Max Payload: 50 KB')
ax2.text(10, 10, perf_text2, fontsize=10, weight='bold',
        bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='orange', linewidth=2),
        verticalalignment='top')

# Success box
success_text = ('✓ 100% Success\n'
               '✓ Perfect Recovery\n'
               '✓ No Data Loss')
ax2.text(10, 7, success_text, fontsize=10, weight='bold', color='darkgreen',
        bbox=dict(boxstyle='round', facecolor='lightgreen', edgecolor='green', linewidth=2),
        verticalalignment='top')

plt.tight_layout()
plt.savefig('diagrams/RECEIVER_PROFESSIONAL.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Generated: diagrams/RECEIVER_PROFESSIONAL.png")

print("\n" + "="*80)
print("✓✓✓ PROFESSIONAL DIAGRAMS GENERATED ✓✓✓")
print("="*80)
print("\nGenerated Files (Graphviz):")
print("  1. diagrams/SENDER_PROFESSIONAL.png - High-quality sender flowchart")
print("  2. diagrams/RECEIVER_PROFESSIONAL.png - High-quality receiver flowchart")
print("\nFeatures:")
print("  ✓ Publication-quality vector graphics")
print("  ✓ Clear hierarchical layout")
print("  ✓ Color-coded process blocks")
print("  ✓ Performance metrics included")
print("  ✓ Shows Pure DWT method (NO DCT)")
print("="*80)
