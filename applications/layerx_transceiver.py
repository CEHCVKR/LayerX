"""
LayerX Transceiver - Combined Sender & Receiver
Features:
- Simultaneous send and receive capabilities
- Automatic peer discovery (UDP broadcast)
- Tabbed GUI interface (Send | Receive | Peers)
- Parallel operations using threading
- Username + automatic ECC key generation
- Full steganographic pipeline
"""

import sys
import os
import json
import socket
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from datetime import datetime
from pathlib import Path

# Add module paths
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir / "core_modules"))

from a1_encryption import encrypt_message, decrypt_message
from a2_key_management import generate_ecc_keypair, serialize_public_key, serialize_private_key, deserialize_public_key
from a3_image_processing_color import read_image_color, dwt_decompose_color, dwt_reconstruct_color, psnr_color
from scipy.fftpack import dct, idct
from a4_compression import compress_huffman, create_payload, decompress_huffman, parse_payload
from a5_embedding_extraction import embed_in_dwt_bands_color, bytes_to_bits, extract_from_dwt_bands_color, bits_to_bytes
from a6_optimization import optimize_coefficients_aco, select_coefficients_chaos
import numpy as np
import cv2

# Configuration
IDENTITY_FILE = "my_identity.json"
BROADCAST_PORT = 37020
DISCOVERY_INTERVAL = 5
FILE_TRANSFER_PORT = 37021
peers_list = {}
peers_lock = threading.Lock()
running = True

# Helper functions
def apply_dct(band):
    """Apply 2D DCT to a band"""
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    """Apply inverse 2D DCT to a band"""
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

def write_image(path, img):
    """Write image to file"""
    cv2.imwrite(path, img.astype(np.uint8))

def load_or_create_identity():
    """Load existing identity or create new one"""
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, 'r') as f:
            identity = json.load(f)
        print(f"[+] Loaded identity: {identity['username']}")
        return identity
    else:
        username = input("Enter your username: ").strip()
        if not username:
            username = f"user_{os.urandom(4).hex()}"
        
        print(f"[+] Generating ECC keypair for {username}...")
        private_key, public_key = generate_ecc_keypair()
        
        identity = {
            "username": username,
            "private_key": serialize_private_key(private_key),
            "public_key": serialize_public_key(public_key),
            "created": datetime.now().isoformat()
        }
        
        with open(IDENTITY_FILE, 'w') as f:
            json.dump(identity, f, indent=2)
        
        print(f"[✓] Identity created and saved to {IDENTITY_FILE}")
        return identity

# Peer Discovery
def peer_discovery_listener(identity, app):
    """Listen for peer announcements"""
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', BROADCAST_PORT))
    sock.settimeout(1.0)
    
    print(f"[+] Listening for peers on port {BROADCAST_PORT}")
    
    while running:
        try:
            data, addr = sock.recvfrom(4096)
            announcement = json.loads(data.decode())
            
            if announcement['username'] != identity['username']:
                with peers_lock:
                    peers_list[announcement['username']] = {
                        'ip': addr[0],
                        'public_key': announcement['public_key'],
                        'last_seen': time.time()
                    }
                    app.update_peers_list()
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"[!] Listener error: {e}")
    
    sock.close()

def peer_discovery_announcer(identity):
    """Announce presence to network"""
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    announcement = {
        'username': identity['username'],
        'public_key': identity['public_key']
    }
    
    while running:
        try:
            sock.sendto(json.dumps(announcement).encode(), ('<broadcast>', BROADCAST_PORT))
            time.sleep(DISCOVERY_INTERVAL)
        except Exception as e:
            if running:
                print(f"[!] Announcer error: {e}")
    
    sock.close()

# File Transfer
def receive_file_listener(app):
    """Listen for incoming file transfers"""
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', FILE_TRANSFER_PORT))
    sock.listen(5)
    sock.settimeout(1.0)
    
    print(f"[+] File transfer listener on port {FILE_TRANSFER_PORT}")
    
    while running:
        try:
            conn, addr = sock.accept()
            threading.Thread(target=handle_file_transfer, args=(conn, addr, app), daemon=True).start()
        except socket.timeout:
            continue
        except Exception as e:
            if running:
                print(f"[!] File listener error: {e}")
    
    sock.close()

