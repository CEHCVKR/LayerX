"""
LayerX Steganographic Secure File Transfer - Receiver
Receives and extracts files from stego images
"""

import os
import socket
import json
import base64
import cv2
import struct
from nacl.signing import VerifyKey
from nacl.public import PrivateKey, PublicKey, Box

# Import LayerX modules (will be in same directory)
from a5_embedding_extraction import extract_from_dwt_bands

IDENTITY_FILE = 'my_identity.json'
PEERS_FILE = 'peers.json'
TRANSFER_PORT = 9000


def generate_keys(username):
    """Generate Ed25519 and X25519 keys for a user"""
    from nacl.signing import SigningKey
    
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    private_key = PrivateKey.generate()
    public_key = private_key.public_key

    return {
        'username': username,
        'signing_private': base64.b64encode(signing_key.encode()).decode(),
        'signing_public': base64.b64encode(verify_key.encode()).decode(),
        'x25519_private': base64.b64encode(private_key.encode()).decode(),
        'x25519_public': base64.b64encode(public_key.encode()).decode()
    }


def load_or_create_identity():
    """Load existing identity or create new one"""
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, 'r') as f:
            identity = json.load(f)
            print(f"✓ Loaded identity for: {identity['username']}")
            return identity
    else:
        username = input("Enter your username: ").strip()
        if not username:
            username = "User_" + os.urandom(4).hex()
        
        identity = generate_keys(username)
        
        with open(IDENTITY_FILE, 'w') as f:
            json.dump(identity, f, indent=2)
        
        print(f"✓ Created new identity for: {username}")
        print(f"✓ Public key: {identity['x25519_public'][:16]}...")
        return identity


def load_peers():
    """Load list of known peers"""
    if os.path.exists(PEERS_FILE):
        with open(PEERS_FILE, 'r') as f:
            return json.load(f)
    return []


def get_peer_by_username(username):
    """Find peer by username"""
    peers = load_peers()
    for peer in peers:
        if peer['username'] == username:
            return peer
    return None


