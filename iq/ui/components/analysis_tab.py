"""
Analysis Tab - Trade analysis and statistics
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime
from typing import Optional

from ui.widgets.stats_cards import StatsCards


class AnalysisTab:
    """Trade analysis and statistics tab"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_trades = []
        self.analysis_result = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the analysis tab UI"""
        # Configure parent grid
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        
        # Create control panel
        self.create_control_panel()
        
        # Create results area
        self.create_results_area()
    
    def create_control_panel(self):
        """Create analysis control panel"""
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(2, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            control_frame,
            text="📊 Trade Analysis",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Date range selection
        date_frame = ctk.CTkFrame(control_frame)
        date_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        date_frame.grid_columnconfigure(1, weight=1)
        date_frame.grid_columnconfigure(3, weight=1)
        
        # Start date
        ctk.CTkLabel(date_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ctk.CTkEntry(date_frame, textvariable=self.start_date_var)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # End date
        ctk.CTkLabel(date_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ctk.CTkEntry(date_frame, textvariable=self.end_date_var)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Analysis buttons
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        self.analyze_button = ctk.CTkButton(
            button_frame,
            text="🔍 Run Analysis",
            command=self.run_analysis,
            width=150
        )
        self.analyze_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.export_button = ctk.CTkButton(
            button_frame,
            text="📤 Export Results",
            command=self.export_results,
            width=150
        )
        self.export_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=100
        )
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Status
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Ready to analyze",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=3, column=0, columnspan=4, pady=5)
    
    def create_results_area(self):
        """Create results display area"""
        # Create notebook for different result views
        self.results_notebook = ttk.Notebook(self.parent)
        self.results_notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Overview tab
        self.overview_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.overview_frame, text="Overview")
        self.create_overview_tab()
        
        # Statistics tab
        self.stats_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.stats_frame, text="Statistics")
        self.create_statistics_tab()
        
        # Charts tab
        self.charts_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.charts_frame, text="Charts")
        self.create_charts_tab()
        
        # Detailed analysis tab
        self.detailed_frame = ctk.CTkFrame(self.results_notebook)
        self.results_notebook.add(self.detailed_frame, text="Detailed")
        self.create_detailed_tab()
    
    def create_overview_tab(self):
        """Create overview tab with summary cards"""
        # Configure grid
        self.overview_frame.grid_columnconfigure(0, weight=1)
        self.overview_frame.grid_rowconfigure(1, weight=1)
        
        # Create stats cards
        self.stats_cards = StatsCards(self.overview_frame)
        
        # Create summary text
        self.summary_text = ctk.CTkTextbox(self.overview_frame, height=200)
        self.summary_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    
    def create_statistics_tab(self):
        """Create detailed statistics tab"""
        # Configure grid
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame
        self.stats_scroll = ctk.CTkScrollableFrame(self.stats_frame)
        self.stats_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Statistics labels will be added dynamically
        self.stats_labels = {}
    
    def create_charts_tab(self):
        """Create charts and visualizations tab"""
        # Configure grid
        self.charts_frame.grid_columnconfigure(0, weight=1)
        self.charts_frame.grid_rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.charts_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def create_detailed_tab(self):
        """Create detailed analysis tab"""
        # Configure grid
        self.detailed_frame.grid_columnconfigure(0, weight=1)
        self.detailed_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview for detailed data
        self.tree_frame = ctk.CTkFrame(self.detailed_frame)
        self.tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview
        columns = ('Date', 'Asset', 'Type', 'Amount', 'Result', 'Profit')
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
    
    def run_analysis(self):
        """Run trade analysis"""
        if not self.app.current_trades:
            messagebox.showwarning("Warning", "No trade data available")
            return
        
        # Parse date range
        start_date = None
        end_date = None
        
        try:
            if self.start_date_var.get():
                start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            
            if self.end_date_var.get():
                end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        # Run analysis
        self.status_label.configure(text="Running analysis...")
        self.analyze_button.configure(state="disabled")
        
        self.app.run_analysis(start_date, end_date)
    
    def on_trades_loaded(self, trades: list):
        """Handle trades loaded event"""
        self.current_trades = trades
        
        # Update date range
        if trades:
            first_trade = min(trades, key=lambda t: t.timestamp)
            last_trade = max(trades, key=lambda t: t.timestamp)
            
            self.start_date_var.set(first_trade.timestamp.strftime("%Y-%m-%d"))
            self.end_date_var.set(last_trade.timestamp.strftime("%Y-%m-%d"))
        
        self.status_label.configure(text=f"Loaded {len(trades)} trades")
        self.analyze_button.configure(state="normal")
    
    def on_analysis_complete(self, result):
        """Handle analysis complete event"""
        self.analysis_result = result
        self.status_label.configure(text="Analysis complete")
        self.analyze_button.configure(state="normal")
        
        # Update all tabs
        self.update_overview_tab()
        self.update_statistics_tab()
        self.update_charts_tab()
        self.update_detailed_tab()
    
    def update_overview_tab(self):
        """Update overview tab with analysis results"""
        if not self.analysis_result:
            return
        
        # Update stats cards
        stats_data = {
            'Total Trades': self.analysis_result.total_trades,
            'Win Rate': f"{self.analysis_result.win_rate:.2%}",
            'Net Profit': f"${self.analysis_result.net_profit:.2f}",
            'Profit Factor': f"{self.analysis_result.profit_factor:.2f}",
            'Max Drawdown': f"{self.analysis_result.max_drawdown:.2f}%",
            'Best Hour': f"{self.analysis_result.best_hour}:00"
        }
        
        self.stats_cards.update_stats(stats_data)
        
        # Update summary text
        summary = f"""