def handle_file_transfer(conn, addr, app):
    """Handle incoming file transfer"""
    try:
        # Receive metadata
        metadata_size = int.from_bytes(conn.recv(4), 'big')
        metadata = json.loads(conn.recv(metadata_size).decode())
        
        # Receive file
        file_size = metadata['file_size']
        filename = metadata['filename']
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"received_{timestamp}_{filename}"
        
        received = 0
        with open(save_path, 'wb') as f:
            while received < file_size:
                chunk = conn.recv(min(4096, file_size - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
        
        app.log_receive(f"✓ Received {filename} ({file_size} bytes) from {addr[0]}")
        app.log_receive(f"  Saved as: {save_path}")
        
        # Auto-load metadata if JSON
        if filename.endswith('.json'):
            base_name = os.path.splitext(filename)[0]
            img_path = f"received_{timestamp}_{base_name.replace('_metadata', '_stego')}.png"
            if os.path.exists(img_path):
                app.log_receive(f"  ℹ Matching image found: {img_path}")
    
    except Exception as e:
        app.log_receive(f"[!] Transfer error: {e}")
    finally:
        conn.close()

def send_file(ip, filepath, app):
    """Send file to peer"""
    try:
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        
        metadata = {
            'filename': filename,
            'file_size': file_size,
            'timestamp': datetime.now().isoformat()
        }
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, FILE_TRANSFER_PORT))
        
        # Send metadata
        metadata_bytes = json.dumps(metadata).encode()
        sock.send(len(metadata_bytes).to_bytes(4, 'big'))
        sock.send(metadata_bytes)
        
        # Send file
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                sock.send(chunk)
        
        sock.close()
        app.log_send(f"✓ Sent {filename} to {ip}")
        return True
    
    except Exception as e:
        app.log_send(f"[!] Failed to send file: {e}")
        return False

