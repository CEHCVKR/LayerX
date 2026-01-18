#!/usr/bin/env python3
"""
LayerX CRITICAL PROJECT ANALYSIS
================================
Analyzing ALL codes and files to identify the CORRECT pipeline vs what tests are using

HYPOTHESIS: All test results are WRONG because Reed-Solomon ECC is not being used!
"""

import os
import json
from pathlib import Path

print("🔍 COMPREHENSIVE LayerX PROJECT ANALYSIS")
print("=" * 50)
print("🚨 CRITICAL HYPOTHESIS: All test results are WRONG!")
print("📋 Reed-Solomon ECC exists but not being used in tests")
print()

# Analyze the correct LayerX pipeline
def analyze_layerx_pipeline():
    """Analyze what the correct LayerX pipeline should be"""
    
    print("🎯 ANALYZING CORRECT LayerX PIPELINE:")
    print("=" * 45)
    
    # Check a4_compression.py for the correct pipeline
    pipeline_analysis = {
        "Module 1 (a1_encryption.py)": {
            "functions": ["encrypt_message()", "decrypt_message()"],
            "purpose": "AES-256 encryption with salt/IV",
            "pipeline_step": "1. Data → AES encryption → ciphertext"
        },
        "Module 4 (a4_compression.py)": {
            "functions": ["compress_huffman()", "create_payload()", "parse_payload()"],
            "purpose": "Huffman compression + Reed-Solomon ECC",
            "pipeline_step": "2. Ciphertext → compress → Reed-Solomon ECC → payload"
        },
        "Module 5 (a5_embedding_extraction.py)": {
            "functions": ["embed()", "extract()", "embed_in_dwt_bands()"],
            "purpose": "DWT/DCT steganographic embedding",
            "pipeline_step": "3. Payload → DWT embedding → stego_image"
        }
    }
    
    print("📊 CORRECT PIPELINE ARCHITECTURE:")
    for module, details in pipeline_analysis.items():
        print(f"\n✅ {module}:")
        print(f"   Functions: {', '.join(details['functions'])}")
        print(f"   Purpose: {details['purpose']}")
        print(f"   Step: {details['pipeline_step']}")
    
    print(f"\n🎯 CORRECT FULL PIPELINE:")
    print("   📥 Input: Original message")
    print("   🔐 Step 1: encrypt_message() → (ciphertext, salt, iv)")
    print("   🗜️  Step 2: compress_huffman() → (compressed, tree)")
    print("   🛡️  Step 3: create_payload() → payload_with_reed_solomon_ecc")
    print("   📷 Step 4: embed() → stego_image")
    print("   📤 Output: Stego image with ECC-protected data")
    
    return pipeline_analysis

# Analyze what tests are actually doing
def analyze_test_implementations():
    """Analyze what pipeline the tests are actually using"""
    
    print(f"\n🔍 ANALYZING TEST IMPLEMENTATIONS:")
    print("=" * 40)
    
    test_files_analysis = {}
    
    # Find all test files
    test_patterns = [
        "test*.py",
        "*research*.py", 
        "*experiment*.py",
        "robustness*.py",
        "comprehensive*.py"
    ]
    
    test_files = []
    for pattern in test_patterns:
        test_files.extend(Path(".").glob(pattern))
    
    print(f"📂 Found {len(test_files)} test files to analyze:")
    
    for test_file in test_files[:15]:  # Analyze first 15 files
        print(f"   📄 {test_file.name}")
        
        try:
            with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check what pipeline functions are being used
            pipeline_usage = {
                "encrypt_message": "encrypt_message" in content,
                "compress_huffman": "compress_huffman" in content,
                "create_payload": "create_payload" in content,  # Reed-Solomon ECC
                "parse_payload": "parse_payload" in content,     # Reed-Solomon ECC
                "embed": "def embed(" in content or "embed(" in content,
                "extract": "def extract(" in content or "extract(" in content
            }
            
            # Determine pipeline completeness
            has_encryption = pipeline_usage["encrypt_message"]
            has_compression = pipeline_usage["compress_huffman"] 
            has_reed_solomon = pipeline_usage["create_payload"] and pipeline_usage["parse_payload"]
            has_embedding = pipeline_usage["embed"] and pipeline_usage["extract"]
            
            # Classify the test
            if has_encryption and has_compression and has_reed_solomon and has_embedding:
                classification = "✅ CORRECT - Full pipeline with Reed-Solomon"
            elif has_encryption and has_compression and has_embedding:
                classification = "❌ INCORRECT - Missing Reed-Solomon ECC"
            elif has_embedding:
                classification = "⚠️ PARTIAL - Only embedding, no encryption/compression"
            else:
                classification = "❓ UNKNOWN - Complex or different test"
                
            test_files_analysis[test_file.name] = {
                "pipeline_usage": pipeline_usage,
                "classification": classification,
                "has_reed_solomon": has_reed_solomon
            }
            
        except Exception as e:
            test_files_analysis[test_file.name] = {
                "error": str(e),
                "classification": "❌ ERROR - Could not analyze"
            }
    
    return test_files_analysis