ANALYSIS SUMMARY
================

Period: {self.analysis_result.date_range[0].strftime('%Y-%m-%d')} to {self.analysis_result.date_range[1].strftime('%Y-%m-%d')}

Performance Metrics:
• Total Trades: {self.analysis_result.total_trades}
• Winning Trades: {self.analysis_result.winning_trades}
• Losing Trades: {self.analysis_result.losing_trades}
• Win Rate: {self.analysis_result.win_rate:.2%}
• Net Profit: ${self.analysis_result.net_profit:.2f}
• Total Profit: ${self.analysis_result.total_profit:.2f}
• Total Loss: ${self.analysis_result.total_loss:.2f}
• Average Profit: ${self.analysis_result.average_profit:.2f}
• Average Loss: ${self.analysis_result.average_loss:.2f}
• Profit Factor: {self.analysis_result.profit_factor:.2f}

Risk Analysis:
• Max Drawdown: {self.analysis_result.max_drawdown:.2f}%
• Max Consecutive Wins: {self.analysis_result.max_consecutive_wins}
• Max Consecutive Losses: {self.analysis_result.max_consecutive_losses}

Best Performing:
• Best Hour: {self.analysis_result.best_hour}:00
• Worst Hour: {self.analysis_result.worst_hour}:00
• Best Asset: {self.analysis_result.best_asset}
• Worst Asset: {self.analysis_result.worst_asset}

