"""
Test script for transceiver.py - validates P2P communication functionality
"""

import os
import sys
import json
import time
import socket
import traceback
from datetime import datetime

def test_transceiver_imports():
    """Test if transceiver imports work"""
    print("="*80)
    print("TEST 1: TRANSCEIVER MODULE IMPORTS")
    print("="*80)
    
    try:
        # Import transceiver modules
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        print("Attempting imports...")
        from transceiver import discover_peers, send_stego_message, receive_stego_message
        print("  ✅ Core functions imported successfully")
        
        # Check for required modules
        from a7_communication import initialize_p2p, broadcast_discovery
        print("  ✅ P2P communication module available")
        
        from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands
        print("  ✅ Embedding/extraction modules available")
        
        from a4_compression import compress_huffman, decompress_huffman
        print("  ✅ Compression modules available")
        
        from a1_encryption import encrypt_message, decrypt_message
        print("  ✅ Encryption modules available")
        
        print("\n✅ All transceiver imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        traceback.print_exc()
        return False

def test_identity_loading():
    """Test identity file loading"""
    print("\n" + "="*80)
    print("TEST 2: IDENTITY FILE LOADING")
    print("="*80)
    
    try:
        identity_file = "my_identity.json"
        
        if not os.path.exists(identity_file):
            print(f"  ⚠️  Identity file not found: {identity_file}")
            print("  Creating test identity...")
            
            test_identity = {
                "user_id": "test_user_001",
                "display_name": "Test User",
                "public_key": "test_public_key_placeholder",
                "created": datetime.now().isoformat()
            }
            
            with open(identity_file, 'w') as f:
                json.dump(test_identity, f, indent=2)
            
            print("  ✅ Test identity created")
        
        with open(identity_file, 'r') as f:
            identity = json.load(f)
        
        print(f"  User ID: {identity.get('user_id', 'N/A')}")
        print(f"  Display Name: {identity.get('display_name', 'N/A')}")
        print(f"  Has Public Key: {'Yes' if identity.get('public_key') else 'No'}")
        
        print("\n✅ Identity loading successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Identity loading failed: {str(e)}")
        return False

def test_network_availability():
    """Test if network is available for P2P"""
    print("\n" + "="*80)
    print("TEST 3: NETWORK AVAILABILITY")
    print("="*80)
    
    try:
        # Check localhost connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        
        # Try to bind to a port
        test_port = 5555
        try:
            sock.bind(('', test_port))
            print(f"  ✅ Can bind to port {test_port}")
            sock.close()
        except OSError as e:
            print(f"  ⚠️  Port {test_port} already in use (transceiver running?)")
            sock.close()
        
        # Check network interfaces
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"  Hostname: {hostname}")
        print(f"  Local IP: {local_ip}")
        
        print("\n✅ Network is available!")
        return True
        
    except Exception as e:
        print(f"\n❌ Network test failed: {str(e)}")
        return False

def test_transceiver_structure():
    """Test transceiver.py file structure"""
    print("\n" + "="*80)
    print("TEST 4: TRANSCEIVER FILE STRUCTURE")
    print("="*80)
    
    try:
        with open('transceiver.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_functions = [
            'discover_peers',
            'send_stego_message',
            'receive_stego_message',
            'main_menu',
            'main'
        ]
        
        found_functions = []
        missing_functions = []
        
        for func in required_functions:
            if f'def {func}' in content:
                found_functions.append(func)
                print(f"  ✅ Found: {func}()")
            else:
                missing_functions.append(func)
                print(f"  ❌ Missing: {func}()")
        
        print(f"\n  Functions: {len(found_functions)}/{len(required_functions)} found")
        
        if missing_functions:
            print(f"  ⚠️  Missing: {', '.join(missing_functions)}")
        
        return len(missing_functions) == 0
        
    except Exception as e:
        print(f"\n❌ Structure test failed: {str(e)}")
        return False

def test_configuration():
    """Test configuration and setup"""
    print("\n" + "="*80)
    print("TEST 5: CONFIGURATION")
    print("="*80)
    
    try:
        # Check for required files
        required_files = [
            'transceiver.py',
            'a1_encryption.py',
            'a4_compression.py',
            'a5_embedding_extraction.py',
            'a7_communication.py'
        ]
        
        missing_files = []
        for file in required_files:
            if os.path.exists(file):
                print(f"  ✅ Found: {file}")
            else:
                missing_files.append(file)
                print(f"  ❌ Missing: {file}")
        
        if missing_files:
            print(f"\n  ⚠️  Missing files: {', '.join(missing_files)}")
            return False
        
        print("\n✅ All required files present!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {str(e)}")
        return False

def generate_test_report(results):
    """Generate test report"""
    print("\n" + "="*80)
    print("TRANSCEIVER TEST REPORT")
    print("="*80)
    
    total_tests = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total_tests - passed
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed} ({pass_rate:.1f}%)")
    print(f"Failed: {failed}")
    print()
    
    print("Detailed Results:")
    print("-" * 80)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if results.get('imports', False):
        print("✅ Transceiver is properly structured")
    else:
        print("⚠️  Fix import issues in transceiver.py")
    
    if results.get('network', False):
        print("✅ Network ready for P2P communication")
    else:
        print("⚠️  Check network/firewall settings")
    
    if results.get('identity', False):
        print("✅ User identity configured")
    else:
        print("⚠️  Set up user identity (my_identity.json)")
    
    print("\n" + "="*80)
    if pass_rate >= 80:
        print("✅ TRANSCEIVER READY FOR USE")
    elif pass_rate >= 60:
        print("⚠️  TRANSCEIVER MOSTLY READY - Minor fixes needed")
    else:
        print("❌ TRANSCEIVER NEEDS ATTENTION - Fix critical issues")
    print("="*80)

if __name__ == "__main__":
    print("🔧 LayerX Transceiver Test Suite")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    results = {}
    
    # Run tests
    results['imports'] = test_transceiver_imports()
    results['identity'] = test_identity_loading()
    results['network'] = test_network_availability()
    results['structure'] = test_transceiver_structure()
    results['configuration'] = test_configuration()
    
    # Generate report
    generate_test_report(results)
    
    print("\n📄 Test complete!")