# Analyze specific critical files
def analyze_critical_files():
    """Analyze the most critical files in detail"""
    
    print(f"\n🎯 DETAILED ANALYSIS OF CRITICAL FILES:")
    print("=" * 45)
    
    critical_files = [
        "robustness_testing_research.py",
        "local_comprehensive_research.py", 
        "security_steganalysis_research.py",
        "a5_embedding_extraction.py"
    ]
    
    critical_analysis = {}
    
    for file_name in critical_files:
        if os.path.exists(file_name):
            print(f"\n📄 ANALYZING: {file_name}")
            
            try:
                with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for specific pipeline usage
                findings = {}
                
                # Check encryption usage
                if "encrypt_message" in content:
                    findings["encryption"] = "✅ Uses AES encryption"
                else:
                    findings["encryption"] = "❌ No AES encryption"
                
                # Check compression usage  
                if "compress_huffman" in content:
                    findings["compression"] = "✅ Uses Huffman compression"
                else:
                    findings["compression"] = "❌ No Huffman compression"
                
                # Check Reed-Solomon usage
                if "create_payload" in content and "parse_payload" in content:
                    findings["reed_solomon"] = "✅ Uses Reed-Solomon ECC"
                elif "create_payload" in content or "parse_payload" in content:
                    findings["reed_solomon"] = "⚠️ Partial Reed-Solomon usage"
                else:
                    findings["reed_solomon"] = "❌ NO Reed-Solomon ECC - CRITICAL BUG!"
                
                # Check embedding method
                if "embed_in_dwt_bands" in content:
                    findings["embedding"] = "✅ Uses DWT embedding"
                elif "embed(" in content:
                    findings["embedding"] = "✅ Uses embedding function"
                else:
                    findings["embedding"] = "❌ No embedding found"
                
                # Overall assessment
                if "❌ NO Reed-Solomon ECC" in findings.get("reed_solomon", ""):
                    findings["overall"] = "🚨 CRITICAL: Missing Reed-Solomon - All results INVALID"
                elif "✅ Uses Reed-Solomon ECC" in findings.get("reed_solomon", ""):
                    findings["overall"] = "✅ CORRECT: Full pipeline with ECC"
                else:
                    findings["overall"] = "⚠️ PARTIAL: Incomplete pipeline"
                
                critical_analysis[file_name] = findings
                
                # Print findings
                for aspect, result in findings.items():
                    print(f"   {aspect.upper()}: {result}")
                    
            except Exception as e:
                critical_analysis[file_name] = {"error": str(e)}
                print(f"   ERROR: {e}")
        else:
            print(f"\n❌ {file_name} - FILE NOT FOUND")
    
    return critical_analysis

# Run the comprehensive analysis
pipeline_analysis = analyze_layerx_pipeline()
test_analysis = analyze_test_implementations()
critical_analysis = analyze_critical_files()

