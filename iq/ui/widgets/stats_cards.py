"""
Stats Cards - Display key statistics in card format
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any


class StatsCards:
    """Display statistics in card format"""
    
    def __init__(self, parent):
        self.parent = parent
        self.cards = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the stats cards UI"""
        # Configure parent grid
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        
        # Create default cards
        default_stats = [
            ("Total Trades", "0", "📊"),
            ("Win Rate", "0%", "🎯"),
            ("Net Profit", "$0.00", "💰"),
            ("Profit Factor", "0.00", "📈"),
            ("Max Drawdown", "0.00%", "📉"),
            ("Best Hour", "00:00", "⏰")
        ]
        
        for i, (title, value, icon) in enumerate(default_stats):
            row, col = i // 3, i % 3
            self.create_card(title, value, icon, row, col)
    
    def create_card(self, title: str, value: str, icon: str, row: int, col: int):
        """Create a single stats card"""
        card_frame = ctk.CTkFrame(self.parent)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        card_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card_frame,
            text=icon,
            font=ctk.CTkFont(size=24)
        )
        icon_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Value
        value_label = ctk.CTkLabel(
            card_frame,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        value_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Store reference
        self.cards[title] = value_label
    
    def update_stats(self, stats_data: Dict[str, Any]):
        """Update statistics values"""
        for title, value in stats_data.items():
            if title in self.cards:
                self.cards[title].configure(text=str(value))
            else:
                # Create new card if it doesn't exist
                # Find an empty position
                for row in range(2):
                    for col in range(3):
                        card_key = f"row_{row}_col_{col}"
                        if card_key not in self.cards:
                            # Find appropriate icon
                            icon = self.get_icon_for_stat(title)
                            self.create_card(title, str(value), icon, row, col)
                            self.cards[card_key] = self.cards[title]
                            break
    
    def get_icon_for_stat(self, stat_name: str) -> str:
        """Get appropriate icon for statistic"""
        stat_lower = stat_name.lower()
        
        if "trade" in stat_lower:
            return "📊"
        elif "win" in stat_lower or "rate" in stat_lower:
            return "🎯"
        elif "profit" in stat_lower or "money" in stat_lower:
            return "💰"
        elif "drawdown" in stat_lower or "loss" in stat_lower:
            return "📉"
        elif "hour" in stat_lower or "time" in stat_lower:
            return "⏰"
        elif "factor" in stat_lower or "ratio" in stat_lower:
            return "📈"
        else:
            return "📋"
    
    def clear_all(self):
        """Clear all statistics"""
        for label in self.cards.values():
            label.configure(text="0")
    
    def highlight_card(self, title: str, highlight: bool = True):
        """Highlight a specific card"""
        if title in self.cards:
            card = self.cards[title].master
            if highlight:
                card.configure(border_width=2, border_color="blue")
            else:
                card.configure(border_width=0, border_color="transparent")
