"""
IQ Analyzer Pro - Main Application Entry Point
Advanced Trading Analysis Platform with AI-powered insights
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path FIRST
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(current_dir)

from ui.main_app import MainApplication
from utils.config import config
from utils.logger import setup_logger


def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logger(
        name="IQ_Analyzer_Pro",
        log_level=config.config.log_level,
        console_output=True
    )
    
    logger.info("Starting IQ Analyzer Pro...")
    
    try:
        # Ensure required directories exist
        config.ensure_directories()
        
        # Create and run application
        app = MainApplication()
        
        # Setup application with configuration
        app.root.geometry(f"{config.config.ui.window_width}x{config.config.ui.window_height}")
        
        logger.info("Application initialized successfully")
        
        # Run the application
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        print(f"Error starting application: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
