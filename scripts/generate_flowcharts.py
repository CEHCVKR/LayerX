"""
Generate correct LAYERX flowcharts for Pure DWT implementation
Shows actual production flow achieving 56.44 dB PSNR
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

def create_box(ax, x, y, width, height, text, color='lightblue', textcolor='black'):
    """Create a rounded box with text"""
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.1", 
        edgecolor='black', 
        facecolor=color,
        linewidth=2
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, 
            weight='bold', color=textcolor, wrap=True)

def create_arrow(ax, x1, y1, x2, y2, label=''):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->', 
        mutation_scale=20, 
        linewidth=2,
        color='black'
    )
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=8, style='italic')

# ============================================================================
# SENDER/EMBEDDING FLOWCHART
# ============================================================================
fig1, ax1 = plt.subplots(figsize=(12, 14))
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 15)
ax1.axis('off')

# Title
ax1.text(5, 14.5, 'LAYERX SENDER - Pure DWT Embedding', 
         ha='center', fontsize=16, weight='bold')
ax1.text(5, 14, 'PSNR: 56.44 dB | Reliability: 100%', 
         ha='center', fontsize=11, style='italic', color='green')

# Start - Secret Message
create_box(ax1, 5, 13, 2.5, 0.6, 'SECRET MESSAGE', color='#FFE5CC')
create_arrow(ax1, 5, 12.7, 5, 12.3)

# Huffman Compression
create_box(ax1, 5, 12, 2.5, 0.6, 'HUFFMAN\nCOMPRESSION', color='#E5F5FF')
ax1.text(7.8, 12, 'Reduces size\n15-30%', fontsize=8, style='italic')
create_arrow(ax1, 5, 11.7, 5, 11.3)

# AES-256 Encryption
create_box(ax1, 5, 11, 2.5, 0.6, 'AES-256\nENCRYPTION', color='#FFE5E5')
ax1.text(7.8, 11, 'PBKDF2\n100K iterations', fontsize=8, style='italic')
create_arrow(ax1, 5, 10.7, 5, 10.3)

# Reed-Solomon ECC
create_box(ax1, 5, 10, 2.5, 0.6, 'REED-SOLOMON ECC', color='#E5FFE5')
ax1.text(7.8, 10, '10 parity\nsymbols', fontsize=8, style='italic')
create_arrow(ax1, 5, 9.7, 5, 9.3)

# Encrypted Payload
create_box(ax1, 5, 9, 2.5, 0.6, 'Encrypted Payload', color='#F0F0F0')
ax1.text(7.8, 9, 'Compressed\n+ Protected', fontsize=8, style='italic')

# Cover Image (parallel path)
create_box(ax1, 2, 9, 2, 0.6, 'COVER IMAGE\n(RGB)', color='#FFFFCC')

# Both converge to DWT
create_arrow(ax1, 5, 8.7, 5, 8)
create_arrow(ax1, 2, 8.7, 3.2, 8)

# DWT Transform
create_box(ax1, 5, 7.7, 3.5, 0.8, '2-LEVEL HAAR DWT\nTRANSFORM', color='#CCE5FF')
ax1.text(8.8, 7.7, '✓ NO DCT!\nDirect DWT', fontsize=8, 
         style='italic', color='green', weight='bold')
create_arrow(ax1, 5, 7.1, 5, 6.7)

# Frequency Bands
create_box(ax1, 5, 6.4, 3.5, 0.6, 'Frequency Bands:\nLH1, HL1, HH1, LH2, HL2, HH2, LL2', 
           color='#E5E5FF')
create_arrow(ax1, 5, 6.1, 5, 5.5)

# ACO Optimization
create_box(ax1, 5, 5.2, 3, 0.8, 'ACO OPTIMIZATION\n(Position Selection)', color='#FFCCFF')
ax1.text(8.3, 5.2, 'Selects best\ncoefficients', fontsize=8, style='italic')
create_arrow(ax1, 5, 4.6, 5, 4.2)

# Quantization Embedding
create_box(ax1, 5, 3.9, 3.5, 0.8, 'QUANTIZATION EMBEDDING\n(Q = 4.0 - 5.0)', 
           color='#FFE5CC')
ax1.text(8.8, 3.9, 'Single\nquantization\nstep', fontsize=8, 
         style='italic', color='green')
create_arrow(ax1, 5, 3.3, 5, 2.9)

# Embed data visual
create_box(ax1, 5, 2.6, 3, 0.6, 'Modified DWT Coefficients', color='#E5FFE5')
create_arrow(ax1, 5, 2.3, 5, 1.9)

# Inverse DWT
create_box(ax1, 5, 1.6, 3.5, 0.8, 'INVERSE DWT\nRECONSTRUCTION', color='#CCE5FF')
create_arrow(ax1, 5, 1, 5, 0.5)

# Output - Stego Image
create_box(ax1, 5, 0.2, 2.5, 0.6, 'STEGO IMAGE', color='#90EE90')

# Add stats box
stats_text = (
    'PERFORMANCE:\n'
    '• PSNR: 56.44 dB avg\n'
    '• Speed: 123-509 ms\n'
    '• Capacity: ~0.22%\n'
    '• Success: 100%'
)
ax1.text(1.2, 3, stats_text, fontsize=9, 
         bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='orange', linewidth=2),
         verticalalignment='top')

# Add encryption flow (side path)
create_box(ax1, 8.5, 11, 1.8, 0.6, "Receiver's\nECC Public Key", color='#FFE5FF')
create_arrow(ax1, 8.5, 10.7, 8.5, 10.3)
create_box(ax1, 8.5, 10, 1.8, 0.6, 'ECC Key\nEncryption', color='#FFE5FF')
create_arrow(ax1, 8.5, 9.7, 7.5, 9.3)

plt.tight_layout()
plt.savefig('LAYERX_SENDER_FLOWCHART.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("✓ Generated: LAYERX_SENDER_FLOWCHART.png")

# ============================================================================
# RECEIVER/EXTRACTION FLOWCHART
# ============================================================================
fig2, ax2 = plt.subplots(figsize=(12, 14))
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 15)
ax2.axis('off')

# Title
ax2.text(5, 14.5, 'LAYERX RECEIVER - Pure DWT Extraction', 
         ha='center', fontsize=16, weight='bold')
ax2.text(5, 14, '100% Success Rate | Perfect Data Recovery', 
         ha='center', fontsize=11, style='italic', color='green')

# Start - Stego Image
create_box(ax2, 5, 13, 2.5, 0.6, 'STEGO IMAGE', color='#90EE90')
create_arrow(ax2, 5, 12.7, 5, 12.3)

# DWT Transform
create_box(ax2, 5, 12, 3.5, 0.8, '2-LEVEL HAAR DWT\nTRANSFORM', color='#CCE5FF')
ax2.text(8.8, 12, '✓ NO DCT!\nDirect DWT', fontsize=8, 
         style='italic', color='green', weight='bold')
create_arrow(ax2, 5, 11.4, 5, 11)

# Frequency Bands
create_box(ax2, 5, 10.7, 3.5, 0.6, 'Frequency Bands:\nLH1, HL1, HH1, LH2, HL2, HH2, LL2', 
           color='#E5E5FF')
create_arrow(ax2, 5, 10.4, 5, 9.8)

# ACO Detection
create_box(ax2, 5, 9.5, 3, 0.8, 'ACO/CHAOS KEY\n(Identifies Locations)', color='#FFCCFF')
ax2.text(8.3, 9.5, 'Same positions\nas embedding', fontsize=8, style='italic')
create_arrow(ax2, 5, 8.9, 5, 8.5)

# Quantization Extraction
create_box(ax2, 5, 8.2, 3.5, 0.8, 'QUANTIZATION EXTRACTION\n(Q = 4.0 - 5.0)', 
           color='#FFE5CC')
ax2.text(8.8, 8.2, 'Read embedded\nbits', fontsize=8, style='italic')
create_arrow(ax2, 5, 7.6, 5, 7.2)

# Extracted Encrypted Payload
create_box(ax2, 5, 6.9, 2.5, 0.6, 'Encrypted Payload', color='#F0F0F0')

# ECC Decryption Path (side)
create_box(ax2, 1.5, 8.5, 1.8, 0.6, "Receiver's\nECC Private Key", color='#FFE5FF')
create_arrow(ax2, 1.5, 8.2, 1.5, 7.8)
create_box(ax2, 1.5, 7.5, 1.8, 0.6, 'ECC Key\nDecryption', color='#FFE5FF')
create_arrow(ax2, 1.5, 7.2, 1.5, 6.8)
create_box(ax2, 1.5, 6.5, 1.8, 0.6, 'Decrypted\nSession Key', color='#E5FFE5')
create_arrow(ax2, 2.4, 6.5, 3.8, 6.5)

# Main path continues
create_arrow(ax2, 5, 6.6, 5, 6)

# AES-256 Decryption
create_box(ax2, 5, 5.7, 2.5, 0.6, 'AES-256\nDECRYPTION', color='#FFE5E5')
ax2.text(7.8, 5.7, 'Uses session\nkey', fontsize=8, style='italic')
create_arrow(ax2, 5, 5.4, 5, 5)

# Reed-Solomon Decoding
create_box(ax2, 5, 4.7, 2.5, 0.6, 'REED-SOLOMON\nDECODING', color='#E5FFE5')
ax2.text(7.8, 4.7, 'Error\ncorrection', fontsize=8, style='italic')
create_arrow(ax2, 5, 4.4, 5, 4)

# Huffman Decompression
create_box(ax2, 5, 3.7, 2.5, 0.6, 'HUFFMAN\nDECOMPRESSION', color='#E5F5FF')
ax2.text(7.8, 3.7, 'Restores\noriginal size', fontsize=8, style='italic')
create_arrow(ax2, 5, 3.4, 5, 3)

# Verification
create_box(ax2, 5, 2.7, 2.5, 0.6, 'INTEGRITY CHECK', color='#FFFFCC')
create_arrow(ax2, 5, 2.4, 5, 2)

# Output - Original Message
create_box(ax2, 5, 1.7, 2.5, 0.6, 'ORIGINAL MESSAGE', color='#FFE5CC')
create_arrow(ax2, 5, 1.4, 5, 0.8)

# Success indicator
create_box(ax2, 5, 0.5, 2, 0.4, '✓ SUCCESS', color='#90EE90')

# Add stats box
stats_text = (
    'PERFORMANCE:\n'
    '• Extraction: 156-484 ms\n'
    '• Success Rate: 100%\n'
    '• Perfect Match: Yes\n'
    '• Max Payload: 50 KB'
)
ax2.text(8.8, 3, stats_text, fontsize=9, 
         bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='orange', linewidth=2),
         verticalalignment='top')

# Add comparison note
comparison_text = (
    'WHY NO DCT?\n'
    '✗ DWT+DCT: 48.54 dB\n'
    '✓ Pure DWT: 56.44 dB\n'
    '\n'
    '✗ DWT+DCT: 75% success\n'
    '✓ Pure DWT: 100% success'
)
ax2.text(1.5, 3.5, comparison_text, fontsize=8, 
         bbox=dict(boxstyle='round', facecolor='#FFE5E5', edgecolor='red', linewidth=2),
         verticalalignment='top')

plt.tight_layout()
plt.savefig('LAYERX_RECEIVER_FLOWCHART.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✓ Generated: LAYERX_RECEIVER_FLOWCHART.png")

# ============================================================================
# COMPARISON DIAGRAM - DWT vs DWT+DCT
# ============================================================================
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 8))

# LEFT: Pure DWT (Recommended)
ax3a.set_xlim(0, 5)
ax3a.set_ylim(0, 10)
ax3a.axis('off')
ax3a.text(2.5, 9.5, 'PURE DWT (Recommended)', ha='center', fontsize=14, weight='bold', color='green')

create_box(ax3a, 2.5, 8.5, 2, 0.5, 'Cover Image', color='#FFFFCC')
create_arrow(ax3a, 2.5, 8.2, 2.5, 7.8)
create_box(ax3a, 2.5, 7.5, 2, 0.5, '2-Level DWT', color='#CCE5FF')
create_arrow(ax3a, 2.5, 7.2, 2.5, 6.8)
create_box(ax3a, 2.5, 6.5, 2.2, 0.5, '7 Frequency Bands', color='#E5E5FF')
create_arrow(ax3a, 2.5, 6.2, 2.5, 5.8)
create_box(ax3a, 2.5, 5.5, 2.5, 0.5, 'Direct Embedding\n(Q=4.5)', color='#FFE5CC')
ax3a.text(4.5, 5.5, '✓ Single\nquantization', fontsize=7, style='italic', color='green')
create_arrow(ax3a, 2.5, 5.2, 2.5, 4.8)
create_box(ax3a, 2.5, 4.5, 2.2, 0.5, 'Modified Bands', color='#E5FFE5')
create_arrow(ax3a, 2.5, 4.2, 2.5, 3.8)
create_box(ax3a, 2.5, 3.5, 2, 0.5, 'Inverse DWT', color='#CCE5FF')
create_arrow(ax3a, 2.5, 3.2, 2.5, 2.8)
create_box(ax3a, 2.5, 2.5, 2, 0.5, 'Stego Image', color='#90EE90')

# Stats
stats_dwt = (
    'RESULTS:\n'
    '✓ PSNR: 56.44 dB\n'
    '✓ Success: 100%\n'
    '✓ Speed: 5-10× faster\n'
    '✓ Simple pipeline'
)
ax3a.text(2.5, 1.3, stats_dwt, fontsize=9, ha='center',
         bbox=dict(boxstyle='round', facecolor='lightgreen', edgecolor='green', linewidth=2))

# RIGHT: DWT+DCT (Not Recommended)
ax3b.set_xlim(0, 5)
ax3b.set_ylim(0, 10)
ax3b.axis('off')
ax3b.text(2.5, 9.5, 'DWT+DCT (Not Recommended)', ha='center', fontsize=14, weight='bold', color='red')

create_box(ax3b, 2.5, 8.5, 2, 0.5, 'Cover Image', color='#FFFFCC')
create_arrow(ax3b, 2.5, 8.2, 2.5, 7.8)
create_box(ax3b, 2.5, 7.5, 2, 0.5, '2-Level DWT', color='#CCE5FF')
create_arrow(ax3b, 2.5, 7.2, 2.5, 6.8)
create_box(ax3b, 2.5, 6.5, 2.2, 0.5, '7 Frequency Bands', color='#E5E5FF')
create_arrow(ax3b, 2.5, 6.2, 2.5, 5.8)
create_box(ax3b, 2.5, 5.5, 2, 0.5, 'Block DCT (8×8)', color='#FFE5E5')
ax3b.text(4.3, 5.5, '✗ Adds\ncomplexity', fontsize=7, style='italic', color='red')
create_arrow(ax3b, 2.5, 5.2, 2.5, 4.8)
create_box(ax3b, 2.5, 4.5, 2.5, 0.5, 'DCT Embedding\n(Q=6-7)', color='#FFE5CC')
ax3b.text(4.5, 4.5, '✗ Double\nquantization', fontsize=7, style='italic', color='red')
create_arrow(ax3b, 2.5, 4.2, 2.5, 3.8)
create_box(ax3b, 2.5, 3.5, 2, 0.5, 'Inverse DCT', color='#FFE5E5')
create_arrow(ax3b, 2.5, 3.2, 2.5, 2.8)
create_box(ax3b, 2.5, 2.5, 2, 0.5, 'Inverse DWT', color='#CCE5FF')
create_arrow(ax3b, 2.5, 2.2, 2.5, 1.8)
create_box(ax3b, 2.5, 1.5, 2, 0.5, 'Stego Image', color='#FFB6C1')

# Stats
stats_dct = (
    'RESULTS:\n'
    '✗ PSNR: 48.54 dB\n'
    '✗ Success: 75%\n'
    '✗ Speed: Slower\n'
    '✗ Complex pipeline'
)
ax3b.text(2.5, 0.6, stats_dct, fontsize=9, ha='center',
         bbox=dict(boxstyle='round', facecolor='#FFE5E5', edgecolor='red', linewidth=2))

fig3.suptitle('Method Comparison: Pure DWT vs DWT+DCT Hybrid', fontsize=16, weight='bold', y=0.98)
plt.tight_layout()
plt.savefig('LAYERX_METHOD_COMPARISON.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✓ Generated: LAYERX_METHOD_COMPARISON.png")

print("\n" + "="*80)
print("✓✓✓ ALL FLOWCHARTS GENERATED SUCCESSFULLY ✓✓✓")
print("="*80)
print("\nGenerated Files:")
print("  1. LAYERX_SENDER_FLOWCHART.png - Embedding process (Pure DWT)")
print("  2. LAYERX_RECEIVER_FLOWCHART.png - Extraction process (Pure DWT)")
print("  3. LAYERX_METHOD_COMPARISON.png - Pure DWT vs DWT+DCT comparison")
print("\nKey Features:")
print("  ✓ Shows Pure DWT method (NO DCT layer)")
print("  ✓ Achieves 56.44 dB PSNR (exceeds 50 dB target)")
print("  ✓ 100% extraction reliability")
print("  ✓ Includes performance statistics")
print("  ✓ Production-ready flowcharts")
print("="*80)
