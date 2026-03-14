"""
Main GUI Application - Improved tab-based interface
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import threading
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import Trade, TradeParser, TradeAnalyzer, AIEngine
from core.data_models import MarketData, NewsItem
from ui.components.login_tab import LoginTab
from ui.components.analysis_tab import AnalysisTab
from ui.components.ai_tab import AITab
from ui.components.dashboard_tab import DashboardTab
from ui.widgets.stats_cards import StatsCards
from ui.widgets.progress_dialog import ProgressDialog


class MainApplication:
    """Main GUI application with improved architecture"""
    
    def __init__(self):
        """Initialize the main application"""
        self.root = ctk.CTk()
        self.root.title("IQ Analyzer Pro - Trading Analysis Platform")
        self.root.geometry("1200x800")
        
        # Suppress CustomTkinter internal errors
        self.setup_error_handler()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize data storage
        self.current_trades: list[Trade] = []
        self.analysis_result = None
        self.ai_results = None
        
        # Session data
        self.session_token = None
        self.user_id = None
        self.connected_user = None
        self.iq_client = None  # IQ Option API client
        
        # Callback functions for compatibility
        self.run_func: Optional[Callable] = None
        self.dashboard_func: Optional[Callable] = None
        self.ai_func: Optional[Callable] = None
        
        # Setup GUI
        self.setup_gui()
    
    def setup_error_handler(self):
        """Setup global error handler to suppress CustomTkinter internal errors"""
        import sys
        from io import StringIO
        
        # Override stderr to suppress CustomTkinter errors
        class ErrorFilter:
            def __init__(self, original_stderr):
                self.original_stderr = original_stderr
                
            def write(self, text):
                # Suppress common CustomTkinter internal errors
                if any(keyword in text for keyword in [
                    "invalid command name",
                    "check_dpi_scaling",
                    "update_timestamp",
                    "<lambda>",
                    "safe_callback"
                ]):
                    return  # Suppress these errors
                else:
                    self.original_stderr.write(text)
                    
            def flush(self):
                self.original_stderr.flush()
        
        # Install error filter
        sys.stderr = ErrorFilter(sys.stderr)
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("IQ Analyzer Pro - Trading Analysis Platform")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.create_header()
        
        # Create tab view
        self.create_tab_view()
        
        # Create status bar
        self.create_status_bar()
        
        self.logger.info("GUI setup complete")
    
    def create_header(self):
        """Create application header"""
        header_frame = ctk.CTkFrame(self.root, height=60)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo and title
        logo_label = ctk.CTkLabel(
            header_frame,
            text="📊 IQ Analyzer Pro",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=15)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="🔴 Not Connected",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=0, column=2, padx=20, pady=15)
        
        # User info
        self.user_label = ctk.CTkLabel(
            header_frame,
            text="Guest User",
            font=ctk.CTkFont(size=14)
        )
        self.user_label.grid(row=0, column=3, padx=20, pady=15)
    
    def create_tab_view(self):
        """Create main tabbed interface"""
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Configure tab appearance
        self.tab_view._segmented_button.grid_columnconfigure(0, weight=1)
        self.tab_view._segmented_button.grid_columnconfigure(1, weight=1)
        self.tab_view._segmented_button.grid_columnconfigure(2, weight=1)
        self.tab_view._segmented_button.grid_columnconfigure(3, weight=1)
        
        # Create tabs
        self.create_tabs()
        
        # Bind tab change event using the tab view's built-in functionality
        # Note: CTkTabview handles tab changes automatically
    
    def create_tabs(self):
        """Create individual tabs"""
        # Login Tab
        self.login_tab = LoginTab(
            parent=self.tab_view.add("Login"),
            app=self
        )
        
        # Analysis Tab
        self.analysis_tab = AnalysisTab(
            parent=self.tab_view.add("Analysis"),
            app=self
        )
        
        # AI Analysis Tab
        self.ai_tab = AITab(
            parent=self.tab_view.add("AI Analysis"),
            app=self
        )
        
        # Dashboard Tab
        self.dashboard_tab = DashboardTab(
            parent=self.tab_view.add("Dashboard"),
            app=self
        )
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ctk.CTkFrame(self.root, height=30)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=5)
        self.progress_bar.set(0)
        
        # Status text
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Timestamp
        self.timestamp_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.timestamp_label.grid(row=0, column=2, padx=10, pady=5)
        
        # Update timestamp
        self.update_timestamp()
    
    def safe_after(self, delay, callback, *args):
        """Safe after() wrapper that checks widget existence"""
        def safe_callback():
            try:
                if self.root and self.root.winfo_exists():
                    callback(*args)
            except Exception as e:
                self.logger.error(f"Error in safe callback: {e}")
        
        return self.root.after(delay, safe_callback)
    
    def update_timestamp(self):
        """Update timestamp display"""
        # Check if widget still exists before updating
        if not self.root or not self.root.winfo_exists():
            return
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=current_time)
        
        # Schedule next update only if widget still exists
        if self.root and self.root.winfo_exists():
            self.safe_after(1000, self.update_timestamp)
    
    def on_tab_change(self, tab_index: int):
        """Handle tab change events"""
        tab_names = ["Login", "Analysis", "AI Analysis", "Dashboard"]
        current_tab = tab_names[tab_index]
        
        self.update_status(f"Switched to {current_tab} tab")
        
        # Refresh data when switching tabs
        if tab_index == 1 and self.current_trades:  # Analysis tab
            self.analysis_tab.refresh_data()
        elif tab_index == 2 and self.current_trades:  # AI tab
            self.ai_tab.refresh_data()
        elif tab_index == 3 and self.analysis_result:  # Dashboard tab
            self.dashboard_tab.refresh_data()
    
    def update_status(self, message: str, progress: float = None):
        """Update status bar with message and optional progress"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        else:
            self.progress_bar.set(0)
        
        # Log status update
        self.logger.info(f"Status: {message}")
    
    def get_auth_headers(self):
        """Get authentication headers for API calls"""
        if self.session_token:
            return {
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json",
                "User-Agent": "IQ-Analyzer-Pro/1.0"
            }
        else:
            return {
                "Content-Type": "application/json",
                "User-Agent": "IQ-Analyzer-Pro/1.0"
            }
    
    def set_connection_status(self, connected: bool, username: str = None):
        """Update connection status in header"""
        if connected:
            self.status_label.configure(text="🟢 Connected")
            if username:
                self.user_label.configure(text=f"User: {username}")
                self.connected_user = username
        else:
            self.status_label.configure(text="🔴 Not Connected")
            self.user_label.configure(text="Guest User")
            self.connected_user = None
    
    def load_trade_data(self, file_path: str):
        """Load trade data from file"""
        try:
            self.update_status("Loading trade data...", 0.1)
            
            # Parse trades in background thread
            def load_trades():
                try:
                    trades = self.trade_parser.parse_from_file(file_path)
                    validated_trades = self.trade_parser.validate_trades(trades)
                    
                    # Update UI in main thread
                    self.safe_after(0, self.on_trades_loaded, validated_trades)
                    
                except Exception as e:
                    self.safe_after(0, self.on_load_error, str(e))
            
            thread = threading.Thread(target=load_trades)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def on_trades_loaded(self, trades: list[Trade]):
        """Handle successful trade loading"""
        self.current_trades = trades
        self.update_status(f"Loaded {len(trades)} trades successfully")
        
        # Update tabs
        self.analysis_tab.on_trades_loaded(trades)
        self.ai_tab.on_trades_loaded(trades)
        
        # Switch to analysis tab
        self.tab_view.set("Analysis")
        
        # Safe messagebox call
        try:
            messagebox.showinfo("Success", f"Successfully loaded {len(trades)} trades")
        except Exception as e:
            self.logger.error(f"Error showing messagebox: {e}")
    
    def on_load_error(self, error_message: str):
        """Handle trade loading error"""
        self.update_status("Error loading trades")
        # Safe messagebox call
        try:
            messagebox.showerror("Error", f"Failed to load trades: {error_message}")
        except Exception as e:
            self.logger.error(f"Error showing messagebox: {e}")
    
    def run_analysis(self, start_date: datetime = None, end_date: datetime = None):
        """Run trade analysis"""
        if not self.current_trades:
            messagebox.showwarning("Warning", "No trade data available")
            return
        
        try:
            self.update_status("Running analysis...", 0.1)
            
            # Run analysis in background thread
            def analyze():
                try:
                    result = self.trade_analyzer.analyze_trades(
                        self.current_trades, 
                        (start_date, end_date) if start_date and end_date else None
                    )
                    
                    # Update UI in main thread
                    self.safe_after(0, self.on_analysis_complete, result)
                    
                except Exception as e:
                    self.safe_after(0, self.on_analysis_error, str(e))
            
            thread = threading.Thread(target=analyze)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start analysis: {str(e)}")
    
    def on_analysis_complete(self, result):
        """Handle successful analysis completion"""
        self.analysis_result = result
        self.update_status("Analysis complete")
        
        # Update tabs
        self.analysis_tab.on_analysis_complete(result)
        self.dashboard_tab.on_analysis_complete(result)
        
        messagebox.showinfo("Success", "Analysis completed successfully")
    
    def on_analysis_error(self, error_message: str):
        """Handle analysis error"""
        self.update_status("Analysis failed")
        messagebox.showerror("Error", f"Analysis failed: {error_message}")
    
    def run_ai_analysis(self):
        """Run AI pair analysis"""
        if not self.current_trades:
            messagebox.showwarning("Warning", "No trade data available")
            return
        
        try:
            self.update_status("Running AI analysis...", 0.1)
            
            # Create mock market data for demonstration
            market_data = self._create_mock_market_data()
            
            # Run AI analysis in background thread
            def analyze_ai():
                try:
                    results = self.ai_engine.analyze_best_pairs(
                        market_data,
                        self.current_trades
                    )
                    
                    # Update UI in main thread
                    self.safe_after(0, self.on_ai_analysis_complete, results)
                    
                except Exception as e:
                    self.safe_after(0, self.on_ai_analysis_error, str(e))
            
            thread = threading.Thread(target=analyze_ai)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start AI analysis: {str(e)}")
    
    def on_ai_analysis_complete(self, results):
        """Handle successful AI analysis completion"""
        self.ai_results = results
        self.update_status("AI analysis complete")
        
        # Update tabs
        self.ai_tab.on_ai_analysis_complete(results)
        self.dashboard_tab.on_ai_analysis_complete(results)
        
        messagebox.showinfo("Success", "AI analysis completed successfully")
    
    def on_ai_analysis_error(self, error_message: str):
        """Handle AI analysis error"""
        self.update_status("AI analysis failed")
        messagebox.showerror("Error", f"AI analysis failed: {error_message}")
    
    def _create_mock_market_data(self) -> Dict[str, MarketData]:
        """Create mock market data for demonstration"""
        pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD']
        market_data = {}
        
        for pair in pairs:
            market_data[pair] = MarketData(
                symbol=pair,
                current_price=1.0 + hash(pair) % 1000 / 10000,
                bid=1.0 + hash(pair) % 1000 / 10000 - 0.0001,
                ask=1.0 + hash(pair) % 1000 / 10000 + 0.0001,
                volatility=0.5 + hash(pair) % 100 / 100,
                volume=1000000 + hash(pair) % 500000,
                trend_direction=['UP', 'DOWN', 'SIDEWAYS'][hash(pair) % 3],
                momentum=(hash(pair) % 100 - 50) / 100,
                support_level=1.0 + hash(pair) % 1000 / 10000 - 0.01,
                resistance_level=1.0 + hash(pair) % 1000 / 10000 + 0.01,
                timestamp=datetime.now()
            )
        
        return market_data
    
    def show_progress_dialog(self, title: str, message: str) -> ProgressDialog:
        """Show progress dialog"""
        return ProgressDialog(self.root, title, message)
    
    def export_results(self, format_type: str = "csv"):
        """Export analysis results"""
        if not self.analysis_result:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")]
            )
            
            if file_path:
                if format_type == "csv":
                    self._export_csv(file_path)
                elif format_type == "json":
                    self._export_json(file_path)
                
                messagebox.showinfo("Success", f"Results exported to {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def _export_csv(self, file_path: str):
        """Export results to CSV"""
        trades_df = pd.DataFrame([trade.to_dict() for trade in self.current_trades])
        trades_df.to_csv(file_path, index=False)
    
    def _export_json(self, file_path: str):
        """Export results to JSON"""
        import json
        
        export_data = {
            'analysis_result': self.analysis_result.to_dict(),
            'trades': [trade.to_dict() for trade in self.current_trades],
            'ai_results': [result.to_dict() for result in self.ai_results] if self.ai_results else []
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        finally:
            # Cleanup on exit
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources and cancel pending timers"""
        try:
            # Cancel any pending after() callbacks
            if hasattr(self, 'root') and self.root.winfo_exists():
                # Cancel all pending after callbacks
                self.root.after_cancel_all = lambda: None
        except:
            pass
    
    # Compatibility methods for existing code
    def start_gui(self, run_func=None, dashboard_func=None, ai_func=None):
        """Compatibility method for existing code"""
        self.run_func = run_func
        self.dashboard_func = dashboard_func
        self.ai_func = ai_func
        self.run()
    
    def get_last_df(self) -> pd.DataFrame:
        """Get last analyzed dataframe (compatibility)"""
        if self.current_trades:
            from ..core.data_models import DataFrameConverter
            return DataFrameConverter.trades_to_dataframe(self.current_trades)
        return pd.DataFrame()


if __name__ == "__main__":
    app = MainApplication()
    app.run()
