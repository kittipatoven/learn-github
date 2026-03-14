"""
Test script to check if all imports work correctly
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test all module imports"""
    try:
        print("Testing core imports...")
        from core import Trade, TradeParser, TradeAnalyzer, AIEngine
        from core.data_models import DataFrameConverter
        print("✅ Core imports successful")
        
        print("Testing UI imports...")
        from ui.main_app import MainApplication
        print("✅ UI imports successful")
        
        print("Testing utility imports...")
        from utils.config import config
        from utils.logger import setup_logger
        print("✅ Utility imports successful")
        
        print("Testing compatibility imports...")
        from app import start_gui
        from ai_pair_analyzer import analyze_best_pairs
        print("✅ Compatibility imports successful")
        
        print("\n🎉 All imports successful! The application should run now.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\nYou can now run the application with:")
        print("python run.py")
        print("or")
        print("python main.py")
    else:
        print("\nPlease check the error above and fix the import issues.")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
