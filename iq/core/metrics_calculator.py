"""
Metrics Calculator - Advanced trading metrics calculations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from core.data_models import Trade


class MetricsCalculator:
    """Calculate advanced trading metrics and risk measures"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_risk_metrics(self, trades: List[Trade]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        if not trades:
            return {}
        
        profits = [trade.profit for trade in trades]
        returns = np.array(profits)
        
        return {
            'var_95': self._calculate_var(returns, 0.95),
            'var_99': self._calculate_var(returns, 0.99),
            'cvar_95': self._calculate_cvar(returns, 0.95),
            'cvar_99': self._calculate_cvar(returns, 0.99),
            'volatility': np.std(returns),
            'skewness': self._calculate_skewness(returns),
            'kurtosis': self._calculate_kurtosis(returns),
            'max_loss': np.min(returns),
            'max_gain': np.max(returns)
        }
    
    def _calculate_var(self, returns: np.ndarray, confidence_level: float) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def _calculate_cvar(self, returns: np.ndarray, confidence_level: float) -> float:
        """Calculate Conditional Value at Risk"""
        var = self._calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calculate skewness"""
        if len(returns) < 3:
            return 0
        
        mean = np.mean(returns)
        std = np.std(returns)
        
        if std == 0:
            return 0
        
        return np.mean(((returns - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calculate kurtosis"""
        if len(returns) < 4:
            return 0
        
        mean = np.mean(returns)
        std = np.std(returns)
        
        if std == 0:
            return 0
        
        return np.mean(((returns - mean) / std) ** 4) - 3
