"""
IQ Analyzer Pro - UI Module
User interface components and GUI application
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.main_app import MainApplication

__all__ = ['MainApplication']
