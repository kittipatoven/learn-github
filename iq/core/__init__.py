"""
IQ Analyzer Pro - Core Module
Core business logic and data processing components
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.data_models import Trade, AnalysisResult, PairScore
from core.trade_parser import TradeParser
from core.trade_analyzer import TradeAnalyzer
from core.ai_engine import AIEngine
from core.metrics_calculator import MetricsCalculator

__all__ = [
    'Trade',
    'AnalysisResult', 
    'PairScore',
    'TradeParser',
    'TradeAnalyzer',
    'AIEngine',
    'MetricsCalculator'
]