# Steganography Pipeline
def embed_message_pipeline(cover_path, message, identity, recipient_username):
    """Complete embedding pipeline"""
    try:
        # 1. Encrypt message
        print("[1/7] Encrypting message...")
        with peers_lock:
            if recipient_username not in peers_list:
                print("[!] Recipient not found in peers list")
                return None, None, None, None
            recipient_key = peers_list[recipient_username]['public_key']
        
        encrypted_msg, salt, iv = encrypt_message(message, recipient_key)
        
        # 2. Compress
        print("[2/7] Compressing...")
        compressed = compress_huffman(encrypted_msg)
        payload = create_payload(compressed)
        
        # 3. Convert to bits
        print("[3/7] Converting to bits...")
        payload_bits = bytes_to_bits(payload)
        
        # 4. Read image
        print("[4/7] Reading cover image...")
        cover_img = read_image_color(cover_path)
        
        # 5. DWT Decomposition
        print("[5/7] Applying DWT...")
        dwt_bands = dwt_decompose_color(cover_img)
        
        # 6. Embed in DWT-DCT
        print("[6/7] Embedding in DWT-DCT bands...")
        modified_bands = embed_in_dwt_bands_color(dwt_bands, payload_bits, Q=5.0)
        
        # 7. Reconstruct
        print("[7/7] Reconstructing stego image...")
        stego_img = dwt_reconstruct_color(modified_bands)
        
        # Calculate PSNR
        psnr = psnr_color(cover_img, stego_img)
        print(f"[✓] PSNR: {psnr:.2f} dB")
        
        return stego_img, salt.hex(), iv.hex(), psnr
    
    except Exception as e:
        print(f"[!] Embedding error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None

def extract_message_pipeline(stego_path, salt_hex, iv_hex, identity):
    """Complete extraction pipeline"""
    try:
        # 1. Read stego image
        print("[1/5] Reading stego image...")
        stego_img = read_image_color(stego_path)
        
        # 2. DWT Decomposition
        print("[2/5] Applying DWT...")
        dwt_bands = dwt_decompose_color(stego_img)
        
        # 3. Extract from DWT-DCT
        print("[3/5] Extracting from DWT-DCT bands...")
        extracted_bits = extract_from_dwt_bands_color(dwt_bands, Q=5.0)
        
        # 4. Decompress
        print("[4/5] Decompressing...")
        extracted_bytes = bits_to_bytes(extracted_bits)
        payload_data = parse_payload(extracted_bytes)
        decompressed = decompress_huffman(payload_data)
        
        # 5. Decrypt
        print("[5/5] Decrypting message...")
        salt = bytes.fromhex(salt_hex)
        iv = bytes.fromhex(iv_hex)
        message = decrypt_message(decompressed, identity['private_key'], salt, iv)
        
        print(f"[✓] Message extracted: {len(message)} characters")
        return message
    
    except Exception as e:
        print(f"[!] Extraction error: {e}")
        import traceback
        traceback.print_exc()
        return None

# GUI Application
class LayerXTransceiver:
    def __init__(self, root, identity):
        self.root = root
        self.identity = identity
        self.root.title(f"LayerX Transceiver - {identity['username']}")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Create notebook (tabs)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', background='#3b3b3b', foreground='white', padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#1a1a1a')])
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.send_tab = tk.Frame(self.notebook, bg='#2b2b2b')
        self.receive_tab = tk.Frame(self.notebook, bg='#2b2b2b')
        self.peers_tab = tk.Frame(self.notebook, bg='#2b2b2b')
        
        self.notebook.add(self.send_tab, text='📤 Send')
        self.notebook.add(self.receive_tab, text='📥 Receive')
        self.notebook.add(self.peers_tab, text='👥 Peers')
        
        self.create_send_ui()
        self.create_receive_ui()
        self.create_peers_ui()
        
    def create_send_ui(self):
        """Create sender interface"""
        # Title
        tk.Label(self.send_tab, text="Send Encrypted Message", font=('Arial', 16, 'bold'),
                bg='#2b2b2b', fg='#00ff88').pack(pady=10)
        
        # Cover Image
        frame1 = tk.Frame(self.send_tab, bg='#2b2b2b')
        frame1.pack(pady=5, padx=20, fill=tk.X)
        tk.Label(frame1, text="Cover Image:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.send_cover_path = tk.StringVar()
        tk.Entry(frame1, textvariable=self.send_cover_path, width=50, bg='#3b3b3b', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="Browse", command=self.browse_cover, bg='#00aa66', fg='white').pack(side=tk.LEFT)
        
        # Recipient
        frame2 = tk.Frame(self.send_tab, bg='#2b2b2b')
        frame2.pack(pady=5, padx=20, fill=tk.X)
        tk.Label(frame2, text="Recipient:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.send_recipient = ttk.Combobox(frame2, width=30, state='readonly')
        self.send_recipient.pack(side=tk.LEFT, padx=5)
        tk.Button(frame2, text="Refresh", command=self.refresh_recipients, bg='#0088cc', fg='white').pack(side=tk.LEFT)
        
        # Message
        tk.Label(self.send_tab, text="Message:", bg='#2b2b2b', fg='white').pack(anchor=tk.W, padx=20, pady=(10,0))
        self.send_message = scrolledtext.ScrolledText(self.send_tab, height=10, width=80, bg='#3b3b3b', fg='white')
        self.send_message.pack(pady=5, padx=20)
        
        # Send Button
        tk.Button(self.send_tab, text="🚀 Send Message", command=self.send_message_action,
                 bg='#00aa66', fg='white', font=('Arial', 12, 'bold'), pady=10).pack(pady=10)
        
        # Log
        tk.Label(self.send_tab, text="Log:", bg='#2b2b2b', fg='white').pack(anchor=tk.W, padx=20)
        self.send_log = scrolledtext.ScrolledText(self.send_tab, height=8, width=80, bg='#1a1a1a', fg='#00ff88')
        self.send_log.pack(pady=5, padx=20)
    
    def create_receive_ui(self):
        """Create receiver interface"""
        # Title
        tk.Label(self.receive_tab, text="Receive Encrypted Message", font=('Arial', 16, 'bold'),
                bg='#2b2b2b', fg='#00ff88').pack(pady=10)
        
        # Stego Image
        frame1 = tk.Frame(self.receive_tab, bg='#2b2b2b')
        frame1.pack(pady=5, padx=20, fill=tk.X)
        tk.Label(frame1, text="Stego Image:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.recv_stego_path = tk.StringVar()
        tk.Entry(frame1, textvariable=self.recv_stego_path, width=50, bg='#3b3b3b', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="Browse", command=self.browse_stego, bg='#00aa66', fg='white').pack(side=tk.LEFT)
        
        # Salt
        frame2 = tk.Frame(self.receive_tab, bg='#2b2b2b')
        frame2.pack(pady=5, padx=20, fill=tk.X)
        tk.Label(frame2, text="Salt (hex):", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.recv_salt = tk.Entry(frame2, width=60, bg='#3b3b3b', fg='white')
        self.recv_salt.pack(side=tk.LEFT, padx=5)
        
        # IV
        frame3 = tk.Frame(self.receive_tab, bg='#2b2b2b')
        frame3.pack(pady=5, padx=20, fill=tk.X)
        tk.Label(frame3, text="IV (hex):", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.recv_iv = tk.Entry(frame3, width=60, bg='#3b3b3b', fg='white')
        self.recv_iv.pack(side=tk.LEFT, padx=5)
        
        # Receive Button
        tk.Button(self.receive_tab, text="📥 Decrypt Message", command=self.receive_message_action,
                 bg='#0088cc', fg='white', font=('Arial', 12, 'bold'), pady=10).pack(pady=10)
        
        # Decrypted Message
        tk.Label(self.receive_tab, text="Decrypted Message:", bg='#2b2b2b', fg='white').pack(anchor=tk.W, padx=20)
        self.recv_message = scrolledtext.ScrolledText(self.receive_tab, height=10, width=80, bg='#3b3b3b', fg='white')
        self.recv_message.pack(pady=5, padx=20)
        
        # Log
        tk.Label(self.receive_tab, text="Log:", bg='#2b2b2b', fg='white').pack(anchor=tk.W, padx=20)
        self.recv_log = scrolledtext.ScrolledText(self.receive_tab, height=8, width=80, bg='#1a1a1a', fg='#00ff88')
        self.recv_log.pack(pady=5, padx=20)
    
    def create_peers_ui(self):
        """Create peers list interface"""
        # Title
        tk.Label(self.peers_tab, text="Discovered Peers", font=('Arial', 16, 'bold'),
                bg='#2b2b2b', fg='#00ff88').pack(pady=10)
        
        # Refresh button
        tk.Button(self.peers_tab, text="🔄 Refresh", command=self.update_peers_list,
                 bg='#0088cc', fg='white').pack(pady=5)
        
        # Peers listbox
        self.peers_listbox = tk.Listbox(self.peers_tab, height=25, width=100, bg='#3b3b3b', fg='white',
                                       font=('Courier', 10))
        self.peers_listbox.pack(pady=10, padx=20)
    
    def browse_cover(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if filepath:
            self.send_cover_path.set(filepath)
    
    def browse_stego(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if filepath:
            self.recv_stego_path.set(filepath)
    
    def refresh_recipients(self):
        with peers_lock:
            usernames = list(peers_list.keys())
        self.send_recipient['values'] = usernames
        if usernames:
            self.send_recipient.current(0)
    
    def update_peers_list(self):
        self.peers_listbox.delete(0, tk.END)
        with peers_lock:
            if not peers_list:
                self.peers_listbox.insert(tk.END, "No peers discovered yet...")
            else:
                for username, info in peers_list.items():
                    elapsed = time.time() - info['last_seen']
                    self.peers_listbox.insert(tk.END, f"👤 {username:20s} | IP: {info['ip']:15s} | Last seen: {elapsed:.0f}s ago")
    
    def log_send(self, msg):
        self.send_log.insert(tk.END, msg + "\n")
        self.send_log.see(tk.END)
    
    def log_receive(self, msg):
        self.recv_log.insert(tk.END, msg + "\n")
        self.recv_log.see(tk.END)
    
    def send_message_action(self):
        """Send message in separate thread"""
        threading.Thread(target=self._send_message_thread, daemon=True).start()
    
    def _send_message_thread(self):
        try:
            cover_path = self.send_cover_path.get()
            recipient = self.send_recipient.get()
            message = self.send_message.get("1.0", tk.END).strip()
            
            if not cover_path or not os.path.exists(cover_path):
                self.log_send("[!] Please select a valid cover image")
                return
            
            if not recipient:
                self.log_send("[!] Please select a recipient")
                return
            
            if not message:
                self.log_send("[!] Please enter a message")
                return
            
            self.log_send(f"\n[*] Sending to {recipient}...")
            
            # Embed message
            stego_img, salt_hex, iv_hex, psnr = embed_message_pipeline(cover_path, message, self.identity, recipient)
            
            if stego_img is None:
                self.log_send("[!] Failed to embed message")
                return
            
            # Save stego image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with peers_lock:
                recipient_ip = peers_list[recipient]['ip']
            
            stego_filename = f"{self.identity['username']}_{timestamp}_{recipient_ip.replace('.', '')}.png"
            write_image(stego_filename, stego_img)
            self.log_send(f"[✓] Stego image created: {stego_filename}")
            self.log_send(f"[✓] PSNR: {psnr:.2f} dB")
            
            # Save metadata
            metadata_filename = stego_filename.replace('.png', '.json')
            metadata = {
                'salt': salt_hex,
                'iv': iv_hex,
                'sender_username': self.identity['username'],
                'sender_address': recipient_ip,
                'timestamp': datetime.now().isoformat(),
                'psnr': psnr
            }
            with open(metadata_filename, 'w') as f:
                json.dump(metadata, f, indent=2)
            self.log_send(f"[✓] Metadata saved: {metadata_filename}")
            
            # Send files to recipient
            self.log_send(f"[*] Transferring files to {recipient_ip}...")
            if send_file(recipient_ip, stego_filename, self):
                send_file(recipient_ip, metadata_filename, self)
                self.log_send("[✓] Transfer complete!\n")
            
        except Exception as e:
            self.log_send(f"[!] Error: {e}\n")
            import traceback
            traceback.print_exc()
    
    def receive_message_action(self):
        """Receive message in separate thread"""
        threading.Thread(target=self._receive_message_thread, daemon=True).start()
    
    def _receive_message_thread(self):
        try:
            stego_path = self.recv_stego_path.get()
            salt_hex = self.recv_salt.get().strip()
            iv_hex = self.recv_iv.get().strip()
            
            if not stego_path or not os.path.exists(stego_path):
                self.log_receive("[!] Please select a valid stego image")
                return
            
            if not salt_hex or not iv_hex:
                self.log_receive("[!] Please enter salt and IV")
                return
            
            self.log_receive(f"\n[*] Extracting message from {os.path.basename(stego_path)}...")
            
            message = extract_message_pipeline(stego_path, salt_hex, iv_hex, self.identity)
            
            if message:
                self.recv_message.delete("1.0", tk.END)
                self.recv_message.insert("1.0", message)
                self.log_receive(f"[✓] Message decrypted successfully!\n")
            else:
                self.log_receive("[!] Failed to extract message\n")
        
        except Exception as e:
            self.log_receive(f"[!] Error: {e}\n")
            import traceback
            traceback.print_exc()

def main():
    """Main application"""
    global running
    
    # Load or create identity
    identity = load_or_create_identity()
    
    # Create GUI
    root = tk.Tk()
    app = LayerXTransceiver(root, identity)
    
    # Start background threads
    listener_thread = threading.Thread(target=peer_discovery_listener, args=(identity, app), daemon=True)
    announcer_thread = threading.Thread(target=peer_discovery_announcer, args=(identity,), daemon=True)
    file_thread = threading.Thread(target=receive_file_listener, args=(app,), daemon=True)
    
    listener_thread.start()
    announcer_thread.start()
    file_thread.start()
    
    print("\n" + "="*60)
    print("LAYERX TRANSCEIVER - Ready for Send & Receive")
    print("="*60)
    
    # Handle window close
    def on_closing():
        global running
        running = False
        time.sleep(0.5)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