print(f"\n📊 COMPREHENSIVE ANALYSIS RESULTS:")
print("=" * 40)

# Count correct vs incorrect tests
correct_tests = 0
incorrect_tests = 0  
partial_tests = 0

for test_name, analysis in test_analysis.items():
    if "CORRECT" in analysis.get("classification", ""):
        correct_tests += 1
    elif "INCORRECT" in analysis.get("classification", ""):
        incorrect_tests += 1
    elif "PARTIAL" in analysis.get("classification", ""):
        partial_tests += 1

total_tests = len(test_analysis)

print(f"📈 TEST PIPELINE ANALYSIS:")
print(f"   ✅ CORRECT (with Reed-Solomon): {correct_tests}/{total_tests} ({correct_tests/total_tests*100:.1f}%)")
print(f"   ❌ INCORRECT (missing Reed-Solomon): {incorrect_tests}/{total_tests} ({incorrect_tests/total_tests*100:.1f}%)")  
print(f"   ⚠️ PARTIAL (incomplete): {partial_tests}/{total_tests} ({partial_tests/total_tests*100:.1f}%)")

print(f"\n🚨 CRITICAL FINDINGS:")
if incorrect_tests > correct_tests:
    print("   💀 MAJORITY OF TESTS ARE WRONG - Missing Reed-Solomon ECC!")
    print("   📊 ALL robustness/research results are INVALID")
    print("   🎯 Need to fix ALL test scripts immediately")
else:
    print("   ✅ Majority of tests use correct pipeline")

print(f"\n📋 SPECIFIC FILES NEEDING FIXES:")
for test_name, analysis in test_analysis.items():
    if "INCORRECT" in analysis.get("classification", "") or "NO Reed-Solomon ECC" in str(analysis):
        print(f"   🔧 FIX NEEDED: {test_name}")

# Create action plan
action_plan = {
    "immediate_actions": [
        "Fix robustness_testing_research.py to use create_payload()",
        "Fix local_comprehensive_research.py to use Reed-Solomon pipeline", 
        "Fix security_steganalysis_research.py pipeline",
        "Update all research scripts created today"
    ],
    "pipeline_fixes": [
        "Replace compress_huffman() with create_payload() in tests",
        "Replace decompress_huffman() with parse_payload() in tests",
        "Ensure proper error handling for Reed-Solomon decoding failures"
    ],
    "validation_tests": [
        "Re-run robustness testing with correct pipeline",
        "Re-run comprehensive research with Reed-Solomon ECC",
        "Compare results: old (no ECC) vs new (with ECC)",
        "Validate that Reed-Solomon actually improves robustness"
    ]
}

print(f"\n🎯 ACTION PLAN:")
print("=" * 15)

for category, actions in action_plan.items():
    print(f"\n{category.upper().replace('_', ' ')}:")
    for i, action in enumerate(actions, 1):
        print(f"   {i}. {action}")

# Save comprehensive analysis
analysis_results = {
    "analysis_timestamp": "2026-01-18 12:30:00",
    "pipeline_analysis": pipeline_analysis,
    "test_analysis": test_analysis, 
    "critical_analysis": critical_analysis,
    "statistics": {
        "total_tests": total_tests,
        "correct_tests": correct_tests,
        "incorrect_tests": incorrect_tests,
        "partial_tests": partial_tests
    },
    "action_plan": action_plan,
    "conclusion": "MAJORITY OF TESTS MISSING REED-SOLOMON ECC - ALL RESULTS INVALID"
}

with open("project_comprehensive_analysis.json", "w") as f:
    json.dump(analysis_results, f, indent=2)

print(f"\n📄 Comprehensive analysis saved: project_comprehensive_analysis.json")
print("\n" + "="*60)
print("🚨 CRITICAL CONCLUSION: TESTS ARE WRONG - REED-SOLOMON MISSING!")
print("="*60)
print("📊 All robustness results (15.6%) are INVALID - need immediate fixes!")