Extreme Trades:
• Best Trade: {self.analysis_result.best_trade.asset} - ${self.analysis_result.best_trade.profit:.2f}
• Worst Trade: {self.analysis_result.worst_trade.asset} - ${self.analysis_result.worst_trade.profit:.2f}
        """
        
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary)
    
    def update_statistics_tab(self):
        """Update statistics tab with detailed analysis"""
        if not self.analysis_result:
            return
        
        # Clear existing labels
        for widget in self.stats_scroll.winfo_children():
            widget.destroy()
        
        # Hourly statistics
        hourly_frame = ctk.CTkFrame(self.stats_scroll)
        hourly_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            hourly_frame,
            text="📅 Hourly Performance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=5)
        
        for hour, stats in self.analysis_result.trades_by_hour.items():
            hour_label = ctk.CTkLabel(
                hourly_frame,
                text=f"Hour {hour:02d}:00 - Trades: {stats['trade_count']}, Win Rate: {stats['win_rate']:.2%}, Profit: ${stats['total_profit']:.2f}",
                font=ctk.CTkFont(size=12)
            )
            hour_label.grid(row=hour + 1, column=0, sticky="w", padx=20, pady=2)
        
        # Asset statistics
        asset_frame = ctk.CTkFrame(self.stats_scroll)
        asset_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            asset_frame,
            text="💱 Asset Performance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=5)
        
        asset_row = 1
        for asset, stats in self.analysis_result.trades_by_asset.items():
            asset_label = ctk.CTkLabel(
                asset_frame,
                text=f"{asset}: Trades: {stats['trade_count']}, Win Rate: {stats['win_rate']:.2%}, Profit: ${stats['total_profit']:.2f}",
                font=ctk.CTkFont(size=12)
            )
            asset_label.grid(row=asset_row, column=0, sticky="w", padx=20, pady=2)
            asset_row += 1
    
    def update_charts_tab(self):
        """Update charts with visualization"""
        if not self.analysis_result:
            return
        
        # Clear existing plots
        for ax in self.axes.flat:
            ax.clear()
        
        # Plot 1: Equity Curve
        equity_curve = self.analysis_result.equity_curve
        self.axes[0, 0].plot(equity_curve, linewidth=2)
        self.axes[0, 0].set_title('Equity Curve')
        self.axes[0, 0].set_xlabel('Trade Number')
        self.axes[0, 0].set_ylabel('Cumulative Profit ($)')
        self.axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Hourly Performance
        hours = list(self.analysis_result.trades_by_hour.keys())
        profits = [self.analysis_result.trades_by_hour[hour]['total_profit'] for hour in hours]
        
        self.axes[0, 1].bar(hours, profits, color='steelblue', alpha=0.7)
        self.axes[0, 1].set_title('Hourly Profit Distribution')
        self.axes[0, 1].set_xlabel('Hour of Day')
        self.axes[0, 1].set_ylabel('Profit ($)')
        self.axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Asset Performance
        assets = list(self.analysis_result.trades_by_asset.keys())
        asset_profits = [self.analysis_result.trades_by_asset[asset]['total_profit'] for asset in assets]
        
        self.axes[1, 0].barh(assets, asset_profits, color='green', alpha=0.7)
        self.axes[1, 0].set_title('Asset Performance')
        self.axes[1, 0].set_xlabel('Profit ($)')
        self.axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Win Rate by Hour
        win_rates = [self.analysis_result.trades_by_hour[hour]['win_rate'] for hour in hours]
        
        self.axes[1, 1].plot(hours, win_rates, marker='o', linewidth=2, color='orange')
        self.axes[1, 1].set_title('Win Rate by Hour')
        self.axes[1, 1].set_xlabel('Hour of Day')
        self.axes[1, 1].set_ylabel('Win Rate')
        self.axes[1, 1].set_ylim(0, 1)
        self.axes[1, 1].grid(True, alpha=0.3)
        
        # Adjust layout and refresh
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_detailed_tab(self):
        """Update detailed tab with trade data"""
        if not self.app.current_trades:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add trade data
        for trade in self.app.current_trades:
            values = (
                trade.timestamp.strftime('%Y-%m-%d %H:%M'),
                trade.asset,
                trade.trade_type.value,
                f"${trade.amount:.2f}",
                trade.result.value,
                f"${trade.profit:.2f}"
            )
            
            # Color code based on result
            tag = 'win' if trade.result.value == 'WIN' else 'loss' if trade.result.value == 'LOSS' else 'draw'
            self.tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure tags
        self.tree.tag_configure('win', background='lightgreen')
        self.tree.tag_configure('loss', background='lightcoral')
        self.tree.tag_configure('draw', background='lightyellow')
    
    def export_results(self):
        """Export analysis results"""
        self.app.export_results()
    
    def refresh_data(self):
        """Refresh displayed data"""
        if self.app.current_trades:
            self.on_trades_loaded(self.app.current_trades)
        
        if self.analysis_result:
            self.on_analysis_complete(self.analysis_result)
