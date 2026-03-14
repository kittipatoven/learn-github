"""
Login Tab - User authentication and data loading
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
from ui.widgets.stats_cards import StatsCards
from services.iq_option_api import IQOptionAPI
from tkinter import filedialog, messagebox
import tkinter as tk
import threading
import logging
from datetime import datetime
from typing import Optional


class LoginTab:
    """Login and data loading tab"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.iq_api = IQOptionAPI()  # Initialize API client
        self.logger = logging.getLogger(__name__)  # Add logger
        self.setup_ui()
    
    def safe_after(self, delay, callback, *args):
        """Safe after() wrapper that uses main app's safe_after"""
        return self.app.safe_after(delay, callback, *args)
    
    def setup_ui(self):
        """Setup the login tab UI"""
        # Configure parent grid
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        
        # Create main sections
        self.create_login_section()
        self.create_data_loading_section()
        self.create_info_section()
    
    def create_login_section(self):
        """Create login form section"""
        login_frame = ctk.CTkFrame(self.parent)
        login_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            login_frame,
            text="🔐 IQ Option Login",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Email field
        email_label = ctk.CTkLabel(login_frame, text="Email:")
        email_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.username_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Enter your IQ Option email",
            width=250
        )
        self.username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Password field
        password_label = ctk.CTkLabel(login_frame, text="Password:")
        password_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Enter your password",
            show="*",
            width=250
        )
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Account Type selector
        account_type_label = ctk.CTkLabel(login_frame, text="Account Type:")
        account_type_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.account_type_var = tk.StringVar(value="PRACTICE")
        self.account_type_menu = ctk.CTkOptionMenu(
            login_frame,
            variable=self.account_type_var,
            values=["PRACTICE", "REAL"],
            width=250
        )
        self.account_type_menu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        # Trade Type selector
        trade_type_label = ctk.CTkLabel(login_frame, text="Trade Type:")
        trade_type_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        self.trade_type_var = tk.StringVar(value="binary-option")
        self.trade_type_menu = ctk.CTkOptionMenu(
            login_frame,
            variable=self.trade_type_var,
            values=["binary-option", "digital-option"],
            width=250
        )
        self.trade_type_menu.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        
        # Login button
        self.login_button = ctk.CTkButton(
            login_frame,
            text="Login to IQ Option",
            command=self.login,
            width=250
        )
        self.login_button.grid(row=5, column=0, columnspan=2, pady=15)
        
        # Status
        self.login_status = ctk.CTkLabel(
            login_frame,
            text="Not connected",
            font=ctk.CTkFont(size=12)
        )
        self.login_status.grid(row=6, column=0, columnspan=2, pady=5)
    
    def create_data_loading_section(self):
        """Create data loading section"""
        data_frame = ctk.CTkFrame(self.parent)
        data_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        
        # Title
        data_title = ctk.CTkLabel(
            data_frame,
            text="📁 Load Trade Data",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        data_title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # File selection
        file_label = ctk.CTkLabel(data_frame, text="Select File:")
        file_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ctk.CTkEntry(data_frame, textvariable=self.file_path_var)
        self.file_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        browse_button = ctk.CTkButton(
            data_frame,
            text="Browse",
            command=self.browse_file,
            width=80
        )
        browse_button.grid(row=1, column=2, padx=10, pady=5)
        
        # Date range
        date_label = ctk.CTkLabel(data_frame, text="Date Range:")
        date_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        
        start_date_entry = ctk.CTkEntry(
            data_frame,
            placeholder_text="YYYY-MM-DD",
            textvariable=self.start_date_var,
            width=120
        )
        start_date_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        end_date_entry = ctk.CTkEntry(
            data_frame,
            placeholder_text="YYYY-MM-DD",
            textvariable=self.end_date_var,
            width=120
        )
        end_date_entry.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        
        # Load button
        self.load_button = ctk.CTkButton(
            data_frame,
            text="Load Data",
            command=self.load_data,
            width=250
        )
        self.load_button.grid(row=3, column=0, columnspan=3, pady=15)
        
        # Status
        self.data_status = ctk.CTkLabel(
            data_frame,
            text="No data loaded",
            font=ctk.CTkFont(size=12)
        )
        self.data_status.grid(row=4, column=0, columnspan=3, pady=5)
    
    def create_info_section(self):
        """Create information section"""
        info_frame = ctk.CTkFrame(self.parent)
        info_frame.grid(row=3, column=1, sticky="ew", padx=10, pady=10)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ️ Login with your IQ Option credentials to automatically load your trading history.\n"
                 "Alternatively, load trade data from a CSV, Excel, or JSON file.",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
    
    def login(self):
        """Handle login button click"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        account_type = self.account_type_var.get()
        trade_type = self.trade_type_var.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter username and password")
            return
        
        # Log selections
        self.logger.info(f"Selected account type: {account_type}")
        self.logger.info(f"Selected trade type: {trade_type}")
        
        # Update UI
        self.login_status.configure(text="Connecting...")
        self.login_button.configure(state="disabled")
        
        def login_process():
            # Use REAL IQ Option API for authentication
            result = self.iq_api.connect(username, password, account_type)
            
            # Update UI in main thread
            if result["success"]:
                self.safe_after(0, self.on_login_complete, username, 
                                 result.get("user_id"), result.get("client"))
            else:
                self.safe_after(0, self.on_login_error, result.get("message", "Unknown error"))
        
        thread = threading.Thread(target=login_process)
        thread.daemon = True
        thread.start()
    
    def on_login_complete(self, username: str, user_id: str = None, client = None):
        """Handle successful login"""
        # Use safe_after for all GUI updates
        self.safe_after(0, lambda: self.login_status.configure(text=f"Connected as {username}"))
        self.safe_after(0, lambda: self.login_button.configure(state="normal"))
        
        # Store session data
        if user_id and client:
            self.app.iq_client = client
            self.app.user_id = user_id
            self.safe_after(0, lambda: self.app.update_status(f"Authenticated with IQ Option as {username}"))
            
            # Auto-load trade history
            self.load_trade_history()
        else:
            # Fallback for simulated login
            self.app.set_connection_status(True, username)
            self.safe_after(0, lambda: self.app.update_status(f"Logged in as {username}"))
        
        # Use safe_after for messagebox to avoid threading issues
        self.safe_after(0, lambda: messagebox.showinfo("Success", f"Successfully logged in as {username}"))
    
    def on_login_error(self, error_msg: str):
        """Handle login error"""
        # Use safe_after for all GUI updates
        self.safe_after(0, lambda: self.login_status.configure(text="Login failed"))
        self.safe_after(0, lambda: self.login_button.configure(state="normal"))
        self.app.set_connection_status(False, "")
        self.safe_after(0, lambda: self.app.update_status(f"Login error: {error_msg}"))
        # Use safe_after for messagebox to avoid threading issues
        self.safe_after(0, lambda: messagebox.showerror("Login Error", error_msg))
    
    def load_trade_history(self):
        """Load trade history from IQ Option API"""
        if not hasattr(self.app, 'iq_client') or not self.app.iq_client:
            self.safe_after(0, lambda: self.app.update_status("Not connected to IQ Option"))
            return
        
        self.safe_after(0, lambda: self.app.update_status("Loading trade history from IQ Option...", 0.1))
        
        # Get trade type in main thread before starting background thread
        trade_type = self.trade_type_var.get()
        self.logger.info(f"Loading {trade_type} trade history...")
        
        def load_process():
            try:
                # Use trade_type captured from main thread
                result = self.iq_api.get_trade_history(limit=1000, trade_type=trade_type)
                
                if result["success"]:
                    trades = result.get("trades", [])
                    self.logger.info(f"Retrieved {len(trades)} {trade_type} trades from IQ Option")
                    
                    # Convert to Trade objects
                    from core.data_models import Trade, TradeResult, TradeType
                    trade_objects = []
                    for trade_data in trades:
                        try:
                            # Convert direction to TradeType
                            direction = trade_data.get("direction", "call").upper()
                            trade_type = TradeType.CALL if direction == "CALL" else TradeType.PUT
                            
                            # Convert result to TradeResult
                            result_str = trade_data.get("result", "draw").upper()
                            if result_str == "WIN":
                                trade_result = TradeResult.WIN
                            elif result_str == "LOSE":
                                trade_result = TradeResult.LOSS
                            else:
                                trade_result = TradeResult.DRAW
                            
                            # Handle timestamp
                            timestamp = trade_data.get("open_time", datetime.now())
                            if isinstance(timestamp, str):
                                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            
                            trade = Trade(
                                id=trade_data.get("iq_trade_id", ""),
                                timestamp=timestamp,
                                asset=trade_data.get("asset", ""),
                                trade_type=trade_type,
                                amount=trade_data.get("amount", 0.0),
                                payout=trade_data.get("amount", 0.0) + trade_data.get("profit", 0.0),
                                result=trade_result,
                                profit=trade_data.get("profit", 0.0)
                            )
                            trade_objects.append(trade)
                        except Exception as e:
                            self.logger.warning(f"Error converting trade {trade_data}: {e}")
                            continue
                    
                    # Store in app
                    self.app.current_trades = trade_objects
                    self.logger.info(f"Converted {len(trade_objects)} trades to Trade objects")
                    
                    # Update UI
                    self.safe_after(0, self.on_trade_history_loaded, len(trade_objects))
                else:
                    error_msg = result.get("message", "Failed to load trade history")
                    self.logger.error(f"Trade history error: {error_msg}")
                    self.safe_after(0, self.on_trade_history_error, error_msg)
                    
            except Exception as e:
                error_msg = f"Error loading trade history: {str(e)}"
                self.logger.error(error_msg)
                self.safe_after(0, self.on_trade_history_error, error_msg)
        
        thread = threading.Thread(target=load_process)
        thread.daemon = True
        thread.start()
    
    def on_trade_history_loaded(self, trade_count: int):
        """Handle successful trade history loading"""
        # Use safe_after for all GUI updates
        self.safe_after(0, lambda: self.app.update_status(f"Loaded {trade_count} trades from IQ Option"))
        self.safe_after(0, lambda: self.data_status.configure(text=f"Loaded {trade_count} trades from IQ Option"))
        
        self.logger.info(f"Successfully loaded {trade_count} trades")
        
        # Trigger analysis if we have trades
        if trade_count > 0:
            self.safe_after(0, lambda: self.app.update_status("Analyzing trades...", 0.9))
            # Switch to analysis tab
            self.safe_after(1000, self.switch_to_analysis_tab)
            
            # Refresh other tabs
            self.refresh_all_tabs()
        else:
            self.safe_after(0, lambda: self.app.update_status("No trades found in the specified period"))
    
    def refresh_all_tabs(self):
        """Refresh all tabs with new trade data"""
        try:
            # Refresh analysis tab
            if hasattr(self.app, 'analysis_tab') and self.app.analysis_tab:
                self.safe_after(1500, self._safe_refresh_analysis_tab)
            
            # Refresh AI tab
            if hasattr(self.app, 'ai_tab') and self.app.ai_tab:
                self.safe_after(2000, self._safe_refresh_ai_tab)
            
            # Refresh dashboard tab
            if hasattr(self.app, 'dashboard_tab') and self.app.dashboard_tab:
                self.safe_after(2500, self._safe_refresh_dashboard_tab)
                
        except Exception as e:
            self.logger.error(f"Error refreshing tabs: {e}")
    
    def _safe_refresh_analysis_tab(self):
        """Safe refresh for analysis tab"""
        try:
            if (self.parent.winfo_exists() and 
                hasattr(self.app, 'analysis_tab') and 
                self.app.analysis_tab):
                # Use safe_after for GUI call
                self.safe_after(0, self.app.analysis_tab.refresh_data)
        except Exception as e:
            self.logger.error(f"Error refreshing analysis tab: {e}")
    
    def _safe_refresh_ai_tab(self):
        """Safe refresh for AI tab"""
        try:
            if (self.parent.winfo_exists() and 
                hasattr(self.app, 'ai_tab') and 
                self.app.ai_tab):
                # Use safe_after for GUI call
                self.safe_after(0, self.app.ai_tab.refresh_data)
        except Exception as e:
            self.logger.error(f"Error refreshing AI tab: {e}")
    
    def _safe_refresh_dashboard_tab(self):
        """Safe refresh for dashboard tab"""
        try:
            if (self.parent.winfo_exists() and 
                hasattr(self.app, 'dashboard_tab') and 
                self.app.dashboard_tab):
                # Use safe_after for GUI call
                self.safe_after(0, self.app.dashboard_tab.refresh_data)
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard tab: {e}")
    
    def on_trade_history_error(self, error_msg: str):
        """Handle trade history loading error"""
        # Use safe_after for all GUI updates
        self.safe_after(0, lambda: self.app.update_status(f"Trade history error: {error_msg}"))
        self.safe_after(0, lambda: self.data_status.configure(text="Failed to load trades"))
        # Use safe_after for messagebox to avoid threading issues
        self.safe_after(0, lambda: messagebox.showerror("Trade History Error", error_msg))
    
    def switch_to_analysis_tab(self):
        """Switch to analysis tab"""
        try:
            # Get tab view from main app
            if hasattr(self.app, 'tab_view'):
                # Use safe_after for GUI call
                self.safe_after(0, lambda: self.app.tab_view.set("Analysis"))
        except Exception as e:
            self.logger.error(f"Error switching to analysis tab: {e}")
    
    def browse_file(self):
        """Browse for trade data file"""
        file_path = filedialog.askopenfilename(
            title="Select Trade Data File",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_data(self):
        """Load trade data from file or API"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            # Use safe_after for messagebox to avoid threading issues
            self.safe_after(0, lambda: messagebox.showwarning("Warning", "Please select a file"))
            return
        
        # Parse date range if provided
        start_date = None
        end_date = None
        
        try:
            if self.start_date_var.get():
                start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            
            if self.end_date_var.get():
                end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
        except ValueError:
            # Use safe_after for messagebox to avoid threading issues
            self.safe_after(0, lambda: messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD"))
            return
        
        # Update UI
        self.safe_after(0, lambda: self.data_status.configure(text="Loading data..."))
        self.safe_after(0, lambda: self.load_button.configure(state="disabled"))
        
        # Capture GUI variables in main thread before starting background thread
        captured_start_date = start_date
        captured_end_date = end_date
        captured_file_path = file_path
        
        def load_process():
            try:
                # Try to load from IQ Option API first if authenticated
                if self.iq_api.is_authenticated():
                    self.safe_after(0, lambda: self.app.update_status("Loading trades from IQ Option API...", 0.1))
                    api_result = self.iq_api.get_trades(captured_start_date, captured_end_date)
                    
                    if api_result["success"]:
                        trades = api_result.get("trades", [])
                        self.safe_after(0, self.on_data_loaded, trades)
                        return
                    else:
                        # Fallback to file loading if API fails
                        self.safe_after(0, lambda: self.app.update_status("API loading failed, loading from file...", 0.1))
                
                # Load from file
                self.safe_after(0, lambda: self.app.update_status("Loading trade data from file...", 0.1))
                trades = self.app.trade_parser.parse_from_file(captured_file_path)
                self.safe_after(0, self.on_data_loaded, trades)
                
            except Exception as e:
                error_msg = f"Error loading data: {str(e)}"
                self.safe_after(0, self.on_data_error, error_msg)
        
        thread = threading.Thread(target=load_process)
        thread.daemon = True
        thread.start()
    
    def on_data_loaded(self, trades):
        """Handle successful data loading"""
        # Use safe_after for all GUI updates
        self.safe_after(0, lambda: self.data_status.configure(text=f"Loaded {len(self.app.current_trades)} trades"))
        self.safe_after(0, lambda: self.load_button.configure(state="normal"))
        
        # Update date range if not set
        if not self.start_date_var.get() and self.app.current_trades:
            first_trade = min(self.app.current_trades, key=lambda t: t.timestamp)
            last_trade = max(self.app.current_trades, key=lambda t: t.timestamp)
            
            self.safe_after(0, lambda: self.start_date_var.set(first_trade.timestamp.strftime("%Y-%m-%d")))
            self.safe_after(0, lambda: self.end_date_var.set(last_trade.timestamp.strftime("%Y-%m-%d")))
    
    def on_data_error(self, error_message: str):
        """Handle data loading error"""
        # Use safe_after for all GUI updates
        self.safe_after(0, lambda: self.data_status.configure(text="Error loading data"))
        self.safe_after(0, lambda: self.load_button.configure(state="normal"))
        # Use safe_after for messagebox to avoid threading issues
        self.safe_after(0, lambda: messagebox.showerror("Error", f"Failed to load data: {error_message}"))
    
    def refresh_data(self):
        """Refresh displayed data"""
        if self.app.current_trades:
            # Use safe_after for all GUI updates
            self.safe_after(0, lambda: self.data_status.configure(text=f"Loaded {len(self.app.current_trades)} trades"))
            self.safe_after(0, lambda: self.load_button.configure(state="normal"))
            
            # Update date range if not set
            if not self.start_date_var.get() and self.app.current_trades:
                first_trade = min(self.app.current_trades, key=lambda t: t.timestamp)
                last_trade = max(self.app.current_trades, key=lambda t: t.timestamp)
                
                self.safe_after(0, lambda: self.start_date_var.set(first_trade.timestamp.strftime("%Y-%m-%d")))
                self.safe_after(0, lambda: self.end_date_var.set(last_trade.timestamp.strftime("%Y-%m-%d")))
