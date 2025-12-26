def on_closing(self):
    """Handle window close event - delete files if marked for self-destruct"""
    if self.delete_on_close:
        try:
            # Delete files without confirmation
            if self.stego_image_path and os.path.exists(self.stego_image_path):
                os.remove(self.stego_image_path)
                print(f"[🗑️] Self-destruct: Deleted {self.stego_image_path}")
            
            # Delete metadata
            if self.metadata and self.stego_image_path:
                base_name = os.path.splitext(os.path.basename(self.stego_image_path))[0]
                json_file = f"{base_name}.json"
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print(f"[🗑️] Self-destruct: Deleted {json_file}")
            
            print("[✓] Self-destruct complete - files deleted on close")
        except Exception as e:
            print(f"[!] Error during self-destruct: {e}")
    
    # Close the window
    self.root.destroy()
