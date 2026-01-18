# Comprehensive Steganography Research Report

**Generated:** 2026-01-18 22:25:28
**Experiment ID:** 20260118_222436

## Research Objectives

1. **Image Size Impact**: How do different image dimensions affect embedding capacity and quality?
2. **Payload Scaling**: What are the optimal payload-to-image size ratios?
3. **Method Comparison**: How do DWT, DCT, and hybrid approaches compare?
4. **Q-Factor Optimization**: Scientific justification for Q=5.0 vs other values
5. **Process Efficiency**: Detailed analysis of processing overheads

## Q-Factor Scientific Analysis

### Research Question: Why Q=5.0?

| Q-Factor | Avg PSNR (dB) | Quality Rating | Success Rate | Avg Time (s) |
|----------|---------------|----------------|--------------|---------------|

### Q-Factor Analysis Conclusions:

- **Optimal Q-Factor: None** (best balance of quality and reliability)
- **Q=5.0 Performance**: Widely used standard providing good quality-reliability tradeoff

## Embedding Method Comparison

| Method | Tests | Avg PSNR (dB) | Success Rate | Avg Time (s) | Avg Capacity Util |
|--------|-------|---------------|--------------|--------------|--------------------|
| DWT_Only       |     3 |       48.34 |     50.0% |       0.17 |            0.371 |

## Detailed Process Analysis

### Processing Stage Breakdown

| Stage | Avg Time (s) | % of Total | Description |
|-------|--------------|------------|-------------|
| Image Loading        |      0.007 |      4.2% | Processing stage |
| Encryption           |      0.042 |     24.1% | Processing stage |
| Compression          |      0.001 |      0.4% | Processing stage |
| Frequency Transform  |      0.009 |      4.9% | Processing stage |
| Embedding            |      0.036 |     20.4% | Processing stage |
| Reconstruction       |      0.003 |      1.7% | Processing stage |
| Quality Analysis     |      0.000 |      0.0% | Processing stage |
| Extraction           |      0.027 |     15.6% | Processing stage |
| Verification         |      0.050 |     28.5% | Processing stage |

### Data Size Analysis

| Payload Size | Encrypted Size | Compressed Size | Compression Ratio | Encryption Overhead |
|--------------|----------------|-----------------|-------------------|-----------------------|
|        512 B |          528 B |           504 B |           0.955 |                16 B |
|      1,024 B |         1040 B |          1024 B |           0.985 |                16 B |
|      4,096 B |         4112 B |          4104 B |           0.998 |                16 B |
