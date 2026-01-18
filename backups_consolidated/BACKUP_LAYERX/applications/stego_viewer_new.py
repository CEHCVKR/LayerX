"""
LayerX Stego Image Viewer - Split Panel Layout
Features:
- Left panel (65%): Image display
- Right panel (35%): Controls + Message display
- Shows sender info, timestamp, and decrypted message
"""

import sys
import os
import json
import base64
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import decrypt_message
from a3_image_processing_color import read_image_color, dwt_decompose_color
from a4_compression import decompress_huffman, parse_payload
from a5_embedding_extraction import extract_from_dwt_bands_color, bits_to_bytes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def extract_hidden_message(stego_image_path, salt, iv, payload_bits_length):
    """Extract and decrypt hidden message from stego image"""
    stego_img = read_image_color(stego_image_path)
    bands = dwt_decompose_color(stego_img, levels=2)
    extracted_bits = extract_from_dwt_bands_color(bands, payload_bits_length, Q_factor=5.0)
    extracted_payload = bits_to_bytes(extracted_bits)
    
    msg_len, tree, compressed = parse_payload(extracted_payload)
    decrypted_ciphertext = decompress_huffman(compressed, tree)
    message = decrypt_message(decrypted_ciphertext, "temp_password", salt, iv)
    
    return message


class StegoViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LayerX Stego Viewer")
        self.root.geometry("1200x750")
        
        self.metadata = None
        self.stego_image_path = None
        self.identity = None
        self.message_text = None
        self.secret_button = None
        self.export_button = None
        self.decrypted_message = None
        self.dark_mode = True  # Default theme
        
        # Theme colors
        self.themes = {
            'dark': {
                'bg': '#2b2b2b',
                'title_bg': '#1a1a1a',
                'title_fg': '#00ff88',
                'text_bg': '#0a0a0a',
                'text_fg': '#cccccc',
                'frame_bg': '#1a1a1a',
                'status_fg': '#888888'
            },
            'light': {
                'bg': '#f0f0f0',
                'title_bg': '#ffffff',
                'title_fg': '#2e7d32',
                'text_bg': '#ffffff',
                'text_fg': '#000000',
                'frame_bg': '#ffffff',
                'status_fg': '#666666'
            }
        }
        
        self.root.configure(bg=self.themes['dark']['bg'])
        
        # Load identity
        self.load_identity()
        
        # Create UI
        self.create_ui()
        
        # Enable drag and drop
        self.setup_drag_drop()
        
    def load_identity(self):
        """Load receiver's identity"""
        if os.path.exists("my_identity.json"):
            with open("my_identity.json", 'r') as f:
                self.identity = json.load(f)
    
    def setup_drag_drop(self):
        """Setup drag and drop for files"""
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            # Enable drag-drop on image label
            self.image_label.drop_target_register(DND_FILES)
            self.image_label.dnd_bind('<<Drop>>', self.on_image_drop)
        except ImportError:
            print("[!] tkinterdnd2 not installed - drag & drop disabled")
            print("[!] Install with: pip install tkinterdnd2")
    
    def on_image_drop(self, event):
        """Handle dropped image file"""
        filepath = event.data
        # Remove curly braces if present
        if filepath.startswith('{') and filepath.endswith('}'):
            filepath = filepath[1:-1]
        
        if filepath.lower().endswith('.png'):
            self.load_image_file(filepath)
            # Auto-detect matching metadata
            self.auto_detect_metadata(filepath)
        elif filepath.lower().endswith('.json'):
            self.load_metadata_file(filepath)
    
    def auto_detect_metadata(self, image_path):
        """Auto-detect matching metadata JSON file"""
        # Extract timestamp from image filename
        import re
        match = re.search(r'(\d{8}_\d{6})', os.path.basename(image_path))
        if match:
            timestamp = match.group(1)
            metadata_file = f"encrypted_metadata_{timestamp}.json"
            
            if os.path.exists(metadata_file):
                print(f"[+] Auto-detected metadata: {metadata_file}")
                self.load_metadata_file(metadata_file)
                self.status_label.config(
                    text=f"✓ Auto-loaded metadata: {metadata_file}",
                    fg=self.get_theme_color('title_fg')
                )
    
    def get_theme_color(self, key):
        """Get color for current theme"""
        theme = 'dark' if self.dark_mode else 'light'
        return self.themes[theme][key]
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = not self.dark_mode
        theme = 'dark' if self.dark_mode else 'light'
        
        # Update all widgets with new theme
        self.root.configure(bg=self.themes[theme]['bg'])
        # Would need to update all widgets - simplified for now
        self.status_label.config(
            text=f"{'🌙 Dark' if self.dark_mode else '☀️ Light'} theme activated",
            fg=self.themes[theme]['title_fg']
        )
    
    def create_ui(self):
        """Create user interface - Split panel layout"""
        
        # Title bar
        title_frame = tk.Frame(self.root, bg='#1a1a1a', height=60)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="🌈 LayerX Stego Viewer",
            font=('Arial', 20, 'bold'),
            bg='#1a1a1a',
            fg='#00ff88'
        )
        title_label.pack(pady=10)
        
        # User info (if logged in)
        if self.identity:
            user_label = tk.Label(
                title_frame,
                text=f"👤 {self.identity['username']} | 🔑 {self.identity['address'][:12]}...",
                font=('Arial', 10),
                bg='#1a1a1a',
                fg='#888888'
            )
            user_label.pack()
        
        # Main content frame (2 halves: left 65% + right 35%)
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === LEFT PANEL - Image display (65% width) ===
        left_frame = tk.Frame(main_frame, bg='#1a1a1a')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.image_label = tk.Label(
            left_frame,
            text="No image loaded\n\nClick 'Load Image' to begin",
            font=('Arial', 14),
            bg='#1a1a1a',
            fg='#666666'
        )
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === RIGHT PANEL - Controls and Message (35% width) ===
        right_frame = tk.Frame(main_frame, bg='#2b2b2b', width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # RIGHT TOP - Control Buttons
        button_frame = tk.Frame(right_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(10, 20), padx=10)
        
        tk.Label(
            button_frame,
            text="CONTROLS",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='#00ff88'
        ).pack(pady=(0, 10))
        
        open_btn = tk.Button(
            button_frame,
            text="📂 Load Image",
            command=self.open_image,
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        open_btn.pack(fill=tk.X, pady=5)
        
        load_meta_btn = tk.Button(
            button_frame,
            text="🔐 Load Metadata",
            command=self.load_metadata,
            font=('Arial', 11, 'bold'),
            bg='#2196F3',
            fg='white',
            cursor='hand2',
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        load_meta_btn.pack(fill=tk.X, pady=5)
        
        # Theme toggle button
        theme_btn = tk.Button(
            button_frame,
            text="🌙 Toggle Theme",
            command=self.toggle_theme,
            font=('Arial', 10),
            bg='#9C27B0',
            fg='white',
            cursor='hand2',
            pady=8,
            relief=tk.RAISED,
            borderwidth=2
        )
        theme_btn.pack(fill=tk.X, pady=5)
        
        # Secret reveal button
        self.secret_button = tk.Button(
            button_frame,
            text="🔓 REVEAL MESSAGE",
            command=self.reveal_message,
            font=('Arial', 12, 'bold'),
            bg='#FF5722',
            fg='white',
            cursor='hand2',
            pady=12,
            state=tk.DISABLED,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.secret_button.pack(fill=tk.X, pady=(15, 5))
        
        # Export message button
        export_btn = tk.Button(
            button_frame,
            text="📤 Export Message",
            command=self.export_message,
            font=('Arial', 10),
            bg='#607D8B',
            fg='white',
            cursor='hand2',
            pady=8,
            state=tk.DISABLED,
            relief=tk.RAISED,
            borderwidth=2
        )
        export_btn.pack(fill=tk.X, pady=5)
        self.export_button = export_btn
        
        # RIGHT BOTTOM - Message Display Area
        tk.Label(
            right_frame,
            text="MESSAGE INFO",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='#00ff88'
        ).pack(pady=(20, 5), padx=10)
        
        # Message info frame with border
        message_info_frame = tk.Frame(right_frame, bg='#1a1a1a', relief=tk.SUNKEN, borderwidth=2)
        message_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollable text widget for message
        scroll_y = tk.Scrollbar(message_info_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.message_text = tk.Text(
            message_info_frame,
            font=('Consolas', 9),
            bg='#0a0a0a',
            fg='#cccccc',
            wrap=tk.WORD,
            padx=10,
            pady=10,
            state=tk.DISABLED,
            yscrollcommand=scroll_y.set
        )
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_y.config(command=self.message_text.yview)
        
        # Initial message
        self.update_message_display("Waiting for data...", "", "", "")
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready | Load image and metadata to decrypt",
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#888888',
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
    
    def open_image(self):
        """Open and display stego image"""
        filepath = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filepath:
            self.load_image_file(filepath)
            self.auto_detect_metadata(filepath)
    
    def load_image_file(self, filepath):
        """Load and display image file"""
        try:
            # Load and display image
            img = Image.open(filepath)
            
            # Resize to fit display (maintain aspect ratio)
            max_width, max_height = 700, 650
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep reference
            
            self.stego_image_path = filepath
            self.status_label.config(
                text=f"✓ Image: {os.path.basename(filepath)} | Drag metadata JSON or click Load",
                fg='#00ff88'
            )
            
            # Enable reveal button if metadata is loaded
            self.check_enable_reveal_button()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")
    
    def load_metadata(self):
        """Load encrypted metadata JSON"""
        filepath = filedialog.askopenfilename(
            title="Select Encrypted Metadata JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            self.load_metadata_file(filepath)
    
    def load_metadata_file(self, filepath):
        """Load metadata from file"""
        try:
            with open(filepath, 'r') as f:
                encrypted_package = json.load(f)
            
            # Decrypt metadata
            metadata = self.decrypt_metadata(encrypted_package)
            self.metadata = metadata
            
            self.status_label.config(
                text=f"✓ Metadata: {os.path.basename(filepath)} | Click REVEAL MESSAGE",
                fg='#00ff88'
            )
            
            # Update message info display
            self.update_message_display(
                "Ready to decrypt",
                self.metadata.get('sender_ip', self.metadata.get('sender_address', 'Unknown')),
                self.metadata.get('received_timestamp', self.metadata.get('timestamp', 'Unknown')),
                "Click 'REVEAL MESSAGE' button to decrypt..."
            )
            
            # Enable reveal button
            self.check_enable_reveal_button()
            
        except Exception as e:
            
                # Enable reveal button
                self.check_enable_reveal_button()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load metadata:\n{e}")
    
    def decrypt_metadata(self, encrypted_package):
        """Decrypt metadata using private key"""
        encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
        aes_key = base64.b64decode(encrypted_package['aes_key'])
        aes_iv = base64.b64decode(encrypted_package['aes_iv'])
        
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(aes_iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_json = decryptor.update(encrypted_data) + decryptor.finalize()
        
        return json.loads(decrypted_json.decode('utf-8'))
    
    def check_enable_reveal_button(self):
        """Enable reveal button if both image and metadata are loaded"""
        if self.stego_image_path and self.metadata:
            self.secret_button.config(state=tk.NORMAL, bg='#FF5722')
            self.status_label.config(text="✓ READY! Click 'REVEAL MESSAGE' to decrypt", fg='#00ff88')
    
    def update_message_display(self, status, sender_ip="", timestamp="", message=""):
        """Update the message display area"""
        self.message_text.config(state=tk.NORMAL)
        self.message_text.delete('1.0', tk.END)
        
        # Format the display
        content = f"{'='*45}\n"
        content += f"  STATUS: {status}\n"
        content += f"{'='*45}\n\n"
        
        if sender_ip:
            content += f"📡 SENDER IP:\n    {sender_ip}\n\n"
        
        if timestamp:
            content += f"📅 RECEIVED:\n    {timestamp}\n\n"
        
        if message and status == "DECRYPTED ✓":
            content += f"💬 MESSAGE:\n"
            content += f"{'-'*45}\n"
            content += f"{message}\n"
            content += f"{'-'*45}\n"
        elif message:
            content += f"{message}\n"
        
        self.message_text.insert('1.0', content)
        self.message_text.config(state=tk.DISABLED)
    
    def reveal_message(self):
        """Extract and display hidden message"""
        if not self.stego_image_path or not self.metadata:
            messagebox.showwarning("Warning", "Please load both image and metadata first!")
            return
        
        try:
            # Show progress
            self.status_label.config(text="⏳ Extracting hidden message...", fg='#ffaa00')
            self.secret_button.config(state=tk.DISABLED, text="DECRYPTING...")
            self.root.update()
            
            # Decode salt and IV
            salt = base64.b64decode(self.metadata['salt'])
            iv = base64.b64decode(self.metadata['iv'])
            
            # Extract message
            message = extract_hidden_message(
                self.metadata['stego_image'],
                salt,
                iv,
                self.metadata['payload_bits_length']
            )
            
            # Display message in the right panel
            self.update_message_display(
                "DECRYPTED ✓",
                self.metadata.get('sender_ip', 'Unknown'),
                self.metadata.get('received_timestamp', 'Unknown'),
                message
            )
            
            self.status_label.config(text="✅ Message revealed successfully!", fg='#00ff88')
            # Store decrypted message and enable export
            self.decrypted_message = message
            self.export_button.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract message:\n{e}")
            self.status_label.config(text="❌ Failed to extract message", fg='#ff0000')
            self.secret_button.config(state=tk.NORMAL, text="🔓 REVEAL MESSAGE")
    
    def export_message(self):
        """Export decrypted message to text file"""
        if not self.decrypted_message:
            messagebox.showwarning("Warning", "No message to export! Reveal the message first.")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Export Message",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("="*60 + "\n")
                    f.write("LayerX Steganography - Exported Message\n")
                    f.write("="*60 + "\n\n")
                    
                    if self.metadata:
                        f.write(f"From: {self.metadata.get('sender_username', 'Unknown')}\n")
                        f.write(f"Address: {self.metadata.get('sender_address', 'Unknown')}\n")
                        f.write(f"Timestamp: {self.metadata.get('timestamp', 'Unknown')}\n")
                        f.write(f"Received: {self.metadata.get('received_timestamp', 'Unknown')}\n")
                    
                    f.write("\n" + "="*60 + "\n")
                    f.write("MESSAGE:\n")
                    f.write("="*60 + "\n\n")
                    f.write(self.decrypted_message)
                    f.write("\n\n" + "="*60 + "\n")
                    f.write(f"Exported: {datetime.now().isoformat()}\n")
                    f.write("="*60 + "\n")
                
                self.status_label.config(text=f"✅ Message exported to: {os.path.basename(filepath)}", fg='#00ff88')
                messagebox.showinfo("Success", f"Message exported successfully!\n\n{filepath}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export message:\n{e}
            self.status_label.config(text="❌ Failed to extract message", fg='#ff0000')
            self.secret_button.config(state=tk.NORMAL, text="🔓 REVEAL MESSAGE")


def main():
    root = tk.Tk()
    app = StegoViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
