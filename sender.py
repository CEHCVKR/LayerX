"""
LayerX Steganographic Secure File Transfer - Sender
Uses DWT+DCT steganography with NaCl encryption
"""

import os
import socket
import json
import base64
import cv2
from nacl.public import Box, PublicKey, PrivateKey
from nacl.signing import SigningKey, VerifyKey

# Import LayerX modules (will be in same directory)
from a1_encryption import encrypt_message
from a5_embedding_extraction import embed_in_dwt_bands

IDENTITY_FILE = 'my_identity.json'
PEERS_FILE = 'peers.json'
TRANSFER_PORT = 9000


def generate_keys(username):
    """Generate Ed25519 and X25519 keys for a user"""
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


def add_peer():
    """Manually add a peer to the network"""
    print("\n--- Add New Peer ---")
    peer_username = input("Peer username: ").strip()
    peer_ip = input("Peer IP address: ").strip()
    peer_x25519_public = input("Peer X25519 public key: ").strip()
    peer_signing_public = input("Peer signing public key: ").strip()
    
    peer = {
        "username": peer_username,
        "ip": peer_ip,
        "x25519_public": peer_x25519_public,
        "signing_public": peer_signing_public
    }
    
    peers = load_peers()
    
    # Check if peer already exists
    for p in peers:
        if p['ip'] == peer_ip:
            print(f"⚠️  Peer {peer_ip} already exists. Updating...")
            p.update(peer)
            with open(PEERS_FILE, 'w') as f:
                json.dump(peers, f, indent=2)
            return
    
    peers.append(peer)
    
    with open(PEERS_FILE, 'w') as f:
        json.dump(peers, f, indent=2)
    
    print(f"✓ Added peer: {peer_username} ({peer_ip})")


def list_peers():
    """Display all known peers"""
    peers = load_peers()
    
    if not peers:
        print("\n⚠️  No peers registered. Add peers first.")
        return None
    
    print("\n--- Available Peers ---")
    for idx, peer in enumerate(peers, 1):
        print(f"{idx}. {peer['username']} ({peer['ip']})")
    
    return peers


def get_peer_by_index(index):
    """Get peer by selection index"""
    peers = load_peers()
    if 0 <= index < len(peers):
        return peers[index]
    return None


def encrypt_and_embed(file_path, peer, my_identity, cover_image_path):
    """Encrypt file and embed in image using steganography"""
    
    # 1. Load keys
    my_priv = PrivateKey(base64.b64decode(my_identity["x25519_private"]))
    peer_pub = PublicKey(base64.b64decode(peer["x25519_public"]))
    box = Box(my_priv, peer_pub)
    
    # 2. Read file
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    print(f"   File size: {len(file_data)} bytes")
    
    # 3. Encrypt using NaCl
    encrypted_data = box.encrypt(file_data)
    print(f"   Encrypted size: {len(encrypted_data)} bytes")
    
    # 4. Sign the encrypted data
    signing_key = SigningKey(base64.b64decode(my_identity["signing_private"]))
    signed_data = signing_key.sign(encrypted_data)
    
    # 5. Create metadata
    file_name = os.path.basename(file_path)
    metadata = {
        "file_name": file_name,
        "sender": my_identity["username"],
        "signed_data": base64.b64encode(signed_data).decode()
    }
    
    # 6. Convert to bytes for embedding
    payload = json.dumps(metadata).encode('utf-8')
    print(f"   Total payload: {len(payload)} bytes")
    
    # 7. Embed in image using DWT+DCT steganography
    print(f"   Embedding in: {cover_image_path}")
    stego_image = embed_in_dwt_bands(cover_image_path, payload)
    
    # 8. Save stego image
    stego_filename = f"stego_{os.path.basename(cover_image_path)}"
    cv2.imwrite(stego_filename, stego_image)
    print(f"   ✓ Stego image saved: {stego_filename}")
    
    return stego_filename, payload


def send_stego_image(stego_image_path, peer_ip):
    """Send stego image over network"""
    try:
        # Read stego image
        with open(stego_image_path, 'rb') as f:
            image_data = f.read()
        
        # Create socket and send
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((peer_ip, TRANSFER_PORT))
        
        # Send image size first (4 bytes)
        import struct
        sock.sendall(struct.pack('!I', len(image_data)))
        
        # Send image data
        sock.sendall(image_data)
        sock.close()
        
        print(f"   ✓ Stego image sent to {peer_ip}:{TRANSFER_PORT}")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed to send: {e}")
        return False


def main():
    """Main sender program"""
    print("="*70)
    print("LAYERX STEGANOGRAPHIC SECURE FILE TRANSFER - SENDER")
    print("="*70)
    
    # Load or create identity
    my_identity = load_or_create_identity()
    
    while True:
        print("\n--- Main Menu ---")
        print("1. List peers")
        print("2. Add new peer")
        print("3. Send file")
        print("4. Show my public key")
        print("5. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            list_peers()
            
        elif choice == "2":
            add_peer()
            
        elif choice == "3":
            # Send file
            peers = list_peers()
            if not peers:
                continue
            
            try:
                peer_idx = int(input("\nSelect peer number: ")) - 1
                peer = get_peer_by_index(peer_idx)
                
                if not peer:
                    print("⚠️  Invalid peer selection")
                    continue
                
                file_path = input("File to send: ").strip().strip('"')
                
                if not os.path.exists(file_path):
                    print(f"⚠️  File not found: {file_path}")
                    continue
                
                cover_image = input("Cover image (default: test_lena.png): ").strip() or "test_lena.png"
                
                if not os.path.exists(cover_image):
                    print(f"⚠️  Cover image not found: {cover_image}")
                    continue
                
                print(f"\n📤 Sending '{file_path}' to {peer['username']} ({peer['ip']})...")
                
                # Encrypt and embed
                stego_path, payload = encrypt_and_embed(file_path, peer, my_identity, cover_image)
                
                # Send stego image
                if send_stego_image(stego_path, peer['ip']):
                    print(f"\n✅ File sent successfully!")
                else:
                    print(f"\n❌ Failed to send file")
                
            except ValueError:
                print("⚠️  Invalid input")
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        elif choice == "4":
            print(f"\n--- Your Public Keys ---")
            print(f"Username: {my_identity['username']}")
            print(f"X25519 Public Key:\n{my_identity['x25519_public']}")
            print(f"Signing Public Key:\n{my_identity['signing_public']}")
            
        elif choice == "5":
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
