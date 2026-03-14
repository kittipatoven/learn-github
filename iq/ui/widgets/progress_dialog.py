"""
Progress Dialog - Show progress for long-running operations
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional


class ProgressDialog:
    """Progress dialog for long-running operations"""
    
    def __init__(self, parent, title: str, message: str):
        self.parent = parent
        self.title = title
        self.message = message
        self.canceled = False
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self.center_dialog()
        
        # Create UI
        self.setup_ui()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the progress dialog UI"""
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)
        
        # Message label
        self.message_label = ctk.CTkLabel(
            self.dialog,
            text=self.message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        self.message_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.dialog, width=300)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=10)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.dialog,
            text="Starting...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=2, column=0, padx=20, pady=5)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.dialog,
            text="Cancel",
            command=self.cancel,
            width=100
        )
        self.cancel_button.grid(row=3, column=0, padx=20, pady=20)
    
    def update_progress(self, value: float, status: str = None):
        """Update progress bar and status"""
        self.progress_bar.set(value)
        
        if status:
            self.status_label.configure(text=status)
        
        # Update UI
        self.dialog.update_idletasks()
    
    def update_message(self, message: str):
        """Update message label"""
        self.message_label.configure(text=message)
        self.dialog.update_idletasks()
    
    def cancel(self):
        """Cancel the operation"""
        self.canceled = True
        self.close()
    
    def is_canceled(self) -> bool:
        """Check if operation was canceled"""
        return self.canceled
    
    def close(self):
        """Close the dialog"""
        self.dialog.destroy()
    
    def show_indeterminate(self):
        """Show indeterminate progress"""
        # For CustomTkinter, we'll simulate indeterminate progress
        self.animate_progress()
    
    def animate_progress(self):
        """Animate progress bar for indeterminate operations"""
        if not self.canceled and self.dialog.winfo_exists():
            current = self.progress_bar.get()
            new_value = (current + 0.1) % 1.0
            self.progress_bar.set(new_value)
            
            # Schedule next animation only if dialog still exists
            if self.dialog.winfo_exists():
                self.dialog.after(100, self.animate_progress)
