"""
Dashboard Tab - Interactive trading dashboard
"""

import sys
import os
import logging
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
from datetime import datetime, timedelta
from typing import Optional

from ui.widgets.stats_cards import StatsCards


class DashboardTab:
    """Interactive trading dashboard tab"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.analysis_result = None
        self.ai_results = None
        self.auto_refresh_var = tk.BooleanVar(value=False)
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
    
    def safe_after(self, delay, callback, *args):
        """Safe after() wrapper that checks widget existence"""
        def safe_callback():
            try:
                if self.parent and self.parent.winfo_exists():
                    callback(*args)
            except Exception as e:
                self.logger.error(f"Error in safe callback: {e}")
        
        return self.parent.after(delay, safe_callback)
    
    def setup_ui(self):
        """Setup the dashboard tab UI"""
        # Configure parent grid
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        
        # Create control panel
        self.create_control_panel()
        
        # Create dashboard area
        self.create_dashboard_area()
    
    def create_control_panel(self):
        """Create dashboard control panel"""
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(2, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            control_frame,
            text="📈 Trading Dashboard",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Refresh controls
        refresh_frame = ctk.CTkFrame(control_frame)
        refresh_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=False)
        auto_refresh_checkbox = ctk.CTkCheckBox(
            refresh_frame,
            text="Auto Refresh (30s)",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh
        )
        auto_refresh_checkbox.grid(row=0, column=0, padx=5, pady=5)
        
        self.refresh_button = ctk.CTkButton(
            refresh_frame,
            text="🔄 Refresh Dashboard",
            command=self.refresh_dashboard,
            width=150
        )
        self.refresh_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.export_dashboard_button = ctk.CTkButton(
            refresh_frame,
            text="📊 Export Dashboard",
            command=self.export_dashboard,
            width=150
        )
        self.export_dashboard_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Status
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Dashboard ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=2, column=0, columnspan=4, pady=5)
    
    def create_dashboard_area(self):
        """Create main dashboard display area"""
        # Create scrollable frame for dashboard
        self.dashboard_scroll = ctk.CTkScrollableFrame(self.parent)
        self.dashboard_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create dashboard sections
        self.create_overview_section()
        self.create_performance_section()
        self.create_charts_section()
        self.create_ai_section()
        self.create_risk_section()
    
    def create_overview_section(self):
        """Create overview section with key metrics"""
        overview_frame = ctk.CTkFrame(self.dashboard_scroll)
        overview_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        overview_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            overview_frame,
            text="📊 Performance Overview",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # Create stats cards
        self.dashboard_stats = StatsCards(overview_frame)
    
    def create_performance_section(self):
        """Create performance metrics section"""
        performance_frame = ctk.CTkFrame(self.dashboard_scroll)
        performance_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        performance_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            performance_frame,
            text="📈 Detailed Performance",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # Performance metrics grid
        metrics_frame = ctk.CTkFrame(performance_frame)
        metrics_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Create metric labels
        self.performance_labels = {}
        metrics = [
            ("Total Trades", "0"),
            ("Win Rate", "0%"),
            ("Net Profit", "$0.00"),
            ("Profit Factor", "0.00"),
            ("Max Drawdown", "0.00%"),
            ("Sharpe Ratio", "0.00"),
            ("Best Trade", "$0.00"),
            ("Worst Trade", "$0.00"),
            ("Avg Win", "$0.00"),
            ("Avg Loss", "$0.00"),
            ("Max Consecutive Wins", "0"),
            ("Max Consecutive Losses", "0")
        ]
        
        for i, (metric, value) in enumerate(metrics):
            row, col = i // 3, i % 3
            
            metric_label = ctk.CTkLabel(
                metrics_frame,
                text=metric + ":",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            metric_label.grid(row=row*2, column=col, padx=10, pady=2, sticky="e")
            
            value_label = ctk.CTkLabel(
                metrics_frame,
                text=value,
                font=ctk.CTkFont(size=12)
            )
            value_label.grid(row=row*2+1, column=col, padx=10, pady=2, sticky="w")
            
            self.performance_labels[metric] = value_label
    
    def create_charts_section(self):
        """Create charts and visualizations section"""
        charts_frame = ctk.CTkFrame(self.dashboard_scroll)
        charts_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        charts_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            charts_frame,
            text="📊 Visual Analytics",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # Create matplotlib figure
        self.dashboard_fig, self.dashboard_axes = plt.subplots(2, 3, figsize=(15, 8))
        self.dashboard_fig.tight_layout(pad=3.0)
        
        # Embed in tkinter
        self.dashboard_canvas = FigureCanvasTkAgg(
            self.dashboard_fig, 
            master=charts_frame
        )
        self.dashboard_canvas.get_tk_widget().grid(
            row=1, column=0, sticky="nsew", padx=10, pady=10
        )
    
    def create_ai_section(self):
        """Create AI analysis section"""
        ai_frame = ctk.CTkFrame(self.dashboard_scroll)
        ai_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        ai_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            ai_frame,
            text="🤖 AI Insights",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # AI insights text
        self.ai_insights_text = ctk.CTkTextbox(ai_frame, height=150)
        self.ai_insights_text.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
    
    def create_risk_section(self):
        """Create risk analysis section"""
        risk_frame = ctk.CTkFrame(self.dashboard_scroll)
        risk_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        risk_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            risk_frame,
            text="⚠️ Risk Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # Risk metrics
        risk_metrics_frame = ctk.CTkFrame(risk_frame)
        risk_metrics_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Risk indicators
        self.risk_labels = {}
        risk_metrics = [
            ("Current Drawdown", "0.00%"),
            ("Risk of Ruin", "0.00%"),
            ("Value at Risk (95%)", "$0.00"),
            ("Conditional VaR (95%)", "$0.00"),
            ("Portfolio Volatility", "0.00%"),
            ("Risk-Adjusted Return", "0.00")
        ]
        
        for i, (metric, value) in enumerate(risk_metrics):
            row, col = i // 2, i % 2
            
            metric_label = ctk.CTkLabel(
                risk_metrics_frame,
                text=metric + ":",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            metric_label.grid(row=row*2, column=col, padx=10, pady=2, sticky="e")
            
            value_label = ctk.CTkLabel(
                risk_metrics_frame,
                text=value,
                font=ctk.CTkFont(size=12)
            )
            value_label.grid(row=row*2+1, column=col, padx=10, pady=2, sticky="w")
            
            self.risk_labels[metric] = value_label
    
    def toggle_auto_refresh(self):
        """Toggle auto refresh functionality"""
        if self.auto_refresh_var.get():
            self.schedule_auto_refresh()
        else:
            # Cancel any scheduled refresh
            pass
    
    def schedule_auto_refresh(self):
        """Schedule automatic dashboard refresh"""
        if self.auto_refresh_var.get() and self.parent.winfo_exists():
            self.refresh_dashboard()
            # Schedule next refresh only if parent still exists
            if self.parent.winfo_exists():
                self.safe_after(30000, self.schedule_auto_refresh)
    
    def refresh_dashboard(self):
        """Refresh all dashboard data"""
        if self.analysis_result:
            self.update_dashboard()
        
        if self.ai_results:
            self.update_ai_dashboard()
        
        self.status_label.configure(text=f"Dashboard refreshed at {datetime.now().strftime('%H:%M:%S')}")
    
    def on_analysis_complete(self, result):
        """Handle analysis complete event"""
        self.analysis_result = result
        self.update_dashboard()
    
    def on_ai_analysis_complete(self, results):
        """Handle AI analysis complete event"""
        self.ai_results = results
        self.update_ai_dashboard()
    
    def update_dashboard(self):
        """Update dashboard with analysis results"""
        if not self.analysis_result:
            return
        
        # Update overview stats
        stats_data = {
            'Total Trades': self.analysis_result.total_trades,
            'Win Rate': f"{self.analysis_result.win_rate:.2%}",
            'Net Profit': f"${self.analysis_result.net_profit:.2f}",
            'Profit Factor': f"{self.analysis_result.profit_factor:.2f}",
            'Max Drawdown': f"{self.analysis_result.max_drawdown:.2f}%",
            'Best Hour': f"{self.analysis_result.best_hour}:00"
        }
        
        self.dashboard_stats.update_stats(stats_data)
        
        # Update performance metrics
        self.performance_labels["Total Trades"].configure(text=str(self.analysis_result.total_trades))
        self.performance_labels["Win Rate"].configure(text=f"{self.analysis_result.win_rate:.2%}")
        self.performance_labels["Net Profit"].configure(text=f"${self.analysis_result.net_profit:.2f}")
        self.performance_labels["Profit Factor"].configure(text=f"{self.analysis_result.profit_factor:.2f}")
        self.performance_labels["Max Drawdown"].configure(text=f"{self.analysis_result.max_drawdown:.2f}%")
        self.performance_labels["Best Trade"].configure(text=f"${self.analysis_result.best_trade.profit:.2f}")
        self.performance_labels["Worst Trade"].configure(text=f"${self.analysis_result.worst_trade.profit:.2f}")
        self.performance_labels["Avg Win"].configure(text=f"${self.analysis_result.average_profit:.2f}")
        self.performance_labels["Avg Loss"].configure(text=f"${self.analysis_result.average_loss:.2f}")
        self.performance_labels["Max Consecutive Wins"].configure(text=str(self.analysis_result.max_consecutive_wins))
        self.performance_labels["Max Consecutive Losses"].configure(text=str(self.analysis_result.max_consecutive_losses))
        
        # Calculate and add Sharpe ratio
        if self.analysis_result.total_trades > 1:
            profits = [trade.profit for trade in self.app.current_trades]
            import numpy as np
            if len(profits) > 1:
                sharpe_ratio = np.mean(profits) / np.std(profits) if np.std(profits) != 0 else 0
                self.performance_labels["Sharpe Ratio"].configure(text=f"{sharpe_ratio:.2f}")
        
        # Update charts
        self.update_dashboard_charts()
        
        # Update risk analysis
        self.update_risk_analysis()
    
    def update_dashboard_charts(self):
        """Update dashboard charts"""
        if not self.analysis_result:
            return
        
        # Clear existing plots
        for ax in self.dashboard_axes.flat:
            ax.clear()
        
        # Plot 1: Equity Curve
        equity_curve = self.analysis_result.equity_curve
        self.dashboard_axes[0, 0].plot(equity_curve, linewidth=2, color='blue')
        self.dashboard_axes[0, 0].set_title('Equity Curve')
        self.dashboard_axes[0, 0].set_xlabel('Trade Number')
        self.dashboard_axes[0, 0].set_ylabel('Cumulative Profit ($)')
        self.dashboard_axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Profit Distribution
        profits = [trade.profit for trade in self.app.current_trades]
        self.dashboard_axes[0, 1].hist(profits, bins=20, color='green', alpha=0.7, edgecolor='black')
        self.dashboard_axes[0, 1].set_title('Profit Distribution')
        self.dashboard_axes[0, 1].set_xlabel('Profit ($)')
        self.dashboard_axes[0, 1].set_ylabel('Frequency')
        self.dashboard_axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Win Rate by Hour
        hours = list(self.analysis_result.trades_by_hour.keys())
        win_rates = [self.analysis_result.trades_by_hour[hour]['win_rate'] for hour in hours]
        
        self.dashboard_axes[0, 2].bar(hours, win_rates, color='orange', alpha=0.7)
        self.dashboard_axes[0, 2].set_title('Win Rate by Hour')
        self.dashboard_axes[0, 2].set_xlabel('Hour of Day')
        self.dashboard_axes[0, 2].set_ylabel('Win Rate')
        self.dashboard_axes[0, 2].set_ylim(0, 1)
        self.dashboard_axes[0, 2].grid(True, alpha=0.3)
        
        # Plot 4: Asset Performance
        assets = list(self.analysis_result.trades_by_asset.keys())[:5]  # Top 5
        asset_profits = [self.analysis_result.trades_by_asset[asset]['total_profit'] for asset in assets]
        
        colors = ['green' if profit > 0 else 'red' for profit in asset_profits]
        self.dashboard_axes[1, 0].barh(assets, asset_profits, color=colors, alpha=0.7)
        self.dashboard_axes[1, 0].set_title('Top Asset Performance')
        self.dashboard_axes[1, 0].set_xlabel('Profit ($)')
        self.dashboard_axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 5: Cumulative Profit
        cumulative_profits = pd.Series(profits).cumsum()
        self.dashboard_axes[1, 1].fill_between(range(len(cumulative_profits)), cumulative_profits, alpha=0.3, color='blue')
        self.dashboard_axes[1, 1].plot(cumulative_profits, linewidth=2, color='blue')
        self.dashboard_axes[1, 1].set_title('Cumulative Profit')
        self.dashboard_axes[1, 1].set_xlabel('Trade Number')
        self.dashboard_axes[1, 1].set_ylabel('Cumulative Profit ($)')
        self.dashboard_axes[1, 1].grid(True, alpha=0.3)
        
        # Plot 6: Trade Results Pie Chart
        win_count = self.analysis_result.winning_trades
        loss_count = self.analysis_result.losing_trades
        
        self.dashboard_axes[1, 2].pie(
            [win_count, loss_count], 
            labels=['Wins', 'Losses'],
            colors=['lightgreen', 'lightcoral'],
            autopct='%1.1f%%'
        )
        self.dashboard_axes[1, 2].set_title('Win/Loss Distribution')
        
        # Adjust layout and refresh
        self.dashboard_fig.tight_layout()
        self.dashboard_canvas.draw()
    
    def update_ai_dashboard(self):
        """Update AI insights section"""
        if not self.ai_results:
            return
        
        # Generate AI insights
        insights = self.generate_dashboard_ai_insights()
        
        # Update AI insights text
        self.ai_insights_text.delete("1.0", "end")
        self.ai_insights_text.insert("1.0", insights)
    
    def update_risk_analysis(self):
        """Update risk analysis section"""
        if not self.analysis_result:
            return
        
        # Calculate risk metrics
        profits = [trade.profit for trade in self.app.current_trades]
        equity_curve = self.analysis_result.equity_curve
        
        # Current drawdown
        current_drawdown = self.analysis_result.max_drawdown
        self.risk_labels["Current Drawdown"].configure(text=f"{current_drawdown:.2f}%")
        
        # Simple risk of ruin calculation
        if len(profits) > 1:
            import numpy as np
            avg_profit = np.mean(profits)
            std_profit = np.std(profits)
            
            if std_profit > 0:
                # Simplified risk of ruin calculation
                risk_of_ruin = max(0, min(1, -avg_profit / std_profit))
                self.risk_labels["Risk of Ruin"].configure(text=f"{risk_of_ruin:.2%}")
            
            # Value at Risk (95%)
            var_95 = np.percentile(profits, 5)
            self.risk_labels["Value at Risk (95%)"].configure(text=f"${var_95:.2f}")
            
            # Conditional VaR (95%)
            cvar_95 = np.mean([p for p in profits if p <= var_95])
            self.risk_labels["Conditional VaR (95%)"].configure(text=f"${cvar_95:.2f}")
            
            # Portfolio volatility
            volatility = np.std(profits) * np.sqrt(252)  # Annualized
            self.risk_labels["Portfolio Volatility"].configure(text=f"{volatility:.2%}")
            
            # Risk-adjusted return (Sharpe ratio)
            sharpe_ratio = avg_profit / std_profit if std_profit != 0 else 0
            self.risk_labels["Risk-Adjusted Return"].configure(text=f"{sharpe_ratio:.2f}")
    
    def generate_dashboard_ai_insights(self) -> str:
        """Generate AI insights for dashboard"""
        if not self.ai_results:
            return "No AI analysis available"
        
        insights = []
        
        # Top recommendations
        top_3 = self.ai_results[:3]
        insights.append("🏆 TOP AI RECOMMENDATIONS:")
        for i, result in enumerate(top_3, 1):
            insights.append(f"{i}. {result.pair} - {result.recommendation} (Score: {result.overall_score:.2f})")
        
        insights.append("")
        
        # Market insights
        high_confidence = [r for r in self.ai_results if r.confidence >= 70]
        insights.append(f"🧠 AI MARKET INSIGHTS:")
        insights.append(f"• High confidence pairs: {len(high_confidence)}/{len(self.ai_results)}")
        
        # Trend analysis
        strong_trends = [r for r in self.ai_results if r.trend_score >= 70]
        if strong_trends:
            insights.append(f"• Strong trending pairs: {len(strong_trends)}")
            insights.append(f"• Top trend: {strong_trends[0].pair}")
        
        # Risk assessment
        avoid_pairs = [r for r in self.ai_results if r.recommendation == "AVOID"]
        if avoid_pairs:
            insights.append(f"• Pairs to avoid: {len(avoid_pairs)}")
        
        return "\n".join(insights)
    
    def export_dashboard(self):
        """Export dashboard as image or report"""
        if not self.analysis_result:
            messagebox.showwarning("Warning", "No dashboard data to export")
            return
        
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.png'):
                    self.dashboard_fig.savefig(file_path, dpi=300, bbox_inches='tight')
                elif file_path.endswith('.pdf'):
                    self.dashboard_fig.savefig(file_path, format='pdf', bbox_inches='tight')
                
                messagebox.showinfo("Success", f"Dashboard exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
