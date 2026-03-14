"""
app.py - Compatibility layer for existing code
Maintains backward compatibility with the original app.py interface
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from main import MainApplication
from core.data_models import DataFrameConverter


class LegacyApp:
    """
    Legacy compatibility wrapper for the original app.py interface
    Maintains the same function signatures as the original code
    """
    
    def __init__(self):
        self.app = MainApplication()
        self.last_df = None
    
    def start_gui(self, run_func=None, dashboard_func=None, ai_func=None):
        """
        Start the GUI with compatibility for original function signatures
        
        Args:
            run_func: Original run function callback
            dashboard_func: Original dashboard function callback  
            ai_func: Original AI function callback
        """
        # Store callbacks for compatibility
        self.app.run_func = run_func
        self.app.dashboard_func = dashboard_func
        self.app.ai_func = ai_func
        
        # Start the application
        self.app.run()
    
    def get_last_df(self):
        """
        Get the last analyzed dataframe (compatibility method)
        
        Returns:
            pandas.DataFrame: Last analyzed trades dataframe
        """
        if self.app.current_trades:
            return DataFrameConverter.trades_to_dataframe(self.app.current_trades)
        return DataFrameConverter.trades_to_dataframe([])


# Global instance for compatibility
app_instance = LegacyApp()


def start_gui(run_func=None, dashboard_func=None, ai_func=None):
    """
    Original start_gui function - maintains compatibility
    
    Args:
        run_func: Function to run trade analysis
        dashboard_func: Function to launch dashboard
        ai_func: Function to run AI analysis
    """
    app_instance.start_gui(run_func, dashboard_func, ai_func)


# Global variable for compatibility (original had this)
last_df = None


def update_last_df(df):
    """
    Update the global last_df variable (compatibility)
    
    Args:
        df: DataFrame to set as last_df
    """
    global last_df
    last_df = df


def get_last_df():
    """
    Get the global last_df variable (compatibility)
    
    Returns:
        pandas.DataFrame: Last analyzed dataframe
    """
    global last_df
    return last_df or app_instance.get_last_df()


# Export the main functions for original compatibility
if __name__ == "__main__":
    start_gui()
