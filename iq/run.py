"""
Simple startup script for IQ Analyzer Pro
Avoids relative import issues
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path at the start
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Set the Python path environment variable
os.environ['PYTHONPATH'] = str(current_dir)

if __name__ == "__main__":
    try:
        # Now import and run the main application
        from main import main
        main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
