"""
UI Components - Tab components for the main application
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ui.components.login_tab import LoginTab
from ui.components.analysis_tab import AnalysisTab
from ui.components.ai_tab import AITab
from ui.components.dashboard_tab import DashboardTab

__all__ = ['LoginTab', 'AnalysisTab', 'AITab', 'DashboardTab']