def receive_stego_image():
    """Listen for incoming stego image"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", TRANSFER_PORT))
    sock.listen(1)
    
    print(f"🔊 Listening on port {TRANSFER_PORT}...")
    print("   Waiting for file...")
    
    conn, addr = sock.accept()
    print(f"\n📥 Connection from {addr[0]}:{addr[1]}")
    
    try:
        # Receive image size (4 bytes)
        size_data = conn.recv(4)
        if len(size_data) < 4:
            raise ValueError("Invalid size header")
        
        image_size = struct.unpack('!I', size_data)[0]
        print(f"   Expected size: {image_size} bytes")
        
        # Receive image data
        image_data = b""
        remaining = image_size
        
        while remaining > 0:
            chunk = conn.recv(min(4096, remaining))
            if not chunk:
                break
            image_data += chunk
            remaining -= len(chunk)
            if len(image_data) % 10000 == 0:
                print(f"   Received: {len(image_data)}/{image_size} bytes")
        
        conn.close()
        sock.close()
        
        if len(image_data) != image_size:
            raise ValueError(f"Incomplete transfer: {len(image_data)}/{image_size}")
        
        print(f"   ✓ Received {len(image_data)} bytes")
        
        # Save received image
        received_filename = "received_stego.png"
        with open(received_filename, 'wb') as f:
            f.write(image_data)
        
        print(f"   ✓ Saved as: {received_filename}")
        
        return received_filename, addr[0]
        
    except Exception as e:
        print(f"   ✗ Reception failed: {e}")
        conn.close()
        sock.close()
        return None, None


def extract_and_decrypt(stego_image_path, sender_ip, my_identity):
    """Extract payload from stego image and decrypt"""
    
    print(f"\n🔍 Extracting from: {stego_image_path}")
    
    # Load stego image
    stego_image = cv2.imread(stego_image_path, cv2.IMREAD_GRAYSCALE)
    if stego_image is None:
        raise ValueError("Cannot load stego image")
    
    # Try different payload sizes (we don't know exact size)
    # Start with reasonable estimates
    max_capacity = int(stego_image.size * 0.1)  # 10% of image
    
    for attempt_size in [500, 1000, 2000, 5000, 10000, 20000, max_capacity]:
        try:
            print(f"   Attempting extraction with size: {attempt_size} bytes")
            
            # Extract payload
            extracted_data = extract_from_dwt_bands(stego_image, attempt_size)
            
            # Try to parse as JSON
            try:
                # Find JSON boundaries
                start = extracted_data.find(b'{')
                if start == -1:
                    continue
                
                # Try to decode JSON
                json_data = extracted_data[start:]
                metadata = json.loads(json_data.decode('utf-8', errors='ignore'))
                
                if 'file_name' in metadata and 'sender' in metadata and 'signed_data' in metadata:
                    print(f"   ✓ Valid metadata found!")
                    
                    # Get sender info
                    sender_username = metadata['sender']
                    sender_peer = get_peer_by_username(sender_username)
                    
                    if not sender_peer:
                        print(f"   ⚠️  Unknown sender: {sender_username}")
                        print(f"   ⚠️  Add sender to peers.json to verify")
                        return None
                    
                    # Verify signature
                    signed_data = base64.b64decode(metadata['signed_data'])
                    verify_key = VerifyKey(base64.b64decode(sender_peer["signing_public"]))
                    
                    try:
                        verified_data = verify_key.verify(signed_data)
                        print(f"   ✓ Signature verified from: {sender_username}")
                    except Exception as e:
                        print(f"   ✗ Signature verification failed: {e}")
                        return None
                    
                    # Decrypt using NaCl
                    my_priv = PrivateKey(base64.b64decode(my_identity["x25519_private"]))
                    sender_pub = PublicKey(base64.b64decode(sender_peer["x25519_public"]))
                    box = Box(my_priv, sender_pub)
                    
                    try:
                        decrypted_data = box.decrypt(verified_data)
                        print(f"   ✓ Decryption successful!")
                    except Exception as e:
                        print(f"   ✗ Decryption failed: {e}")
                        return None
                    
                    # Save file
                    output_filename = f"received_{metadata['file_name']}"
                    with open(output_filename, 'wb') as f:
                        f.write(decrypted_data)
                    
                    print(f"   ✓ File saved: {output_filename}")
                    print(f"   ✓ Size: {len(decrypted_data)} bytes")
                    
                    return output_filename
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"   Attempt failed: {e}")
                continue
                
        except Exception as e:
            continue
    
    print(f"   ✗ Could not extract valid payload")
    return None


def main():
    """Main receiver program"""
    print("="*70)
    print("LAYERX STEGANOGRAPHIC SECURE FILE TRANSFER - RECEIVER")
    print("="*70)
    
    # Load or create identity
    my_identity = load_or_create_identity()
    
    while True:
        print("\n--- Receiver Menu ---")
        print("1. Receive file")
        print("2. Show my public key")
        print("3. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            try:
                # Receive stego image
                stego_path, sender_ip = receive_stego_image()
                
                if stego_path:
                    # Extract and decrypt
                    output_file = extract_and_decrypt(stego_path, sender_ip, my_identity)
                    
                    if output_file:
                        print(f"\n✅ File received successfully: {output_file}")
                    else:
                        print(f"\n❌ Failed to extract/decrypt file")
                else:
                    print(f"\n❌ Failed to receive stego image")
                    
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        elif choice == "2":
            print(f"\n--- Your Public Keys ---")
            print(f"Username: {my_identity['username']}")
            print(f"X25519 Public Key:\n{my_identity['x25519_public']}")
            print(f"Signing Public Key:\n{my_identity['signing_public']}")
            print(f"\n💡 Share these keys with senders to receive files")
            
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("⚠️  Invalid choice")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
