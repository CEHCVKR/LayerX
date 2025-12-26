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
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ExifTags
import glob
import time
import threading
from datetime import datetime, timedelta

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
        self.psnr_value = None
        self.self_destruct_timer = None
        self.timer_label = None
        self.timer_thread = None  # Active timer thread
        self.timer_target_path = None  # Path to delete when timer expires
        self.timer_active = False  # Flag to stop running timer
        self.recent_files = []
        self.thumbnail_frame = None
        self.delete_on_close = False  # Flag for self-destruct on close
        
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
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load recent files
        self.load_recent_files()
        
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
            print("[+] Drag & Drop enabled")
        except (ImportError, AttributeError, Exception) as e:
            # Drag & drop not available - not critical
            pass
    
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
        # Try to find matching JSON file
        # New format: username_timestamp_ip.png -> username_timestamp_ip.json
        # Old format: received_stego_timestamp.png -> encrypted_metadata_timestamp.json
        
        print(f"[DEBUG] auto_detect_metadata called for: {image_path}")
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        img_dir = os.path.dirname(image_path)
        print(f"[DEBUG] Looking for metadata in: {img_dir}")
        print(f"[DEBUG] Base name: {base_name}")
        
        # First try: Same base name (new format)
        metadata_file = os.path.join(img_dir, f"{base_name}.json")
        print(f"[DEBUG] Checking for: {metadata_file}")
        print(f"[DEBUG] File exists: {os.path.exists(metadata_file)}")
        
        if os.path.exists(metadata_file):
            print(f"[+] Auto-detected metadata: {metadata_file}")
            self.load_metadata_file(metadata_file)
            self.status_label.config(
                text=f"✓ Auto-loaded metadata: {os.path.basename(metadata_file)}",
                fg=self.get_theme_color('title_fg')
            )
            return
        else:
            print(f"[DEBUG] Metadata file not found at expected path")
        
        # Second try: Old naming pattern (backward compatibility)
        import re
        match = re.search(r'(\d{8}_\d{6})', base_name)
        if match:
            timestamp = match.group(1)
            old_metadata_file = os.path.join(img_dir, f"encrypted_metadata_{timestamp}.json")
            
            if os.path.exists(old_metadata_file):
                print(f"[+] Auto-detected metadata (old format): {old_metadata_file}")
                self.load_metadata_file(old_metadata_file)
                self.status_label.config(
                    text=f"✓ Auto-loaded metadata: {os.path.basename(old_metadata_file)}",
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
        
        # Title bar with gradient effect
        title_frame = tk.Frame(self.root, bg='#0d0d0d', height=80)
        title_frame.pack(fill=tk.X)
        
        # Theme toggle button - top right
        theme_btn = tk.Button(
            title_frame,
            text="🌙",
            command=self.toggle_theme,
            font=('Segoe UI', 16),
            bg='#1a1a1a',
            fg='#6a1b9a',
            activebackground='#2a2a2a',
            cursor='hand2',
            relief=tk.FLAT,
            borderwidth=0,
            width=3,
            height=1
        )
        theme_btn.place(relx=0.98, rely=0.5, anchor='e')
        
        # Main title
        title_label = tk.Label(
            title_frame,
            text="🔐 LayerX",
            font=('Segoe UI', 28, 'bold'),
            bg='#0d0d0d',
            fg='#00ff88'
        )
        title_label.pack(pady=(10, 0))
        
        subtitle_label = tk.Label(
            title_frame,
            text="Steganography Message Viewer",
            font=('Segoe UI', 11),
            bg='#0d0d0d',
            fg='#666666'
        )
        subtitle_label.pack(pady=(0, 5))
        
        # User info (if logged in)
        if self.identity:
            user_frame = tk.Frame(title_frame, bg='#1a1a1a')
            user_frame.pack(pady=5)
            
            user_label = tk.Label(
                user_frame,
                text=f"  👤 {self.identity['username']}  •  🔑 {self.identity['address'][:12]}...  ",
                font=('Consolas', 9),
                bg='#1a1a1a',
                fg='#00ff88',
                relief=tk.FLAT,
                padx=8,
                pady=3
            )
            user_label.pack()
        
        # Main content frame (2 halves: left 65% + right 35%)
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === LEFT PANEL - Image display (65% width) ===
        left_frame = tk.Frame(main_frame, bg='#1a1a1a', relief=tk.SUNKEN, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Image header
        img_header = tk.Frame(left_frame, bg='#0d0d0d', height=40)
        img_header.pack(fill=tk.X)
        img_header.pack_propagate(False)
        
        tk.Label(
            img_header,
            text="🖼️  STEGO IMAGE",
            font=('Segoe UI', 11, 'bold'),
            bg='#0d0d0d',
            fg='#00ff88'
        ).pack(side=tk.LEFT, padx=15, pady=10)
        
        # Image display area with border
        img_container = tk.Frame(left_frame, bg='#0a0a0a', relief=tk.RIDGE, borderwidth=2)
        img_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.image_label = tk.Label(
            img_container,
            text="📂 No Image Loaded\n\n⬇️ Click 'Load Image' or drag & drop PNG file",
            font=('Segoe UI', 13),
            bg='#0a0a0a',
            fg='#555555',
            justify=tk.CENTER
        )
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # === RIGHT PANEL - Controls and Message (35% width) ===
        right_frame = tk.Frame(main_frame, bg='#2b2b2b', width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # RIGHT TOP - Control Buttons
        button_frame = tk.Frame(right_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(8, 15), padx=12)
        
        # Controls header
        controls_header = tk.Frame(button_frame, bg='#0d0d0d', height=35)
        controls_header.pack(fill=tk.X, pady=(0, 12))
        controls_header.pack_propagate(False)
        
        tk.Label(
            controls_header,
            text="⚙️  CONTROLS",
            font=('Segoe UI', 11, 'bold'),
            bg='#0d0d0d',
            fg='#00ff88'
        ).pack(side=tk.LEFT, padx=10, pady=8)
        
        # Load buttons group
        open_btn = tk.Button(
            button_frame,
            text="📂  Load Image",
            command=self.open_image,
            font=('Segoe UI', 11, 'bold'),
            bg='#2e7d32',
            fg='white',
            activebackground='#388e3c',
            cursor='hand2',
            pady=11,
            relief=tk.FLAT,
            borderwidth=0
        )
        open_btn.pack(fill=tk.X, pady=(0, 8), ipady=2)
        
        load_meta_btn = tk.Button(
            button_frame,
            text="🔐  Load Metadata",
            command=self.load_metadata,
            font=('Segoe UI', 11, 'bold'),
            bg='#1565c0',
            fg='white',
            activebackground='#1976d2',
            cursor='hand2',
            pady=11,
            relief=tk.FLAT,
            borderwidth=0
        )
        load_meta_btn.pack(fill=tk.X, pady=(0, 15), ipady=2)
        
        # Divider
        tk.Frame(button_frame, bg='#444444', height=1).pack(fill=tk.X, pady=8)
        
        # Hidden reveal button (auto-triggers on metadata load)
        self.secret_button = tk.Button(
            button_frame,
            text="🔓 REVEAL MESSAGE",
            command=self.reveal_message,
            state=tk.DISABLED
        )
        # Keep button reference but don't pack it (invisible)
        
        # RIGHT BOTTOM - Message Display Area
        msg_container = tk.Frame(right_frame, bg='#2b2b2b')
        msg_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 10))
        
        # Message header
        msg_header = tk.Frame(msg_container, bg='#0d0d0d', height=35)
        msg_header.pack(fill=tk.X, pady=(0, 8))
        msg_header.pack_propagate(False)
        
        tk.Label(
            msg_header,
            text="💬  MESSAGE INFO",
            font=('Segoe UI', 11, 'bold'),
            bg='#0d0d0d',
            fg='#00ff88'
        ).pack(side=tk.LEFT, padx=10, pady=8)
        
        # SECRET BUTTON - Hidden in place (use Ctrl+R to reveal)
        self.secret_reveal_btn = tk.Button(
            msg_header,
            text="",  # No text
            command=self.authenticate_and_reveal,
            bg='#0d0d0d',  # Same as background
            fg='#0d0d0d',  # Same as background
            activebackground='#0d0d0d',
            relief=tk.FLAT,
            borderwidth=0,
            cursor='arrow',  # Normal cursor - no indication
            width=0,  # Zero width - invisible
            height=0,  # Zero height - invisible
            state=tk.DISABLED
        )
        self.secret_reveal_btn.pack(side=tk.RIGHT, padx=0)  # Pack but takes no space
        
        # Message info frame with enhanced border
        message_info_frame = tk.Frame(msg_container, bg='#0a0a0a', relief=tk.RIDGE, borderwidth=2)
        message_info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inner frame for padding
        inner_frame = tk.Frame(message_info_frame, bg='#0a0a0a')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Scrollable text widget for message
        scroll_y = tk.Scrollbar(inner_frame, bg='#1a1a1a', troughcolor='#0a0a0a')
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.message_text = tk.Text(
            inner_frame,
            font=('Consolas', 9),
            bg='#0a0a0a',
            fg='#d0d0d0',
            wrap=tk.WORD,
            padx=12,
            pady=12,
            state=tk.DISABLED,
            yscrollcommand=scroll_y.set,
            relief=tk.FLAT,
            selectbackground='#00ff88',
            selectforeground='#000000'
        )
        self.message_text.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.message_text.yview)
        
        # Initial message
        self.update_message_display("Waiting for data...", "", "", "")
        
        # Status bar with enhanced styling
        status_container = tk.Frame(self.root, bg='#0d0d0d', height=35)
        status_container.pack(fill=tk.X, side=tk.BOTTOM)
        status_container.pack_propagate(False)
        
        # Status indicator
        self.status_indicator = tk.Label(
            status_container,
            text="●",
            font=('Arial', 14),
            bg='#0d0d0d',
            fg='#00ff88'
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(10, 5))
        
        self.status_label = tk.Label(
            status_container,
            text="Ready | Load image and metadata to decrypt",
            font=('Segoe UI', 10),
            bg='#0d0d0d',
            fg='#888888',
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
        
        # PSNR Indicator
        self.psnr_label = tk.Label(
            status_container,
            text="",
            font=('Consolas', 9, 'bold'),
            bg='#0d0d0d',
            fg='#888888'
        )
        self.psnr_label.pack(side=tk.RIGHT, padx=10)
        
        # Self-Destruct Timer
        self.timer_label = tk.Label(
            status_container,
            text="",
            font=('Consolas', 9, 'bold'),
            bg='#0d0d0d',
            fg='#ff8800'
        )
        self.timer_label.pack(side=tk.RIGHT, padx=10)
        
        # Version label
        tk.Label(
            status_container,
            text="v2.5",
            font=('Consolas', 8),
            bg='#0d0d0d',
            fg='#444444'
        ).pack(side=tk.RIGHT, padx=10)
    
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
            print(f"\n[DEBUG] ===== LOADING NEW IMAGE: {os.path.basename(filepath)} =====")
            print(f"[DEBUG] Previous image path: {self.stego_image_path}")
            print(f"[DEBUG] Previous metadata: {self.metadata is not None}")
            print(f"[DEBUG] Button state before reset: {self.secret_reveal_btn.cget('state')}")
            
            # Cancel any running self-destruct timer
            if self.timer_active:
                self.timer_active = False
                self.timer_target_path = None
                if self.timer_label:
                    self.timer_label.config(text="")
                print("[⏱️] Previous timer cancelled")
            
            # Delete current 1-time view image BEFORE loading new one
            if self.delete_on_close and self.stego_image_path:
                try:
                    base_name = os.path.splitext(os.path.basename(self.stego_image_path))[0]
                    img_dir = os.path.dirname(self.stego_image_path)
                    
                    # Delete image file
                    if os.path.exists(self.stego_image_path):
                        os.remove(self.stego_image_path)
                        print(f"[DEBUG] Deleted 1-time view image: {self.stego_image_path}")
                    
                    # Delete metadata JSON
                    json_file = os.path.join(img_dir, f"{base_name}.json")
                    if os.path.exists(json_file):
                        os.remove(json_file)
                        print(f"[DEBUG] Deleted 1-time view metadata: {json_file}")
                except Exception as e:
                    print(f"Error deleting previous 1-time view files: {e}")
            
            # Reset everything for new image
            self.secret_reveal_btn.config(state=tk.DISABLED)
            self.decrypted_message = None
            self.metadata = None
            self.delete_on_close = False
            self.psnr_value = None
            self._already_authenticated = False  # Reset authentication for new image
            print(f"[DEBUG] State reset - metadata=None, button=DISABLED, auth reset")
            
            # Clear message display
            self.update_message_display("Waiting for metadata...", "", "", "")
            
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
    
    def decrypt_metadata(self, encrypted_package):
        """Decrypt metadata using AES"""
        try:
            # Handle both old and new formats
            if 'encrypted_package' in encrypted_package:
                # New format with nested structure
                pkg = encrypted_package['encrypted_package']
                encrypted_data = base64.b64decode(pkg['encrypted_data'])
                aes_key = base64.b64decode(pkg['aes_key'])
                aes_iv = base64.b64decode(pkg['aes_iv'])
            else:
                # Old format - direct encrypted package
                encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
                aes_key = base64.b64decode(encrypted_package['aes_key'])
                aes_iv = base64.b64decode(encrypted_package['aes_iv'])
            
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(aes_iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_json = decryptor.update(encrypted_data) + decryptor.finalize()
            
            return json.loads(decrypted_json.decode('utf-8'))
        except Exception as e:
            # If decryption fails, check if metadata is already decrypted in the package
            if 'metadata' in encrypted_package:
                return encrypted_package['metadata']
            raise e
    
    def load_metadata_file(self, filepath):
        """Load metadata from file"""
        try:
            print(f"[DEBUG] load_metadata_file called: {filepath}")
            # Reset button state for new metadata
            self.secret_reveal_btn.config(state=tk.DISABLED)
            self.decrypted_message = None
            self.delete_on_close = False
            print(f"[DEBUG] Button set to DISABLED in load_metadata_file")
            
            with open(filepath, 'r') as f:
                encrypted_package = json.load(f)
            
            # Decrypt metadata
            metadata = self.decrypt_metadata(encrypted_package)
            self.metadata = metadata
            print(f"[DEBUG] Metadata loaded successfully, self.metadata is now: {self.metadata is not None}")
            
            # Extract PSNR if available
            if 'psnr' in metadata:
                self.psnr_value = metadata['psnr']
                self.update_psnr_display()
            
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
            messagebox.showerror("Error", f"Failed to load metadata:\n{e}")
    
    def check_enable_reveal_button(self):
        """Enable secret reveal button when both image and metadata are loaded"""
        print(f"[DEBUG] check_enable_reveal_button called")
        print(f"[DEBUG]   - self.stego_image_path: {self.stego_image_path}")
        print(f"[DEBUG]   - self.metadata: {self.metadata is not None}")
        
        if self.stego_image_path and self.metadata:
            self.secret_reveal_btn.config(state=tk.NORMAL)
            print(f"[DEBUG]   - Button set to NORMAL")
            print(f"[DEBUG]   - Button state after set: {self.secret_reveal_btn.cget('state')}")
            self.status_label.config(text="✓ Ready | Press Ctrl+R to reveal message", fg='#00ff88')
            self.status_indicator.config(fg='#00ff88')
        else:
            print(f"[DEBUG]   - Conditions NOT met, button stays DISABLED")
    
    def update_psnr_display(self):
        """Update PSNR indicator in status bar"""
        if not self.psnr_value:
            return
        
        # Color-code based on quality
        if self.psnr_value > 50:
            color = '#00ff88'  # Green - Excellent
            quality = "Excellent"
        elif self.psnr_value > 40:
            color = '#ffaa00'  # Yellow - Good
            quality = "Good"
        else:
            color = '#ff5555'  # Red - Fair
            quality = "Fair"
        
        self.psnr_label.config(
            text=f"PSNR: {self.psnr_value:.1f}dB ({quality})",
            fg=color
        )
    
    def authenticate_and_reveal(self):
        """Authenticate user before revealing message"""
        if hasattr(self, '_already_authenticated') and self._already_authenticated:
            return
        
        import tkinter.simpledialog as simpledialog
        
        # Simple PIN-based authentication (more reliable than Windows auth)
        password = simpledialog.askstring(
            "LayerX Security",
            "Enter PIN to reveal hidden message\n(Default: 1234)",
            show='●'
        )
        
        if not password:
            self.status_label.config(text="❌ Authentication cancelled", fg='#ff5555')
            self.status_indicator.config(fg='#ff5555')
            return
        
        # Check if PIN file exists, otherwise use default
        pin_file = "layerx_pin.txt"
        default_pin = "1234"
        
        try:
            if os.path.exists(pin_file):
                with open(pin_file, 'r') as f:
                    stored_pin = f.read().strip()
            else:
                stored_pin = default_pin
            
            if password == stored_pin:
                self._already_authenticated = True
                self.status_label.config(text="✅ Authenticated", fg='#00ff88')
                self.status_indicator.config(fg='#00ff88')
                
                # Proceed with reveal
                self.reveal_message()
            else:
                self.status_label.config(text="❌ Invalid PIN", fg='#ff5555')
                self.status_indicator.config(fg='#ff5555')
                messagebox.showerror("Authentication Failed", "Invalid PIN. Default is 1234")
                
        except Exception as e:
            messagebox.showerror("Error", f"Authentication error:\n{e}")
    
    def update_message_display(self, status, sender_ip="", timestamp="", message="", username=""):
        """Update the message display area with enhanced formatting"""
        self.message_text.config(state=tk.NORMAL)
        self.message_text.delete('1.0', tk.END)
        
        # Format the display with better styling
        content = f"{'═'*47}\n"
        
        # Status indicator
        if status == "DECRYPTED ✓":
            content += f"  ✅ STATUS: {status}\n"
        elif "Ready" in status:
            content += f"  🔄 STATUS: {status}\n"
        else:
            content += f"  ⏳ STATUS: {status}\n"
        
        content += f"{'═'*47}\n\n"
        
        if username or sender_ip:
            content += f"╔══ SENDER INFORMATION\n"
            content += f"║\n"
            if username:
                content += f"║  👤 Username:\n"
                content += f"║     {username}\n"
                content += f"║\n"
            if sender_ip:
                content += f"║  📡 Address:\n"
                content += f"║     {sender_ip}\n"
                content += f"║\n"
        
        if timestamp:
            if not sender_ip:
                content += f"╔══ MESSAGE INFORMATION\n║\n"
            content += f"║  📅 Received:\n"
            content += f"║     {timestamp}\n"
            content += f"║\n"
            content += f"╚{'═'*45}\n\n"
        
        if message and status == "DECRYPTED ✓":
            content += f"╔══ DECRYPTED MESSAGE\n"
            content += f"║\n"
            content += f"║  {message.replace(chr(10), chr(10) + '║  ')}\n"
            content += f"║\n"
            content += f"╚{'═'*45}\n"
        elif message:
            content += f"\n{message}\n"
        
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
            self.secret_button.config(state=tk.DISABLED)
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
                self.metadata.get('sender_address', self.metadata.get('sender_ip', 'Unknown')),
                self.metadata.get('timestamp', self.metadata.get('received_timestamp', 'Unknown')),
                message,
                self.metadata.get('sender_username', 'Unknown')
            )
            
            self.status_label.config(text="✅ Message revealed successfully!", fg='#00ff88')
            self.status_indicator.config(fg='#00ff88')
            self.secret_button.config(state=tk.NORMAL)
            # Store decrypted message
            self.decrypted_message = message
            
            # Start self-destruct countdown if applicable
            self.check_self_destruct()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract message:\n{e}")
            self.status_label.config(text="❌ Failed to extract message", fg='#ff0000')
            self.status_indicator.config(fg='#ff0000')
            self.secret_button.config(state=tk.NORMAL)
    
    def handle_ctrl_r(self):
        """Handle Ctrl+R keyboard shortcut with debugging"""
        print(f"\n[DEBUG] ===== Ctrl+R PRESSED =====")
        print(f"[DEBUG] Button state: {self.secret_reveal_btn.cget('state')}")
        print(f"[DEBUG] Image path: {self.stego_image_path}")
        print(f"[DEBUG] Metadata: {self.metadata is not None}")
        
        if self.secret_reveal_btn.cget('state') == tk.NORMAL:
            print(f"[DEBUG] Button is NORMAL - calling authenticate_and_reveal()")
            self.authenticate_and_reveal()
        else:
            print(f"[DEBUG] Button is DISABLED - Ctrl+R blocked!")
            print(f"[DEBUG] Image loaded: {bool(self.stego_image_path)}")
            print(f"[DEBUG] Metadata loaded: {bool(self.metadata)}")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick actions"""
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-m>', lambda e: self.load_metadata())
        self.root.bind('<Control-r>', lambda e: self.handle_ctrl_r())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-i>', lambda e: self.show_image_metadata())
        self.root.bind('<F5>', lambda e: self.refresh_thumbnails())
        print("[+] Keyboard shortcuts enabled: Ctrl+O, Ctrl+M, Ctrl+R, Ctrl+T, Ctrl+Q, Ctrl+I, F5")
    
    def load_recent_files(self):
        """Load list of recent stego images"""
        try:
            # Find all PNG files matching pattern
            png_files = glob.glob("*.png") + glob.glob("*/*.png")
            json_files = glob.glob("*.json") + glob.glob("*/*.json")
            
            # Match PNG files with their JSON counterparts
            self.recent_files = []
            for png in sorted(png_files, key=os.path.getmtime, reverse=True)[:15]:
                base_name = os.path.splitext(os.path.basename(png))[0]
                json_file = f"{base_name}.json"
                
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r') as f:
                            pkg = json.load(f)
                            metadata = pkg.get('metadata', {})
                            self.recent_files.append({
                                'png': png,
                                'json': json_file,
                                'sender': metadata.get('sender_username', 'Unknown'),
                                'timestamp': metadata.get('timestamp', metadata.get('received_timestamp', 'Unknown')),
                                'mtime': os.path.getmtime(png)
                            })
                    except:
                        pass
        except Exception as e:
            print(f"[!] Error loading recent files: {e}")
    
    def show_image_metadata(self):
        """Show detailed image metadata in terminal"""
        if not self.stego_image_path:
            print("\n[!] No image loaded")
            return
        
        try:
            img = Image.open(self.stego_image_path)
            file_size = os.path.getsize(self.stego_image_path) / 1024  # KB
            
            print("\n" + "="*60)
            print("   IMAGE METADATA INSPECTOR")
            print("="*60)
            print(f"\n📁 FILE: {os.path.basename(self.stego_image_path)}")
            print(f"📏 Size: {file_size:.2f} KB")
            print(f"🖼️  Dimensions: {img.size[0]} x {img.size[1]} pixels")
            print(f"🎨 Mode: {img.mode}")
            print(f"📊 Format: {img.format}")
            
            # EXIF data
            if hasattr(img, '_getexif') and img._getexif():
                exif_data = img._getexif()
                print(f"\n📝 EXIF DATA:")
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    print(f"   {tag}: {value}")
            else:
                print(f"\n📝 EXIF DATA: None")
            
            # Embedding statistics
            if self.metadata:
                print(f"\n🔐 EMBEDDING STATISTICS:")
                payload_bits = self.metadata.get('payload_bits_length', 0)
                payload_bytes = payload_bits // 8
                print(f"   Payload Size: {payload_bytes} bytes ({payload_bits} bits)")
                
                # Calculate capacity
                total_pixels = img.size[0] * img.size[1]
                channels = len(img.mode)
                # DWT embedding in 7 bands, ~20% of coefficients usable
                capacity_bits = int(total_pixels * channels * 0.20)
                capacity_bytes = capacity_bits // 8
                used_percent = (payload_bits / capacity_bits) * 100
                
                print(f"   Total Capacity: ~{capacity_bytes} bytes")
                print(f"   Used: {used_percent:.1f}%")
                print(f"   Remaining: ~{capacity_bytes - payload_bytes} bytes")
                
                if self.psnr_value:
                    print(f"\n📊 QUALITY METRICS:")
                    print(f"   PSNR: {self.psnr_value:.2f} dB", end="")
                    if self.psnr_value > 50:
                        print(" (Excellent)")
                    elif self.psnr_value > 40:
                        print(" (Good)")
                    else:
                        print(" (Fair)")
            
            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"\n[!] Error inspecting metadata: {e}\n")
    
    def check_self_destruct(self):
        """Check and initiate self-destruct countdown if applicable"""
        if not self.metadata or not self.metadata.get('self_destruct'):
            return
        
        sd = self.metadata['self_destruct']
        sd_type = sd.get('type')
        
        if sd_type == 'timer':
            # Timer-based destruction - delete when window closes OR timer expires
            seconds = sd.get('seconds', sd.get('minutes', 5) * 60)  # Support both formats
            self.start_destruction_timer(seconds)
            # Mark for deletion on close
            self.delete_on_close = True
        elif sd_type == 'view_count':
            # View count based - delete after reading and closing
            max_views = sd.get('max_views', 1)
            current_views = sd.get('current_views', 0) + 1
            
            if current_views >= max_views:
                # Mark for deletion when window closes
                self.delete_on_close = True
                self.status_label.config(
                    text=f"⚠️ Final view - will delete on close",
                    fg='#ff5555'
                )
            else:
                # Update view count in metadata
                self.metadata['self_destruct']['current_views'] = current_views
                self.status_label.config(
                    text=f"⚠️ Warning: {max_views - current_views} views remaining",
                    fg='#ff8800'
                )
    
    def start_destruction_timer(self, seconds):
        """Start countdown timer for self-destruct"""
        # Store the current image path - this is what we'll delete
        self.timer_target_path = self.stego_image_path
        self.timer_active = True
        end_time = datetime.now() + timedelta(seconds=seconds)
        
        def countdown():
            while datetime.now() < end_time and self.timer_active:
                remaining = end_time - datetime.now()
                total_secs = remaining.seconds
                mins, secs = divmod(total_secs, 60)
                
                if self.timer_label:
                    if mins > 0:
                        self.timer_label.config(
                            text=f"⏱️ Self-Destruct: {mins}m {secs}s"
                        )
                    else:
                        self.timer_label.config(
                            text=f"⏱️ Self-Destruct: {secs}s"
                        )
                else:
                    # Create timer label if doesn't exist
                    break
                
                time.sleep(1)
            
            # Time's up - destroy message if timer wasn't cancelled
            if self.timer_active and self.timer_target_path:
                self.destroy_message_by_path(self.timer_target_path, f"Timer expired ({seconds}s)")
                self.timer_active = False
                self.timer_target_path = None
        
        # Run countdown in separate thread
        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()
        
        print(f"[⏱️] Self-destruct timer started: {seconds} seconds for {os.path.basename(self.timer_target_path)}")
    
    def destroy_message_by_path(self, image_path, reason):
        """Destroy message and associated files for a specific path"""
        try:
            # Show warning notification (non-blocking)
            messagebox.showwarning("Self-Destruct", f"Message will self-destruct!\n\nReason: {reason}")
            
            # Delete files immediately without confirmation
            if image_path and os.path.exists(image_path):
                # Get the directory and base filename
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                img_dir = os.path.dirname(image_path)
                
                # Delete image file
                os.remove(image_path)
                print(f"[🔥] Deleted stego image: {image_path}")
                
                # Delete metadata JSON
                json_file = os.path.join(img_dir, f"{base_name}.json")
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print(f"[🔥] Deleted metadata: {json_file}")
                
                # Clear display if this was the current image
                if image_path == self.stego_image_path:
                    self.image_label.configure(image='', text='Image deleted (self-destruct)')
                    self.update_message_display("Message destroyed", "", "", "")
                    self.stego_image_path = None
                    self.metadata = None
                
                print(f"[✓] Self-destruct complete: {reason}")
        except Exception as e:
            print(f"[!] Error during self-destruct: {e}")
    
    def destroy_message(self, reason):
        """Destroy current message and associated files"""
        try:
            # Show warning notification (non-blocking)
            messagebox.showwarning("Self-Destruct", f"Message will self-destruct!\n\nReason: {reason}")
            
            # Delete files immediately without confirmation
            if self.stego_image_path and os.path.exists(self.stego_image_path):
                # Get the directory and base filename
                img_dir = os.path.dirname(self.stego_image_path)
                base_name = os.path.splitext(os.path.basename(self.stego_image_path))[0]
                
                # Delete image
                os.remove(self.stego_image_path)
                print(f"[🗑️] Deleted: {self.stego_image_path}")
                
                # Delete metadata JSON
                json_file = os.path.join(img_dir, f"{base_name}.json")
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print(f"[🗑️] Deleted: {json_file}")
            
            # Clear UI
            self.image_label.config(image='', text="🔥 Message Self-Destructed")
            self.metadata = None
            self.stego_image_path = None
            self.decrypted_message = None
            self.update_message_display("DESTROYED", "", "", f"Message deleted: {reason}")
            
            messagebox.showinfo("Self-Destruct Complete", "Message and files deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to self-destruct: {e}")
    
    def refresh_thumbnails(self):
        """Refresh the thumbnails view"""
        print("[🔄] Refreshing thumbnails...")
        self.load_recent_files()
        messagebox.showinfo("Refresh", f"Found {len(self.recent_files)} recent messages")
    
    def on_closing(self):
        """Handle window close event - delete files if marked for self-destruct"""
        if self.delete_on_close:
            try:
                # Delete files without confirmation when window closes
                if self.stego_image_path and os.path.exists(self.stego_image_path):
                    # Get directory and base filename
                    img_dir = os.path.dirname(self.stego_image_path)
                    base_name = os.path.splitext(os.path.basename(self.stego_image_path))[0]
                    
                    # Delete image
                    os.remove(self.stego_image_path)
                    print(f"[🗑️] Self-destruct on close: Deleted {self.stego_image_path}")
                    
                    # Delete metadata JSON
                    json_file = os.path.join(img_dir, f"{base_name}.json")
                    if os.path.exists(json_file):
                        os.remove(json_file)
                        print(f"[🗑️] Self-destruct on close: Deleted {json_file}")
                
                print("[✓] Self-destruct complete - files deleted on window close")
            except Exception as e:
                print(f"[!] Error during self-destruct: {e}")
        
        # Close the window
        self.root.destroy()


def main():
    root = tk.Tk()
    app = StegoViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
